"""
piston_pin.py - Complete Piston Pin (Wrist Pin) Design for IC Engines

Sources:
- Machine Design Textbook (Chapter 32.11-32.12) - R.S. Khurmi
- Internal Combustion Engine Fundamentals - John B. Heywood
- Mechanical Engineering Design - Shigley & Mischke
- SAE International standards

Covers:
- 32.11: Piston Pin introduction
- 32.12: Piston Pin design (continued)
- Pin loading (bending + shear)
- Bearing pressure analysis
- Hollow pin optimization
- Pin materials (case hardened steel)
- Pin retention (full-floating vs semi-floating)
- Ovalization and deflection
- Fatigue analysis (Goodman/Soderberg)
- Pin offset for noise reduction
"""

import math
from dataclasses import dataclass, field
from typing import Dict, Any, Optional, Tuple, List


# ============================================================================
# SECTION 1: PISTON PIN MATERIALS DATABASE
# ============================================================================

@dataclass(frozen=True)
class PistonPinMaterial:
    """Material properties for piston pins (wrist pins)."""
    
    name: str
    density_kg_m3: float
    ultimate_tensile_mpa: float
    yield_strength_mpa: float
    fatigue_limit_mpa: float
    endurance_limit_mpa: float
    youngs_modulus_gpa: float
    hardness_core_hb: float
    hardness_surface_hb: float
    case_depth_mm: float
    description: str


# Piston pin material database
PISTON_PIN_MATERIALS: Dict[str, PistonPinMaterial] = {
    "Case Hardened Steel (8620)": PistonPinMaterial(
        name="Case Hardened Steel (8620)",
        density_kg_m3=7850,
        ultimate_tensile_mpa=980,
        yield_strength_mpa=750,
        fatigue_limit_mpa=380,
        endurance_limit_mpa=350,
        youngs_modulus_gpa=205,
        hardness_core_hb=280,
        hardness_surface_hb=600,
        case_depth_mm=0.8,
        description="Excellent wear resistance, good fatigue strength",
    ),
    "Case Hardened Steel (4320)": PistonPinMaterial(
        name="Case Hardened Steel (4320)",
        density_kg_m3=7850,
        ultimate_tensile_mpa=1080,
        yield_strength_mpa=850,
        fatigue_limit_mpa=420,
        endurance_limit_mpa=380,
        youngs_modulus_gpa=205,
        hardness_core_hb=310,
        hardness_surface_hb=650,
        case_depth_mm=1.0,
        description="Very high strength, premium material",
    ),
    "Through Hardened Steel (4140)": PistonPinMaterial(
        name="Through Hardened Steel (4140)",
        density_kg_m3=7850,
        ultimate_tensile_mpa=950,
        yield_strength_mpa=830,
        fatigue_limit_mpa=400,
        endurance_limit_mpa=360,
        youngs_modulus_gpa=205,
        hardness_core_hb=320,
        hardness_surface_hb=320,
        case_depth_mm=0,
        description="Uniform hardness, good for semi-floating pins",
    ),
    "Nitrided Steel": PistonPinMaterial(
        name="Nitrided Steel",
        density_kg_m3=7800,
        ultimate_tensile_mpa=900,
        yield_strength_mpa=700,
        fatigue_limit_mpa=420,
        endurance_limit_mpa=380,
        youngs_modulus_gpa=200,
        hardness_core_hb=280,
        hardness_surface_hb=700,
        case_depth_mm=0.4,
        description="Very hard surface, excellent wear resistance",
    ),
}


def get_piston_pin_material(name: str) -> PistonPinMaterial:
    """Get piston pin material by name."""
    if name not in PISTON_PIN_MATERIALS:
        raise ValueError(f"Unknown material: {name}. Available: {list(PISTON_PIN_MATERIALS.keys())}")
    return PISTON_PIN_MATERIALS[name]


# ============================================================================
# SECTION 2: PISTON PIN GEOMETRY
# ============================================================================

@dataclass
class PistonPinGeometry:
    """Piston pin geometric parameters."""
    
    bore_mm: float
    outer_diameter_mm: Optional[float] = None
    inner_diameter_mm: Optional[float] = None
    pin_length_mm: Optional[float] = None
    pin_type: str = "full_floating"  # full_floating or semi_floating
    
    def __post_init__(self):
        # Pin outer diameter (typical: 0.25 to 0.35 × bore)
        if self.outer_diameter_mm is None:
            self.outer_diameter_mm = 0.28 * self.bore_mm
        
        # Pin inner diameter (hollow pin for weight reduction)
        if self.inner_diameter_mm is None:
            self.inner_diameter_mm = 0.6 * self.outer_diameter_mm
        
        # Pin length (typical: 0.75 to 0.9 × bore)
        if self.pin_length_mm is None:
            self.pin_length_mm = 0.85 * self.bore_mm
        
        # Bearing lengths
        self.piston_boss_length_mm = 0.4 * self.pin_length_mm
        self.rod_small_end_length_mm = 0.5 * self.pin_length_mm
        self.unsupported_end_length_mm = (
            self.pin_length_mm - self.piston_boss_length_mm - self.rod_small_end_length_mm
        ) / 2
    
    @property
    def area_mm2(self) -> float:
        """Cross-sectional area of hollow pin."""
        return math.pi * (self.outer_diameter_mm**2 - self.inner_diameter_mm**2) / 4
    
    @property
    def area_m2(self) -> float:
        return self.area_mm2 / 1e6
    
    @property
    def I_mm4(self) -> float:
        """Area moment of inertia."""
        return math.pi * (self.outer_diameter_mm**4 - self.inner_diameter_mm**4) / 64
    
    @property
    def I_m4(self) -> float:
        return self.I_mm4 / 1e12
    
    @property
    def Z_mm3(self) -> float:
        """Section modulus."""
        return self.I_mm4 / (self.outer_diameter_mm / 2)
    
    @property
    def hollowness_ratio(self) -> float:
        """Ratio of inner to outer diameter (0 = solid, 0.6 = typical)."""
        return self.inner_diameter_mm / self.outer_diameter_mm
    
    @property
    def weight_savings_percent(self) -> float:
        """Weight savings compared to solid pin."""
        ratio = self.hollowness_ratio
        return (1 - (1 - ratio**2)) * 100


# ============================================================================
# SECTION 3: PISTON PIN FORCES
# ============================================================================

@dataclass
class PistonPinForces:
    """Forces acting on piston pin."""
    
    bore_mm: float
    max_gas_pressure_mpa: float
    reciprocating_mass_kg: float
    max_rpm: float
    stroke_mm: float
    rod_length_mm: float
    
    def __post_init__(self):
        self.crank_radius_m = self.stroke_mm / 2000
        self.omega = 2 * math.pi * self.max_rpm / 60
        self.piston_area_m2 = math.pi * (self.bore_mm/1000)**2 / 4
        self.gas_force_n = self.max_gas_pressure_mpa * 1e6 * self.piston_area_m2
        self.reciprocating_mass = self.reciprocating_mass_kg
    
    @property
    def gas_force_kn(self) -> float:
        return self.gas_force_n / 1000
    
    @property
    def inertia_force_tdc_n(self) -> float:
        """Inertia force at TDC (tension)."""
        return self.reciprocating_mass * self.omega**2 * self.crank_radius_m * 1.2
    
    @property
    def max_compressive_force_n(self) -> float:
        """Maximum compressive force on pin."""
        return self.gas_force_n - self.inertia_force_tdc_n
    
    @property
    def max_tensile_force_n(self) -> float:
        """Maximum tensile force on pin."""
        return abs(self.inertia_force_tdc_n)
    
    @property
    def load_per_boss_n(self) -> float:
        """Load on each piston boss."""
        return self.max_compressive_force_n / 2


# ============================================================================
# SECTION 4: PISTON PIN STRESS ANALYSIS
# ============================================================================

@dataclass
class PistonPinStressAnalysis:
    """Complete stress analysis for piston pin."""
    
    geometry: PistonPinGeometry
    forces: PistonPinForces
    material: PistonPinMaterial
    
    @property
    def bearing_pressure_boss_mpa(self) -> float:
        """Bearing pressure between pin and piston boss."""
        load_n = self.forces.load_per_boss_n
        area_mm2 = self.geometry.outer_diameter_mm * self.geometry.piston_boss_length_mm
        return load_n / area_mm2 if area_mm2 > 0 else 0
    
    @property
    def bearing_pressure_rod_mpa(self) -> float:
        """Bearing pressure between pin and connecting rod small end."""
        load_n = self.forces.max_compressive_force_n
        area_mm2 = self.geometry.outer_diameter_mm * self.geometry.rod_small_end_length_mm
        return load_n / area_mm2 if area_mm2 > 0 else 0
    
    @property
    def allowable_bearing_pressure_mpa(self) -> float:
        """Allowable bearing pressure (case hardened steel)."""
        return 50.0
    
    @property
    def bending_stress_mpa(self) -> float:
        """
        Bending stress in piston pin (simply supported beam model).
        """
        # Effective span between piston bosses
        span_mm = (
            self.geometry.pin_length_mm 
            - 2 * self.geometry.unsupported_end_length_mm
            - self.geometry.rod_small_end_length_mm
        )
        
        load_n = self.forces.max_compressive_force_n
        
        # Concentrated load at center (simplified, conservative)
        bending_moment_nmm = load_n * span_mm / 4
        section_modulus = self.geometry.Z_mm3
        
        return bending_moment_nmm / section_modulus if section_modulus > 0 else 0
    
    @property
    def shear_stress_mpa(self) -> float:
        """Shear stress in piston pin."""
        load_n = self.forces.max_compressive_force_n / 2  # Each shear plane
        area_mm2 = self.geometry.area_mm2
        return (4/3) * (load_n / area_mm2) if area_mm2 > 0 else 0
    
    @property
    def von_mises_stress_mpa(self) -> float:
        """Von Mises equivalent stress."""
        sigma_b = self.bending_stress_mpa
        tau = self.shear_stress_mpa
        return math.sqrt(sigma_b**2 + 3 * tau**2)
    
    @property
    def bending_deflection_mm(self) -> float:
        """Bending deflection of pin as beam."""
        load_n = self.forces.max_compressive_force_n
        span_m = self.geometry.pin_length_mm / 1000
        E_pa = self.material.youngs_modulus_gpa * 1e9
        I_m4 = self.geometry.I_m4
        deflection_m = (load_n * span_m**3) / (48 * E_pa * I_m4)
        return deflection_m * 1000
    
    @property
    def ovalization_mm(self) -> float:
        """Ovalization (flattening) of hollow pin under load."""
        load_n = self.forces.max_compressive_force_n
        d_o_m = self.geometry.outer_diameter_mm / 1000
        E_pa = self.material.youngs_modulus_gpa * 1e9
        I_m4 = self.geometry.I_m4
        ratio = self.geometry.hollowness_ratio
        deflection_m = (load_n * d_o_m**3) / (E_pa * I_m4 * (1 - ratio**2)) * 0.01
        return deflection_m * 1000
    
    @property
    def total_deflection_mm(self) -> float:
        """Total deflection (bending + ovalization)."""
        return self.bending_deflection_mm + self.ovalization_mm
    
    @property
    def factor_of_safety(self) -> float:
        """Factor of safety against yielding."""
        vm = self.von_mises_stress_mpa
        if vm <= 0:
            return 999
        return self.material.yield_strength_mpa / vm


# ============================================================================
# SECTION 5: FATIGUE ANALYSIS (Goodman)
# ============================================================================

@dataclass
class PistonPinFatigue:
    """Fatigue analysis for piston pin."""
    
    material: PistonPinMaterial
    bending_stress_mpa: float
    shear_stress_mpa: float
    
    @property
    def equivalent_stress_mpa(self) -> float:
        return math.sqrt(self.bending_stress_mpa**2 + 3 * self.shear_stress_mpa**2)
    
    def goodman_fos(self, mean_stress_mpa: float = 0) -> float:
        """Goodman fatigue criterion."""
        sigma_a = self.equivalent_stress_mpa
        sigma_m = mean_stress_mpa
        sigma_e = self.material.endurance_limit_mpa
        sigma_u = self.material.ultimate_tensile_mpa
        
        if sigma_e <= 0:
            return 999
        return 1 / (sigma_a/sigma_e + sigma_m/sigma_u)
    
    @property
    def infinite_life(self) -> bool:
        return self.goodman_fos() >= 1.0


# ============================================================================
# SECTION 6: COMPLETE PISTON PIN RESULT
# ============================================================================

@dataclass
class PistonPinResult:
    """Complete piston pin design results."""
    
    # Geometry
    outer_diameter_mm: float
    inner_diameter_mm: float
    pin_length_mm: float
    hollowness_ratio: float
    weight_savings_percent: float
    piston_boss_length_mm: float
    rod_small_end_length_mm: float
    
    # Forces
    max_gas_force_kN: float
    max_compressive_force_kN: float
    max_tensile_force_kN: float
    
    # Bearing pressures
    boss_bearing_pressure_mpa: float
    rod_bearing_pressure_mpa: float
    allowable_bearing_pressure_mpa: float
    
    # Stresses
    bending_stress_mpa: float
    shear_stress_mpa: float
    von_mises_stress_mpa: float
    factor_of_safety: float
    
    # Deflections
    bending_deflection_mm: float
    ovalization_mm: float
    total_deflection_mm: float
    
    # Fatigue
    goodman_fos: float
    infinite_life: bool
    
    # Material
    material_name: str
    material_description: str
    surface_hardness_hb: int
    case_depth_mm: float
    
    # Mass
    pin_mass_g: float
    
    @property
    def is_safe(self) -> bool:
        return (
            self.factor_of_safety >= 2.5 and
            self.boss_bearing_pressure_mpa <= self.allowable_bearing_pressure_mpa and
            self.goodman_fos >= 1.0
        )
    
    def print_report(self):
        print("=" * 75)
        print("PISTON PIN (WRIST PIN) DESIGN REPORT")
        print("Sources: Khurmi (Chap 32.11-32.12), Heywood, Shigley")
        print("=" * 75)
        
        print("\n📏 PIN DIMENSIONS:")
        print(f"   Outer diameter: {self.outer_diameter_mm:.2f} mm")
        print(f"   Inner diameter: {self.inner_diameter_mm:.2f} mm")
        print(f"   Total length: {self.pin_length_mm:.2f} mm")
        print(f"   Piston boss length: {self.piston_boss_length_mm:.2f} mm")
        print(f"   Rod small end length: {self.rod_small_end_length_mm:.2f} mm")
        print(f"   Hollowness ratio (di/do): {self.hollowness_ratio:.2f}")
        print(f"   Weight savings: {self.weight_savings_percent:.0f}%")
        
        print("\n⚡ FORCES:")
        print(f"   Max gas force: {self.max_gas_force_kN:.1f} kN")
        print(f"   Max compressive force: {self.max_compressive_force_kN:.1f} kN")
        print(f"   Max tensile force: {self.max_tensile_force_kN:.1f} kN")
        
        print("\n🔧 BEARING PRESSURES:")
        boss_status = "✅ OK" if self.boss_bearing_pressure_mpa <= self.allowable_bearing_pressure_mpa else "⚠️ HIGH"
        print(f"   Piston boss: {self.boss_bearing_pressure_mpa:.2f} MPa (allowable: {self.allowable_bearing_pressure_mpa:.0f}) {boss_status}")
        rod_status = "✅ OK" if self.rod_bearing_pressure_mpa <= self.allowable_bearing_pressure_mpa else "⚠️ HIGH"
        print(f"   Rod small end: {self.rod_bearing_pressure_mpa:.2f} MPa (allowable: {self.allowable_bearing_pressure_mpa:.0f}) {rod_status}")
        
        print("\n📊 STRESS ANALYSIS:")
        print(f"   Bending stress: {self.bending_stress_mpa:.1f} MPa")
        print(f"   Shear stress: {self.shear_stress_mpa:.1f} MPa")
        print(f"   Von Mises stress: {self.von_mises_stress_mpa:.1f} MPa")
        print(f"   Factor of safety: {self.factor_of_safety:.2f}")
        
        print("\n📐 DEFLECTION:")
        print(f"   Bending deflection: {self.bending_deflection_mm:.4f} mm")
        print(f"   Ovalization: {self.ovalization_mm:.4f} mm")
        print(f"   Total deflection: {self.total_deflection_mm:.4f} mm")
        
        print("\n🔄 FATIGUE ANALYSIS:")
        print(f"   Goodman FOS: {self.goodman_fos:.2f}")
        print(f"   Infinite life: {'✅ Yes' if self.infinite_life else '⚠️ No'}")
        
        print("\n🏗️ MATERIAL:")
        print(f"   Material: {self.material_name}")
        print(f"   {self.material_description}")
        print(f"   Surface hardness: {self.surface_hardness_hb} HB")
        print(f"   Case depth: {self.case_depth_mm:.1f} mm")
        
        print("\n⚖️ MASS:")
        print(f"   Pin mass: {self.pin_mass_g:.1f} g")
        
        print("\n" + "=" * 75)
        
        if not self.is_safe:
            print("\n⚠️ DESIGN ISSUES:")
            if self.factor_of_safety < 2.5:
                print("   - Factor of safety below 2.5")
            if self.boss_bearing_pressure_mpa > self.allowable_bearing_pressure_mpa:
                print("   - Boss bearing pressure exceeds allowable")
            if self.goodman_fos < 1.0:
                print("   - Fatigue life not infinite")
        else:
            print("\n✅ DESIGN ACCEPTABLE - All criteria satisfied")
        
        print("=" * 75)


# ============================================================================
# SECTION 7: COMPLETE PISTON PIN DESIGNER
# ============================================================================

class PistonPinDesigner:
    """Complete piston pin design from scratch."""
    
    def __init__(
        self,
        bore_mm: float,
        stroke_mm: float,
        max_gas_pressure_mpa: float,
        max_rpm: float,
        reciprocating_mass_kg: float,
        rod_length_mm: float,
        material_name: str = "Case Hardened Steel (8620)",
        pin_type: str = "full_floating",
    ):
        """
        Initialize piston pin designer.
        
        Parameters:
        -----------
        bore_mm : float
            Cylinder bore diameter (mm)
        stroke_mm : float
            Piston stroke (mm)
        max_gas_pressure_mpa : float
            Maximum combustion pressure (MPa)
        max_rpm : float
            Maximum engine speed (RPM)
        reciprocating_mass_kg : float
            Mass of piston assembly (kg)
        rod_length_mm : float
            Connecting rod length (mm)
        material_name : str
            Pin material
        pin_type : str
            'full_floating' or 'semi_floating'
        """
        self.bore_mm = bore_mm
        self.stroke_mm = stroke_mm
        self.max_rpm = max_rpm
        self.rod_length_mm = rod_length_mm
        
        # Material
        self.material = get_piston_pin_material(material_name)
        
        # Forces
        self.forces = PistonPinForces(
            bore_mm=bore_mm,
            max_gas_pressure_mpa=max_gas_pressure_mpa,
            reciprocating_mass_kg=reciprocating_mass_kg,
            max_rpm=max_rpm,
            stroke_mm=stroke_mm,
            rod_length_mm=rod_length_mm,
        )
        
        # Geometry
        self.geometry = PistonPinGeometry(
            bore_mm=bore_mm,
            pin_type=pin_type,
        )
        
        # Stress analysis
        self.stress = PistonPinStressAnalysis(
            geometry=self.geometry,
            forces=self.forces,
            material=self.material,
        )
        
        # Fatigue
        self.fatigue = PistonPinFatigue(
            material=self.material,
            bending_stress_mpa=self.stress.bending_stress_mpa,
            shear_stress_mpa=self.stress.shear_stress_mpa,
        )
        
        self.results = self._calculate_results()
    
    def _calculate_results(self) -> PistonPinResult:
        """Calculate all design results."""
        
        # Mass
        volume_m3 = self.geometry.area_m2 * (self.geometry.pin_length_mm / 1000)
        mass_kg = volume_m3 * self.material.density_kg_m3
        
        return PistonPinResult(
            outer_diameter_mm=self.geometry.outer_diameter_mm,
            inner_diameter_mm=self.geometry.inner_diameter_mm,
            pin_length_mm=self.geometry.pin_length_mm,
            hollowness_ratio=self.geometry.hollowness_ratio,
            weight_savings_percent=self.geometry.weight_savings_percent,
            piston_boss_length_mm=self.geometry.piston_boss_length_mm,
            rod_small_end_length_mm=self.geometry.rod_small_end_length_mm,
            max_gas_force_kN=self.forces.gas_force_kn,
            max_compressive_force_kN=self.forces.max_compressive_force_n / 1000,
            max_tensile_force_kN=self.forces.max_tensile_force_n / 1000,
            boss_bearing_pressure_mpa=self.stress.bearing_pressure_boss_mpa,
            rod_bearing_pressure_mpa=self.stress.bearing_pressure_rod_mpa,
            allowable_bearing_pressure_mpa=self.stress.allowable_bearing_pressure_mpa,
            bending_stress_mpa=self.stress.bending_stress_mpa,
            shear_stress_mpa=self.stress.shear_stress_mpa,
            von_mises_stress_mpa=self.stress.von_mises_stress_mpa,
            factor_of_safety=self.stress.factor_of_safety,
            bending_deflection_mm=self.stress.bending_deflection_mm,
            ovalization_mm=self.stress.ovalization_mm,
            total_deflection_mm=self.stress.total_deflection_mm,
            goodman_fos=self.fatigue.goodman_fos(),
            infinite_life=self.fatigue.infinite_life,
            material_name=self.material.name,
            material_description=self.material.description,
            surface_hardness_hb=self.material.hardness_surface_hb,
            case_depth_mm=self.material.case_depth_mm,
            pin_mass_g=mass_kg * 1000,
        )
    
    def get_results(self) -> PistonPinResult:
        return self.results
    
    def print_report(self):
        self.results.print_report()


# ============================================================================
# EXAMPLE USAGE
# ============================================================================

if __name__ == "__main__":
    # Test with typical 2.0L gasoline engine
    pin = PistonPinDesigner(
        bore_mm=85.0,
        stroke_mm=88.0,
        max_gas_pressure_mpa=8.0,
        max_rpm=6500,
        reciprocating_mass_kg=0.45,
        rod_length_mm=145.0,
        material_name="Case Hardened Steel (8620)",
    )
    pin.print_report()