// =====================================================================
// Nod case for the M5Stack Cardputer ADV  --  parametric, two parts
//   part 1: back shell  (tray, vents, embossed "nod" mark, lanyard tab)
//   part 2: front frame (bezel with screen lip, keyboard window)
// NOT TEST-PRINTED.  See README.md and DIMENSIONS.md.
//
// Licence: same as the repo (see /LICENSE).  No third-party libraries.
// OpenSCAD 2021.01 or newer.
//
// COORDINATES (device frame):
//   X = long axis (84 mm), +X end = USB-C / speaker / M5 Stamp end
//   Y = short axis (54 mm), +Y edge = screen end (SD slot, power switch),
//                           -Y edge = keyboard end
//   Z = thickness, Z=0 is the device BACK face, +Z is the front.
//
// Every dimension is tagged:
//   [OFFICIAL] from M5Stack drawing / official STL (see DIMENSIONS.md)
//   [SCALED]   read off the official drawing/STL by me, about +-0.5 mm
//   [OWNER-MEASURE] placeholder estimate: verify with calipers
// =====================================================================

// ---------- what to render ------------------------------------------
// "assembly" | "back" | "frame" | "exploded" | "print_plate"
part = "assembly";
show_device_ghost = true;   // translucent Cardputer in previews only

// ---------- options --------------------------------------------------
use_snaps      = true;    // snap-fit dimples/bumps (no screws needed)
use_screws     = false;   // add 4 M2 ears; screws go frame -> back shell
use_lanyard    = true;    // lanyard tab on the -X end
use_nod_mark   = true;    // embossed "nod" on back
use_vents      = true;    // battery heat vents in the back shell floor
antenna_open   = true;    // open windows over the Stamp/antenna zone
// FUTURE (placeholder only, not implemented): pop-in larger screen
// module rail. See the commented block near the end of this file.

// ---------- print tolerances ----------------------------------------
include <case_dimensions.scad> // Shared unchanged dimensions; also used by accessories.
joint_gap = 0.18;  // gap between back-shell lip and frame skirt
snap_depth= 0.40;  // snap bump height
hole_tol  = 0.20;  // added to round holes (printer undersizing)

// ---------- device dimensions ---------------------------------------
dev_T_plate  = 16.0;   // [OFFICIAL] thickness at keyboard plate (drawing "16")
key_top_z    = 17.0;   // [SCALED]  keycap top above back (STL: 17.0)
block_y0     = 6.2;    // [SCALED]  block (thick end) spans Y=block_y0..+27
r_kb         = 3.0;    // [SCALED]  corner radius, keyboard end (STL)
r_scr        = 1.7;    // [SCALED]  corner radius, screen end (STL)

// keyboard: 14 columns x 4 rows
key_cols     = 14;
key_pitch_x  = 5.8;    // [SCALED] STL, along X
key_row_pitch= 7.5;    // [SCALED] STL, along Y
key_w_top    = 3.64;   // [SCALED] keycap top width (X)
key_h_top    = 2.14;   // [SCALED] keycap top height (Y)
key_row0_y   = 0.0;    // [SCALED] centre of row nearest screen
key_rows     = 4;

// screen window (visible glass) -- scaled from the official drawing
scr_cx = -8.85;        // [SCALED]
scr_cy = 16.55;        // [SCALED]
scr_w  = 24.9;         // [SCALED]
scr_h  = 15.5;         // [SCALED]

// ports (positions scaled from official STL end views; verify!)
usb_cy   = 17.4;  usb_w = 11.0;  usb_z0 = 16.5;  usb_h = 3.3;  // [SCALED] +X end
spk_cy   = 18.2;  spk_cz = 12.6; spk_pitch = 2.2; spk_d = 1.3; // [SCALED] +X end
grove_y0 = 8.0;   grove_y1 = 25.0; grove_z0 = 11.0;            // [OWNER-MEASURE] -X end
edge_x0  = -17.0; edge_x1  = 15.0; edge_z0 = 9.0; edge_z1 = 17.5; // [SCALED] +Y edge: SD slot (~X=-8), switch (~X=+9)
mic_x = -34.5;    mic_y = 8.7;     mic_d  = 1.8;               // [OWNER-MEASURE] front mic pinhole
ant_x0 = 16.5; ant_x1 = 40.0; ant_y0 = 7.5; ant_y1 = 24.5;     // [OWNER-MEASURE] Stamp/antenna keep-out
front_screw_pts = [[-29, 9], [12.5, 9]];  // [OFFICIAL] drawing: 13 from edge, 41.5 apart, 18 from screen end

// ---------- case design parameters ----------------------------------
z_split   = 8.0;      // joint height (device Z) between parts
lap       = 3.0;      // overlap height of lip inside skirt
edge_r    = 1.4;      // soft outer edge rounding
lip_h     = 0.7;      // protective bezel lip height around screen
lip_w     = 1.2;      // bezel lip width
scr_flare = 0.6;      // chamfer on screen window (viewing angle)
scr_margin= 0.3;      // window oversize vs scr_w/scr_h
key_margin= 0.9;      // keyboard window oversize vs keycaps

// derived
o     = clr + wall;                 // outer offset from device outline
wl    = wall / 2;                   // lip thickness
Zk_in = dev_T_plate + clr_z;        // frame underside over keyboard plate
Zb_in = dev_T_block + clr_z;        // frame underside over block
Zk_top= Zk_in + plate_t;            // keyboard-zone rim top (keycaps recessed below)
Zb_top= Zb_in + plate_t;            // block-zone top

// ear / screw params
ear_r   = 2.8;
ear_x   = 26;
m2_pilot= 1.7;   // self-tapping into PLA/PETG; use 3.2 for heat-set M2 inserts
m2_clear= 2.4;
m2_head = 4.2;

$fn = 40;
eps = 0.01;

// ---------- helpers --------------------------------------------------
module dev2d(d = 0) {
    hull() for (sx = [-1, 1]) {
        translate([sx * (dev_L/2 - r_kb),  -dev_W/2 + r_kb]) circle(r = r_kb + d);
        translate([sx * (dev_L/2 - r_scr),  dev_W/2 - r_scr]) circle(r = r_scr + d);
    }
}
module rr(cx, cy, w, h, r = 1) {
    translate([cx, cy]) offset(r = r) square([w - 2*r, h - 2*r], center = true);
}
// convex solid, soft edges top and bottom
module soft(zb, zt, d0, rb, n = 6) {
    hull() {
        for (i = [0:n]) {
            a = 90 * i / n;
            translate([0, 0, zb + rb * (1 - cos(a))])
                linear_extrude(eps) dev2d(d0 - rb * (1 - sin(a)));
            translate([0, 0, zt - rb * (1 - cos(a))])
                linear_extrude(eps) dev2d(d0 - rb * (1 - sin(a)));
        }
    }
}
module slab(z0, z1, y0 = -100) { translate([-100, y0, z0]) cube([200, 200, z1 - z0]); }

// ---------- device ghost (for previews only) ------------------------
module device_ghost() {
    color("silver", 0.35) {
        linear_extrude(dev_T_plate) dev2d(0);
        intersection() {
            linear_extrude(dev_T_block) dev2d(0);
            slab(0, dev_T_block, block_y0);
        }
        for (c = [0:key_cols-1], r = [0:key_rows-1])
            translate([(c - (key_cols-1)/2) * key_pitch_x, key_row0_y - r*key_row_pitch, dev_T_plate - eps])
                translate([-key_w_top/2, -key_h_top/2, 0]) cube([key_w_top, key_h_top, key_top_z - dev_T_plate]);
    }
}

// ---------- outer solid ---------------------------------------------
module outer() {
    union() {
        soft(-floor_t, Zk_top, o, edge_r);
        intersection() {
            soft(-floor_t, Zb_top, o, edge_r);
            slab(-floor_t - 1, Zb_top + 1, block_y0 - clr);
        }
    }
}

// device cavity (everything the device occupies + clearance)
module cavity() {
    translate([0, 0, 0]) linear_extrude(Zk_in) dev2d(clr);
    intersection() {
        linear_extrude(Zb_in) dev2d(clr);
        slab(-1, Zb_in, block_y0 - clr);
    }
}

// ---------- cut-outs through the walls (both parts) -----------------
module cutouts() {
    // USB-C (+X end): rounded slot
    hull() for (dy = [-1, 1])
        translate([dev_L/2 - 1, usb_cy + dy * (usb_w/2 - usb_h/2), usb_z0 + usb_h/2])
            rotate([0, 90, 0]) cylinder(d = usb_h + 0.6, h = o + 3);
    // speaker grille: 3-4-4-3 holes, +X end
    for (r = [0:3]) {
        n = (r == 0 || r == 3) ? 3 : 4;
        for (i = [0:n-1])
            translate([dev_L/2 - 1, spk_cy + (i - (n-1)/2) * spk_pitch,
                       spk_cz + (r - 1.5) * spk_pitch])
                rotate([0, 90, 0]) cylinder(d = spk_d + hole_tol, h = o + 3, $fn = 16);
    }
    // Grove / EXT end (-X): generous until measured
    translate([-dev_L/2 - o - 2, grove_y0, grove_z0])
        cube([o + 3, grove_y1 - grove_y0, 30]);
    // screen-end edge access window: SD slot, power switch, (IR?)
    translate([edge_x0, dev_W/2 - 1, edge_z0])
        cube([edge_x1 - edge_x0, o + 3, edge_z1 - edge_z0]);
}

// ---------- back shell ----------------------------------------------
module ears(z0, z1) {
    if (use_screws)
        for (sx = [-1, 1], sy = [-1, 1])
            translate([sx * ear_x, sy * (dev_W/2 + o + 0.9), z0])
                linear_extrude(z1 - z0)
                    hull() {
                        circle(r = ear_r);
                        translate([0, -sy * 2.2]) square([2 * ear_r, 0.5], center = true);
                    }
}

module back_shell() {
    difference() {
        union() {
            intersection() { outer(); slab(-floor_t - 1, z_split); }
            // lip that slides inside the frame skirt
            translate([0, 0, z_split - eps]) linear_extrude(lap + eps)
                difference() { dev2d(clr + wl); dev2d(clr); }
            // snap bumps on the lip, outer face
            if (use_snaps)
                for (p = snap_pts()) snap_bump(p);
            ears(-floor_t, z_split);
            if (use_lanyard) lanyard_tab();
        }
        cavity();
        cutouts();
        if (use_screws)
            for (sx = [-1, 1], sy = [-1, 1])
                translate([sx * ear_x, sy * (dev_W/2 + o + 0.9), z_split - 6])
                    cylinder(d = m2_pilot + hole_tol, h = 7, $fn = 20);
        floor_features();
    }
}

function snap_pts() = [[-28, -1], [28, -1], [-28, 1], [28, 1]];
// bumps on the Y walls only; direction sy
module snap_bump(p) {
    sy = p[1];
    translate([p[0], sy * (dev_W/2 + clr + wl - 0.05), z_split + lap/2])
        scale([1, 1, 0.8]) sphere(r = snap_depth + 0.2, $fn = 20);
}
module snap_pocket(p) {
    sy = p[1];
    translate([p[0], sy * (dev_W/2 + clr + wl - 0.05), z_split + lap/2])
        scale([1, 1, 0.8]) sphere(r = snap_depth + 0.2 + 0.1, $fn = 20);
}

module lanyard_tab() {
    ty = -13;
    difference() {
        hull() {
            translate([-dev_L/2 - o + 0.5, ty - 5, -floor_t]) cube([1, 10, 4.5]);
            translate([-dev_L/2 - o - 6, ty, -floor_t]) cylinder(r = 5, h = 4.5);
        }
        translate([-dev_L/2 - o - 6, ty, -floor_t - 1])
            hull() for (dy = [-2.2, 2.2]) translate([0, dy, 0]) cylinder(d = 2.8, h = 8, $fn = 20);
    }
}

module floor_features() {
    if (use_vents)
        for (sx = [-1, 1], i = [0:4])
            translate([sx * 26 + (i - 2) * 3.2, -12, -floor_t - 1])
                hull() for (dy = [-7, 7]) translate([0, dy, 0]) cylinder(d = 1.5, h = floor_t + 2, $fn = 16);
    if (antenna_open)
        for (k = [0:2]) {
            h = (ant_y1 - ant_y0 - 2 * 1.2) / 3;
            translate([0, ant_y0 + k * (h + 1.2), -floor_t - 1])
                linear_extrude(floor_t + 2)
                    rr((ant_x0 + ant_x1)/2, h/2, ant_x1 - ant_x0, h, 1);
        }
    if (use_nod_mark) nod_mark_cut();
}

// raised "nod" letters standing in a shallow recess; letters are flush with
// the bed face so the shell prints flat. Mirrored so it reads correctly
// when you look at the back of the device.
emb = 0.6;
module nod_mark_2d() {
    mirror([1, 0]) text("nod", size = 8.5, font = "DejaVu Sans:style=Bold",
                        halign = "center", valign = "center", spacing = 1.05);
}
module nod_mark_cut() {
    translate([0, -3, -floor_t - eps]) {
        difference() {
            linear_extrude(emb) rr(0, 0, 34, 14, 5);
            translate([0, 0, -1]) linear_extrude(emb + 2) nod_mark_2d();
        }
    }
    // the cut above removes the recess *minus* letters: letters remain
}
// note: nod_mark_cut() is subtracted, so only the recess-minus-letters is
// removed and the letters stay standing at bed level.

// ---------- front frame ---------------------------------------------
module screen_win2d(d = 0) { rr(scr_cx, scr_cy, scr_w + 2*scr_margin + 2*d, scr_h + 2*scr_margin + 2*d, 1.5 + d); }

module front_frame() {
    kb_x = ((key_cols - 1)/2) * key_pitch_x + key_w_top/2 + key_margin;
    kb_y_top = key_row0_y + key_h_top/2 + key_margin;
    kb_y_bot = key_row0_y - (key_rows-1) * key_row_pitch - key_h_top/2 - key_margin;
    difference() {
        union() {
            intersection() { outer(); slab(z_split, Zb_top + 1); }
            // protective bezel lip around the screen
            translate([0, 0, Zb_top - eps]) linear_extrude(lip_h + eps) screen_win2d(lip_w);
            ears(z_split, Zk_top);
        }
        cavity();
        // widened cavity for the lip/skirt joint
        translate([0, 0, z_split - eps]) linear_extrude(lap + joint_gap + eps) dev2d(clr + wl + joint_gap);
        cutouts();
        // screen window with viewing-angle chamfer
        hull() {
            translate([0, 0, Zb_in - eps]) linear_extrude(eps) screen_win2d(0);
            translate([0, 0, Zb_top + lip_h - scr_flare]) linear_extrude(scr_flare + 1) screen_win2d(scr_flare);
        }
        // keyboard window
        translate([0, 0, Zk_in - 1]) linear_extrude(plate_t + 8)
            rr(0, (kb_y_top + kb_y_bot)/2, 2*kb_x, kb_y_top - kb_y_bot, 1.5);
        // Stamp/antenna zone: open, no plastic over the antenna
        if (antenna_open)
            translate([0, 0, Zb_in - 1]) linear_extrude(plate_t + 4)
                rr((ant_x0 + ant_x1)/2, (ant_y0 + ant_y1)/2, ant_x1 - ant_x0, ant_y1 - ant_y0, 2);
        // mic pinhole
        translate([mic_x, mic_y, Zb_in - 1]) cylinder(d = mic_d + hole_tol, h = plate_t + 3, $fn = 20);
        // snap pockets (inner face of skirt)
        if (use_snaps)
            for (p = snap_pts()) snap_pocket(p);
        if (use_screws)
            for (sx = [-1, 1], sy = [-1, 1])
                translate([sx * ear_x, sy * (dev_W/2 + o + 0.9), z_split - 1]) {
                    cylinder(d = m2_clear + hole_tol, h = 20, $fn = 20);
                    translate([0, 0, Zk_top - z_split - 2.2 + 1]) cylinder(d = m2_head + 0.4, h = 5, $fn = 24);
                }
    }
}

// ---------- FUTURE: pop-in larger screen module (placeholder) --------
// A rail/slot for a bigger display module could replace the screen
// window region of the frame: a 2 mm dovetail groove along X at
// Y = scr_cy +- 12, with a retaining detent at +X. Not designed yet,
// needs the module's dimensions first. Deliberately left as a comment.

// ---------- output ---------------------------------------------------
module assembly_view() {
    color("#2b2b33") back_shell();
    color("#e8e2d4") front_frame();
}

if (part == "back") back_shell();
else if (part == "frame") front_frame();
else if (part == "print_plate") {
    translate([0, -45, floor_t]) back_shell();
    // frame flipped (front face down) so the flat top prints on the bed
    translate([0, 45, Zb_top + lip_h]) rotate([180, 0, 0]) front_frame();
}
else if (part == "exploded") {
    color("#2b2b33") back_shell();
    translate([0, 0, 30]) color("#e8e2d4") front_frame();
    if (show_device_ghost) translate([0, 0, 12]) device_ghost();
}
else {
    assembly_view();
    if (show_device_ghost) device_ghost();
}
