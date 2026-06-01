"""
deformation.py - Chapter 4: Strain, Elasticity, and Deformation

Based on Machine Design textbook (R.S. Khurmi, J.K. Gupta)
Sections covered:
- 4.4: Strain
- 4.7: Young's Modulus or Modulus of Elasticity
- 4.8: Shear Modulus or Modulus of Rigidity
- 4.17: Linear and Lateral Strain
- 4.18: Poisson's Ratio
- 4.19: Volumetric Strain
- 4.20: Bulk Modulus
- 4.21: Relation Between Bulk Modulus and Young's Modulus
- 4.22: Relation Between Young's Modulus and Modulus of Rigidity
"""

import math


class Strain:
    """Chapter 4.4: Strain is the deformation per unit length."""
    
    @staticmethod
    def linear(original_length, change_in_length):
        """
        ε = ΔL / L
        
        Linear strain (tensile or compressive).
        
        Parameters:
        -----------
        original_length : float
            Original length (L) in meters
        change_in_length : float
            Change in length (ΔL) in meters
            
        Returns:
        --------
        float : Strain (dimensionless)
        
        Example:
        --------
        >>> Strain.linear(original_length=100, change_in_length=0.2)
        0.002
        """
        return change_in_length / original_length
    
    @staticmethod
    def shear(shear_displacement, height):
        """
        γ = δ / h
        
        Shear strain (angular deformation).
        
        Parameters:
        -----------
        shear_displacement : float
            Displacement (δ) in meters
        height : float
            Height (h) in meters
            
        Returns:
        --------
        float : Shear strain (radians)
        """
        return shear_displacement / height
    
    @staticmethod
    def volumetric(original_volume, change_in_volume):
        """
        ε_v = ΔV / V
        
        Volumetric strain.
        
        Parameters:
        -----------
        original_volume : float
            Original volume (V) in m³
        change_in_volume : float
            Change in volume (ΔV) in m³
            
        Returns:
        --------
        float : Volumetric strain (dimensionless)
        """
        return change_in_volume / original_volume


class ElasticConstants:
    """Chapter 4.7, 4.8: Elastic constants of materials."""
    
    def __init__(self, youngs_modulus_gpa, poissons_ratio, shear_modulus_gpa=None):
        """
        Parameters:
        -----------
        youngs_modulus_gpa : float
            Young's modulus (E) in GPa (10^9 Pa)
        poissons_ratio : float
            Poisson's ratio (ν), dimensionless (typically 0.25-0.35 for metals)
        shear_modulus_gpa : float, optional
            Shear modulus (G) in GPa. If not provided, calculated from E and ν.
        """
        self.E = youngs_modulus_gpa * 1e9  # Convert to Pa
        self.nu = poissons_ratio
        self.G = shear_modulus_gpa * 1e9 if shear_modulus_gpa else None
    
    @property
    def youngs_modulus_pa(self):
        """E in Pascals (Pa)."""
        return self.E
    
    @property
    def youngs_modulus_gpa(self):
        """E in GPa for display."""
        return self.E / 1e9
    
    @property
    def shear_modulus_pa(self):
        """G in Pascals (Pa). Chapter 4.8"""
        if self.G is None:
            # G = E / (2(1 + ν))
            self.G = self.E / (2 * (1 + self.nu))
        return self.G
    
    @property
    def shear_modulus_gpa(self):
        """G in GPa for display."""
        return self.shear_modulus_pa / 1e9
    
    @property
    def bulk_modulus_pa(self):
        """
        K = E / (3(1 - 2ν))
        
        Chapter 4.20: Bulk Modulus
        Chapter 4.21: Relation between K and E
        """
        return self.E / (3 * (1 - 2 * self.nu))
    
    @property
    def bulk_modulus_gpa(self):
        """K in GPa for display."""
        return self.bulk_modulus_pa / 1e9
    
    def modulus_of_rigidity_relation(self):
        """
        Chapter 4.22: Relation between E and G
        E = 2G(1 + ν) → G = E / (2(1 + ν))
        """
        return self.shear_modulus_pa


class HookesLaw:
    """Chapter 4.7: Hooke's Law - Stress is proportional to strain."""
    
    @staticmethod
    def axial_stress(youngs_modulus, strain):
        """
        σ = E × ε
        
        For uniaxial loading.
        
        Parameters:
        -----------
        youngs_modulus : float
            Young's modulus (E) in Pa
        strain : float
            Linear strain (ε)
            
        Returns:
        --------
        float : Stress (σ) in Pa
        """
        return youngs_modulus * strain
    
    @staticmethod
    def axial_strain(youngs_modulus, stress):
        """
        ε = σ / E
        
        For uniaxial loading.
        """
        return stress / youngs_modulus
    
    @staticmethod
    def shear_stress(shear_modulus, shear_strain):
        """
        τ = G × γ
        
        For shear loading.
        """
        return shear_modulus * shear_strain
    
    @staticmethod
    def shear_strain(shear_modulus, shear_stress):
        """
        γ = τ / G
        """
        return shear_stress / shear_modulus


class PoissonsRatio:
    """Chapter 4.18: Poisson's Ratio - Lateral strain to axial strain ratio."""
    
    @staticmethod
    def from_strains(lateral_strain, axial_strain):
        """
        ν = -ε_lateral / ε_axial
        
        Parameters:
        -----------
        lateral_strain : float
            Strain perpendicular to loading direction
        axial_strain : float
            Strain parallel to loading direction
            
        Returns:
        --------
        float : Poisson's ratio (ν)
        
        Example:
        --------
        >>> PoissonsRatio.from_strains(lateral_strain=-0.0007, axial_strain=0.002)
        0.35
        """
        return -lateral_strain / axial_strain
    
    @staticmethod
    def lateral_strain(axial_strain, poissons_ratio):
        """
        ε_lateral = -ν × ε_axial
        """
        return -poissons_ratio * axial_strain
    
    @staticmethod
    def axial_strain(lateral_strain, poissons_ratio):
        """
        ε_axial = -ε_lateral / ν
        """
        return -lateral_strain / poissons_ratio
    
    @staticmethod
    def typical_values():
        """
        Typical Poisson's ratio values for common materials (Chapter 4.18).
        
        Returns:
        --------
        dict : Material to Poisson's ratio mapping
        """
        return {
            "Steel": 0.28,
            "Cast Iron": 0.25,
            "Aluminum": 0.33,
            "Copper": 0.34,
            "Brass": 0.35,
            "Rubber": 0.50,
            "Concrete": 0.20,
            "Glass": 0.24,
        }


class Deformation:
    """Chapter 4.4-4.7: Deformation calculations under load."""
    
    @staticmethod
    def elastic_elongation(force, length, area, youngs_modulus):
        """
        ΔL = (P × L) / (A × E)
        
        Elastic deformation of a prismatic bar under axial load.
        
        Parameters:
        -----------
        force : float
            Axial force (P) in Newtons
        length : float
            Original length (L) in meters
        area : float
            Cross-sectional area (A) in m²
        youngs_modulus : float
            Young's modulus (E) in Pa
            
        Returns:
        --------
        float : Deformation (ΔL) in meters
        
        Example:
        --------
        >>> Deformation.elastic_elongation(force=10000, length=2, area=0.0001, youngs_modulus=200e9)
        0.001  # 1 mm elongation
        """
        return (force * length) / (area * youngs_modulus)
    
    @staticmethod
    def elastic_elongation_stress_based(stress, length, youngs_modulus):
        """
        ΔL = (σ × L) / E
        
        Alternative formula using stress instead of force.
        """
        return (stress * length) / youngs_modulus
    
    @staticmethod
    def tapered_bar_elongation(
        force, 
        length, 
        diameter_large, 
        diameter_small, 
        youngs_modulus
    ):
        """
        ΔL = (4 × P × L) / (π × E × d1 × d2)
        
        For a circular tapered bar (conical shape).
        
        Parameters:
        -----------
        force : float
            Axial force (P) in Newtons
        length : float
            Length (L) in meters
        diameter_large : float
            Larger diameter (d1) in meters
        diameter_small : float
            Smaller diameter (d2) in meters
        youngs_modulus : float
            Young's modulus (E) in Pa
            
        Returns:
        --------
        float : Deformation (ΔL) in meters
        """
        return (4 * force * length) / (
            math.pi * youngs_modulus * diameter_large * diameter_small
        )
    
    @staticmethod
    def stepped_bar_elongation(segments):
        """
        ΔL_total = Σ (P_i × L_i) / (A_i × E_i)
        
        For a bar with multiple segments (different areas, loads, materials).
        
        Parameters:
        -----------
        segments : list of tuples
            Each segment: (force, length, area, youngs_modulus)
            
        Returns:
        --------
        float : Total deformation in meters
        
        Example:
        --------
        >>> segments = [
        ...     (10000, 1, 0.0001, 200e9),  # Segment 1
        ...     (10000, 0.5, 0.0002, 200e9), # Segment 2
        ... ]
        >>> Deformation.stepped_bar_elongation(segments)
        """
        total = 0
        for force, length, area, modulus in segments:
            total += (force * length) / (area * modulus)
        return total


class VolumetricDeformation:
    """Chapter 4.19-4.21: Volume changes under stress."""
    
    @staticmethod
    def volumetric_strain_from_linear(linear_strain_x, linear_strain_y, linear_strain_z):
        """
        ε_v = ε_x + ε_y + ε_z
        
        For small strains, volumetric strain is sum of linear strains.
        """
        return linear_strain_x + linear_strain_y + linear_strain_z
    
    @staticmethod
    def volumetric_strain_uniaxial(stress, youngs_modulus, poissons_ratio):
        """
        ε_v = (σ / E) × (1 - 2ν)
        
        For uniaxial loading (stress in one direction only).
        """
        return (stress / youngs_modulus) * (1 - 2 * poissons_ratio)
    
    @staticmethod
    def volumetric_strain_hydrostatic(bulk_modulus, pressure):
        """
        ε_v = ΔP / K
        
        For hydrostatic (uniform) pressure.
        """
        return pressure / bulk_modulus
    
    @staticmethod
    def change_in_volume(original_volume, volumetric_strain):
        """
        ΔV = V × ε_v
        """
        return original_volume * volumetric_strain


# Common material database (Chapter 2)
MATERIALS_DATABASE = {
    "Structural Steel": {
        "youngs_modulus_gpa": 200,
        "poissons_ratio": 0.30,
        "yield_strength_mpa": 250,
        "ultimate_tensile_mpa": 400,
    },
    "Cast Iron (Gray)": {
        "youngs_modulus_gpa": 100,
        "poissons_ratio": 0.25,
        "yield_strength_mpa": 200,
        "ultimate_tensile_mpa": 250,
    },
    "Aluminum (6061)": {
        "youngs_modulus_gpa": 68.9,
        "poissons_ratio": 0.33,
        "yield_strength_mpa": 275,
        "ultimate_tensile_mpa": 310,
    },
    "Copper": {
        "youngs_modulus_gpa": 110,
        "poissons_ratio": 0.34,
        "yield_strength_mpa": 70,
        "ultimate_tensile_mpa": 220,
    },
    "Brass": {
        "youngs_modulus_gpa": 100,
        "poissons_ratio": 0.35,
        "yield_strength_mpa": 140,
        "ultimate_tensile_mpa": 330,
    },
    "Titanium": {
        "youngs_modulus_gpa": 110,
        "poissons_ratio": 0.32,
        "yield_strength_mpa": 880,
        "ultimate_tensile_mpa": 950,
    },
}


def get_material(material_name):
    """
    Get material properties from database.
    
    Parameters:
    -----------
    material_name : str
        Name of material (e.g., "Steel", "Aluminum")
    
    Returns:
    --------
    dict : Material properties including E, ν, yield_strength
    """
    return MATERIALS_DATABASE.get(material_name, None)


# ============================================================================
# Example usage and test
# ============================================================================

if __name__ == "__main__":
    print("=" * 60)
    print("Deformation Module Test (Based on Machine Design Textbook)")
    print("=" * 60)
    
    # Example 1: Simple strain calculation
    print("\n1. Linear Strain Example:")
    strain = Strain.linear(original_length=200, change_in_length=0.4)
    print(f"   ε = 0.4 / 200 = {strain}")
    
    # Example 2: Hooke's Law
    print("\n2. Hooke's Law Example:")
    steel = ElasticConstants(youngs_modulus_gpa=200, poissons_ratio=0.3)
    stress = HookesLaw.axial_stress(steel.E, strain=0.001)
    print(f"   σ = E × ε = 200 GPa × 0.001 = {stress/1e6:.1f} MPa")
    
    # Example 3: Elastic constants relations
    print("\n3. Elastic Constants Relations:")
    print(f"   E = {steel.youngs_modulus_gpa:.1f} GPa")
    print(f"   G = {steel.shear_modulus_gpa:.1f} GPa")
    print(f"   K = {steel.bulk_modulus_gpa:.1f} GPa")
    print(f"   ν = {steel.nu}")
    
    # Example 4: Check relation G = E/(2(1+ν))
    calculated_G = steel.E / (2 * (1 + steel.nu))
    print(f"\n   G (calculated from E,ν) = {calculated_G/1e9:.1f} GPa")
    
    # Example 5: Deformation calculation
    print("\n4. Deformation Example (Steel rod):")
    force = 50000  # 50 kN
    length = 3.0  # 3 meters
    diameter = 0.03  # 30 mm
    area = math.pi * (diameter / 2) ** 2
    
    delta = Deformation.elastic_elongation(
        force=force,
        length=length,
        area=area,
        youngs_modulus=200e9
    )
    print(f"   Force = {force/1000:.1f} kN")
    print(f"   Length = {length} m")
    print(f"   Diameter = {diameter*1000:.0f} mm")
    print(f"   Area = {area*1e6:.2f} mm²")
    print(f"   Deformation = {delta*1000:.3f} mm")
    
    # Example 6: Poisson's ratio typical values
    print("\n5. Typical Poisson's Ratio Values:")
    for material, nu in PoissonsRatio.typical_values().items():
        print(f"   {material}: ν = {nu}")
    
    # Example 7: Material database
    print("\n6. Material Database Example:")
    aluminum = get_material("Aluminum (6061)")
    if aluminum:
        print(f"   Aluminum 6061:")
        print(f"     E = {aluminum['youngs_modulus_gpa']} GPa")
        print(f"     ν = {aluminum['poissons_ratio']}")
        print(f"     σ_yield = {aluminum['yield_strength_mpa']} MPa")
    
    print("\n" + "=" * 60)
    print("All deformation functions ready for use in engine design.")
    print("=" * 60)