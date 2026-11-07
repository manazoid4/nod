#!/usr/bin/env bash
# Rebuild and render the three Nod films, then master audio and make web versions + posters.
# Needs: node, ffmpeg, npx (HyperFrames 0.9.20 is fetched on demand).
set -e
cd "$(dirname "$0")"
OUT=../out; mkdir -p $OUT
node build.mjs
for f in product everyday launch; do
  (cd $f && npx -y hyperframes@0.9.20 render -q delivery -f 30 -o ../$OUT/raw-$f.mp4 --skill=hyperframes)
  # master: fixed +6 dB gain and a -1.5 dBTP limiter (loudnorm would pump the quiet room tone), 1080x1920 H.264 30 fps, AAC 48 kHz, fast start
  ffmpeg -v error -y -i $OUT/raw-$f.mp4 -c:v copy -af "volume=6dB,alimiter=limit=0.84:level=false" -ar 48000 -c:a aac -b:a 192k -movflags +faststart $OUT/nod-$f-final.mp4
done
echo "done: $(ls $OUT)"
