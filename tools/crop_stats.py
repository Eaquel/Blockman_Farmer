"""crops.csv + RanchItems.csv'den ekin süre/verim tablosu üretir.

Kullanım: python3 tools/crop_stats.py <crops.csv> <RanchItems.csv>
"""
import csv
import sys


def read(path):
    return list(csv.reader(open(path, encoding="utf-8-sig"), delimiter="\t"))


def main():
    crops, ranch = read(sys.argv[1]), read(sys.argv[2])
    price = {r[1]: (r[2], r[7]) for r in ranch[2:] if len(r) > 7}
    print("ekin|ürün|toplam süre(dk)|hasat|çalınabilir|toparlanma(s)|cube fiyatı")
    for r in crops[2:]:
        if len(r) < 12:
            continue
        total = sum(int(x) for x in r[3:7])
        name, cube = price.get(r[10], (r[10], "-"))
        print(r[1], name.replace("_ranch_item_name_", " "), round(total / 60, 1),
              r[8].replace("#", "-"), r[9].replace("#", "-"), r[7], cube, sep="|")


if __name__ == "__main__":
    main()
