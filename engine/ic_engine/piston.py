"""
piston.py - Chapter 32.5-32.12: Piston Design for IC Engines

Based on Machine Design textbook (R.S. Khurmi, J.K. Gupta)
Sections covered:
- 32.5: Piston (introduction and design considerations)
- 32.6: Design considerations for a piston
- 32.7: Material for pistons
- 32.8: Piston head or crown
- 32.9: Piston rings
- 32.10: Piston skirt
- 32.11: Piston pin (see piston_pin.py for full details)
- 32.12: Piston pin (continued)

Additional references:
- Heat transfer in piston head
- Thermal stresses
- Ring groove design
- Piston slap and clearance
"""

import math


class PistonMaterial:
    """Chapter 32.7: Material properties for pistons."""
    
    # Material database (typical values from textbook)
    MATERIALS = {
        "Cast Iron": {
            "density_kg_m3": 7200,
            "thermal_conductivity_w_mk": 52,
            "coefficient_thermal_expansion_1e6": 11,
            "ultimate_tensile_mpa": 250,
            "yield_strength_mpa": 200,
            "fatigue_limit_mpa": 100,
            "max_temperature_c": 400,
            "hardness_hb": 220,
        },
        "Aluminum Alloy (4032)": {
            "density_kg_m3": 2700,
            "thermal_conductivity_w_mk": 155,
            "coefficient_thermal_expansion_1e6": 19,
            "ultimate_tensile_mpa": 330,
            "yield_strength_mpa": 280,
            "fatigue_limit_mpa": 120,
            "max_temperature_c": 350,
            "hardness_hb": 120,
        },
        "Aluminum Alloy (2618)": {
            "density_kg_m3": 2760,
            "thermal_conductivity_w_mk": 160,
            "coefficient_thermal_expansion_1e6": 22,
            "ultimate_tensile_mpa": 380,
            "yield_strength_mpa": 320,
            "fatigue_limit_mpa": 140,
            "max_temperature_c": 350,
            "hardness_hb": 130,
        },
        "Forged Steel": {
            "density_kg_m3": 7850,
            "thermal_conductivity_w_mk": 45,
            "coefficient_thermal_expansion_1e6": 12,
            "ultimate_tensile_mpa": 800,
            "yield_strength_mpa": 600,
            "fatigue_limit_mpa": 280,
            "max_temperature_c": 500,
            "hardness_hb": 250,
        },
        "Hypereutectic Aluminum": {
            "density_kg_m3": 2680,
            "thermal_conductivity_w_mk": 150,
            "coefficient_thermal_expansion_1e6": 18,
            "ultimate_tensile_mpa": 350,
            "yield_strength_mpa": 300,
            "fatigue_limit_mpa": 130,
            "max_temperature_c": 300,
            "hardness_hb": 110,
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
        """List all available piston materials."""
        return list(cls.MATERIALS.keys())


class PistonHead:
    """Chapter 32.8: Piston head or crown design."""
    
    def __init__(self, bore_mm, max_gas_pressure_mpa, material):
        """
        Parameters:
        -----------
        bore_mm : float
            Cylinder bore diameter in mm
        max_gas_pressure_mpa : float
            Maximum combustion pressure in MPa
        material : dict
            Material properties from PistonMaterial
        """
        self.bore_mm = bore_mm
        self.bore_m = bore_mm / 1000
        self.pressure_mpa = max_gas_pressure_mpa
        self.pressure_pa = max_gas_pressure_mpa * 1e6
        self.material = material
    
    def area_mm2(self):
        """Piston area in mm²."""
        return math.pi * (self.bore_mm ** 2) / 4
    
    def area_m2(self):
        """Piston area in m²."""
        return math.pi * (self.bore_m ** 2) / 4
    
    def gas_force_n(self):
        """Maximum gas force on piston in Newtons."""
        return self.pressure_pa * self.area_m2()
    
    def gas_force_kn(self):
        """Gas force in kN."""
        return self.gas_force_n() / 1000
    
    def thickness_grashof_mm(self):
        """
        Grashof's formula for piston head thickness.
        
        t_H = D × √(0.1 × p_max / σ_t)
        
        Where:
        - D = cylinder bore (mm)
        - p_max = maximum gas pressure (MPa)
        - σ_t = permissible tensile stress (MPa)
        
        This is an empirical formula based on heat dissipation.
        
        Returns:
        --------
        float : Piston head thickness in mm
        """
        # Permissible tensile stress (MPa) = ultimate/3 for cast iron, ultimate/5 for aluminum
        if "Aluminum" in self.material.get("name", ""):
            permissible_stress = self.material["ultimate_tensile_mpa"] / 5
        else:
            permissible_stress = self.material["ultimate_tensile_mpa"] / 3
        
        thickness = self.bore_mm * math.sqrt(0.1 * self.pressure_mpa / permissible_stress)
        return max(thickness, 0.05 * self.bore_mm)  # Minimum 5% of bore
    
    def thickness_heat_transfer_mm(self, max_temperature_c=220, heat_flux_w_mm2=0.035):
        """
        Heat transfer based thickness for aluminum pistons.
        
        t_H = (H × D) / (12.56 × k × (T_c - T_e))
        
        Where:
        - H = heat flux (W/mm²) - typically 0.035 for CI engines
        - D = bore (mm)
        - k = thermal conductivity (W/mK)
        - T_c = temperature at center (℃)
        - T_e = temperature at edge (℃)
        
        Returns:
        --------
        float : Required thickness for heat dissipation in mm
        """
        k = self.material["thermal_conductivity_w_mk"]
        
        if k < 50:  # Cast iron
            return 0.045 * self.bore_mm
        else:  # Aluminum
            # More accurate heat transfer calculation
            temp_diff = max_temperature_c - 180  # Edge temperature approx 180°C
            thickness = (heat_flux_w_mm2 * self.bore_mm) / (12.56 * k / 1000 * temp_diff)
            return max(thickness, 0.03 * self.bore_mm)
    
    def thickness_stress_based_mm(self, factor_of_safety=3):
        """
        Stress-based thickness (treating head as circular plate).
        
        t_H = (3 × p_max × D²) / (16 × σ_allow)
        
        Returns:
        --------
        float : Required thickness in mm
        """
        # Permissible stress = yield strength / factor of safety
        sigma_allow = self.material["yield_strength_mpa"] / factor_of_safety
        thickness = math.sqrt((3 * self.pressure_mpa * (self.bore_mm ** 2)) / (16 * sigma_allow))
        return thickness
    
    def recommended_thickness_mm(self):
        """
        Recommended piston head thickness based on textbook guidelines.
        
        Returns:
        --------
        float : Recommended thickness in mm
        """
        grashof = self.thickness_grashof_mm()
        heat = self.thickness_heat_transfer_mm()
        stress = self.thickness_stress_based_mm()
        
        # Use the maximum of the three methods (conservative design)
        recommended = max(grashof, heat, stress)
        
        # Round up to nearest mm for manufacturing
        return math.ceil(recommended)
    
    def thermal_stress_mpa(self, temperature_drop_c=50):
        """
        Chapter 32.8: Thermal stress due to temperature gradient.
        
        σ_th = E × α × ΔT / (1 - ν)
        
        Returns:
        --------
        float : Thermal stress in MPa
        """
        E = self.material.get("youngs_modulus_gpa", 70) * 1000  # MPa
        alpha = self.material["coefficient_thermal_expansion_1e6"] / 1e6
        nu = 0.33  # Poisson's ratio for metals
        
        thermal_stress_pa = E * 1e6 * alpha * temperature_drop_c / (1 - nu)
        return thermal_stress_pa / 1e6  # Convert to MPa
    
    def factor_of_safety(self):
        """Calculate factor of safety for piston head."""
        max_stress = self.pressure_mpa * 1.5  # Approximate maximum stress
        yield_stress = self.material["yield_strength_mpa"]
        return yield_stress / max_stress


class PistonRing:
    """Chapter 32.9: Piston ring design."""
    
    def __init__(self, bore_mm, radial_width_mm=None, axial_thickness_mm=None, num_compression_rings=3, num_oil_rings=1):
        """
        Parameters:
        -----------
        bore_mm : float
            Cylinder bore diameter in mm
        radial_width_mm : float, optional
            Radial width of ring (t) in mm. Default = 0.04 * bore
        axial_thickness_mm : float, optional
            Axial thickness of ring (h) in mm. Default = 0.8 * radial_width
        num_compression_rings : int
            Number of compression rings (typical: 2-3)
        num_oil_rings : int
            Number of oil control rings (typical: 1)
        """
        self.bore_mm = bore_mm
        self.radial_width_mm = radial_width_mm or (0.04 * bore_mm)
        self.axial_thickness_mm = axial_thickness_mm or (0.8 * self.radial_width_mm)
        self.num_compression_rings = num_compression_rings
        self.num_oil_rings = num_oil_rings
    
    def mean_diameter_mm(self):
        """Mean diameter of ring when free."""
        return self.bore_mm - self.radial_width_mm
    
    def gap_clearance_mm(self):
        """
        Ring gap when installed in cylinder.
        
        Gap = 0.0035 × D (for cast iron rings)
        Gap = 0.005 × D (for aluminum pistons)
        
        Returns:
        --------
        float : Ring gap in mm
        """
        # Standard gap = 0.003 to 0.005 × bore
        return 0.004 * self.bore_mm
    
    def free_gap_mm(self):
        """
        Ring gap when free (not installed).
        
        For easy assembly, free gap is larger.
        """
        return 3.14 * self.radial_width_mm + self.gap_clearance_mm()
    
    def ring_stress_mpa(self, youngs_modulus_gpa=110):
        """
        Bending stress in ring during assembly/installation.
        
        σ = (E × (D - t/2)) / (6.28 × (D/t - 1))
        
        Returns:
        --------
        float : Maximum bending stress in MPa
        """
        E = youngs_modulus_gpa * 1000  # MPa
        D = self.bore_mm
        t = self.radial_width_mm
        
        stress = (E * (D - t/2)) / (6.28 * (D/t - 1))
        return stress
    
    def allowable_radial_pressure_mpa(self):
        """
        Allowable radial pressure between ring and cylinder wall.
        
        p_r = (σ_t × t²) / (D × h)
        
        Where:
        - σ_t = allowable tensile stress (MPa)
        - t = radial width (mm)
        - D = bore (mm)
        - h = axial thickness (mm)
        
        Returns:
        --------
        float : Allowable radial pressure in MPa
        """
        sigma_t = 85  # MPa for cast iron rings
        t = self.radial_width_mm
        D = self.bore_mm
        h = self.axial_thickness_mm
        
        pressure = (sigma_t * t**2) / (D * h)
        return pressure
    
    def total_ring_area_mm2(self):
        """Total axial area occupied by rings."""
        compression_area = self.num_compression_rings * self.axial_thickness_mm
        oil_area = self.num_oil_rings * self.axial_thickness_mm
        return (compression_area + oil_area) * self.bore_mm * math.pi
    
    def ring_land_height_mm(self):
        """
        Recommended ring land height (space between rings).
        
        Returns:
        --------
        float : Ring land height in mm
        """
        return 0.8 * self.axial_thickness_mm
    
    def top_land_height_mm(self):
        """
        Height from piston crown to first ring.
        
        Returns:
        --------
        float : Top land height in mm
        """
        if self.bore_mm < 100:
            return 0.06 * self.bore_mm
        else:
            return 0.08 * self.bore_mm


class PistonSkirt:
    """Chapter 32.10: Piston skirt design."""
    
    def __init__(self, bore_mm, stroke_mm, max_gas_pressure_mpa, material):
        """
        Parameters:
        -----------
        bore_mm : float
            Cylinder bore diameter in mm
        stroke_mm : float
            Piston stroke in mm
        max_gas_pressure_mpa : float
            Maximum combustion pressure in MPa
        material : dict
            Material properties
        """
        self.bore_mm = bore_mm
        self.stroke_mm = stroke_mm
        self.pressure_mpa = max_gas_pressure_mpa
        self.material = material
    
    def skirt_length_mm(self):
        """
        Recommended skirt length (guidance from side thrust).
        
        L_s = (0.6 to 0.8) × D for high-speed engines
        L_s = (1.0 to 1.2) × D for low-speed engines
        
        Returns:
        --------
        float : Skirt length in mm
        """
        # For automotive engines (high speed)
        return 0.7 * self.bore_mm
    
    def total_piston_length_mm(self, head_thickness_mm, ring_section_height_mm):
        """
        Total piston length from crown to skirt bottom.
        
        L_total = t_H + h_rings + L_s
        
        Returns:
        --------
        float : Total piston length in mm
        """
        return head_thickness_mm + ring_section_height_mm + self.skirt_length_mm()
    
    def bearing_pressure_mpa(self, side_force_n=None):
        """
        Chapter 32.10: Bearing pressure between skirt and cylinder wall.
        
        p_b = (μ × P_max) / (D × L_s)
        
        Where:
        - μ = coefficient of friction (0.05-0.1)
        - P_max = maximum gas force (N)
        - D = bore (mm)
        - L_s = skirt length (mm)
        
        Returns:
        --------
        float : Bearing pressure in MPa
        """
        # Side force = gas force × tan(connecting rod angle)
        # Typical maximum side force is 0.3 × gas force
        gas_force_n = (self.pressure_mpa * 1e6) * (math.pi * (self.bore_mm/1000)**2 / 4)
        side_force = side_force_n or (0.3 * gas_force_n)
        
        area_mm2 = self.bore_mm * self.skirt_length_mm()
        pressure_mpa = side_force / (area_mm2 * 1e6)  # N/mm² = MPa
        
        return pressure_mpa
    
    def permissible_bearing_pressure_mpa(self):
        """
        Permissible bearing pressure based on material and application.
        
        Returns:
        --------
        float : Permissible bearing pressure in MPa
        """
        if "Aluminum" in self.material.get("name", ""):
            return 0.5  # MPa for aluminum pistons
        else:
            return 0.7  # MPa for cast iron pistons
    
    def piston_clearance_mm(self, operating_temperature_c=200, ambient_temperature_c=20):
        """
        Thermal clearance between piston and cylinder wall.
        
        Δ = D × (α_aluminum - α_cylinder) × (T_op - T_amb)
        
        Returns:
        --------
        float : Required piston clearance in mm
        """
        alpha_piston = self.material["coefficient_thermal_expansion_1e6"] / 1e6
        alpha_cylinder = 11e-6  # Cast iron cylinder
        
        delta_T = operating_temperature_c - ambient_temperature_c
        clearance = self.bore_mm * (alpha_piston - alpha_cylinder) * delta_T
        
        return clearance
    
    def piston_slap_risk(self):
        """
        Estimate risk of piston slap (noise/vibration).
        
        Returns:
        --------
        str : Risk assessment
        """
        clearance = self.piston_clearance_mm()
        
        if clearance < 0.05:
            return "LOW - Clearance too small (seizure risk)"
        elif clearance < 0.15:
            return "MEDIUM - Normal clearance range"
        elif clearance < 0.30:
            return "HIGH - Potential slap"
        else:
            return "VERY HIGH - Excessive clearance"


class PistonComplete:
    """Complete piston design integrating all components."""
    
    def __init__(self, bore_mm, stroke_mm, max_gas_pressure_mpa, material_name="Aluminum Alloy (2618)", 
                 num_compression_rings=2, num_oil_rings=1):
        """
        Complete piston design calculator.
        
        Parameters:
        -----------
        bore_mm : float
            Cylinder bore diameter in mm
        stroke_mm : float
            Piston stroke in mm
        max_gas_pressure_mpa : float
            Maximum combustion pressure in MPa (typical: 5-10 for NA, 10-20 for turbo)
        material_name : str
            Piston material (see PistonMaterial.list_materials())
        num_compression_rings : int
            Number of compression rings (typically 2-3)
        num_oil_rings : int
            Number of oil control rings (typically 1)
        """
        self.bore_mm = bore_mm
        self.stroke_mm = stroke_mm
        self.pressure_mpa = max_gas_pressure_mpa
        
        # Get material properties
        self.material_data = PistonMaterial.get_material(material_name)
        self.material_data["name"] = material_name
        self.material = self.material_data
        
        # Initialize components
        self.head = PistonHead(bore_mm, max_gas_pressure_mpa, self.material)
        self.rings = PistonRing(bore_mm, num_compression_rings=num_compression_rings, 
                                num_oil_rings=num_oil_rings)
        self.skirt = PistonSkirt(bore_mm, stroke_mm, max_gas_pressure_mpa, self.material)
    
    def design_summary(self):
        """Generate complete piston design summary."""
        
        # Calculate all dimensions
        head_thickness = self.head.recommended_thickness_mm()
        top_land = self.rings.top_land_height_mm()
        ring_section_height = (self.rings.num_compression_rings + self.rings.num_oil_rings) * \
                              self.rings.axial_thickness_mm + \
                              (self.rings.num_compression_rings + self.rings.num_oil_rings - 1) * \
                              self.rings.ring_land_height_mm()
        skirt_length = self.skirt.skirt_length_mm()
        total_length = head_thickness + top_land + ring_section_height + skirt_length
        
        # Calculate forces and stresses
        gas_force = self.head.gas_force_kn()
        bearing_pressure = self.skirt.bearing_pressure_mpa()
        thermal_clearance = self.skirt.piston_clearance_mm()
        
        # Ring analysis
        ring_stress = self.rings.ring_stress_mpa()
        ring_pressure = self.rings.allowable_radial_pressure_mpa()
        
        summary = {
            # Dimensions
            "bore_mm": self.bore_mm,
            "stroke_mm": self.stroke_mm,
            "displacement_cc": math.pi * (self.bore_mm**2) / 4 * self.stroke_mm / 1000,
            "head_thickness_mm": round(head_thickness, 2),
            "top_land_mm": round(top_land, 2),
            "ring_section_height_mm": round(ring_section_height, 2),
            "skirt_length_mm": round(skirt_length, 2),
            "total_length_mm": round(total_length, 2),
            
            # Ring data
            "ring_radial_width_mm": round(self.rings.radial_width_mm, 2),
            "ring_axial_thickness_mm": round(self.rings.axial_thickness_mm, 2),
            "ring_gap_mm": round(self.rings.gap_clearance_mm(), 3),
            "ring_bending_stress_mpa": round(ring_stress, 1),
            "ring_radial_pressure_mpa": round(ring_pressure, 3),
            
            # Forces and pressures
            "max_gas_pressure_mpa": self.pressure_mpa,
            "max_gas_force_kn": round(gas_force, 1),
            "bearing_pressure_mpa": round(bearing_pressure, 3),
            "permissible_bearing_pressure_mpa": round(self.skirt.permissible_bearing_pressure_mpa(), 3),
            
            # Thermal
            "thermal_clearance_mm": round(thermal_clearance, 3),
            "thermal_stress_mpa": round(self.head.thermal_stress_mpa(), 1),
            "max_operating_temp_c": self.material["max_temperature_c"],
            
            # Material
            "material": self.material["name"],
            "density_kg_m3": self.material["density_kg_m3"],
            "piston_mass_kg": round(self.piston_mass_kg(total_length), 2),
            
            # Safety
            "factor_of_safety": round(self.head.factor_of_safety(), 2),
            "piston_slap_risk": self.skirt.piston_slap_risk(),
        }
        
        return summary
    
    def piston_mass_kg(self, total_length_mm):
        """
        Estimate piston mass based on volume and density.
        
        Simplified as a cylinder with holes for pin.
        """
        # Volume of piston as cylinder (simplified)
        area_m2 = math.pi * (self.bore_mm/1000)**2 / 4
        volume_m3 = area_m2 * (total_length_mm / 1000)
        
        # Subtract 30% for hollow sections (pin boss, undercrown)
        volume_m3 *= 0.7
        
        mass_kg = volume_m3 * self.material["density_kg_m3"]
        return mass_kg
    
    def print_design_report(self):
        """Print formatted design report."""
        s = self.design_summary()
        
        print("=" * 70)
        print("PISTON DESIGN REPORT - Machine Design Textbook Chapter 32")
        print("=" * 70)
        
        print(f"\n📐 DIMENSIONS:")
        print(f"   Bore: {s['bore_mm']:.1f} mm")
        print(f"   Stroke: {s['stroke_mm']:.1f} mm")
        print(f"   Displacement: {s['displacement_cc']:.1f} cc")
        print(f"   Head thickness: {s['head_thickness_mm']:.2f} mm")
        print(f"   Top land: {s['top_land_mm']:.2f} mm")
        print(f"   Ring section height: {s['ring_section_height_mm']:.2f} mm")
        print(f"   Skirt length: {s['skirt_length_mm']:.2f} mm")
        print(f"   Total length: {s['total_length_mm']:.2f} mm")
        
        print(f"\n🔧 PISTON RINGS:")
        print(f"   Radial width: {s['ring_radial_width_mm']:.2f} mm")
        print(f"   Axial thickness: {s['ring_axial_thickness_mm']:.2f} mm")
        print(f"   Ring gap: {s['ring_gap_mm']:.3f} mm")
        print(f"   Bending stress: {s['ring_bending_stress_mpa']:.1f} MPa")
        print(f"   Radial pressure: {s['ring_radial_pressure_mpa']:.3f} MPa")
        
        print(f"\n💪 FORCES & PRESSURES:")
        print(f"   Max gas pressure: {s['max_gas_pressure_mpa']:.1f} MPa")
        print(f"   Max gas force: {s['max_gas_force_kn']:.1f} kN")
        print(f"   Bearing pressure: {s['bearing_pressure_mpa']:.3f} MPa (allowable: {s['permissible_bearing_pressure_mpa']:.3f})")
        
        print(f"\n🌡️ THERMAL:")
        print(f"   Thermal clearance: {s['thermal_clearance_mm']:.3f} mm")
        print(f"   Thermal stress: {s['thermal_stress_mpa']:.1f} MPa")
        print(f"   Max operating temp: {s['max_operating_temp_c']}°C")
        
        print(f"\n🏗️ MATERIAL & MASS:")
        print(f"   Material: {s['material']}")
        print(f"   Density: {s['density_kg_m3']} kg/m³")
        print(f"   Estimated mass: {s['piston_mass_kg']:.2f} kg")
        
        print(f"\n✅ SAFETY:")
        print(f"   Factor of safety: {s['factor_of_safety']:.2f}")
        print(f"   Piston slap risk: {s['piston_slap_risk']}")
        
        print("\n" + "=" * 70)
        
        # Validation checks
        issues = []
        if s['bearing_pressure_mpa'] > s['permissible_bearing_pressure_mpa']:
            issues.append("⚠️ BEARING PRESSURE EXCEEDS ALLOWABLE")
        if s['factor_of_safety'] < 2:
            issues.append("⚠️ FACTOR OF SAFETY BELOW 2 (unsafe)")
        if "EXCESSIVE" in s['piston_slap_risk']:
            issues.append("⚠️ EXCESSIVE PISTON CLEARANCE")
        
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
    print("PISTON DESIGN CALCULATOR - Machine Design Textbook Chapter 32")
    print("=" * 70)
    
    print("\n📌 Example: 4-Cylinder Automotive Engine")
    print("   Bore: 85 mm, Stroke: 88 mm, Max Pressure: 8 MPa (NA gasoline)")
    print("   Material: Aluminum Alloy 2618")
    print("-" * 70)
    
    # Create piston design
    piston = PistonComplete(
        bore_mm=85,
        stroke_mm=88,
        max_gas_pressure_mpa=8.0,
        material_name="Aluminum Alloy (2618)",
        num_compression_rings=2,
        num_oil_rings=1
    )
    
    # Print design report
    piston.print_design_report()
    
    print("\n" + "=" * 70)
    print("Piston design ready for engine integration.")
    print("=" * 70)