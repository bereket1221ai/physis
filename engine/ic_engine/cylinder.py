"""
cylinder.py - Chapter 32.3-32.4: Cylinder and Cylinder Liner Design

Based on Machine Design textbook (R.S. Khurmi, J.K. Gupta)
Sections covered:
- 32.3: Cylinder and Cylinder Liner
- 32.4: Design of a Cylinder
- Chapter 7: Pressure Vessels (Thick and Thin Cylinders)
- Cylinder head design
- Cooling system integration
- Material selection for cylinder blocks
- Liner types (wet, dry, integral)
- Hoop stress analysis
- Thermal stress management
"""

import math


class CylinderMaterial:
    """Chapter 32.3: Material properties for cylinders and liners."""
    
    MATERIALS = {
        "Gray Cast Iron (Class 30)": {
            "density_kg_m3": 7200,
            "ultimate_tensile_mpa": 250,
            "yield_strength_mpa": 200,
            "fatigue_limit_mpa": 100,
            "youngs_modulus_gpa": 100,
            "thermal_conductivity_w_mk": 52,
            "coefficient_thermal_expansion_1e6": 11,
            "poissons_ratio": 0.25,
            "hardness_hb": 210,
            "max_temperature_c": 400,
        },
        "Alloy Cast Iron": {
            "density_kg_m3": 7300,
            "ultimate_tensile_mpa": 350,
            "yield_strength_mpa": 280,
            "fatigue_limit_mpa": 140,
            "youngs_modulus_gpa": 120,
            "thermal_conductivity_w_mk": 48,
            "coefficient_thermal_expansion_1e6": 10,
            "poissons_ratio": 0.25,
            "hardness_hb": 260,
            "max_temperature_c": 450,
        },
        "Aluminum (319 Alloy)": {
            "density_kg_m3": 2790,
            "ultimate_tensile_mpa": 250,
            "yield_strength_mpa": 180,
            "fatigue_limit_mpa": 90,
            "youngs_modulus_gpa": 71,
            "thermal_conductivity_w_mk": 120,
            "coefficient_thermal_expansion_1e6": 22,
            "poissons_ratio": 0.33,
            "hardness_hb": 85,
            "max_temperature_c": 250,
        },
        "Compact Graphite Iron": {
            "density_kg_m3": 7200,
            "ultimate_tensile_mpa": 500,
            "yield_strength_mpa": 350,
            "fatigue_limit_mpa": 200,
            "youngs_modulus_gpa": 155,
            "thermal_conductivity_w_mk": 45,
            "coefficient_thermal_expansion_1e6": 11,
            "poissons_ratio": 0.26,
            "hardness_hb": 240,
            "max_temperature_c": 450,
        },
        "Ductile Iron (60-40-18)": {
            "density_kg_m3": 7100,
            "ultimate_tensile_mpa": 420,
            "yield_strength_mpa": 290,
            "fatigue_limit_mpa": 180,
            "youngs_modulus_gpa": 169,
            "thermal_conductivity_w_mk": 38,
            "coefficient_thermal_expansion_1e6": 12,
            "poissons_ratio": 0.27,
            "hardness_hb": 180,
            "max_temperature_c": 400,
        },
    }
    
    LINER_MATERIALS = {
        "Hardened Cast Iron": {
            "density_kg_m3": 7300,
            "ultimate_tensile_mpa": 400,
            "yield_strength_mpa": 320,
            "fatigue_limit_mpa": 180,
            "youngs_modulus_gpa": 110,
            "thermal_conductivity_w_mk": 46,
            "coefficient_thermal_expansion_1e6": 11,
            "hardness_hb": 300,
            "max_temperature_c": 450,
            "wear_resistance": "Excellent",
        },
        "Nodular Iron": {
            "density_kg_m3": 7200,
            "ultimate_tensile_mpa": 550,
            "yield_strength_mpa": 420,
            "fatigue_limit_mpa": 220,
            "youngs_modulus_gpa": 165,
            "thermal_conductivity_w_mk": 42,
            "coefficient_thermal_expansion_1e6": 12,
            "hardness_hb": 280,
            "max_temperature_c": 450,
            "wear_resistance": "Excellent",
        },
        "Steel Alloy (4130)": {
            "density_kg_m3": 7850,
            "ultimate_tensile_mpa": 850,
            "yield_strength_mpa": 700,
            "fatigue_limit_mpa": 350,
            "youngs_modulus_gpa": 205,
            "thermal_conductivity_w_mk": 43,
            "coefficient_thermal_expansion_1e6": 12,
            "hardness_hb": 250,
            "max_temperature_c": 500,
            "wear_resistance": "Very Good",
        },
    }
    
    @classmethod
    def get_material(cls, name, category="block"):
        """Get material properties by name."""
        if category == "liner":
            materials = cls.LINER_MATERIALS
        else:
            materials = cls.MATERIALS
        
        if name not in materials:
            raise ValueError(f"Unknown material: {name}. Available: {list(materials.keys())}")
        return materials[name]
    
    @classmethod
    def list_materials(cls, category="block"):
        """List all available materials."""
        if category == "liner":
            return list(cls.LINER_MATERIALS.keys())
        return list(cls.MATERIALS.keys())


class CylinderGeometry:
    """Chapter 32.3: Cylinder geometric parameters."""
    
    def __init__(self, bore_mm, stroke_mm, number_of_cylinders=4, cylinder_spacing_mm=None):
        """
        Parameters:
        -----------
        bore_mm : float
            Cylinder bore diameter (mm)
        stroke_mm : float
            Piston stroke (mm)
        number_of_cylinders : int
            Number of cylinders in engine
        cylinder_spacing_mm : float, optional
            Distance between cylinder centers (mm)
        """
        self.bore_mm = bore_mm
        self.stroke_mm = stroke_mm
        self.bore_m = bore_mm / 1000
        self.stroke_m = stroke_mm / 1000
        self.cylinders = number_of_cylinders
        
        # Cylinder spacing (typical: 1.2 to 1.3 × bore)
        if cylinder_spacing_mm:
            self.spacing_mm = cylinder_spacing_mm
        else:
            self.spacing_mm = 1.25 * bore_mm
        
        # Calculate cylinder volumes
        self.swept_volume_cc = math.pi * (bore_mm ** 2) / 4 * stroke_mm / 1000
        self.total_displacement_cc = self.swept_volume_cc * number_of_cylinders
        self.total_displacement_l = self.total_displacement_cc / 1000
        
        # Calculate cylinder area
        self.area_mm2 = math.pi * (bore_mm ** 2) / 4
        self.area_m2 = self.area_mm2 / 1e6
        
        # Cylinder wall thickness (initial estimate)
        self.wall_thickness_mm = self.calculate_initial_wall_thickness()
    
    def calculate_initial_wall_thickness(self):
        """
        Initial cylinder wall thickness estimate based on bore.
        
        For cast iron: t = 0.045 × bore + 3 mm
        For aluminum: t = 0.035 × bore + 2 mm
        """
        # Conservative estimate for cast iron
        return 0.045 * self.bore_mm + 3
    
    def inner_radius_mm(self):
        """Inner radius of cylinder (bore radius)."""
        return self.bore_mm / 2
    
    def outer_radius_mm(self, wall_thickness_mm=None):
        """Outer radius of cylinder."""
        t = wall_thickness_mm or self.wall_thickness_mm
        return self.inner_radius_mm() + t
    
    def block_length_mm(self):
        """Total engine block length."""
        return self.spacing_mm * self.cylinders
    
    def block_width_mm(self):
        """Approximate engine block width."""
        return self.bore_mm * 1.5
    
    def block_height_mm(self):
        """Approximate engine block height."""
        return self.stroke_mm * 1.8
    
    def water_jacket_thickness_mm(self):
        """Recommended water jacket thickness around cylinder."""
        return 0.1 * self.bore_mm
    
    def bore_to_stroke_ratio(self):
        """Bore-to-stroke ratio (square = 1, oversquare >1, undersquare <1)."""
        return self.bore_mm / self.stroke_mm
    
    def engine_type(self):
        """Determine engine type based on bore/stroke ratio."""
        ratio = self.bore_to_stroke_ratio()
        if ratio > 1.1:
            return "Oversquare (performance-oriented, high RPM)"
        elif ratio > 0.9:
            return "Square (balanced design)"
        else:
            return "Undersquare (torque-oriented, low RPM)"
    
    def cylinder_arrangement_description(self):
        """Describe cylinder arrangement based on count."""
        arrangements = {
            1: "Single cylinder",
            2: "Inline-2 (parallel twin)",
            3: "Inline-3",
            4: "Inline-4 (most common)",
            5: "Inline-5",
            6: "Inline-6 or V6",
            8: "V8",
            10: "V10",
            12: "V12",
        }
        return arrangements.get(self.cylinders, f"{self.cylinders}-cylinder engine")


class CylinderStresses:
    """Chapter 7: Stress analysis for thick/thin cylinders."""
    
    def __init__(self, bore_mm, wall_thickness_mm, max_pressure_mpa, material):
        """
        Parameters:
        -----------
        bore_mm : float
            Cylinder bore diameter (mm)
        wall_thickness_mm : float
            Cylinder wall thickness (mm)
        max_pressure_mpa : float
            Maximum cylinder pressure (MPa)
        material : dict
            Material properties
        """
        self.bore_mm = bore_mm
        self.bore_m = bore_mm / 1000
        self.t_mm = wall_thickness_mm
        self.t_m = wall_thickness_mm / 1000
        self.P_mpa = max_pressure_mpa
        self.P_pa = max_pressure_mpa * 1e6
        self.material = material
        
        # Calculate inner and outer radii
        self.r_i_m = self.bore_m / 2
        self.r_o_m = self.r_i_m + self.t_m
        self.r_i_mm = self.r_i_m * 1000
        self.r_o_mm = self.r_o_m * 1000
        
        # Determine if thin or thick cylinder
        self.is_thick = (self.r_o_m / self.r_i_m) > 1.1
    
    def hoop_stress_thin_mpa(self):
        """
        Chapter 7.3: Hoop (circumferential) stress for thin cylinder.
        
        σ_h = (P × D) / (2 × t)
        
        For thin cylinders (t < D/10).
        """
        if not self.is_thick:
            stress_pa = (self.P_pa * self.bore_m) / (2 * self.t_m)
            return stress_pa / 1e6
        else:
            # Use thick cylinder formula
            return self.hoop_stress_thick_mpa(inner=True)
    
    def longitudinal_stress_thin_mpa(self):
        """
        Chapter 7.5: Longitudinal (axial) stress for thin cylinder.
        
        σ_l = (P × D) / (4 × t)
        """
        stress_pa = (self.P_pa * self.bore_m) / (4 * self.t_m)
        return stress_pa / 1e6
    
    def hoop_stress_thick_mpa(self, inner=True):
        """
        Chapter 7.9: Hoop stress for thick cylinder (Lame's equations).
        
        At inner surface: σ_h = P × (r_o² + r_i²) / (r_o² - r_i²)
        At outer surface: σ_h = 2P × r_i² / (r_o² - r_i²)
        """
        r_i = self.r_i_m
        r_o = self.r_o_m
        P = self.P_pa
        
        if inner:
            # Hoop stress at inner surface (maximum)
            stress_pa = P * (r_o**2 + r_i**2) / (r_o**2 - r_i**2)
        else:
            # Hoop stress at outer surface
            stress_pa = 2 * P * r_i**2 / (r_o**2 - r_i**2)
        
        return stress_pa / 1e6
    
    def radial_stress_thick_mpa(self, radius_m=None):
        """
        Chapter 7.9: Radial stress for thick cylinder.
        
        σ_r = P × (r_i²/r²) × (r_o² - r²) / (r_o² - r_i²)
        """
        r_i = self.r_i_m
        r_o = self.r_o_m
        P = self.P_pa
        
        if radius_m is None:
            # At inner surface (maximum radial stress = -P)
            return -self.P_mpa
        
        r = radius_m
        stress_pa = P * (r_i**2 / r**2) * (r_o**2 - r**2) / (r_o**2 - r_i**2)
        return stress_pa / 1e6
    
    def von_mises_stress_mpa(self):
        """
        Von Mises equivalent stress at inner cylinder wall.
        
        σ_vm = √(σ_h² + σ_r² - σ_hσ_r + 3τ²)
        For cylinder under pressure, τ = 0 (principal stresses).
        """
        if self.is_thick:
            sigma_h = self.hoop_stress_thick_mpa(inner=True)
            sigma_r = self.radial_stress_thick_mpa()
        else:
            sigma_h = self.hoop_stress_thin_mpa()
            sigma_r = -self.P_mpa
        
        sigma_vm = math.sqrt(sigma_h**2 + sigma_r**2 - sigma_h * sigma_r)
        return sigma_vm
    
    def factor_of_safety(self):
        """Factor of safety for cylinder wall."""
        sigma_vm = self.von_mises_stress_mpa()
        yield_stress = self.material["yield_strength_mpa"]
        
        if sigma_vm > 0:
            return yield_stress / sigma_vm
        return 999
    
    def required_wall_thickness_mm(self, target_fs=3.0):
        """
        Calculate required wall thickness for desired safety factor.
        
        Uses thick cylinder formula: t = r_i × (√((σ_y/FS + P)/(σ_y/FS - P)) - 1)
        """
        sigma_allow = self.material["yield_strength_mpa"] / target_fs
        r_i = self.r_i_m
        
        ratio = (sigma_allow + self.P_mpa) / (sigma_allow - self.P_mpa)
        r_o = r_i * math.sqrt(ratio)
        thickness_m = r_o - r_i
        
        return thickness_m * 1000


class CylinderLiner:
    """Chapter 32.3: Cylinder liner (sleeve) design."""
    
    LINER_TYPES = {
        "dry": {
            "description": "Pressed into cylinder block, not in contact with coolant",
            "thickness_mm_factor": 0.02,
            "removable": False,
            "typical_material": "Hardened Cast Iron",
        },
        "wet": {
            "description": "Directly in contact with coolant, removable",
            "thickness_mm_factor": 0.03,
            "removable": True,
            "typical_material": "Nodular Iron",
        },
        "integral": {
            "description": "Cast as part of cylinder block (no separate liner)",
            "thickness_mm_factor": 0,
            "removable": False,
            "typical_material": "Gray Cast Iron",
        },
    }
    
    def __init__(self, bore_mm, liner_type="wet", material_name=None):
        """
        Parameters:
        -----------
        bore_mm : float
            Cylinder bore diameter (mm)
        liner_type : str
            'wet', 'dry', or 'integral'
        material_name : str, optional
            Liner material (default based on liner type)
        """
        self.bore_mm = bore_mm
        self.liner_type = liner_type
        
        if liner_type not in self.LINER_TYPES:
            raise ValueError(f"Unknown liner type: {liner_type}. Use: {list(self.LINER_TYPES.keys())}")
        
        self.type_info = self.LINER_TYPES[liner_type]
        
        # Material selection
        if material_name:
            self.material = CylinderMaterial.get_material(material_name, category="liner")
        else:
            self.material = CylinderMaterial.get_material(
                self.type_info["typical_material"], category="liner"
            )
        
        # Liner dimensions
        self.liner_thickness_mm = self.type_info["thickness_mm_factor"] * bore_mm
        if liner_type == "dry":
            self.liner_thickness_mm = max(self.liner_thickness_mm, 1.5)
        elif liner_type == "wet":
            self.liner_thickness_mm = max(self.liner_thickness_mm, 2.5)
        else:
            self.liner_thickness_mm = 0
        
        self.liner_outer_diameter_mm = bore_mm + 2 * self.liner_thickness_mm
        self.liner_length_mm = 1.2 * bore_mm  # Typical liner length
    
    def liner_interference_fit_mm(self):
        """
        Interference fit for dry liners.
        
        Typically 0.05-0.15 mm interference for proper heat transfer.
        """
        if self.liner_type == "dry":
            return 0.05 + 0.0005 * self.bore_mm
        return 0
    
    required_press_fit_tonnes(self):
        """Force required to press liner into block (for dry liners)."""
        if self.liner_type != "dry":
            return 0
        
        interference = self.liner_interference_fit_mm() / 1000
        diameter_m = self.liner_outer_diameter_mm / 1000
        length_m = self.liner_length_mm / 1000
        
        # Contact area
        area_m2 = math.pi * diameter_m * length_m
        
        # Approximate pressure for interference fit
        E = self.material["youngs_modulus_gpa"] * 1e9
        pressure_pa = (E * interference) / diameter_m
        
        force_n = pressure_pa * area_m2
        force_tonnes = force_n / 1000 / 9.81
        
        return force_tonnes
    
    def recommended_liner_thickness_mm(self):
        """
        Recommended liner thickness based on bore and type.
        """
        recommendations = {
            "wet": 0.03 * self.bore_mm,
            "dry": 0.02 * self.bore_mm,
            "integral": 0,
        }
        return recommendations.get(self.liner_type, 0)
    
    def liner_mass_kg(self):
        """Estimated mass of one liner."""
        if self.liner_type == "integral":
            return 0
        
        volume_m3 = (math.pi * (self.liner_outer_diameter_mm/1000)**2 / 4 * 
                    (self.liner_length_mm/1000) -
                    math.pi * (self.bore_mm/1000)**2 / 4 * 
                    (self.liner_length_mm/1000))
        mass_kg = volume_m3 * self.material["density_kg_m3"]
        return mass_kg


class CylinderCooling:
    """Chapter 32.4: Cooling system design for cylinders."""
    
    def __init__(self, bore_mm, stroke_mm, max_power_kw, max_rpm, 
                 cooling_type="water", ambient_temp_c=25):
        """
        Parameters:
        -----------
        bore_mm : float
            Cylinder bore diameter (mm)
        stroke_mm : float
            Piston stroke (mm)
        max_power_kw : float
            Maximum engine power (kW)
        max_rpm : float
            Maximum engine speed (RPM)
        cooling_type : str
            'water' or 'air'
        ambient_temp_c : float
            Ambient temperature (°C)
        """
        self.bore_mm = bore_mm
        self.stroke_mm = stroke_mm
        self.power_kw = max_power_kw
        self.max_rpm = max_rpm
        self.cooling_type = cooling_type
        self.ambient_temp_c = ambient_temp_c
        
        # Surface areas
        self.cylinder_area_m2 = math.pi * (bore_mm/1000) * (stroke_mm/1000)
        self.total_cylinder_area_m2 = self.cylinder_area_m2 * 4  # Assume 4 cylinders
    
    def heat_generated_kw(self):
        """
        Heat generated in cylinder (approximate).
        
        Approximately 25-35% of fuel energy becomes heat to coolant.
        For power output, heat to coolant ≈ power output.
        """
        # Simplified: heat to coolant ≈ 1.2 × power output
        return self.power_kw * 1.2
    
    def coolant_flow_rate_l_min(self, delta_t_c=10):
        """
        Required coolant flow rate (water cooling).
        
        Q = m_dot × c_p × ΔT
        
        Where:
        - Q = heat to coolant (kW)
        - c_p = specific heat of water (4.18 kJ/kg·K)
        - ΔT = temperature rise (°C)
        """
        Q_kw = self.heat_generated_kw()
        cp = 4.18  # kJ/kg·K for water
        
        mass_flow_kg_s = Q_kw / (cp * delta_t_c)
        mass_flow_kg_min = mass_flow_kg_s * 60
        volume_flow_l_min = mass_flow_kg_min  # 1 kg water ≈ 1 L
        
        return volume_flow_l_min
    
    def water_jacket_velocity_m_s(self, water_jacket_area_cm2=50):
        """
        Water velocity in water jacket.
        
        V = Q_flow / A_jacket
        """
        flow_m3_s = self.coolant_flow_rate_l_min() / 1000 / 60
        area_m2 = water_jacket_area_cm2 / 10000
        velocity = flow_m3_s / area_m2
        return velocity
    
    def fin_area_required_m2(self, heat_transfer_coefficient_w_m2k=100):
        """
        Required fin area for air cooling.
        
        Q = h × A × ΔT
        """
        if self.cooling_type != "air":
            return 0
        
        Q_w = self.heat_generated_kw() * 1000
        delta_T = 150  # Temperature difference between fin and air (°C)
        
        area_m2 = Q_w / (heat_transfer_coefficient_w_m2k * delta_T)
        return area_m2
    
    def recommended_water_jacket_thickness_mm(self):
        """
        Recommended water jacket thickness around cylinder.
        """
        # Typically 5-10 mm for automotive engines
        return max(6, 0.07 * self.bore_mm)
    
    def cooling_system_capacity_l(self):
        """
        Estimated cooling system capacity.
        """
        # Rough estimate: 0.5-1.0 L per cylinder
        return 0.7 * 4  # Assuming 4 cylinders


class CylinderHead:
    """Chapter 32.4: Cylinder head design."""
    
    def __init__(self, bore_mm, max_pressure_mpa, material=None):
        """
        Parameters:
        -----------
        bore_mm : float
            Cylinder bore diameter (mm)
        max_pressure_mpa : float
            Maximum cylinder pressure (MPa)
        material : dict, optional
            Material properties for head (default: Gray Cast Iron)
        """
        self.bore_mm = bore_mm
        self.bore_m = bore_mm / 1000
        self.P_mpa = max_pressure_mpa
        self.P_pa = max_pressure_mpa * 1e6
        
        if material:
            self.material = material
        else:
            self.material = CylinderMaterial.get_material("Gray Cast Iron (Class 30)")
        
        self.area_m2 = math.pi * (self.bore_m ** 2) / 4
        self.force_n = self.P_pa * self.area_m2
    
    def head_thickness_flat_mm(self, factor_of_safety=3):
        """
        Cylinder head thickness (flat plate formula).
        
        t = D × √(P × k / σ_allow)
        
        Where k = 0.1 for clamped edges
        """
        sigma_allow = self.material["yield_strength_mpa"] / factor_of_safety
        thickness_m = self.bore_m * math.sqrt(0.1 * self.P_mpa / sigma_allow)
        return thickness_m * 1000
    
    def head_thickness_ribbed_mm(self):
        """
        Reduced thickness for ribbed cylinder head.
        
        Ribs allow thinner walls (60-70% of flat thickness).
        """
        flat_thickness = self.head_thickness_flat_mm()
        return 0.65 * flat_thickness
    
    def number_of_head_bolts(self):
        """
        Recommended number of cylinder head bolts.
        """
        if self.bore_mm < 70:
            return 4
        elif self.bore_mm < 90:
            return 6
        elif self.bore_mm < 120:
            return 8
        else:
            return 10
    
    def bolt_diameter_mm(self, num_bolts=None, factor_of_safety=3):
        """
        Required cylinder head bolt diameter.
        """
        if num_bolts is None:
            num_bolts = self.number_of_head_bolts()
        
        force_per_bolt = self.force_n / num_bolts
        sigma_allow = self.material["yield_strength_mpa"] / factor_of_safety
        
        # Required area
        area_mm2 = force_per_bolt / sigma_allow
        diameter_mm = math.sqrt(4 * area_mm2 / math.pi)
        
        # Round up to standard size
        standard_sizes = [8, 10, 12, 14, 16, 18, 20]
        for size in standard_sizes:
            if size >= diameter_mm:
                return size
        return diameter_mm
    
    def head_gasket_thickness_mm(self):
        """
        Recommended head gasket thickness.
        """
        # Typically 1-2 mm for modern engines
        return 1.5
    
    def compression_ratio_effect(self, compressed_thickness_mm):
        """
        Calculate effect of gasket thickness on compression ratio.
        """
        # Simplified - assumes gasket volume adds to clearance volume
        gasket_volume_cc = self.area_m2 * (compressed_thickness_mm / 1000) * 1e6
        return gasket_volume_cc


class CylinderComplete:
    """Complete cylinder design integrating all components."""
    
    def __init__(self, bore_mm, stroke_mm, max_pressure_mpa, max_power_kw, max_rpm,
                 number_of_cylinders=4, compression_ratio=10.5,
                 cylinder_material_name="Gray Cast Iron (Class 30)",
                 liner_type="wet", cooling_type="water",
                 target_fs=3.0):
        """
        Complete cylinder design calculator.
        
        Parameters:
        -----------
        bore_mm : float
            Cylinder bore diameter (mm)
        stroke_mm : float
            Piston stroke (mm)
        max_pressure_mpa : float
            Maximum cylinder pressure (MPa)
        max_power_kw : float
            Maximum engine power (kW)
        max_rpm : float
            Maximum engine speed (RPM)
        number_of_cylinders : int
            Number of cylinders
        compression_ratio : float
            Engine compression ratio
        cylinder_material_name : str
            Cylinder block material
        liner_type : str
            'wet', 'dry', or 'integral'
        cooling_type : str
            'water' or 'air'
        target_fs : float
            Target factor of safety
        """
        self.bore_mm = bore_mm
        self.stroke_mm = stroke_mm
        self.pressure_mpa = max_pressure_mpa
        self.power_kw = max_power_kw
        self.max_rpm = max_rpm
        self.cylinders = number_of_cylinders
        self.cr = compression_ratio
        self.target_fs = target_fs
        
        # Material
        self.material = CylinderMaterial.get_material(cylinder_material_name, category="block")
        self.material["name"] = cylinder_material_name
        
        # Geometry
        self.geometry = CylinderGeometry(bore_mm, stroke_mm, number_of_cylinders)
        
        # Stresses
        self.stresses = CylinderStresses(bore_mm, self.geometry.wall_thickness_mm, 
                                         max_pressure_mpa, self.material)
        
        # Liner
        self.liner = CylinderLiner(bore_mm, liner_type)
        
        # Cooling
        self.cooling = CylinderCooling(bore_mm, stroke_mm, max_power_kw, max_rpm, cooling_type)
        
        # Head
        self.head = CylinderHead(bore_mm, max_pressure_mpa, self.material)
        
        # Update wall thickness based on stress analysis
        self.required_wall_thickness_mm = self.stresses.required_wall_thickness_mm(target_fs)
        self.recommended_wall_thickness_mm = max(
            self.geometry.wall_thickness_mm,
            self.required_wall_thickness_mm,
            self.cooling.recommended_water_jacket_thickness_mm() + 5
        )
    
    def design_summary(self):
        """Generate complete cylinder design summary."""
        
        summary = {
            # Basic parameters
            "bore_mm": self.bore_mm,
            "stroke_mm": self.stroke_mm,
            "bore_stroke_ratio": round(self.geometry.bore_to_stroke_ratio(), 2),
            "engine_type": self.geometry.engine_type(),
            "displacement_cc": round(self.geometry.total_displacement_cc, 1),
            "displacement_l": round(self.geometry.total_displacement_l, 2),
            
            # Wall thickness
            "initial_wall_thickness_mm": round(self.geometry.wall_thickness_mm, 2),
            "required_wall_thickness_mm": round(self.required_wall_thickness_mm, 2),
            "recommended_wall_thickness_mm": round(self.recommended_wall_thickness_mm, 2),
            
            # Stresses
            "hoop_stress_mpa": round(self.stresses.hoop_stress_thin_mpa(), 1),
            "longitudinal_stress_mpa": round(self.stresses.longitudinal_stress_thin_mpa(), 1),
            "von_mises_stress_mpa": round(self.stresses.von_mises_stress_mpa(), 1),
            "yield_strength_mpa": self.material["yield_strength_mpa"],
            "factor_of_safety": round(self.stresses.factor_of_safety(), 2),
            
            # Liner
            "liner_type": self.liner.liner_type,
            "liner_material": self.liner.material.get("name", "N/A"),
            "liner_thickness_mm": round(self.liner.liner_thickness_mm, 2),
            "liner_interference_mm": round(self.liner.liner_interference_fit_mm(), 3),
            
            # Cooling
            "cooling_type": self.cooling.cooling_type,
            "heat_generated_kw": round(self.cooling.heat_generated_kw(), 1),
            "coolant_flow_l_min": round(self.cooling.coolant_flow_rate_l_min(), 1),
            "water_jacket_thickness_mm": round(self.cooling.recommended_water_jacket_thickness_mm(), 1),
            
            # Cylinder head
            "head_thickness_flat_mm": round(self.head.head_thickness_flat_mm(), 2),
            "head_thickness_ribbed_mm": round(self.head.head_thickness_ribbed_mm(), 2),
            "head_bolts": self.head.number_of_head_bolts(),
            "bolt_diameter_mm": self.head.bolt_diameter_mm(),
            "gasket_thickness_mm": self.head.head_gasket_thickness_mm(),
            
            # Dimensions
            "block_length_mm": round(self.geometry.block_length_mm(), 1),
            "block_width_mm": round(self.geometry.block_width_mm(), 1),
            "cylinder_spacing_mm": round(self.geometry.spacing_mm, 1),
            
            # Material
            "cylinder_material": self.material["name"],
            "cylinder_mass_kg": round(self.estimate_cylinder_mass_kg(), 2),
        }
        
        return summary
    
    def estimate_cylinder_mass_kg(self):
        """Estimate cylinder block mass."""
        # Simplified volume calculation
        block_length_m = self.geometry.block_length_mm() / 1000
        block_width_m = self.geometry.block_width_mm() / 1000
        block_height_m = self.geometry.block_height_mm() / 1000
        
        # Approximate block volume (subtract cylinder bores)
        total_volume_m3 = block_length_m * block_width_m * block_height_m
        cylinder_volume_m3 = (math.pi * (self.bore_mm/1000)**2 / 4 * 
                              (self.stroke_mm/1000) * self.cylinders * 1.5)
        
        block_volume_m3 = total_volume_m3 - cylinder_volume_m3
        mass_kg = block_volume_m3 * self.material["density_kg_m3"]
        
        return mass_kg
    
    def print_design_report(self):
        """Print formatted design report."""
        s = self.design_summary()
        
        print("=" * 70)
        print("CYLINDER DESIGN REPORT - Machine Design Textbook Chapter 32")
        print("=" * 70)
        
        print(f"\n📐 ENGINE SPECIFICATIONS:")
        print(f"   Bore: {s['bore_mm']:.1f} mm")
        print(f"   Stroke: {s['stroke_mm']:.1f} mm")
        print(f"   Bore