// Piblo desk stand. UNTESTED: check balance, fit and access before use.
include <../case/case_dimensions.scad>
angle = 60; // Screen angle above the desk, degrees; 30..80.
a = max(30, min(80, angle));
case_L = dev_L + 2*(clr + wall);
case_W = dev_W + 2*(clr + wall);
case_T = dev_T_block + clr_z + plate_t + floor_t;
width = case_L + 2;
toe = case_T*sin(a) + 5;
run = case_W*cos(a);
rise = case_W*sin(a);
depth = toe + run + 15;
union() {
    translate([-width/2, 0, 0]) rotate([90, 0, 90]) linear_extrude(width)
        polygon([[0,0], [depth,0], [toe+run,rise+3], [toe,3], [0,3]]);
    // Front stop retains the lower edge; side faces stay open for cables.
    translate([-width/2, 0, 3]) cube([width, 3, case_T*cos(a)+7]);
}
