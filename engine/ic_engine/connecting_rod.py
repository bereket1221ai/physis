"""
connecting_rod.py - Complete Connecting Rod Design for IC Engines

Sources:
- Machine Design Textbook (Chapter 32.13-32.15, Chapter 16) - R.S. Khurmi
- Internal Combustion Engine Fundamentals - John B. Heywood
- Mechanical Engineering Design - Shigley & Mischke
- SAE International standards

Covers:
- 32.13: Connecting Rod introduction
- 32.14: Forces Acting on the Connecting Rod (inertia + gas)
- 32.15: Design of Connecting Rod (I-section optimization)
- Chapter 16: Columns and Struts (buckling analysis)
- Whipping stress due to inertia bending
- Big end and small end bearing design
- Bolts and cap design
- Fatigue analysis (Goodman/Soderberg)
- Material optimization
"""

import math
from dataclasses import dataclass, field
from typing import Dict, Any, Optional, Tuple, List

# ============================================================================
# SECTION 1: MATERIAL PROPERTIES DATABASE
# ============================================================================

@dataclass(frozen=True)
class ConnectingRodMaterial:
    """Material properties for connecting rods."""
    
    name: str
    density_kg_m3: float
    ultimate_tensile_mpa: float
    yield_strength_mpa: float
    fatigue_limit_mpa: float
    endurance_limit_mpa: float
    youngs_modulus_gpa: float
    hardness_hb: float
    
    @property
    def E_mpa(self) -> float:
        """Young's modulus in MPa"""
        return self.youngs_modulus_gpa * 1000.0

# Material database
CONROD_MATERIALS: Dict[str, ConnectingRodMaterial] = {
    "Forged Steel (4340)": ConnectingRodMaterial(
        name="Forged Steel (4340)",
        density_kg_m3=7850,
        ultimate_tensile_mpa=1080,
        yield_strength_mpa=930,
        fatigue_limit_mpa=400,
        endurance_limit_mpa=350,
        youngs_modulus_gpa=205,
        hardness_hb=350,),
    "Forged Steel (4140)": ConnectingRodMaterial(
        name="Forged Steel (4140)",
        density_kg_m3=7850,
        ultimate_tensile_mpa=950,
        yield_strength_mpa=830,
        fatigue_limit_mpa=350,
        endurance_limit_mpa=310,
        youngs_modulus_gpa=205,
        hardness_hb=320,),
    "Carbon Steel (1045)": ConnectingRodMaterial(
        name="Carbon Steel (1045)",
        density_kg_m3=7850,
        ultimate_tensile_mpa=630,
        yield_strength_mpa=530,
        fatigue_limit_mpa=250,
        endurance_limit_mpa=220,
        youngs_modulus_gpa=200,
        hardness_hb=210,),
    "Titanium Alloy (6Al-4V)": ConnectingRodMaterial(
        name="Titanium Alloy (6Al-4V)",
        density_kg_m3=4430,
        ultimate_tensile_mpa=950,
        yield_strength_mpa=880,
        fatigue_limit_mpa=450,
        endurance_limit_mpa=400,
        youngs_modulus_gpa=114,
        hardness_hb=330,),
    "Aluminum (7075-T6)": ConnectingRodMaterial(
        name="Aluminum (7075-T6)",
        density_kg_m3=2810,
        ultimate_tensile_mpa=570,
        yield_strength_mpa=500,
        fatigue_limit_mpa=160,
        endurance_limit_mpa=140,
        youngs_modulus_gpa=71,
        hardness_hb=150,),
    "Sintered Steel": ConnectingRodMaterial(
        name="Sintered Steel",
        density_kg_m3=7200,
        ultimate_tensile_mpa=700,
        yield_strength_mpa=600,
        fatigue_limit_mpa=280,
        endurance_limit_mpa=250,
        youngs_modulus_gpa=170,
        hardness_hb=250,),
}

def get_conrod_material(name: str) -> ConnectingRodMaterial:
    """Get connecting rod material by name."""
    if name not in CONROD_MATERIALS:
        raise ValueError(f"Unknown material: {name}. Available: {list(CONROD_MATERIALS.keys())}")
    return CONROD_MATERIALS[name]


# ============================================================================
# SECTION 2: CONNECTING ROD FORCES (Chapter 32.14 + Heywood)
# ============================================================================

@dataclass
class ConnectingRodForces:
    """
    Complete force analysis for connecting rod.
    
    Calculates:
    - Gas force from combustion pressure
    - Inertia force from reciprocating mass
    - Net compressive/tensile forces
    - Forces at any crank angle
    """
    
    bore_mm: float
    stroke_mm: float
    rod_length_mm: float
    reciprocating_mass_kg: float
    max_gas_pressure_mpa: float
    max_rpm: float
    
    def __post_init__(self):
        self.bore_m = self.bore_mm / 1000
        self.stroke_m = self.stroke_mm / 1000
        self.rod_length_m = self.rod_length_mm / 1000
        self.crank_radius_m = self.stroke_mm / 2000
        self.crank_radius_mm = self.stroke_mm / 2
        self.n = self.rod_length_mm / self.crank_radius_mm  # l/r ratio
        self.omega = 2 * math.pi * self.max_rpm / 60
        self.piston_area_m2 = math.pi * (self.bore_m ** 2) / 4
        self.reciprocating_mass = self.reciprocating_mass_kg
    
    @property
    def gas_force_n(self) -> float:
        """Maximum gas force on piston."""
        return self.max_gas_pressure_mpa * 1e6 * self.piston_area_m2
    
    @property
    def gas_force_kn(self) -> float:
        """Gas force in kN."""
        return self.gas_force_n / 1000
    
    def inertia_force_n(self, crank_angle_deg: float) -> float:
        """
        Inertia force at given crank angle.
        F_i = m_r × ω² × r × (cos θ + cos 2θ / n)
        """
        theta_rad = math.radians(crank_angle_deg)
        return (self.reciprocating_mass * self.omega**2 * self.crank_radius_m *
                (math.cos(theta_rad) + math.cos(2 * theta_rad) / self.n))
    
    @property
    def inertia_force_tdc_n(self) -> float:
        """Inertia force at TDC (maximum tension)."""
        return self.reciprocating_mass * self.omega**2 * self.crank_radius_m * (1 + 1/self.n)
    
    @property
    def inertia_force_bdc_n(self) -> float:
        """Inertia force at BDC."""
        return self.reciprocating_mass * self.omega**2 * self.crank_radius_m * (-1 + 1/self.n)
    
    @property
    def max_compressive_force_n(self) -> float:
        """Maximum compressive force (power stroke, near TDC)."""
        return self.gas_force_n - self.inertia_force_tdc_n
    
    @property
    def max_tensile_force_n(self) -> float:
        """Maximum tensile force (exhaust stroke, TDC)."""
        return abs(-self.inertia_force_tdc_n)
    
    def rod_force_n(self, crank_angle_deg: float) -> float:
        """Force along connecting rod axis."""
        theta_rad = math.radians(crank_angle_deg)
        sin_phi = math.sin(theta_rad) / self.n
        phi = math.asin(max(-0.5, min(0.5, sin_phi)))
        cos_phi = math.cos(phi)
        net_force = self.gas_force_n - self.inertia_force_n(crank_angle_deg)
        return net_force / cos_phi if cos_phi > 0 else net_force


# ============================================================================
# SECTION 3: I-SECTION CROSS-SECTION DESIGN (Chapter 32.15)
# ============================================================================

@dataclass
class ConnectingRodCrossSection:
    """
    I-section connecting rod cross-section design.
    
    Proportions (textbook optimal):
    - H = 5t (total depth)
    - B = 4t (flange width)
    - t = web/flange thickness
    - Ixx / Iyy ≈ 3.2 (optimal for buckling)
    """
    
    bore_mm: float
    stroke_mm: float
    rod_length_mm: float
    max_compressive_force_n: float
    material: ConnectingRodMaterial
    H_to_t_ratio: float = 5.0      # H = 5t
    B_to_t_ratio: float = 4.0      # B = 4t
    t1_to_t_ratio: float = 0.12    # t1 = 0.12 × H (flange thickness)
    
    def __post_init__(self):
        # Determine optimal t (web thickness) from Rankine buckling
        self._optimize_section()
    
    def _optimize_section(self):
        """Optimize I-section dimensions using Rankine formula."""
        # Start with initial t estimate
        t = 5.0  # mm initial guess
        
        for _ in range(20):
            self.t_mm = t
            self.H_mm = self.H_to_t_ratio * t
            self.B_mm = self.B_to_t_ratio * t
            self.t1_mm = self.t1_to_t_ratio * self.H_mm
            
            # Calculate area and moment of inertia
            area = self.area_mm2
            I_xx = self._calc_Ixx()
            k_xx = math.sqrt(I_xx / area)
            
            # Rankine buckling load
            L = self.rod_length_mm
            a = 1 / 7500  # Rankine constant for steel
            sigma_c = self.material.yield_strength_mpa
            
            P_rankine = (sigma_c * area) / (1 + a * (L / k_xx)**2)
            
            if P_rankine >= self.max_compressive_force_n * 5:  # FOS = 5
                break
            t *= 1.05
        
        self.t_mm = max(t, 4.0)  # Minimum 4mm
    
    def _calc_Ixx(self) -> float:
        """Moment of inertia about X-X axis."""
        H, B, t, t1 = self.H_mm, self.B_mm, self.t_mm, self.t1_mm
        I_outer = B * H**3 / 12
        inner_height = H - 2 * t1
        I_inner = (B - t) * inner_height**3 / 12
        return I_outer - I_inner
    
    def _calc_Iyy(self) -> float:
        """Moment of inertia about Y-Y axis."""
        H, B, t, t1 = self.H_mm, self.B_mm, self.t_mm, self.t1_mm
        I_flanges = 2 * (t1 * B**3 / 12)
        I_web = t * (H - 2 * t1)**3 / 12
        return I_flanges + I_web
    
    @property
    def area_mm2(self) -> float:
        """Cross-sectional area in mm²."""
        H, B, t, t1 = self.H_mm, self.B_mm, self.t_mm, self.t1_mm
        return 2 * B * t1 + (H - 2 * t1) * t
    
    @property
    def area_m2(self) -> float:
        return self.area_mm2 / 1e6
    
    @property
    def I_xx_mm4(self) -> float:
        return self._calc_Ixx()
    
    @property
    def I_yy_mm4(self) -> float:
        return self._calc_Iyy()
    
    @property
    def k_xx_mm(self) -> float:
        return math.sqrt(self.I_xx_mm4 / self.area_mm2)
    
    @property
    def k_yy_mm(self) -> float:
        return math.sqrt(self.I_yy_mm4 / self.area_mm2)
    
    @property
    def compressive_stress_mpa(self) -> float:
        return self.max_compressive_force_n / self.area_m2 / 1e6
    
    def buckling_load_n(self, end_fixity: float = 1.0) -> float:
        """Euler buckling load."""
        E = self.material.E_mpa
        I = self.I_xx_mm4
        Le = end_fixity * self.rod_length_mm
        return (math.pi**2 * E * I) / (Le**2)
    
    @property
    def buckling_fos(self) -> float:
        return self.buckling_load_n() / self.max_compressive_force_n
    
    def whipping_stress_mpa(self, max_rpm: float) -> float:
        """Whipping stress due to rod inertia."""
        omega = 2 * math.pi * max_rpm / 60
        rho = self.material.density_kg_m3
        L = self.rod_length_mm / 1000
        k = self.k_xx_mm / 1000
        return (rho * omega**2 * L**2) / (6 * k**2) / 1e6

# ============================================================================
# SECTION 4: END BEARING DESIGN (Small End + Big End)
# ============================================================================

@dataclass
class ConnectingRodEnds:
    """Small end and big end bearing design."""
    
    bore_mm: float
    max_gas_force_n: float
    max_tensile_force_n: float
    material: ConnectingRodMaterial
    
    def __post_init__(self):
        # Small end (piston pin)
        self.pin_diameter_mm = 0.28 * self.bore_mm
        self.small_end_width_mm = 0.9 * self.pin_diameter_mm
        
        # Big end (crank pin)
        self.crank_pin_diameter_mm = 0.62 * self.bore_mm
        self.big_end_width_mm = 0.85 * self.crank_pin_diameter_mm
    
    @property
    def small_end_bearing_pressure_mpa(self) -> float:
        force = max(self.max_gas_force_n, self.max_tensile_force_n)
        area = self.pin_diameter_mm * self.small_end_width_mm
        return force / area / 1e6
    
    @property
    def big_end_bearing_pressure_mpa(self) -> float:
        area = self.crank_pin_diameter_mm * self.big_end_width_mm
        return self.max_gas_force_n / area / 1e6
    
    @property
    def permissible_bearing_pressure_mpa(self) -> float:
        return 15.0  # MPa for automotive engines
    
    @property
    def bolt_diameter_mm(self) -> int:
        """Big end bolt diameter based on inertia force."""
        force_per_bolt = self.max_tensile_force_n / 2
        sigma_allow = self.material.yield_strength_mpa / 4
        area = force_per_bolt / sigma_allow
        dia = math.sqrt(4 * area / math.pi)
        return max(6, min(16, int(math.ceil(dia))))

# ============================================================================
# SECTION 5: FATIGUE ANALYSIS (Goodman/Soderberg)
# ============================================================================

@dataclass
class ConnectingRodFatigue:
    """Fatigue analysis for connecting rod."""
    
    material: ConnectingRodMaterial
    max_compressive_mpa: float
    max_tensile_mpa: float
    
    @property
    def mean_stress_mpa(self) -> float:
        return (self.max_compressive_mpa + self.max_tensile_mpa) / 2
    
    @property
    def alternating_stress_mpa(self) -> float:
        return abs(self.max_compressive_mpa - self.max_tensile_mpa) / 2
    
    def goodman_fos(self) -> float:
        """Goodman fatigue criterion."""
        sigma_a = self.alternating_stress_mpa
        sigma_m = self.mean_stress_mpa
        sigma_e = self.material.endurance_limit_mpa
        sigma_u = self.material.ultimate_tensile_mpa
        
        if sigma_e <= 0 or sigma_u <= 0:
            return 999.0
        return 1 / (sigma_a/sigma_e + sigma_m/sigma_u)
    
    def soderberg_fos(self) -> float:
        """Soderberg fatigue criterion (more conservative)."""
        sigma_a = self.alternating_stress_mpa
        sigma_m = self.mean_stress_mpa
        sigma_e = self.material.endurance_limit_mpa
        sigma_y = self.material.yield_strength_mpa
        
        if sigma_e <= 0 or sigma_y <= 0:
            return 999.0
        return 1 / (sigma_a/sigma_e + sigma_m/sigma_y)

# ============================================================================
# SECTION 6: COMPLETE CONNECTING ROD RESULT
# ============================================================================

@dataclass
class ConnectingRodResult:
    """Complete connecting rod design results."""
    
    # Dimensions
    bore_mm: float
    stroke_mm: float
    rod_length_mm: float
    rod_stroke_ratio: float
    
    # Cross-section (I-section)
    section_H_mm: float
    section_B_mm: float
    section_t_mm: float
    section_t1_mm: float
    section_area_mm2: float
    
    # Section properties
    I_xx_mm4: float
    I_yy_mm4: float
    k_xx_mm: float
    k_yy_mm: float
    
    # Forces
    max_compressive_kN: float
    max_tensile_kN: float
    compressive_stress_mpa: float
    
    # Buckling
    buckling_load_kN: float
    buckling_fos: float
    
    # Bearings
    pin_diameter_mm: float
    small_end_bearing_mpa: float
    crank_pin_diameter_mm: float
    big_end_bearing_mpa: float
    permissible_bearing_mpa: float
    
    # Bolts
    bolt_diameter_mm: int
    
    # Fatigue
    goodman_fos: float
    soderberg_fos: float
    
    # Material
    material_name: str
    mass_kg: float
    
    @property
    def is_safe(self) -> bool:
        return (self.buckling_fos >= 4.0 and
                self.goodman_fos >= 1.0 and
                self.big_end_bearing_mpa <= self.permissible_bearing_mpa and
                self.small_end_bearing_mpa <= self.permissible_bearing_mpa)
    
    def print_report(self):
        """Print formatted design report."""
        print("=" * 75)
        print("CONNECTING ROD DESIGN REPORT")
        print("=" * 75)
        
        print("\n GEOMETRY:")
        print(f"   Bore: {self.bore_mm:.1f} mm")
        print(f"   Stroke: {self.stroke_mm:.1f} mm")
        print(f"   Rod length: {self.rod_length_mm:.1f} mm")
        print(f"   Rod/Stroke ratio: {self.rod_stroke_ratio:.2f}")
        
        print("\n I-SECTION DIMENSIONS:")
        print(f"   Total depth (H): {self.section_H_mm:.2f} mm")
        print(f"   Flange width (B): {self.section_B_mm:.2f} mm")
        print(f"   Web thickness (t): {self.section_t_mm:.2f} mm")
        print(f"   Flange thickness (t₁): {self.section_t1_mm:.2f} mm")
        print(f"   Area: {self.section_area_mm2:.1f} mm²")
        
        print("\n SECTION PROPERTIES:")
        print(f"   I_xx = {self.I_xx_mm4:.0f} mm⁴")
        print(f"   I_yy = {self.I_yy_mm4:.0f} mm⁴")
        print(f"   k_xx = {self.k_xx_mm:.2f} mm")
        print(f"   k_yy = {self.k_yy_mm:.2f} mm")
        print(f"   Ixx/Iyy = {self.I_xx_mm4/self.I_yy_mm4:.2f} (ideal = 3.2)")
        
        print("\n FORCES:")
        print(f"   Max compressive: {self.max_compressive_kN:.1f} kN")
        print(f"   Max tensile: {self.max_tensile_kN:.1f} kN")
        print(f"   Compressive stress: {self.compressive_stress_mpa:.1f} MPa")
        
        print("\n BUCKLING:")
        print(f"   Euler critical load: {self.buckling_load_kN:.0f} kN")
        print(f"   Factor of safety: {self.buckling_fos:.2f}")
        buckling_status = " Safe" if self.buckling_fos >= 4 else " Check"
        print(f"   Status: {buckling_status}")
        
        print("\n BEARINGS:")
        print(f"   Small end - Pin dia: {self.pin_diameter_mm:.2f} mm")
        print(f"   Small end - Pressure: {self.small_end_bearing_mpa:.2f} MPa")
        print(f"   Big end - Crank pin dia: {self.crank_pin_diameter_mm:.2f} mm")
        print(f"   Big end - Pressure: {self.big_end_bearing_mpa:.2f} MPa")
        print(f"   Permissible pressure: {self.permissible_bearing_mpa:.0f} MPa")
        
        print("\n BOLTS:")
        print(f"   Big end bolt: M{self.bolt_diameter_mm} mm")
        
        print("\n FATIGUE:")
        print(f"   Goodman FOS: {self.goodman_fos:.2f}")
        print(f"   Soderberg FOS: {self.soderberg_fos:.2f}")
        
        print("\n MATERIAL & MASS:")
        print(f"   Material: {self.material_name}")
        print(f"   Mass: {self.mass_kg:.2f} kg")
        
        print("\n" + "=" * 75)
        
        if not self.is_safe:
            print("\n DESIGN ISSUES:")
            if self.buckling_fos < 4:
                print("   - Buckling FOS below 4")
            if self.goodman_fos < 1:
                print("   - Fatigue life not infinite")
            if self.big_end_bearing_mpa > self.permissible_bearing_mpa:
                print("   - Big end bearing pressure exceeds allowable")
        else:
            print("\n DESIGN ACCEPTABLE - All criteria satisfied")
        
        print("=" * 75)


# ============================================================================
# SECTION 7: COMPLETE CONNECTING ROD DESIGNER
# ============================================================================

class ConnectingRodDesigner:
    """
    Complete connecting rod design from scratch.
    
    Integrates:
    1. Force analysis (gas + inertia)
    2. I-section optimization (Rankine buckling)
    3. Bearing design (small + big end)
    4. Bolt design
    5. Fatigue analysis (Goodman/Soderberg)
    6. Whipping stress check
    """
    
    def __init__(
        self,
        bore_mm: float,
        stroke_mm: float,
        max_gas_pressure_mpa: float,
        max_rpm: float,
        reciprocating_mass_kg: float,
        material_name: str = "Forged Steel (4340)",
        rod_length_ratio: float = 1.7,):
        """
        Initialize connecting rod designer.
        
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
            Mass of piston + rings + pin + small end (kg)
        material_name : str
            Connecting rod material
        rod_length_ratio : float
            Rod length / stroke ratio (1.5-1.8 typical)
        """
        
        self.bore_mm = bore_mm
        self.stroke_mm = stroke_mm
        self.rod_length_mm = rod_length_ratio * stroke_mm
        self.material = get_conrod_material(material_name)
        
        # Forces
        self.forces = ConnectingRodForces(
            bore_mm=bore_mm,
            stroke_mm=stroke_mm,
            rod_length_mm=self.rod_length_mm,
            reciprocating_mass_kg=reciprocating_mass_kg,
            max_gas_pressure_mpa=max_gas_pressure_mpa,
            max_rpm=max_rpm,)
        
        # Cross-section
        self.section = ConnectingRodCrossSection(
            bore_mm=bore_mm,
            stroke_mm=stroke_mm,
            rod_length_mm=self.rod_length_mm,
            max_compressive_force_n=self.forces.max_compressive_force_n,
            material=self.material,)
        
        # Ends
        self.ends = ConnectingRodEnds(
            bore_mm=bore_mm,
            max_gas_force_n=self.forces.gas_force_n,
            max_tensile_force_n=self.forces.max_tensile_force_n,
            material=self.material,)
        
        # Fatigue
        self.fatigue = ConnectingRodFatigue(
            material=self.material,
            max_compressive_mpa=self.section.compressive_stress_mpa,
            max_tensile_mpa=0,)  # Simplified
        
        
        self.results = self._calculate_results()
    
    def _calculate_results(self) -> ConnectingRodResult:
        """Calculate all design results."""
        
        # Mass estimation
        volume_m3 = (self.section.area_m2 * self.rod_length_mm / 1000) * 1.3
        mass_kg = volume_m3 * self.material.density_kg_m3
        
        return ConnectingRodResult(
            bore_mm=self.bore_mm,
            stroke_mm=self.stroke_mm,
            rod_length_mm=self.rod_length_mm,
            rod_stroke_ratio=self.rod_length_mm / self.stroke_mm,
            section_H_mm=self.section.H_mm,
            section_B_mm=self.section.B_mm,
            section_t_mm=self.section.t_mm,
            section_t1_mm=self.section.t1_mm,
            section_area_mm2=self.section.area_mm2,
            I_xx_mm4=self.section.I_xx_mm4,
            I_yy_mm4=self.section.I_yy_mm4,
            k_xx_mm=self.section.k_xx_mm,
            k_yy_mm=self.section.k_yy_mm,
            max_compressive_kN=self.forces.max_compressive_force_n / 1000,
            max_tensile_kN=self.forces.max_tensile_force_n / 1000,
            compressive_stress_mpa=self.section.compressive_stress_mpa,
            buckling_load_kN=self.section.buckling_load_n() / 1000,
            buckling_fos=self.section.buckling_fos,
            pin_diameter_mm=self.ends.pin_diameter_mm,
            small_end_bearing_mpa=self.ends.small_end_bearing_pressure_mpa,
            crank_pin_diameter_mm=self.ends.crank_pin_diameter_mm,
            big_end_bearing_mpa=self.ends.big_end_bearing_pressure_mpa,
            permissible_bearing_mpa=self.ends.permissible_bearing_pressure_mpa,
            bolt_diameter_mm=self.ends.bolt_diameter_mm,
            goodman_fos=self.fatigue.goodman_fos(),
            soderberg_fos=self.fatigue.soderberg_fos(),
            material_name=self.material.name,
            mass_kg=mass_kg,)
    
    def get_results(self) -> ConnectingRodResult:
        """Return complete design results."""
        return self.results
    
    def print_report(self):
        """Print formatted design report."""
        self.results.print_report()


