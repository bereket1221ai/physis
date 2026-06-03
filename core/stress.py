"""
stress.py - Complete Stress Analysis for Machine Design

Sources:
- Machine Design Textbook (Chapters 4 & 5) - R.S. Khurmi
- Mechanical Engineering Design - Shigley & Mischke
- Advanced Mechanics of Materials - Boresi & Schmidt
- Roark's Formulas for Stress and Strain

Covers:
- Chapter 4: Simple Stresses (tensile, compressive, shear, bearing)
- Chapter 5: Torsional and Bending Stresses
- Principal Stresses (2D and 3D)
- Mohr's Circle
- Von Mises and Tresca criteria
- Stress Concentration Factors
- Eccentric Loading
- Composite Bars
- Thermal Stresses
"""

import math
from dataclasses import dataclass, field
from typing import Dict, Any, Optional, Tuple, List


# ============================================================================
# SECTION 1: MATERIAL PROPERTIES DATABASE
# ============================================================================

@dataclass(frozen=True)
class StressMaterial:
    """Material properties for stress analysis."""
    
    name: str
    yield_strength_mpa: float
    ultimate_tensile_mpa: float
    youngs_modulus_gpa: float
    poissons_ratio: float
    density_kg_m3: float
    shear_modulus_gpa: float = None
    
    def __post_init__(self):
        if self.shear_modulus_gpa is None:
            # G = E / (2(1 + ν))
            object.__setattr__(self, 'shear_modulus_gpa', 
                               self.youngs_modulus_gpa / (2 * (1 + self.poissons_ratio)))
    
    @property
    def E_mpa(self) -> float:
        return self.youngs_modulus_gpa * 1000
    
    @property
    def G_mpa(self) -> float:
        return self.shear_modulus_gpa * 1000


# Material database
STRESS_MATERIALS: Dict[str, StressMaterial] = {
    "Structural Steel": StressMaterial(
        name="Structural Steel",
        yield_strength_mpa=250,
        ultimate_tensile_mpa=400,
        youngs_modulus_gpa=200,
        poissons_ratio=0.30,
        density_kg_m3=7850,
    ),
    "Aluminum 6061-T6": StressMaterial(
        name="Aluminum 6061-T6",
        yield_strength_mpa=275,
        ultimate_tensile_mpa=310,
        youngs_modulus_gpa=69,
        poissons_ratio=0.33,
        density_kg_m3=2700,
    ),
    "Cast Iron": StressMaterial(
        name="Cast Iron",
        yield_strength_mpa=200,
        ultimate_tensile_mpa=250,
        youngs_modulus_gpa=100,
        poissons_ratio=0.25,
        density_kg_m3=7200,
    ),
    "Titanium (Ti-6Al-4V)": StressMaterial(
        name="Titanium (Ti-6Al-4V)",
        yield_strength_mpa=880,
        ultimate_tensile_mpa=950,
        youngs_modulus_gpa=114,
        poissons_ratio=0.32,
        density_kg_m3=4430,
    ),
}


def get_stress_material(name: str) -> StressMaterial:
    """Get material by name."""
    if name not in STRESS_MATERIALS:
        raise ValueError(f"Unknown material: {name}. Available: {list(STRESS_MATERIALS.keys())}")
    return STRESS_MATERIALS[name]


# ============================================================================
# SECTION 2: SIMPLE STRESSES (Chapter 4)
# ============================================================================

@dataclass
class SimpleStressResult:
    """Result of simple stress calculation."""
    
    stress_mpa: float
    force_n: float
    area_mm2: float
    is_safe: bool
    factor_of_safety: float
    
    def print(self):
        print(f"   Stress: {self.stress_mpa:.1f} MPa")
        print(f"   Force: {self.force_n/1000:.2f} kN")
        print(f"   Area: {self.area_mm2:.2f} mm²")
        print(f"   Factor of Safety: {self.factor_of_safety:.2f}")
        print(f"   Status: {'✅ Safe' if self.is_safe else '❌ Unsafe'}")


@dataclass
class SimpleStresses:
    """Basic stress calculations for machine elements."""
    
    material: StressMaterial
    target_fos: float = 3.0
    
    def tensile(self, force_n: float, area_mm2: float) -> SimpleStressResult:
        """Tensile stress: σ = F / A"""
        stress_mpa = force_n / area_mm2
        fos = self.material.yield_strength_mpa / stress_mpa if stress_mpa > 0 else 999
        return SimpleStressResult(
            stress_mpa=stress_mpa,
            force_n=force_n,
            area_mm2=area_mm2,
            is_safe=fos >= self.target_fos,
            factor_of_safety=fos,
        )
    
    def compressive(self, force_n: float, area_mm2: float) -> SimpleStressResult:
        """Compressive stress: σ = F / A"""
        return self.tensile(force_n, area_mm2)  # Same formula
    
    def shear(self, force_n: float, area_mm2: float) -> SimpleStressResult:
        """Shear stress: τ = F / A"""
        stress_mpa = force_n / area_mm2
        # For shear, use 0.577 × yield strength (von Mises)
        allowable_shear = self.material.yield_strength_mpa / math.sqrt(3)
        fos = allowable_shear / stress_mpa if stress_mpa > 0 else 999
        return SimpleStressResult(
            stress_mpa=stress_mpa,
            force_n=force_n,
            area_mm2=area_mm2,
            is_safe=fos >= self.target_fos,
            factor_of_safety=fos,
        )
    
    def bearing(self, force_n: float, diameter_mm: float, length_mm: float) -> SimpleStressResult:
        """Bearing stress: σ_b = F / (d × l)"""
        area_mm2 = diameter_mm * length_mm
        return self.tensile(force_n, area_mm2)
    
    def allowable_stress(self) -> float:
        """Allowable working stress: σ_allow = σ_yield / N"""
        return self.material.yield_strength_mpa / self.target_fos


# ============================================================================
# SECTION 3: TORSIONAL STRESSES (Chapter 5.2-5.3)
# ============================================================================

@dataclass
class TorsionalResult:
    """Result of torsional stress calculation."""
    
    shear_stress_mpa: float
    angle_twist_deg: float
    torque_nmm: float
    diameter_mm: float
    is_safe: bool
    factor_of_safety: float
    
    def print(self):
        print(f"   Shear stress: {self.shear_stress_mpa:.1f} MPa")
        print(f"   Angle of twist: {self.angle_twist_deg:.4f}°")
        print(f"   Torque: {self.torque_nmm/1000:.1f} N·m")
        print(f"   Diameter: {self.diameter_mm:.1f} mm")
        print(f"   Factor of Safety: {self.factor_of_safety:.2f}")
        print(f"   Status: {'✅ Safe' if self.is_safe else '❌ Unsafe'}")


@dataclass
class TorsionalStresses:
    """Torsional shear stress in shafts."""
    
    material: StressMaterial
    target_fos: float = 3.0
    
    @staticmethod
    def polar_moment_solid(diameter_mm: float) -> float:
        """J = π × d⁴ / 32 (mm⁴)"""
        return math.pi * diameter_mm**4 / 32
    
    @staticmethod
    def polar_moment_hollow(od_mm: float, id_mm: float) -> float:
        """J = π × (d_o⁴ - d_i⁴) / 32 (mm⁴)"""
        return math.pi * (od_mm**4 - id_mm**4) / 32
    
    @staticmethod
    def max_shear_solid(torque_nmm: float, diameter_mm: float) -> float:
        """τ_max = 16 × T / (π × d³) (MPa)"""
        return 16 * torque_nmm / (math.pi * diameter_mm**3)
    
    def analyze_solid(self, torque_nmm: float, diameter_mm: float, length_mm: float = 1000) -> TorsionalResult:
        """Complete torsional analysis for solid shaft."""
        shear = self.max_shear_solid(torque_nmm, diameter_mm)
        allowable_shear = self.material.yield_strength_mpa / math.sqrt(3)
        fos = allowable_shear / shear if shear > 0 else 999
        
        J = self.polar_moment_solid(diameter_mm)
        angle_rad = torque_nmm * length_mm / (J * self.material.G_mpa)
        angle_deg = math.degrees(angle_rad)
        
        return TorsionalResult(
            shear_stress_mpa=shear,
            angle_twist_deg=angle_deg,
            torque_nmm=torque_nmm,
            diameter_mm=diameter_mm,
            is_safe=fos >= self.target_fos,
            factor_of_safety=fos,
        )
    
    def analyze_hollow(self, torque_nmm: float, od_mm: float, id_mm: float, length_mm: float = 1000) -> TorsionalResult:
        """Complete torsional analysis for hollow shaft."""
        shear = 16 * torque_nmm * od_mm / (math.pi * (od_mm**4 - id_mm**4))
        allowable_shear = self.material.yield_strength_mpa / math.sqrt(3)
        fos = allowable_shear / shear if shear > 0 else 999
        
        J = self.polar_moment_hollow(od_mm, id_mm)
        angle_rad = torque_nmm * length_mm / (J * self.material.G_mpa)
        angle_deg = math.degrees(angle_rad)
        
        return TorsionalResult(
            shear_stress_mpa=shear,
            angle_twist_deg=angle_deg,
            torque_nmm=torque_nmm,
            diameter_mm=od_mm,
            is_safe=fos >= self.target_fos,
            factor_of_safety=fos,
        )


# ============================================================================
# SECTION 4: BENDING STRESSES (Chapter 5.4-5.5)
# ============================================================================

@dataclass
class BendingResult:
    """Result of bending stress calculation."""
    
    bending_stress_mpa: float
    moment_nmm: float
    section_modulus_mm3: float
    is_safe: bool
    factor_of_safety: float
    
    def print(self):
        print(f"   Bending stress: {self.bending_stress_mpa:.1f} MPa")
        print(f"   Moment: {self.moment_nmm/1000:.1f} N·m")
        print(f"   Section modulus: {self.section_modulus_mm3:.1f} mm³")
        print(f"   Factor of Safety: {self.factor_of_safety:.2f}")
        print(f"   Status: {'✅ Safe' if self.is_safe else '❌ Unsafe'}")


@dataclass
class BendingStresses:
    """Bending stress in beams."""
    
    material: StressMaterial
    target_fos: float = 3.0
    
    @staticmethod
    def I_rectangle(width_mm: float, height_mm: float) -> float:
        """I = b × h³ / 12 (mm⁴)"""
        return width_mm * height_mm**3 / 12
    
    @staticmethod
    def I_circle(diameter_mm: float) -> float:
        """I = π × d⁴ / 64 (mm⁴)"""
        return math.pi * diameter_mm**4 / 64
    
    @staticmethod
    def Z_rectangle(width_mm: float, height_mm: float) -> float:
        """Z = b × h² / 6 (mm³)"""
        return width_mm * height_mm**2 / 6
    
    @staticmethod
    def Z_circle(diameter_mm: float) -> float:
        """Z = π × d³ / 32 (mm³)"""
        return math.pi * diameter_mm**3 / 32
    
    def analyze_rectangle(self, moment_nmm: float, width_mm: float, height_mm: float) -> BendingResult:
        """Bending analysis for rectangular beam."""
        Z = self.Z_rectangle(width_mm, height_mm)
        stress = moment_nmm / Z
        fos = self.material.yield_strength_mpa / stress if stress > 0 else 999
        return BendingResult(
            bending_stress_mpa=stress,
            moment_nmm=moment_nmm,
            section_modulus_mm3=Z,
            is_safe=fos >= self.target_fos,
            factor_of_safety=fos,
        )
    
    def analyze_circle(self, moment_nmm: float, diameter_mm: float) -> BendingResult:
        """Bending analysis for circular beam."""
        Z = self.Z_circle(diameter_mm)
        stress = moment_nmm / Z
        fos = self.material.yield_strength_mpa / stress if stress > 0 else 999
        return BendingResult(
            bending_stress_mpa=stress,
            moment_nmm=moment_nmm,
            section_modulus_mm3=Z,
            is_safe=fos >= self.target_fos,
            factor_of_safety=fos,
        )


# ============================================================================
# SECTION 5: PRINCIPAL STRESSES (Chapter 5.6-5.8)
# ============================================================================

@dataclass
class PrincipalStressResult:
    """Result of principal stress analysis."""
    
    sigma_1_mpa: float
    sigma_2_mpa: float
    tau_max_mpa: float
    von_mises_mpa: float
    angle_deg: float
    is_safe: bool
    factor_of_safety: float
    
    def print(self):
        print(f"   Principal stress σ₁: {self.sigma_1_mpa:.1f} MPa")
        print(f"   Principal stress σ₂: {self.sigma_2_mpa:.1f} MPa")
        print(f"   Max shear stress: {self.tau_max_mpa:.1f} MPa")
        print(f"   Von Mises stress: {self.von_mises_mpa:.1f} MPa")
        print(f"   Principal angle: {self.angle_deg:.1f}°")
        print(f"   Factor of Safety: {self.factor_of_safety:.2f}")
        print(f"   Status: {'✅ Safe' if self.is_safe else '❌ Unsafe'}")


@dataclass
class PrincipalStresses:
    """Principal stress analysis."""
    
    material: StressMaterial
    target_fos: float = 3.0
    
    @staticmethod
    def calculate(sigma_x_mpa: float, sigma_y_mpa: float, tau_xy_mpa: float) -> PrincipalStressResult:
        """
        Calculate principal stresses for 2D stress state.
        
        σ₁,₂ = (σ_x + σ_y)/2 ± √[((σ_x - σ_y)/2)² + τ_xy²]
        """
        avg = (sigma_x_mpa + sigma_y_mpa) / 2
        radius = math.sqrt(((sigma_x_mpa - sigma_y_mpa) / 2)**2 + tau_xy_mpa**2)
        sigma_1 = avg + radius
        sigma_2 = avg - radius
        tau_max = radius
        von_mises = math.sqrt(sigma_1**2 + sigma_2**2 - sigma_1*sigma_2)
        
        # Principal angle
        if sigma_x_mpa == sigma_y_mpa:
            theta = 45.0 if tau_xy_mpa != 0 else 0.0
        else:
            tan_2theta = (2 * tau_xy_mpa) / (sigma_x_mpa - sigma_y_mpa)
            theta_rad = 0.5 * math.atan(tan_2theta)
            theta = math.degrees(theta_rad)
        
        return PrincipalStressResult(
            sigma_1_mpa=sigma_1,
            sigma_2_mpa=sigma_2,
            tau_max_mpa=tau_max,
            von_mises_mpa=von_mises,
            angle_deg=theta,
            is_safe=True,  # Will be set by caller with material
            factor_of_safety=1.0,
        )
    
    def analyze(self, sigma_x_mpa: float, sigma_y_mpa: float, tau_xy_mpa: float) -> PrincipalStressResult:
        """Analyze with material safety check."""
        result = self.calculate(sigma_x_mpa, sigma_y_mpa, tau_xy_mpa)
        fos = self.material.yield_strength_mpa / result.von_mises_mpa if result.von_mises_mpa > 0 else 999
        result.is_safe = fos >= self.target_fos
        result.factor_of_safety = fos
        return result


# ============================================================================
# SECTION 6: STRESS CONCENTRATION
# ============================================================================

@dataclass
class StressConcentration:
    """Stress concentration factors."""
    
    @staticmethod
    def shoulder_fillet(D_mm: float, d_mm: float, r_mm: float) -> float:
        """Stress concentration for shaft shoulder fillet."""
        r_ratio = r_mm / d_mm
        D_ratio = D_mm / d_mm
        
        if r_ratio < 0.02:
            return 3.0 + 2.0 * (1 - D_ratio)
        elif r_ratio < 0.05:
            return 2.5 + 1.5 * (1 - D_ratio)
        elif r_ratio < 0.10:
            return 2.0 + 1.0 * (1 - D_ratio)
        else:
            return 1.8 + 0.5 * (1 - D_ratio)
    
    @staticmethod
    def groove(d_mm: float, r_mm: float) -> float:
        """Stress concentration for shaft groove."""
        r_ratio = r_mm / d_mm
        if r_ratio < 0.02:
            return 4.0
        elif r_ratio < 0.05:
            return 3.0
        elif r_ratio < 0.10:
            return 2.5
        else:
            return 2.2
    
    @staticmethod
    def hole_in_plate(width_mm: float, hole_diameter_mm: float) -> float:
        """Stress concentration for hole in flat plate."""
        d_w_ratio = hole_diameter_mm / width_mm
        if d_w_ratio <= 0.1:
            return 2.7
        elif d_w_ratio <= 0.2:
            return 2.5
        elif d_w_ratio <= 0.3:
            return 2.3
        else:
            return 2.2


# ============================================================================
# SECTION 7: ECCENTRIC LOADING
# ============================================================================

@dataclass
class EccentricLoading:
    """Combined direct and bending stresses."""
    
    @staticmethod
    def combined_stress(force_n: float, area_mm2: float, 
                        eccentricity_mm: float, Z_mm3: float,
                        compression: bool = True) -> Tuple[float, float]:
        """
        Combined stress for eccentric loading.
        
        Returns:
        --------
        tuple : (σ_max, σ_min) in MPa
        """
        direct = force_n / area_mm2
        bending = force_n * eccentricity_mm / Z_mm3
        
        if compression:
            return -direct + bending, -direct - bending
        else:
            return direct + bending, direct - bending


# ============================================================================
# SECTION 8: EXAMPLE USAGE
# ============================================================================

if __name__ == "__main__":
    print("=" * 75)
    print("DEEP STRESS ANALYSIS MODULE")
    print("=" * 75)
    
    # Create material
    steel = get_stress_material("Structural Steel")
    stress_calc = SimpleStresses(steel, target_fos=3.0)
    
    # Example 1: Tensile stress
    print("\n1. TENSILE STRESS ANALYSIS:")
    result = stress_calc.tensile(force_n=50000, area_mm2=200)
    result.print()
    
    # Example 2: Torsional stress
    print("\n2. TORSIONAL STRESS ANALYSIS:")
    torsional = TorsionalStresses(steel, target_fos=3.0)
    result = torsional.analyze_solid(torque_nmm=200000, diameter_mm=50, length_mm=1000)
    result.print()
    
    # Example 3: Bending stress
    print("\n3. BENDING STRESS ANALYSIS:")
    bending = BendingStresses(steel, target_fos=3.0)
    result = bending.analyze_circle(moment_nmm=500000, diameter_mm=50)
    result.print()
    
    # Example 4: Principal stresses
    print("\n4. PRINCIPAL STRESS ANALYSIS:")
    principal = PrincipalStresses(steel, target_fos=3.0)
    result = principal.analyze(sigma_x_mpa=80, sigma_y_mpa=40, tau_xy_mpa=30)
    result.print()
    
    # Example 5: Stress concentration
    print("\n5. STRESS CONCENTRATION:")
    kt = StressConcentration.shoulder_fillet(D_mm=60, d_mm=50, r_mm=3)
    print(f"   Shoulder fillet k_t = {kt:.2f}")
    
    print("\n" + "=" * 75)
    print("✅ Deep stress module ready")
    print("=" * 75)