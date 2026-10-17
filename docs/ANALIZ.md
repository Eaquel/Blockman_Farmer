# Blockman GO – Assets Analizi (Decompile)

Kaynak: Drive'daki `Test_Blockman_Assets.zip` (233 MB, 13.343 dosya, istemci sürümü `4.1383.0.0`).
Yöntem: Lua 5.3 bytecode dosyaları `unluac` ile decompile edildi (1.399 dosyadan 1.397'si başarılı, ~11 MB okunabilir Lua).
Tekrar üretmek için: `tools/decompile.sh <zip>`.

> Oyunun kendi kodu bu repoya konmadı. Burada sadece analiz ve kendi yazdığımız araçlar var.

---

## 1. Paketin yapısı

| Klasör | İçerik | Okunabilir mi? |
|---|---|---|
| `lib/*/libBlockMan*.so` | v1 / v2 / v4 C++ motoru | Hayır. Paketlenmiş/şifreli, string bile çıkmıyor |
| `resourcesv2/lua/` | **v2 motoru**: `client/` (89K satır), `server/` (32K), `common/` (37K), `plugins/` | Evet, decompile edildi |
| `resources/Media/Setting/*.csv` | v1 veri tabloları: silahlar, ekinler, çiftlik ürünleri, binekler, araçlar | Evet, düz metin |
| `resources/recipe/*.json` | 471 üretim tarifi | Evet |
| `resources/Media/Scripts/ScriptSetting.csv` | Bütün oyun modlarının kod listesi | Evet |
| `resources/Media/Scripts/Game/g1008…` | Bed Wars arayüz ve sesleri (oyun mantığı yok) | Kısmen |

**Önemli:** Skyblock (`g1048`), Bed Wars (`g1008`) gibi modların **oyun mantığı pakette yok**. Moda girince sunucudan indiriliyor (`HotUpdate=1`). Para, eşya ve sonuçlar sunucuda hesaplanıyor.

### Mod kodları (ScriptSetting.csv)
| Kod | Mod | Kod | Mod |
|---|---|---|---|
| g1008 / g1046 | Bed Wars / lobi | g1048 | **Skyblock – ana ada** |
| g1061 / g1062 / g1065 | Bed Wars solo / duo / 10v10 | g1049 | Skyblock – büyük dünya |
| g1031 | Rancher (Büyük Çiftçi) | g1050 | Skyblock – süreli etkinlik |
| g1047 | Ev (Home) | g1066 / g1067 / g1068 | Skyblock – özel mod / hapishane / dünya madeni |
| g1054 / g1058 | Lucky Block Skywars | g1002 / g1027 | Skywars / Sky Royale |
| g1042–g1045, g1053 | Pixel Gun (lobi / takım / solo / 1v1 / battle royale) | g1071–g1072 | Klan savaşı |
| g1055 | Fitness Simulator | g1148–g1150 | Valto (ana ada / dünya / gizli bölge) |

---

## 2. PvP – Savaş mekaniği (v2 motoru, `server/entity/entity.lua`)

Oyun 20 tick/sn çalışır (`GAME_LOGIC_FPS = 20`).

### 2.1 Hasar formülü
```
hasar = max(saldırı.damage × (saldırı.dmgFactor − hedef.deDmgPct) − hedef.defense, 0) × saldırı.damagePct
```
Editor şablonundaki oyunlarda (`editor_template`) zırh delme de var:
```
hasar = max(damage×dmgFactor − max(defense − deArmour, 0), 0) × damagePct   (en az 1)
```
**Taktik:** `defense` (zırh) **sabit bir sayı olarak çıkarılır**. Bu yüzden zırhlı rakibe zayıf ama hızlı vuruşlar neredeyse işlemez. Vuruş başına yüksek hasarlı silah seç. Zırhsız rakipte ise fark azalır.

### 2.2 Hasar sonrası koruma (en önemli bulgu)
```lua
hurtResistantTime = cfg.hurtResistantTime or 20   -- 20 tick = 1 saniye
if hurtResistantTime >= Now and damage <= lastDamage then return 0 end
damage = damage - lastDamage
```
- Vurulan oyuncu **1 saniye korunur**. Bu sürede gelen vuruş, önceki vuruştan **büyük değilse 0 hasar** verir. Büyükse **sadece farkı** verir.
- `/attack` yeteneğinin kendi bekleme süresi yok, ama bu koruma yüzünden **spam tıklamak hasarı artırmaz**.
- **Taktik:**
  1. Vuruşlarını yaklaşık 1 saniye aralıkla zamanla. Aradaki tıklar boşa gider.
  2. Önce güçlü silahla vur. Zayıfla açıp güçlüye geçersen sadece fark işler.
  3. Takım savaşında iki kişi aynı hedefe aynı saniyede vurursa ikinci vuruş büyük ölçüde boşa gider. Hedefleri dağıtın ya da sırayla vurun.
- Bazı modlarda ek bir `enableDamageProtection` koruması var: 40 tick = **2 saniye** tam dokunulmazlık (doğma koruması gibi).

### 2.3 Menzil ve geri tepme
- Yakın dövüş menzilini sunucu kontrol eder: **4 blok** (`MeleeAttack.range = 4`). Daha uzaktan yapılan vuruşları sunucu reddeder.
- Varsayılan geri tepme **çok düşük** (`hurtDistance = 0.1`). Rakibi kenardan düşürmek için tek vuruş genelde yetmez. Mod kendi değerini koymadıysa birkaç vuruş ya da düşme hasarı gerekir.
- Zıplamanın 10 tick (**0,5 sn**) bekleme süresi var.

### 2.4 Düşme hasarı
`düşme hasarı = düşüş hızı × 5` (`dropDamageRatio = 5`). Yüksekten düşmek ciddi hasar verir. Skyblock ve Skywars'ta rakibi aşağı düşürmek yakın dövüşten daha etkili olabilir.

### 2.5 Kritik, kaçınma, can çalma, yansıtma
- `critDmgProb` ve `dodgeDmgProb` diye özellikler var, ama **temel saldırı kodu bunları kullanmıyor** (`damageIsCrit = false`). Sadece moda özel kodla çalışırlar.
- `lifeSteal`: verdiğin hasarın belli bir oranı kadar can kazanırsın.
- `dmgRebound`: aldığın hasarın belli bir oranı saldırana geri yansır. Yansıyan hasara 1 saniyelik koruma uygulanmaz.
- Altın elma: hasar önce ekstra can (`extraHp`) kalkanından düşülür.

### 2.6 Silahlar (`ItemGun.csv`, v1 silahlı modlar)
`tools/gun_stats.py` ile hesaplandı. Atış arası saniye, şarjör değiştirme tick cinsinden. Sürekli DPS şarjör değiştirmeyi de hesaba katar.

| Silah | Hasar | Atış arası | Şarjör | Değiştirme | Anlık DPS | Sürekli DPS |
|---|---|---|---|---|---|---|
| Gatling | 20 | 0,1 sn | 50 | 3 sn | 200 | **125** |
| Barrett | 250 | 3 sn | 20 | 2,5 sn | 83 | 80 (tek atış öldürür) |
| M4A1 | 13 | 0,25 sn | 50 | 1 sn | 52 | 48 |
| 98K | 140 | 3 sn | 20 | 2 sn | 47 | 45 (tek atış) |
| M1014 | 5 | 0,5 sn | 20 | 1,5 sn | 10 | 8,7 |

Not: Birçok silah aynı yer tutucu değerleri taşıyor (AK47 = 1,5 hasar gibi). Modlar bunları kendi ayarlarıyla değiştiriyor olabilir, o yüzden tabloyu kesin sayı değil, kabaca bir sıralama olarak düşün. Buradaki genel kural, 1 saniyelik koruma ve sabit zırh çıkarma yüzünden **vuruş başına yüksek hasar her zaman avantajlı**.

---

## 3. Coin / Gold kasma (ekonomi)

### 3.1 Maç sonu Gold ödülü (`server/reward_manager.lua`)
Ödülü merkezi sunucu hesaplar. Sunucuya gönderilen bilgiler:
```
rank        – maçtaki sıran (varsayılan 10)
duration    – maç süresi (sn)
totalNum    – maç başındaki oyuncu sayısı
standardNum – 10 (referans oyuncu sayısı)
```
**Taktik:**
1. **Dolu lobilerde** oyna. Başlangıçtaki oyuncu sayısı 10'un üstünde olmalı. Oran `totalNum/standardNum` gibi görünüyor.
2. **Maçı sonuna kadar oyna.** Süre de hesaba giriyor; erken çıkarsan ödül azalır ya da hiç gelmez.
3. Üst sıralarda bitir.
4. Ödül oyuncu başına **maç başına bir kez** veriliyor (`RewardHistory`).

### 3.2 Günlük giriş (`player_sign_in.lua`)
Gün değişimi sunucu saatine göre (`Lib.getYearDayStr`). Kaçırılan günler ödül listesinde atlanıyor, bazı etkinlikler `repeatDay` ile baştan başlıyor. **Her gün bir kez girmek** zinciri korur.

### 3.3 Sürpriz yumurtalar (`plugins/easter_eggs`)
- Belirli saatlerde haritanın rastgele noktalarında ödül yumurtaları çıkar (`refreshTime`).
- **Yoğun saatlerde** (`peakStart`–`peakEnd`) **Gelişmiş (Advanced)** yumurta çıkar. Daha iyi ödül için bu saatlerde oyunda ol.
- Her yenilemede konumlar oyuncu başına rastgele seçiliyor ve her yumurta bir kez alınabiliyor.

### 3.4 Çekiliş ve şans sistemi (`plugins/limited_time_activity`, `plugins/activity`)
- **Süreli çekiliş:** Bir **garanti sayacı** var ve etkinlik boyunca korunuyor. Belirli çekiliş sayılarında garanti ödül havuzu devreye giriyor. **Büyük ödül çıkınca sayaç sıfırlanıyor.**
  - 10'lu çekiliş, kodda 10 tekli çekilişle aynı hesap. Avantajı sadece fiyat indirimi varsa.
  - Sayaç kaybolmadığı için çekilişleri etkinlik boyunca **bölerek** yapabilirsin. Sonuç değişmez.
- **Kesin kazanmalı çekiliş:** Kazandığın eşya havuzdan çıkarılıyor, yani **tekrar gelmiyor**. Her çekilişte fiyat artıyor. Sınırlı sayıda çekilişte bütün havuz biter. Büyük ödülün kaçıncı çekilişte garanti olduğunu toplam maliyetle karşılaştırıp karar ver.
- **Blind box ve şans değeri:** Şans değerin arttıkça büyük ödül ağırlığı (`grandPrizeWeights`) kademeli olarak yükseliyor.

### 3.5 Takas güvenliği (`server/trade.lua`), dolandırılmamak için
- İki taraf da onaylayınca **4 saniye (80 tick)** bekleniyor, sonra takas tamamlanıyor. Bu sürede onayı geri çekersen takas iptal olur.
- **Dikkat:** Ana kodda, bir taraf eşya ekleyip çıkardığında **diğer tarafın onayı otomatik sıfırlanmıyor** (moda özel bir kontrol yoksa). Eşya değiştirmek sadece iki taraf da onaylamadan önce mümkün.
  - **Kural:** **Her zaman en son sen onayla.** Onaylamadan hemen önce karşı tarafın koyduğu eşyaları yeniden kontrol et. Önce sen onaylarsan karşı taraf eşyasını değiştirip sonra onaylayabilir.

---

## 4. Çiftlik ve Skyblock verileri

### 4.1 Rancher (g1031) ekinleri (`crops.csv`)
| Ekin | Süre | Cube fiyatı |
|---|---|---|
| Buğday | 2 dk | 1 |
| Mısır | 5 dk | 1 |
| Havuç | 10 dk | 2 |
| Şeker kamışı | 20 dk | 3 |
| Pamuk | 30 dk | 4 |
| Çilek | 1 sa | 5 |
| Domates | 2 sa | 7 |
| Çam | 3 sa | 8 |
| Patates | 4 sa | 9 |
| Kakao | 8 sa | 11 |
| Kauçuk | 12 sa | 13 |
| İpek | 15 sa | 14 |

Her hasattan 1–2 ürün çıkar.
- **Oyundayken:** buğday ve mısır gibi kısa süreli ekinler zaman başına en çok ürünü verir.
- **Uyumadan / çıkmadan önce:** uzun süreli ekinler (kakao 8 sa, kauçuk 12 sa, ipek 15 sa) ek.
- En değerli ürünler işlenmiş ürünler: prenses tacı (1365), yıldız küpe (1309), mutluluk yüzüğü (725). Toplam 316 ürün var. Ham ürünü işleyip satmak çok daha kârlı.

### 4.2 Genel ekinler ve çalma mekaniği (`crops.csv`, ilk 5 satır)
Eşya 296 (buğday) ve 391 (havuç) gibi genel ekinler: 10 / 20 / 60 / 120 dk, hasatta 9–10 / 8–9 / 7–8 ürün.
**Çalınabilir miktar 1–2** ve hasattan sonra toparlanma süresi (100–900 sn) var. Başkasının tarlasından küçük bir miktar alınabiliyor. Kendi tarlanı **olgunlaşınca hemen hasat et.**

### 4.3 Skyblock için üretim tarifleri
`resources/recipe/` altında 471 tarif var (örs = 4 demir blok, işaret ateşi, büyü masası…). Skyblock'ta ne üretebileceğinin tam listesi bu. İleride bir arama aracı yapılabilir.

---

## 5. Geliştirici / test artıkları (güvenlik tespitleri)

Bunlar kodda **var olan** şeyler. Olduğu gibi, tespit olarak yazıyorum. Çalışır bir hile,
bot ya da adım adım istismar yöntemi **bilerek verilmedi**: bunların kullanımı oyunun
kurallarına aykırı, hesabı kalıcı banlatır ve çoğu zaten sunucu tarafında doğrulanıyor.

- **Debug port (`common/debugport.lua`).** İstemci açılışta yerel makinede (`127.0.0.1`)
  6661–6666 arası bir TCP debug portu ve bir UDP portu açıyor. Debug konsolu Lua `load()`
  ile komut çalıştırabiliyor (`poco_start`, sahne/eşya komutları vb.). Ayrıca sabit bir
  rapor sunucusuna (`47.243.80.43:10086`) cihaz bilgisi + kullanıcı id gönderiyor.
  Bu bir **geliştirici arayüzü**; yayın sürümünde açık kalması bir ayak izi. Sadece yerel
  arayüzden erişilebiliyor, uzaktan rastgele birine açık değil.
- **Otomasyon çatısı (`client/autotest/`, Poco SDK).** NetEase'in UI test aracı pakette
  gömülü. `localhost:8081` üstünden pencere tıklama, `GMMoveTo`, `CallScript`, `WaitWindow`
  gibi otomasyon komutları sunuyor. Bu, QA testleri için; oyun oynamayı otomatikleştiren bir
  **bot iskeleti olarak kötüye kullanılabilir**, o yüzden risk olarak not ediyorum.
- **Reklam ödülü istemci tarafında (`client/player/player_packet.lua` → `OnWatchAd`).**
  Belirli bir platformda (`getPlatformId()==1`) istemci, reklamın izlendiğini sunucuya
  kendisi bildiriyor (`code=1`). Yani reklam izleme doğrulaması **istemciye güveniyor**.
  Bu bir güven zafiyeti olarak görünüyor; ama ödülün gerçekten verilip verilmediği yine
  sunucudaki tetikleyicilere (`WATCH_AD_FINISHED`) bağlı ve orada sınır/doğrulama olabilir.
- **GM komutları (`client/gm.lua`, `server/gm.lua`).** Geliştirici komutları pakette var,
  ama bunlar normal oyuncuda yetki kontrolünden geçmiyor (sunucu reddediyor).
- **Menzil/hız istemci kontrollü değil.** Yakın dövüş menzili (4 blok) ve hareket
  sunucuda doğrulanıyor (bkz. bölüm 2.3). İstemciyi değiştirip "menzil uzatmak"
  işe yaramaz; sunucu sınırın dışındaki vuruşu düşürür.

**Özet:** Bu artıklar çoğunlukla QA/geliştirici amaçlı ve kritik işlemler (ödül, eşya,
menzil, takas) sunucuda doğrulanıyor. Bir avantaja çevirmek için verilebilecek pratik bir
yol yok; denemek banla sonuçlanır. Bu yüzden yukarıdakileri sadece "kodda ne var" diye
belgeliyorum, istismar rehberi olarak değil.

## 6. Neler yapılmadı ve neden
- `.so` motor dosyaları şifreli/paketli. Korumayı kırmak gerektiği için açılmadı.
- Çalışır hile, hız/menzil hilesi, otomatik bot ya da reklam ödülü atlatma **üretilmedi**.
  Sunucu menzil, bekleme süreleri ve ödülleri kendisi kontrol ediyor; ayrıca bunlar
  hesabın banlanmasına yol açar.

## 7. Sonraki adımlar
1. `recipe/*.json` + `RanchItems.csv` → aranabilir **tarif ve çiftlik planlayıcısı** (web sayfası).
2. Skyblock modunun indirilen dosyaları (`g1048`) telefondan alınırsa aynı yöntemle analiz edilip ada ekonomisi ve mağaza fiyatları çıkarılabilir.
3. Blockman Editor ile kendi Skyblock benzeri modunu yapmak. `editor_template` eklentisi bu sistemin bir örneği.
