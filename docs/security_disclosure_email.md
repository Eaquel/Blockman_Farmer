# Responsible Disclosure — Blockman GO Android client

> Draft to send to the vendor. Fill the **[ ]** placeholders before sending.
> Findings come from **static analysis only** (decompiled Lua bytecode shipped in the
> app's assets). Nothing was exploited against live servers or other users.

---

**To:** [vendor security contact — e.g. security@blockmango.com; if none, use official
support / check for a security.txt or the publisher GVERSE INTERNATIONAL PTE. LTD.]
**Subject:** Security report — debug interface & client-trust issues in Blockman GO (com.sandboxol.blockymods 3.29.3)

Hello Blockman GO / GVERSE security team,

I'm a player and hobbyist who was studying the game's client for my own learning. During
static analysis of the Lua scripts shipped in the app's assets I noticed a few things that
look like they could matter for security. I'm reporting them privately so you can review and
fix if relevant. I have **not** exploited any of these against your servers or other players,
and I'm not sharing the details publicly.

**Scope analysed**
- APK: `com.sandboxol.blockymods` version **3.29.3** (versionCode 5753)
- Lua engine resources: client version **4.1383.0.0**
- Method: offline decompilation of the shipped Lua bytecode and inspection of CSV/JSON config.

---

## Finding 1 — Debug interface appears enabled in the release build (highest concern)

- **Where:** `lua/common/debugport.lua`, invoked from `lua/client/main.lua` at startup:
  `debugport.Init(... , 6661, 6666)` — I could not find an `isDebug`/build-type guard around
  this call.
- **What it does:** opens a local TCP debug port (first free of 6661–6666) and a UDP socket.
  The debug command handler evaluates text with Lua `load()` (arbitrary script execution),
  and includes commands such as `poco_start` that start the Poco automation server. It also
  periodically sends device info and the logged-in `userId` to a hardcoded address
  (`47.243.80.43:10086`).
- **Why it matters:** a developer/debug surface shipped to production is risky. Even though
  it binds to localhost, any local process (another installed app, an ADB session, a
  malicious SDK) could reach it; `load()`-based command handling is a code-execution surface,
  and the device/user telemetry to a fixed IP is an information-exposure concern.
- **Recommendation:** gate `debugport.Init` (and the Poco automation hooks below) behind a
  debug build flag so they are compiled out of release; remove or authenticate the hardcoded
  telemetry endpoint.

## Finding 2 — QA automation framework (Poco) shipped in release

- **Where:** `lua/client/autotest/` (NetEase Poco SDK), `autotest.lua` with
  `serverUrl = "http://localhost:8081/"`; also reachable via the debug command `poco_start`.
- **Why it matters:** this is a UI-automation/remote-control framework intended for QA. Left
  in the shipped client, it is an automation/bot surface and increases attack surface.
- **Recommendation:** exclude the autotest package from release builds.

## Finding 3 — Ad-reward completion is self-reported by the client on one platform

- **Where:** `lua/client/player/player_packet.lua`, `handles:OnWatchAd`. When
  `getPlatformId() == 1`, the client immediately sends `OnWatchAdResult {type=1, code=1}` to
  the server instead of going through the real ad SDK callback.
- **Why it matters:** if the server grants the ad reward on receipt of this packet without an
  independent ad-network verification (SSV/callback), a modified client could claim rewards
  without watching ads. (I did not test the server side, so this depends on whether the
  server independently verifies ad completion.)
- **Recommendation:** verify ad completion server-side via the ad network's server-side
  verification callback; do not grant rewards on a client-sent completion packet alone.

## Finding 4 — Trade confirmation is not reset when the offer changes (design/anti-scam)

- **Where:** `lua/server/trade.lua`. In `playerAddItem` / `playerDelItem` I did not see the
  counterpart's `confirmed` flag being cleared when one side changes the items on the table
  (there is a reset on cancel/confirm-toggle, but not on every item change in the base flow).
- **Why it matters:** this can enable a bait-and-switch between the moment a player reviews an
  offer and the moment they confirm, if a game mode doesn't add its own re-check. This is more
  of a player-safety/scam concern than a classic vulnerability.
- **Recommendation:** clear both parties' confirmation state on any change to the traded item
  set, and show a clear "offer changed" prompt.

---

**Notes**
- Severity ordering is my own estimate from static analysis; you're better placed to judge
  real impact given your server-side checks.
- I'm happy to share the exact file/line references and coordinate on timing. I'm not
  publishing anything and have no interest in misusing this.
- If you run a bug-bounty or vulnerability-disclosure program, please point me to it and I'll
  refile there.

Thank you for your time, and thanks for the game.

Best regards,
Eaquel
[your contact email]
