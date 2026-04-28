// --- Parameters ---
hole_d = 3.4;           // Protoboard hole diameter
peg_height = 12;        // Total height of the peg
taper_ratio = 1.3;      // How much wider the base is than the hole
clearance = 0.4;        // Reduction for the tip to ensure easy entry

// Base Plate Parameters
plate_h = 1.5;          // Thickness of the individual base plate
plate_d = 15.0;         // Diameter of the individual base plate

// --- Modules ---

module tapered_peg() {
    $fn = 64;
    cylinder(h = peg_height, 
             d1 = hole_d * taper_ratio,  // Bottom is wider than hole
             d2 = hole_d - clearance);   // Top is narrower than hole
}

module base_plate() {
    $fn = 64;
    cylinder(h = plate_h, d = plate_d);
}


// Complete Stand Module
module individual_stand() {
    base_plate();
    tapered_peg();
}

// Render one stand
individual_stand();