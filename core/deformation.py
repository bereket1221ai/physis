"""
deformation.py - Complete Deformation and Elasticity Analysis

Sources:
- Machine Design Textbook (Chapter 4) - R.S. Khurmi
- Mechanical Engineering Design - Shigley & Mischke
- Advanced Mechanics of Materials - Boresi & Schmidt
- Elasticity and Plasticity - Timoshenko

Covers:
- Chapter 4.4: Strain (linear, shear, volumetric)
- Chapter 4.7: Young's Modulus or Modulus of Elasticity
- Chapter 4.8: Shear Modulus or Modulus of Rigidity
- Chapter 4.17: Linear and Lateral Strain
- Chapter 4.18: Poisson's Ratio
- Chapter 4.19: Volumetric Strain
- Chapter 4.20: Bulk Modulus
- Chapter 4.21: Relation Between Bulk Modulus and Young's Modulus
- Chapter 4.22: Relation Between Young's Modulus and Modulus of Rigidity
- Composite bars and thermal deformation
"""

import math
from dataclasses import dataclass, field
from typing import Dict, Any, Optional, Tuple, List


# ============================================================================
# SECTION 1: MATERIAL PROPERTIES DATABASE
# ============================================================================

@dataclass(frozen=True)
class DeformationMaterial:
    """Material properties for deformation analysis."""
    
    name: str
    youngs_modulus_gpa: float
    poissons_ratio: float
    yield_strength_mpa: float
    ultimate_tensile_mpa: float
    density_kg_m3: float
    shear_modulus_gpa: Optional[float] = None
    bulk_modulus_gpa: Optional[float] = None
    
    def __post_init__(self):
        if self.shear_modulus_gpa is None:
            G = self.youngs_modulus_gpa / (2 * (1 + self.poissons_ratio))
            object.__setattr__(self, 'shear_modulus_gpa', G)
        if self.bulk_modulus_gpa is None:
            K = self.youngs_modulus_gpa / (3 * (1 - 2 * self.poissons_ratio))
            object.__setattr__(self, 'bulk_modulus_gpa', K)
    
    @property
    def E_pa(self) -> float:
        return self.youngs_modulus_gpa * 1e9
    
    @property
    def G_pa(self) -> float:
        return self.shear_modulus_gpa * 1e9
    
    @property
    def K_pa(self) -> float:
        return self.bulk_modulus_gpa * 1e9


# Material database
DEFORMATION_MATERIALS: Dict[str, DeformationMaterial] = {
    "Structural Steel": DeformationMaterial(
        name="Structural Steel",
        youngs_modulus_gpa=200,
        poissons_ratio=0.30,
        yield_strength_mpa=250,
        ultimate_tensile_mpa=400,
        density_kg_m3=7850,
    ),
    "Cast Iron": DeformationMaterial(
        name="Cast Iron",
        youngs_modulus_gpa=100,
        poissons_ratio=0.25,
        yield_strength_mpa=200,
        ultimate_tensile_mpa=250,
        density_kg_m3=7200,
    ),
    "Aluminum 6061": DeformationMaterial(
        name="Aluminum 6061",
        youngs_modulus_gpa=68.9,
        poissons_ratio=0.33,
        yield_strength_mpa=275,
        ultimate_tensile_mpa=310,
        density_kg_m3=2700,
    ),
    "Titanium (Ti-6Al-4V)": DeformationMaterial(
        name="Titanium (Ti-6Al-4V)",
        youngs_modulus_gpa=114,
        poissons_ratio=0.32,
        yield_strength_mpa=880,
        ultimate_tensile_mpa=950,
        density_kg_m3=4430,
    ),
    "Copper": DeformationMaterial(
        name="Copper",
        youngs_modulus_gpa=110,
        poissons_ratio=0.34,
        yield_strength_mpa=70,
        ultimate_tensile_mpa=220,
        density_kg_m3=8960,
    ),
    "Brass": DeformationMaterial(
        name="Brass",
        youngs_modulus_gpa=100,
        poissons_ratio=0.35,
        yield_strength_mpa=140,
        ultimate_tensile_mpa=330,
        density_kg_m3=8500,
    ),
}


def get_deformation_material(name: str) -> DeformationMaterial:
    """Get material by name."""
    if name not in DEFORMATION_MATERIALS:
        raise ValueError(f"Unknown material: {name}. Available: {list(DEFORMATION_MATERIALS.keys())}")
    return DEFORMATION_MATERIALS[name]


# ============================================================================
# SECTION 2: STRAIN CALCULATIONS
# ============================================================================

@dataclass
class StrainResult:
    """Result of strain calculation."""
    
    strain: float
    type: str
    original_dimension: float
    change_dimension: float
    
    def print(self):
        print(f"   {self.type}: ε = {self.strain:.6f}")
        print(f"   Original: {self.original_dimension:.4f}, Change: {self.change_dimension:.4f}")


@dataclass
class Strain:
    """Strain calculations - Chapter 4.4."""
    
    @staticmethod
    def linear(original_length_mm: float, change_in_length_mm: float) -> StrainResult:
        """Linear strain: ε = ΔL / L"""
        strain = change_in_length_mm / original_length_mm if original_length_mm > 0 else 0
        return StrainResult(
            strain=strain,
            type="Linear Strain",
            original_dimension=original_length_mm,
            change_dimension=change_in_length_mm,
        )
    
    @staticmethod
    def shear(shear_displacement_mm: float, height_mm: float) -> StrainResult:
        """Shear strain: γ = δ / h"""
        strain = shear_displacement_mm / height_mm if height_mm > 0 else 0
        return StrainResult(
            strain=strain,
            type="Shear Strain",
            original_dimension=height_mm,
            change_dimension=shear_displacement_mm,
        )
    
    @staticmethod
    def volumetric(original_volume_m3: float, change_in_volume_m3: float) -> StrainResult:
        """Volumetric strain: ε_v = ΔV / V"""
        strain = change_in_volume_m3 / original_volume_m3 if original_volume_m3 > 0 else 0
        return StrainResult(
            strain=strain,
            type="Volumetric Strain",
            original_dimension=original_volume_m3,
            change_dimension=change_in_volume_m3,
        )


# ============================================================================
# SECTION 3: ELASTIC CONSTANTS
# ============================================================================

@dataclass
class ElasticConstantsResult:
    """Result of elastic constants calculation."""
    
    E_gpa: float
    G_gpa: float
    K_gpa: float
    nu: float
    material_name: str
    
    def print(self):
        print(f"   Material: {self.material_name}")
        print(f"   Young's Modulus E: {self.E_gpa:.1f} GPa")
        print(f"   Shear Modulus G: {self.G_gpa:.1f} GPa")
        print(f"   Bulk Modulus K: {self.K_gpa:.1f} GPa")
        print(f"   Poisson's Ratio ν: {self.nu:.3f}")


@dataclass
class ElasticConstants:
    """Elastic constants of materials - Chapter 4.7, 4.8."""
    
    material: DeformationMaterial
    
    def get_constants(self) -> ElasticConstantsResult:
        """Get all elastic constants."""
        return ElasticConstantsResult(
            E_gpa=self.material.youngs_modulus_gpa,
            G_gpa=self.material.shear_modulus_gpa,
            K_gpa=self.material.bulk_modulus_gpa,
            nu=self.material.poissons_ratio,
            material_name=self.material.name,
        )
    
    @staticmethod
    def from_youngs_poisson(E_gpa: float, nu: float) -> Tuple[float, float]:
        """Calculate G and K from E and ν."""
        G = E_gpa / (2 * (1 + nu))
        K = E_gpa / (3 * (1 - 2 * nu))
        return G, K


# ============================================================================
# SECTION 4: HOOKE'S LAW
# ============================================================================

@dataclass
class HookeResult:
    """Result of Hooke's law calculation."""
    
    value: float
    unit: str
    formula: str
    
    def print(self):
        print(f"   {self.formula}: {self.value:.2f} {self.unit}")


@dataclass
class HookesLaw:
    """Hooke's Law - Chapter 4.7."""
    
    @staticmethod
    def axial_stress(E_gpa: float, strain: float) -> HookeResult:
        """σ = E × ε"""
        stress = E_gpa * 1000 * strain
        return HookeResult(value=stress, unit="MPa", formula="σ = E × ε")
    
    @staticmethod
    def axial_strain(E_gpa: float, stress_mpa: float) -> HookeResult:
        """ε = σ / E"""
        strain = stress_mpa / (E_gpa * 1000)
        return HookeResult(value=strain, unit="mm/mm", formula="ε = σ / E")
    
    @staticmethod
    def shear_stress(G_gpa: float, shear_strain: float) -> HookeResult:
        """τ = G × γ"""
        stress = G_gpa * 1000 * shear_strain
        return HookeResult(value=stress, unit="MPa", formula="τ = G × γ")
    
    @staticmethod
    def shear_strain(G_gpa: float, shear_stress_mpa: float) -> HookeResult:
        """γ = τ / G"""
        strain = shear_stress_mpa / (G_gpa * 1000)
        return HookeResult(value=strain, unit="rad", formula="γ = τ / G")


# ============================================================================
# SECTION 5: POISSON'S RATIO
# ============================================================================

@dataclass
class PoissonResult:
    """Result of Poisson's ratio calculation."""
    
    poissons_ratio: float
    lateral_strain: float
    axial_strain: float
    
    def print(self):
        print(f"   Poisson's Ratio ν: {self.poissons_ratio:.3f}")
        print(f"   Lateral strain: {self.lateral_strain:.6f}")
        print(f"   Axial strain: {self.axial_strain:.6f}")


@dataclass
class PoissonsRatio:
    """Poisson's Ratio - Chapter 4.18."""
    
    material: DeformationMaterial
    
    @staticmethod
    def calculate(lateral_strain: float, axial_strain: float) -> float:
        """ν = -ε_lateral / ε_axial"""
        return -lateral_strain / axial_strain if axial_strain != 0 else 0
    
    def get_lateral_strain(self, axial_strain: float) -> float:
        """ε_lateral = -ν × ε_axial"""
        return -self.material.poissons_ratio * axial_strain
    
    def get_axial_strain(self, lateral_strain: float) -> float:
        """ε_axial = -ε_lateral / ν"""
        return -lateral_strain / self.material.poissons_ratio if self.material.poissons_ratio != 0 else 0
    
    def analyze(self, axial_strain: float) -> PoissonResult:
        """Complete Poisson analysis for given axial strain."""
        lateral = self.get_lateral_strain(axial_strain)
        return PoissonResult(
            poissons_ratio=self.material.poissons_ratio,
            lateral_strain=lateral,
            axial_strain=axial_strain,
        )
    
    @staticmethod
    def typical_values() -> Dict[str, float]:
        """Typical Poisson's ratio values for common materials."""
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


# ============================================================================
# SECTION 6: DEFORMATION CALCULATIONS
# ============================================================================

@dataclass
class DeformationResult:
    """Result of deformation calculation."""
    
    deformation_mm: float
    force_kN: float
    length_mm: float
    area_mm2: float
    material: str
    
    def print(self):
        print(f"   Deformation: {self.deformation_mm:.4f} mm")
        print(f"   Force: {self.force_kN:.2f} kN")
        print(f"   Length: {self.length_mm:.1f} mm")
        print(f"   Area: {self.area_mm2:.2f} mm²")
        print(f"   Material: {self.material}")


@dataclass
class DeformationCalculator:
    """Deformation calculations - Chapter 4.4-4.7."""
    
    material: DeformationMaterial
    
    def elastic_elongation(self, force_n: float, length_mm: float, area_mm2: float) -> DeformationResult:
        """ΔL = (P × L) / (A × E)"""
        E_pa = self.material.E_pa
        deformation_m = (force_n * (length_mm / 1000)) / ((area_mm2 / 1e6) * E_pa)
        deformation_mm = deformation_m * 1000
        
        return DeformationResult(
            deformation_mm=deformation_mm,
            force_kN=force_n / 1000,
            length_mm=length_mm,
            area_mm2=area_mm2,
            material=self.material.name,
        )
    
    def tapered_bar(self, force_n: float, length_mm: float, 
                    d1_mm: float, d2_mm: float) -> DeformationResult:
        """ΔL = (4 × P × L) / (π × E × d1 × d2)"""
        area_eff = math.pi * d1_mm * d2_mm / 4
        return self.elastic_elongation(force_n, length_mm, area_eff)
    
    @staticmethod
    def stepped_bar(segments: List[Tuple[float, float, float, float]]) -> float:
        """
        Total deformation for stepped bar.
        
        Parameters:
        -----------
        segments : list of (force_N, length_mm, area_mm2, E_gpa)
        """
        total = 0
        for force, length, area, E_gpa in segments:
            E_pa = E_gpa * 1e9
            area_m2 = area / 1e6
            length_m = length / 1000
            deformation_m = (force * length_m) / (area_m2 * E_pa)
            total += deformation_m * 1000
        return total


# ============================================================================
# SECTION 7: VOLUMETRIC DEFORMATION
# ============================================================================

@dataclass
class VolumetricResult:
    """Result of volumetric deformation calculation."""
    
    volumetric_strain: float
    volume_change_m3: float
    original_volume_m3: float
    pressure_mpa: float
    
    def print(self):
        print(f"   Volumetric strain: ε_v = {self.volumetric_strain:.6f}")
        print(f"   Volume change: {self.volume_change_m3 * 1e6:.2f} cm³")
        print(f"   Original volume: {self.original_volume_m3 * 1e6:.2f} cm³")
        print(f"   Pressure: {self.pressure_mpa:.2f} MPa")


@dataclass
class VolumetricDeformation:
    """Volume changes under stress - Chapter 4.19-4.21."""
    
    material: DeformationMaterial
    
    def uniaxial(self, stress_mpa: float, volume_m3: float) -> VolumetricResult:
        """ε_v = (σ / E) × (1 - 2ν) for uniaxial loading."""
        E_pa = self.material.E_pa
        nu = self.material.poissons_ratio
        stress_pa = stress_mpa * 1e6
        
        volumetric_strain = (stress_pa / E_pa) * (1 - 2 * nu)
        volume_change = volume_m3 * volumetric_strain
        
        return VolumetricResult(
            volumetric_strain=volumetric_strain,
            volume_change_m3=volume_change,
            original_volume_m3=volume_m3,
            pressure_mpa=stress_mpa,
        )
    
    def hydrostatic(self, pressure_mpa: float, volume_m3: float) -> VolumetricResult:
        """ε_v = ΔP / K for hydrostatic pressure."""
        K_pa = self.material.K_pa
        pressure_pa = pressure_mpa * 1e6
        
        volumetric_strain = pressure_pa / K_pa
        volume_change = volume_m3 * volumetric_strain
        
        return VolumetricResult(
            volumetric_strain=volumetric_strain,
            volume_change_m3=volume_change,
            original_volume_m3=volume_m3,
            pressure_mpa=pressure_mpa,
        )


# ============================================================================
# SECTION 8: EXAMPLE USAGE
# ============================================================================

if __name__ == "__main__":
    print("=" * 75)
    print("DEEP DEFORMATION ANALYSIS MODULE")
    print("Sources: Khurmi (Chap 4), Shigley, Timoshenko")
    print("=" * 75)
    
    # Example 1: Get material and elastic constants
    print("\n1. ELASTIC CONSTANTS:")
    print("-" * 40)
    steel = get_deformation_material("Structural Steel")
    constants = ElasticConstants(steel)
    constants.get_constants().print()
    
    # Example 2: Strain calculation
    print("\n2. STRAIN CALCULATION:")
    print("-" * 40)
    result = Strain.linear(original_length_mm=200, change_in_length_mm=0.4)
    result.print()
    
    # Example 3: Hooke's Law
    print("\n3. HOOKE'S LAW:")
    print("-" * 40)
    stress = HookesLaw.axial_stress(steel.youngs_modulus_gpa, strain=0.001)
    stress.print()
    
    # Example 4: Deformation calculation
    print("\n4. DEFORMATION CALCULATION:")
    print("-" * 40)
    deform = DeformationCalculator(steel)
    result = deform.elastic_elongation(force_n=50000, length_mm=3000, area_mm2=706.86)
    result.print()
    
    # Example 5: Poisson's ratio analysis
    print("\n5. POISSON'S RATIO ANALYSIS:")
    print("-" * 40)
    poisson = PoissonsRatio(steel)
    result = poisson.analyze(axial_strain=0.001)
    result.print()
    
    # Example 6: Volumetric deformation
    print("\n6. VOLUMETRIC DEFORMATION:")
    print("-" * 40)
    volume = VolumetricDeformation(steel)
    result = volume.uniaxial(stress_mpa=100, volume_m3=0.001)
    result.print()
    
    print("\n" + "=" * 75)
    print("✅ Deep deformation module ready")
    print("=" * 75)