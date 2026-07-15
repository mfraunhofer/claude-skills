#!/usr/bin/env bash
# seo-geo-audit: image -> responsive WebP (ffmpeg/libwebp).
#
# Produces one WebP variant per target width: <base>-<width>.webp (for a <picture>
# srcset). With no widths: one WebP at original size (<base>.webp).
#
# Usage:
#   ./to-webp.sh hero.jpg 1600 1024      # -> hero-1600.webp, hero-1024.webp
#   ./to-webp.sh icon.png                # -> icon.webp (original size)
#
# Default quality 78 (good/small for photos). Override: Q=82 ./to-webp.sh ...
set -euo pipefail
command -v ffmpeg >/dev/null || { echo "ffmpeg missing (brew install ffmpeg / apt install ffmpeg)"; exit 1; }

SRC="${1:?Usage: to-webp.sh <image> [width ...]}"
[ -f "$SRC" ] || { echo "not found: $SRC"; exit 1; }
shift
Q="${Q:-78}"
DIR=$(dirname "$SRC"); BASE=$(basename "$SRC"); STEM="${BASE%.*}"

osize=$(wc -c < "$SRC" | tr -d ' ')
echo "Source: $SRC ($((osize/1024)) KB), quality $Q"

if [ "$#" -eq 0 ]; then
  OUT="$DIR/$STEM.webp"
  ffmpeg -y -loglevel error -i "$SRC" -c:v libwebp -quality "$Q" "$OUT"
  printf '  -> %s (%s KB)\n' "$OUT" "$(( $(wc -c < "$OUT") / 1024 ))"
else
  for W in "$@"; do
    OUT="$DIR/$STEM-$W.webp"
    ffmpeg -y -loglevel error -i "$SRC" -vf "scale=$W:-1" -c:v libwebp -quality "$Q" "$OUT"
    printf '  -> %s (%s KB)\n' "$OUT" "$(( $(wc -c < "$OUT") / 1024 ))"
  done
fi

echo
echo "Embed in HTML as <picture> (example):"
echo '  <picture>'
echo "    <source type=\"image/webp\" srcset=\"$STEM-1024.webp 1024w, $STEM-1600.webp 1600w\" sizes=\"100vw\" />"
echo "    <img src=\"$BASE\" width=\"W\" height=\"H\" loading=\"lazy\" decoding=\"async\" alt=\"…\" />"
echo '  </picture>'
echo "For the LCP hero also: <link rel=preload as=image type=image/webp ...> + fetchpriority=high, loading=eager."
