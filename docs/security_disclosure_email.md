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

## Finding 5 — Client can invoke arbitrary server-side triggers with attacker-controlled context

- **Where:** `lua/server/player/player_packet.lua`, `handles:ClientTrigger`. The handler calls
  `Trigger.CheckTriggers(cfg, packet.name, context)` where `packet.name` (trigger name),
  `packet.target` (object/block to resolve `cfg` from), `packet.obj1`, `packet.obj2`, and the
  entire `packet.context` table are taken from the client and merged into `context`.
- **Why it matters:** triggers are the server's game-logic/event system (rewards, state
  changes, trade/sell events, etc.). Letting the client choose which trigger fires, against
  which object, with an arbitrary context, means client input can drive server logic that is
  presumably meant to be server-initiated. Depending on what each trigger does, this is a
  potentially serious logic-abuse surface.
- **Recommendation:** restrict `ClientTrigger` to an explicit allow-list of trigger names that
  are safe to be client-initiated; validate that `obj1/obj2/target` belong to / are visible to
  the calling player; ignore client-supplied context keys beyond a known schema.

## Finding 6 — `EntityValue` lets the client set value keys flagged client-writable; `sinValue` is one of them

- **Where:** `handles:EntityValue` + `Entity.ValueDef` (`lua/common/entity.lua`). The handler
  accepts a client `key`/`value` and calls `setValue` as long as `ValueDef[key][2]` (the
  "client-writable" flag) is truthy. `ValueDef.sinValue = {false, true, ...}` — i.e. the
  crime/"sin" value is marked client-writable.
- **Why it matters:** `sinValue` drives wanted/criminal state in some modes. A client being
  able to set its own `sinValue` could clear a wanted status or otherwise manipulate mode
  logic. More generally, the whole model relies on every `ValueDef` entry being correctly
  flagged; one mistakenly-writable sensitive key is a problem, and the value is taken verbatim
  from the client (including `BigInteger`).
- **Recommendation:** audit every `ValueDef` client-writable flag; `sinValue` and any
  gameplay-authority stat should be server-only. Range/type-check accepted values.

## Finding 7 — Callback dispatch is driven by client-supplied identifiers and context

- **Where:** `handles:DoCallBack` / `handles:DoRemoteCallback` →
  `doCallBack(packet.modName, packet.key, packet.regId, packet.context)`. The module name,
  callback key, registration id and context all come from the client.
- **Why it matters:** if a client can select which registered server callback to invoke (and
  with what context), it may be able to trigger callbacks out of their intended flow. Impact
  depends on what plugins register, but client-chosen callback dispatch is a trust-boundary
  risk worth reviewing.
- **Recommendation:** bind callbacks to the session/flow that created them and verify the
  caller is allowed to invoke that `regId`, rather than trusting client-supplied ids.

## Finding 8 — `SellItem` reward derived from client-supplied quantity

- **Where:** `handles:SellItem` / `handles:SellItems`. `sellNum` comes from the client;
  reward currency is `sellNum * itemcost`. Quantity is gated by `item:consume(sellNum)`, but
  I could not confirm `sellNum` is validated as a positive integer, nor that the currency
  granted is reconciled against the amount actually consumed.
- **Why it matters:** if `sellNum` can be non-positive or otherwise abnormal, or if the
  reward trigger grants currency independently of a successful, bounded consume, this is an
  economy-integrity risk.
- **Recommendation:** validate `sellNum` is a positive integer ≤ owned quantity; compute and
  grant the reward strictly from the quantity actually consumed, server-side.

## Finding 9 — GM access is enabled by a map/config flag (defense-in-depth)

- **Where:** `handles:GM` gate: `if not World.gameCfg.gm and not Game.HasGMPermission(...)
  then return end`. If a map/mode ships with `gameCfg.gm` enabled, the GM command surface
  (teleport, `GMCall`, edit-entity, debug-port set) is available to any player in it.
- **Why it matters:** a single production/test map accidentally shipped with `gm = true`
  would expose GM functionality to everyone in that room.
- **Recommendation:** ensure no production map ships with `gm` enabled; prefer gating GM on
  per-account permission only, and log/alert if a non-permitted account reaches GM.

## Finding 10 — Chat profanity/word filter can be bypassed with a client-set field

- **Where:** `lua/server/player/player_packet.lua`, `handles:ChatMessage`. The server applies
  `self:wordFilter(packet.msg)` **only when `packet.voiceTime` is absent**; if the client
  includes a `voiceTime` field, the branch takes `msg = packet.msg` (raw, unfiltered) and then
  broadcasts it (world chat / `SEND_CHAT_MESSAGE` trigger / `WorldServer.ChatMessage`).
- **Why it matters:** a client can send a text chat message that skips the word filter simply
  by attaching a `voiceTime` value, defeating content moderation on text chat.
- **Recommendation:** apply the word filter based on the actual message type/content, not the
  mere presence of `voiceTime`; filter all text that is broadcast as text, and validate that
  `voiceTime` only accompanies genuine voice messages.

## Finding 11 — Chest interaction trusts a client-supplied position (no proximity/ownership check)

- **Where:** `handles:SwitchChestItem` / `handles:SwitchNpcChestItem`. The chest is resolved
  from `self.map:getBlockData(packet.chestPos)` using the client-supplied `chestPos`; the base
  handler does not appear to verify the player is in range of, or permitted to access, that
  chest (access control is left to optional `CHECK_PUT_INTO_CHEST` / `CHECK_TAKE_FROM_CHEST`
  triggers that a given mode may or may not implement).
- **Why it matters:** if a mode doesn't add its own checks, a player could move items to/from
  a chest at arbitrary coordinates they name, without being near it (interact-from-anywhere).
  Also, an invalid `chestPos` (no `.tray`) would error in the handler.
- **Recommendation:** in the base handler, validate `chestPos` resolves to a real container,
  that the player is within interaction range, and that access is permitted; reject otherwise.

## Finding 12 — Missing bounds / positivity validation on client indices and counts

- **Where:**
  - `handles:RoutineCommit`: `routine[packet.typeIndex].content` is indexed with the
    client's `typeIndex` without a bounds/nil check (malformed value → handler error).
  - `Player:splitTrayItem` (`server/player/player.lua`): `splitCount` is checked
    `>= stack_count` → false, but is **not** checked `> 0`, so zero/negative split counts are
    not rejected.
- **Why it matters:** unvalidated client indices can crash handlers (local DoS / unexpected
  state), and non-positive counts in stack-splitting are a classic source of quantity/duplication
  anomalies depending on downstream add/remove logic.
- **Recommendation:** validate every client-supplied index exists before use, and require
  counts to be positive integers within the owned amount; treat item moves/splits as atomic
  transactions so a failure can't leave duplicated or orphaned stacks.

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
