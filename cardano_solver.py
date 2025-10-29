import cmath

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
    
    # Normalize the equation by dividing by a
    b, c, d = b/a, c/a, d/a
    
    # Convert to depressed cubic: t³ + pt + q = 0
    # Using substitution x = t - b/3
    p = c - b**2 / 3
    q = 2*b**3/27 - b*c/3 + d
    
    # Calculate discriminant
    delta = q**2/4 + p**3/27
    
    # Calculate the cube roots more carefully
    # We need to use a proper cube root function for complex numbers
    def complex_cube_root(z):
        """Calculate the principal cube root of a complex number"""
        if z == 0:
            return 0
        r = abs(z)
        theta = cmath.phase(z)
        cube_root_r = r ** (1/3)
        cube_root_theta = theta / 3
        return cube_root_r * cmath.exp(1j * cube_root_theta)
    
    # Calculate u using the principal cube root
    u = complex_cube_root(-q/2 + cmath.sqrt(delta))
    
    # Calculate v using the constraint u*v = -p/3
    if abs(u) > 1e-10:
        v = -p / (3 * u)
    else:
        # If u is very small, calculate v directly
        v = complex_cube_root(-q/2 - cmath.sqrt(delta))
    
    # Complex cube roots of unity
    omega = complex(-1/2, cmath.sqrt(3)/2)
    omega2 = complex(-1/2, -cmath.sqrt(3)/2)
    
    # Three roots of depressed cubic
    t1 = u + v
    t2 = omega * u + omega2 * v
    t3 = omega2 * u + omega * v
    
    # Convert back to original equation (x = t - b/3)
    shift = b / 3
    x1 = t1 - shift
    x2 = t2 - shift
    x3 = t3 - shift
    
    # Round to clean up floating point errors
    # Only round to integers if the values are very close to integers
    def clean_root(root, tolerance=1e-9):
        real = root.real
        imag = root.imag
        
        # Check if close to an integer
        if abs(real - round(real)) < tolerance:
            real = round(real)
        if abs(imag - round(imag)) < tolerance:
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
    
    # Example 4: Large coefficients (adjusted from original example 2)
    print("Example 4: Large coefficients")
    a, b, c, d = 1, -90241940450, 10125996102586212012093, -495773079457841151858151341690006
    result = cardano_formula(a, b, c, d)
    print(result)
