#!/usr/bin/env bash
# Kullanım: tools/decompile.sh <Test_Blockman_Assets.zip> [çalışma_dizini]
# Zip'i açar, Lua 5.3 bytecode dosyalarını unluac ile okunabilir Lua'ya çevirir.
# .jit32/.jit64 dosyaları aynı kodun LuaJIT kopyalarıdır, atlanır.
set -euo pipefail
ZIP=${1:?zip yolu gerekli}
WORK=${2:-work}
HERE=$(cd "$(dirname "$0")" && pwd)
JAR=$HERE/unluac.jar
[ -f "$JAR" ] || curl -sSL -o "$JAR" "https://sourceforge.net/projects/unluac/files/latest/download"
mkdir -p "$WORK/raw" "$WORK/dec"
unzip -q -o "$ZIP" -d "$WORK/raw"
A=$(find "$WORK/raw" -maxdepth 2 -type d -name assets | head -1)
cd "$A"
find . -name '*.lua' ! -name '*.jit32.lua' ! -name '*.jit64.lua' | while read -r f; do
  out="../../../dec/$f"; mkdir -p "$(dirname "$out")"
  if head -c1 "$f" | grep -q $'\x1b'; then
    java -jar "$JAR" "$f" > "$out" 2>/dev/null || echo "FAIL $f"
  else
    cp "$f" "$out"
  fi
done
echo "Bitti: $WORK/dec"
