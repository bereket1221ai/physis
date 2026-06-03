"""
valve.py - Complete Valve and Valve Train Design

Sources:
- Machine Design Textbook (Chapter 32.22-32.24)
- Internal Combustion Engine Fundamentals - Heywood
- Valve and Valve Train Design - SAE
- Mechanical Engineering Design - Shigley

Covers:
- Poppet valve geometry
- Valve spring design (dynamic)
- Port flow analysis (discharge coefficient)
- Heat transfer and cooling
- Seat pressure and sealing
- Valve timing and lift profiles
- Material selection (high temperature alloys)
"""

import math
from dataclasses import dataclass, field
from typing import Dict, Any, Optional, Tuple, List


# ============================================================================
# SECTION 1: VALVE MATERIALS DATABASE
# ============================================================================

@dataclass(frozen=True)
class ValveMaterial:
    """High temperature materials for engine valves."""
    
    name: str
    density_kg_m3: float
    ultimate_tensile_mpa: float
    yield_strength_mpa: float
    youngs_modulus_gpa: float
    thermal_conductivity_w_mk: float
    coefficient_thermal_expansion_1e6: float
    max_temperature_c: float
    hardness_hb: float
    wear_resistance: str
    application: str  # 'intake', 'exhaust', 'both'
    
    @property
    def E_mpa(self) -> float:
        return self.youngs_modulus_gpa * 1000.0


# Valve material database
VALVE_MATERIALS: Dict[str, ValveMaterial] = {
    "Martensitic Steel (X45CrSi9-3)": ValveMaterial(
        name="Martensitic Steel (X45CrSi9-3)",
        density_kg_m3=7600,
        ultimate_tensile_mpa=880,
        yield_strength_mpa=720,
        youngs_modulus_gpa=208,
        thermal_conductivity_w_mk=24,
        coefficient_thermal_expansion_1e6=11,
        max_temperature_c=800,
        hardness_hb=320,
        wear_resistance="Good",
        application="intake",
    ),
    "Silicon Chrome Steel (21-4N)": ValveMaterial(
        name="Silicon Chrome Steel (21-4N)",
        density_kg_m3=7700,
        ultimate_tensile_mpa=950,
        yield_strength_mpa=800,
        youngs_modulus_gpa=210,
        thermal_conductivity_w_mk=22,
        coefficient_thermal_expansion_1e6=11,
        max_temperature_c=850,
        hardness_hb=350,
        wear_resistance="Very Good",
        application="exhaust",
    ),
    "Inconel 751": ValveMaterial(
        name="Inconel 751",
        density_kg_m3=8200,
        ultimate_tensile_mpa=1200,
        yield_strength_mpa=1000,
        youngs_modulus_gpa=214,
        thermal_conductivity_w_mk=11,
        coefficient_thermal_expansion_1e6=12,
        max_temperature_c=980,
        hardness_hb=380,
        wear_resistance="Excellent",
        application="exhaust",
    ),
    "Nimonic 80A": ValveMaterial(
        name="Nimonic 80A",
        density_kg_m3=8100,
        ultimate_tensile_mpa=1100,
        yield_strength_mpa=900,
        youngs_modulus_gpa=211,
        thermal_conductivity_w_mk=13,
        coefficient_thermal_expansion_1e6=12,
        max_temperature_c=950,
        hardness_hb=360,
        wear_resistance="Excellent",
        application="exhaust",
    ),
    "Titanium (Ti-6Al-4V)": ValveMaterial(
        name="Titanium (Ti-6Al-4V)",
        density_kg_m3=4430,
        ultimate_tensile_mpa=950,
        yield_strength_mpa=880,
        youngs_modulus_gpa=114,
        thermal_conductivity_w_mk=7,
        coefficient_thermal_expansion_1e6=9,
        max_temperature_c=550,
        hardness_hb=330,
        wear_resistance="Good",
        application="intake",
    ),
    "Stellite Faced": ValveMaterial(
        name="Stellite Faced",
        density_kg_m3=8400,
        ultimate_tensile_mpa=900,
        yield_strength_mpa=700,
        youngs_modulus_gpa=230,
        thermal_conductivity_w_mk=15,
        coefficient_thermal_expansion_1e6=13,
        max_temperature_c=850,
        hardness_hb=480,
        wear_resistance="Excellent",
        application="both",
    ),
}


def get_valve_material(name: str) -> ValveMaterial:
    """Get valve material by name."""
    if name not in VALVE_MATERIALS:
        raise ValueError(f"Unknown material: {name}. Available: {list(VALVE_MATERIALS.keys())}")
    return VALVE_MATERIALS[name]


# ============================================================================
# SECTION 2: VALVE GEOMETRY
# ============================================================================

@dataclass
class ValveGeometry:
    """Poppet valve geometric parameters."""
    
    head_diameter_mm: float
    seat_angle_deg: float = 45.0
    stem_diameter_mm: Optional[float] = None
    
    def __post_init__(self):
        if self.stem_diameter_mm is None:
            self.stem_diameter_mm = 0.18 * self.head_diameter_mm
        
        self.seat_angle_rad = math.radians(self.seat_angle_deg)
        self.margin_thickness_mm = 0.05 * self.head_diameter_mm
        self.head_thickness_mm = 0.1 * self.head_diameter_mm
        self.stem_length_mm = 5 * self.head_diameter_mm
        self.seat_width_mm = 0.03 * self.head_diameter_mm
    
    @property
    def head_area_mm2(self) -> float:
        return math.pi * self.head_diameter_mm**2 / 4
    
    @property
    def stem_area_mm2(self) -> float:
        return math.pi * self.stem_diameter_mm**2 / 4
    
    def curtain_area_mm2(self, lift_mm: float) -> float:
        """Flow area when valve is open."""
        return math.pi * self.head_diameter_mm * lift_mm * math.cos(self.seat_angle_rad)
    
    def flow_coefficient(self, lift_mm: float) -> float:
        """Discharge coefficient (Cd) based on lift/diameter ratio."""
        lift_ratio = lift_mm / self.head_diameter_mm
        if lift_ratio < 0.1:
            return 0.60
        elif lift_ratio < 0.2:
            return 0.65
        elif lift_ratio < 0.3:
            return 0.70
        return 0.72
    
    def valve_mass_kg(self, density: float) -> float:
        """Estimate valve mass."""
        head_vol = self.head_area_mm2 * self.head_thickness_mm / 1e9
        stem_vol = self.stem_area_mm2 * self.stem_length_mm / 1e9
        return (head_vol + stem_vol) * density


# ============================================================================
# SECTION 3: VALVE FORCES AND DYNAMICS
# ============================================================================

@dataclass
class ValveForces:
    """Forces acting on valve and valve train."""
    
    head_diameter_mm: float
    max_cylinder_pressure_mpa: float
    max_rpm: float
    valve_mass_kg: float
    spring_rate_n_mm: float = 30.0
    preload_mm: float = 20.0
    max_lift_mm: float = 10.0
    
    @property
    def head_area_m2(self) -> float:
        return math.pi * (self.head_diameter_mm / 1000)**2 / 4
    
    @property
    def gas_force_n(self) -> float:
        """Force from cylinder gas pressure."""
        return self.max_cylinder_pressure_mpa * 1e6 * self.head_area_m2
    
    def inertia_force_n(self, acceleration_m_s2: float) -> float:
        """Inertia force from valve motion."""
        return self.valve_mass_kg * acceleration_m_s2
    
    @property
    def spring_force_n(self) -> float:
        """Spring force at max lift."""
        return self.spring_rate_n_mm * (self.preload_mm + self.max_lift_mm)
    
    @property
    def seat_force_n(self) -> float:
        """Force on valve seat when closed."""
        return self.spring_rate_n_mm * self.preload_mm + self.gas_force_n
    
    @property
    def max_acceleration_m_s2(self) -> float:
        """Maximum valve acceleration (simplified)."""
        # For performance cam profile
        return 3000.0
    
    @property
    def max_spring_force_n(self) -> float:
        """Maximum spring force."""
        return self.spring_force_n


# ============================================================================
# SECTION 4: VALVE SPRING DESIGN (Dynamic)
# ============================================================================

@dataclass
class ValveSpring:
    """High-performance valve spring design with surge analysis."""
    
    wire_diameter_mm: float
    mean_coil_diameter_mm: float
    active_coils: int
    free_length_mm: float
    installed_length_mm: float
    material_gpa: float = 80.0  # Shear modulus
    density_kg_m3: float = 7850.0
    
    def __post_init__(self):
        self.d_m = self.wire_diameter_mm / 1000
        self.D_m = self.mean_coil_diameter_mm / 1000
        self.C = self.mean_coil_diameter_mm / self.wire_diameter_mm
        # Wahl factor for curvature stress correction
        self.K_w = (4 * self.C - 1) / (4 * self.C - 4) + 0.615 / self.C
    
    @property
    def spring_rate_n_mm(self) -> float:
        """Spring stiffness (N/mm)."""
        G = self.material_gpa * 1e9
        k_n_m = (G * self.d_m**4) / (8 * self.D_m**3 * self.active_coils)
        return k_n_m / 1000
    
    @property
    def preload_mm(self) -> float:
        return self.free_length_mm - self.installed_length_mm
    
    def preload_force_n(self, max_lift_mm: float) -> float:
        return self.spring_rate_n_mm * (self.preload_mm + max_lift_mm)
    
    @property
    def solid_length_mm(self) -> float:
        return self.active_coils * self.wire_diameter_mm
    
    def coil_bind_safety(self, max_lift_mm: float) -> float:
        max_compression = self.preload_mm + max_lift_mm
        return (self.free_length_mm - self.solid_length_mm) / max_compression
    
    @property
    def natural_frequency_hz(self) -> float:
        """Spring natural frequency (avoid resonance)."""
        G = self.material_gpa * 1e9
        rho = self.density_kg_m3
        return (self.wire_diameter_mm / 1000) / (math.pi * (self.mean_coil_diameter_mm/1000)**2 * self.active_coils) * math.sqrt(G / (2 * rho))
    
    def valve_float_rpm(self, max_lift_mm: float) -> float:
        """Estimated RPM where valve float occurs."""
        spring_force = self.preload_force_n(max_lift_mm)
        return math.sqrt(spring_force / 0.0001) * 60


# ============================================================================
# SECTION 5: VALVE SEAT AND SEALING
# ============================================================================

@dataclass
class ValveSeat:
    """Valve seat design and analysis."""
    
    head_diameter_mm: float
    seat_angle_deg: float = 45.0
    seat_width_mm: Optional[float] = None
    
    def __post_init__(self):
        if self.seat_width_mm is None:
            self.seat_width_mm = 0.03 * self.head_diameter_mm
        self.seat_angle_rad = math.radians(self.seat_angle_deg)
    
    @property
    def contact_diameter_mm(self) -> float:
        """Mean contact diameter of seat."""
        return self.head_diameter_mm - self.seat_width_mm
    
    @property
    def contact_area_mm2(self) -> float:
        return math.pi * self.contact_diameter_mm * self.seat_width_mm
    
    def seat_pressure_mpa(self, closing_force_n: float) -> float:
        return closing_force_n / self.contact_area_mm2 / 1e6
    
    @staticmethod
    def allowable_pressure_mpa(material_name: str) -> float:
        if "Stellite" in material_name:
            return 200.0
        elif "Titanium" in material_name:
            return 150.0
        return 120.0
    
    @property
    def recommended_interference_mm(self) -> float:
        """Interference fit for valve seat insert."""
        return 0.05 + 0.0003 * self.head_diameter_mm


# ============================================================================
# SECTION 6: VALVE TIMING AND LIFT
# ============================================================================

@dataclass
class ValveTiming:
    """Valve timing and lift profile."""
    
    max_lift_mm: float
    cam_duration_deg: float = 260.0
    lobe_center_angle_deg: float = 110.0
    opening_before_tdc_deg: float = 10.0
    closing_after_bdc_deg: float = 10.0
    
    @property
    def overlap_deg(self) -> float:
        """Valve overlap period (both valves open)."""
        return self.opening_before_tdc_deg + self.closing_after_bdc_deg
    
    def lift_at_crank_angle(self, crank_angle_deg: float) -> float:
        """Valve lift at given crank angle (simplified polynomial)."""
        cam_angle = crank_angle_deg * 0.5
        if cam_angle < 0 or cam_angle > self.cam_duration_deg:
            return 0.0
        x = (cam_angle / self.cam_duration_deg) * 2 - 1
        return self.max_lift_mm * (1 - x**2)
    
    @property
    def lift_area_mm2_deg(self) -> float:
        """Area under lift curve (flow potential)."""
        return (2/3) * self.max_lift_mm * self.cam_duration_deg


# ============================================================================
# SECTION 7: COMPLETE VALVE RESULT
# ============================================================================

@dataclass
class ValveDesignResult:
    """Complete valve design results."""
    
    # Geometry
    head_diameter_mm: float
    stem_diameter_mm: float
    seat_angle_deg: float
    seat_width_mm: float
    max_lift_mm: float
    head_thickness_mm: float
    margin_thickness_mm: float
    
    # Flow
    curtain_area_mm2: float
    flow_coefficient: float
    
    # Forces
    gas_force_n: float
    spring_force_n: float
    seat_force_n: float
    
    # Seat
    seat_pressure_mpa: float
    allowable_seat_pressure_mpa: float
    
    # Spring
    spring_rate_n_mm: float
    spring_natural_frequency_hz: float
    spring_coil_bind_safety: float
    
    # Timing
    overlap_deg: float
    lift_area_mm2_deg: float
    
    # Material
    material_name: str
    max_temperature_c: float
    valve_mass_g: float
    
    @property
    def is_safe(self) -> bool:
        return (self.seat_pressure_mpa <= self.allowable_seat_pressure_mpa and
                self.spring_coil_bind_safety >= 1.2)
    
    def print_report(self):
        print("=" * 75)
        print("COMPLETE VALVE DESIGN REPORT")
        print("=" * 75)
        
        print("\n VALVE GEOMETRY:")
        print(f"   Head diameter: {self.head_diameter_mm:.1f} mm")
        print(f"   Stem diameter: {self.stem_diameter_mm:.2f} mm")
        print(f"   Seat angle: {self.seat_angle_deg:.0f}°")
        print(f"   Seat width: {self.seat_width_mm:.3f} mm")
        print(f"   Max lift: {self.max_lift_mm:.2f} mm")
        print(f"   Head thickness: {self.head_thickness_mm:.2f} mm")
        
        print("\n FLOW CHARACTERISTICS:")
        print(f"   Curtain area: {self.curtain_area_mm2:.1f} mm²")
        print(f"   Flow coefficient (Cd): {self.flow_coefficient:.3f}")
        
        print("\n FORCES:")
        print(f"   Gas force: {self.gas_force_n:.1f} N")
        print(f"   Spring force: {self.spring_force_n:.1f} N")
        print(f"   Seat force: {self.seat_force_n:.1f} N")
        
        print("\n VALVE SEAT:")
        print(f"   Seat pressure: {self.seat_pressure_mpa:.1f} MPa")
        print(f"   Allowable pressure: {self.allowable_seat_pressure_mpa:.0f} MPa")
        seat_status = " OK" if self.seat_pressure_mpa <= self.allowable_seat_pressure_mpa else "⚠️ HIGH"
        print(f"   Status: {seat_status}")
        
        print("\n VALVE SPRING:")
        print(f"   Spring rate: {self.spring_rate_n_mm:.2f} N/mm")
        print(f"   Natural frequency: {self.spring_natural_frequency_hz:.1f} Hz")
        print(f"   Coil bind safety: {self.spring_coil_bind_safety:.2f}")
        
        print("\n⏱ VALVE TIMING:")
        print(f"   Overlap: {self.overlap_deg:.0f}°")
        print(f"   Lift area: {self.lift_area_mm2_deg:.0f} mm²·deg")
        
        print("\n MATERIAL:")
        print(f"   Material: {self.material_name}")
        print(f"   Max temp: {self.max_temperature_c}°C")
        print(f"   Mass: {self.valve_mass_g:.1f} g")
        
        print("\n" + "=" * 75)
        
        if not self.is_safe:
            print("\n DESIGN ISSUES:")
            if self.seat_pressure_mpa > self.allowable_seat_pressure_mpa:
                print("   - Seat pressure exceeds allowable")
            if self.spring_coil_bind_safety < 1.2:
                print("   - Spring coil bind risk")
        else:
            print("\n DESIGN ACCEPTABLE - All criteria satisfied")
        
        print("=" * 75)


# ============================================================================
# SECTION 8: COMPLETE VALVE DESIGNER
# ============================================================================

class ValveDesigner:
    """Complete valve design from scratch."""
    
    def __init__(
        self,
        bore_mm: float,
        head_diameter_mm: float,
        max_cylinder_pressure_mpa: float,
        max_rpm: float,
        application: str = "intake",
        material_name: Optional[str] = None,
        seat_angle_deg: float = 45.0,
        max_lift_mm: Optional[float] = None,
    ):
        self.bore_mm = bore_mm
        self.head_diameter_mm = head_diameter_mm
        self.max_pressure_mpa = max_cylinder_pressure_mpa
        self.max_rpm = max_rpm
        self.application = application
        
        # Auto-select material if not provided
        if material_name is None:
            if application == "exhaust":
                material_name = "Silicon Chrome Steel (21-4N)"
            else:
                material_name = "Martensitic Steel (X45CrSi9-3)"
        
        self.material = get_valve_material(material_name)
        self.geometry = ValveGeometry(head_diameter_mm, seat_angle_deg)
        
        if max_lift_mm is None:
            max_lift_mm = 0.25 * head_diameter_mm
        self.max_lift_mm = max_lift_mm
        
        self.valve_mass_kg = self.geometry.valve_mass_kg(self.material.density_kg_m3)
        
        self.forces = ValveForces(
            head_diameter_mm=head_diameter_mm,
            max_cylinder_pressure_mpa=max_cylinder_pressure_mpa,
            max_rpm=max_rpm,
            valve_mass_kg=self.valve_mass_kg,
            max_lift_mm=max_lift_mm,
        )
        
        self.spring = ValveSpring(
            wire_diameter_mm=4.0,
            mean_coil_diameter_mm=25.0,
            active_coils=6,
            free_length_mm=60.0,
            installed_length_mm=40.0,
        )
        
        self.seat = ValveSeat(head_diameter_mm, seat_angle_deg)
        self.timing = ValveTiming(max_lift_mm)
        
        self.results = self._calculate_results()
    
    def _calculate_results(self) -> ValveDesignResult:
        curtain = self.geometry.curtain_area_mm2(self.max_lift_mm)
        
        return ValveDesignResult(
            head_diameter_mm=self.head_diameter_mm,
            stem_diameter_mm=self.geometry.stem_diameter_mm,
            seat_angle_deg=self.geometry.seat_angle_deg,
            seat_width_mm=self.geometry.seat_width_mm,
            max_lift_mm=self.max_lift_mm,
            head_thickness_mm=self.geometry.head_thickness_mm,
            margin_thickness_mm=self.geometry.margin_thickness_mm,
            curtain_area_mm2=curtain,
            flow_coefficient=self.geometry.flow_coefficient(self.max_lift_mm),
            gas_force_n=self.forces.gas_force_n,
            spring_force_n=self.forces.spring_force_n,
            seat_force_n=self.forces.seat_force_n,
            seat_pressure_mpa=self.seat.seat_pressure_mpa(self.forces.seat_force_n),
            allowable_seat_pressure_mpa=ValveSeat.allowable_pressure_mpa(self.material.name),
            spring_rate_n_mm=self.spring.spring_rate_n_mm,
            spring_natural_frequency_hz=self.spring.natural_frequency_hz,
            spring_coil_bind_safety=self.spring.coil_bind_safety(self.max_lift_mm),
            overlap_deg=self.timing.overlap_deg,
            lift_area_mm2_deg=self.timing.lift_area_mm2_deg,
            material_name=self.material.name,
            max_temperature_c=self.material.max_temperature_c,
            valve_mass_g=self.valve_mass_kg * 1000,
        )
    
    def get_results(self) -> ValveDesignResult:
        return self.results
    
    def print_report(self):
        self.results.print_report()


# ============================================================================
# EXAMPLE USAGE
# ============================================================================

if __name__ == "__main__":
    # Intake valve
    intake = ValveDesigner(
        bore_mm=85.0,
        head_diameter_mm=34.0,
        max_cylinder_pressure_mpa=8.0,
        max_rpm=6500,
        application="intake",
    )
    intake.print_report()
    
    # Exhaust valve
    exhaust = ValveDesigner(
        bore_mm=85.0,
        head_diameter_mm=30.0,
        max_cylinder_pressure_mpa=8.0,
        max_rpm=6500,
        application="exhaust",
        material_name="Inconel 751",
    )
    exhaust.print_report()