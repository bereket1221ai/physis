"""
crankshaft.py - Chapter 32.16-32.21: Crankshaft Design for IC Engines

Based on Machine Design textbook (R.S. Khurmi, J.K. Gupta)
Sections covered:
- 32.16: Crankshaft
- 32.17: Material and Manufacture of Crankshafts
- 32.18: Bearing Pressure and Stresses in Crankshafts
- 32.19: Design Procedure for Crankshaft
- 32.20: Design for Centre Crankshaft
- 32.21: Side or Overhung Crankshaft

Additional references:
- FEA validation principles
- Fillet radius optimization
- Torsional vibration analysis
- Balance mass design
- Failure mode analysis (fatigue, wear, bending)
"""

import math


class CrankshaftMaterial:
    """Chapter 32.17: Material properties for crankshafts."""
    
    MATERIALS = {
        "Forged Steel (4340)": {
            "density_kg_m3": 7850,
            "ultimate_tensile_mpa": 1080,
            "yield_strength_mpa": 930,
            "fatigue_limit_mpa": 400,
            "endurance_limit_mpa": 350,
            "youngs_modulus_gpa": 205,
            "hardness_hb": 350,
            "max_torsional_stress_mpa": 280,
            "max_bending_stress_mpa": 350,
        },
        "Forged Steel (4140)": {
            "density_kg_m3": 7850,
            "ultimate_tensile_mpa": 950,
            "yield_strength_mpa": 830,
            "fatigue_limit_mpa": 350,
            "endurance_limit_mpa": 310,
            "youngs_modulus_gpa": 205,
            "hardness_hb": 320,
            "max_torsional_stress_mpa": 250,
            "max_bending_stress_mpa": 310,
        },
        "Ductile Iron (80-55-06)": {
            "density_kg_m3": 7300,
            "ultimate_tensile_mpa": 550,
            "yield_strength_mpa": 380,
            "fatigue_limit_mpa": 220,
            "endurance_limit_mpa": 200,
            "youngs_modulus_gpa": 170,
            "hardness_hb": 230,
            "max_torsional_stress_mpa": 200,
            "max_bending_stress_mpa": 250,
        },
        "Compact Graphite Iron": {
            "density_kg_m3": 7200,
            "ultimate_tensile_mpa": 500,
            "yield_strength_mpa": 350,
            "fatigue_limit_mpa": 250,
            "endurance_limit_mpa": 230,
            "youngs_modulus_gpa": 155,
            "hardness_hb": 240,
            "max_torsional_stress_mpa": 210,
            "max_bending_stress_mpa": 260,
        },
        "Billet Steel": {
            "density_kg_m3": 7850,
            "ultimate_tensile_mpa": 900,
            "yield_strength_mpa": 750,
            "fatigue_limit_mpa": 360,
            "endurance_limit_mpa": 320,
            "youngs_modulus_gpa": 200,
            "hardness_hb": 300,
            "max_torsional_stress_mpa": 260,
            "max_bending_stress_mpa": 320,
        },
    }
    
    @classmethod
    def get_material(cls, name):
        """Get material properties by name."""
        if name not in cls.MATERIALS:
            raise ValueError(f"Unknown material: {name}. Available: {list(cls.MATERIALS.keys())}")
        return cls.MATERIALS[name]
    
    @classmethod
    def list_materials(cls):
        """List all available crankshaft materials."""
        return list(cls.MATERIALS.keys())


class CrankshaftForces:
    """Forces and moments acting on crankshaft."""
    
    def __init__(self, bore_mm, stroke_mm, max_gas_pressure_mpa, max_torque_nm,
                 reciprocating_mass_kg, rotating_mass_kg):
        """
        Parameters:
        -----------
        bore_mm : float
            Cylinder bore diameter (mm)
        stroke_mm : float
            Piston stroke (mm)
        max_gas_pressure_mpa : float
            Maximum combustion pressure (MPa)
        max_torque_nm : float
            Maximum engine torque (N·m)
        reciprocating_mass_kg : float
            Mass of piston + rings + pin + small end of rod (kg)
        rotating_mass_kg : float
            Mass of crankpin + big end of rod (kg)
        """
        self.bore_mm = bore_mm
        self.stroke_mm = stroke_mm
        self.pressure_mpa = max_gas_pressure_mpa
        self.max_torque_nm = max_torque_nm
        self.m_r = reciprocating_mass_kg
        self.m_c = rotating_mass_kg
        
        # Derived values
        self.crank_radius_m = stroke_mm / 2000
        self.crank_radius_mm = stroke_mm / 2
        self.piston_area_mm2 = math.pi * (bore_mm ** 2) / 4
        self.piston_area_m2 = self.piston_area_mm2 / 1e6
        
        # Gas force
        self.gas_force_n = self.pressure_mpa * 1e6 * self.piston_area_m2
        self.gas_force_kN = self.gas_force_n / 1000
    
    def tangential_force_n(self, crank_angle_deg):
        """
        Tangential force on crankpin (contributing to torque).
        
        F_t = F_rod × sin(θ + φ) / cos(φ)
        """
        theta_rad = math.radians(crank_angle_deg)
        
        # Crank to rod ratio (n = l/r)
        n = 3.5  # Typical l/r ratio (connecting rod length / crank radius)
        
        # sin φ = sin θ / n
        sin_phi = math.sin(theta_rad) / n
        phi = math.asin(min(0.5, max(-0.5, sin_phi)))  # Clamp
        cos_phi = math.cos(phi)
        
        # Rod force (simplified - uses gas force at this angle)
        # For peak torque, use max gas force at approximately 30° after TDC
        f_rod = self.gas_force_n / cos_phi if cos_phi > 0 else self.gas_force_n
        
        # Tangential component
        f_tangential = f_rod * math.sin(theta_rad + phi) / cos_phi
        
        return f_tangential
    
    def radial_force_n(self, crank_angle_deg):
        """
        Radial force on crankpin (acting along crank axis).
        
        F_r = F_rod × cos(θ + φ) / cos(φ)
        """
        theta_rad = math.radians(crank_angle_deg)
        n = 3.5
        sin_phi = math.sin(theta_rad) / n
        phi = math.asin(min(0.5, max(-0.5, sin_phi)))
        cos_phi = math.cos(phi)
        
        f_rod = self.gas_force_n / cos_phi if cos_phi > 0 else self.gas_force_n
        f_radial = f_rod * math.cos(theta_rad + phi) / cos_phi
        
        return f_radial
    
    def centrifugal_force_n(self):
        """
        Centrifugal force from rotating masses.
        
        F_c = m_c × ω² × r
        """
        # Using peak torque RPM (typically 3000-5000 for max torque)
        rpm = 4000  # Estimated peak torque RPM
        omega = 2 * math.pi * rpm / 60
        f_centrifugal = self.m_c * omega ** 2 * self.crank_radius_m
        return f_centrifugal
    
    def net_load_on_crankpin_n(self, crank_angle_deg=30):
        """
        Net load on crankpin (vector sum of tangential and radial).
        
        For design, use maximum load position (typically 30-40° after TDC).
        """
        f_t = self.tangential_force_n(crank_angle_deg)
        f_r = self.radial_force_n(crank_angle_deg)
        f_c = self.centrifugal_force_n()
        
        # Net radial load = radial - centrifugal
        f_radial_net = abs(f_r - f_c)
        f_net = math.sqrt(f_t ** 2 + f_radial_net ** 2)
        
        return f_net


class CrankshaftGeometry:
    """Chapter 32.19-32.21: Crankshaft geometric parameters."""
    
    def __init__(self, bore_mm, stroke_mm, crankpin_diameter_mm, journal_diameter_mm):
        """
        Parameters:
        -----------
        bore_mm : float
            Cylinder bore diameter (mm)
        stroke_mm : float
            Piston stroke (mm)
        crankpin_diameter_mm : float
            Diameter of crankpin (connecting rod bearing)
        journal_diameter_mm : float
            Diameter of main bearing journal
        """
        self.bore_mm = bore_mm
        self.stroke_mm = stroke_mm
        self.crankpin_d = crankpin_diameter_mm
        self.journal_d = journal_diameter_mm
        self.crank_radius_mm = stroke_mm / 2
        
        # Typical proportions (based on bore)
        if crankpin_diameter_mm is None:
            self.crankpin_d = 0.55 * bore_mm
        if journal_diameter_mm is None:
            self.journal_d = 0.6 * bore_mm
        
        # Derived dimensions
        self.crankpin_length_mm = 0.8 * self.crankpin_d
        self.journal_length_mm = 0.7 * self.journal_d
        
        # Crank web dimensions
        self.web_width_mm = 0.4 * bore_mm
        self.web_thickness_mm = 0.25 * bore_mm
        self.web_radius_mm = 0.06 * bore_mm  # Fillet radius
        
        # Crank throw
        self.throw_length_mm = self.crank_radius_mm + self.web_width_mm
        
        # Overall length
        self.overall_length_mm = 2 * self.throw_length_mm + self.journal_length_mm
    
    def crankpin_area_mm2(self):
        """Cross-sectional area of crankpin."""
        return math.pi * (self.crankpin_d ** 2) / 4
    
    def crankpin_section_modulus_mm3(self):
        """Section modulus of crankpin for bending."""
        return math.pi * (self.crankpin_d ** 3) / 32
    
    def crankpin_polar_modulus_mm3(self):
        """Polar modulus of crankpin for torsion."""
        return math.pi * (self.crankpin_d ** 3) / 16
    
    def journal_section_modulus_mm3(self):
        """Section modulus of main journal."""
        return math.pi * (self.journal_d ** 3) / 32
    
    def web_section_modulus_mm3(self):
        """Section modulus of crank web (rectangular)."""
        return (self.web_width_mm * self.web_thickness_mm ** 2) / 6


class CrankshaftStresses:
    """Chapter 32.18: Stress analysis for crankshaft."""
    
    def __init__(self, geometry, forces, material):
        """
        Parameters:
        -----------
        geometry : CrankshaftGeometry
            Geometric parameters
        forces : CrankshaftForces
            Force calculations
        material : dict
            Material properties
        """
        self.geometry = geometry
        self.forces = forces
        self.material = material
        
        # For design, use crank angle of maximum stress (typically 30-40° after TDC)
        self.crank_angle_deg = 35
        self.f_net = forces.net_load_on_crankpin_n(self.crank_angle_deg)
        self.f_tangential = forces.tangential_force_n(self.crank_angle_deg)
        self.f_radial = forces.radial_force_n(self.crank_angle_deg)
        self.f_centrifugal = forces.centrifugal_force_n()
    
    def crankpin_bending_stress_mpa(self):
        """
        Bending stress in crankpin (due to gas force).
        
        σ_b = (M_b × c) / I
        where M_b = F_net × L (beam between webs)
        """
        # Crankpin as beam supported by webs
        span_mm = self.geometry.web_width_mm * 2 + self.geometry.crankpin_length_mm
        bending_moment_nmm = self.f_net * span_mm / 2  # Simply supported
        
        section_modulus = self.geometry.crankpin_section_modulus_mm3()
        stress_mpa = bending_moment_nmm / section_modulus
        
        return stress_mpa / 1e6  # Convert Pa to MPa
    
    def crankpin_shear_stress_mpa(self):
        """
        Shear stress in crankpin.
        
        τ = F / A
        """
        area_mm2 = self.geometry.crankpin_area_mm2()
        shear_stress_mpa = self.f_net / area_mm2
        return shear_stress_mpa
    
    def crankpin_torsional_stress_mpa(self):
        """
        Torsional stress in crankpin.
        
        τ_t = T × r / J
        """
        torque_nmm = self.f_tangential * self.geometry.crank_radius_mm
        polar_modulus = self.geometry.crankpin_polar_modulus_mm3()
        stress_mpa = torque_nmm / polar_modulus / 1e3  # Approximate
        return stress_mpa
    
    def main_journal_bending_stress_mpa(self):
        """
        Bending stress in main journal bearing.
        
        Reaction forces from adjacent cylinders.
        """
        # Simplified: assume 0.5 of crankpin load
        load_n = self.f_net / 2
        span_mm = self.geometry.journal_length_mm
        bending_moment_nmm = load_n * span_mm / 4
        
        section_modulus = self.geometry.journal_section_modulus_mm3()
        stress_mpa = bending_moment_nmm / section_modulus / 1e6
        
        return stress_mpa
    
    def crank_web_bending_stress_mpa(self):
        """
        Bending stress at crank web fillet (critical location).
        
        σ_web = (M_b × y) / I + (P / A)
        where M_b = F_radial × distance
        """
        # Bending moment at web from radial force
        distance_mm = self.geometry.crank_radius_mm
        bending_moment_nmm = self.f_radial * distance_mm
        
        section_modulus = self.geometry.web_section_modulus_mm3()
        bending_stress_mpa = bending_moment_nmm / section_modulus / 1e6
        
        # Direct compression stress
        area_mm2 = self.geometry.web_width_mm * self.geometry.web_thickness_mm
        direct_stress_mpa = self.f_radial / area_mm2
        
        total_stress_mpa = bending_stress_mpa + direct_stress_mpa
        
        return total_stress_mpa
    
    def crank_web_shear_stress_mpa(self):
        """
        Shear stress at crank web from tangential force.
        """
        shear_force_n = self.f_tangential
        area_mm2 = self.geometry.web_width_mm * self.geometry.web_thickness_mm
        shear_stress_mpa = shear_force_n / area_mm2
        
        return shear_stress_mpa
    
    def fillet_stress_concentration_factor(self):
        """
        Chapter 32.18: Stress concentration at fillet radius.
        
        k_t = 1 + (r_fillet × D)^-0.5 × factor
        """
        r_mm = self.geometry.web_radius_mm
        d_mm = self.geometry.journal_d
        
        if r_mm < 0.5:
            return 3.5
        elif r_mm < 1.0:
            return 3.0
        elif r_mm < 2.0:
            return 2.5
        elif r_mm < 3.0:
            return 2.2
        elif r_mm < 5.0:
            return 2.0
        else:
            return 1.8
    
    def max_combined_stress_mpa(self, location="crankpin"):
        """
        Chapter 32.18: Maximum combined stress using Von Mises.
        
        For ductile materials: σ_vm = √(σ_b² + 3τ²)
        """
        if location == "crankpin":
            sigma_b = self.crankpin_bending_stress_mpa()
            tau = max(self.crankpin_shear_stress_mpa(), 
                     self.crankpin_torsional_stress_mpa())
        elif location == "web_fillet":
            sigma_b = self.crank_web_bending_stress_mpa()
            tau = self.crank_web_shear_stress_mpa()
            # Apply stress concentration factor at fillet
            k_t = self.fillet_stress_concentration_factor()
            sigma_b *= k_t
            tau *= k_t
        elif location == "main_journal":
            sigma_b = self.main_journal_bending_stress_mpa()
            tau = 0
        else:
            sigma_b = 0
            tau = 0
        
        # Von Mises equivalent stress
        sigma_vm = math.sqrt(sigma_b ** 2 + 3 * tau ** 2)
        
        return sigma_vm
    
    def factor_of_safety(self, location="web_fillet"):
        """
        Factor of safety at critical location.
        """
        sigma_vm = self.max_combined_stress_mpa(location)
        fatigue_limit = self.material["fatigue_limit_mpa"]
        
        # Apply reduction factors
        # Surface factor (forged crankshaft)
        surface_factor = 0.85
        # Size factor
        size_factor = 0.85
        # Load factor
        load_factor = 1.0
        
        corrected_endurance = fatigue_limit * surface_factor * size_factor * load_factor
        
        fs = corrected_endurance / sigma_vm if sigma_vm > 0 else 999
        
        return fs


class CrankshaftBearings:
    """Main bearing and connecting rod bearing design."""
    
    def __init__(self, geometry, forces, material):
        """
        Parameters:
        -----------
        geometry : CrankshaftGeometry
            Geometric parameters
        forces : CrankshaftForces
            Force calculations
        material : dict
            Material properties
        """
        self.geometry = geometry
        self.forces = forces
        self.material = material
        
        # Bearing properties
        self.allowable_bearing_pressure_mpa = 15  # MPa (typical)
        self.oil_viscosity_cst = 70  # mm²/s (SAE 30 at 70°C)
        self.oil_clearance_mm = 0.05  # Typical radial clearance
    
    def crankpin_bearing_pressure_mpa(self):
        """
        Bearing pressure at crankpin (connecting rod bearing).
        
        p = F_net / (d × l)
        """
        load_n = self.forces.net_load_on_crankpin_n(35)
        area_mm2 = (self.geometry.crankpin_d * 
                   self.geometry.crankpin_length_mm)
        pressure_mpa = load_n / area_mm2
        
        return pressure_mpa
    
    def main_bearing_pressure_mpa(self):
        """
        Bearing pressure at main journal.
        """
        load_n = self.forces.gas_force_n / 2  # Shared between two bearings
        area_mm2 = (self.geometry.journal_d * 
                   self.geometry.journal_length_mm)
        pressure_mpa = load_n / area_mm2
        
        return pressure_mpa
    
    def sommerfeld_number(self, rpm):
        """
        Sommerfeld number for journal bearing analysis.
        
        S = (r/c)² × (μ × N) / p
        """
        # Radius (mm)
        r = self.geometry.journal_d / 2
        # Clearance ratio
        c = self.oil_clearance_mm
        # Oil viscosity (Pa·s)
        mu = self.oil_viscosity_cst / 1e6 * 850  # Approximate
        # Speed (rev/s)
        N = rpm / 60
        # Bearing pressure (Pa)
        p = self.main_bearing_pressure_mpa() * 1e6
        
        S = (r / c) ** 2 * (mu * N) / p
        
        return S
    
    def minimum_oil_film_thickness_mm(self, rpm):
        """
        Minimum oil film thickness (Raimondi-Boyd approximation).
        """
        S = self.sommerfeld_number(rpm)
        
        # Empirical relation
        if S < 0.05:
            h_min = 0.001
        elif S < 0.2:
            h_min = 0.002 + (S - 0.05) * 0.006
        else:
            h_min = 0.005
        
        return h_min
    
    def oil_temperature_rise_c(self, rpm):
        """
        Estimated oil temperature rise due to friction.
        """
        pressure = self.main_bearing_pressure_mpa()
        speed = rpm
        
        # Empirical formula
        delta_T = 0.001 * pressure * speed / 10
        
        return min(delta_T, 40)  # Max 40°C rise
    
    def bearing_life_hours(self, rpm, load_factor=1.0):
        """
        Estimated bearing life using empirical durability.
        """
        pressure = self.main_bearing_pressure_mpa() * load_factor
        
        if pressure < 10:
            life = 5000
        elif pressure < 12:
            life = 3000
        elif pressure < 15:
            life = 2000
        elif pressure < 18:
            life = 1000
        else:
            life = 500
        
        # Speed factor
        speed_factor = 6000 / max(rpm, 1000)
        
        return life * speed_factor


class BalanceMass:
    """Crankshaft balance mass (counterweight) design."""
    
    def __init__(self, stroke_mm, rotating_mass_kg, reciprocating_mass_kg,
                 crankpin_diameter_mm, crank_radius_mm):
        """
        Parameters:
        -----------
        stroke_mm : float
            Piston stroke (mm)
        rotating_mass_kg : float
            Rotating mass (crankpin + big end)
        reciprocating_mass_kg : float
            Reciprocating mass (piston + small end)
        crankpin_diameter_mm : float
            Crankpin diameter (mm)
        crank_radius_mm : float
            Crank radius (mm)
        """
        self.stroke_mm = stroke_mm
        self.m_r = rotating_mass_kg
        self.m_rec = reciprocating_mass_kg
        self.crankpin_d = crankpin_diameter_mm
        self.crank_r = crank_radius_mm
        
        # Balance factor (typically 0.5-0.6 for automotive)
        self.balance_factor = 0.55
    
    def required_balance_mass_kg(self):
        """
        Required counterweight mass.
        
        m_b × r_b = m_r × r + m_rec × r × balance_factor
        """
        # Assume balance mass radius = crank radius
        r_b = self.crank_r
        
        required_moment = (self.m_r * self.crank_r + 
                          self.m_rec * self.crank_r * self.balance_factor)
        balance_mass_kg = required_moment / r_b
        
        return balance_mass_kg
    
    def balance_mass_volume_mm3(self, material_density=7800):
        """
        Volume of balance mass (assuming steel).
        """
        mass_kg = self.required_balance_mass_kg()
        volume_mm3 = mass_kg / material_density * 1e9
        return volume_mm3
    
    def balance_mass_center_of_gravity_mm(self, crankshaft_length_mm):
        """
        Estimated center of gravity location for balance mass.
        """
        return crankshaft_length_mm / 3
    
    def residual_unbalance_percent(self):
        """
        Residual unbalance as percentage of reciprocating mass.
        """
        return (1 - self.balance_factor) * 100


class CrankshaftComplete:
    """Complete crankshaft design integrating all components."""
    
    def __init__(self, bore_mm, stroke_mm, max_gas_pressure_mpa, max_torque_nm,
                 max_rpm, reciprocating_mass_kg, rotating_mass_kg,
                 material_name="Forged Steel (4340)",
                 cylinder_count=4, engine_layout="inline"):
        """
        Complete crankshaft design calculator.
        
        Parameters:
        -----------
        bore_mm : float
            Cylinder bore diameter (mm)
        stroke_mm : float
            Piston stroke (mm)
        max_gas_pressure_mpa : float
            Maximum combustion pressure (MPa)
        max_torque_nm : float
            Maximum engine torque (N·m)
        max_rpm : float
            Maximum engine speed (RPM)
        reciprocating_mass_kg : float
            Mass of piston + rings + pin + small end (kg)
        rotating_mass_kg : float
            Mass of crankpin + big end of rod (kg)
        material_name : str
            Crankshaft material
        cylinder_count : int
            Number of cylinders
        engine_layout : str
            'inline', 'v6', 'v8', 'flat'
        """
        self.bore_mm = bore_mm
        self.stroke_mm = stroke_mm
        self.pressure_mpa = max_gas_pressure_mpa
        self.max_torque = max_torque_nm
        self.max_rpm = max_rpm
        self.m_rec = reciprocating_mass_kg
        self.m_rot = rotating_mass_kg
        self.cylinder_count = cylinder_count
        self.layout = engine_layout
        
        # Material
        self.material_data = CrankshaftMaterial.get_material(material_name)
        self.material_data["name"] = material_name
        self.material = self.material_data
        
        # Crank radius
        self.crank_radius_mm = stroke_mm / 2
        self.crank_radius_m = self.crank_radius_mm / 1000
        
        # Geometry (initial estimates)
        self.geometry = CrankshaftGeometry(
            bore_mm=bore_mm,
            stroke_mm=stroke_mm,
            crankpin_diameter_mm=0.55 * bore_mm,
            journal_diameter_mm=0.60 * bore_mm
        )
        
        # Forces
        self.forces = CrankshaftForces(
            bore_mm=bore_mm,
            stroke_mm=stroke_mm,
            max_gas_pressure_mpa=max_gas_pressure_mpa,
            max_torque_nm=max_torque_nm,
            reciprocating_mass_kg=m_rec,
            rotating_mass_kg=m_rot
        )
        
        # Stresses
        self.stresses = CrankshaftStresses(self.geometry, self.forces, self.material)
        
        # Bearings
        self.bearings = CrankshaftBearings(self.geometry, self.forces, self.material)
        
        # Balance
        self.balance = BalanceMass(
            stroke_mm=stroke_mm,
            rotating_mass_kg=m_rot,
            reciprocating_mass_kg=m_rec,
            crankpin_diameter_mm=self.geometry.crankpin_d,
            crank_radius_mm=self.crank_radius_mm
        )
    
    def design_summary(self):
        """Generate complete crankshaft design summary."""
        
        # Get critical stresses
        sigma_crankpin = self.stresses.crankpin_bending_stress_mpa()
        sigma_web = self.stresses.crank_web_bending_stress_mpa()
        tau_web = self.stresses.crank_web_shear_stress_mpa()
        sigma_vm_fillet = self.stresses.max_combined_stress_mpa("web_fillet")
        fs_fillet = self.stresses.factor_of_safety("web_fillet")
        
        # Bearing pressures
        p_crankpin = self.bearings.crankpin_bearing_pressure_mpa()
        p_main = self.bearings.main_bearing_pressure_mpa()
        
        summary = {
            # Dimensions
            "bore_mm": self.bore_mm,
            "stroke_mm": self.stroke_mm,
            "crank_radius_mm": self.crank_radius_mm,
            "crankpin_diameter_mm": round(self.geometry.crankpin_d, 2),
            "crankpin_length_mm": round(self.geometry.crankpin_length_mm, 2),
            "journal_diameter_mm": round(self.geometry.journal_d, 2),
            "journal_length_mm": round(self.geometry.journal_length_mm, 2),
            "web_width_mm": round(self.geometry.web_width_mm, 2),
            "web_thickness_mm": round(self.geometry.web_thickness_mm, 2),
            "fillet_radius_mm": round(self.geometry.web_radius_mm, 2),
            
            # Forces
            "max_gas_force_kN": round(self.forces.gas_force_kN, 1),
            "net_crankpin_load_kN": round(self.forces.net_load_on_crankpin_n(35)/1000, 1),
            
            # Stresses
            "crankpin_bending_stress_mpa": round(sigma_crankpin, 1),
            "crank_web_bending_stress_mpa": round(sigma_web, 1),
            "crank_web_shear_stress_mpa": round(tau_web, 1),
            "von_mises_stress_fillet_mpa": round(sigma_vm_fillet, 1),
            "fatigue_limit_mpa": self.material["fatigue_limit_mpa"],
            "factor_of_safety_fillet": round(fs_fillet, 2),
            
            # Bearings
            "crankpin_bearing_pressure_mpa": round(p_crankpin, 2),
            "main_bearing_pressure_mpa": round(p_main, 2),
            "allowable_bearing_pressure_mpa": self.bearings.allowable_bearing_pressure_mpa,
            "min_oil_film_mm": round(self.bearings.minimum_oil_film_thickness_mm(self.max_rpm) * 1000, 3),
            
            # Balance
            "balance_mass_kg": round(self.balance.required_balance_mass_kg(), 2),
            "balance_factor": self.balance.balance_factor,
            "residual_unbalance_percent": round(self.balance.residual_unbalance_percent(), 1),
            
            # Material
            "material": self.material["name"],
            "crankshaft_mass_kg": round(self.estimate_mass_kg(), 2),
        }
        
        return summary
    
    def estimate_mass_kg(self):
        """Estimate crankshaft mass."""
        # Volume estimation (simplified)
        main_journal_volume = (math.pi * (self.geometry.journal_d/2)**2 * 
                               self.geometry.journal_length_mm * self.cylinder_count)
        crankpin_volume = (math.pi * (self.geometry.crankpin_d/2)**2 * 
                          self.geometry.crankpin_length_mm * self.cylinder_count)
        web_volume = (self.geometry.web_width_mm * 
                     self.geometry.web_thickness_mm * 
                     self.crank_radius_mm * 2 * self.cylinder_count)
        
        total_volume_mm3 = main_journal_volume + crankpin_volume + web_volume
        total_volume_m3 = total_volume_mm3 / 1e9
        
        mass_kg = total_volume_m3 * self.material["density_kg_m3"]
        
        return mass_kg
    
    def print_design_report(self):
        """Print formatted design report."""
        s = self.design_summary()
        
        print("=" * 70)
        print("CRANKSHAFT DESIGN REPORT - Machine Design Textbook Chapter 32")
        print("=" * 70)
        
        print(f"\n📐 ENGINE SPECIFICATIONS:")
        print(f"   Bore: {s['bore_mm']:.1f} mm")
        print(f"   Stroke: {s['stroke_mm']:.1f} mm")
        print(f"   Cylinders: {self.cylinder_count} ({self.layout})")
        print(f"   Max RPM: {self.max_rpm:.0f}")
        print(f"   Max Torque: {self.max_torque:.1f} N·m")
        
        print(f"\n📏 CRANKSHAFT DIMENSIONS:")
        print(f"   Crank radius: {s['crank_radius_mm']:.1f} mm")
        print(f"   Crankpin diameter: {s['crankpin_diameter_mm']:.2f} mm")
        print(f"   Crankpin length: {s['crankpin_length_mm']:.2f} mm")
        print(f"   Main journal diameter: {s['journal_diameter_mm']:.2f} mm")
        print(f"   Main journal length: {s['journal_length_mm']:.2f} mm")
        print(f"   Web width: {s['web_width_mm']:.2f} mm")
        print(f"   Web thickness: {s['web_thickness_mm']:.2f} mm")
        print(f"   Fillet radius: {s['fillet_radius_mm']:.2f} mm")
        
        print(f"\n⚡ FORCES:")
        print(f"   Max gas force: {s['max_gas_force_kN']:.1f} kN")
        print(f"   Net crankpin load: {s['net_crankpin_load_kN']:.1f} kN")
        
        print(f"\n📊 STRESS ANALYSIS (Critical at Fillet):")
        print(f"   Crankpin bending: {s['crankpin_bending_stress_mpa']:.1f} MPa")
        print(f"   Web bending: {s['crank_web_bending_stress_mpa']:.1f} MPa")
        print(f"   Web shear: {s['crank_web_shear_stress_mpa']:.1f} MPa")
        print(f"   Von Mises (fillet): {s['von_mises_stress_fillet_mpa']:.1f} MPa")
        print(f"   Fatigue limit: {s['fatigue_limit_mpa']} MPa")
        print(f"   ✅ Factor of Safety: {s['factor_of_safety_fillet']:.2f}")
        
        print(f"\n🔧 BEARING ANALYSIS:")
        print(f"   Crankpin bearing pressure