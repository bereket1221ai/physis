"""
connecting_rod.py - Chapter 32.13-32.15: Connecting Rod Design for IC Engines

Based on Machine Design textbook (R.S. Khurmi, J.K. Gupta)
Sections covered:
- 32.13: Connecting Rod
- 32.14: Forces Acting on the Connecting Rod
- 32.15: Design of Connecting Rod
- Chapter 16: Columns and Struts (buckling analysis)

Additional references:
- Inertia forces at TDC and BDC
- Whipping stress
- Big end and small end bearing design
- I-section optimization
- Bolts and caps
"""

import math


class ConnectingRodMaterial:
    """Material properties for connecting rods."""
    
    MATERIALS = {
        "Forged Steel (4340)": {
            "density_kg_m3": 7850,
            "ultimate_tensile_mpa": 1080,
            "yield_strength_mpa": 930,
            "fatigue_limit_mpa": 400,
            "endurance_limit_mpa": 350,
            "youngs_modulus_gpa": 205,
            "hardness_hb": 350,
        },
        "Forged Steel (4140)": {
            "density_kg_m3": 7850,
            "ultimate_tensile_mpa": 950,
            "yield_strength_mpa": 830,
            "fatigue_limit_mpa": 350,
            "endurance_limit_mpa": 310,
            "youngs_modulus_gpa": 205,
            "hardness_hb": 320,
        },
        "Carbon Steel (1045)": {
            "density_kg_m3": 7850,
            "ultimate_tensile_mpa": 630,
            "yield_strength_mpa": 530,
            "fatigue_limit_mpa": 250,
            "endurance_limit_mpa": 220,
            "youngs_modulus_gpa": 200,
            "hardness_hb": 210,
        },
        "Titanium Alloy (6Al-4V)": {
            "density_kg_m3": 4430,
            "ultimate_tensile_mpa": 950,
            "yield_strength_mpa": 880,
            "fatigue_limit_mpa": 450,
            "endurance_limit_mpa": 400,
            "youngs_modulus_gpa": 114,
            "hardness_hb": 330,
        },
        "Aluminum (7075-T6)": {
            "density_kg_m3": 2810,
            "ultimate_tensile_mpa": 570,
            "yield_strength_mpa": 500,
            "fatigue_limit_mpa": 160,
            "endurance_limit_mpa": 140,
            "youngs_modulus_gpa": 71,
            "hardness_hb": 150,
        },
        "Sintered Steel": {
            "density_kg_m3": 7200,
            "ultimate_tensile_mpa": 700,
            "yield_strength_mpa": 600,
            "fatigue_limit_mpa": 280,
            "endurance_limit_mpa": 250,
            "youngs_modulus_gpa": 170,
            "hardness_hb": 250,
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
        """List all available connecting rod materials."""
        return list(cls.MATERIALS.keys())


class ConnectingRodForces:
    """Chapter 32.14: Forces acting on connecting rod."""
    
    def __init__(self, bore_mm, stroke_mm, rod_length_mm, reciprocating_mass_kg, 
                 max_gas_pressure_mpa, max_rpm):
        """
        Parameters:
        -----------
        bore_mm : float
            Cylinder bore diameter in mm
        stroke_mm : float
            Piston stroke in mm
        rod_length_mm : float
            Center-to-center length of connecting rod in mm
        reciprocating_mass_kg : float
            Mass of piston, rings, pin, and small end of rod in kg
        max_gas_pressure_mpa : float
            Maximum combustion pressure in MPa
        max_rpm : float
            Maximum engine speed in RPM
        """
        self.bore_mm = bore_mm
        self.bore_m = bore_mm / 1000
        self.stroke_mm = stroke_mm
        self.stroke_m = stroke_mm / 1000
        self.rod_length_mm = rod_length_mm
        self.rod_length_m = rod_length_mm / 1000
        self.reciprocating_mass = reciprocating_mass_kg
        self.gas_pressure_pa = max_gas_pressure_mpa * 1e6
        self.max_rpm = max_rpm
        
        # Crank radius
        self.crank_radius_m = stroke_mm / 2000
        self.crank_radius_mm = stroke_mm / 2
        
        # Crank to rod ratio (n = l/r)
        self.n = rod_length_mm / self.crank_radius_mm
        
        # Angular velocity
        self.omega = 2 * math.pi * max_rpm / 60
        
        # Piston area
        self.piston_area_m2 = math.pi * (self.bore_m ** 2) / 4
        self.piston_area_mm2 = math.pi * (self.bore_mm ** 2) / 4
    
    def piston_area_m2(self):
        """Piston area in square meters."""
        return self.piston_area_m2
    
    def gas_force_n(self, crank_angle_deg=0):
        """
        Gas force on piston at given crank angle.
        
        Maximum at TDC (0 degrees) during combustion.
        """
        return self.gas_pressure_pa * self.piston_area_m2
    
    def gas_force_kn(self):
        """Gas force in kN."""
        return self.gas_force_n() / 1000
    
    def inertia_force_n(self, crank_angle_deg):
        """
        Chapter 32.14: Inertia force of reciprocating parts.
        
        F_i = m_r × ω² × r × (cos θ + cos 2θ / n)
        
        Where:
        - m_r = reciprocating mass (kg)
        - ω = angular velocity (rad/s)
        - r = crank radius (m)
        - θ = crank angle from TDC (degrees)
        - n = l/r (rod length / crank radius)
        
        Returns:
        --------
        float : Inertia force in Newtons (positive = away from crankshaft)
        """
        theta_rad = math.radians(crank_angle_deg)
        
        inertia = (self.reciprocating_mass * 
                   self.omega ** 2 * 
                   self.crank_radius_m * 
                   (math.cos(theta_rad) + math.cos(2 * theta_rad) / self.n))
        
        return inertia
    
    def inertia_force_tdc_n(self):
        """
        Inertia force at Top Dead Center (θ = 0°).
        
        F_i,max = m_r × ω² × r × (1 + 1/n)
        """
        theta_rad = 0
        inertia = (self.reciprocating_mass * 
                   self.omega ** 2 * 
                   self.crank_radius_m * 
                   (math.cos(theta_rad) + math.cos(2 * theta_rad) / self.n))
        return inertia
    
    def inertia_force_bdc_n(self):
        """
        Inertia force at Bottom Dead Center (θ = 180°).
        
        F_i = m_r × ω² × r × (-1 + 1/n)
        (Negative = toward crankshaft)
        """
        theta_rad = math.radians(180)
        inertia = (self.reciprocating_mass * 
                   self.omega ** 2 * 
                   self.crank_radius_m * 
                   (math.cos(theta_rad) + math.cos(2 * theta_rad) / self.n))
        return inertia
    
    def net_force_n(self, crank_angle_deg):
        """
        Net force on connecting rod = Gas force + Inertia force.
        
        At TDC during combustion: gas force down + inertia force up
        Maximum tension occurs during exhaust stroke at TDC
        Maximum compression occurs during power stroke near TDC
        """
        gas = self.gas_force_n(crank_angle_deg)
        inertia = self.inertia_force_n(crank_angle_deg)
        
        # Gas force acts downward (positive)
        # Inertia force acts upward at TDC (negative for compression)
        # Net = Gas - Inertia (sign convention: positive = compression)
        return gas - inertia
    
    def max_compressive_force_n(self):
        """
        Maximum compressive force on connecting rod.
        
        Occurs near TDC during power stroke when gas pressure peaks.
        """
        # At TDC with peak combustion pressure
        return self.gas_force_n(0) - self.inertia_force_tdc_n()
    
    def max_tensile_force_n(self):
        """
        Maximum tensile force on connecting rod.
        
        Occurs at TDC during exhaust stroke (no gas pressure, inertia only).
        """
        # At TDC with no gas pressure (exhaust stroke)
        return -self.inertia_force_tdc_n()
    
    def connecting_rod_force_kn(self, crank_angle_deg):
        """
        Force along connecting rod axis.
        
        F_rod = F_net / cos(φ)
        
        Where φ = angle between connecting rod and cylinder axis.
        """
        theta_rad = math.radians(crank_angle_deg)
        
        # sin φ = sin θ / n
        sin_phi = math.sin(theta_rad) / self.n
        phi = math.asin(min(1.0, max(-1.0, sin_phi)))  # Clamp to valid range
        cos_phi = math.cos(phi)
        
        net_force = self.net_force_n(crank_angle_deg)
        
        if cos_phi > 0:
            return net_force / cos_phi
        else:
            return net_force / 0.01  # Large number if near 90 degrees
    
    def crank_angle_at_max_force(self):
        """
        Approximate crank angle where maximum compressive force occurs.
        
        Typically 5-15 degrees after TDC.
        """
        return 10  # Degrees after TDC (empirical)


class ConnectingRodCrossSection:
    """Chapter 32.15: I-section design for connecting rod."""
    
    def __init__(self, bore_mm, stroke_mm, rod_length_mm, max_compressive_force_n, material):
        """
        Design I-section connecting rod cross-section.
        
        Typical dimensions (for automotive engine):
        - Flange width (H) = 0.8 to 1.0 × bore
        - Web thickness (t) = 0.2 to 0.3 × H
        - Flange thickness (t1) = 0.1 to 0.15 × H
        """
        self.bore_mm = bore_mm
        self.stroke_mm = stroke_mm
        self.rod_length_mm = rod_length_mm
        self.max_force_n = max_compressive_force_n
        self.material = material
        
        # Recommended H (total depth) based on bore
        self.H_mm = 0.85 * bore_mm  # Total depth of I-section
        self.H_m = self.H_mm / 1000
        
        # Web thickness (t)
        self.t_mm = 0.25 * self.H_mm
        self.t_m = self.t_mm / 1000
        
        # Flange thickness (t1)
        self.t1_mm = 0.12 * self.H_mm
        self.t1_m = self.t1_mm / 1000
        
        # Flange width (B)
        self.B_mm = 0.7 * self.H_mm
        self.B_m = self.B_mm / 1000
    
    def area_mm2(self):
        """Cross-sectional area of I-section in mm²."""
        # Area = (B × t1) × 2 + (H - 2×t1) × t
        flange_area = self.B_mm * self.t1_mm * 2
        web_area = (self.H_mm - 2 * self.t1_mm) * self.t_mm
        return flange_area + web_area
    
    def area_m2(self):
        """Cross-sectional area in m²."""
        return self.area_mm2() / 1e6
    
    def moment_of_inertia_x_mm4(self):
        """
        Moment of inertia about X-X axis (bending in plane of rotation).
        
        I_xx = (B × H³/12) - ((B - t) × (H - 2×t1)³/12)
        """
        # Outer rectangle
        I_outer = (self.B_mm * self.H_mm ** 3) / 12
        # Inner rectangle (hollow part)
        inner_height = self.H_mm - 2 * self.t1_mm
        I_inner = ((self.B_mm - self.t_mm) * inner_height ** 3) / 12
        return I_outer - I_inner
    
    def moment_of_inertia_y_mm4(self):
        """
        Moment of inertia about Y-Y axis (bending perpendicular to rotation).
        
        I_yy = (t1 × B³/6) + (H × t³/12)
        """
        # Top and bottom flanges
        I_flanges = 2 * (self.t1_mm * self.B_mm ** 3) / 12
        # Web
        I_web = (self.t_mm * (self.H_mm - 2 * self.t1_mm) ** 3) / 12
        return I_flanges + I_web
    
    def section_modulus_x_mm3(self):
        """Section modulus about X-X axis."""
        return self.moment_of_inertia_x_mm4() / (self.H_mm / 2)
    
    def section_modulus_y_mm3(self):
        """Section modulus about Y-Y axis."""
        return self.moment_of_inertia_y_mm4() / (self.B_mm / 2)
    
    def radius_of_gyration_x_mm(self):
        """Radius of gyration about X-X axis."""
        return math.sqrt(self.moment_of_inertia_x_mm4() / self.area_mm2())
    
    def radius_of_gyration_y_mm(self):
        """Radius of gyration about Y-Y axis."""
        return math.sqrt(self.moment_of_inertia_y_mm4() / self.area_mm2())
    
    def compressive_stress_mpa(self):
        """Direct compressive stress on cross-section."""
        return self.max_force_n / self.area_m2() / 1e6
    
    def buckling_load_n(self, length_mm, end_fixity_factor):
        """
        Chapter 16: Euler's buckling load.
        
        P_cr = π² × E × I / Lₑ²
        
        Where Lₑ = K × L (end fixity factor)
        - K = 1.0 for pinned-pinned (most conservative)
        - K = 0.65 for fixed-fixed
        - K = 0.8 for pinned-fixed
        
        Parameters:
        -----------
        length_mm : float
            Effective length for buckling (mm)
        end_fixity_factor : float
            K factor (typically 1.0 for connecting rod)
        """
        E = self.material["youngs_modulus_gpa"] * 1000  # MPa
        I = self.moment_of_inertia_x_mm4()  # mm⁴
        Le = end_fixity_factor * length_mm
        
        # Convert units carefully
        P_cr_N = (math.pi ** 2 * E * I) / (Le ** 2)
        return P_cr_N
    
    def buckling_factor_of_safety(self, length_mm, end_fixity_factor=1.0):
        """Factor of safety against buckling."""
        P_cr = self.buckling_load_n(length_mm, end_fixity_factor)
        return P_cr / self.max_force_n
    
    def whipping_stress_mpa(self, max_rpm, stroke_mm):
        """
        Chapter 32.15: Whipping stress due to inertia of rod itself.
        
        Approximate formula for bending stress due to rod's own inertia.
        """
        # Simplified estimation
        omega = 2 * math.pi * max_rpm / 60
        # Whipping stress = ρ × ω² × l² / (6 × (k_x)²) × c
        density = self.material["density_kg_m3"]
        l = self.rod_length_mm / 1000
        k_x = self.radius_of_gyration_x_mm() / 1000
        
        # Simplified whipping stress (MPa)
        whipping = (density * omega ** 2 * l ** 2) / (6 * k_x ** 2) / 1e6
        return whipping


class ConnectingRodEnds:
    """Small end and big end bearing design."""
    
    def __init__(self, bore_mm, max_gas_force_n, max_tensile_force_n, material):
        """
        Parameters:
        -----------
        bore_mm : float
            Cylinder bore in mm
        max_gas_force_n : float
            Maximum gas force in Newtons
        max_tensile_force_n : float
            Maximum tensile force in Newtons
        material : dict
            Material properties
        """
        self.bore_mm = bore_mm
        self.max_gas_force_n = max_gas_force_n
        self.max_tensile_force_n = max_tensile_force_n
        self.material = material
        
        # Small end (piston pin) dimensions
        self.pin_diameter_mm = 0.25 * bore_mm  # Approximate
        self.small_end_width_mm = 0.9 * self.pin_diameter_mm
        
        # Big end (crank pin) dimensions
        self.crank_pin_diameter_mm = 0.6 * bore_mm
        self.big_end_width_mm = 0.8 * self.crank_pin_diameter_mm
    
    def small_end_bearing_pressure_mpa(self):
        """
        Bearing pressure at small end (piston pin bearing).
        
        p = F_max / (d_pin × l_small)
        """
        force_n = max(self.max_gas_force_n, self.max_tensile_force_n)
        area_mm2 = self.pin_diameter_mm * self.small_end_width_mm
        pressure_mpa = force_n / area_mm2 / 1e6  # N/mm² = MPa
        return pressure_mpa
    
    def big_end_bearing_pressure_mpa(self):
        """
        Bearing pressure at big end (crank pin bearing).
        
        p = F_max / (d_crank × l_big)
        """
        force_n = self.max_gas_force_n
        area_mm2 = self.crank_pin_diameter_mm * self.big_end_width_mm
        pressure_mpa = force_n / area_mm2 / 1e6
        return pressure_mpa
    
    def permissible_bearing_pressure_mpa(self):
        """
        Permissible bearing pressure for connecting rod bearings.
        """
        return 15  # MPa (typical for automotive engines)
    
    def small_end_eye_thickness_mm(self):
        """Thickness of small end eye bushing."""
        return 0.1 * self.pin_diameter_mm
    
    def big_end_bolt_diameter_mm(self, num_bolts=2, factor_of_safety=3):
        """
        Chapter 32.15: Big end bolt design.
        
        Bolts must withstand inertia force at TDC.
        """
        force_per_bolt = self.max_tensile_force_n / num_bolts
        allowable_stress = self.material["yield_strength_mpa"] / factor_of_safety
        
        # Required area per bolt
        area_mm2 = force_per_bolt / allowable_stress
        diameter_mm = math.sqrt(4 * area_mm2 / math.pi)
        
        # Round up to standard size
        standard_sizes = [6, 8, 10, 12, 14, 16]
        for size in standard_sizes:
            if size >= diameter_mm:
                return size
        return diameter_mm


class ConnectingRodComplete:
    """Complete connecting rod design integrating all components."""
    
    def __init__(self, bore_mm, stroke_mm, max_gas_pressure_mpa, max_rpm,
                 reciprocating_mass_kg, material_name="Forged Steel (4340)",
                 rod_length_ratio=1.7):
        """
        Complete connecting rod design calculator.
        
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
            Rod length / stroke ratio (typical: 1.5-1.8)
        """
        self.bore_mm = bore_mm
        self.stroke_mm = stroke_mm
        
        # Rod length = rod_length_ratio × stroke
        self.rod_length_mm = rod_length_ratio * stroke_mm
        
        # Material
        self.material_data = ConnectingRodMaterial.get_material(material_name)
        self.material_data["name"] = material_name
        self.material = self.material_data
        
        # Forces
        self.forces = ConnectingRodForces(
            bore_mm=bore_mm,
            stroke_mm=stroke_mm,
            rod_length_mm=self.rod_length_mm,
            reciprocating_mass_kg=reciprocating_mass_kg,
            max_gas_pressure_mpa=max_gas_pressure_mpa,
            max_rpm=max_rpm
        )
        
        # Force calculations
        self.max_compressive_force_n = self.forces.max_compressive_force_n()
        self.max_tensile_force_n = abs(self.forces.max_tensile_force_n())
        
        # Cross-section
        self.cross_section = ConnectingRodCrossSection(
            bore_mm=bore_mm,
            stroke_mm=stroke_mm,
            rod_length_mm=self.rod_length_mm,
            max_compressive_force_n=self.max_compressive_force_n,
            material=self.material
        )
        
        # Ends
        self.ends = ConnectingRodEnds(
            bore_mm=bore_mm,
            max_gas_force_n=self.forces.gas_force_n(),
            max_tensile_force_n=self.max_tensile_force_n,
            material=self.material
        )
    
    def design_summary(self):
        """Generate complete connecting rod design summary."""
        
        # Buckling analysis (both X-X and Y-Y axes)
        buckling_fs_xx = self.cross_section.buckling_factor_of_safety(
            self.rod_length_mm, end_fixity_factor=1.0
        )
        buckling_fs_yy = self.cross_section.buckling_factor_of_safety(
            self.rod_length_mm * 0.8, end_fixity_factor=1.0
        )  # Effective length shorter for Y-Y axis
        
        summary = {
            # Dimensions
            "bore_mm": self.bore_mm,
            "stroke_mm": self.stroke_mm,
            "rod_length_mm": round(self.rod_length_mm, 1),
            "rod_to_stroke_ratio": round(self.rod_length_mm / self.stroke_mm, 2),
            
            # Cross-section dimensions (I-section)
            "section_depth_H_mm": round(self.cross_section.H_mm, 2),
            "section_width_B_mm": round(self.cross_section.B_mm, 2),
            "web_thickness_t_mm": round(self.cross_section.t_mm, 2),
            "flange_thickness_t1_mm": round(self.cross_section.t1_mm, 2),
            "cross_section_area_mm2": round(self.cross_section.area_mm2(), 1),
            
            # Section properties
            "I_xx_mm4": round(self.cross_section.moment_of_inertia_x_mm4(), 0),
            "I_yy_mm4": round(self.cross_section.moment_of_inertia_y_mm4(), 0),
            "k_x_mm": round(self.cross_section.radius_of_gyration_x_mm(), 2),
            "k_y_mm": round(self.cross_section.radius_of_gyration_y_mm(), 2),
            
            # Forces
            "max_compressive_force_kN": round(self.max_compressive_force_n / 1000, 1),
            "max_tensile_force_kN": round(self.max_tensile_force_n / 1000, 1),
            "direct_compressive_stress_mpa": round(self.cross_section.compressive_stress_mpa(), 1),
            
            # Buckling
            "buckling_load_xx_kN": round(self.cross_section.buckling_load_n(self.rod_length_mm, 1.0) / 1000, 1),
            "buckling_fs_xx": round(buckling_fs_xx, 2),
            "buckling_fs_yy": round(buckling_fs_yy, 2),
            
            # Small end (piston pin)
            "pin_diameter_mm": round(self.ends.pin_diameter_mm, 2),
            "small_end_width_mm": round(self.ends.small_end_width_mm, 2),
            "small_end_bearing_pressure_mpa": round(self.ends.small_end_bearing_pressure_mpa(), 2),
            
            # Big end (crank pin)
            "crank_pin_diameter_mm": round(self.ends.crank_pin_diameter_mm, 2),
            "big_end_width_mm": round(self.ends.big_end_width_mm, 2),
            "big_end_bearing_pressure_mpa": round(self.ends.big_end_bearing_pressure_mpa(), 2),
            "permissible_bearing_pressure_mpa": self.ends.permissible_bearing_pressure_mpa(),
            
            # Bolts
            "bolt_diameter_mm": self.ends.big_end_bolt_diameter_mm(),
            
            # Material
            "material": self.material["name"],
            "mass_estimate_kg": round(self.estimate_mass_kg(), 2),
        }
        
        return summary
    
    def estimate_mass_kg(self):
        """Estimate connecting rod mass."""
        # Volume = area × length (plus 30% for big/small ends)
        volume_m3 = (self.cross_section.area_m2() * self.rod_length_mm / 1000) * 1.3
        mass_kg = volume_m3 * self.material["density_kg_m3"]
        return mass_kg
    
    def print_design_report(self):
        """Print formatted design report."""
        s = self.design_summary()
        
        print("=" * 70)
        print("CONNECTING ROD DESIGN REPORT - Machine Design Textbook Chapter 32")
        print("=" * 70)
        
        print(f"\n📐 ENGINE SPECIFICATIONS:")
        print(f"   Bore: {s['bore_mm']:.1f} mm")
        print(f"   Stroke: {s['stroke_mm']:.1f} mm")
        print(f"   Rod length: {s['rod_length_mm']:.1f} mm")
        print(f"   Rod/Stroke ratio: {s['rod_to_stroke_ratio']:.2f}")
        
        print(f"\n📏 CROSS-SECTION (I-Section):")
        print(f"   Total depth (H): {s['section_depth_H_mm']:.2f} mm")
        print(f"   Flange width (B): {s['section_width_B_mm']:.2f} mm")
        print(f"   Web thickness (t): {s['web_thickness_t_mm']:.2f} mm")
        print(f"   Flange thickness (t₁): {s['flange_thickness_t1_mm']:.2f} mm")
        print(f"   Area: {s['cross_section_area_mm2']:.1f} mm²")
        
        print(f"\n📊 SECTION PROPERTIES:")
        print(f"   I_xx = {s['I_xx_mm4']:.0f} mm⁴")
        print(f"   I_yy = {s['I_yy_mm4']:.0f} mm⁴")
        print(f"   k_x = {s['k_x_mm']:.2f} mm")
        print(f"   k_y = {s['k_y_mm']:.2f} mm")
        
        print(f"\n⚡ FORCES:")
        print(f"   Max compressive force: {s['max_compressive_force_kN']:.1f} kN")
        print(f"   Max tensile force: {s['max_tensile_force_kN']:.1f} kN")
        print(f"   Direct compressive stress: {s['direct_compressive_stress_mpa']:.1f} MPa")
        
        print(f"\n🔒 BUCKLING ANALYSIS:")
        print(f"   Critical load (X-X): {s['buckling_load_xx_kN']:.1f} kN")
        print(f"   Buckling F.S. (X-X): {s['buckling_fs_xx']:.2f}")
        print(f"   Buckling F.S. (Y-Y): {s['buckling_fs_yy']:.2f}")
        
        print(f"\n🔧 SMALL END (Piston Pin):")
        print(f"   Pin diameter: {s['pin_diameter_mm']:.2f} mm")
        print(f"   Bearing width: {s['small_end_width_mm']:.2f} mm")
        print(f"   Bearing pressure: {s['small_end_bearing_pressure_mpa']:.2f} MPa")
        
        print(f"\n🔧 BIG END (Crank Pin):")
        print(f"   Crank pin diameter: {s['crank_pin_diameter_mm']:.2f} mm")
        print(f"   Bearing width: {s['big_end_width_mm']:.2f} mm")
        print(f"   Bearing pressure: {s['big_end_bearing_pressure_mpa']:.2f} MPa")
        print(f"   Permissible pressure: {s['permissible_bearing_pressure_mpa']:.2f} MPa")
        
        print(f"\n🔩 BIG END BOLTS:")
        print(f"   Bolt diameter: M{s['bolt_diameter_mm']:.0f} mm")
        
        print(f"\n🏗️ MATERIAL & MASS:")
        print(f"   Material: {s['material']}")
        print(f"   Estimated mass: {s['mass_estimate_kg']:.2f} kg")
        
        print("\n" + "=" * 70)
        
        # Validation checks
        issues = []
        
        if s['small_end_bearing_pressure_mpa'] > s['permissible_bearing_pressure_mpa']:
            issues.append("⚠️ SMALL END BEARING PRESSURE EXCEEDS ALLOWABLE")
        if s['big_end_bearing_pressure_mpa'] > s['permissible_bearing_pressure_mpa']:
            issues.append("⚠️ BIG END BEARING PRESSURE EXCEEDS ALLOWABLE")
        if s['buckling_fs_xx'] < 3:
            issues.append("⚠️ BUCKLING F.S. BELOW 3 (unsafe for dynamic loads)")
        if s['direct_compressive_stress_mpa'] > self.material["yield_strength_mpa"] / 2:
            issues.append("⚠️ COMPRESSIVE STRESS HIGH")
        
        if issues:
            print("\n⚠️ DESIGN ISSUES:")
            for issue in issues:
                print(f"   {issue}")
        else:
            print("\n✅ DESIGN ACCEPTABLE - All criteria satisfied")
        
        print("=" * 70)


# ============================================================================
# Example usage
# ============================================================================

if __name__ == "__main__":
    print("=" * 70)
    print("CONNECTING ROD DESIGN CALCULATOR - Machine Design Textbook")
    print("=" * 70)
    
    print("\n📌 Example: 4-Cylinder Automotive Engine")
    print("   Bore: 85 mm, Stroke: 88 mm, Max Pressure: 8 MPa")
    print("   Max RPM: 6500, Reciprocating mass: 0.65 kg")
    print("-" * 70)
    
    # Create connecting rod design
    connecting_rod = ConnectingRodComplete(
        bore_mm=85,
        stroke_mm=88,
        max_gas_pressure_mpa=8.0,
        max_rpm=6500,
        reciprocating_mass_kg=0.65,  # Piston + rings + pin + small end
        material_name="Forged Steel (4340)",
        rod_length_ratio=1.7
    )
    
    # Print design report
    connecting_rod.print_design_report()
    
    print("\n" + "=" * 70)
    print("Connecting rod design ready for engine integration.")
    print("=" * 70)