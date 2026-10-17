# SkyBlock (g1048) – İçerik Referansı

Kaynak: oyunun cihaza indirdiği `m1048_1` paketi (SkyBlock mod verisi, 581 dosya).
Decompile değil — veriler doğrudan modun `setting/` JSON/lang/yml dosyalarından okundu.

> **Kesin sayısal statlar hakkında dürüst not:** her kılıcın tam hasarı / her zırhın tam
> savunması `sandboxol` adlı **sıkıştırılmış/paketli bir blob** içinde ve büyük ölçüde sunucuda
> tutuluyor — düz metin değil, o yüzden "Elmas Kılıç = +N hasar" gibi birebir sayıları buradan
> veremiyorum (paketlemeyi kırmam). Aşağıdakiler: tam **isim + kademe + açıklama + set etkisi**
> kataloğu ve **pet stat sistemi** (bunların sayıları açık).

---

## 1. Kılıçlar / Silahlar

**Temel kademe (malzemeye göre, artan hasar):**
Tahta → Taş → Demir → Altın → Elmas → **Ametist (Amethyst)**

**Özel / nadir silahlar (açıklamalardan):**
| Silah | Not |
|---|---|
| Excalibur, Arondight, Gram | Efsanevi kılıçlar |
| Titan Silahı | "Antik Titanların kullandığı, çok nadir, **sınırsız dayanıklılık**" |
| Odin'in Silahı | "Tanrı Odin'in silahı, buzul ışığı yayar" |
| Soul Beam Sword, Ice Dragon Sword, Shark Sword | Temalı |
| Death Scythe (tırpan), Necrotic Battle Axe | Temalı |
| Miner's Sword, Ice-Iron Sword, Skeletal Sword | Temalı |
| Magic Broom, 2019 Christmas tree weapon | Etkinlik/kozmetik |
| Titanyum balta / kazma (Item_3871/3872) | "blokları hızlı kırar" (araç) |

Yay: "uzun menzilli, çantanda ok olmalı".

## 2. Zırhlar ve Setler

**Temel zırh kademeleri** (kask / göğüslük / bacak / bot):
Demir → Altın → Elmas → **Ametist**. Açıklama: kask/zırh "savunmanı artırır".

**İsimli setler ve set etkileri (önemli kısım):**
| Set | Set etkisi (oyun açıklaması) |
|---|---|
| **Titan** | Kask+zırh+bacak+bot, hepsi **sınırsız dayanıklılık** |
| **Odin** | "Ekstra HP sağlayan efsanevi zırh"; set: *Odin Footprints* (ayak izi efekti) |
| **Round Table Knight** (Yuvarlak Masa Şövalyesi) | Kask/bacak/bot – kozmetik+stat set |
| **Archangel (Baş Melek)** | 5 parça. Set etkisi: **ölümcül hasar alınca 2 sn kontrol-bağışıklığı + yenilmezlik**; bitince HP yeniler, **True Damage** artar, alan hasarı verir. Ayrıca *Footprints* ve *Aura* efektleri |
| **Chariot (Tarot)** – yeni | Silahla savaşırken **Silver Chariot** çağırır (hayaletler saldırır, ek hasar + **Armor Break**). Set giyince savaşta **Unarmored State** şansı: **ATK↑ + Lifesteal**, ama daha kırılgan. "Yüksek risk, yüksek ödül". Lucky Draw'dan |
| **Reaper's Suit** (Azrail) | Süreli set (Lucky Draw/paket) |

**Paketler (mağaza):** First Top-up, Value, Mine Unlocking, Star Discovery, Tool, **Armor Pack**,
**Weapon Pack**, Supreme Pack, Reaper's Suit Pack, Archangel Set Pack, Reforging Stone Package,
Block Pack'ler (Space Expedition / Cute Pink / Ocean Temple).

**Reforging Stone (Yeniden Dövme Taşı):** zırhı hızlı güçlendirmek için (süreli etkinlik item'ı).

## 3. Petler

Rozet/id ön ekine göre **4 nadirlik kademesi** (1xxx temel → 2xxx nadir → 3xxx epik → 9xxx özel):

| Kademe | Petler |
|---|---|
| **1xxx (temel)** | Fighting Cat, Hunting Dog, Moon Rabbit, Quack Duck, Scout Chick, Squirrel |
| **2xxx (nadir)** | Wild Wolf, Boxing Bear, Peregrine Falcon, Armored Horse, King Frog, Long-hair Pig, Starbutterfly, Volt Goat, Floating Grass, Ninja Cat |
| **3xxx (epik)** | Magic Flame Dragon, Roar Flame Tiger, Nine-tailed Fox, Snake Nian Beast, Polar Ice Shark, Thorn Shooter, CumulusBird, Blaze Rex, Pegasus Beast, Pegasus Girl |
| **9xxx (özel)** | Slime, Icy Boom, Seabed Rock |

5 adet **Pet Egg Incubator** (kuluçka), 16 adet **mount** (binek) tanımı var.

### Pet stat sistemi (`PetSetting.json` — sayılar net)
- **Savaş gücü (power) katsayıları:** `MaxHealth×4 · Attack×20 · Defense×40 · Productivity×5`.
  → Savunma ve saldırı, güç puanına en çok katkıyı yapar; üretkenlik en az.
- **Başlangıç attribute puanı dağılımı (10.000 üzerinden ağırlık):**
  - Normal: 5p=%23, 6p=%36, 7p=%24, 8p=%12, 9p=%4, 10p=%1
  - Etkinlik: 6p=%51, 7p=%30, 8p=%14, 9p=%4, 10p=%1 (5p yok → daha iyi rulo)
- **Attribute dönüşüm oranı:** MaxHealth 5 · Attack 1 · Defense 0.5 · Productivity 4
- **Yetenek slotu açılışı:** slot1/2 → seviye 1, slot3 → seviye 3, slot4 → seviye 5
- **"Kitap basma" ile yetenek sayısı artırma ihtimali** (on binde): 1.→10000, 2.→10000,
  3.→1500, 4.→300, 5.→80 (yani 3+ yetenek bağlamak çok zor).
- **Elementler:** 1=Ateş, 2=Yıldırım.
- **Çalışma (打工) döngüsü:** 18.000 sn = **5 saat** (pet'i işe gönderme periyodu).

**Oyuncu için çıkarım:** Yüksek başlangıç attribute puanı nadir (10 puanlık rulo on binde 100).
Attack puanı güç formülünde ×20 ama dönüşüm oranı 1 — yani saldırı puanı "pahalı ama değerli".
Çalışma/üretim petleri 5 saatlik döngüyle pasif kazanç sağlıyor.

## 4. SkyBlock mod sistemleri (aktif plugin'ler)

`setting.json` modun açık sistemlerini listeliyor — SkyBlock'un kapsamı:

- **Ekonomi/eşya:** equipment, inventory, item_container, item_chest (sandık limiti **70**),
  item_book, item_bucket, furnace (fırın), workbench (tezgah), trade (takas), store, product,
  random_shop / dynamic_shop / common_shop, custom_lottery, lucky_chest, treasure_chest,
  treasure_map, cash_recharge, app_store, safe_lock (kasa).
- **Ada/dünya:** open_world, one_block, module_block, mine_field, mine_hole, home,
  home_plant (ekim), home_terrain, home_actor, build_blueprint, multi_build, schematic.
- **Savaş/PvP:** battle, pvp_rank, gem_arena, poison_circle (zehir çemberi), monster,
  hide_and_seek, fishing.
- **Sosyal:** friend, clan, team, party, chat, chat_bubble, email, privilege, rank.
- **İlerleme:** task, task_chain, pass (battle pass), achieve, check_in, guide, pet, activity,
  christmas, vf_app_activity.
- **Anti-hile:** `cheat_detect` + `db_lock` (SkyBlock'ta da aktif).

## 4.1 Sezon setleri (topluluk kaynakları — doğrulanmamış)

SkyBlock sürekli yeni **sezon seti** ekliyor. Topluluk wiki'lerinden derlenen liste
(isimler kaynaklar arasında biraz değişiyor, numaralandırma kesin değil):

S1 Necrotic (Gangrene) · S2 Nightmare Knight · S3 Silverfang · S4 Astral · S5 Angelic ·
S6 Forest Guardian · … · S15 Frost Lord · S17 Black Rose · S18 Stars & Moon · S19 Elf ·
S20 Shark · S21 Cloud · S22 Raven · S23 Blaze State · S24 Nebula · … (sezon sayısı büyüyor,
bir TikTok S42'den söz ediyor).
Kaynak: [Fandom – SkyBlock](https://blockman-go-blocky-mods.fandom.com/wiki/SkyBlock),
[NamuWiki](https://en.namu.wiki/w/Skyblock%20for%20Blockman%20GO).

## 4.2 Bulunabilen sayısal statlar (topluluk — doğrulanmamış)

Kesin statlar oyun paketinde açık değil (bkz. baştaki not). Web'de bulunabilen parçalar:

| Öğe | Değer | Kaynak |
|---|---|---|
| **Odin seti** | ~60 HP, ~23 DEF, tam set ~2.4M coin, silahı **Gram** | [Fandom – Odin armor](https://blockman-go-blocky-mods.fandom.com/wiki/Odin_armor) |
| **Ice Dragon Sword** | 20 hasar | [NamuWiki](https://en.namu.wiki/w/Skyblock%20for%20Blockman%20GO) |
| Set bonusları genel biçim | "HP +6", "DEF +0.5" gibi küçük toplanır bonuslar | [FunPay ilanları](https://funpay.com/en/lots/1241/) |

> **Uyarı:** Topluluk tier-list'leri **çelişkili** — kimi **Hades**'i 1 numara sayıyor,
> kimi Odin'i düşük. Bu sayılar güncellemelerle değişiyor; resmi değil.

## 4.3 Kaynak erişim durumu (dürüst not)
- `res.pack` (10 MB): tamamen sıkıştırılmış, okunabilir stat yok (kırılmadı).
- Fandom & NamuWiki: Cloudflare JS koruması yüzünden bu ortamdan **açılamadı** (403).
  Sayılar yukarıda arama motorunun özetlediği parçalardan; tam tablo için wiki'ye
  tarayıcıdan bakmak gerekiyor.
- YouTube "value list" videoları: stat değil, **takas değeri** listeleri; ayrıca video
  içeriği izlenemiyor.
- **Kesin per-set/per-sword sayıları için tek güvenilir yol:** oyun-içi item ekranı
  (ekran görüntüsü) → birebir tabloya dökülebilir.

## 5. Diğer veriler
- **Sandık limiti:** 70 (`ItemChest.yml`).
- **Blok id → ad eşlemesi:** `id_mappings.ini` (ör. 1360=white_light, 2367+ özel bloklar).
- Kesin kılıç hasarı / zırh savunması / set stat sayıları: `sandboxol` paketli blob + sunucu;
  birebir sayı için oyun-içi item ekranı ya da topluluk wiki'si gerekir.
