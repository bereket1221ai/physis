"""
crankshaft.py - Complete Crankshaft Design for IC Engines
"""

import math
from dataclasses import dataclass
from typing import Dict, Optional


# ============================================================================
# MATERIALS
# ============================================================================

@dataclass(frozen=True)
class CrankshaftMaterial:
    name: str
    density_kg_m3: float
    ultimate_tensile_mpa: float
    yield_strength_mpa: float
    endurance_limit_bending_mpa: float
    endurance_limit_shear_mpa: float
    allowable_bending_mpa: float
    allowable_shear_mpa: float
    youngs_modulus_gpa: float
    hardness_hb: float


CRANKSHAFT_MATERIALS = {
    "Chrome Nickel Steel": CrankshaftMaterial(
        name="Chrome Nickel Steel", density_kg_m3=7850, ultimate_tensile_mpa=900,
        yield_strength_mpa=750, endurance_limit_bending_mpa=525,
        endurance_limit_shear_mpa=290, allowable_bending_mpa=175,
        allowable_shear_mpa=97, youngs_modulus_gpa=205, hardness_hb=350,
    ),
    "Carbon Steel": CrankshaftMaterial(
        name="Carbon Steel", density_kg_m3=7850, ultimate_tensile_mpa=600,
        yield_strength_mpa=450, endurance_limit_bending_mpa=225,
        endurance_limit_shear_mpa=124, allowable_bending_mpa=75,
        allowable_shear_mpa=42, youngs_modulus_gpa=200, hardness_hb=250,
    ),
}


def get_crankshaft_material(name: str):
    return CRANKSHAFT_MATERIALS[name]


# ============================================================================
# LOADS
# ============================================================================

@dataclass(frozen=True)
class CrankshaftLoads:
    bore_mm: float
    stroke_mm: float
    p_dead_mpa: float
    p_torque_mpa: float
    flywheel_weight_N: float
    belt_pull_N: float
    l_r_ratio: float = 5.0
    theta_deg: float = 35.0

    @property
    def crank_radius_mm(self) -> float:
        return self.stroke_mm / 2.0

    @property
    def crank_radius_m(self) -> float:
        return self.stroke_mm / 2000.0

    @property
    def piston_area_mm2(self) -> float:
        return math.pi * self.bore_mm ** 2 / 4.0

    @property
    def FP_dead_N(self) -> float:
        return self.piston_area_mm2 * self.p_dead_mpa

    @property
    def FP_dead_kN(self) -> float:
        return self.FP_dead_N / 1000

    def evaluate_torque_forces(self):
        theta_rad = math.radians(self.theta_deg)
        sin_phi = math.sin(theta_rad) / self.l_r_ratio
        phi_rad = math.asin(max(-0.5, min(0.5, sin_phi)))
        FQ = self.FP_dead_N / math.cos(phi_rad)
        FT = FQ * math.sin(theta_rad + phi_rad)
        FR = FQ * math.cos(theta_rad + phi_rad)
        return {"FQ_N": FQ, "FT_N": FT, "FR_N": FR, "phi_deg": math.degrees(phi_rad)}


# ============================================================================
# FATIGUE
# ============================================================================

class CrankshaftFatigue:
    def __init__(self, material, bending_stress_mpa, shear_stress_mpa):
        self.material = material
        self.bending = bending_stress_mpa
        self.shear = shear_stress_mpa
    
    def goodman_fos(self):
        vm = math.sqrt(self.bending**2 + 3 * self.shear**2)
        if vm <= 0:
            return 999
        return self.material.endurance_limit_bending_mpa / vm


# ============================================================================
# RESULT
# ============================================================================

@dataclass
class CentreCrankshaftResult:
    bearing_span_mm: float
    crankpin_diameter_mm: float
    crankpin_length_mm: float
    web_thickness_mm: float
    web_width_mm: float
    shaft_flywheel_diameter_mm: float
    shaft_junction_diameter_mm: float
    gas_force_kN: float
    tangential_force_kN: float
    radial_force_kN: float
    bending_stress_mpa: float
    shear_stress_mpa: float
    von_mises_stress_mpa: float
    goodman_fos: float
    material_name: str
    mass_kg: float
    
    def print_report(self):
        print("=" * 75)
        print("CENTRE CRANKSHAFT DESIGN REPORT")
        print("=" * 75)
        print(f"\n📐 DIMENSIONS:")
        print(f"   Bearing span: {self.bearing_span_mm:.1f} mm")
        print(f"   Crankpin diameter: {self.crankpin_diameter_mm:.2f} mm")
        print(f"   Crankpin length: {self.crankpin_length_mm:.2f} mm")
        print(f"   Web thickness: {self.web_thickness_mm:.2f} mm")
        print(f"   Web width: {self.web_width_mm:.2f} mm")
        print(f"   Flywheel shaft diameter: {self.shaft_flywheel_diameter_mm:.2f} mm")
        print(f"   Junction shaft diameter: {self.shaft_junction_diameter_mm:.2f} mm")
        print(f"\n⚡ FORCES:")
        print(f"   Gas force: {self.gas_force_kN:.1f} kN")
        print(f"   Tangential force: {self.tangential_force_kN:.1f} kN")
        print(f"   Radial force: {self.radial_force_kN:.1f} kN")
        print(f"\n📊 STRESS ANALYSIS:")
        print(f"   Bending stress: {self.bending_stress_mpa:.1f} MPa")
        print(f"   Shear stress: {self.shear_stress_mpa:.1f} MPa")
        print(f"   Von Mises stress: {self.von_mises_stress_mpa:.1f} MPa")
        print(f"\n🔄 FATIGUE ANALYSIS:")
        print(f"   Goodman FOS: {self.goodman_fos:.2f}")
        print(f"\n🏗️ MATERIAL:")
        print(f"   Material: {self.material_name}")
        print(f"   Mass: {self.mass_kg:.2f} kg")
        print("=" * 75)


# ============================================================================
# DESIGNER
# ============================================================================

class CentreCrankshaftDesigner:
    def __init__(self, loads: CrankshaftLoads, material_name: str = "Carbon Steel",
                 sigma_b_mpa: Optional[float] = None, tau_mpa: Optional[float] = None,
                 pb_mpa: float = 10.0):
        self.loads = loads
        self.material = get_crankshaft_material(material_name)
        self.sigma_b = sigma_b_mpa or self.material.allowable_bending_mpa
        self.tau = tau_mpa or self.material.allowable_shear_mpa
        self.pb = pb_mpa
        self.results = self._execute()
    
    def _execute(self):
        f = self.loads
        D = f.bore_mm
        r_mm = f.crank_radius_mm
        r_m = f.crank_radius_m
        
        b = 2.0 * D
        b1 = b2 = b / 2.0
        
        # Dead centre
        H1 = f.FP_dead_N * b2 / b
        MC = H1 * b1
        
        # Crankpin diameter
        dc = ((32.0 * MC) / (math.pi * self.sigma_b)) ** (1/3)
        lc = f.FP_dead_N / (dc * self.pb)
        t = 0.65 * dc + 6.35
        w = 1.125 * dc + 12.7
        
        # Flywheel shaft
        V3 = f.flywheel_weight_N / 2.0
        H3p = f.belt_pull_N / 2.0
        c1 = 1.5 * D
        MS = math.sqrt((V3 * c1)**2 + (H3p * c1)**2)
        ds = ((32.0 * MS) / (math.pi * self.sigma_b)) ** (1/3)
        
        # Max torque
        tf = f.evaluate_torque_forces()
        FT = tf["FT_N"]
        FR = tf["FR_N"]
        
        HT1 = FT * b2 / b
        HR1 = FR * b2 / b
        
        R1 = math.sqrt(HT1**2 + HR1**2)
        MS1 = abs(R1 * (b2 + lc/2 + t/2) - tf["FQ_N"] * (lc/2 + t/2))
        TS = FT * r_mm
        Te = math.sqrt(MS1**2 + TS**2)
        ds1 = ((16.0 * Te) / (math.pi * self.tau)) ** (1/3)
        
        Te_fly = math.sqrt(MS**2 + TS**2)
        ds_torque = ((16.0 * Te_fly) / (math.pi * self.tau)) ** (1/3)
        ds = max(ds, ds_torque)
        
        # ================================================================
        # ACTUAL STRESS CALCULATIONS (IN MPa)
        # ================================================================
        
        # Convert to meters for stress calculation
        dc_m = dc / 1000
        MC_Nm = MC / 1000  # Convert to N-m
        
        # Bending stress
        I = math.pi * dc_m**4 / 64
        c_m = dc_m / 2
        bending_stress = (MC_Nm * c_m) / I / 1e6
        
        # Shear stress (torsion)
        J = math.pi * dc_m**4 / 32
        TC_Nm = HT1 * (r_mm / 1000)
        shear_stress = (TC_Nm * c_m) / J / 1e6
        
        # Von Mises
        vm = math.sqrt(bending_stress**2 + 3 * shear_stress**2)
        
        # Fatigue
        fatigue = CrankshaftFatigue(self.material, bending_stress, shear_stress)
        fos = fatigue.goodman_fos()
        
        # Mass
        vol = math.pi * (dc/2)**2 * lc + math.pi * (ds/2)**2 * b
        mass = vol / 1e9 * self.material.density_kg_m3
        
        return CentreCrankshaftResult(
            bearing_span_mm=b,
            crankpin_diameter_mm=dc,
            crankpin_length_mm=lc,
            web_thickness_mm=t,
            web_width_mm=w,
            shaft_flywheel_diameter_mm=ds,
            shaft_junction_diameter_mm=ds1,
            gas_force_kN=f.FP_dead_kN,
            tangential_force_kN=FT/1000,
            radial_force_kN=FR/1000,
            bending_stress_mpa=bending_stress,
            shear_stress_mpa=shear_stress,
            von_mises_stress_mpa=vm,
            goodman_fos=fos,
            material_name=self.material.name,
            mass_kg=mass,)
    
    def get_results(self):
        return self.results
    
    def print_report(self):
        self.results.print_report()


# ============================================================================
# TEST
# ============================================================================

if __name__ == "__main__":
    loads = CrankshaftLoads(
        bore_mm=350,
        stroke_mm=500,
        p_dead_mpa=3.5,
        p_torque_mpa=1.5,
        flywheel_weight_N=40000,
        belt_pull_N=5000,)

    crank = CentreCrankshaftDesigner(loads, material_name="Chrome Nickel Steel")
    crank.print_report()