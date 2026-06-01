"""
cycle.py - Engine Cycles: Otto and Diesel Cycle Analysis

Based on Machine Design textbook and Thermodynamics principles
Sections covered:
- Air-standard cycles
- Otto cycle (spark ignition)
- Diesel cycle (compression ignition)
- P-V and T-S diagrams
- Efficiency calculations
- Mean effective pressure
- Work output analysis
- Heat transfer calculations
"""

import math


class WorkingFluid:
    """Working fluid properties for engine cycle analysis."""
    
    # Air properties (typical for engine cycle analysis)
    AIR_PROPERTIES = {
        "R_specific_j_kgk": 287,      # Specific gas constant (J/kg·K)
        "cp_j_kgk": 1005,              # Specific heat at constant pressure (J/kg·K)
        "cv_j_kgk": 718,               # Specific heat at constant volume (J/kg·K)
        "gamma": 1.4,                  # Ratio of specific heats (cp/cv)
        "molar_mass_kg_kmol": 28.97,   # Molar mass (kg/kmol)
    }
    
    def __init__(self, gamma=1.4, gas_constant=287, cp=1005, cv=718):
        """
        Parameters:
        -----------
        gamma : float
            Ratio of specific heats (cp/cv) - typically 1.4 for air
        gas_constant : float
            Specific gas constant (R) in J/kg·K
        cp : float
            Specific heat at constant pressure (J/kg·K)
        cv : float
            Specific heat at constant volume (J/kg·K)
        """
        self.gamma = gamma
        self.R = gas_constant
        self.cp = cp
        self.cv = cv
    
    @classmethod
    def air(cls):
        """Create working fluid with air properties."""
        return cls(
            gamma=cls.AIR_PROPERTIES["gamma"],
            gas_constant=cls.AIR_PROPERTIES["R_specific_j_kgk"],
            cp=cls.AIR_PROPERTIES["cp_j_kgk"],
            cv=cls.AIR_PROPERTIES["cv_j_kgk"]
        )
    
    @classmethod
    def custom(cls, gamma, gas_constant, cp, cv):
        """Create custom working fluid."""
        return cls(gamma=gamma, gas_constant=gas_constant, cp=cp, cv=cv)


class StatePoint:
    """Thermodynamic state point (P, V, T)."""
    
    def __init__(self, pressure_pa, volume_m3, temperature_k, mass_kg=None):
        """
        Parameters:
        -----------
        pressure_pa : float
            Absolute pressure (Pa)
        volume_m3 : float
            Volume (m³)
        temperature_k : float
            Absolute temperature (K)
        mass_kg : float, optional
            Mass of working fluid (kg)
        """
        self.P = pressure_pa
        self.V = volume_m3
        self.T = temperature_k
        self.m = mass_kg
    
    @property
    def pressure_mpa(self):
        """Pressure in MPa."""
        return self.P / 1e6
    
    @property
    def pressure_bar(self):
        """Pressure in bar."""
        return self.P / 1e5
    
    @property
    def volume_cc(self):
        """Volume in cubic centimeters (cc)."""
        return self.V * 1e6
    
    def __repr__(self):
        return f"StatePoint(P={self.P/1e3:.1f}kPa, V={self.V*1e6:.1f}cc, T={self.T:.1f}K)"


class OttoCycle:
    """Chapter 32: Otto cycle for spark ignition engines."""
    
    def __init__(self, bore_mm, stroke_mm, compression_ratio, clearance_volume_cc=None,
                 inlet_pressure_kpa=101.3, inlet_temperature_k=298,
                 peak_pressure_mpa=None, peak_temperature_k=None,
                 working_fluid=None):
        """
        Parameters:
        -----------
        bore_mm : float
            Cylinder bore diameter (mm)
        stroke_mm : float
            Piston stroke (mm)
        compression_ratio : float
            Compression ratio (V1/V2) - typically 8-12 for gasoline
        clearance_volume_cc : float, optional
            Clearance volume (cc) - calculated if not provided
        inlet_pressure_kpa : float
            Intake manifold pressure (kPa) - typically 101.3 for naturally aspirated
        inlet_temperature_k : float
            Intake air temperature (K) - typically 298-320 K
        peak_pressure_mpa : float, optional
            Peak combustion pressure (MPa) - calculated if not provided
        peak_temperature_k : float, optional
            Peak combustion temperature (K) - calculated if not provided
        working_fluid : WorkingFluid, optional
            Working fluid properties (default: air)
        """
        self.bore_mm = bore_mm
        self.stroke_mm = stroke_mm
        self.r = compression_ratio
        self.P1_pa = inlet_pressure_kpa * 1000
        self.T1_K = inlet_temperature_k
        self.peak_pressure_mpa = peak_pressure_mpa
        self.peak_temperature_K = peak_temperature_k
        
        # Working fluid
        self.fluid = working_fluid or WorkingFluid.air()
        
        # Calculate volumes
        self.swept_volume_cc = math.pi * (bore_mm ** 2) / 4 * stroke_mm / 1000
        self.swept_volume_m3 = self.swept_volume_cc / 1e6
        
        if clearance_volume_cc:
            self.clearance_volume_cc = clearance_volume_cc
        else:
            self.clearance_volume_cc = self.swept_volume_cc / (compression_ratio - 1)
        
        self.clearance_volume_m3 = self.clearance_volume_cc / 1e6
        self.total_volume_cc = self.swept_volume_cc + self.clearance_volume_cc
        self.total_volume_m3 = self.total_volume_cc / 1e6
        
        # Mass of working fluid (from ideal gas law at inlet)
        self.mass_kg = (self.P1_pa * self.total_volume_m3) / (self.fluid.R * self.T1_K)
    
    def state_1_intake_bdc(self):
        """
        State 1: Start of compression stroke (BDC, intake valve closes).
        
        P₁ = intake pressure
        V₁ = total volume (swept + clearance)
        T₁ = intake temperature
        """
        return StatePoint(
            pressure_pa=self.P1_pa,
            volume_m3=self.total_volume_m3,
            temperature_k=self.T1_K,
            mass_kg=self.mass_kg
        )
    
    def state_2_compression_tdc(self):
        """
        State 2: End of compression stroke (TDC).
        
        Isentropic compression: P₂ = P₁ × r^γ
                              V₂ = V₁ / r
                              T₂ = T₁ × r^(γ-1)
        """
        state1 = self.state_1_intake_bdc()
        
        P2_pa = state1.P * (self.r ** self.fluid.gamma)
        V2_m3 = state1.V / self.r
        T2_K = state1.T * (self.r ** (self.fluid.gamma - 1))
        
        return StatePoint(P2_pa, V2_m3, T2_K, self.mass_kg)
    
    def state_3_combustion(self):
        """
        State 3: After heat addition (constant volume combustion).
        
        V₃ = V₂ (constant volume)
        P₃ = peak combustion pressure
        T₃ = P₃ × V₃ / (m × R)
        """
        state2 = self.state_2_compression_tdc()
        
        # Calculate peak pressure if not provided
        if self.peak_pressure_mpa:
            P3_pa = self.peak_pressure_mpa * 1e6
        else:
            # Estimate: 4-6 times compression pressure for gasoline
            P3_pa = state2.P * 5.0
        
        V3_m3 = state2.V
        
        # Temperature from ideal gas law
        T3_K = (P3_pa * V3_m3) / (self.mass_kg * self.fluid.R)
        
        return StatePoint(P3_pa, V3_m3, T3_K, self.mass_kg)
    
    def state_4_expansion_bdc(self):
        """
        State 4: End of expansion stroke (BDC, exhaust valve opens).
        
        Isentropic expansion: P₄ = P₃ / r^γ
                             V₄ = V₁ (total volume)
                             T₄ = T₃ / r^(γ-1)
        """
        state3 = self.state_3_combustion()
        state1 = self.state_1_intake_bdc()
        
        P4_pa = state3.P / (self.r ** self.fluid.gamma)
        V4_m3 = state1.V
        T4_K = state3.T / (self.r ** (self.fluid.gamma - 1))
        
        return StatePoint(P4_pa, V4_m3, T4_K, self.mass_kg)
    
    def heat_added_j(self):
        """
        Heat added during combustion (Q_in).
        
        Q_in = m × c_v × (T₃ - T₂)
        """
        state2 = self.state_2_compression_tdc()
        state3 = self.state_3_combustion()
        
        Q_in = self.mass_kg * self.fluid.cv * (state3.T - state2.T)
        return Q_in
    
    def heat_rejected_j(self):
        """
        Heat rejected during exhaust (Q_out).
        
        Q_out = m × c_v × (T₄ - T₁)
        """
        state1 = self.state_1_intake_bdc()
        state4 = self.state_4_expansion_bdc()
        
        Q_out = self.mass_kg * self.fluid.cv * (state4.T - state1.T)
        return Q_out
    
    def work_net_j(self):
        """
        Net work output per cycle.
        
        W_net = Q_in - Q_out
        """
        return self.heat_added_j() - self.heat_rejected_j()
    
    def efficiency(self):
        """
        Otto cycle thermal efficiency.
        
        η = 1 - 1 / r^(γ-1)
        """
        return 1 - (1 / (self.r ** (self.fluid.gamma - 1)))
    
    def mean_effective_pressure_pa(self):
        """
        Mean effective pressure (MEP).
        
        MEP = W_net / V_swept
        """
        W_net = self.work_net_j()
        return W_net / self.swept_volume_m3
    
    def mean_effective_pressure_mpa(self):
        """Mean effective pressure in MPa."""
        return self.mean_effective_pressure_pa() / 1e6
    
    def power_kw(self, rpm, cylinders=4, cycles_per_revolution=0.5):
        """
        Engine power output.
        
        Power = W_net × (rpm/60) × cylinders × cycles_per_revolution
        
        For 4-stroke: cycles_per_revolution = 0.5
        For 2-stroke: cycles_per_revolution = 1.0
        """
        cycles_per_second = (rpm / 60) * cycles_per_revolution
        power_w = self.work_net_j() * cylinders * cycles_per_second
        return power_w / 1000
    
    def get_all_states(self):
        """
        Get all four states of the Otto cycle.
        
        Returns:
        --------
        dict : States 1, 2, 3, 4 with P, V, T
        """
        return {
            "state1": self.state_1_intake_bdc(),
            "state2": self.state_2_compression_tdc(),
            "state3": self.state_3_combustion(),
            "state4": self.state_4_expansion_bdc(),
        }
    
    def print_cycle_report(self):
        """Print detailed cycle analysis report."""
        states = self.get_all_states()
        
        print("=" * 70)
        print("OTTO CYCLE ANALYSIS - Spark Ignition Engine")
        print("=" * 70)
        
        print(f"\n📌 ENGINE PARAMETERS:")
        print(f"   Bore: {self.bore_mm:.1f} mm")
        print(f"   Stroke: {self.stroke_mm:.1f} mm")
        print(f"   Compression ratio: {self.r:.1f}:1")
        print(f"   Swept volume: {self.swept_volume_cc:.1f} cc")
        print(f"   Clearance volume: {self.clearance_volume_cc:.1f} cc")
        print(f"   Total volume: {self.total_volume_cc:.1f} cc")
        
        print(f"\n🌡️ WORKING FLUID:")
        print(f"   Mass of air: {self.mass_kg * 1000:.2f} g")
        print(f"   γ (cp/cv): {self.fluid.gamma:.3f}")
        print(f"   R: {self.fluid.R:.1f} J/kg·K")
        
        print(f"\n📍 STATE POINTS:")
        print(f"   State 1 (Intake BDC):  P={states['state1'].pressure_bar:.2f} bar, "
              f"T={states['state1'].T:.1f}K, V={states['state1'].volume_cc:.1f}cc")
        print(f"   State 2 (Compression TDC): P={states['state2'].pressure_bar:.2f} bar, "
              f"T={states['state2'].T:.1f}K, V={states['state2'].volume_cc:.1f}cc")
        print(f"   State 3 (Combustion): P={states['state3'].pressure_bar:.2f} bar, "
              f"T={states['state3'].T:.1f}K, V={states['state3'].volume_cc:.1f}cc")
        print(f"   State 4 (Expansion BDC): P={states['state4'].pressure_bar:.2f} bar, "
              f"T={states['state4'].T:.1f}K, V={states['state4'].volume_cc:.1f}cc")
        
        print(f"\n⚡ CYCLE PERFORMANCE:")
        print(f"   Heat added (Q_in): {self.heat_added_j():.1f} J")
        print(f"   Heat rejected (Q_out): {self.heat_rejected_j():.1f} J")
        print(f"   Net work (W_net): {self.work_net_j():.1f} J")
        print(f"   Thermal efficiency (η): {self.efficiency() * 100:.2f}%")
        print(f"   Mean effective pressure: {self.mean_effective_pressure_mpa():.2f} MPa")
        
        print(f"\n🔧 ENGINE POWER (4-cylinder):")
        for rpm in [2000, 4000, 6000]:
            power = self.power_kw(rpm, cylinders=4)
            print(f"   {rpm} RPM: {power:.1f} kW ({power * 1.341:.1f} HP)")
        
        print("=" * 70)
        
        return states


class DieselCycle:
    """Chapter 32: Diesel cycle for compression ignition engines."""
    
    def __init__(self, bore_mm, stroke_mm, compression_ratio, cutoff_ratio,
                 inlet_pressure_kpa=101.3, inlet_temperature_k=298,
                 peak_pressure_mpa=None, working_fluid=None):
        """
        Parameters:
        -----------
        bore_mm : float
            Cylinder bore diameter (mm)
        stroke_mm : float
            Piston stroke (mm)
        compression_ratio : float
            Compression ratio (V1/V2) - typically 16-22 for diesel
        cutoff_ratio : float
            Cutoff ratio (V3/V2) - typically 1.5-2.5
        inlet_pressure_kpa : float
            Intake manifold pressure (kPa)
        inlet_temperature_k : float
            Intake air temperature (K)
        peak_pressure_mpa : float, optional
            Peak combustion pressure (MPa)
        working_fluid : WorkingFluid, optional
            Working fluid properties
        """
        self.bore_mm = bore_mm
        self.stroke_mm = stroke_mm
        self.r = compression_ratio
        self.beta = cutoff_ratio  # Cutoff ratio (V3/V2)
        self.P1_pa = inlet_pressure_kpa * 1000
        self.T1_K = inlet_temperature_k
        self.peak_pressure_mpa = peak_pressure_mpa
        
        # Working fluid
        self.fluid = working_fluid or WorkingFluid.air()
        
        # Calculate volumes
        self.swept_volume_cc = math.pi * (bore_mm ** 2) / 4 * stroke_mm / 1000
        self.swept_volume_m3 = self.swept_volume_cc / 1e6
        self.clearance_volume_cc = self.swept_volume_cc / (compression_ratio - 1)
        self.clearance_volume_m3 = self.clearance_volume_cc / 1e6
        self.total_volume_cc = self.swept_volume_cc + self.clearance_volume_cc
        self.total_volume_m3 = self.total_volume_cc / 1e6
        
        # Mass of working fluid
        self.mass_kg = (self.P1_pa * self.total_volume_m3) / (self.fluid.R * self.T1_K)
    
    def state_1_intake_bdc(self):
        """State 1: Start of compression (BDC)."""
        return StatePoint(
            pressure_pa=self.P1_pa,
            volume_m3=self.total_volume_m3,
            temperature_k=self.T1_K,
            mass_kg=self.mass_kg
        )
    
    def state_2_compression_tdc(self):
        """State 2: End of compression (TDC) - isentropic compression."""
        state1 = self.state_1_intake_bdc()
        
        P2_pa = state1.P * (self.r ** self.fluid.gamma)
        V2_m3 = state1.V / self.r
        T2_K = state1.T * (self.r ** (self.fluid.gamma - 1))
        
        return StatePoint(P2_pa, V2_m3, T2_K, self.mass_kg)
    
    def state_3_combustion_end(self):
        """
        State 3: End of combustion - constant pressure heat addition.
        
        V₃ = V₂ × β (expansion during combustion)
        P₃ = P₂ (constant pressure)
        T₃ = T₂ × β
        """
        state2 = self.state_2_compression_tdc()
        
        P3_pa = state2.P
        V3_m3 = state2.V * self.beta
        T3_K = state2.T * self.beta
        
        return StatePoint(P3_pa, V3_m3, T3_K, self.mass_kg)
    
    def state_4_expansion_bdc(self):
        """
        State 4: End of expansion - isentropic expansion.
        
        V₄ = V₁ (total volume)
        P₄ = P₃ × (V₃/V₄)^γ
        T₄ = T₃ × (V₃/V₄)^(γ-1)
        """
        state1 = self.state_1_intake_bdc()
        state3 = self.state_3_combustion_end()
        
        V4_m3 = state1.V
        expansion_ratio = V4_m3 / state3.V
        
        P4_pa = state3.P / (expansion_ratio ** self.fluid.gamma)
        T4_K = state3.T / (expansion_ratio ** (self.fluid.gamma - 1))
        
        return StatePoint(P4_pa, V4_m3, T4_K, self.mass_kg)
    
    def heat_added_j(self):
        """
        Heat added during combustion (constant pressure).
        
        Q_in = m × c_p × (T₃ - T₂)
        """
        state2 = self.state_2_compression_tdc()
        state3 = self.state_3_combustion_end()
        
        Q_in = self.mass_kg * self.fluid.cp * (state3.T - state2.T)
        return Q_in
    
    def heat_rejected_j(self):
        """
        Heat rejected during exhaust (constant volume).
        
        Q_out = m × c_v × (T₄ - T₁)
        """
        state1 = self.state_1_intake_bdc()
        state4 = self.state_4_expansion_bdc()
        
        Q_out = self.mass_kg * self.fluid.cv * (state4.T - state1.T)
        return Q_out
    
    def work_net_j(self):
        """Net work output per cycle."""
        return self.heat_added_j() - self.heat_rejected_j()
    
    def efficiency(self):
        """
        Diesel cycle thermal efficiency.
        
        η = 1 - [1/(r^(γ-1))] × [(β^γ - 1)/(γ(β - 1))]
        """
        term1 = 1 / (self.r ** (self.fluid.gamma - 1))
        term2 = (self.beta ** self.fluid.gamma - 1) / (self.fluid.gamma * (self.beta - 1))
        return 1 - (term1 * term2)
    
    def mean_effective_pressure_pa(self):
        """Mean effective pressure (MEP)."""
        return self.work_net_j() / self.swept_volume_m3
    
    def mean_effective_pressure_mpa(self):
        """Mean effective pressure in MPa."""
        return self.mean_effective_pressure_pa() / 1e6
    
    def power_kw(self, rpm, cylinders=4, cycles_per_revolution=0.5):
        """Engine power output."""
        cycles_per_second = (rpm / 60) * cycles_per_revolution
        power_w = self.work_net_j() * cylinders * cycles_per_second
        return power_w / 1000
    
    def get_all_states(self):
        """Get all four states of the Diesel cycle."""
        return {
            "state1": self.state_1_intake_bdc(),
            "state2": self.state_2_compression_tdc(),
            "state3": self.state_3_combustion_end(),
            "state4": self.state_4_expansion_bdc(),
        }
    
    def print_cycle_report(self):
        """Print detailed Diesel cycle analysis report."""
        states = self.get_all_states()
        
        print("=" * 70)
        print("DIESEL CYCLE ANALYSIS - Compression Ignition Engine")
        print("=" * 70)
        
        print(f"\n📌 ENGINE PARAMETERS:")
        print(f"   Bore: {self.bore_mm:.1f} mm")
        print(f"   Stroke: {self.stroke_mm:.1f} mm")
        print(f"   Compression ratio: {self.r:.1f}:1")
        print(f"   Cutoff ratio: {self.beta:.2f}")
        print(f"   Swept volume: {self.swept_volume_cc:.1f} cc")
        print(f"   Clearance volume: {self.clearance_volume_cc:.1f} cc")
        
        print(f"\n📍 STATE POINTS:")
        print(f"   State 1 (Intake BDC): P={states['state1'].pressure_bar:.2f} bar, "
              f"T={states['state1'].T:.1f}K")
        print(f"   State 2 (Compression TDC): P={states['state2'].pressure_bar:.2f} bar, "
              f"T={states['state2'].T:.1f}K")
        print(f"   State 3 (Combustion end): P={states['state3'].pressure_bar:.2f} bar, "
              f"T={states['state3'].T:.1f}K")
        print(f"   State 4 (Expansion BDC): P={states['state4'].pressure_bar:.2f} bar, "
              f"T={states['state4'].T:.1f}K")
        
        print(f"\n⚡ CYCLE PERFORMANCE:")
        print(f"   Heat added (Q_in): {self.heat_added_j():.1f} J")
        print(f"   Heat rejected (Q_out): {self.heat_rejected_j():.1f} J")
        print(f"   Net work (W_net): {self.work_net_j():.1f} J")
        print(f"   Thermal efficiency (η): {self.efficiency() * 100:.2f}%")
        print(f"   Mean effective pressure: {self.mean_effective_pressure_mpa():.2f} MPa")
        
        print("=" * 70)
        
        return states


class CycleComparison:
    """Compare Otto and Diesel cycles."""
    
    @staticmethod
    def compare(otto_cycle, diesel_cycle):
        """
        Compare Otto and Diesel cycle performance.
        
        Parameters:
        -----------
        otto_cycle : OttoCycle
            Otto cycle instance
        diesel_cycle : DieselCycle
            Diesel cycle instance
        """
        print("=" * 70)
        print("OTTO vs DIESEL CYCLE COMPARISON")
        print("=" * 70)
        
        print(f"\n{'Parameter':<30} {'Otto':>15} {'Diesel':>15} {'Difference':>15}")
        print("-" * 75)
        
        params = [
            ("Compression Ratio", f"{otto_cycle.r:.1f}", f"{diesel_cycle.r:.1f}"),
            ("Efficiency (%)", f"{otto_cycle.efficiency()*100:.1f}", 
             f"{diesel_cycle.efficiency()*100:.1f}"),
            ("MEP (MPa)", f"{otto_cycle.mean_effective_pressure_mpa():.2f}", 
             f"{diesel_cycle.mean_effective_pressure_mpa():.2f}"),
            ("Work per cycle (J)", f"{otto_cycle.work_net_j():.1f}", 
             f"{diesel_cycle.work_net_j():.1f}"),
        ]
        
        for name, otto_val, diesel_val in params:
            try:
                diff = float(diesel_val) - float(otto_val)
                diff_str = f"{diff:+.1f}"
            except:
                diff_str = "N/A"
            
            print(f"{name:<30} {otto_val:>15} {diesel_val:>15} {diff_str:>15}")
        
        print("=" * 70)
        
        # Recommendations
        print("\n📌 RECOMMENDATIONS:")
        if otto_cycle.efficiency() > diesel_cycle.efficiency():
            print("   → Otto cycle has higher thermal efficiency")
            print("   → Better for light-duty, high-speed applications (gasoline engines)")
        else:
            print("   → Diesel cycle has higher thermal efficiency")
            print("   → Better for heavy-duty, low-speed applications (diesel engines)")
        
        if otto_cycle.mean_effective_pressure_mpa() > diesel_cycle.mean_effective_pressure_mpa():
            print("   → Otto cycle produces higher power per displacement")
        else:
            print("   → Diesel cycle produces higher torque per displacement")


# ============================================================================
# Example usage
# ============================================================================

if __name__ == "__main__":
    print("=" * 70)
    print("ENGINE CYCLE ANALYSIS - Machine Design Textbook")
    print("=" * 70)
    
    # Example 1: Otto Cycle (Gasoline Engine)
    print("\n📌 EXAMPLE 1: 2.0L Gasoline Engine (Otto Cycle)")
    print("-" * 50)
    
    otto = OttoCycle(
        bore_mm=85,
        stroke_mm=88,
        compression_ratio=10.5,
        inlet_pressure_kpa=101.3,
        inlet_temperature_k=298,
        peak_pressure_mpa=6.0  # 60 bar peak pressure
    )
    otto.print_cycle_report()
    
    # Example 2: Diesel Cycle
    print("\n\n📌 EXAMPLE 2: 2.0L Diesel Engine (Diesel Cycle)")
    print("-" * 50)
    
    diesel = DieselCycle(
        bore_mm=85,
        stroke_mm=88,
        compression_ratio=18.0,
        cutoff_ratio=2.0,
        inlet_pressure_kpa=150,  # Turbocharged
        inlet_temperature_k=320
    )
    diesel.print_cycle_report()
    
    # Example 3: Comparison
    print("\n\n")
    CycleComparison.compare(otto, diesel)
    
    print("\n" + "=" * 70)
    print("Cycle analysis ready for engine integration.")
    print("=" * 70)