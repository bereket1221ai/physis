"""
valve.py - Chapter 32.22: Valve and Valve Gear Mechanism Design

Based on Machine Design textbook (R.S. Khurmi, J.K. Gupta)
Sections covered:
- 32.22: Valves

Additional references:
- Valve types (poppet, sleeve, rotary)
- Valve materials and heat treatment
- Valve spring design
- Valve timing and lift profiles
- Port flow analysis
- Valve train dynamics
- Seat pressure and sealing
- Cooling and lubrication
"""

import math


class ValveMaterial:
    """Material properties for engine valves."""
    
    MATERIALS = {
        "Silicon Chrome Steel (21-4N)": {
            "density_kg_m3": 7700,
            "ultimate_tensile_mpa": 950,
            "yield_strength_mpa": 800,
            "fatigue_limit_mpa": 350,
            "youngs_modulus_gpa": 210,
            "hardness_hb": 350,
            "max_temperature_c": 850,
            "thermal_conductivity_w_mk": 22,
            "coefficient_thermal_expansion_1e6": 11,
            "description": "Common exhaust valve material",
            "application": "Exhaust valves",
        },
        "Inconel (751)": {
            "density_kg_m3": 8200,
            "ultimate_tensile_mpa": 1200,
            "yield_strength_mpa": 1000,
            "fatigue_limit_mpa": 450,
            "youngs_modulus_gpa": 214,
            "hardness_hb": 380,
            "max_temperature_c": 980,
            "thermal_conductivity_w_mk": 11,
            "coefficient_thermal_expansion_1e6": 12,
            "description": "High temperature exhaust valves (racing/turbo)",
            "application": "Exhaust valves",
        },
        "Nimonic (80A)": {
            "density_kg_m3": 8100,
            "ultimate_tensile_mpa": 1100,
            "yield_strength_mpa": 900,
            "fatigue_limit_mpa": 420,
            "youngs_modulus_gpa": 211,
            "hardness_hb": 360,
            "max_temperature_c": 950,
            "thermal_conductivity_w_mk": 13,
            "coefficient_thermal_expansion_1e6": 12,
            "description": "High temperature alloy for extreme conditions",
            "application": "Exhaust valves",
        },
        "Martensitic Steel (X45CrSi9-3)": {
            "density_kg_m3": 7600,
            "ultimate_tensile_mpa": 880,
            "yield_strength_mpa": 720,
            "fatigue_limit_mpa": 330,
            "youngs_modulus_gpa": 208,
            "hardness_hb": 320,
            "max_temperature_c": 800,
            "thermal_conductivity_w_mk": 24,
            "coefficient_thermal_expansion_1e6": 11,
            "description": "Intake valve material",
            "application": "Intake valves",
        },
        "Titanium (Ti-6Al-4V)": {
            "density_kg_m3": 4430,
            "ultimate_tensile_mpa": 950,
            "yield_strength_mpa": 880,
            "fatigue_limit_mpa": 480,
            "youngs_modulus_gpa": 114,
            "hardness_hb": 330,
            "max_temperature_c": 550,
            "thermal_conductivity_w_mk": 7,
            "coefficient_thermal_expansion_1e6": 9,
            "description": "High performance intake valves, lightweight",
            "application": "Intake valves (racing)",
        },
        "Stellite (Faced)": {
            "density_kg_m3": 8400,
            "ultimate_tensile_mpa": 900,
            "yield_strength_mpa": 700,
            "fatigue_limit_mpa": 380,
            "youngs_modulus_gpa": 230,
            "hardness_hb": 480,
            "max_temperature_c": 850,
            "thermal_conductivity_w_mk": 15,
            "coefficient_thermal_expansion_1e6": 13,
            "description": "Hard facing for valve seats",
            "application": "Valve face coating",
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
        """List all available valve materials."""
        return list(cls.MATERIALS.keys())


class ValveGeometry:
    """Valve geometric parameters."""
    
    def __init__(self, head_diameter_mm, stem_diameter_mm=None, valve_type="poppet"):
        """
        Parameters:
        -----------
        head_diameter_mm : float
            Diameter of valve head (mm)
        stem_diameter_mm : float, optional
            Diameter of valve stem (mm)
        valve_type : str
            'poppet', 'sleeve', 'rotary'
        """
        self.head_diameter_mm = head_diameter_mm
        self.head_diameter_m = head_diameter_mm / 1000
        self.valve_type = valve_type
        
        # Stem diameter (typical: 0.16 to 0.2 × head diameter)
        if stem_diameter_mm:
            self.stem_diameter_mm = stem_diameter_mm
        else:
            self.stem_diameter_mm = 0.18 * head_diameter_mm
        
        self.stem_diameter_m = self.stem_diameter_mm / 1000
        
        # Valve seat angles
        self.seat_angle_deg = 45  # Typical: 30°, 45°, 60°
        self.seat_angle_rad = math.radians(self.seat_angle_deg)
        
        # Margin thickness (top of valve head)
        self.margin_thickness_mm = 0.05 * head_diameter_mm
        self.margin_thickness_m = self.margin_thickness_mm / 1000
        
        # Valve head thickness
        self.head_thickness_mm = 0.1 * head_diameter_mm
        self.head_thickness_m = self.head_thickness_mm / 1000
        
        # Stem length (approximate)
        self.stem_length_mm = 5 * head_diameter_mm
        self.stem_length_m = self.stem_length_mm / 1000
        
        # Seat width
        self.seat_width_mm = 0.03 * head_diameter_mm
        self.seat_width_m = self.seat_width_mm / 1000
        
        # Valve lift (port opening)
        self.max_lift_mm = 0.25 * head_diameter_mm
        self.max_lift_m = self.max_lift_mm / 1000
    
    def valve_head_area_mm2(self):
        """Area of valve head."""
        return math.pi * (self.head_diameter_mm**2) / 4
    
    def valve_head_area_m2(self):
        """Area of valve head in m²."""
        return self.valve_head_area_mm2() / 1e6
    
    def valve_stem_area_mm2(self):
        """Cross-sectional area of valve stem."""
        return math.pi * (self.stem_diameter_mm**2) / 4
    
    def valve_stem_area_m2(self):
        """Valve stem area in m²."""
        return self.valve_stem_area_mm2() / 1e6
    
    def curtain_area_mm2(self, lift_mm=None):
        """
        Curtain area (flow area when valve is open).
        
        A_curtain = π × D_head × lift × cos(seat_angle)
        """
        if lift_mm is None:
            lift_mm = self.max_lift_mm
        
        area = math.pi * self.head_diameter_mm * lift_mm * math.cos(self.seat_angle_rad)
        return max(area, 0)
    
    def port_area_mm2(self):
        """Port cross-sectional area (should match curtain area at max lift)."""
        return self.curtain_area_mm2(self.max_lift_mm)
    
    def flow_coefficient(self, lift_mm=None):
        """
        Estimated flow coefficient (Cd) based on lift/diameter ratio.
        """
        if lift_mm is None:
            lift_mm = self.max_lift_mm
        
        lift_ratio = lift_mm / self.head_diameter_mm
        
        if lift_ratio < 0.1:
            return 0.6
        elif lift_ratio < 0.2:
            return 0.65
        elif lift_ratio < 0.3:
            return 0.7
        else:
            return 0.72
    
    def valve_mass_kg(self, density_kg_m3=7800):
        """Estimate valve mass."""
        # Head volume (simplified as disc)
        head_volume_m3 = (self.valve_head_area_m2() * self.head_thickness_m)
        # Stem volume (cylinder)
        stem_volume_m3 = (self.valve_stem_area_m2() * self.stem_length_m)
        
        total_volume = head_volume_m3 + stem_volume_m3
        return total_volume * density_kg_m3


class ValveForces:
    """Forces acting on valve and valve train."""
    
    def __init__(self, head_diameter_mm, max_cylinder_pressure_mpa, max_rpm,
                 valve_mass_kg, valve_spring_rate_n_mm=None):
        """
        Parameters:
        -----------
        head_diameter_mm : float
            Valve head diameter (mm)
        max_cylinder_pressure_mpa : float
            Maximum cylinder pressure (MPa)
        max_rpm : float
            Maximum engine speed (RPM)
        valve_mass_kg : float
            Mass of valve (kg)
        valve_spring_rate_n_mm : float, optional
            Valve spring rate (N/mm)
        """
        self.head_diameter_mm = head_diameter_mm
        self.head_diameter_m = head_diameter_mm / 1000
        self.pressure_mpa = max_cylinder_pressure_mpa
        self.max_rpm = max_rpm
        self.valve_mass_kg = valve_mass_kg
        self.spring_rate_n_mm = valve_spring_rate_n_mm or 30  # Typical N/mm
        
        # Valve head area
        self.head_area_m2 = math.pi * (self.head_diameter_m**2) / 4
        
        # Angular velocity
        self.omega = 2 * math.pi * max_rpm / 60
    
    def gas_pressure_force_n(self):
        """
        Force from cylinder gas pressure on valve head.
        
        F_gas = P_max × A_head
        """
        return self.pressure_mpa * 1e6 * self.head_area_m2
    
    def inertia_force_n(self, acceleration_m_s2):
        """
        Inertia force from valve motion.
        
        F_inertia = m_valve × a
        """
        return self.valve_mass_kg * acceleration_m_s2
    
    def spring_force_n(self, preload_mm=20, lift_mm=10):
        """
        Spring force at given lift.
        
        F_spring = k × (preload + lift)
        """
        return self.spring_rate_n_mm * (preload_mm + lift_mm)
    
    def seat_force_n(self, preload_mm=20):
        """
        Force on valve seat when closed.
        
        F_seat = k × preload + gas_pressure
        """
        return self.spring_force_n(preload_mm, 0) + self.gas_pressure_force_n()
    
    def max_valve_acceleration_m_s2(self, cam_profile="typical"):
        """
        Maximum valve acceleration based on cam profile.
        
        Typical: 2000-4000 m/s² for performance engines
        """
        if cam_profile == "race":
            return 4000
        elif cam_profile == "performance":
            return 3000
        else:
            return 2000
    
    def max_spring_force_n(self, preload_mm=20, lift_mm=10):
        """
        Maximum spring force (at max lift + preload).
        """
        return self.spring_force_n(preload_mm, lift_mm)


class ValveSpring:
    """Valve spring design and analysis."""
    
    def __init__(self, wire_diameter_mm, mean_coil_diameter_mm, active_coils,
                 free_length_mm, installed_length_mm, material_gpa=80):
        """
        Parameters:
        -----------
        wire_diameter_mm : float
            Spring wire diameter (mm)
        mean_coil_diameter_mm : float
            Mean diameter of spring coils (mm)
        active_coils : int
            Number of active coils
        free_length_mm : float
            Free length of spring (mm)
        installed_length_mm : float
            Installed length (preload) (mm)
        material_gpa : float
            Shear modulus of spring material (GPa)
        """
        self.d_mm = wire_diameter_mm
        self.d_m = wire_diameter_mm / 1000
        self.D_mm = mean_coil_diameter_mm
        self.D_m = mean_coil_diameter_mm / 1000
        self.N = active_coils
        self.L_free_mm = free_length_mm
        self.L_installed_mm = installed_length_mm
        self.G_pa = material_gpa * 1e9
        
        # Spring index
        self.C = self.D_mm / self.d_mm
        
        # Wahl factor (stress correction)
        self.K_w = (4 * self.C - 1) / (4 * self.C - 4) + 0.615 / self.C
    
    def spring_rate_n_mm(self):
        """
        Spring rate (stiffness).
        
        k = G × d⁴ / (8 × D³ × N)
        """
        k_n_m = (self.G_pa * self.d_m**4) / (8 * self.D_m**3 * self.N)
        return k_n_m / 1000  # Convert to N/mm
    
    def preload_mm(self):
        """Preload (compression from free length to installed length)."""
        return self.L_free_mm - self.L_installed_mm
    
    def max_compression_mm(self, max_lift_mm):
        """Maximum compression (preload + max lift)."""
        return self.preload_mm() + max_lift_mm
    
    def preload_force_n(self):
        """Force at installed height (closed valve)."""
        return self.spring_rate_n_mm() * self.preload_mm()
    
    def max_force_n(self, max_lift_mm):
        """Maximum spring force (at full lift)."""
        return self.spring_rate_n_mm() * self.max_compression_mm(max_lift_mm)
    
    def maximum_shear_stress_mpa(self, max_lift_mm):
        """
        Maximum shear stress in spring wire.
        
        τ_max = K_w × (8 × F × D) / (π × d³)
        """
        F_max = self.max_force_n(max_lift_mm) * 1000  # Convert to N
        tau_pa = (self.K_w * 8 * F_max * self.D_m) / (math.pi * self.d_m**3)
        return tau_pa / 1e6
    
    def solid_length_mm(self):
        """Length when spring is fully compressed (coils touching)."""
        return self.N * self.d_mm
    
    def safety_factor_clearance(self, max_lift_mm):
        """Safety factor against coil bind."""
        max_compression = self.max_compression_mm(max_lift_mm)
        return (self.L_free_mm - self.solid_length_mm()) / max_compression
    
    def natural_frequency_hz(self):
        """
        Natural frequency of spring (avoid resonance).
        
        f_n = (d / (π × D² × N)) × √(G / (2 × ρ))
        """
        rho = 7850  # Density of steel (kg/m³)
        d = self.d_m
        D = self.D_m
        G = self.G_pa
        
        freq = (d / (math.pi * D**2 * self.N)) * math.sqrt(G / (2 * rho))
        return freq
    
    def valve_float_rpm(self, max_lift_mm):
        """
        RPM at which valve float occurs.
        
        Engine speed where inertia forces exceed spring force.
        """
        spring_force = self.max_force_n(max_lift_mm)
        # Simplified critical RPM estimation
        # Varies with valve train design, rough estimate
        return math.sqrt(spring_force / 0.0001) * 60


class ValveSeat:
    """Valve seat design and analysis."""
    
    def __init__(self, head_diameter_mm, seat_angle_deg=45, seat_width_mm=None):
        """
        Parameters:
        -----------
        head_diameter_mm : float
            Valve head diameter (mm)
        seat_angle_deg : float
            Seat angle (degrees) - 30, 45, or 60
        seat_width_mm : float, optional
            Seat contact width (mm)
        """
        self.head_diameter_mm = head_diameter_mm
        self.head_diameter_m = head_diameter_mm / 1000
        self.seat_angle_deg = seat_angle_deg
        self.seat_angle_rad = math.radians(seat_angle_deg)
        
        if seat_width_mm:
            self.seat_width_mm = seat_width_mm
        else:
            self.seat_width_mm = 0.03 * head_diameter_mm
        
        self.seat_width_m = self.seat_width_mm / 1000
    
    def seat_contact_area_mm2(self):
        """Contact area of valve seat."""
        # Average diameter of seat contact
        avg_diameter_mm = self.head_diameter_mm - self.seat_width_mm
        return math.pi * avg_diameter_mm * self.seat_width_mm
    
    def seat_contact_area_m2(self):
        """Contact area in m²."""
        return self.seat_contact_area_mm2() / 1e6
    
    def seat_pressure_mpa(self, closing_force_n):
        """
        Seat contact pressure.
        
        p = F_seat / A_contact
        """
        area_m2 = self.seat_contact_area_m2()
        pressure_pa = closing_force_n / area_m2
        return pressure_pa / 1e6
    
    def allowable_seat_pressure_mpa(self, material):
        """
        Allowable seat pressure based on material.
        """
        if "Stellite" in material.get("name", ""):
            return 200
        elif "Titanium" in material.get("name", ""):
            return 150
        else:
            return 120
    
    def recommended_interference_mm(self):
        """
        Recommended interference fit between valve and seat.
        """
        return 0.05  # mm typical for interference fit


class ValveTiming:
    """Valve timing and lift profile."""
    
    def __init__(self, max_lift_mm, cam_duration_deg=260, lobe_center_angle_deg=110,
                 opening_before_tdc_deg=10, closing_after_bdc_deg=10):
        """
        Parameters:
        -----------
        max_lift_mm : float
            Maximum valve lift (mm)
        cam_duration_deg : float
            Cam duration (degrees of crank rotation)
        lobe_center_angle_deg : float
            Lobe center angle (degrees)
        opening_before_tdc_deg : float
            Intake valve opening before TDC (degrees)
        closing_after_bdc_deg : float
            Intake valve closing after BDC (degrees)
        """
        self.max_lift_mm = max_lift_mm
        self.duration_deg = cam_duration_deg
        self.lobe_center = lobe_center_angle_deg
        self.opening_before_tdc = opening_before_tdc_deg
        self.closing_after_bdc = closing_after_bdc_deg
        
        # Derived values
        self.opening_angle_deg = 360 - opening_before_tdc_deg
        self.closing_angle_deg = 180 + closing_after_bdc_deg
    
    def lift_at_crank_angle_mm(self, crank_angle_deg):
        """
        Calculate valve lift at given crank angle.
        
        Simplified polynomial cam profile.
        """
        # Normalize angle within cam duration
        cam_angle = crank_angle_deg * 0.5  # Cam rotates at half crank speed
        
        if cam_angle < 0 or cam_angle > self.duration_deg:
            return 0
        
        # Use symmetric cam profile (simplified)
        x = (cam_angle / self.duration_deg) * 2 - 1
        # Polynomial: 1 - x^2 (simplified)
        lift_ratio = 1 - x**2
        
        return self.max_lift_mm * lift_ratio
    
    def overlap_period_deg(self, intake_opening, exhaust_closing):
        """
        Valve overlap period (both valves open).
        """
        return intake_opening + exhaust_closing
    
    def lift_area_mm2_deg(self):
        """
        Area under lift curve (flow potential).
        
        Approximated by 2/3 × max_lift × duration
        """
        return (2/3) * self.max_lift_mm * self.duration_deg


class ValveComplete:
    """Complete valve design integrating all components."""
    
    def __init__(self, bore_mm, head_diameter_mm, max_cylinder_pressure_mpa,
                 max_rpm, valve_type="poppet", application="intake",
                 material_name=None):
        """
        Complete valve design calculator.
        
        Parameters:
        -----------
        bore_mm : float
            Cylinder bore diameter (mm)
        head_diameter_mm : float
            Valve head diameter (mm)
        max_cylinder_pressure_mpa : float
            Maximum cylinder pressure (MPa)
        max_rpm : float
            Maximum engine speed (RPM)
        valve_type : str
            'poppet', 'sleeve', 'rotary'
        application : str
            'intake' or 'exhaust'
        material_name : str, optional
            Valve material (auto-selected based on application if not provided)
        """
        self.bore_mm = bore_mm
        self.head_diameter_mm = head_diameter_mm
        self.pressure_mpa = max_cylinder_pressure_mpa
        self.max_rpm = max_rpm
        self.valve_type = valve_type
        self.application = application
        
        # Auto-select material based on application
        if material_name:
            self.material_data = ValveMaterial.get_material(material_name)
        else:
            if application == "exhaust":
                default_material = "Silicon Chrome Steel (21-4N)"
            else:
                default_material = "Martensitic Steel (X45CrSi9-3)"
            self.material_data = ValveMaterial.get_material(default_material)
        
        self.material_data["name"] = material_name or default_material
        self.material = self.material_data
        
        # Geometry
        self.geometry = ValveGeometry(head_diameter_mm, valve_type=valve_type)
        
        # Initial valve mass estimate
        self.valve_mass_kg = self.geometry.valve_mass_kg(self.material["density_kg_m3"])
        
        # Forces
        self.forces = ValveForces(
            head_diameter_mm, max_cylinder_pressure_mpa, max_rpm, self.valve_mass_kg
        )
        
        # Spring (typical design)
        self.spring = ValveSpring(
            wire_diameter_mm=4.0,
            mean_coil_diameter_mm=25,
            active_coils=6,
            free_length_mm=60,
            installed_length_mm=40
        )
        
        # Seat
        self.seat = ValveSeat(head_diameter_mm)
        
        # Timing
        if application == "intake":
            self.timing = ValveTiming(self.geometry.max_lift_mm)
        else:
            self.timing = ValveTiming(self.geometry.max_lift_mm, cam_duration_deg=280)
    
    def design_summary(self):
        """Generate complete valve design summary."""
        
        spring_force_max = self.spring.max_force_n(self.geometry.max_lift_mm)
        spring_force_preload = self.spring.preload_force_n()
        gas_force = self.forces.gas_pressure_force_n()
        seat_force = self.forces.seat_force_n()
        seat_pressure = self.seat.seat_pressure_mpa(seat_force)
        
        summary = {
            # Basic dimensions
            "bore_mm": self.bore_mm,
            "valve_type": self.valve_type,
            "application": self.application,
            "head_diameter_mm": self.head_diameter_mm,
            "head_to_bore_ratio": round(self.head_diameter_mm / self.bore_mm, 2),
            "stem_diameter_mm": round(self.geometry.stem_diameter_mm, 2),
            "stem_length_mm": round(self.geometry.stem_length_mm, 1),
            
            # Valve geometry
            "seat_angle_deg": self.geometry.seat_angle_deg,
            "seat_width_mm": round(self.geometry.seat_width_mm, 3),
            "margin_thickness_mm": round(self.geometry.margin_thickness_mm, 2),
            "head_thickness_mm": round(self.geometry.head_thickness_mm, 2),
            "max_lift_mm": round(self.geometry.max_lift_mm, 2),
            "curtain_area_mm2": round(self.geometry.curtain_area_mm2(), 1),
            "flow_coefficient": round(self.geometry.flow_coefficient(), 3),
            
            # Forces
            "gas_force_n": round(gas_force, 1),
            "spring_preload_n": round(spring_force_preload, 1),
            "spring_max_force_n": round(spring_force_max, 1),
            "seat_force_n": round(seat_force, 1),
            
            # Seat analysis
            "seat_contact_area_mm2": round(self.seat.seat_contact_area_mm2(), 2),
            "seat_pressure_mpa": round(seat_pressure, 1),
            "allowable_seat_pressure_mpa": self.seat.allowable_seat_pressure_mpa(self.material),
            
            # Spring analysis
            "spring_rate_n_mm": round(self.spring.spring_rate_n_mm(), 2),
            "spring_preload_mm": round(self.spring.preload_mm(), 1),
            "spring_max_shear_mpa": round(self.spring.maximum_shear_stress_mpa(self.geometry.max_lift_mm), 1),
            "spring_natural_frequency_hz": round(self.spring.natural_frequency_hz(), 1),
            "spring_safety_clearance": round(self.spring.safety_factor_clearance(self.geometry.max_lift_mm), 2),
            
            # Timing
            "cam_duration_deg": self.timing.duration_deg,
            "valve_overlap_suggestion_deg": self.timing.overlap_period_deg(10, 10),
            
            # Material
            "material": self.material["name"],
            "material_description": self.material["description"],
            "max_temperature_c": self.material["max_temperature_c"],
            "hardness_hb": self.material["hardness_hb"],
            
            # Mass
            "valve_mass_g": round(self.valve_mass_kg * 1000, 1),
        }
        
        return summary
    
    def print_design_report(self):
        """Print formatted design report."""
        s = self.design_summary()
        
        print("=" * 70)
        print(f"VALVE DESIGN REPORT - {s['application'].upper()} VALVE")
        print("Machine Design Textbook - Chapter 32.22")
        print("=" * 70)
        
        print(f"\n📐 ENGINE SPECIFICATIONS:")
        print(f"   Bore: {s['bore_mm']:.1f} mm")
        print(f"   Max RPM: {self.max_rpm:.0f}")
        print(f"   Max cylinder pressure: {self.pressure_mpa:.1f} MPa")
        
        print(f"\n📏 VALVE DIMENSIONS:")
        print(f"   Type: {s['valve_type'].title()}")
        print(f"   Head diameter: {s['head_diameter_mm']:.2f} mm")
        print(f"   Head/bore ratio: {s['head_to_bore_ratio']:.2f}")
        print(f"   Stem diameter: {s['stem_diameter_mm']:.2f} mm")
        print(f"   Stem length: {s['stem_length_mm']:.1f} mm")
        print(f"   Seat angle: {s['seat_angle_deg']}°")
        print(f"   Seat width: {s['seat_width_mm']:.3f} mm")
        print(f"   Margin thickness: {s['margin_thickness_mm']:.2f} mm")
        print(f"   Head thickness: {s['head_thickness_mm']:.2f} mm")
        
        print(f"\n🌊 FLOW CHARACTERISTICS:")
        print(f"   Max lift: {s['max_lift_mm']:.2f} mm")
        print(f"   Curtain area: {s['curtain_area_mm2']:.1f} mm²")
        print(f"   Flow coefficient (Cd): {s['flow_coefficient']:.3f}")
        
        print(f"\n⚡ FORCES:")
        print(f"   Gas pressure force: {s['gas_force_n']:.1f} N")
        print(f"   Spring preload: {s['spring_preload_n']:.1f} N")
        print(f"   Spring @ max lift: {s['spring_max_force_n']:.1f} N")
        print(f"   Seat closing force: {s['seat_force_n']:.1f} N")
        
        print(f"\n🔧 VALVE SEAT:")
        print(f"   Contact area: {s['seat_contact_area_mm2']:.2f} mm²")
        print(f"   Seat pressure: {s['seat_pressure_mpa']:.1f} MPa")
        print(f"   Allowable pressure: {s['allowable_seat_pressure_mpa']:.0f} MPa")
        seat_status = "✅ OK" if s['seat_pressure_mpa'] < s['allowable_seat_pressure_mpa'] else "⚠️ HIGH"
        print(f"   Status: {seat_status}")
        
        print(f"\n🔩 VALVE SPRING:")
        print(f"   Spring rate: {s['spring_rate_n_mm']:.2f} N/mm")
        print(f"   Preload: {s['spring_preload_mm']:.1f} mm")
        print(f"   Max shear stress: {s['spring_max_shear_mpa']:.1f} MPa")
        print(f"   Natural frequency: {s['spring_natural_frequency_hz']:.1f} Hz")
        print(f"   Safety factor (coil bind): {s['spring_safety_clearance']:.2f}")
        
        print(f"\n⏱️ VALVE TIMING:")
        print(f"   Cam duration: {s['cam_duration_deg']:.0f}° crank")
        print(f"   Suggested overlap: {s['valve_overlap_suggestion_deg']:.0f}°")
        
        print(f"\n🏗️ MATERIAL:")
        print(f"   Material: {s['material']}")
        print(f"   {s['material_description']}")
        print(f"   Max operating temp: {s['max_temperature_c']}°C")
        print(f"   Hardness: {s['hardness_hb']} HB")
        
        print(f"\n⚖️ MASS:")
        print(f"   Valve mass: {s['valve_mass_g']:.1f} g")
        
        print("\n" + "=" * 70)
        
        # Validation checks
        issues = []
        if s['seat_pressure_mpa'] > s['allowable_seat_pressure_mpa']:
            issues.append("⚠️ SEAT PRESSURE EXCEEDS ALLOWABLE")
        if s['head_to_bore_ratio'] > 0.55:
            issues.append("⚠️ VALVE HEAD MAY BE TOO LARGE (flow limitation)")
        if s['head_to_bore_ratio'] < 0.35:
            issues.append("⚠️ VALVE HEAD MAY BE TOO SMALL (power limitation)")
        if s['spring_safety_clearance'] < 1.2:
            issues.append("⚠️ SPRING COULD BIND (add more clearance)")
        
        if issues:
            print("\n⚠️ DESIGN ISSUES / RECOMMENDATIONS:")
            for issue in issues:
                print(f"   {issue}")
        else:
            print("\n✅ DESIGN ACCEPTABLE - All criteria satisfied")
        
        print("=" * 70)
        
        # Design tips
        print("\n💡 DESIGN TIPS:")
        if self.application == "intake":
            print("   • Larger intake valves improve volumetric efficiency")
            print("   • 2 intake valves per cylinder improve flow and reduce mass")
        else:
            print("   • Exhaust valves require higher temperature materials")
            print("   • Sodium-filled stems improve cooling (racing applications)")
        print("   • Multi-angle valve seats improve flow (30°/45°/60°)")
        print("   • Valve seat interference: 0.05-0.10 mm for aluminum heads")
        print("   • Avoid valve spring resonance (natural frequency above engine harmonics)")


# ============================================================================
# Example usage
# ============================================================================

if __name__ == "__main__":
    print("=" * 70)
    print("VALVE DESIGN CALCULATOR")
    print("Machine Design Textbook - Chapter 32.22")
    print("=" * 70)
    
    print("\n📌 Example: 2.0L Automotive Engine")
    print("   Bore: 85 mm, Max Pressure: 8 MPa")
    print("   Max RPM: 6500")
    print("-" * 70)
    
    # Intake valve
    print("\n🔧 INTAKE VALVE DESIGN")
    print("-" * 50)
    
    intake_valve = ValveComplete(
        bore_mm=85,
        head_diameter_mm=34,  # Typical intake valve size
        max_cylinder_pressure_mpa=8.0,
        max_rpm=6500,
        application="intake"
    )
    intake_valve.print_design_report()
    
    # Exhaust valve
    print("\n\n🔧 EXHAUST VALVE DESIGN")
    print("-" * 50)
    
    exhaust_valve = ValveComplete(
        bore_mm=85,
        head_diameter_mm=30,  # Typical exhaust valve size
        max_cylinder_pressure_mpa=8.0,
        max_rpm=6500,
        application="exhaust",
        material_name="Silicon Chrome Steel (21-4N)"
    )
    exhaust_valve.print_design_report()
    
    print("\n" + "=" * 70)
    print("Valve design ready for engine integration.")
    print("=" * 70)