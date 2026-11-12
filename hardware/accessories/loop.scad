// Piblo removable case-edge clip with lanyard/keyring eye. UNTESTED.
// Print with supports under the upper jaw. Check grip before attaching Piblo.
include <../case/case_dimensions.scad>
hole_d = 5;
gap = dev_T_block + clr_z + plate_t + floor_t + 0.5;
eye_d = max(3, min(8, hole_d));
$fn = 40;
union() {
    difference() {
        cube([13, 16, gap+6]);
        translate([3, -0.1, 3]) cube([10.1, 16.2, gap]);
    }
    difference() {
        hull() {
            translate([-6,8,0]) cylinder(d=eye_d+7, h=3);
            translate([1,8,0]) cylinder(d=eye_d+7, h=3);
        }
        translate([-6,8,-0.1]) cylinder(d=eye_d, h=3.2);
    }
}
