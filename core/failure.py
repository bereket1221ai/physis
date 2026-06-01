"""
failure.py - Chapter 6: Variable Stresses and Failure Analysis

Based on Machine Design textbook (R.S. Khurmi, J.K. Gupta)
Sections covered:
- 6.1-6.3: Fatigue and Endurance Limit
- 6.4-6.9: Factors Affecting Endurance Limit
- 6.10-6.11: Stress Concentration
- 6.12-6.16: Stress Concentration Factors
- 6.17-6.18: Notch Sensitivity
- 6.19-6.22: Combined Steady and Variable Stresses (Gerber, Goodman, Soderberg)
- 6.23: Combined Variable Normal and Shear Stress
"""

import math


class EnduranceLimit:
    """Chapter 6.3: Endurance limit (σₑ) is the stress below which a material can endure infinite cycles."""
    
    @staticmethod
    def from_ultimate_tensile(ultimate_tensile_stress_mpa):
        """
        σₑ = 0.5 × σ_ut (for steels, empirical relation)
        
        Chapter 6.9: Relation between endurance limit and ultimate tensile strength.
        
        Parameters:
        -----------
        ultimate_tensile_stress_mpa : float
            Ultimate tensile strength (σ_ut) in MPa
            
        Returns:
        --------
        float : Endurance limit (σₑ) in MPa
        
        Example:
        --------
        >>> EnduranceLimit.from_ultimate_tensile(400)
        200.0
        """
        return 0.5 * ultimate_tensile_stress_mpa
    
    @staticmethod
    def corrected(ultimate_tensile_mpa, surface_factor, size_factor, load_factor, 
                  temperature_factor=1.0, reliability_factor=1.0, miscellaneous_factor=1.0):
        """
        σₑ' = σₑ × k_a × k_b × k_c × k_d × k_e × k_f
        
        Chapter 6.4-6.8: Corrected endurance limit considering various factors.
        
        Parameters:
        -----------
        ultimate_tensile_mpa : float
            Ultimate tensile strength (σ_ut) in MPa
        surface_factor : float
            Surface finish factor (k_a) - Table 6.1
        size_factor : float
            Size factor (k_b) - Section 6.6
        load_factor : float
            Load factor (k_c) - Section 6.4
        temperature_factor : float, optional
            Temperature factor (k_d) - Default 1.0
        reliability_factor : float, optional
            Reliability factor (k_e) - Default 1.0
        miscellaneous_factor : float, optional
            Miscellaneous factor (k_f) - Default 1.0
        
        Returns:
        --------
        float : Corrected endurance limit in MPa
        """
        endurance_limit_base = EnduranceLimit.from_ultimate_tensile(ultimate_tensile_mpa)
        return (endurance_limit_base * surface_factor * size_factor * load_factor *
                temperature_factor * reliability_factor * miscellaneous_factor)
    
    @staticmethod
    def surface_factor_surface(ultimate_tensile_mpa, surface_type):
        """
        Chapter 6.5: Surface finish factor (k_a) based on surface condition.
        
        Parameters:
        -----------
        ultimate_tensile_mpa : float
            Ultimate tensile strength in MPa
        surface_type : str
            'ground', 'machined', 'cold_drawn', 'hot_rolled', 'as_forged'
        
        Returns:
        --------
        float : Surface factor (k_a)
        """
        # Constants for different surface conditions (Textbook Table 6.1)
        # k_a = a × (σ_ut)^b
        surface_constants = {
            'ground': (1.34, -0.085),
            'machined': (4.51, -0.265),
            'cold_drawn': (2.70, -0.265),
            'hot_rolled': (57.7, -0.718),
            'as_forged': (272.0, -0.995),
        }
        
        if surface_type not in surface_constants:
            raise ValueError(f"Unknown surface type: {surface_type}. Use: {list(surface_constants.keys())}")
        
        a, b = surface_constants[surface_type]
        return a * (ultimate_tensile_mpa ** b)
    
    @staticmethod
    def size_factor_rotating(diameter_mm):
        """
        Chapter 6.6: Size factor (k_b) for rotating beams.
        
        For diameter between 2.5 mm and 50 mm: k_b = 1.0 (size not significant)
        For diameter > 50 mm: k_b = 1.189 × d^(-0.097)
        
        Parameters:
        -----------
        diameter_mm : float
            Diameter in mm
        
        Returns:
        --------
        float : Size factor (k_b)
        """
        if diameter_mm <= 2.5:
            return 1.0
        elif diameter_mm <= 50:
            return 1.0
        else:
            return 1.189 * (diameter_mm ** -0.097)
    
    @staticmethod
    def load_factor(loading_type):
        """
        Chapter 6.4: Load factor (k_c) based on loading type.
        
        Parameters:
        -----------
        loading_type : str
            'bending', 'axial', 'torsion'
        
        Returns:
        --------
        float : Load factor (k_c)
        """
        factors = {
            'bending': 1.0,
            'axial': 0.85,
            'torsion': 0.58,  # For shear (0.577 for steels)
        }
        
        if loading_type not in factors:
            raise ValueError(f"Unknown loading type: {loading_type}. Use: {list(factors.keys())}")
        
        return factors[loading_type]
    
    @staticmethod
    def reliability_factor(reliability_percent):
        """
        Chapter 6.8: Reliability factor (k_e) for desired reliability.
        
        Parameters:
        -----------
        reliability_percent : float
            Desired reliability (50%, 90%, 95%, 99%, 99.9%)
        
        Returns:
        --------
        float : Reliability factor (k_e)
        """
        reliability_factors = {
            50: 1.000,
            90: 0.897,
            95: 0.868,
            99: 0.814,
            99.9: 0.753,
        }
        
        if reliability_percent not in reliability_factors:
            raise ValueError(f"Unknown reliability: {reliability_percent}%. Use: {list(reliability_factors.keys())}")
        
        return reliability_factors[reliability_percent]


class StressConcentration:
    """Chapter 6.10-6.16: Stress concentration due to geometric discontinuities."""
    
    @staticmethod
    def theoretical_stress_concentration_factor(nominal_stress, maximum_stress):
        """
        k_t = σ_max / σ_nom
        
        Chapter 6.11: Theoretical or form stress concentration factor.
        
        Parameters:
        -----------
        nominal_stress : float
            Nominal stress (σ_nom) in Pa
        maximum_stress : float
            Maximum stress at discontinuity (σ_max) in Pa
            
        Returns:
        --------
        float : Theoretical stress concentration factor (k_t)
        """
        return maximum_stress / nominal_stress
    
    @staticmethod
    def fatigue_stress_concentration_factor(theoretical_factor, notch_sensitivity, notch_type='normal'):
        """
        k_f = 1 + q(k_t - 1)
        
        Chapter 6.16: Fatigue stress concentration factor.
        
        Parameters:
        -----------
        theoretical_factor : float
            Theoretical stress concentration factor (k_t)
        notch_sensitivity : float
            Notch sensitivity (q) - from NotchSensitivity class
        notch_type : str, optional
            'normal' or 'shear' for different formulas
        
        Returns:
        --------
        float : Fatigue stress concentration factor (k_f)
        """
        if notch_type == 'shear':
            # For shear loading: k_fs = 1 + q_s(k_ts - 1)
            return 1 + notch_sensitivity * (theoretical_factor - 1)
        else:
            return 1 + notch_sensitivity * (theoretical_factor - 1)
    
    @staticmethod
    def shaft_shoulder_fillet(d_mm, d_small_mm, r_mm):
        """
        Chapter 6.15: Stress concentration factor for shaft with shoulder fillet.
        
        Parameters:
        -----------
        d_mm : float
            Larger diameter (D) in mm
        d_small_mm : float
            Smaller diameter (d) in mm
        r_mm : float
            Fillet radius (r) in mm
        
        Returns:
        --------
        float : Theoretical stress concentration factor (k_t)
        """
        # Simplified approximation based on textbook charts
        d_ratio = d_mm / d_small_mm
        r_ratio = r_mm / d_small_mm
        
        if r_ratio < 0.01:
            return 3.0 + 5 * (1 - d_ratio)
        elif r_ratio < 0.05:
            return 2.5 + 3 * (1 - d_ratio)
        elif r_ratio < 0.10:
            return 2.0 + 2 * (1 - d_ratio)
        else:
            return 1.8 + 1.5 * (1 - d_ratio)
    
    @staticmethod
    def shaft_groove(d_mm, r_mm):
        """
        Chapter 6.15: Stress concentration factor for shaft with groove.
        
        Parameters:
        -----------
        d_mm : float
            Shaft diameter at groove root in mm
        r_mm : float
            Groove radius in mm
        
        Returns:
        --------
        float : Theoretical stress concentration factor (k_t)
        """
        r_ratio = r_mm / d_mm
        
        if r_ratio < 0.01:
            return 4.0
        elif r_ratio < 0.02:
            return 3.5
        elif r_ratio < 0.05:
            return 3.0
        elif r_ratio < 0.10:
            return 2.5
        else:
            return 2.2
    
    @staticmethod
    def hole_in_plate(width_mm, hole_diameter_mm):
        """
        Chapter 6.12: Stress concentration for hole in flat plate under tension.
        
        Parameters:
        -----------
        width_mm : float
            Plate width (W) in mm
        hole_diameter_mm : float
            Hole diameter (d) in mm
        
        Returns:
        --------
        float : Theoretical stress concentration factor (k_t)
        """
        d_w_ratio = hole_diameter_mm / width_mm
        
        if d_w_ratio <= 0.1:
            return 2.7
        elif d_w_ratio <= 0.2:
            return 2.5
        elif d_w_ratio <= 0.3:
            return 2.3
        elif d_w_ratio <= 0.4:
            return 2.2
        else:
            return 2.1


class NotchSensitivity:
    """Chapter 6.17-6.18: Notch sensitivity (q) for various materials."""
    
    @staticmethod
    def for_steel(ultimate_tensile_mpa, notch_radius_mm):
        """
        Chapter 6.17: Notch sensitivity for steel based on notch radius.
        
        Parameters:
        -----------
        ultimate_tensile_mpa : float
            Ultimate tensile strength in MPa
        notch_radius_mm : float
            Notch radius in mm
        
        Returns:
        --------
        float : Notch sensitivity (q)
        """
        # Simplified empirical relation (Peterson's formula)
        # q = 1 / (1 + √(a/r))
        # where 'a' is a material constant
        
        if ultimate_tensile_mpa <= 560:
            a_sqrt = 0.5  # Approximate for low-strength steels
        elif ultimate_tensile_mpa <= 1400:
            a_sqrt = 0.2 + (0.5 - 0.2) * (1400 - ultimate_tensile_mpa) / (1400 - 560)
        else:
            a_sqrt = 0.2
        
        r_mm = max(notch_radius_mm, 0.05)
        return 1.0 / (1.0 + a_sqrt / math.sqrt(r_mm))
    
    @staticmethod
    def for_other_materials():
        """
        Chapter 6.18: Typical notch sensitivity values.
        
        Returns:
        --------
        dict : Material to notch sensitivity mapping
        """
        return {
            "Aluminum": 0.4,
            "Cast Iron": 0.2,
            "High-strength Steel": 0.7,
            "Medium-strength Steel": 0.5,
            "Low-strength Steel": 0.3,
            "Copper Alloys": 0.35,
        }


class FailureTheories:
    """Chapter 6.10-6.14: Theories of failure under static load."""
    
    @staticmethod
    def rankine_theory(principal_stress, yield_strength):
        """
        Chapter 6.10: Maximum Principal/Normal Stress Theory (Rankine).
        
        Failure occurs when maximum principal stress equals yield strength.
        
        Parameters:
        -----------
        principal_stress : float
            Maximum principal stress (σ₁) in Pa
        yield_strength : float
            Yield strength (σ_y) in Pa
        
        Returns:
        --------
        float : Factor of safety
        """
        return yield_strength / principal_stress
    
    @staticmethod
    def tresca_theory(shear_stress_max, yield_strength):
        """
        Chapter 6.11: Maximum Shear Stress Theory (Guest/Tresca).
        
        Failure occurs when maximum shear stress equals half of yield strength.
        
        Parameters:
        -----------
        shear_stress_max : float
            Maximum shear stress (τ_max) in Pa
        yield_strength : float
            Yield strength (σ_y) in Pa
        
        Returns:
        --------
        float : Factor of safety
        """
        return (yield_strength / 2) / shear_stress_max
    
    @staticmethod
    def von_mises_theory(stress_x, stress_y, shear_xy, yield_strength):
        """
        Chapter 6.14: Maximum Distortion Energy Theory (Hencky/Von Mises).
        
        Parameters:
        -----------
        stress_x : float
            Normal stress in x-direction (σ_x) in Pa
        stress_y : float
            Normal stress in y-direction (σ_y) in Pa
        shear_xy : float
            Shear stress (τ_xy) in Pa
        yield_strength : float
            Yield strength (σ_y) in Pa
        
        Returns:
        --------
        float : Factor of safety
        """
        # Von Mises equivalent stress
        sigma_vm = math.sqrt(stress_x**2 + stress_y**2 - stress_x*stress_y + 3*shear_xy**2)
        return yield_strength / sigma_vm if sigma_vm > 0 else float('inf')
    
    @staticmethod
    def von_mises_from_principal(sigma_1, sigma_2, sigma_3, yield_strength):
        """
        Von Mises failure criterion using principal stresses.
        
        Parameters:
        -----------
        sigma_1 : float
            First principal stress (σ₁) in Pa
        sigma_2 : float
            Second principal stress (σ₂) in Pa
        sigma_3 : float
            Third principal stress (σ₃) in Pa
        yield_strength : float
            Yield strength in Pa
        
        Returns:
        --------
        float : Factor of safety
        """
        sigma_vm = math.sqrt(((sigma_1 - sigma_2)**2 + (sigma_2 - sigma_3)**2 + 
                              (sigma_3 - sigma_1)**2) / 2)
        return yield_strength / sigma_vm if sigma_vm > 0 else float('inf')


class FatigueFailureCriteria:
    """Chapter 6.19-6.22: Combined steady and variable stress criteria."""
    
    @staticmethod
    def soderberg(mean_stress, alternating_stress, yield_strength, endurance_limit):
        """
        Chapter 6.21: Soderberg Method (Conservative).
        
        1/FS = σ_m/σ_y + σ_a/σ_e
        
        Parameters:
        -----------
        mean_stress : float
            Mean stress (σ_m) in Pa
        alternating_stress : float
            Alternating stress (σ_a) in Pa
        yield_strength : float
            Yield strength (σ_y) in Pa
        endurance_limit : float
            Endurance limit (σ_e) in Pa
        
        Returns:
        --------
        float : Factor of safety
        """
        return 1 / ((mean_stress / yield_strength) + (alternating_stress / endurance_limit))
    
    @staticmethod
    def goodman(mean_stress, alternating_stress, ultimate_tensile, endurance_limit):
        """
        Chapter 6.20: Goodman Method (Most Common).
        
        1/FS = σ_m/σ_ut + σ_a/σ_e
        
        Parameters:
        -----------
        mean_stress : float
            Mean stress (σ_m) in Pa
        alternating_stress : float
            Alternating stress (σ_a) in Pa
        ultimate_tensile : float
            Ultimate tensile strength (σ_ut) in Pa
        endurance_limit : float
            Endurance limit (σ_e) in Pa
        
        Returns:
        --------
        float : Factor of safety
        """
        return 1 / ((mean_stress / ultimate_tensile) + (alternating_stress / endurance_limit))
    
    @staticmethod
    def gerber(mean_stress, alternating_stress, ultimate_tensile, endurance_limit):
        """
        Chapter 6.19: Gerber Method (More accurate for ductile materials).
        
        (1/FS) = σ_a/σ_e + (σ_m/σ_ut)^2
        
        Parameters:
        -----------
        mean_stress : float
            Mean stress (σ_m) in Pa
        alternating_stress : float
            Alternating stress (σ_a) in Pa
        ultimate_tensile : float
            Ultimate tensile strength (σ_ut) in Pa
        endurance_limit : float
            Endurance limit (σ_e) in Pa
        
        Returns:
        --------
        float : Factor of safety
        """
        # Solve quadratic: (σ_e)(σ_m^2/σ_ut^2) + (σ_a) = σ_e/FS
        # This is the allowable alternating stress for given mean stress
        
        if mean_stress == 0:
            return endurance_limit / alternating_stress
        
        # Find factor of safety numerically (simplified)
        # Gerber parabola: σ_a = σ_e [1 - (σ_m/σ_ut)^2]
        allowable_alternating = endurance_limit * (1 - (mean_stress / ultimate_tensile)**2)
        return allowable_alternating / alternating_stress if alternating_stress > 0 else float('inf')
    
    @staticmethod
    def combined_stress_soderberg(mean_vm, alternating_vm, yield_strength, endurance_limit):
        """
        Chapter 6.23: Soderberg for combined variable normal and shear stress.
        
        Using Von Mises equivalent stresses.
        
        Parameters:
        -----------
        mean_vm : float
            Von Mises equivalent mean stress in Pa
        alternating_vm : float
            Von Mises equivalent alternating stress in Pa
        yield_strength : float
            Yield strength in Pa
        endurance_limit : float
            Endurance limit in Pa
        
        Returns:
        --------
        float : Factor of safety
        """
        return 1 / ((mean_vm / yield_strength) + (alternating_vm / endurance_limit))


# ============================================================================
# Example usage and test (Engine Design Context)
# ============================================================================

if __name__ == "__main__":
    print("=" * 70)
    print("Failure Module Test (Based on Machine Design Textbook Chapter 6)")
    print("=" * 70)
    
    # EXAMPLE 1: Endurance limit calculation for engine connecting rod
    print("\n1. Connecting Rod Fatigue Analysis:")
    print("-" * 40)
    
    # Material: Forged steel connecting rod
    ultimate_tensile = 800  # MPa
    yield_strength = 600  # MPa
    
    # Surface factor: forged (as-forged)
    surface_k = EnduranceLimit.surface_factor_surface(ultimate_tensile, 'as_forged')
    
    # Size factor: connecting rod approx 25 mm diameter
    size_k = EnduranceLimit.size_factor_rotating(25)
    
    # Load factor: axial loading (tension-compression)
    load_k = EnduranceLimit.load_factor('axial')
    
    # Reliability: 95%
    reliability_k = EnduranceLimit.reliability_factor(95)
    
    corrected_endurance = EnduranceLimit.corrected(
        ultimate_tensile_mpa=ultimate_tensile,
        surface_factor=surface_k,
        size_factor=size_k,
        load_factor=load_k,
        reliability_factor=reliability_k
    )
    
    print(f"   Material: Forged Steel")
    print(f"   σ_ut = {ultimate_tensile} MPa, σ_y = {yield_strength} MPa")
    print(f"   Endurance limit (corrected) = {corrected_endurance:.1f} MPa")
    
    # EXAMPLE 2: Failure criteria for engine piston pin
    print("\n2. Piston Pin Failure Analysis:")
    print("-" * 40)
    
    # Alternating stress from combustion cycles: 200 MPa
    # Mean stress from assembly preload: 50 MPa
    sigma_m = 50  # MPa
    sigma_a = 200  # MPa
    
    # Soderberg (conservative)
    fs_soderberg = FatigueFailureCriteria.soderberg(
        sigma_m, sigma_a, yield_strength, corrected_endurance
    )
    
    # Goodman (common)
    fs_goodman = FatigueFailureCriteria.goodman(
        sigma_m, sigma_a, ultimate_tensile, corrected_endurance
    )
    
    # Gerber (more accurate)
    fs_gerber = FatigueFailureCriteria.gerber(
        sigma_m, sigma_a, ultimate_tensile, corrected_endurance
    )
    
    print(f"   σ_m = {sigma_m} MPa, σ_a = {sigma_a} MPa")
    print(f"   Soderberg FS = {fs_soderberg:.2f}")
    print(f"   Goodman FS = {fs_goodman:.2f}")
    print(f"   Gerber FS = {fs_gerber:.2f}")
    
    if fs_soderberg < 1:
        print("   → Design FAILS (need larger pin or stronger material)")
    else:
        print("   → Design acceptable")
    
    # EXAMPLE 3: Stress concentration in crankshaft
    print("\n3. Crankshaft Stress Concentration:")
    print("-" * 40)
    
    # Crankshaft journal with fillet
    D = 80  # mm (larger diameter)
    d = 60  # mm (journal diameter)
    r = 3   # mm (fillet radius)
    
    k_t = StressConcentration.shaft_shoulder_fillet(D, d, r)
    
    # Notch sensitivity for steel
    q = NotchSensitivity.for_steel(ultimate_tensile, r)
    
    # Fatigue stress concentration factor
    k_f = StressConcentration.fatigue_stress_concentration_factor(k_t, q)
    
    print(f"   D = {D} mm, d = {d} mm, r = {r} mm")
    print(f"   k_t (theoretical) = {k_t:.2f}")
    print(f"   q (notch sensitivity) = {q:.2f}")
    print(f"   k_f (fatigue factor) = {k_f:.2f}")
    
    # EXAMPLE 4: Failure theory comparison
    print("\n4. Failure Theories Comparison (Static Load):")
    print("-" * 40)
    
    # Stress state in engine cylinder wall
    sigma_x = 120  # MPa (hoop stress)
    sigma_y = 60   # MPa (longitudinal stress)
    tau_xy = 0     # MPa (no shear)
    
    rankine_fs = FailureTheories.rankine_theory(sigma_x, yield_strength)
    tresca_fs = FailureTheories.tresca_theory((sigma_x - sigma_y)/2, yield_strength)
    von_mises_fs = FailureTheories.von_mises_theory(sigma_x, sigma_y, tau_xy, yield_strength)
    
    print(f"   σ_x = {sigma_x} MPa, σ_y = {sigma_y} MPa, τ_xy = {tau_xy} MPa")
    print(f"   Rankine (Max Principal) FS = {rankine_fs:.2f}")
    print(f"   Tresca (Max Shear) FS = {tresca_fs:.2f}")
    print(f"   Von Mises FS = {von_mises_fs:.2f}")
    
    # EXAMPLE 5: Reliability factors
    print("\n5. Reliability Factors (k_e) for Different Confidence Levels:")
    print("-" * 40)
    for rel, factor in EnduranceLimit.reliability_factor.__code__.co_consts:
        if isinstance(rel, dict):
            for rel_val, k_e in rel.items():
                print(f"   {rel_val}% reliability: k_e = {k_e}")
    
    print("\n" + "=" * 70)
    print("All failure functions ready for use in engine component design.")
    print("=" * 70)