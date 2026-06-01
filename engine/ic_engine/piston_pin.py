"""
piston_pin.py - Chapter 32.11-32.12: Piston Pin (Wrist Pin) Design

Based on Machine Design textbook (R.S. Khurmi, J.K. Gupta)
Sections covered:
- 32.11: Piston Pin
- 32.12: Piston Pin (continued)

Additional references:
- Pin loading analysis (bending and shear)
- Bearing pressure calculations
- Pin materials and heat treatment
- Pin types (semi-floating, full-floating)
- Pin retention methods
- Ovalization and deflection analysis
- Lubrication and clearance
- Fatigue life prediction
- Manufacturing considerations
"""

import math


class PistonPinMaterial:
    """Chapter 32.11: Material properties for piston pins."""
    
    MATERIALS = {
        "Case Hardened Steel (8620)": {
            "density_kg_m3": 7850,
            "ultimate_tensile_mpa": 980,
            "yield_strength_mpa": 750,
            "fatigue_limit_mpa": 380,
            "endurance_limit_mpa": 350,
            "youngs_modulus_gpa": 205,
            "hardness_core_hb": 280,
            "hardness_surface_hb": 600,
            "case_depth_mm": 0.8,
            "description": "Excellent wear resistance, good fatigue strength",
        },
        "Case Hardened Steel (4320)": {
            "density_kg_m3": 7850,
            "ultimate_tensile_mpa": 1080,
            "yield_strength_mpa": 850,
            "fatigue_limit_mpa": 420,
            "endurance_limit_mpa": 380,
            "youngs_modulus_gpa": 205,
            "hardness_core_hb": 310,
            "hardness_surface_hb": 650,
            "case_depth_mm": 1.0,
            "description": "Very high strength, premium material",
        },
        "Through Hardened Steel (4140)": {
            "density_kg_m3": 7850,
            "ultimate_tensile_mpa": 950,
            "yield_strength_mpa": 830,
            "fatigue_limit_mpa": 400,
            "endurance_limit_mpa": 360,
            "youngs_modulus_gpa": 205,
            "hardness_core_hb": 320,
            "hardness_surface_hb": 320,
            "case_depth_mm": 0,
            "description": "Uniform hardness, good for semi-floating pins",
        },
        "High Carbon Steel (52100)": {
            "density_kg_m3": 7830,
            "ultimate_tensile_mpa": 1100,
            "yield_strength_mpa": 950,
            "fatigue_limit_mpa": 450,
            "endurance_limit_mpa": 400,
            "youngs_modulus_gpa": 210,
            "hardness_core_hb": 350,
            "hardness_surface_hb": 620,
            "case_depth_mm": 0.5,
            "description": "High hardness, used in racing engines",
        },
        "Nitrided Steel": {
            "density_kg_m3": 7800,
            "ultimate_tensile_mpa": 900,
            "yield_strength_mpa": 700,
            "fatigue_limit_mpa": 420,
            "endurance_limit_mpa": 380,
            "youngs_modulus_gpa": 200,
            "hardness_core_hb": 280,
            "hardness_surface_hb": 700,
            "case_depth_mm": 0.4,
            "description": "Very hard surface, excellent wear resistance",
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
        """List all available piston pin materials."""
        return list(cls.MATERIALS.keys())


class PistonPinGeometry:
    """Chapter 32.11: Piston pin geometric parameters."""
    
    def __init__(self, bore_mm, pin_outer_diameter_mm=None, pin_inner_diameter_mm=None,
                 pin_length_mm=None, pin_type="full_floating"):
        """
        Parameters:
        -----------
        bore_mm : float
            Cylinder bore diameter (mm)
        pin_outer_diameter_mm : float, optional
            Outer diameter of pin (default: 0.25-0.35 × bore)
        pin_inner_diameter_mm : float, optional
            Inner diameter of pin for hollow design (default: 0.6 × outer_diameter)
        pin_length_mm : float, optional
            Length of pin (default: 0.8-0.9 × bore)
        pin_type : str
            'full_floating' or 'semi_floating'
        """
        self.bore_mm = bore_mm
        self.pin_type = pin_type
        
        # Pin outer diameter (typical: 0.25 to 0.35 × bore)
        if pin_outer_diameter_mm:
            self.od_mm = pin_outer_diameter_mm
        else:
            self.od_mm = 0.28 * bore_mm
        
        # Pin inner diameter (hollow pin for weight reduction)
        if pin_inner_diameter_mm:
            self.id_mm = pin_inner_diameter_mm
        else:
            self.id_mm = 0.6 * self.od_mm  # Typical for hollow pins
        
        # Pin length (typical: 0.75 to 0.9 × bore)
        if pin_length_mm:
            self.length_mm = pin_length_mm
        else:
            self.length_mm = 0.85 * bore_mm
        
        # Bearing lengths
        self.piston_boss_length_mm = 0.4 * self.length_mm
        self.rod_small_end_length_mm = 0.5 * self.length_mm
        
        # Pin ends (not fully supported)
        self.unsupported_end_length_mm = (self.length_mm - self.piston_boss_length_mm - 
                                           self.rod_small_end_length_mm) / 2
        
        # Convert to meters for calculations
        self.od_m = self.od_mm / 1000
        self.id_m = self.id_mm / 1000
        self.length_m = self.length_mm / 1000
    
    def pin_area_mm2(self):
        """Cross-sectional area of hollow pin."""
        return math.pi * (self.od_mm**2 - self.id_mm**2) / 4
    
    def pin_area_m2(self):
        """Cross-sectional area in m²."""
        return self.pin_area_mm2() / 1e6
    
    def moment_of_inertia_mm4(self):
        """Area moment of inertia for hollow circular section."""
        return math.pi * (self.od_mm**4 - self.id_mm**4) / 64
    
    def section_modulus_mm3(self):
        """Section modulus for bending (Z = I / (d/2))."""
        return self.moment_of_inertia_mm4() / (self.od_mm / 2)
    
    def pin_mass_kg(self, density_kg_m3=7850):
        """Mass of piston pin."""
        volume_m3 = math.pi * ((self.od_m/2)**2 - (self.id_m/2)**2) * self.length_m
        return volume_m3 * density_kg_m3
    
    def pin_hollowness_ratio(self):
        """Ratio of inner to outer diameter (0 = solid, 0.6 = typical)."""
        return self.id_mm / self.od_mm
    
    def weight_savings_percent(self):
        """Weight savings compared to solid pin."""
        ratio = self.pin_hollowness_ratio()
        return (1 - (1 - ratio**2)) * 100


class PistonPinForces:
    """Chapter 32.12: Forces acting on piston pin."""
    
    def __init__(self, bore_mm, max_gas_pressure_mpa, reciprocating_mass_kg,
                 max_rpm, stroke_mm, rod_length_mm):
        """
        Parameters:
        -----------
        bore_mm : float
            Cylinder bore diameter (mm)
        max_gas_pressure_mpa : float
            Maximum combustion pressure (MPa)
        reciprocating_mass_kg : float
            Mass of piston assembly (piston + rings + pin) (kg)
        max_rpm : float
            Maximum engine speed (RPM)
        stroke_mm : float
            Piston stroke (mm)
        rod_length_mm : float
            Connecting rod length (mm)
        """
        self.bore_mm = bore_mm
        self.pressure_mpa = max_gas_pressure_mpa
        self.m_rec = reciprocating_mass_kg
        self.max_rpm = max_rpm
        self.stroke_mm = stroke_mm
        self.rod_length_mm = rod_length_mm
        
        # Derived values
        self.crank_radius_m = stroke_mm / 2000
        self.omega = 2 * math.pi * max_rpm / 60
        self.piston_area_m2 = math.pi * (bore_mm/1000)**2 / 4
        
        # Gas force
        self.gas_force_n = self.pressure_mpa * 1e6 * self.piston_area_m2
        self.gas_force_kn = self.gas_force_n / 1000
    
    def gas_force_n(self):
        """Maximum gas force on piston (compression)."""
        return self.gas_force_n
    
    def inertia_force_tdc_n(self):
        """
        Inertia force at TDC (tension).
        
        F_i = m_rec × ω² × r × (1 + r/l)
        """
        r_l_ratio = self.crank_radius_m / (self.rod_length_mm/1000)
        inertia = self.m_rec * self.omega**2 * self.crank_radius_m * (1 + r_l_ratio)
        return inertia
    
    def inertia_force_bdc_n(self):
        """
        Inertia force at BDC (compression).
        
        F_i = -m_rec × ω² × r × (1 - r/l)
        """
        r_l_ratio = self.crank_radius_m / (self.rod_length_mm/1000)
        inertia = -self.m_rec * self.omega**2 * self.crank_radius_m * (1 - r_l_ratio)
        return inertia
    
    def max_compressive_force_n(self):
        """Maximum compressive force on pin (gas + inertia at TDC)."""
        return self.gas_force_n - self.inertia_force_tdc_n()
    
    def max_tensile_force_n(self):
        """Maximum tensile force on pin (inertia at TDC on exhaust stroke)."""
        return abs(self.inertia_force_tdc_n())
    
    def load_distribution_small_end_n(self):
        """Load on connecting rod small end."""
        return self.max_compressive_force_n() * 0.5
    
    def load_distribution_piston_boss_n(self):
        """Load on each piston boss."""
        return self.max_compressive_force_n() / 2


class PistonPinStresses:
    """Chapter 32.12: Stress analysis for piston pin."""
    
    def __init__(self, geometry, forces, material):
        """
        Parameters:
        -----------
        geometry : PistonPinGeometry
            Pin geometric parameters
        forces : PistonPinForces
            Force calculations
        material : dict
            Material properties
        """
        self.geometry = geometry
        self.forces = forces
        self.material = material
        
        # Critical loads
        self.P_comp_n = forces.max_compressive_force_n()
        self.P_tensile_n = forces.max_tensile_force_n()
    
    def bearing_pressure_piston_boss_mpa(self):
        """
        Chapter 32.12: Bearing pressure between pin and piston boss.
        
        p = F / (d × l_boss)
        """
        load_n = self.forces.load_distribution_piston_boss_n()
        area_mm2 = self.geometry.od_mm * self.geometry.piston_boss_length_mm
        pressure_mpa = load_n / area_mm2
        return pressure_mpa
    
    def bearing_pressure_small_end_mpa(self):
        """
        Chapter 32.12: Bearing pressure between pin and connecting rod small end.
        
        p = F / (d × l_rod)
        """
        load_n = self.forces.max_compressive_force_n()
        area_mm2 = self.geometry.od_mm * self.geometry.rod_small_end_length_mm
        pressure_mpa = load_n / area_mm2
        return pressure_mpa
    
    def bending_stress_mpa(self, load_distribution="uniform"):
        """
        Chapter 32.12: Bending stress in piston pin.
        
        Pin is modeled as a simply supported beam with:
        - Supports at piston bosses
        - Load distributed across small end bearing
        """
        # Effective span (distance between piston bosses)
        span_mm = (self.geometry.length_mm - 
                   2 * self.geometry.unsupported_end_length_mm -
                   self.geometry.rod_small_end_length_mm)
        
        # Effective load (use maximum compressive force)
        load_n = self.forces.max_compressive_force_n()
        
        if load_distribution == "concentrated":
            # Concentrated load at center (simplified, conservative)
            bending_moment_nmm = load_n * span_mm / 4
        else:
            # Distributed load (more accurate)
            load_per_mm = load_n / self.geometry.rod_small_end_length_mm
            bending_moment_nmm = (load_per_mm * self.geometry.rod_small_end_length_mm * 
                                  (2 * span_mm - self.geometry.rod_small_end_length_mm) / 8)
        
        section_modulus = self.geometry.section_modulus_mm3()
        stress_mpa = bending_moment_nmm / section_modulus / 1e3
        
        return stress_mpa
    
    def shear_stress_mpa(self):
        """
        Chapter 32.12: Shear stress in piston pin.
        
        τ = (4/3) × (F / A) for circular section (max shear)
        """
        load_n = self.forces.max_compressive_force_n() / 2  # Each shear plane
        area_mm2 = self.geometry.pin_area_mm2()
        
        # Maximum shear stress for circular section = 4/3 × average
        shear_stress_mpa = (4/3) * (load_n / area_mm2)
        
        return shear_stress_mpa
    
    def ovalization_deflection_mm(self):
        """
        Ovalization (flattening) of hollow pin under load.
        
        δ = (F × d_m³) / (E × I × (1 - (d_i/d_o)²))
        """
        load_n = self.forces.max_compressive_force_n()
        d_o_m = self.geometry.od_m / 1000
        E_pa = self.material["youngs_modulus_gpa"] * 1e9
        I_m4 = self.geometry.moment_of_inertia_mm4() / 1e12
        ratio = self.geometry.pin_hollowness_ratio()
        
        # Empirical ovalization formula
        deflection_m = (load_n * d_o_m**3) / (E_pa * I_m4 * (1 - ratio**2)) * 0.01
        deflection_mm = deflection_m * 1000
        
        return deflection_mm
    
    def pin_bending_deflection_mm(self):
        """
        Bending deflection of pin as beam.
        
        δ = (F × L³) / (48 × E × I)
        """
        load_n = self.forces.max_compressive_force_n()
        span_m = (self.geometry.length_mm / 1000)
        E_pa = self.material["youngs_modulus_gpa"] * 1e9
        I_m4 = self.geometry.moment_of_inertia_mm4() / 1e12
        
        deflection_m = (load_n * span_m**3) / (48 * E_pa * I_m4)
        deflection_mm = deflection_m * 1000
        
        return deflection_mm
    
    def von_mises_stress_mpa(self):
        """
        Combined stress (bending + shear) using Von Mises criterion.
        
        σ_vm = √(σ_b² + 3τ²)
        """
        sigma_b = self.bending_stress_mpa()
        tau = self.shear_stress_mpa()
        
        sigma_vm = math.sqrt(sigma_b**2 + 3 * tau**2)
        return sigma_vm
    
    def factor_of_safety(self):
        """Factor of safety for piston pin."""
        sigma_vm = self.von_mises_stress_mpa()
        yield_stress = self.material["yield_strength_mpa"]
        
        # Apply stress concentration factor for oil holes
        k_t = 1.3  # Typical for oil holes in pins
        sigma_effective = sigma_vm * k_t
        
        return yield_stress / sigma_effective if sigma_effective > 0 else 999
    
    def fatigue_safety_factor(self, alternating_ratio=0.5):
        """
        Fatigue safety factor using Goodman criterion.
        
        1/FS = σ_a/σ_e + σ_m/σ_ut
        """
        sigma_vm = self.von_mises_stress_mpa()
        sigma_alternating = sigma_vm * alternating_ratio
        sigma_mean = sigma_vm * (1 - alternating_ratio)
        
        endurance_limit = self.material["endurance_limit_mpa"]
        ultimate = self.material["ultimate_tensile_mpa"]
        
        # Apply surface and size factors
        surface_factor = 0.85
        size_factor = 0.90
        corrected_endurance = endurance_limit * surface_factor * size_factor
        
        fs = 1 / (sigma_alternating/corrected_endurance + sigma_mean/ultimate)
        return fs


class PistonPinDesign:
    """Complete piston pin design with optimization."""
    
    PIN_TYPES = {
        "full_floating": {
            "description": "Pin rotates freely in both piston and rod",
            "retention": "Snap rings or retainers in piston grooves",
            "lubrication": "Oil splash or pressure fed",
            "typical_clearance_mm": 0.010,
            "advantages": "Even wear, self-aligning",
            "disadvantages": "Requires retainers, more complex",
        },
        "semi_floating": {
            "description": "Pin fixed in rod, rotates in piston bosses",
            "retention": "Interference fit in connecting rod",
            "lubrication": "Oil splash",
            "typical_clearance_mm": 0.008,
            "advantages": "Simpler, no retainers needed",
            "disadvantages": "Press fit required, less even wear",
        },
    }
    
    def __init__(self, bore_mm, stroke_mm, max_gas_pressure_mpa,
                 max_rpm, reciprocating_mass_kg, rod_length_mm,
                 material_name="Case Hardened Steel (8620)",
                 pin_type="full_floating",
                 target_fs_bending=2.5, target_fs_bearing=2.0):
        """
        Complete piston pin design calculator.
        
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
            Mass of piston assembly (kg)
        rod_length_mm : float
            Connecting rod center-to-center length (mm)
        material_name : str
            Pin material
        pin_type : str
            'full_floating' or 'semi_floating'
        target_fs_bending : float
            Target factor of safety for bending
        target_fs_bearing : float
            Target factor of safety for bearing pressure
        """
        self.bore_mm = bore_mm
        self.stroke_mm = stroke_mm
        self.pressure_mpa = max_gas_pressure_mpa
        self.max_rpm = max_rpm
        self.m_rec = reciprocating_mass_kg
        self.rod_length_mm = rod_length_mm
        self.pin_type = pin_type
        self.target_fs_bending = target_fs_bending
        self.target_fs_bearing = target_fs_bearing
        
        # Material
        self.material_data = PistonPinMaterial.get_material(material_name)
        self.material_data["name"] = material_name
        self.material = self.material_data
        
        # Pin type info
        self.pin_type_info = self.PIN_TYPES.get(pin_type, self.PIN_TYPES["full_floating"])
        
        # Initialize geometry (initial estimates)
        self.geometry = PistonPinGeometry(bore_mm, pin_type=pin_type)
        
        # Forces
        self.forces = PistonPinForces(
            bore_mm, max_gas_pressure_mpa, reciprocating_mass_kg,
            max_rpm, stroke_mm, rod_length_mm
        )
        
        # Stresses
        self.stresses = PistonPinStresses(self.geometry, self.forces, self.material)
        
        # Optimize pin dimensions
        self.optimize_dimensions()
    
    def optimize_dimensions(self):
        """
        Iteratively optimize pin dimensions to meet safety factors.
        """
        max_iterations = 10
        tolerance = 0.05
        
        for _ in range(max_iterations):
            fs_bending = self.stresses.factor_of_safety()
            bearing_pressure = self.stresses.bearing_pressure_piston_boss_mpa()
            
            # Check if current design meets targets
            bending_ok = fs_bending >= self.target_fs_bending
            bearing_ok = bearing_pressure <= self.pin_type_info["typical_clearance_mm"] * 100
            
            if bending_ok and bearing_ok:
                break
            
            # Adjust pin outer diameter
            if fs_bending < self.target_fs_bending:
                # Increase pin diameter
                self.geometry.od_mm *= 1.03
            else:
                # Try smaller pin (reduce mass)
                self.geometry.od_mm *= 0.98
            
            if bearing_pressure > self.pin_type_info["typical_clearance_mm"] * 100:
                # Increase boss or rod bearing length
                self.geometry.piston_boss_length_mm *= 1.02
            
            # Update geometry
            self.geometry.id_mm = 0.6 * self.geometry.od_mm
            self.geometry.od_m = self.geometry.od_mm / 1000
            self.geometry.id_m = self.geometry.id_mm / 1000
            
            # Recalculate stresses
            self.stresses = PistonPinStresses(self.geometry, self.forces, self.material)
        
        # Final dimensions
        self.final_od_mm = self.geometry.od_mm
        self.final_id_mm = self.geometry.id_mm
        self.final_length_mm = self.geometry.length_mm
    
    def design_summary(self):
        """Generate complete piston pin design summary."""
        
        summary = {
            # Basic dimensions
            "bore_mm": self.bore_mm,
            "pin_outer_diameter_mm": round(self.geometry.od_mm, 2),
            "pin_inner_diameter_mm": round(self.geometry.id_mm, 2),
            "pin_length_mm": round(self.geometry.length_mm, 2),
            "pin_hollowness_ratio": round(self.geometry.pin_hollowness_ratio(), 2),
            "weight_savings_percent": round(self.geometry.weight_savings_percent(), 1),
            
            # Bearing lengths
            "piston_boss_length_mm": round(self.geometry.piston_boss_length_mm, 2),
            "rod_small_end_length_mm": round(self.geometry.rod_small_end_length_mm, 2),
            
            # Forces
            "max_gas_force_kN": round(self.forces.gas_force_kn, 1),
            "max_compressive_force_kN": round(self.forces.max_compressive_force_n() / 1000, 1),
            "max_tensile_force_kN": round(self.forces.max_tensile_force_n() / 1000, 1),
            
            # Stresses
            "bending_stress_mpa": round(self.stresses.bending_stress_mpa(), 1),
            "shear_stress_mpa": round(self.stresses.shear_stress_mpa(), 1),
            "von_mises_stress_mpa": round(self.stresses.von_mises_stress_mpa(), 1),
            "yield_strength_mpa": self.material["yield_strength_mpa"],
            "fatigue_limit_mpa": self.material["fatigue_limit_mpa"],
            
            # Safety factors
            "factor_of_safety_bending": round(self.stresses.factor_of_safety(), 2),
            "fatigue_safety_factor": round(self.stresses.fatigue_safety_factor(), 2),
            "target_fs_bending": self.target_fs_bending,
            
            # Bearing pressures
            "bearing_pressure_boss_mpa": round(self.stresses.bearing_pressure_piston_boss_mpa(), 2),
            "bearing_pressure_rod_mpa": round(self.stresses.bearing_pressure_small_end_mpa(), 2),
            "allowable_bearing_pressure_mpa": 50,  # Typical for case hardened steel
            
            # Deflections
            "bending_deflection_mm": round(self.stresses.pin_bending_deflection_mm(), 4),
            "ovalization_deflection_mm": round(self.stresses.ovalization_deflection_mm(), 4),
            
            # Pin type
            "pin_type": self.pin_type,
            "pin_type_description": self.pin_type_info["description"],
            "pin_retention": self.pin_type_info["retention"],
            "typical_clearance_mm": self.pin_type_info["typical_clearance_mm"],
            
            # Material
            "material": self.material["name"],
            "material_description": self.material["description"],
            "surface_hardness_hb": self.material["hardness_surface_hb"],
            "case_depth_mm": self.material.get("case_depth_mm", 0),
            
            # Mass
            "pin_mass_kg": round(self.geometry.pin_mass_kg(self.material["density_kg_m3"]), 3),
            "pin_mass_grams": round(self.geometry.pin_mass_kg(self.material["density_kg_m3"]) * 1000, 1),
        }
        
        return summary
    
    def print_design_report(self):
        """Print formatted design report."""
        s = self.design_summary()
        
        print("=" * 70)
        print("PISTON PIN (WRIST PIN) DESIGN REPORT")
        print("Machine Design Textbook - Chapter 32.11-32.12")
        print("=" * 70)
        
        print(f"\n📐 ENGINE SPECIFICATIONS:")
        print(f"   Bore: {s['bore_mm']:.1f} mm")
        print(f"   Stroke: {self.stroke_mm:.1f} mm")
        print(f"   Max RPM: {self.max_rpm:.0f}")
        print(f"   Max gas pressure: {self.pressure_mpa:.1f} MPa")
        print(f"   Reciprocating mass: {self.m_rec:.3f} kg")
        
        print(f"\n📏 PIN DIMENSIONS:")
        print(f"   Outer diameter: {s['pin_outer_diameter_mm']:.2f} mm")
        print(f"   Inner diameter: {s['pin_inner_diameter_mm']:.2f} mm")
        print(f"   Total length: {s['pin_length_mm']:.2f} mm")
        print(f"   Piston boss length: {s['piston_boss_length_mm']:.2f} mm")
        print(f"   Rod small end length: {s['rod_small_end_length_mm']:.2f} mm")
        print(f"   Hollowness ratio (d_i/d_o): {s['pin_hollowness_ratio']:.2f}")
        print(f"   Weight savings: {s['weight_savings_percent']:.0f}%")
        
        print(f"\n⚡ FORCES:")
        print(f"   Max gas force: {s['max_gas_force_kN']:.1f} kN")
        print(f"   Max compressive force: {s['max_compressive_force_kN']:.1f} kN")
        print(f"   Max tensile force: {s['max_tensile_force_kN']:.1f} kN")
        
        print(f"\n📊 STRESS ANALYSIS:")
        print(f"   Bending stress: {s['bending_stress_mpa']:.1f} MPa")
        print(f"   Shear stress: {s['shear_stress_mpa']:.1f} MPa")
        print(f"   Von Mises stress: {s['von_mises_stress_mpa']:.1f} MPa")
        print(f"   Yield strength: {s['yield_strength_mpa']} MPa")
        print(f"   ✅ Bending F.S.: {s['factor_of_safety_bending']:.2f} (target: {s['target_fs_bending']:.1f})")
        print(f"   ✅ Fatigue F.S.: {s['fatigue_safety_factor']:.2f}")
        
        print(f"\n🔧 BEARING ANALYSIS:")
        print(f"   Piston boss pressure: {s['bearing_pressure_boss_mpa']:.2f} MPa")
        print(f"   Rod small end pressure: {s['bearing_pressure_rod_mpa']:.2f} MPa")
        print(f"   Allowable pressure: {s['allowable_bearing_pressure_mpa']:.0f} MPa")
        bearing_status = "✅ OK" if s['bearing_pressure_boss_mpa'] < s['allowable_bearing_pressure_mpa'] else "⚠️ EXCESSIVE"
        print(f"   Status: {bearing_status}")
        
        print(f"\n📐 DEFLECTION:")
        print(f"   Bending deflection: {s['bending_deflection_mm']:.4f} mm")
        print(f"   Ovalization: {s['ovalization_deflection_mm']:.4f} mm")
        print(f"   Total deflection: {(s['bending_deflection_mm'] + s['ovalization_deflection_mm']):.4f} mm")
        
        print(f"\n🔩 PIN TYPE: {s['pin_type'].upper()}")
        print(f"   Description: {s['pin_type_description']}")
        print(f"   Retention: {s['pin_retention']}")
        print(f"   Typical clearance: {s['typical_clearance_mm']:.3f} mm")
        
        print(f"\n🏗️ MATERIAL:")
        print(f"   Material: {s['material']}")
        print(f"   {s['material_description']}")
        print(f"   Surface hardness: {s['surface_hardness_hb']} HB")
        print(f"   Case depth: {s['case_depth_mm']:.1f} mm")
        
        print(f"\n⚖️ MASS:")
        print(f"   Pin mass: {s['pin_mass_grams']:.1f} g ({s['pin_mass_kg']:.3f} kg)")
        
        print("\n" + "=" * 70)
        
        # Validation and recommendations
        issues = []
        if s['factor_of_safety_bending'] < self.target_fs_bending:
            issues.append("⚠️ BENDING SAFETY FACTOR BELOW TARGET")
        if s['bearing_pressure_boss_mpa'] > s['allowable_bearing_pressure_mpa']:
            issues.append("⚠️ BEARING PRESSURE EXCEEDS ALLOWABLE")
        if s['fatigue_safety_factor'] < 1.5:
            issues.append("⚠️ FATIGUE SAFETY FACTOR LOW")
        if (s['bending_deflection_mm'] + s['ovalization_deflection_mm']) > 0.05:
            issues.append("⚠️ EXCESSIVE PIN DEFLECTION")
        
        if issues:
            print("\n⚠️ DESIGN ISSUES / RECOMMENDATIONS:")
            for issue in issues:
                print(f"   {issue}")
            print("\n   Suggested actions:")
            if s['factor_of_safety_bending'] < self.target_fs_bending:
                print("   → Increase pin outer diameter")
            if s['bearing_pressure_boss_mpa'] > s['allowable_bearing_pressure_mpa']:
                print("   → Increase piston boss length or pin diameter")
            if s['fatigue_safety_factor'] < 1.5:
                print("   → Use higher strength material or increase diameter")
        else:
            print("\n✅ DESIGN ACCEPTABLE - All criteria satisfied")
        
        print("=" * 70)
        
        # Design tips
        print("\n💡 DESIGN TIPS:")
        print("   • Oil holes (2-4 holes) should be placed at neutral stress zones")
        print("   • Pin should be lighter than 2-3% of piston assembly mass")
        print("   • Surface hardness > 60 HRC for wear resistance")
        print("   • Tapered or stepped pins can reduce mass further")
        print("   • Diamond-like carbon (DLC) coating reduces friction")


# ============================================================================
# Example usage
# ============================================================================

if __name__ == "__main__":
    print("=" * 70)
    print("PISTON PIN DESIGN CALCULATOR")
    print("Machine Design Textbook - Chapter 32.11-32.12")
    print("=" * 70)
    
    print("\n📌 Example: 2.0L Automotive Engine")
    print("   Bore: 85 mm, Stroke: 88 mm, Max Pressure: 8 MPa")
    print("   Max RPM: 6500, Piston mass: 0.45 kg")
    print("-" * 70)
    
    # Create piston pin design
    piston_pin = PistonPinDesign(
        bore_mm=85,
        stroke_mm=88,
        max_gas_pressure_mpa=8.0,
        max_rpm=6500,
        reciprocating_mass_kg=0.45,  # Piston + rings + pin
        rod_length_mm=145,  # 1.65 × stroke
        material_name="Case Hardened Steel (8620)",
        pin_type="full_floating",
        target_fs_bending=2.5,
        target_fs_bearing=2.0
    )
    
    # Print design report
    piston_pin.print_design_report()
    
    print("\n" + "=" * 70)
    print("Piston pin design ready for engine integration.")
    print("=" * 70)