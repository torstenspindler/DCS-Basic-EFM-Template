#include <cassert>
#include <cmath>
#include <iostream>

#include "Utility.h"

static bool nearlyEqual(double a, double b, double eps = 1e-9) {
    return std::fabs(a - b) <= eps * std::max(1.0, std::max(std::fabs(a), std::fabs(b)));
}

int main() {
    // rad/deg
    assert(nearlyEqual(rad(180.0), M_PI));
    assert(nearlyEqual(deg(M_PI), 180.0));

    // limit
    assert(nearlyEqual(limit(5.0, 0.0, 10.0), 5.0));
    assert(nearlyEqual(limit(-1.0, 0.0, 10.0), 0.0));
    assert(nearlyEqual(limit(20.0, 0.0, 10.0), 10.0));

    // actuator
    {
        double v = 0.0;
        // target 1.0, up_speed 0.1 increments
        for (int i = 0; i < 5; ++i) v = actuator(v, 1.0, -0.1, 0.1);
        assert(nearlyEqual(v, 0.5));
        // jump past target should clamp to target
        v = actuator(0.95, 1.0, -0.1, 0.1);
        assert(nearlyEqual(v, 1.0));
        // move down toward 0.0 using down_speed
        v = actuator(1.0, 0.0, -0.2, 0.2);
        assert(nearlyEqual(v, 0.8));
    }

    // rescale: [-1,1] -> [min,max]
    assert(nearlyEqual(rescale(1.0, -10.0, 15.0), 15.0));
    assert(nearlyEqual(rescale(-1.0, -10.0, 15.0), -10.0));
    assert(nearlyEqual(rescale(0.5, -10.0, 20.0), 10.0));
    assert(nearlyEqual(rescale(-0.5, -10.0, 20.0), -5.0));

    // cross product
    {
        Vec3 a(1, 0, 0);
        Vec3 b(0, 1, 0);
        Vec3 c = cross(a, b);
        assert(nearlyEqual(c.x, 0.0));
        assert(nearlyEqual(c.y, 0.0));
        assert(nearlyEqual(c.z, 1.0));
    }

    // lerp: use the FM_DATA tables to validate monotonic increasing output within bounds
    {
        double x[] = {0.0, 0.4, 0.8};
        double f[] = {0.0,  1.0, 2.0};
        assert(nearlyEqual(lerp(x, f, 3, -1.0), 0.0));
        assert(nearlyEqual(lerp(x, f, 3, 0.0), 0.0));
        assert(nearlyEqual(lerp(x, f, 3, 0.2), 0.5));
        assert(nearlyEqual(lerp(x, f, 3, 0.4), 1.0));
        assert(nearlyEqual(lerp(x, f, 3, 0.6), 1.5));
        assert(nearlyEqual(lerp(x, f, 3, 0.8), 2.0));
        assert(nearlyEqual(lerp(x, f, 3, 1.0), 2.0));
    }

    // smooth_lerp
    assert(nearlyEqual(smooth_lerp(0.0, 10.0, 0.0), 0.0));
    assert(nearlyEqual(smooth_lerp(0.0, 10.0, 1.0), 10.0));
    assert(nearlyEqual(smooth_lerp(0.0, 10.0, 0.5), 5.0));

    std::cout << "All Utility.h tests passed\n";
    return 0;
}
