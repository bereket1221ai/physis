"""
Engine Design Automation Library (EDAL) - Crankshaft Module
Implements the full analytical and empirical design procedure from Chapter 32
(Sections 32.16 - 32.21) for Centre and Side Crankshafts.
"""

import math
from dataclasses import dataclass, field
from typing import Dict, Any, Optional


@dataclass(frozen=True)
class CrankshaftLoads:
    """
    Evaluates and holds the engine force dynamics acting on the crankshaft assembly.
    Derived from Section 32.18 of the textbook methodology.
    """
    bore_mm: float
    stroke_mm: float
    p_dead_mpa: float          # Maximum gas pressure at dead centre
    p_torque_mpa: float        # Gas pressure at maximum torque position
    flywheel_weight_N: float
    belt_pull_N: float
    l_r_ratio: float = 5.0     # Connecting rod length to crank radius ratio (n)
    theta_deg: float = 35.0    # Crank angle for maximum twisting moment

    @property
    def crank_radius_mm(self) -> float:
        return self.stroke_mm / 2.0

    @property
    def piston_area_mm2(self) -> float:
        return (math.pi * (self.bore_mm ** 2)) / 4.0

    @property
    def FP_dead_N(self) -> float:
        """Piston gas force at dead centre position."""
        return self.piston_area_mm2 * self.p_dead_mpa

    @property
    def FP_torque_N(self) -> float:
        """Piston gas force at maximum torque position."""
        return self.piston_area_mm2 * self.p_torque_mpa

    def evaluate_torque_forces(self) -> Dict[str, float]:
        """Calculates oblique engine forces (FQ, FT, FR) for Case 2."""
        theta_rad = math.radians(self.theta_deg)
        # sin(phi) = sin(theta) / (l/r)
        sin_phi = math.sin(theta_rad) / self.l_r_ratio
        phi_rad = math.asin(min(1.0, max(-1.0, sin_phi)))
        
        # Force in connecting rod (FQ)
        FQ = self.FP_torque_N / math.cos(phi_rad)
        # Tangential force driving torque (FT)
        FT = FQ * math.sin(theta_rad + phi_rad)
        # Radial force squeezing down the crank web (FR)
        FR = FQ * math.cos(theta_rad + phi_rad)
        
        return {"FQ_N": FQ, "FT_N": FT, "FR_N": FR}


class CentreCrankshaftDesigner:
    """
    Automates Section 32.20 (Example 32.4) for a 3-bearing centre crankshaft.
    Includes geometric overlap loops and stress concentration integration.
    """
    def __init__(
        self, 
        loads: CrankshaftLoads, 
        sigma_b_mpa: float = 75.0, 
        tau_mpa: float = 35.0,
        pb_mpa: float = 10.0,
        fillet_concentration_factor: float = 1.8
    ):
        self.loads = loads
        self.sigma_b = sigma_b_mpa
        self.tau = tau_mpa
        self.pb = pb_mpa
        self.Kt = fillet_concentration_factor
        self.results: Dict[str, Any] = {}
        self._execute_design()

    def _execute_design(self):
        f = self.loads
        D = f.bore_mm
        r = f.crank_radius_mm

        # Step 1: Establish default textbook bearing span (b ≈ 2 * D)
        b_mm = 2.0 * D
        b1_mm = b2_mm = b_mm / 2.0

        # ====================================================================
        # CASE 1: Crank at Dead Centre (Max Bending Moment Configuration)
        # ====================================================================
        H1_dead = f.FP_dead_N * b2_mm / b_mm
        MC_pin = H1_dead * b1_mm
        
        # Diameter derived from bending: d = ∛(32 * M * Kt / (pi * sigma_b))
        dc_mm = ((32.0 * MC_pin * self.Kt) / (math.pi * self.sigma_b)) ** (1.0 / 3.0)
        # Length calculated from allowable bearing pressure: lc = FP / (dc * pb)
        lc_mm = f.FP_dead_N / (dc_mm * self.pb)

        # Standard empirical proportions for the crank web
        t_mm = 0.65 * dc_mm + 6.35
        w_mm = 1.125 * dc_mm + 12.7

        # GEOMETRIC BOUNDARY GUARDRAIL CHECK
        bearing_space_remaining = b2_mm - (lc_mm / 2.0) - t_mm
        if bearing_space_remaining <= 0:
            # Dynamically override and expand the bearing span to resolve geometric conflict
            b_mm = 2.5 * D
            b1_mm = b2_mm = b_mm / 2.0
            H1_dead = f.FP_dead_N * b2_mm / b_mm
            MC_pin = H1_dead * b1_mm
            dc_mm = ((32.0 * MC_pin * self.Kt) / (math.pi * self.sigma_b)) ** (1.0 / 3.0)
            lc_mm = f.FP_dead_N / (dc_mm * self.pb)
            t_mm = 0.65 * dc_mm + 6.35
            w_mm = 1.125 * dc_mm + 12.7
            bearing_space_remaining = b2_mm - (lc_mm / 2.0) - t_mm

        # Shaft layout under flywheel (incorporating overhung weights)
        V3 = f.flywheel_weight_N / 2.0
        H3p = f.belt_pull_N / 2.0
        c1_mm = 1.5 * D  # Estimated standard overhang distance
        MW_flywheel = V3 * c1_mm
        MT_belt = H3p * c1_mm
        MS_combined = math.sqrt(MW_flywheel**2 + MT_belt**2)
        ds_mm = ((32.0 * MS_combined * self.Kt) / (math.pi * self.sigma_b)) ** (1.0 / 3.0)

  
      # ====================================================================
        # CASE 2: Crank at Maximum Torque Angle (Combined Torsion/Bending)
        # ====================================================================
        t_forces = f.evaluate_torque_forces()
        FT = t_forces["FT_N"]
        FR = t_forces["FR_N"]

        HT1 = FT * b2_mm / b_mm
        HR1 = FR * b2_mm / b_mm

        # 1. Validate crankpin diameter against maximum twisting load
        MC2_pin = HR1 * b1_mm
        TC_pin = HT1 * r
        Te_pin = math.sqrt(MC2_pin**2 + TC_pin**2)
        dc_torque_demand = ((16.0 * Te_pin * self.Kt) / (math.pi * self.tau)) ** (1.0 / 3.0)
        dc_mm = max(dc_mm, dc_torque_demand)

        # 2. Validate shaft junction journal size verification
        R1 = math.sqrt(HT1**2 + HR1**2)
        MS1_junc = abs(R1 * (b2_mm + lc_mm/2.0 + t_mm/2.0) - t_forces["FQ_N"] * (lc_mm/2.0 + t_mm/2.0))
        TS_junc = FT * r
        Te_junc = math.sqrt(MS1_junc**2 + TS_junc**2)
        ds1_mm = ((16.0 * Te_junc * self.Kt) / (math.pi * self.tau)) ** (1.0 / 3.0)

        # 3. ADD THIS FIX: Validate Flywheel Shaft against Combined Bending + Torque
        # Equivalent Twisting Moment on Flywheel Shaft
        Te_flywheel = math.sqrt(MS_combined**2 + TS_junc**2)
        ds_torque_demand = ((16.0 * Te_flywheel * self.Kt) / (math.pi * self.tau)) ** (1.0 / 3.0)
        ds_mm = max(ds_mm, ds_torque_demand)  # Choose the larger diameter constraint

        # Final structural parameters storage
        self.results = {
            "configuration": "Centre Crankshaft (3 Bearings)",
            "bearing_span_mm": round(b_mm, 2),
            "crankpin_diameter_mm": round(dc_mm, 2),
            "crankpin_length_mm": round(lc_mm, 2),
            "web_thickness_mm": round(t_mm, 2),
            "web_width_mm": round(w_mm, 2),
            "shaft_flywheel_diameter_mm": round(ds_mm, 2),
            "shaft_junction_diameter_mm": round(ds1_mm, 2),
            "clearance_margin_mm": round(max(0.0, bearing_space_remaining), 2)
        }
        return self.results


class SideCrankshaftDesigner:
    """
    Automates Section 32.21 (Example 32.5) for a 2-bearing overhung side crankshaft.
    Enforces empirical cross-section proportion safety clamps.
    """
    def __init__(
        self, 
        loads: CrankshaftLoads, 
        sigma_b_mpa: float = 60.0, 
        tau_mpa: float = 35.0,
        pb_mpa: float = 10.0,
        fillet_concentration_factor: float = 1.8
    ):
        self.loads = loads
        self.sigma_b = sigma_b_mpa
        self.tau = tau_mpa
        self.pb = pb_mpa
        self.Kt = fillet_concentration_factor
        self.results: Dict[str, Any] = {}
        self._execute_design()

    def _execute_design(self):
        f = self.loads
        r = f.crank_radius_mm

        # Standard analytical textbook aspect ratios for initial design estimates
        lc_dc_ratio = 0.8
        t_dc_ratio = 0.6
        l1_dc_ratio = 1.7

        # ====================================================================
        # CASE 1: Crank at Dead Centre
        # ====================================================================
        # Crankpin sized via bearing pressure allocation constraints
        dc_mm = math.sqrt(f.FP_dead_N / (lc_dc_ratio * self.pb))
        lc_mm = lc_dc_ratio * dc_mm
        t_mm = t_dc_ratio * dc_mm
        l1_mm = l1_dc_ratio * dc_mm  # Main journal bearing length

        # Analytical determination of bearing journal distance 'a'
        a_mm = 0.75 * lc_mm + t_mm + 0.5 * l1_mm
        M_journal = f.FP_dead_N * a_mm
        d1_mm = ((32.0 * M_journal * self.Kt) / (math.pi * self.sigma_b)) ** (1.0 / 3.0)

        # Crank web width determination from bending section modulus logic
        M_web = f.FP_dead_N * (0.75 * lc_mm + 0.5 * t_mm)
        numerator = 6.0 * M_web + f.FP_dead_N * t_mm
        w_mm = math.sqrt(numerator / (self.sigma_b * t_mm))
        
        # Structural Clamp: Ensure the web width does not narrow below the pin diameter boundary
        w_mm = max(w_mm, 1.4 * dc_mm)

        # ====================================================================
        # CASE 2: Crank at Max Torque Angle (Combined Loading Matrix)
        # ====================================================================
        t_forces = f.evaluate_torque_forces()
        FT = t_forces["FT_N"]
        FR = t_forces["FR_N"]

        # Calculate torque metrics at shaft journal junction location
        M_junc = t_forces["FQ_N"] * (0.75 * lc_mm + t_mm)
        TS_junc = FT * r
        Te_junc = math.sqrt(M_junc**2 + TS_junc**2)
        ds1_mm = ((16.0 * Te_junc * self.Kt) / (math.pi * self.tau)) ** (1.0 / 3.0)

        # Choose safe max diameter sizing across both execution conditions
        final_main_journal_dia = max(d1_mm, ds1_mm)

        self.results = {
            "configuration": "Side/Overhung Crankshaft (2 Bearings)",
            "crankpin_diameter_mm": round(dc_mm, 2),
            "crankpin_length_mm": round(lc_mm, 2),
            "web_thickness_mm": round(t_mm, 2),
            "web_width_mm": round(w_mm, 2),
            "main_journal_diameter_mm": round(final_main_journal_dia, 2),
            "main_journal_length_mm": round(l1_mm, 2)
        }
        return self.results