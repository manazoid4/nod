#!/usr/bin/env bash
# Rebuild and render the three Piblo films, then master audio and make web versions + posters.
# Needs: node, ffmpeg, npx (HyperFrames 0.9.20 is fetched on demand).
set -e
cd "$(dirname "$0")"
OUT=../out; mkdir -p $OUT
node build.mjs
for f in product everyday launch; do
  (cd $f && npx -y hyperframes@0.9.20 render -q delivery -f 30 -o ../$OUT/raw-$f.mp4 --skill=hyperframes)
  # master: fixed +6 dB gain and a -1.5 dBTP limiter (loudnorm would pump the quiet room tone), 1080x1920 H.264 30 fps, AAC 48 kHz, fast start
  ffmpeg -v error -y -i $OUT/raw-$f.mp4 -c:v copy -af "volume=6dB,alimiter=limit=0.84:level=false" -ar 48000 -c:a aac -b:a 192k -movflags +faststart $OUT/piblo-$f-final.mp4
done
# website versions (site/media): 720x1280 H.264 CRF 26 + AAC 96k, posters, link preview, exploded image
W=../../site/media; S=../stills; mkdir -p $W $S
for f in everyday product launch; do
  ffmpeg -v error -y -i $OUT/piblo-$f-final.mp4 -vf scale=720:1280:flags=lanczos -c:v libx264 -preset slow -crf 26 -profile:v high -pix_fmt yuv420p -c:a aac -b:a 96k -movflags +faststart $W/piblo-$f.mp4
done
ffmpeg -v error -y -ss 1.2 -i $OUT/piblo-everyday-final.mp4 -frames:v 1 -vf scale=720:1280 -q:v 4 $W/piblo-everyday-poster.jpg
ffmpeg -v error -y -ss 3.6 -i $OUT/piblo-product-final.mp4 -frames:v 1 -vf scale=720:1280 -q:v 4 $W/piblo-product-poster.jpg
ffmpeg -v error -y -ss 9.6 -i $OUT/piblo-launch-final.mp4 -frames:v 1 -vf scale=720:1280 -q:v 4 $W/piblo-launch-poster.jpg
ffmpeg -v error -y -ss 3.6 -i $OUT/piblo-product-final.mp4 -frames:v 1 -q:v 2 $OUT/piblo-thumbnail.jpg
# stills: clean device renders (Flow references) and the label-free exploded view for the site
SNAP=$(cd stills && npx -y hyperframes@0.9.20 snapshot --at 0.5,1.5,2.5,3.5,5.5 | tr "\\\\" "/" | grep -oE "[A-Za-z]:/[^ ]*frame-00[^ ]*png" | head -1); SNAP=$(dirname "$SNAP")
i=0; for n in piblo-original-orange piblo-classic-cream piblo-mint piblo-concept-still piblo-exploded-bare; do
  cp "$SNAP"/frame-0$i-*.png $S/$n-full.png; i=$((i+1))
  [ $n = piblo-exploded-bare ] || ffmpeg -v error -y -i $S/$n-full.png -vf crop=1080:900:0:540 $S/$n.png
done
ffmpeg -v error -y -i $S/piblo-exploded-bare-full.png -vf crop=1080:1460:0:340 -quality 82 $W/piblo-exploded.webp
# link preview card: typographic, no render. Source media/marketing/og.html (1200x630), screenshot saved as site/media/piblo-og.jpg
echo "done: $(ls $OUT) + site/media"
