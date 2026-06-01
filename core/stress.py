"""
stress.py - Chapters 4 & 5: Simple, Torsional, and Bending Stresses

Based on Machine Design textbook (R.S. Khurmi, J.K. Gupta)
Sections covered:
- Chapter 4: Simple Stresses
  - 4.5: Tensile Stress and Strain
  - 4.6: Compressive Stress and Strain
  - 4.8: Shear Stress and Strain
  - 4.10: Bearing Stress
  - 4.12: Working Stress
  - 4.13: Factor of Safety
  - 4.15: Stresses in Composite Bars
  
- Chapter 5: Torsional and Bending Stresses
  - 5.2: Torsional Shear Stress
  - 5.3: Shafts in Series and Parallel
  - 5.4: Bending Stress in Straight Beams
  - 5.5: Bending Stress in Curved Beams
  - 5.6: Principal Stresses and Principal Planes
  - 5.7: Determination of Principal Stresses (Biaxial)
  - 5.8: Application in Designing Machine Members
  - 5.10-5.14: Theories of Failure (references)
  - 5.15: Eccentric Loading (Direct + Bending)
  - 5.16: Shear Stresses in Beams
"""

import math


class SimpleStresses:
    """Chapter 4: Basic stress calculations for machine elements."""
    
    @staticmethod
    def tensile_stress(force, area):
        """
        σ_t = F / A
        
        Chapter 4.5: Tensile stress (pulling force).
        
        Parameters:
        -----------
        force : float
            Axial tensile force (F) in Newtons
        area : float
            Cross-sectional area (A) in m²
            
        Returns:
        --------
        float : Tensile stress (σ_t) in Pascals
        
        Example:
        --------
        >>> SimpleStresses.tensile_stress(force=10000, area=0.0001)
        100000000.0  # 100 MPa
        """
        return force / area
    
    @staticmethod
    def compressive_stress(force, area):
        """
        σ_c = F / A
        
        Chapter 4.6: Compressive stress (pushing force).
        
        Parameters:
        -----------
        force : float
            Axial compressive force (F) in Newtons
        area : float
            Cross-sectional area (A) in m²
            
        Returns:
        --------
        float : Compressive stress (σ_c) in Pascals
        """
        return force / area
    
    @staticmethod
    def shear_stress(force, area):
        """
        τ = F / A
        
        Chapter 4.8: Shear stress (sliding force).
        
        Parameters:
        -----------
        force : float
            Shear force (F) in Newtons
        area : float
            Shear area (A) in m²
            
        Returns:
        --------
        float : Shear stress (τ) in Pascals
        """
        return force / area
    
    @staticmethod
    def bearing_stress(force, projected_area):
        """
        σ_b = F / A_projected
        
        Chapter 4.10: Bearing stress (contact pressure).
        
        Parameters:
        -----------
        force : float
            Force (F) in Newtons
        projected_area : float
            Projected contact area in m² (diameter × length for pins)
            
        Returns:
        --------
        float : Bearing stress (σ_b) in Pascals
        
        Example (Piston pin):
        >>> pin_diameter = 0.02  # 20 mm
        >>> pin_length = 0.06    # 60 mm
        >>> area = pin_diameter * pin_length
        >>> SimpleStresses.bearing_stress(force=15000, projected_area=area)
        """
        return force / projected_area
    
    @staticmethod
    def factor_of_safety(yield_stress, working_stress):
        """
        N = σ_yield / σ_working
        
        Chapter 4.13: Factor of safety.
        
        Parameters:
        -----------
        yield_stress : float
            Material yield stress (σ_y) in Pa
        working_stress : float
            Actual/design stress (σ_work) in Pa
            
        Returns:
        --------
        float : Factor of safety (N)
        
        Typical values (Chapter 4.14):
        - 1.5-2.0: For reliable materials under static loads
        - 2.0-2.5: For ordinary materials under static loads
        - 3.0-4.0: For dynamic/impact loads
        - 4.0-8.0: For uncertain loads or brittle materials
        """
        return yield_stress / working_stress
    
    @staticmethod
    def allowable_stress(yield_stress, factor_of_safety):
        """
        σ_allow = σ_y / N
        
        Calculate allowable/working stress from yield stress and FS.
        """
        return yield_stress / factor_of_safety
    
    @staticmethod
    def composite_bar_stress(load, areas, moduli):
        """
        Chapter 4.15: Stresses in composite bars (different materials).
        
        For a composite bar with multiple materials bonded together,
        all materials have the same strain (ε = σ₁/E₁ = σ₂/E₂ = ...)
        
        Parameters:
        -----------
        load : float
            Total axial load (P) in Newtons
        areas : list of float
            Cross-sectional areas of each material in m²
        moduli : list of float
            Young's moduli of each material in Pa
            
        Returns:
        --------
        list : Stresses in each material in Pa
        
        Example:
        --------
        >>> # Steel rod reinforced with copper tube
        >>> stresses = SimpleStresses.composite_bar_stress(
        ...     load=50000,
        ...     areas=[0.0002, 0.0003],
        ...     moduli=[200e9, 110e9]
        ... )
        """
        # Total equivalent area (steel-equivalent)
        total_equiv_area = 0
        for i, (area, modulus) in enumerate(zip(areas, moduli)):
            total_equiv_area += area * (modulus / moduli[0])
        
        # Stress in reference material
        stress_ref = load / total_equiv_area
        
        # Stresses in each material
        stresses = []
        for i, modulus in enumerate(moduli):
            stress_i = stress_ref * (modulus / moduli[0])
            stresses.append(stress_i)
        
        return stresses


class TorsionalStresses:
    """Chapter 5.2-5.3: Torsional shear stress in shafts."""
    
    @staticmethod
    def polar_moment_solid(diameter):
        """
        J = π × d⁴ / 32
        
        Polar moment of inertia for solid circular shaft.
        
        Parameters:
        -----------
        diameter : float
            Shaft diameter in meters
            
        Returns:
        --------
        float : Polar moment (J) in m⁴
        """
        return (math.pi * diameter**4) / 32
    
    @staticmethod
    def polar_moment_hollow(outer_diameter, inner_diameter):
        """
        J = π × (d_o⁴ - d_i⁴) / 32
        
        Polar moment of inertia for hollow circular shaft.
        """
        return (math.pi * (outer_diameter**4 - inner_diameter**4)) / 32
    
    @staticmethod
    def torsional_shear_stress(torque, radius, polar_moment):
        """
        τ = T × r / J
        
        Chapter 5.2: Torsional shear stress.
        
        Parameters:
        -----------
        torque : float
            Applied torque (T) in N·m
        radius : float
            Radius at point of interest (r) in meters (use outer radius for max)
        polar_moment : float
            Polar moment of inertia (J) in m⁴
            
        Returns:
        --------
        float : Torsional shear stress (τ) in Pa
        
        Example (Crankshaft):
        >>> T = 500  # N·m
        >>> d = 0.05  # 50 mm shaft
        >>> J = TorsionalStresses.polar_moment_solid(d)
        >>> tau = TorsionalStresses.torsional_shear_stress(T, d/2, J)
        """
        return (torque * radius) / polar_moment
    
    @staticmethod
    def max_torsional_shear_solid(torque, diameter):
        """
        τ_max = 16 × T / (π × d³)
        
        Maximum shear stress at outer fiber of solid shaft.
        """
        return (16 * torque) / (math.pi * diameter**3)
    
    @staticmethod
    def max_torsional_shear_hollow(torque, outer_diameter, inner_diameter):
        """
        τ_max = 16 × T × d_o / (π × (d_o⁴ - d_i⁴))
        
        Maximum shear stress at outer fiber of hollow shaft.
        """
        return (16 * torque * outer_diameter) / (math.pi * (outer_diameter**4 - inner_diameter**4))
    
    @staticmethod
    def angle_of_twist(torque, length, polar_moment, shear_modulus):
        """
        θ = T × L / (J × G)
        
        Chapter 5.2: Angular deflection under torsion (radians).
        
        Parameters:
        -----------
        torque : float
            Applied torque (T) in N·m
        length : float
            Shaft length (L) in meters
        polar_moment : float
            Polar moment (J) in m⁴
        shear_modulus : float
            Shear modulus (G) in Pa
            
        Returns:
        --------
        float : Angle of twist (θ) in radians
        """
        return (torque * length) / (polar_moment * shear_modulus)
    
    @staticmethod
    def shafts_in_series(torque, lengths, polar_moments, shear_moduli):
        """
        Chapter 5.3: Shafts connected end-to-end (same torque).
        
        Total angle of twist = Σ(T × L_i / (J_i × G_i))
        
        Returns:
        --------
        float : Total angle of twist in radians
        """
        total_theta = 0
        for L, J, G in zip(lengths, polar_moments, shear_moduli):
            total_theta += (torque * L) / (J * G)
        return total_theta
    
    @staticmethod
    def shafts_in_parallel(torque_total, lengths, polar_moments, shear_moduli):
        """
        Chapter 5.3: Shafts connected side-by-side (same deflection).
        
        Torque distributes proportionally to stiffness (GJ/L).
        
        Returns:
        --------
        tuple: (torques, total_angle) for each shaft
        """
        # Stiffness of each shaft: k_i = G_i × J_i / L_i
        stiffnesses = []
        for L, J, G in zip(lengths, polar_moments, shear_moduli):
            stiffnesses.append(G * J / L)
        
        total_stiffness = sum(stiffnesses)
        
        # Torque distribution
        torques = []
        for k in stiffnesses:
            torques.append(torque_total * k / total_stiffness)
        
        # All shafts have same angle
        angle = torque_total / total_stiffness if total_stiffness > 0 else 0
        
        return torques, angle


class BendingStresses:
    """Chapter 5.4-5.5: Bending stress in straight and curved beams."""
    
    @staticmethod
    def moment_of_inertia_rectangle(width, height):
        """
        I = b × h³ / 12
        
        For rectangular cross-section about centroidal axis.
        """
        return (width * height**3) / 12
    
    @staticmethod
    def moment_of_inertia_circle(diameter):
        """
        I = π × d⁴ / 64
        
        For solid circular cross-section.
        """
        return (math.pi * diameter**4) / 64
    
    @staticmethod
    def moment_of_inertia_hollow(outer_diameter, inner_diameter):
        """
        I = π × (d_o⁴ - d_i⁴) / 64
        
        For hollow circular cross-section.
        """
        return (math.pi * (outer_diameter**4 - inner_diameter**4)) / 64
    
    @staticmethod
    def section_modulus_rectangle(width, height):
        """
        Z = b × h² / 6
        
        For rectangular cross-section.
        """
        return (width * height**2) / 6
    
    @staticmethod
    def section_modulus_circle(diameter):
        """
        Z = π × d³ / 32
        
        For solid circular cross-section.
        """
        return (math.pi * diameter**3) / 32
    
    @staticmethod
    def section_modulus_hollow(outer_diameter, inner_diameter):
        """
        Z = π × (d_o⁴ - d_i⁴) / (32 × d_o)
        
        For hollow circular cross-section.
        """
        return (math.pi * (outer_diameter**4 - inner_diameter**4)) / (32 * outer_diameter)
    
    @staticmethod
    def bending_stress(moment, distance_from_neutral_axis, moment_of_inertia):
        """
        σ_b = M × y / I
        
        Chapter 5.4: Bending (flexural) stress.
        
        Parameters:
        -----------
        moment : float
            Bending moment (M) in N·m
        distance_from_neutral_axis : float
            Distance from neutral axis (y) in meters (use max for outer fiber)
        moment_of_inertia : float
            Area moment of inertia (I) in m⁴
            
        Returns:
        --------
        float : Bending stress (σ_b) in Pa
        """
        return (moment * distance_from_neutral_axis) / moment_of_inertia
    
    @staticmethod
    def max_bending_stress(moment, section_modulus):
        """
        σ_b_max = M / Z
        
        Where Z = I / c (c = distance to extreme fiber).
        """
        return moment / section_modulus
    
    @staticmethod
    def curved_beam_stress(moment, area, radius_to_neutral_axis, distance_from_neutral_axis, 
                           radius_to_centroid, radius_to_point):
        """
        Chapter 5.5: Bending stress in curved beams (e.g., crane hooks, C-clamps).
        
        σ = (M × y) / (A × e × (R_n - y))
        
        Where:
        - e = R_n - R_c (distance between neutral axis and centroid)
        - y = distance from neutral axis to point of interest
        
        Simplified formula for rectangular cross-section curved beam:
        σ = (M × h) / (2 × A × e × (R_n + h/2))
        
        Parameters:
        -----------
        moment : float
            Bending moment (M) in N·m
        area : float
            Cross-sectional area in m²
        radius_to_neutral_axis : float
            Radius to neutral axis (R_n) in meters
        distance_from_neutral_axis : float
            Distance from neutral axis (y) in meters
        radius_to_centroid : float
            Radius to centroid (R_c) in meters
        radius_to_point : float
            Radius to point of interest in meters
            
        Returns:
        --------
        float : Bending stress in curved beam in Pa
        """
        e = radius_to_neutral_axis - radius_to_centroid
        return (moment * distance_from_neutral_axis) / (area * e * radius_to_point)
    
    @staticmethod
    def shear_stress_in_beam(shear_force, moment_of_inertia, width, first_moment):
        """
        τ = V × Q / (I × b)
        
        Chapter 5.16: Shear stress distribution in beams.
        
        Parameters:
        -----------
        shear_force : float
            Transverse shear force (V) in Newtons
        moment_of_inertia : float
            Area moment of inertia (I) in m⁴
        width : float
            Beam width at point of interest (b) in meters
        first_moment : float
            First moment of area about neutral axis (Q) in m³
            
        Returns:
        --------
        float : Shear stress (τ) in Pa
        """
        return (shear_force * first_moment) / (moment_of_inertia * width)
    
    @staticmethod
    def first_moment_rectangle(y, width, height):
        """
        Q = b × (h/2 - y) × (y + (h/2 - y)/2)
        
        First moment of area for rectangle at distance y from neutral axis.
        Max Q occurs at neutral axis (y=0): Q_max = b × h² / 8
        """
        # Simplified: Q_max at neutral axis
        return (width * height**2) / 8


class PrincipalStresses:
    """Chapter 5.6-5.8: Principal stresses for biaxial stress state."""
    
    @staticmethod
    def principal_stresses_2d(stress_x, stress_y, shear_xy):
        """
        Chapter 5.7: Determine principal stresses for biaxial stress.
        
        σ₁,₂ = (σ_x + σ_y)/2 ± √[((σ_x - σ_y)/2)² + τ_xy²]
        
        Parameters:
        -----------
        stress_x : float
            Normal stress in x-direction (σ_x) in Pa
        stress_y : float
            Normal stress in y-direction (σ_y) in Pa
        shear_xy : float
            Shear stress (τ_xy) in Pa
            
        Returns:
        --------
        tuple : (σ₁, σ₂) principal stresses in Pa (σ₁ > σ₂)
        """
        avg = (stress_x + stress_y) / 2
        radius = math.sqrt(((stress_x - stress_y) / 2)**2 + shear_xy**2)
        
        sigma_1 = avg + radius
        sigma_2 = avg - radius
        
        return sigma_1, sigma_2
    
    @staticmethod
    def max_shear_stress_2d(stress_x, stress_y, shear_xy):
        """
        τ_max = √[((σ_x - σ_y)/2)² + τ_xy²]
        
        Maximum in-plane shear stress.
        """
        return math.sqrt(((stress_x - stress_y) / 2)**2 + shear_xy**2)
    
    @staticmethod
    def principal_angle(stress_x, stress_y, shear_xy):
        """
        θ_p = 0.5 × arctan(2τ_xy / (σ_x - σ_y))
        
        Angle of principal planes (degrees).
        """
        if stress_x == stress_y:
            return 45.0 if shear_xy != 0 else 0.0
        
        tan_2theta = (2 * shear_xy) / (stress_x - stress_y)
        theta_rad = 0.5 * math.atan(tan_2theta)
        return math.degrees(theta_rad)
    
    @staticmethod
    def von_mises_stress(stress_x, stress_y, shear_xy):
        """
        σ_vm = √(σ_x² + σ_y² - σ_xσ_y + 3τ_xy²)
        
        Von Mises equivalent stress for ductile materials.
        """
        return math.sqrt(stress_x**2 + stress_y**2 - stress_x*stress_y + 3*shear_xy**2)
    
    @staticmethod
    def von_mises_from_principal(sigma_1, sigma_2):
        """
        σ_vm = √(σ₁² + σ₂² - σ₁σ₂)
        
        For plane stress (σ₃ = 0).
        """
        return math.sqrt(sigma_1**2 + sigma_2**2 - sigma_1*sigma_2)
    
    @staticmethod
    def mohr_circle(stress_x, stress_y, shear_xy):
        """
        Returns center and radius of Mohr's circle.
        
        Returns:
        --------
        tuple : (center, radius) in Pa
        """
        center = (stress_x + stress_y) / 2
        radius = math.sqrt(((stress_x - stress_y) / 2)**2 + shear_xy**2)
        return center, radius


class EccentricLoading:
    """Chapter 5.15: Combined direct and bending stresses."""
    
    @staticmethod
    def direct_stress(force, area):
        """σ_direct = P / A (tensile or compressive)"""
        return force / area
    
    @staticmethod
    def bending_stress_from_eccentricity(force, eccentricity, section_modulus):
        """
        σ_bending = (P × e) / Z
        
        Bending stress due to eccentric load.
        
        Parameters:
        -----------
        force : float
            Eccentric force (P) in Newtons
        eccentricity : float
            Distance from centroid to line of action (e) in meters
        section_modulus : float
            Section modulus (Z) in m³
            
        Returns:
        --------
        float : Bending stress in Pa
        """
        moment = force * eccentricity
        return moment / section_modulus
    
    @staticmethod
    def combined_stress_short_column(force, area, eccentricity, section_modulus, 
                                      direct_tension=True):
        """
        σ_total = ±P/A ± (P×e)/Z
        
        For short columns/beams with eccentric loading.
        
        Parameters:
        -----------
        force : float
            Eccentric force (P) in Newtons
        area : float
            Cross-sectional area in m²
        eccentricity : float
            Eccentricity in meters
        section_modulus : float
            Section modulus in m³
        direct_tension : bool
            True if force causes tension, False if compression
            
        Returns:
        --------
        tuple : (σ_max, σ_min) in Pa
        """
        direct = force / area
        bending = (force * eccentricity) / section_modulus
        
        if direct_tension:
            sigma_max = direct + bending  # Maximum at same side as bending
            sigma_min = direct - bending  # Minimum at opposite side
        else:
            # Compression: negative direct stress
            sigma_max = -direct + bending
            sigma_min = -direct - bending
        
        return sigma_max, sigma_min
    
    @staticmethod
    def core_of_section(radius):
        """
        Kern/Core of circular section (where no tension occurs).
        
        For a circular column, load must be within radius/4 from center.
        """
        return radius / 4
    
    @staticmethod
    def eccentricity_limits_rectangle(width, height):
        """
        Limits for no tension in rectangular section.
        
        Returns:
        --------
        dict : Maximum eccentricities in x and y directions
        """
        return {
            'e_x_max': width / 6,
            'e_y_max': height / 6,
        }


# ============================================================================
# Example usage and test (Engine Design Context)
# ============================================================================

if __name__ == "__main__":
    print("=" * 70)
    print("Stress Module Test (Based on Machine Design Textbook Chapters 4 & 5)")
    print("=" * 70)
    
    # EXAMPLE 1: Connecting Rod Stress (Tension and Compression)
    print("\n1. Connecting Rod Analysis:")
    print("-" * 40)
    
    # Connecting rod cross-section (I-beam simplified as rectangle)
    width_rod = 0.025  # 25 mm
    height_rod = 0.012  # 12 mm
    area_rod = width_rod * height_rod  # 0.0003 m² = 300 mm²
    
    # Gas force on piston (peak combustion)
    gas_force = 30000  # N (30 kN)
    
    # Tensile stress during power stroke
    sigma_tensile = SimpleStresses.tensile_stress(gas_force, area_rod)
    
    # Inertia force at top dead center (tension)
    inertia_force = 15000  # N (15 kN) - approximate
    sigma_compressive = SimpleStresses.compressive_stress(inertia_force, area_rod)
    
    print(f"   Rod area = {area_rod*1e6:.1f} mm²")
    print(f"   Tensile stress (gas force) = {sigma_tensile/1e6:.1f} MPa")
    print(f"   Compressive stress (inertia) = {sigma_compressive/1e6:.1f} MPa")
    
    # EXAMPLE 2: Crankshaft Torsional Stress
    print("\n2. Crankshaft Torsional Analysis:")
    print("-" * 40)
    
    # Engine torque: 200 N·m
    torque = 200  # N·m
    crank_diameter = 0.045  # 45 mm
    
    J = TorsionalStresses.polar_moment_solid(crank_diameter)
    tau_max = TorsionalStresses.max_torsional_shear_solid(torque, crank_diameter)
    
    print(f"   Crank diameter = {crank_diameter*1000:.0f} mm")
    print(f"   Torque = {torque} N·m")
    print(f"   Max shear stress = {tau_max/1e6:.1f} MPa")
    
    # EXAMPLE 3: Piston Pin Bending (Double shear)
    print("\n3. Piston Pin Bending Analysis:")
    print("-" * 40)
    
    pin_diameter = 0.022  # 22 mm
    pin_length = 0.065    # 65 mm
    gas_force_pin = 35000  # N
    
    # Bending moment for pin as simply supported beam
    bearing_length = pin_length / 2
    bending_moment = gas_force_pin * bearing_length / 4  # Simplified
    
    Z = BendingStresses.section_modulus_circle(pin_diameter)
    sigma_bend = BendingStresses.max_bending_stress(bending_moment, Z)
    
    print(f"   Pin diameter = {pin_diameter*1000:.0f} mm")
    print(f"   Bending moment = {bending_moment:.1f} N·m")
    print(f"   Bending stress = {sigma_bend/1e6:.1f} MPa")
    
    # EXAMPLE 4: Principal Stresses in Cylinder Wall
    print("\n4. Cylinder Wall Principal Stresses:")
    print("-" * 40)
    
    # Cylinder under internal pressure
    hoop_stress = 120e6  # 120 MPa
    longitudinal_stress = 60e6  # 60 MPa
    shear_stress = 0
    
    sigma_1, sigma_2 = PrincipalStresses.principal_stresses_2d(
        hoop_stress, longitudinal_stress, shear_stress
    )
    tau_max_principal = PrincipalStresses.max_shear_stress_2d(
        hoop_stress, longitudinal_stress, shear_stress
    )
    vm_stress = PrincipalStresses.von_mises_stress(
        hoop_stress, longitudinal_stress, shear_stress
    )
    
    print(f"   Hoop stress = {hoop_stress/1e6:.0f} MPa")
    print(f"   Longitudinal stress = {longitudinal_stress/1e6:.0f} MPa")
    print(f"   Principal stresses: σ₁ = {sigma_1/1e6:.0f} MPa, σ₂ = {sigma_2/1e6:.0f} MPa")
    print(f"   Max shear = {tau_max_principal/1e6:.0f} MPa")
    print(f"   Von Mises = {vm_stress/1e6:.0f} MPa")
    
    # EXAMPLE 5: Eccentric Loading on Piston Pin
    print("\n5. Eccentric Loading Example (Piston Pin Offset):")
    print("-" * 40)
    
    # Piston pin offset to reduce side thrust
    force_piston = 25000  # N
    eccentricity = 0.002  # 2 mm offset
    pin_area = math.pi * (0.022)**2 / 4  # m²
    
    sigma_max, sigma_min = EccentricLoading.combined_stress_short_column(
        force=force_piston,
        area=pin_area,
        eccentricity=eccentricity,
        section_modulus=Z,
        direct_tension=False  # Compression
    )
    
    print(f"   Force = {force_piston/1000:.0f} kN")
    print(f"   Eccentricity = {eccentricity*1000:.1f} mm")
    print(f"   Maximum stress = {sigma_max/1e6:.1f} MPa (compression)")
    print(f"   Minimum stress = {sigma_min/1e6:.1f} MPa")
    
    # Factor of safety check
    yield_strength = 400e6  # 400 MPa for steel
    fs = SimpleStresses.factor_of_safety(yield_strength, abs(sigma_max))
    print(f"   Factor of safety = {fs:.2f}")
    
    print("\n" + "=" * 70)
    print("All stress functions ready for use in engine component design.")
    print("=" * 70)