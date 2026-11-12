// Piblo open wall/fridge cradle. UNTESTED: verify retention and fasteners.
include <../case/case_dimensions.scad>
attachment = "screw"; // "screw" or "magnet"; glue magnets into rear pockets.
case_L = dev_L + 2*(clr + wall) + 1;
case_W = dev_W + 2*(clr + wall) + 1;
case_T = dev_T_block + clr_z + plate_t + floor_t;
base_t = 4;
$fn = 40;
difference() {
    union() {
        translate([-case_L/2-3, -case_W/2-3, 0]) cube([case_L+6, case_W+6, base_t]);
        // Shallow side guides leave the case ports open above the back edge.
        for (s = [-1,1]) translate([s*(case_L/2+1.5)-1.5, -case_W/2, base_t])
            cube([3, case_W, 5]);
        translate([-case_L/2-3, -case_W/2-3, base_t]) cube([case_L+6, 3, case_T+2]);
        translate([-case_L/2-3, -case_W/2-3, base_t+case_T]) cube([case_L+6, 6, 2]);
        if (attachment == "screw") for (s = [-1,1])
            translate([s*(case_L/2+8), 0, 0]) cylinder(d=20, h=base_t);
    }
    // Open centre preserves rear airflow.
    translate([-case_L/2+18, -case_W/2+16, -0.1]) cube([case_L-36, case_W-32, base_t+0.2]);
    if (attachment == "screw") for (s = [-1,1])
        translate([s*(case_L/2+8), 0, -0.1]) cylinder(d=4.5, h=base_t+0.2);
    if (attachment == "magnet") for (x = [-1,1], y = [-1,1])
        translate([x*(case_L/2-10), y*(case_W/2-10), -0.1]) cylinder(d=10.3, h=3.2);
}
