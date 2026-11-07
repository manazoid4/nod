# Nod case for the M5Stack Cardputer ADV

**Status: NOT test-printed.** The geometry renders cleanly in OpenSCAD 2021.01 (STLs are manifold-simple),
but nobody has fitted a real Cardputer ADV in it yet. Several port positions are scaled estimates; see
`DIMENSIONS.md`. Expect one or two tweak iterations.

## Files

- `nod_case.scad` : parametric source. All sizes, clearances and options are named variables at the top.
- `DIMENSIONS.md` : every dimension with its source URL, or marked OWNER-MEASURE.
- `stl/nod_back.stl`, `stl/nod_frame.stl` : parts in assembly orientation (Z = 0 at the device back).
- `stl/nod_print_plate.stl` : both parts laid out in print orientation (back shell floor down, frame flipped front-face down).
- `preview*.png` : OpenSCAD renders (front, top, back with "nod" mark, exploded with device ghost).

Render yourself: `openscad -o stl/nod_back.stl -D 'part="back"' nod_case.scad` (parts: `back`, `frame`,
`assembly`, `exploded`, `print_plate`). PNG needs a display, e.g. `xvfb-run openscad -o p.png --imgsize=1200,900 nod_case.scad`.

## Design

Two parts wrapping the whole device: a back shell (tray with battery vents, embossed "nod" mark, optional
lanyard tab) and a front frame (rounded bezel, raised protective lip and flared window around the screen,
open keyboard window with keycaps recessed below the rim). Both are open over the M5 Stamp/antenna zone
(front window and rear slots) so no thick plastic sits over the antenna. Cut-outs: USB-C and speaker grille
(+X end), Grove window (-X end), one edge window for microSD / power switch / IR (screen-end edge), mic
pinhole. Joint: back shell has an inner lip that slides inside the frame skirt.

Options (top of the SCAD): `use_snaps` (default on, four dimple/bump pairs), `use_screws` (adds four ears for
M2 x 12 screws from the front down into the back shell; 1.7 mm pilots for self-tapping, use 3.2 mm for heat-set
inserts), `use_lanyard`, `use_nod_mark`, `use_vents`, `antenna_open`. No glue. The larger pop-in screen module
rail is only a commented placeholder.

## Print profile (suggested, untested)

- Material: PETG preferred (snaps flex better and survive heat from the battery); PLA works for fit checks.
- Layer height 0.2 mm, 0.4 mm nozzle, 3 walls (min 1.2 mm skirt/lip must stay solid), 4 top/bottom layers, infill 15% gyroid.
- Back shell: floor on the bed, no supports needed (vent slots and the "nod" recess print flat; the letters sit flush with the bed face). Ironing off.
- Front frame: print front face down (as in `nod_print_plate.stl`). The keyboard-zone ledge needs support
  (tree supports, only under that 1.5 mm ledge); keep supports off the screen window chamfer if possible.
- Ear/screw option: print ears with 100% infill around holes (4 walls).
- Tune `clr`, `clr_z`, `joint_gap` and `hole_tol` first if parts are tight or loose.

## Assembly

1. Switch the Cardputer off. Drop it into the back shell, screen end toward the +Y edge window, USB-C end toward the speaker holes.
2. Check the USB-C slot, microSD/switch window and Grove window line up with the ports.
3. Press the front frame down over the device until the skirt covers the lip and the snaps click (or fit four M2 x 12 screws if `use_screws` is on).
4. To open: pry gently at the snaps with a guitar pick (or remove screws).

## Fit-check checklist

- [ ] Device drops in without force; no bulging of the walls.
- [ ] All 56 keys press freely and return (keycap rim not touching the frame window).
- [ ] USB-C plug seats fully (try a bulky plug, not just a thin cable).
- [ ] microSD card inserts and ejects; power switch slides with a fingernail.
- [ ] Grove cable plugs in; IR emitter has a clear line of sight.
- [ ] Screen fully visible at about 45 degrees; lip keeps the glass off the table.
- [ ] Speaker audible; mic picks up voice through the front pinhole.
- [ ] Wi-Fi/BT range (RSSI) unchanged versus bare device with the case on.
- [ ] After 30 minutes of use the back shell is not hot to the touch; vents clear.
- [ ] Frame snaps open and closed several times without cracking.

## Known weak points

Port positions marked SCALED/OWNER-MEASURE; thin 1.2 mm lip/skirt; snap geometry untested; Grove window is oversize on purpose;
the 3.5 mm jack and two small edge slots have no published location and are covered.
