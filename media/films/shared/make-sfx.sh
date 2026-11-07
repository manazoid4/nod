#!/usr/bin/env bash
# Synthesised, royalty-free sound effects for the Piblo films (no third-party audio).
set -e; cd "$(dirname "$0")"
# one soft key click: 30 ms band-passed noise with a fast decay
ffmpeg -v error -y -f lavfi -i "aevalsrc=exp(-t*170)*(0.5*sin(2*PI*2300*t)+0.5*(random(1)*2-1))*0.7:d=0.045:s=48000" -af "highpass=f=900,lowpass=f=7000" click.wav
# typing: 16 clicks with human-ish spacing over ~1.7 s
T="0 0.09 0.21 0.30 0.46 0.55 0.63 0.74 0.86 0.98 1.07 1.16 1.29 1.37 1.48 1.62"
IN=""; MIX=""; i=0
for t in $T; do IN="$IN -i click.wav"; MIX="$MIX[$i]adelay=$(awk "BEGIN{print int($t*1000)}")|$(awk "BEGIN{print int($t*1000)}"),volume=$(awk "BEGIN{srand($i);print 0.7+rand()*0.3}")[a$i];"; i=$((i+1)); done
L=""; for j in $(seq 0 $((i-1))); do L="$L[a$j]"; done
ffmpeg -v error -y $IN -filter_complex "${MIX}${L}amix=inputs=$i:normalize=0" -t 2 typing.wav
# saved chime: two soft sine partials, gentle decay
ffmpeg -v error -y -f lavfi -i "sine=f=880:d=1.2:r=48000" -f lavfi -i "sine=f=1318.5:d=1.2:r=48000" -filter_complex "[0]volume=0.22,afade=t=out:st=0.02:d=1.15:curve=exp[a];[1]adelay=90|90,volume=0.16,afade=t=out:st=0.1:d=1.0:curve=exp[b];[a][b]amix=inputs=2:normalize=0,afade=t=in:d=0.008,volume=7" chime.wav
# warm room tone bed so graphic scenes are not dead silent
ffmpeg -v error -y -f lavfi -i "anoisesrc=d=30:c=brown:a=0.05:r=48000" -af "lowpass=f=500,volume=0.5" room.wav
