// --- User Settings ---
switch_width = 14.3;      // Square hole for the switch body
leg_height = 5.0;         // Clearance for the Hall Effect sensor
wall_thickness = 3.0;     // Thickness of the bridge legs
pin_diameter = 0.8;       // Fit for breadboard holes
pin_length = 3.5;         // Total depth of the peg
fillet_height = 1.;      // How far the reinforcement extends down the peg

/* [Calculated Dimensions] */
grid = 2.54;
outer_size = switch_width + (wall_thickness * 2);
// Align pins to the nearest 2.54mm breadboard hole
pin_offset = round((outer_size / 2 - 1.5) / grid) * grid;

$fn = 64;

module breadboard_bridge() {
    union() {
        // 1. The Main Frame (The Garage)
        difference() {
            translate([0, 0, leg_height / 2])
                cube([outer_size, outer_size, leg_height], center = true);
            
            // Hollow center for the sensor
            translate([0, 0, leg_height / 2])
                cube([switch_width, switch_width, leg_height + 1], center = true);
            
            // Side arches for wire access
                cube([outer_size + 2, switch_width - 3, leg_height + 2], center = true);
                cube([switch_width - 3, outer_size + 2, leg_height + 2], center = true);
        }

        // 2. The Mounting Plate (1.5mm standard)
        translate([0, 0, leg_height + 0.75])
            difference() {
                cube([outer_size, outer_size, 1.5], center = true);
                cube([switch_width, switch_width, 2], center = true);
            }

        // 3. Properly Reinforced Pins
        for (x = [-pin_offset, pin_offset]) {
            for (y = [-pin_offset, pin_offset]) {
                translate([x, y, 0]) {
                    // CONICAL FILLET
                    // This starts at the base and tapers down into the pin
                    // We use negative Z to ensure it goes DOWN from the base
                    translate([0, 0, -fillet_height])
                        cylinder(d1 = pin_diameter, d2 = pin_diameter + (fillet_height * 1.5), h = fillet_height); 
                    
                    // THE MAIN PEG
                    // Starts from the end of the fillet to reach total pin_length
                    translate([0, 0, -pin_length])
                        cylinder(d = pin_diameter, h = pin_length - fillet_height + 0.2);
                }
            }
        }
    }
}

breadboard_bridge();