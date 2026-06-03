"""
failure.py - Complete Fatigue and Failure Analysis

Sources:
- Machine Design Textbook (Chapter 6) - R.S. Khurmi
- Mechanical Engineering Design - Shigley & Mischke
- Fatigue of Materials - Suresh
- ASME Boiler and Pressure Vessel Code

Covers:
- Chapter 6.1-6.3: Fatigue and Endurance Limit
- Chapter 6.4-6.9: Factors Affecting Endurance Limit
- Chapter 6.10-6.11: Stress Concentration
- Chapter 6.12-6.16: Stress Concentration Factors
- Chapter 6.17-6.18: Notch Sensitivity
- Chapter 6.19-6.22: Combined Steady and Variable Stresses
- Chapter 6.23: Combined Variable Normal and Shear Stress
- Goodman, Soderberg, Gerber criteria
- von Mises and Tresca failure theories
"""

import math
from dataclasses import dataclass, field
from typing import Dict, Any, Optional, Tuple, List


# ============================================================================
# SECTION 1: MATERIAL PROPERTIES DATABASE
# ============================================================================

@dataclass(frozen=True)
class FatigueMaterial:
    """Material properties for fatigue analysis."""
    
    name: str
    ultimate_tensile_mpa: float
    yield_strength_mpa: float
    endurance_limit_mpa: float
    youngs_modulus_gpa: float
    density_kg_m3: float
    
    @property
    def E_mpa(self) -> float:
        return self.youngs_modulus_gpa * 1000


# Material database for fatigue analysis
FATIGUE_MATERIALS: Dict[str, FatigueMaterial] = {
    "Structural Steel": FatigueMaterial(
        name="Structural Steel",
        ultimate_tensile_mpa=400,
        yield_strength_mpa=250,
        endurance_limit_mpa=200,
        youngs_modulus_gpa=200,
        density_kg_m3=7850,
    ),
    "High Strength Steel": FatigueMaterial(
        name="High Strength Steel",
        ultimate_tensile_mpa=800,
        yield_strength_mpa=600,
        endurance_limit_mpa=400,
        youngs_modulus_gpa=205,
        density_kg_m3=7850,
    ),
    "Aluminum 6061-T6": FatigueMaterial(
        name="Aluminum 6061-T6",
        ultimate_tensile_mpa=310,
        yield_strength_mpa=275,
        endurance_limit_mpa=140,
        youngs_modulus_gpa=69,
        density_kg_m3=2700,
    ),
    "Cast Iron": FatigueMaterial(
        name="Cast Iron",
        ultimate_tensile_mpa=250,
        yield_strength_mpa=200,
        endurance_limit_mpa=100,
        youngs_modulus_gpa=100,
        density_kg_m3=7200,
    ),
    "Titanium (Ti-6Al-4V)": FatigueMaterial(
        name="Titanium (Ti-6Al-4V)",
        ultimate_tensile_mpa=950,
        yield_strength_mpa=880,
        endurance_limit_mpa=450,
        youngs_modulus_gpa=114,
        density_kg_m3=4430,
    ),
}


def get_fatigue_material(name: str) -> FatigueMaterial:
    """Get material by name."""
    if name not in FATIGUE_MATERIALS:
        raise ValueError(f"Unknown material: {name}. Available: {list(FATIGUE_MATERIALS.keys())}")
    return FATIGUE_MATERIALS[name]


# ============================================================================
# SECTION 2: ENDURANCE LIMIT FACTORS
# ============================================================================

@dataclass
class EnduranceLimitFactors:
    """Factors affecting endurance limit (Chapter 6.4-6.9)."""
    
    # Surface finish constants (Table 6.1)
    SURFACE_CONSTANTS = {
        'ground': (1.34, -0.085),
        'machined': (4.51, -0.265),
        'cold_drawn': (2.70, -0.265),
        'hot_rolled': (57.7, -0.718),
        'as_forged': (272.0, -0.995),
    }
    
    # Reliability factors (Section 6.8)
    RELIABILITY_FACTORS = {
        50: 1.000,
        90: 0.897,
        95: 0.868,
        99: 0.814,
        99.9: 0.753,
    }
    
    @staticmethod
    def surface_factor(ultimate_tensile_mpa: float, surface_type: str) -> float:
        """Surface finish factor (k_a)."""
        if surface_type not in EnduranceLimitFactors.SURFACE_CONSTANTS:
            raise ValueError(f"Unknown surface type: {surface_type}")
        a, b = EnduranceLimitFactors.SURFACE_CONSTANTS[surface_type]
        return a * (ultimate_tensile_mpa ** b)
    
    @staticmethod
    def size_factor(diameter_mm: float) -> float:
        """Size factor (k_b) for rotating beams."""
        if diameter_mm <= 50:
            return 1.0
        return 1.189 * (diameter_mm ** -0.097)
    
    @staticmethod
    def load_factor(loading_type: str) -> float:
        """Load factor (k_c)."""
        factors = {'bending': 1.0, 'axial': 0.85, 'torsion': 0.58}
        if loading_type not in factors:
            raise ValueError(f"Unknown loading type: {loading_type}")
        return factors[loading_type]
    
    @staticmethod
    def temperature_factor(temperature_c: float) -> float:
        """Temperature factor (k_d)."""
        if temperature_c <= 200:
            return 1.0
        elif temperature_c <= 300:
            return 0.95
        elif temperature_c <= 400:
            return 0.90
        elif temperature_c <= 500:
            return 0.85
        return 0.75
    
    @staticmethod
    def reliability_factor(reliability_percent: float) -> float:
        """Reliability factor (k_e)."""
        if reliability_percent not in EnduranceLimitFactors.RELIABILITY_FACTORS:
            raise ValueError(f"Unknown reliability: {reliability_percent}%")
        return EnduranceLimitFactors.RELIABILITY_FACTORS[reliability_percent]


# ============================================================================
# SECTION 3: ENDURANCE LIMIT RESULT
# ============================================================================

@dataclass
class EnduranceLimitResult:
    """Result of endurance limit calculation."""
    
    base_endurance_mpa: float
    corrected_endurance_mpa: float
    surface_factor: float
    size_factor: float
    load_factor: float
    temperature_factor: float
    reliability_factor: float
    material_name: str
    ultimate_tensile_mpa: float
    
    def print(self):
        print(f"   Material: {self.material_name}")
        print(f"   Ultimate tensile: {self.ultimate_tensile_mpa} MPa")
        print(f"   Base endurance limit: {self.base_endurance_mpa:.1f} MPa")
        print(f"   Corrected endurance limit: {self.corrected_endurance_mpa:.1f} MPa")
        print(f"   Factors: k_a={self.surface_factor:.2f}, k_b={self.size_factor:.2f}, "
              f"k_c={self.load_factor:.2f}, k_d={self.temperature_factor:.2f}, "
              f"k_e={self.reliability_factor:.2f}")


# ============================================================================
# SECTION 4: STRESS CONCENTRATION RESULT
# ============================================================================

@dataclass
class StressConcentrationResult:
    """Result of stress concentration calculation."""
    
    kt_theoretical: float
    notch_sensitivity: float
    kf_fatigue: float
    geometry: str
    dimensions: Dict[str, float]
    
    def print(self):
        print(f"   Geometry: {self.geometry}")
        print(f"   Dimensions: {self.dimensions}")
        print(f"   Theoretical k_t: {self.kt_theoretical:.2f}")
        print(f"   Notch sensitivity q: {self.notch_sensitivity:.2f}")
        print(f"   Fatigue k_f: {self.kf_fatigue:.2f}")


# ============================================================================
# SECTION 5: FATIGUE RESULT (Goodman/Soderberg/Gerber)
# ============================================================================

@dataclass
class FatigueResult:
    """Result of fatigue failure criteria."""
    
    method: str
    factor_of_safety: float
    mean_stress_mpa: float
    alternating_stress_mpa: float
    endurance_limit_mpa: float
    ultimate_tensile_mpa: float
    is_safe: bool
    
    def print(self):
        print(f"   Method: {self.method}")
        print(f"   Mean stress: {self.mean_stress_mpa:.1f} MPa")
        print(f"   Alternating stress: {self.alternating_stress_mpa:.1f} MPa")
        print(f"   Endurance limit: {self.endurance_limit_mpa:.1f} MPa")
        print(f"   Ultimate tensile: {self.ultimate_tensile_mpa:.1f} MPa")
        print(f"   Factor of Safety: {self.factor_of_safety:.2f}")
        print(f"   Status: {'✅ Safe' if self.is_safe else '❌ Unsafe'}")


# ============================================================================
# SECTION 6: FATIGUE ANALYSIS CLASS
# ============================================================================

@dataclass
class FatigueAnalysis:
    """Complete fatigue analysis using Goodman, Soderberg, Gerber."""
    
    material: FatigueMaterial
    target_fos: float = 2.0
    
    def goodman(self, mean_stress_mpa: float, alternating_stress_mpa: float) -> FatigueResult:
        """
        Goodman criterion: 1/FS = σ_m/σ_ut + σ_a/σ_e
        """
        if self.material.endurance_limit_mpa <= 0:
            fos = 999.0
        else:
            denominator = (mean_stress_mpa / self.material.ultimate_tensile_mpa + 
                          alternating_stress_mpa / self.material.endurance_limit_mpa)
            fos = 1 / denominator if denominator > 0 else 999
        
        return FatigueResult(
            method="Goodman",
            factor_of_safety=fos,
            mean_stress_mpa=mean_stress_mpa,
            alternating_stress_mpa=alternating_stress_mpa,
            endurance_limit_mpa=self.material.endurance_limit_mpa,
            ultimate_tensile_mpa=self.material.ultimate_tensile_mpa,
            is_safe=fos >= self.target_fos,
        )
    
    def soderberg(self, mean_stress_mpa: float, alternating_stress_mpa: float) -> FatigueResult:
        """
        Soderberg criterion (more conservative): 1/FS = σ_m/σ_y + σ_a/σ_e
        """
        denominator = (mean_stress_mpa / self.material.yield_strength_mpa + 
                      alternating_stress_mpa / self.material.endurance_limit_mpa)
        fos = 1 / denominator if denominator > 0 else 999
        
        return FatigueResult(
            method="Soderberg",
            factor_of_safety=fos,
            mean_stress_mpa=mean_stress_mpa,
            alternating_stress_mpa=alternating_stress_mpa,
            endurance_limit_mpa=self.material.endurance_limit_mpa,
            ultimate_tensile_mpa=self.material.ultimate_tensile_mpa,
            is_safe=fos >= self.target_fos,
        )
    
    def gerber(self, mean_stress_mpa: float, alternating_stress_mpa: float) -> FatigueResult:
        """
        Gerber criterion (more accurate for ductile materials): σ_a = σ_e[1 - (σ_m/σ_ut)^2]
        """
        if mean_stress_mpa == 0:
            allowable = self.material.endurance_limit_mpa
        else:
            allowable = self.material.endurance_limit_mpa * (1 - (mean_stress_mpa / self.material.ultimate_tensile_mpa)**2)
        
        fos = allowable / alternating_stress_mpa if alternating_stress_mpa > 0 else 999
        
        return FatigueResult(
            method="Gerber",
            factor_of_safety=fos,
            mean_stress_mpa=mean_stress_mpa,
            alternating_stress_mpa=alternating_stress_mpa,
            endurance_limit_mpa=self.material.endurance_limit_mpa,
            ultimate_tensile_mpa=self.material.ultimate_tensile_mpa,
            is_safe=fos >= self.target_fos,
        )
    
    def compare_all(self, mean_stress_mpa: float, alternating_stress_mpa: float) -> Dict[str, float]:
        """Compare all three methods."""
        return {
            "Goodman": self.goodman(mean_stress_mpa, alternating_stress_mpa).factor_of_safety,
            "Soderberg": self.soderberg(mean_stress_mpa, alternating_stress_mpa).factor_of_safety,
            "Gerber": self.gerber(mean_stress_mpa, alternating_stress_mpa).factor_of_safety,
        }


# ============================================================================
# SECTION 7: STRESS CONCENTRATION CALCULATOR
# ============================================================================

@dataclass
class StressConcentrationCalculator:
    """Stress concentration factor calculations."""
    
    @staticmethod
    def shoulder_fillet(D_mm: float, d_mm: float, r_mm: float) -> StressConcentrationResult:
        """Shaft shoulder fillet."""
        d_ratio = D_mm / d_mm
        r_ratio = r_mm / d_mm
        
        if r_ratio < 0.01:
            kt = 3.0 + 5 * (1 - d_ratio)
        elif r_ratio < 0.05:
            kt = 2.5 + 3 * (1 - d_ratio)
        elif r_ratio < 0.10:
            kt = 2.0 + 2 * (1 - d_ratio)
        else:
            kt = 1.8 + 1.5 * (1 - d_ratio)
        
        # Notch sensitivity for steel (approximate)
        q = 0.5 + 0.3 * (1 - math.exp(-r_mm / 2))
        kf = 1 + q * (kt - 1)
        
        return StressConcentrationResult(
            kt_theoretical=kt,
            notch_sensitivity=q,
            kf_fatigue=kf,
            geometry="Shoulder Fillet",
            dimensions={"D": D_mm, "d": d_mm, "r": r_mm},
        )
    
    @staticmethod
    def groove(d_mm: float, r_mm: float) -> StressConcentrationResult:
        """Shaft groove."""
        r_ratio = r_mm / d_mm
        
        if r_ratio < 0.01:
            kt = 4.0
        elif r_ratio < 0.02:
            kt = 3.5
        elif r_ratio < 0.05:
            kt = 3.0
        elif r_ratio < 0.10:
            kt = 2.5
        else:
            kt = 2.2
        
        q = 0.5 + 0.3 * (1 - math.exp(-r_mm / 2))
        kf = 1 + q * (kt - 1)
        
        return StressConcentrationResult(
            kt_theoretical=kt,
            notch_sensitivity=q,
            kf_fatigue=kf,
            geometry="Groove",
            dimensions={"d": d_mm, "r": r_mm},
        )
    
    @staticmethod
    def hole_in_plate(width_mm: float, hole_diameter_mm: float) -> StressConcentrationResult:
        """Hole in flat plate."""
        d_w_ratio = hole_diameter_mm / width_mm
        
        if d_w_ratio <= 0.1:
            kt = 2.7
        elif d_w_ratio <= 0.2:
            kt = 2.5
        elif d_w_ratio <= 0.3:
            kt = 2.3
        else:
            kt = 2.2
        
        q = 0.4  # Lower sensitivity for holes
        kf = 1 + q * (kt - 1)
        
        return StressConcentrationResult(
            kt_theoretical=kt,
            notch_sensitivity=q,
            kf_fatigue=kf,
            geometry="Hole in Plate",
            dimensions={"W": width_mm, "d": hole_diameter_mm},
        )


# ============================================================================
# SECTION 8: FAILURE THEORIES
# ============================================================================

@dataclass
class FailureTheories:
    """Theories of failure under static load."""
    
    material: FatigueMaterial
    target_fos: float = 2.5
    
    def rankine(self, sigma_1_mpa: float) -> float:
        """Maximum principal stress theory."""
        return self.material.yield_strength_mpa / sigma_1_mpa if sigma_1_mpa > 0 else 999
    
    def tresca(self, sigma_1_mpa: float, sigma_3_mpa: float) -> float:
        """Maximum shear stress theory."""
        tau_max = abs(sigma_1_mpa - sigma_3_mpa) / 2
        return (self.material.yield_strength_mpa / 2) / tau_max if tau_max > 0 else 999
    
    def von_mises(self, sigma_x_mpa: float, sigma_y_mpa: float, tau_xy_mpa: float) -> float:
        """Distortion energy theory (von Mises)."""
        sigma_vm = math.sqrt(sigma_x_mpa**2 + sigma_y_mpa**2 - sigma_x_mpa*sigma_y_mpa + 3*tau_xy_mpa**2)
        return self.material.yield_strength_mpa / sigma_vm if sigma_vm > 0 else 999
    
    def von_mises_principal(self, sigma_1_mpa: float, sigma_2_mpa: float, sigma_3_mpa: float = 0) -> float:
        """von Mises from principal stresses."""
        sigma_vm = math.sqrt(0.5 * ((sigma_1_mpa - sigma_2_mpa)**2 + 
                                     (sigma_2_mpa - sigma_3_mpa)**2 + 
                                     (sigma_3_mpa - sigma_1_mpa)**2))
        return self.material.yield_strength_mpa / sigma_vm if sigma_vm > 0 else 999


# ============================================================================
# SECTION 9: EXAMPLE USAGE
# ============================================================================

if __name__ == "__main__":
    print("=" * 75)
    print("DEEP FATIGUE AND FAILURE ANALYSIS MODULE")
    print("=" * 75)
    
    # Create material
    steel = get_fatigue_material("High Strength Steel")
    
    # Example 1: Endurance limit
    print("\n1. ENDURANCE LIMIT CALCULATION:")
    print("-" * 40)
    base_endurance = 0.5 * steel.ultimate_tensile_mpa
    ka = EnduranceLimitFactors.surface_factor(steel.ultimate_tensile_mpa, "machined")
    kb = EnduranceLimitFactors.size_factor(30)
    kc = EnduranceLimitFactors.load_factor("bending")
    kd = EnduranceLimitFactors.temperature_factor(150)
    ke = EnduranceLimitFactors.reliability_factor(95)
    
    corrected = base_endurance * ka * kb * kc * kd * ke
    print(f"   Material: {steel.name}")
    print(f"   Base endurance: {base_endurance:.1f} MPa")
    print(f"   Corrected endurance: {corrected:.1f} MPa")
    
    # Example 2: Fatigue analysis
    print("\n2. FATIGUE ANALYSIS (Connecting Rod):")
    print("-" * 40)
    mean_stress = 50  # MPa
    alt_stress = 200  # MPa
    
    fatigue = FatigueAnalysis(steel, target_fos=2.0)
    
    goodman_result = fatigue.goodman(mean_stress, alt_stress)
    goodman_result.print()
    
    # Example 3: Stress concentration
    print("\n3. STRESS CONCENTRATION (Crankshaft Fillet):")
    print("-" * 40)
    sc = StressConcentrationCalculator.shoulder_fillet(D_mm=80, d_mm=60, r_mm=3)
    sc.print()
    
    # Example 4: Compare all fatigue methods
    print("\n4. COMPARISON OF FATIGUE METHODS:")
    print("-" * 40)
    results = fatigue.compare_all(mean_stress, alt_stress)
    for method, fos in results.items():
        print(f"   {method}: FOS = {fos:.2f}")
    
    # Example 5: Failure theories
    print("\n5. FAILURE THEORIES (Cylinder Wall):")
    print("-" * 40)
    sigma_x, sigma_y, tau_xy = 120, 60, 0
    theories = FailureTheories(steel, target_fos=2.5)
    
    vm_fs = theories.von_mises(sigma_x, sigma_y, tau_xy)
    print(f"   Stress state: σx={sigma_x}, σy={sigma_y}, τxy={tau_xy} MPa")
    print(f"   von Mises FOS: {vm_fs:.2f}")
    
    print("\n" + "=" * 75)
    print("✅ Deep failure module ready")
    print("=" * 75)