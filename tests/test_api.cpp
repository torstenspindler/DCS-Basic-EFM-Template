// Separate test binary to avoid duplicate mains; we will compile and link this
// file into its own executable.
#include <cassert>
#include <cmath>
#include <iostream>

#include "include/FM/API_Declare.h"
#include "Inputs.h"
#include "Utility.h"

static bool nearlyEqual(double a, double b, double eps = 1e-9) {
    return std::fabs(a - b) <= eps * std::max(1.0, std::max(std::fabs(a), std::fabs(b)));
}

int main() {
    // Start conditions
    ed_fm_cold_start();

    // Keep this a smoke test that avoids running the full simulator step
    // to keep it platform-agnostic and side-effect free.

    // Draw args array gets populated based on internal control states
    EdDrawArgument args[200] = {};
    ed_fm_set_draw_args(args, 200);

    // Gear should be down after cold start
    assert(args[0].f >= 0.99f);

    // Get some params: internal fuel starts at 0 by default in template
    double internal_fuel = ed_fm_get_param(ED_FM_FUEL_INTERNAL_FUEL);
    assert(nearlyEqual(internal_fuel, ed_fm_get_internal_fuel()));

    // Shake amplitude is a valid non-negative number
    // shake amplitude accessor not declared in API_Declare.h in this template; skip direct call

    std::cout << "Basic API smoke tests passed\n";
    return 0;
}
