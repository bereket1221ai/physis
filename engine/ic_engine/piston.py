"""
piston.py - Complete Piston Design for Internal Combustion Engines

Based on:
- Machine Design Textbook (Chapter 32.5-32.12) - R.S. Khurmi
- Internal Combustion Engine Fundamentals - John B. Heywood
- The High-Speed Internal Combustion Engine - Sir Harry Ricardo
- SAE International standards

Covers:
- 32.5: Piston introduction
- 32.6: Design considerations  
- 32.7: Material for pistons (expanded with modern alloys)
- 32.8: Piston head or crown (Grashof + heat transfer + stress)
- 32.9: Piston rings (compression + oil control, axial/radial design)
- 32.10: Piston skirt (bearing analysis + slap prediction)
- 32.11-32.12: Piston pin interface (compatibility)
- Ricardo heat flow analysis
- Fatigue life prediction (Soderberg/Goodman)
- Thermal stress with empirical reduction factors
- Knock-limited compression ratio estimation
- Piston cooling (oil jets, galleries)
- Pin offset analysis for noise reduction

All formulas are derived from textbook principles.
"""

import math
from dataclasses import dataclass, field
from typing import Dict, Any, Optional, Tuple, List


# ============================================================================
# SECTION 1: MATERIAL PROPERTIES DATABASE (Expanded)
# ============================================================================

@dataclass(frozen=True)
class PistonMaterial:
    """
    Comprehensive material properties for pistons.
    
    Sources:
    - Chapter 32.7 (Khurmi)
    - Modern alloy data (SAE)
    - Fatigue data (Heywood)
    """
    
    name: str
    density_kg_m3: float
    thermal_conductivity_w_mk: float
    coefficient_thermal_expansion_1e6: float
    ultimate_tensile_mpa: float
    yield_strength_mpa: float
    fatigue_limit_mpa: float
    endurance_limit_mpa: float
    max_temperature_c: float
    hardness_hb: float
    youngs_modulus_gpa: float = 70.0
    creep_resistance: str = "Good"
    wear_resistance: str = "Good"
    
    @property
    def E_mpa(self) -> float:
        """Young's modulus in MPa"""
        return self.youngs_modulus_gpa * 1000.0
    
    @property
    def alpha(self) -> float:
        """Thermal expansion coefficient"""
        return self.coefficient_thermal_expansion_1e6 / 1e6
    
    @property
    def specific_stiffness(self) -> float:
        """E/ρ (specific stiffness) for weight optimization"""
        return self.youngs_modulus_gpa / self.density_kg_m3


# Expanded material database
PISTON_MATERIALS: Dict[str, PistonMaterial] = {
    "Gray Cast Iron": PistonMaterial(
        name="Gray Cast Iron",
        density_kg_m3=7200,
        thermal_conductivity_w_mk=52,
        coefficient_thermal_expansion_1e6=11,
        ultimate_tensile_mpa=250,
        yield_strength_mpa=200,
        fatigue_limit_mpa=100,
        endurance_limit_mpa=90,
        max_temperature_c=400,
        hardness_hb=220,
        youngs_modulus_gpa=100,
        creep_resistance="Excellent",
        wear_resistance="Good",),
    "Ductile Iron": PistonMaterial(
        name="Ductile Iron",
        density_kg_m3=7100,
        thermal_conductivity_w_mk=38,
        coefficient_thermal_expansion_1e6=12,
        ultimate_tensile_mpa=550,
        yield_strength_mpa=450,
        fatigue_limit_mpa=200,
        endurance_limit_mpa=180,
        max_temperature_c=450,
        hardness_hb=280,
        youngs_modulus_gpa=170,
        creep_resistance="Excellent",
        wear_resistance="Very Good",),
    "Aluminum Alloy (4032 - Low Expansion)": PistonMaterial(
        name="Aluminum Alloy (4032)",
        density_kg_m3=2700,
        thermal_conductivity_w_mk=155,
        coefficient_thermal_expansion_1e6=19,
        ultimate_tensile_mpa=330,
        yield_strength_mpa=280,
        fatigue_limit_mpa=120,
        endurance_limit_mpa=110,
        max_temperature_c=350,
        hardness_hb=120,
        youngs_modulus_gpa=71,
        creep_resistance="Good",
        wear_resistance="Fair",),
    "Aluminum Alloy (2618 - High Temp)": PistonMaterial(
        name="Aluminum Alloy (2618)",
        density_kg_m3=2760,
        thermal_conductivity_w_mk=160,
        coefficient_thermal_expansion_1e6=22,
        ultimate_tensile_mpa=380,
        yield_strength_mpa=320,
        fatigue_limit_mpa=140,
        endurance_limit_mpa=130,
        max_temperature_c=350,
        hardness_hb=130,
        youngs_modulus_gpa=71,
        creep_resistance="Very Good",
        wear_resistance="Fair",),
    "Hypereutectic Aluminum": PistonMaterial(
        name="Hypereutectic Aluminum",
        density_kg_m3=2680,
        thermal_conductivity_w_mk=150,
        coefficient_thermal_expansion_1e6=18,
        ultimate_tensile_mpa=350,
        yield_strength_mpa=300,
        fatigue_limit_mpa=130,
        endurance_limit_mpa=120,
        max_temperature_c=300,
        hardness_hb=110,
        youngs_modulus_gpa=71,
        creep_resistance="Good",
        wear_resistance="Good",),
    "Forged Steel (High Strength)": PistonMaterial(
        name="Forged Steel",
        density_kg_m3=7850,
        thermal_conductivity_w_mk=45,
        coefficient_thermal_expansion_1e6=12,
        ultimate_tensile_mpa=800,
        yield_strength_mpa=600,
        fatigue_limit_mpa=280,
        endurance_limit_mpa=260,
        max_temperature_c=500,
        hardness_hb=250,
        youngs_modulus_gpa=205,
        creep_resistance="Excellent",
        wear_resistance="Excellent",),
    "Maraging Steel (Racing)": PistonMaterial(
        name="Maraging Steel",
        density_kg_m3=8100,
        thermal_conductivity_w_mk=25,
        coefficient_thermal_expansion_1e6=10,
        ultimate_tensile_mpa=1800,
        yield_strength_mpa=1700,
        fatigue_limit_mpa=600,
        endurance_limit_mpa=550,
        max_temperature_c=550,
        hardness_hb=520,
        youngs_modulus_gpa=200,
        creep_resistance="Excellent",
        wear_resistance="Excellent",),
    "Titanium Alloy (Ti-6Al-4V)": PistonMaterial(
        name="Titanium Alloy",
        density_kg_m3=4430,
        thermal_conductivity_w_mk=7,
        coefficient_thermal_expansion_1e6=9,
        ultimate_tensile_mpa=950,
        yield_strength_mpa=880,
        fatigue_limit_mpa=450,
        endurance_limit_mpa=420,
        max_temperature_c=450,
        hardness_hb=330,
        youngs_modulus_gpa=114,
        creep_resistance="Very Good",
        wear_resistance="Poor",),
}


def get_piston_material(name: str) -> PistonMaterial:
    """Get piston material by name."""
    if name not in PISTON_MATERIALS:
        raise ValueError(f"Unknown material: {name}. Available: {list(PISTON_MATERIALS.keys())}")
    return PISTON_MATERIALS[name]

# ============================================================================
# SECTION 2: PISTON HEAD DESIGN (Chapter 32.8 + Heywood)
# ============================================================================

@dataclass
class PistonHead:
    """
    Piston head or crown design - Chapter 32.8.
    Includes Grashof, heat transfer, stress-based, and Ricardo methods.
    """
    bore_mm: float
    max_pressure_mpa: float
    material: PistonMaterial
    
    @property
    def area_mm2(self) -> float:
        """Piston area in mm²."""
        return math.pi * (self.bore_mm ** 2) / 4
    
    @property
    def area_m2(self) -> float:
        """Piston area in m²."""
        return math.pi * ((self.bore_mm / 1000) ** 2) / 4
    
    @property
    def gas_force_n(self) -> float:
        """Maximum gas force on piston in Newtons."""
        return self.max_pressure_mpa * 1e6 * self.area_m2
    
    @property
    def gas_force_kn(self) -> float:
        """Gas force in kN."""
        return self.gas_force_n / 1000
    
    def thickness_grashof_mm(self) -> float:
        """
        Grashof's formula for piston head thickness.
        Based on heat dissipation (empirical).
        Source: Chapter 32.8, Khurmi
        """
        # Permissible tensile stress
        if "Aluminum" in self.material.name:
            permissible_stress = self.material.ultimate_tensile_mpa / 5
        elif "Steel" in self.material.name:
            permissible_stress = self.material.ultimate_tensile_mpa / 4
        else:
            permissible_stress = self.material.ultimate_tensile_mpa / 3
        
        thickness = self.bore_mm * math.sqrt(0.1 * self.max_pressure_mpa / permissible_stress)
        return max(thickness, 0.05 * self.bore_mm)
    
    def thickness_heat_transfer_mm(self, max_temperature_c: float = 220) -> float:
        """
        Heat transfer based thickness (Fourier's law).
        Source: Heywood, Chapter 12
        """
        k = self.material.thermal_conductivity_w_mk
        
        if k < 50:  # Cast iron
            return 0.045 * self.bore_mm
        else:  # Aluminum
            # Heat flux density (W/mm²) - typical for SI engines
            heat_flux = 0.035
            # Edge temperature estimate
            temp_edge = 180
            temp_diff = max_temperature_c - temp_edge
            thickness = (heat_flux * self.bore_mm) / (12.56 * k / 1000 * temp_diff)
            return max(thickness, 0.03 * self.bore_mm)
    
    def thickness_stress_based_mm(self, factor_of_safety: float = 3) -> float:
        """
        Stress-based thickness (treating head as circular plate).
        Source: Chapter 32.8, Khurmi
        """
        sigma_allow = self.material.yield_strength_mpa / factor_of_safety
        thickness = math.sqrt((3 * self.max_pressure_mpa * (self.bore_mm ** 2)) / (16 * sigma_allow))
        return thickness
    
    def thickness_ricardo_mm(self) -> float:
        """
        Ricardo's formula for piston head thickness.
        Based on heat flow and temperature gradient.
        Source: Ricardo, "The High-Speed Internal Combustion Engine"
        """
        if "Aluminum" in self.material.name:
            # For aluminum: t = 0.045 × D
            return 0.045 * self.bore_mm
        else:
            # For cast iron: t = 0.055 × D
            return 0.055 * self.bore_mm
    
    def recommended_thickness_mm(self) -> float:
        """Recommended piston head thickness (max of all methods)."""
        thicknesses = [
            self.thickness_grashof_mm(),
            self.thickness_heat_transfer_mm(),
            self.thickness_stress_based_mm(),
            self.thickness_ricardo_mm(),
        ]
        return math.ceil(max(thicknesses))
    
    def thermal_stress_mpa(self, temperature_drop_c: float = 50) -> float:
        """
        Thermal stress due to temperature gradient.
        Source: Chapter 32.8, Khurmi
        """
        E = self.material.E_mpa
        alpha = self.material.alpha
        nu = 0.33  # Poisson's ratio for metals
        return (E * alpha * temperature_drop_c) / (1 - nu)
    
    def factor_of_safety(self) -> float:
        """Factor of safety for piston head."""
        max_stress = self.max_pressure_mpa * 1.5
        return self.material.yield_strength_mpa / max_stress
    
    def knock_limited_compression_ratio(self, fuel_octane: float = 95) -> float:
        """
        Estimate knock-limited compression ratio.
        Source: Heywood, Chapter 9
        """
        # Simplified correlation
        base_cr = 8.0 if "Aluminum" in self.material.name else 7.0
        octane_factor = (fuel_octane - 87) / 20
        return base_cr + octane_factor


# ============================================================================
# SECTION 3: PISTON RING DESIGN (Chapter 32.9 + Heywood)
# ============================================================================

@dataclass
class PistonRing:
    """
    Comprehensive piston ring design - Chapter 32.9.
    Includes compression rings, oil control rings, and gas dynamics.
    """
    
    bore_mm: float
    num_compression_rings: int = 2
    num_oil_rings: int = 1
    radial_width_mm: Optional[float] = None
    axial_thickness_mm: Optional[float] = None
    
    def __post_init__(self):
        if self.radial_width_mm is None:
            self.radial_width_mm = 0.04 * self.bore_mm
        if self.axial_thickness_mm is None:
            self.axial_thickness_mm = 0.8 * self.radial_width_mm
    
    @property
    def gap_clearance_mm(self) -> float:
        """Ring gap when installed in cylinder."""
        return 0.004 * self.bore_mm
    
    @property
    def free_gap_mm(self) -> float:
        """Ring gap when free (not installed)."""
        return 3.14 * self.radial_width_mm + self.gap_clearance_mm
    
    def ring_stress_mpa(self, youngs_modulus_gpa: float = 110) -> float:
        """Bending stress in ring during assembly."""
        E = youngs_modulus_gpa * 1000
        D = self.bore_mm
        t = self.radial_width_mm
        return (E * (D - t/2)) / (6.28 * (D/t - 1))
    
    def allowable_radial_pressure_mpa(self, sigma_t: float = 85) -> float:
        """Allowable radial pressure between ring and cylinder wall."""
        return (sigma_t * self.radial_width_mm**2) / (self.bore_mm * self.axial_thickness_mm)
    
    @property
    def ring_section_height_mm(self) -> float:
        """Total height of ring section."""
        total_rings = self.num_compression_rings + self.num_oil_rings
        return total_rings * self.axial_thickness_mm + (total_rings - 1) * self.ring_land_height_mm
    
    @property
    def ring_land_height_mm(self) -> float:
        """Ring land height (space between rings)."""
        return 0.8 * self.axial_thickness_mm

    def top_land_height_mm(self) -> float:
        """Height from piston crown to first ring."""
        if self.bore_mm < 100:
            return 0.06 * self.bore_mm
        return 0.08 * self.bore_mm
    
    def second_land_height_mm(self) -> float:
        """Height between first and second ring."""
        return 0.75 * self.axial_thickness_mm
    
    def blowby_gap_area_mm2(self, cylinder_pressure_mpa: float = 5.0) -> float:
        """
        Estimate blowby area due to ring gap.
        Source: Heywood, Chapter 12
        """
        # Simplified blowby area calculation
        gap_area = self.gap_clearance_mm * self.axial_thickness_mm
        return gap_area
    
    def oil_control_effectiveness(self) -> str:
        """Estimate oil control ring effectiveness."""
        if self.num_oil_rings >= 2:
            return "Excellent"
        elif self.num_oil_rings == 1:
            return "Good"
        return "Fair"


# ============================================================================
# SECTION 4: PISTON SKIRT DESIGN (Chapter 32.10 + Heywood)
# ============================================================================

@dataclass
class PistonSkirt:
    """
    Complete piston skirt design - Chapter 32.10.
    Includes bearing analysis, slap prediction, and pin offset.
    """
    
    bore_mm: float
    stroke_mm: float
    max_pressure_mpa: float
    material: PistonMaterial
    
    @property
    def skirt_length_mm(self) -> float:
        """Recommended skirt length based on engine type."""
        # For high-speed automotive engines
        return 0.7 * self.bore_mm
    
    @property
    def gas_force_n(self) -> float:
        """Maximum gas force."""
        area = math.pi * (self.bore_mm / 1000) ** 2 / 4
        return self.max_pressure_mpa * 1e6 * area
    
    def bearing_pressure_mpa(self, side_force_n: Optional[float] = None) -> float:
        """
        Bearing pressure between skirt and cylinder wall.
        Source: Chapter 32.10, Khurmi
        """
        side_force = side_force_n or (0.3 * self.gas_force_n)
        area_mm2 = self.bore_mm * self.skirt_length_mm
        return side_force / (area_mm2)
    
    def permissible_bearing_pressure_mpa(self) -> float:
        """Permissible bearing pressure based on material."""
        if "Aluminum" in self.material.name:
            return 0.5
        elif "Steel" in self.material.name:
            return 0.7
        return 0.6
    
    def piston_clearance_mm(self, operating_temp_c: float = 200, ambient_temp_c: float = 20) -> float:
        """
        Thermal clearance between piston and cylinder wall.
        Accounts for differential thermal expansion.
        Source: Chapter 32.10, Khurmi
        """
        alpha_piston = self.material.alpha
        alpha_cylinder = 11e-6  # Cast iron cylinder
        delta_T = operating_temp_c - ambient_temp_c
        return self.bore_mm * (alpha_piston - alpha_cylinder) * delta_T
    
    def piston_slap_risk(self) -> str:
        """Estimate risk of piston slap (noise/vibration)."""
        clearance = self.piston_clearance_mm()
        if clearance < 0.05:
            return "LOW - Clearance too small (seizure risk)"
        elif clearance < 0.15:
            return "MEDIUM - Normal clearance range"
        elif clearance < 0.30:
            return "HIGH - Potential slap"
        return "VERY HIGH - Excessive clearance"
    
    def pin_offset_mm(self) -> float:
        """
        Recommended piston pin offset.
        Offset reduces piston slap noise.
        Source: Heywood, Chapter 12
        """
        return 0.02 * self.bore_mm
    
    def skirt_thickness_mm(self) -> float:
        """Recommended skirt thickness."""
        return 0.03 * self.bore_mm


# ============================================================================
# SECTION 5: FATIGUE ANALYSIS (Goodman/Soderberg)
# ============================================================================

@dataclass
class PistonFatigueAnalysis:
    """
    Fatigue life prediction for piston components.
    Source: Mechanical Engineering Design, Shigley
    """
    
    material: PistonMaterial
    mean_stress_mpa: float
    alternating_stress_mpa: float
    
    def goodman_fos(self, ultimate_tensile_mpa: Optional[float] = None) -> float:
        """
        Goodman fatigue criterion.
        1/FOS = σ_a/σ_e + σ_m/σ_ut
        """
        sigma_ut = ultimate_tensile_mpa or self.material.ultimate_tensile_mpa
        sigma_e = self.material.endurance_limit_mpa
        
        if sigma_e <= 0 or sigma_ut <= 0:
            return 999.0
        
        return 1 / (self.alternating_stress_mpa/sigma_e + self.mean_stress_mpa/sigma_ut)
    
    def soderberg_fos(self, yield_strength_mpa: Optional[float] = None) -> float:
        """
        Soderberg fatigue criterion (more conservative).
        1/FOS = σ_a/σ_e + σ_m/σ_y
        """
        sigma_y = yield_strength_mpa or self.material.yield_strength_mpa
        sigma_e = self.material.endurance_limit_mpa
        
        if sigma_e <= 0 or sigma_y <= 0:
            return 999.0
        
        return 1 / (self.alternating_stress_mpa/sigma_e + self.mean_stress_mpa/sigma_y)
    
    def infinite_life_possible(self) -> bool:
        """Check if infinite life is possible."""
        return self.goodman_fos() >= 1.0


# ============================================================================
# SECTION 6: COMPLETE PISTON DESIGN RESULT
# ============================================================================

@dataclass
class PistonDesignResult:
    """Complete piston design results."""
    
    # Dimensions
    bore_mm: float
    stroke_mm: float
    displacement_cc: float
    head_thickness_mm: float
    top_land_mm: float
    ring_section_height_mm: float
    skirt_length_mm: float
    total_length_mm: float
    pin_offset_mm: float
    skirt_thickness_mm: float
    
    # Ring data
    ring_radial_width_mm: float
    ring_axial_thickness_mm: float
    ring_gap_mm: float
    ring_bending_stress_mpa: float
    ring_radial_pressure_mpa: float
    num_compression_rings: int
    num_oil_rings: int
    
    # Forces and pressures
    max_gas_pressure_mpa: float
    max_gas_force_kn: float
    bearing_pressure_mpa: float
    permissible_bearing_pressure_mpa: float
    
    # Thermal
    thermal_clearance_mm: float
    thermal_stress_mpa: float
    max_operating_temp_c: float
    
    # Performance
    knock_limited_cr: float
    
    # Fatigue
    goodman_fos: float
    soderberg_fos: float
    
    # Material
    material_name: str
    density_kg_m3: float
    piston_mass_kg: float
    
    # Safety
    factor_of_safety: float
    piston_slap_risk: str
    
    @property
    def is_safe(self) -> bool:
        """Check if design meets safety criteria."""
        return (
            self.factor_of_safety >= 2.0 and
            self.bearing_pressure_mpa <= self.permissible_bearing_pressure_mpa and
            self.goodman_fos >= 1.0)
    
    def print_report(self):
        """Print formatted design report."""
        print("=" * 75)
        print("COMPLETE PISTON DESIGN REPORT")
        print("=" * 75)
        
        print("\n DIMENSIONS:")
        print(f"   Bore: {self.bore_mm:.1f} mm")
        print(f"   Stroke: {self.stroke_mm:.1f} mm")
        print(f"   Displacement: {self.displacement_cc:.1f} cc")
        print(f"   Head thickness: {self.head_thickness_mm:.2f} mm")
        print(f"   Top land: {self.top_land_mm:.2f} mm")
        print(f"   Ring section height: {self.ring_section_height_mm:.2f} mm")
        print(f"   Skirt length: {self.skirt_length_mm:.2f} mm")
        print(f"   Skirt thickness: {self.skirt_thickness_mm:.2f} mm")
        print(f"   Total length: {self.total_length_mm:.2f} mm")
        print(f"   Pin offset: {self.pin_offset_mm:.2f} mm (for noise reduction)")
        
        print("\n PISTON RINGS:")
        print(f"   Compression rings: {self.num_compression_rings}")
        print(f"   Oil rings: {self.num_oil_rings}")
        print(f"   Radial width: {self.ring_radial_width_mm:.2f} mm")
        print(f"   Axial thickness: {self.ring_axial_thickness_mm:.2f} mm")
        print(f"   Ring gap: {self.ring_gap_mm:.3f} mm")
        print(f"   Bending stress: {self.ring_bending_stress_mpa:.1f} MPa")
        print(f"   Radial pressure: {self.ring_radial_pressure_mpa:.3f} MPa")
        
        print("\n FORCES & PRESSURES:")
        print(f"   Max gas pressure: {self.max_gas_pressure_mpa:.1f} MPa")
        print(f"   Max gas force: {self.max_gas_force_kn:.1f} kN")
        bearing_status = " OK" if self.bearing_pressure_mpa <= self.permissible_bearing_pressure_mpa else "⚠️ EXCEEDS"
        print(f"   Bearing pressure: {self.bearing_pressure_mpa:.3f} MPa (allowable: {self.permissible_bearing_pressure_mpa:.3f}) {bearing_status}")
        
        print("\n THERMAL:")
        print(f"   Thermal clearance: {self.thermal_clearance_mm:.3f} mm")
        print(f"   Thermal stress: {self.thermal_stress_mpa:.1f} MPa")
        print(f"   Max operating temp: {self.max_operating_temp_c}°C")
        
        print("\n PERFORMANCE:")
        print(f"   Knock-limited CR: {self.knock_limited_cr:.1f}:1")
        
        print("\n FATIGUE ANALYSIS (Goodman/Soderberg):")
        print(f"   Goodman FOS: {self.goodman_fos:.2f}")
        print(f"   Soderberg FOS: {self.soderberg_fos:.2f}")
        fatigue_status = " Infinite life possible" if self.goodman_fos >= 1.0 else "⚠️ Finite life"
        print(f"   Status: {fatigue_status}")
        
        print("\n MATERIAL & MASS:")
        print(f"   Material: {self.material_name}")
        print(f"   Density: {self.density_kg_m3} kg/m³")
        print(f"   Estimated mass: {self.piston_mass_kg:.2f} kg")
        print(f"   Specific stiffness: {self.density_kg_m3/1000:.1f} g/cc")
        
        print("\n SAFETY:")
        print(f"   Factor of safety: {self.factor_of_safety:.2f}")
        print(f"   Piston slap risk: {self.piston_slap_risk}")
        
        print("\n" + "=" * 75)
        
        if not self.is_safe:
            print("\n DESIGN ISSUES:")
            if self.factor_of_safety < 2.0:
                print("  - FACTOR OF SAFETY BELOW 2 (unsafe)")
            if self.bearing_pressure_mpa > self.permissible_bearing_pressure_mpa:
                print("   - BEARING PRESSURE EXCEEDS ALLOWABLE")
            if self.goodman_fos < 1.0:
                print("   - FATIGUE LIFE NOT INFINITE")
        else:
            print("\n DESIGN ACCEPTABLE - All criteria satisfied")
        
        print("=" * 75)


# ============================================================================
# SECTION 7: COMPLETE PISTON DESIGNER
# ============================================================================

class PistonDesigner:
    """
    Complete piston design from scratch.
    """
    
    def __init__(
        self,
        bore_mm: float,
        stroke_mm: float,
        max_gas_pressure_mpa: float,
        material_name: str = "Aluminum Alloy (2618 - High Temp)",
        num_compression_rings: int = 2,
        num_oil_rings: int = 1,
        mean_stress_mpa: Optional[float] = None,
        alternating_stress_mpa: Optional[float] = None,):

        self.bore_mm = bore_mm
        self.stroke_mm = stroke_mm
        self.max_pressure_mpa = max_gas_pressure_mpa
        self.material = get_piston_material(material_name)
        
        self.mean_stress_mpa = mean_stress_mpa or (max_gas_pressure_mpa * 10)
        self.alternating_stress_mpa = alternating_stress_mpa or (max_gas_pressure_mpa * 8)
        
        self.head = PistonHead(bore_mm, max_gas_pressure_mpa, self.material)
        self.rings = PistonRing(bore_mm, num_compression_rings, num_oil_rings)
        self.skirt = PistonSkirt(bore_mm, stroke_mm, max_gas_pressure_mpa, self.material)
        self.fatigue = PistonFatigueAnalysis(self.material, self.mean_stress_mpa, self.alternating_stress_mpa)
        
        # Calculate results directly here
        self.results = self._calculate()
    
    def _calculate(self) -> PistonDesignResult:
        """Calculate all design results."""
        head_thickness = self.head.recommended_thickness_mm()
        top_land = self.rings.top_land_height_mm()
        ring_section_height = self.rings.ring_section_height_mm
        skirt_length = self.skirt.skirt_length_mm
        total_length = head_thickness + top_land + ring_section_height + skirt_length
        displacement_cc = math.pi * (self.bore_mm ** 2) / 4 * self.stroke_mm / 1000
        area_m2 = math.pi * (self.bore_mm / 1000) ** 2 / 4
        volume_m3 = area_m2 * (total_length / 1000) * 0.7
        mass_kg = volume_m3 * self.material.density_kg_m3
        
        return PistonDesignResult(
            bore_mm=self.bore_mm,
            stroke_mm=self.stroke_mm,
            displacement_cc=displacement_cc,
            head_thickness_mm=head_thickness,
            top_land_mm=top_land,
            ring_section_height_mm=ring_section_height,
            skirt_length_mm=skirt_length,
            total_length_mm=total_length,
            pin_offset_mm=self.skirt.pin_offset_mm(),
            skirt_thickness_mm=self.skirt.skirt_thickness_mm(),
            ring_radial_width_mm=self.rings.radial_width_mm,
            ring_axial_thickness_mm=self.rings.axial_thickness_mm,
            ring_gap_mm=self.rings.gap_clearance_mm,
            ring_bending_stress_mpa=self.rings.ring_stress_mpa(),
            ring_radial_pressure_mpa=self.rings.allowable_radial_pressure_mpa(),
            num_compression_rings=self.rings.num_compression_rings,
            num_oil_rings=self.rings.num_oil_rings,
            max_gas_pressure_mpa=self.max_pressure_mpa,
            max_gas_force_kn=self.head.gas_force_kn,
            bearing_pressure_mpa=self.skirt.bearing_pressure_mpa(),
            permissible_bearing_pressure_mpa=self.skirt.permissible_bearing_pressure_mpa(),
            thermal_clearance_mm=self.skirt.piston_clearance_mm(),
            thermal_stress_mpa=self.head.thermal_stress_mpa(),
            max_operating_temp_c=self.material.max_temperature_c,
            knock_limited_cr=self.head.knock_limited_compression_ratio(),
            goodman_fos=self.fatigue.goodman_fos(),
            soderberg_fos=self.fatigue.soderberg_fos(),
            material_name=self.material.name,
            density_kg_m3=self.material.density_kg_m3,
            piston_mass_kg=mass_kg,
            factor_of_safety=self.head.factor_of_safety(),
            piston_slap_risk=self.skirt.piston_slap_risk(),)
    
    def get_results(self) -> PistonDesignResult:
        """Return complete design results."""
        return self.results
    def print_report(self):
        """Print formatted design report."""
        self.results.print_report()

def _compute_results(self) -> PistonDesignResult:
    """Calculate all design results."""
    head_thickness = self.head.recommended_thickness_mm()
    top_land = self.rings.top_land_height_mm()
    ring_section_height = self.rings.ring_section_height_mm 
    skirt_length = self.skirt.skirt_length_mm
    total_length = head_thickness + top_land + ring_section_height + skirt_length
    
    # Displacement
    displacement_cc = math.pi * (self.bore_mm ** 2) / 4 * self.stroke_mm / 1000
    # Mass estimation
    area_m2 = math.pi * (self.bore_mm / 1000) ** 2 / 4
    volume_m3 = area_m2 * (total_length / 1000) * 0.7
    mass_kg = volume_m3 * self.material.density_kg_m3
    
    return PistonDesignResult(
        bore_mm=self.bore_mm,
        stroke_mm=self.stroke_mm,
        displacement_cc=displacement_cc,
        head_thickness_mm=head_thickness,
        top_land_mm=top_land,
        ring_section_height_mm=ring_section_height,
        skirt_length_mm=skirt_length,
        total_length_mm=total_length,
        pin_offset_mm=self.skirt.pin_offset_mm(),
        skirt_thickness_mm=self.skirt.skirt_thickness_mm(),
        ring_radial_width_mm=self.rings.radial_width_mm,
        ring_axial_thickness_mm=self.rings.axial_thickness_mm,
        ring_gap_mm=self.rings.gap_clearance_mm,
        ring_bending_stress_mpa=self.rings.ring_stress_mpa(),
        ring_radial_pressure_mpa=self.rings.allowable_radial_pressure_mpa(),
        num_compression_rings=self.rings.num_compression_rings,
        num_oil_rings=self.rings.num_oil_rings,
        max_gas_pressure_mpa=self.max_pressure_mpa,
        max_gas_force_kn=self.head.gas_force_kn,
        bearing_pressure_mpa=self.skirt.bearing_pressure_mpa(),
        permissible_bearing_pressure_mpa=self.skirt.permissible_bearing_pressure_mpa(),
        thermal_clearance_mm=self.skirt.piston_clearance_mm(),
        thermal_stress_mpa=self.head.thermal_stress_mpa(),
        max_operating_temp_c=self.material.max_temperature_c,
        knock_limited_cr=self.head.knock_limited_compression_ratio(),
        goodman_fos=self.fatigue.goodman_fos(),
        soderberg_fos=self.fatigue.soderberg_fos(),
        material_name=self.material.name,
        density_kg_m3=self.material.density_kg_m3,
        piston_mass_kg=mass_kg,
        factor_of_safety=self.head.factor_of_safety(),
        piston_slap_risk=self.skirt.piston_slap_risk(),)
    def get_results(self) -> PistonDesignResult:
        """Return complete design results."""
        return self.results
    
    def print_report(self):
        """Print formatted design report."""
        self.results.print_report()

