"""ItemGun.csv'den silah DPS tablosu üretir.

Kullanım: python3 tools/gun_stats.py <ItemGun.csv> [en.lang]
CdTime saniye, ReloadTime tick (1 sn = 20 tick) cinsindendir.
"""
import csv
import sys

TYPES = {"1": "Tabanca", "2": "Tüfek", "3": "Sniper", "4": "Pompalı", "5": "SMG"}


def load_names(path):
    names = {}
    if path:
        for line in open(path, encoding="utf-8", errors="ignore"):
            key, _, val = line.strip().partition("=")
            if key.startswith("gui_gun_name_"):
                names[key.replace(".name", "")] = val
    return names


def main():
    rows = list(csv.reader(open(sys.argv[1], encoding="utf-8-sig"), delimiter="\t"))
    names = load_names(sys.argv[2] if len(sys.argv) > 2 else None)
    ix = {k: i for i, k in enumerate(rows[0])}
    out = []
    for r in rows[2:]:
        try:
            g = lambda k: r[ix[k]].strip()
            cd, dmg = float(g("CdTime")), float(g("Damage"))
            pellets = float(g("BulletPerShoot") or 1)
            mag, reload_s = float(g("MaxBulletNum")), float(g("ReloadTime")) / 20
        except (ValueError, IndexError, KeyError):
            continue
        burst = dmg * pellets / cd
        sustained = dmg * pellets * mag / (mag * cd + reload_s)
        out.append((g("GunId"), names.get(g("Name"), g("Name")), TYPES.get(g("GunType"), g("GunType")),
                     dmg, int(pellets), cd, int(mag), reload_s, round(burst, 1), round(sustained, 1)))
    print("id|isim|tip|hasar|saçma|atış arası(s)|şarjör|reload(s)|anlık DPS|sürekli DPS")
    for o in sorted(out, key=lambda x: -x[-1]):
        print(*o, sep="|")


if __name__ == "__main__":
    main()
