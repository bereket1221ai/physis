"""
cycle.py - Complete Engine Cycle Analysis

Sources:
- Machine Design Textbook
- Internal Combustion Engine Fundamentals - John B. Heywood
- Engineering Thermodynamics - Cengel & Boles
- SAE International standards

Covers:
- Otto Cycle (Spark Ignition)
- Diesel Cycle (Compression Ignition)
- Dual Cycle (Limited Pressure)
- Real gas properties (variable specific heat)
- Heat release modeling (Wiebe function)
- Knock prediction
- Turbocharging effects
- Engine performance maps
- Emissions estimation
"""

import math
from dataclasses import dataclass, field
from typing import Dict, Any, Optional, Tuple, List


# ============================================================================
# SECTION 1: WORKING FLUID PROPERTIES
# ============================================================================

@dataclass(frozen=True)
class WorkingFluid:
    """Real gas properties for working fluid."""
    
    name: str
    gamma: float  # Ratio of specific heats (cp/cv)
    R_j_kgk: float  # Specific gas constant
    cp_j_kgk: float  # Specific heat at constant pressure
    cv_j_kgk: float  # Specific heat at constant volume
    
    @classmethod
    def air(cls) -> 'WorkingFluid':
        """Standard air properties."""
        return cls(
            name="Air",
            gamma=1.4,
            R_j_kgk=287.0,
            cp_j_kgk=1005.0,
            cv_j_kgk=718.0,
        )
    
    @classmethod
    def air_variable_cp(cls, temperature_k: float) -> 'WorkingFluid':
        """Air with temperature-dependent specific heat."""
        # Polynomial approximation for cp(T)
        cp = 1000 + 0.1 * (temperature_k - 300)
        cv = cp / 1.4
        gamma = cp / cv
        return cls(
            name="Air (Variable CP)",
            gamma=gamma,
            R_j_kgk=287.0,
            cp_j_kgk=cp,
            cv_j_kgk=cv,
        )


# ============================================================================
# SECTION 2: THERMODYNAMIC STATE
# ============================================================================

@dataclass
class StatePoint:
    """Thermodynamic state (P, V, T)."""
    
    pressure_pa: float
    volume_m3: float
    temperature_k: float
    mass_kg: float
    fluid: WorkingFluid
    
    @property
    def pressure_mpa(self) -> float:
        return self.pressure_pa / 1e6
    
    @property
    def pressure_bar(self) -> float:
        return self.pressure_pa / 1e5
    
    @property
    def volume_cc(self) -> float:
        return self.volume_m3 * 1e6
    
    def print(self):
        print(f"  P={self.pressure_bar:.2f} bar, T={self.temperature_k:.1f}K, V={self.volume_cc:.1f}cc")
    
    def copy(self) -> 'StatePoint':
        return StatePoint(
            pressure_pa=self.pressure_pa,
            volume_m3=self.volume_m3,
            temperature_k=self.temperature_k,
            mass_kg=self.mass_kg,
            fluid=self.fluid,
        )


# ============================================================================
# SECTION 3: OTTO CYCLE (Spark Ignition)
# ============================================================================

@dataclass
class OttoCycle:
    """
    Otto cycle for spark ignition engines.
    
    Processes:
    1→2: Isentropic compression
    2→3: Constant volume heat addition
    3→4: Isentropic expansion
    4→1: Constant volume heat rejection
    """
    
    bore_mm: float
    stroke_mm: float
    compression_ratio: float
    inlet_pressure_kpa: float = 101.3
    inlet_temperature_k: float = 298.0
    peak_pressure_mpa: Optional[float] = None
    peak_temperature_k: Optional[float] = None
    fluid: WorkingFluid = field(default_factory=WorkingFluid.air)
    
    def __post_init__(self):
        # Volume calculations
        self.swept_volume_cc = math.pi * (self.bore_mm**2) / 4 * self.stroke_mm / 1000
        self.swept_volume_m3 = self.swept_volume_cc / 1e6
        self.clearance_volume_cc = self.swept_volume_cc / (self.compression_ratio - 1)
        self.clearance_volume_m3 = self.clearance_volume_cc / 1e6
        self.total_volume_cc = self.swept_volume_cc + self.clearance_volume_cc
        self.total_volume_m3 = self.total_volume_cc / 1e6
        
        # Mass of working fluid
        self.mass_kg = (self.inlet_pressure_kpa * 1000 * self.total_volume_m3) / (self.fluid.R_j_kgk * self.inlet_temperature_k)
    
    @classmethod
    def from_power(cls, power_kw: float, rpm: float, compression_ratio: float, 
                   mep_mpa: float = 1.0, cylinders: int = 4, L_D_ratio: float = 1.2):
        """
        START HERE: Design Otto cycle from power requirement.
        
        Parameters:
        -----------
        power_kw : float
            Total engine power (kW)
        rpm : float
            Engine speed (RPM)
        compression_ratio : float
            Compression ratio (e.g., 10.5)
        mep_mpa : float
            Mean effective pressure (MPa) - typical 0.8-1.2 for gasoline
        cylinders : int
            Number of cylinders
        L_D_ratio : float
            Stroke/Bore ratio (typical 1.0-1.3)
        
        Returns:
        --------
        OttoCycle : OttoCycle instance with calculated bore/stroke
        """
        # Power per cylinder
        power_per_cyl = power_kw * 1000 / cylinders
        
        # Strokes per second (4-stroke: power every 2 revolutions)
        strokes_per_sec = rpm / 120
        mep_pa = mep_mpa * 1e6
        
        # L × A = Power / (MEP × strokes/sec)
        LA_m3 = power_per_cyl / (mep_pa * strokes_per_sec)
        LA_mm3 = LA_m3 * 1e9
        
        # Calculate bore and stroke
        bore_mm = ((4 * LA_mm3) / (L_D_ratio * math.pi)) ** (1/3)
        stroke_mm = L_D_ratio * bore_mm
        
        # Create instance with calculated dimensions
        return cls(
            bore_mm=bore_mm,
            stroke_mm=stroke_mm,
            compression_ratio=compression_ratio,)
    
    def state1_intake(self) -> StatePoint:
        """Start of compression stroke (BDC)."""
        return StatePoint(
            pressure_pa=self.inlet_pressure_kpa * 1000,
            volume_m3=self.total_volume_m3,
            temperature_k=self.inlet_temperature_k,
            mass_kg=self.mass_kg,
            fluid=self.fluid,
        )
    
    def state2_compression(self) -> StatePoint:
        """End of compression stroke (TDC)."""
        s1 = self.state1_intake()
        P2 = s1.pressure_pa * (self.compression_ratio ** self.fluid.gamma)
        V2 = s1.volume_m3 / self.compression_ratio
        T2 = s1.temperature_k * (self.compression_ratio ** (self.fluid.gamma - 1))
        return StatePoint(P2, V2, T2, self.mass_kg, self.fluid)
    
    def state3_combustion(self) -> StatePoint:
        """After heat addition (constant volume)."""
        s2 = self.state2_compression()
        V3 = s2.volume_m3
        
        if self.peak_pressure_mpa:
            P3 = self.peak_pressure_mpa * 1e6
        else:
            P3 = s2.pressure_pa * 4.0  # Typical pressure ratio
        
        T3 = (P3 * V3) / (self.mass_kg * self.fluid.R_j_kgk)
        return StatePoint(P3, V3, T3, self.mass_kg, self.fluid)
    
    def state4_expansion(self) -> StatePoint:
        """End of expansion stroke (BDC)."""
        s3 = self.state3_combustion()
        s1 = self.state1_intake()
        P4 = s3.pressure_pa / (self.compression_ratio ** self.fluid.gamma)
        V4 = s1.volume_m3
        T4 = s3.temperature_k / (self.compression_ratio ** (self.fluid.gamma - 1))
        return StatePoint(P4, V4, T4, self.mass_kg, self.fluid)
    
    @property
    def heat_added_j(self) -> float:
        """Heat added during combustion (J)."""
        s2 = self.state2_compression()
        s3 = self.state3_combustion()
        return self.mass_kg * self.fluid.cv_j_kgk * (s3.temperature_k - s2.temperature_k)
    
    @property
    def heat_rejected_j(self) -> float:
        """Heat rejected during exhaust (J)."""
        s1 = self.state1_intake()
        s4 = self.state4_expansion()
        return self.mass_kg * self.fluid.cv_j_kgk * (s4.temperature_k - s1.temperature_k)
    
    @property
    def work_net_j(self) -> float:
        """Net work output per cycle (J)."""
        return self.heat_added_j - self.heat_rejected_j
    
    @property
    def thermal_efficiency(self) -> float:
        """Air-standard Otto cycle efficiency."""
        return 1 - 1 / (self.compression_ratio ** (self.fluid.gamma - 1))
    
    @property
    def actual_efficiency(self) -> float:
        """Actual efficiency (including losses)."""
        return self.thermal_efficiency * 0.85
    
    @property
    def mean_effective_pressure_mpa(self) -> float:
        """Mean effective pressure (MPa)."""
        return self.work_net_j / self.swept_volume_m3 / 1e6
    
    def power_kw(self, cylinders: int = 4, rpm: float = 6000) -> float:
        """Engine power output (kW)."""
        cycles_per_sec = (rpm / 60) * 0.5  # 4-stroke
        return self.work_net_j * cylinders * cycles_per_sec / 1000
    
    @property
    def knock_limited_compression_ratio(self, fuel_octane: float = 95.0) -> float:
        """Maximum compression ratio before knock."""
        return 8.0 + (fuel_octane - 90) / 10
    
    def print_report(self):
        """Print cycle analysis report."""
        s1 = self.state1_intake()
        s2 = self.state2_compression()
        s3 = self.state3_combustion()
        s4 = self.state4_expansion()
        
        print("=" * 75)
        print("OTTO CYCLE ANALYSIS - Spark Ignition Engine")
        print("=" * 75)
        
        print(f"\n📌 ENGINE PARAMETERS:")
        print(f"   Bore: {self.bore_mm:.1f} mm")
        print(f"   Stroke: {self.stroke_mm:.1f} mm")
        print(f"   Compression ratio: {self.compression_ratio:.1f}:1")
        print(f"   Displacement: {self.swept_volume_cc:.1f} cc")
        print(f"   Mass of air: {self.mass_kg * 1000:.2f} g")
        
        print(f"\n📍 STATE POINTS:")
        print(f"   State 1 (Intake BDC): ", end="")
        s1.print()
        print(f"   State 2 (Compression TDC): ", end="")
        s2.print()
        print(f"   State 3 (Combustion): ", end="")
        s3.print()
        print(f"   State 4 (Expansion BDC): ", end="")
        s4.print()
        
        print(f"\n⚡ CYCLE PERFORMANCE:")
        print(f"   Heat added (Q_in): {self.heat_added_j:.1f} J")
        print(f"   Heat rejected (Q_out): {self.heat_rejected_j:.1f} J")
        print(f"   Net work (W_net): {self.work_net_j:.1f} J")
        print(f"   Thermal efficiency (η): {self.thermal_efficiency * 100:.2f}%")
        print(f"   Actual efficiency: {self.actual_efficiency * 100:.2f}%")
        print(f"   Mean effective pressure: {self.mean_effective_pressure_mpa:.2f} MPa")
        
        print(f"\n🔧 ENGINE POWER (4-cylinder):")
        for rpm in [2000, 4000, 6000, 8000]:
            power = self.power_kw(cylinders=4, rpm=rpm)
            print(f"   {rpm} RPM: {power:.1f} kW ({power * 1.341:.1f} HP)")
        
        print("=" * 75)


# ============================================================================
# SECTION 4: DIESEL CYCLE (Compression Ignition)
# ============================================================================

@dataclass
class DieselCycle:
    """
    Diesel cycle for compression ignition engines.
    
    Processes:
    1→2: Isentropic compression
    2→3: Constant pressure heat addition
    3→4: Isentropic expansion
    4→1: Constant volume heat rejection
    """
    
    bore_mm: float
    stroke_mm: float
    compression_ratio: float
    cutoff_ratio: float  # V3/V2 (1.5-2.5 typical)
    inlet_pressure_kpa: float = 101.3
    inlet_temperature_k: float = 298.0
    fluid: WorkingFluid = field(default_factory=WorkingFluid.air)
    
    def __post_init__(self):
        self.swept_volume_cc = math.pi * (self.bore_mm**2) / 4 * self.stroke_mm / 1000
        self.swept_volume_m3 = self.swept_volume_cc / 1e6
        self.clearance_volume_cc = self.swept_volume_cc / (self.compression_ratio - 1)
        self.clearance_volume_m3 = self.clearance_volume_cc / 1e6
        self.total_volume_cc = self.swept_volume_cc + self.clearance_volume_cc
        self.total_volume_m3 = self.total_volume_cc / 1e6
        self.mass_kg = (self.inlet_pressure_kpa * 1000 * self.total_volume_m3) / (self.fluid.R_j_kgk * self.inlet_temperature_k)
    
    @classmethod
    def from_power(cls, power_kw: float, rpm: float, compression_ratio: float, 
                   cutoff_ratio: float, mep_mpa: float = 1.2, cylinders: int = 4, 
                   L_D_ratio: float = 1.2):
        """
        START HERE: Design Diesel cycle from power requirement.
        
        Parameters:
        -----------
        power_kw : float
            Total engine power (kW)
        rpm : float
            Engine speed (RPM)
        compression_ratio : float
            Compression ratio (e.g., 18.0)
        cutoff_ratio : float
            Cutoff ratio (V3/V2, typical 1.5-2.5)
        mep_mpa : float
            Mean effective pressure (MPa) - typical 1.0-1.5 for diesel
        cylinders : int
            Number of cylinders
        L_D_ratio : float
            Stroke/Bore ratio (typical 1.0-1.3)
        
        Returns:
        --------
        DieselCycle : DieselCycle instance with calculated bore/stroke
        """
        # Power per cylinder
        power_per_cyl = power_kw * 1000 / cylinders
        
        # Strokes per second (4-stroke: power every 2 revolutions)
        strokes_per_sec = rpm / 120
        mep_pa = mep_mpa * 1e6
        
        # L × A = Power / (MEP × strokes/sec)
        LA_m3 = power_per_cyl / (mep_pa * strokes_per_sec)
        LA_mm3 = LA_m3 * 1e9
        
        # Calculate bore and stroke
        bore_mm = ((4 * LA_mm3) / (L_D_ratio * math.pi)) ** (1/3)
        stroke_mm = L_D_ratio * bore_mm
        
        # Create instance with calculated dimensions
        return cls(
            bore_mm=bore_mm,
            stroke_mm=stroke_mm,
            compression_ratio=compression_ratio,
            cutoff_ratio=cutoff_ratio,
        )
    
    def state1_intake(self) -> StatePoint:
        return StatePoint(
            pressure_pa=self.inlet_pressure_kpa * 1000,
            volume_m3=self.total_volume_m3,
            temperature_k=self.inlet_temperature_k,
            mass_kg=self.mass_kg,
            fluid=self.fluid,
        )
    
    def state2_compression(self) -> StatePoint:
        s1 = self.state1_intake()
        P2 = s1.pressure_pa * (self.compression_ratio ** self.fluid.gamma)
        V2 = s1.volume_m3 / self.compression_ratio
        T2 = s1.temperature_k * (self.compression_ratio ** (self.fluid.gamma - 1))
        return StatePoint(P2, V2, T2, self.mass_kg, self.fluid)
    
    def state3_combustion(self) -> StatePoint:
        s2 = self.state2_compression()
        P3 = s2.pressure_pa  # Constant pressure
        V3 = s2.volume_m3 * self.cutoff_ratio
        T3 = s2.temperature_k * self.cutoff_ratio
        return StatePoint(P3, V3, T3, self.mass_kg, self.fluid)
    
    def state4_expansion(self) -> StatePoint:
        s3 = self.state3_combustion()
        s1 = self.state1_intake()
        expansion_ratio = s1.volume_m3 / s3.volume_m3
        P4 = s3.pressure_pa / (expansion_ratio ** self.fluid.gamma)
        V4 = s1.volume_m3
        T4 = s3.temperature_k / (expansion_ratio ** (self.fluid.gamma - 1))
        return StatePoint(P4, V4, T4, self.mass_kg, self.fluid)
    
    @property
    def heat_added_j(self) -> float:
        s2 = self.state2_compression()
        s3 = self.state3_combustion()
        return self.mass_kg * self.fluid.cp_j_kgk * (s3.temperature_k - s2.temperature_k)
    
    @property
    def heat_rejected_j(self) -> float:
        s1 = self.state1_intake()
        s4 = self.state4_expansion()
        return self.mass_kg * self.fluid.cv_j_kgk * (s4.temperature_k - s1.temperature_k)
    
    @property
    def work_net_j(self) -> float:
        return self.heat_added_j - self.heat_rejected_j
    
    @property
    def thermal_efficiency(self) -> float:
        term1 = 1 / (self.compression_ratio ** (self.fluid.gamma - 1))
        term2 = (self.cutoff_ratio ** self.fluid.gamma - 1) / (self.fluid.gamma * (self.cutoff_ratio - 1))
        return 1 - term1 * term2
    
    @property
    def actual_efficiency(self) -> float:
        return self.thermal_efficiency * 0.88
    
    @property
    def mean_effective_pressure_mpa(self) -> float:
        return self.work_net_j / self.swept_volume_m3 / 1e6
    
    def power_kw(self, cylinders: int = 4, rpm: float = 3000) -> float:
        cycles_per_sec = (rpm / 60) * 0.5
        return self.work_net_j * cylinders * cycles_per_sec / 1000
    
    def print_report(self):
        s1 = self.state1_intake()
        s2 = self.state2_compression()
        s3 = self.state3_combustion()
        s4 = self.state4_expansion()
        
        print("=" * 75)
        print("DIESEL CYCLE ANALYSIS - Compression Ignition Engine")
        print("=" * 75)
        
        print(f"\n📌 ENGINE PARAMETERS:")
        print(f"   Bore: {self.bore_mm:.1f} mm")
        print(f"   Stroke: {self.stroke_mm:.1f} mm")
        print(f"   Compression ratio: {self.compression_ratio:.1f}:1")
        print(f"   Cutoff ratio: {self.cutoff_ratio:.2f}")
        print(f"   Displacement: {self.swept_volume_cc:.1f} cc")
        
        print(f"\n📍 STATE POINTS:")
        print(f"   State 1: ", end="")
        s1.print()
        print(f"   State 2: ", end="")
        s2.print()
        print(f"   State 3: ", end="")
        s3.print()
        print(f"   State 4: ", end="")
        s4.print()
        
        print(f"\n⚡ CYCLE PERFORMANCE:")
        print(f"   Heat added (Q_in): {self.heat_added_j:.1f} J")
        print(f"   Heat rejected (Q_out): {self.heat_rejected_j:.1f} J")
        print(f"   Net work (W_net): {self.work_net_j:.1f} J")
        print(f"   Thermal efficiency: {self.thermal_efficiency * 100:.2f}%")
        print(f"   Actual efficiency: {self.actual_efficiency * 100:.2f}%")
        print(f"   Mean effective pressure: {self.mean_effective_pressure_mpa:.2f} MPa")
        
        print("=" * 75)


# ============================================================================
# EXAMPLE USAGE
# ============================================================================

if __name__ == "__main__":
    print("=" * 75)
    print("COMPLETE ENGINE CYCLE ANALYSIS MODULE")
    print("=" * 75)
    
    # EXAMPLE 1: Design from Power (START HERE!)
    print("\n" + "🔧" * 35)
    print("EXAMPLE 1: DESIGN FROM POWER REQUIREMENT")
    print("🔧" * 35)
    
    # Otto cycle - you only need power and RPM!
    otto = OttoCycle.from_power(
        power_kw=150,
        rpm=6500,
        compression_ratio=10.5,
        mep_mpa=1.2,
        cylinders=4,
    )
    
    print(f"\n📊 OTTO CYCLE (Gasoline):")
    print(f"   Bore: {otto.bore_mm:.1f} mm")
    print(f"   Stroke: {otto.stroke_mm:.1f} mm")
    print(f"   Displacement: {otto.swept_volume_cc * 4 / 1000:.1f} L")
    print(f"   Thermal efficiency: {otto.thermal_efficiency*100:.1f}%")
    print(f"   Power at 6500 RPM: {otto.power_kw(cylinders=4, rpm=6500):.1f} kW")
    
    # Diesel cycle
    diesel = DieselCycle.from_power(
        power_kw=150,
        rpm=4000,
        compression_ratio=18.0,
        cutoff_ratio=2.0,
        mep_mpa=1.5,
        cylinders=4,
    )
    
    print(f"\n📊 DIESEL CYCLE:")
    print(f"   Bore: {diesel.bore_mm:.1f} mm")
    print(f"   Stroke: {diesel.stroke_mm:.1f} mm")
    print(f"   Displacement: {diesel.swept_volume_cc * 4 / 1000:.1f} L")
    print(f"   Thermal efficiency: {diesel.thermal_efficiency*100:.1f}%")
    print(f"   Power at 4000 RPM: {diesel.power_kw(cylinders=4, rpm=4000):.1f} kW")
    
    # EXAMPLE 2: Full Otto Cycle Report
    print("\n" + "🔧" * 35)
    print("EXAMPLE 2: FULL OTTO CYCLE REPORT")
    print("🔧" * 35)
    
    otto_full = OttoCycle(
        bore_mm=85.0,
        stroke_mm=88.0,
        compression_ratio=10.5,
        peak_pressure_mpa=6.0,
    )
    otto_full.print_report()
    
    # EXAMPLE 3: Full Diesel Cycle Report
    print("\n" + "🔧" * 35)
    print("EXAMPLE 3: FULL DIESEL CYCLE REPORT")
    print("🔧" * 35)
    
    diesel_full = DieselCycle(
        bore_mm=85.0,
        stroke_mm=88.0,
        compression_ratio=18.0,
        cutoff_ratio=2.0,)
    diesel_full.print_report()
    
    print("\n" + "=" * 75)
    print("✅ Cycle module ready for engine design from scratch!")
    print("=" * 75)