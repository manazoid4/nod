# Cardputer ADV dimensions and sources

Axes used in `nod_case.scad`: X = 84 mm long axis (+X = USB-C / M5 Stamp end),
Y = 54 mm short axis (+Y = screen end, -Y = keyboard end), Z = 0 at the back face.

## Sources

- S1: M5Stack Cardputer-Adv docs page. https://docs.m5stack.com/en/core/Cardputer-Adv
- S2: Official dimension drawing PDF (K132-Adv). https://m5stack-doc.oss-cn-shenzhen.aliyuncs.com/1178/K132-Adv-cardputer-ADV.pdf
- S3: Official structure file `Cardputer-Adv.stl` (an assembly mesh with internals; I analysed it numerically).
  https://github.com/m5stack/M5_Hardware/tree/master/Products/K132-Adv_Cardputer-Adv/Structures
- S4: CNX Software launch article (cross-check only). https://www.cnx-software.com/2025/10/23/m5stack-cardputer-adv-esp32-s3-computer-gains-improved-antenna-larger-1750-mah-battery-es8311-audio-codec/

Note: S1's change log says the battery was changed from 1750 mAh to 1500 mAh (2026-07-13). Battery pack size
is not published; treat the rear volume as full (back face is flat in S3).

## OFFICIAL (printed on S1/S2)

| Item | Value | Source |
|---|---|---|
| Length x width x max thickness | 84.0 x 54.0 x 19.6 mm | S1, S2 |
| Thickness at keyboard section | 16 mm | S2 (drawing "16") |
| Front M2 screws | 13 mm from left edge, 41.5 mm apart, 36 mm from keyboard-end edge (18 mm from screen end) | S2 |
| Rear M2 screws | 29.5 mm from left edge, 41.5 mm apart, 36 mm from keyboard-end edge | S2 (not used by the case) |
| Rear corner features | 6 / 8 / 56 / 8 mm spacing along the screen-end edge, 14 mm row offset | S2 (covered by back shell; magnets/LEGO holes) |
| Screen | ST7789V2 1.14", 240x135 | S1 |
| Keyboard | 56 keys (4 x 14) | S1 |
| Weight | 81 g | S1 |
| Features present | USB-C, microSD, Grove HY2.0-4P, EXT 2.54-14P, IR emitter, MEMS mic, 8 ohm speaker, 3.5 mm jack, side power switch, lanyard hole | S1 |

## SCALED (read off S2/S3 by me, about +-0.5 mm, verify)

| Item | Value | Basis |
|---|---|---|
| Keycap pitch | 5.8 mm (X) x 7.5 mm (Y) | S3 mesh, keycap top clusters |
| Keycap top size | 3.64 x 2.14 mm; top at Z = 17.0 | S3 |
| Keyboard plate top | Z = 16.0 (keycaps +1.0) | S3 |
| Thick-end block | Y = 6.2 .. 27, Z up to 19.68 | S3 (step at 20.8 mm from screen-end edge) |
| Corner radius | 3.0 mm keyboard end, 1.7 mm screen end | S3 outline fit |
| Screen window | about 24.9 x 15.5 mm, centre (-8.85, 16.55) | S2 front view scaled |
| USB-C opening, +X end | about 11 x 3.3 mm, centre Y = 17.4, Z = 16.5..19.8 | S3 end view |
| Speaker holes, +X end | 3-4-4-3 pattern, centre Y = 18.2, Z = 12.6 | S3 end view |
| Power switch, screen-end edge | centre X about +9, Z about 13 | S2 bottom view, S3 |
| microSD slot, screen-end edge | centre X about -8, Z about 12-16 | S2 bottom view, S3 (uncertain Z) |

## OWNER-MEASURE (placeholders; measure with calipers)

| Item | Placeholder in SCAD | Why |
|---|---|---|
| Grove port window, -X end | Y 8..25, Z >= 11 (deliberately oversize) | position not published, not clear in mesh |
| IR emitter position | covered by the +Y edge window (X -17..15, Z 9..17.5) | not published |
| microSD slot exact X/Z and card clearance | edge window above | uncertain |
| Mic pinhole | front, X -34.5, Y 8.7, 1.8 mm | inferred from small holes in S2 front view |
| Antenna / Stamp keep-out | X 16.5..40, Y 7.5..24.5 | inferred from Stamp position in S3 |
| 3.5 mm audio jack location | not cut (no location published) | add a window if you use it |
| Two rounded slots on screen-end edge (X about -27 and +20, about 5.4 wide) | left covered | purpose unknown (latch/lanyard/magnet?) |
| Device lanyard hole | not used; case has its own tab | location not published |
| Real corner radii, wall tolerances of your unit | 3.0 / 1.7 | fit-check on a real unit |

## Measure with calipers (in this order)

1. Total thickness at the screen end and at the keycap tops (confirm 19.6 and about 17).
2. Y position of the thick-end step from the screen-end edge (expect 20.8 mm).
3. Grove port: centre offset from the -X end/screen-end edge, width, height above the back.
4. microSD slot and power switch: X centre and Z centre on the screen-end edge.
5. Screen glass: left offset, width, height (expect 24.9 x 15.5, centre 8.85 left of middle).
6. USB-C opening: centre and height above the back.
