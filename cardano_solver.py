from decimal import Decimal, getcontext
import cmath
import math

# Set precision high enough for large numbers
getcontext().prec = 100

def cardano_formula(a, b, c, d):
    """
    Solve cubic equation ax³ + bx² + cx + d = 0 using Cardano's formula
    
    Args:
        a, b, c, d: Coefficients of x³, x², x¹, x⁰ respectively
    
    Returns:
        str: Three roots sorted and formatted as 'a+bi' separated by newlines
    """
    if a == 0:
        raise ValueError("Coefficient 'a' cannot be zero for a cubic equation")
    
    # Convert to Decimal for high precision
    a_dec, b_dec, c_dec, d_dec = Decimal(a), Decimal(b), Decimal(c), Decimal(d)
    
    # Normalize the equation by dividing by a
    b_dec, c_dec, d_dec = b_dec/a_dec, c_dec/a_dec, d_dec/a_dec
    
    # Convert to depressed cubic: t³ + pt + q = 0
    # Using substitution x = t - b/3
    p_dec = c_dec - b_dec**2 / 3
    q_dec = 2*b_dec**3/27 - b_dec*c_dec/3 + d_dec
    
    # Convert to float for complex arithmetic (preserve precision as much as possible)
    p = float(p_dec)
    q = float(q_dec)
    b_norm = float(b_dec)
    
    # Calculate discriminant
    delta = q**2/4 + p**3/27
    
    # Calculate the cube roots using complex arithmetic
    def complex_cube_root(z):
        """Calculate the principal cube root of a complex number"""
        if abs(z) < 1e-15:
            return complex(0, 0)
        
        # Use polar form: z = r * e^(i*theta)
        r = abs(z)
        theta = cmath.phase(z)
        
        # Cube root: z^(1/3) = r^(1/3) * e^(i*theta/3)
        cube_root_r = r ** (1/3)
        cube_root_theta = theta / 3
        
        return cube_root_r * cmath.exp(1j * cube_root_theta)
    
    # Calculate square root
    sqrt_delta = cmath.sqrt(delta)
    
    # Calculate u using the principal cube root
    u = complex_cube_root(-q/2 + sqrt_delta)
    
    # Calculate v using the constraint u*v = -p/3
    if abs(u) > 1e-10:
        v = -p / (3 * u)
    else:
        # If u is very small, calculate v directly
        v = complex_cube_root(-q/2 - sqrt_delta)
    
    # Complex cube roots of unity
    omega = complex(-1/2, math.sqrt(3)/2)
    omega2 = complex(-1/2, -math.sqrt(3)/2)
    
    # Three roots of depressed cubic
    t1 = u + v
    t2 = omega * u + omega2 * v
    t3 = omega2 * u + omega * v
    
    # Convert back to original equation (x = t - b/3)
    shift = b_norm / 3
    x1 = t1 - shift
    x2 = t2 - shift
    x3 = t3 - shift
    
    # Round to clean up floating point errors
    def clean_root(root):
        real = root.real
        imag = root.imag
        
        # Calculate relative tolerance based on magnitude
        real_mag = abs(real) if real != 0 else 1
        imag_mag = abs(imag) if imag != 0 else 1
        
        real_tolerance = max(1e-6, real_mag * 1e-9)
        imag_tolerance = max(1e-6, imag_mag * 1e-9)
        
        # Check if close to an integer
        if abs(real - round(real)) < real_tolerance:
            real = round(real)
        if abs(imag - round(imag)) < imag_tolerance:
            imag = round(imag)
        
        return complex(real, imag)
    
    roots = [clean_root(x1), clean_root(x2), clean_root(x3)]
    
    # Format as strings
    def format_complex(num):
        real = num.real
        imag = num.imag
        
        # Convert to int if they are whole numbers
        if real == int(real):
            real = int(real)
        if imag == int(imag):
            imag = int(imag)
        
        if imag >= 0:
            return f"{real}+{imag}i"
        else:
            return f"{real}{imag}i"
    
    # Sort the roots
    # Sort by real part first, then by imaginary part
    roots.sort(key=lambda x: (x.real, x.imag))
    
    # Format and join with newlines
    result = '\n'.join(format_complex(root) for root in roots)
    return result


# Example usage
if __name__ == "__main__":
    # Example 1: x³ - 6x² + 11x - 6 = 0
    # Known roots: 1, 2, 3
    print("Example 1: x³ - 6x² + 11x - 6 = 0")
    print("Known roots: 1, 2, 3")
    a, b, c, d = 1, -6, 11, -6
    result = cardano_formula(a, b, c, d)
    print(result)
    
    print("\n" + "="*50 + "\n")
    
    # Example 2: x³ + 3x² - 4x - 12 = 0
    # Known roots: -3, -2, 2
    print("Example 2: x³ + 3x² - 4x - 12 = 0")
    print("Known roots: -3, -2, 2")
    a, b, c, d = 1, 3, -4, -12
    result = cardano_formula(a, b, c, d)
    print(result)
    
    print("\n" + "="*50 + "\n")
    
    # Example 3: x³ - 1 = 0
    # Known roots: 1, complex roots
    print("Example 3: x³ - 1 = 0")
    print("Known roots: 1, and two complex cube roots of unity")
    a, b, c, d = 1, 0, 0, -1
    result = cardano_formula(a, b, c, d)
    print(result)
    
    print("\n" + "="*50 + "\n")
    
    # Example 4: Large coefficients
    print("Example 4: Large coefficients")
    print("Expected roots: -1831912200±37614515196i, 57715266291")
    a = 1
    b = -54051441891
    c = 1206749054849160314880
    d = -81852232506889517992956183707648
    result = cardano_formula(a, b, c, d)
    print(result)
