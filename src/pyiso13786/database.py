"""Database class to manage material, layer, construction system and space
   data for ISO 13796 package."""
import os
from ast import literal_eval
from typing import List, Dict, Optional
from pathlib import Path
import pandas as pd

# Local imports
from .layer import Material, Layer
from .construction import Construction
from .space import Space

class Database:
    """Database for ISO 13786 materials, layers, construction types and spaces."""
    _instance = None

    @classmethod
    def get_instance(cls, data_dir: Path = Path("data")):
        """Return the shared database instance, creating it on first use."""
        if cls._instance is None:
            cls._instance = cls(data_dir)
        return cls._instance

    def __init__(self, data_dir: Path = Path("data")):
        """Initialise the database from CSV data files in the given directory."""
        if self.__class__._instance is not None:
            raise RuntimeError("Database is a singleton. Use get_instance()" +
                               " instead of direct instantiation")
        self.data_dir = data_dir
        self.data_dir.mkdir(parents=True, exist_ok=True)

        # Read all materials to dict of Material instances.
        materials_df = pd.read_csv(Path(self.data_dir / 'materials.csv'))
        self.materials = {
            row['name']: Material(
                name=row['name'],
                density=float(row['density']),
                specific_heat=float(row['specific_heat']),
                thermal_conductivity=float(row['thermal_conductivity']),
                vapor_permeability=float(row['vapor_permeability'])
            )
            for _, row in materials_df.iterrows()
        }

        # Read all layers to dict of Layer instances.
        layers_df = pd.read_csv(Path(self.data_dir / 'layers.csv'))
        self.layers = {
            row['name']: Layer(
                name=row['name'],
                thickness=float(row['thickness']),
                material=self.materials[row['material']],
                color=row['color']
            )
            for _, row in layers_df.iterrows()
        }

        # Read all constructions to dict of Construction instances.
        constructions_df = pd.read_csv(Path(self.data_dir / 'constructions.csv'))
        self.constructions = {
            row['name']: Construction(
                name=row['name'],
                layers=[self.layers[layer.strip()]
                        for layer in row['layers'].split(', ')],
                partition=row['partition'],
                type=row['type']
            )
            for _, row in constructions_df.iterrows()
        }

        # Read all spaces to dict of Space instances.
        spaces_df = pd.read_csv(Path(self.data_dir / 'spaces.csv'))
        self.spaces = {}
        for _, row in spaces_df.iterrows():
            # Convert construction_list string back to list of tuples
            construction_list = literal_eval(row['construction_list'])

            # Create Space object
            self.spaces[row['name']] =\
                Space(
                    name=row['name'],
                    width=row['width'],
                    height=row['height'],
                    depth=row['depth'],
                    construction_list=[(desc, self.constructions[name])
                                       for desc, name in construction_list],
                    depth_factor=row['depth_factor'],
                    deeper_than=row['deeper_than'],
                    glass_area_number=row['glass_area_number'],
                    window_frame_fraction=row['window_frame_fraction'],
                    ceiling_split_fraction=row['ceiling_split_fraction'],
                    windows_in_two_facades=row['windows_in_two_facades'],
                    roof_space=row['roof_space'],
                    jamb_height=row['jamb_height'],
                    roof_tilt=row['roof_tilt']
                )

    def deconstruct_space(self, space: Space) -> Dict[str, Dict]:
        r"""Deconstruct a space into its constituent materials, layers and constructions.

        Parameters
        ----------
        space : Space
            A Space object from ISO_13786.

        Returns
        -------
        dict : Dictionary containing all components organized by type.

        """
        # Get all constructions from the space
        constructions = {}
        seen_construction_names = set()
        for _, construction in space.construction_list:
            construction_key = construction.name
            if construction_key not in seen_construction_names:
                constructions[construction_key] = {
                    'name': construction.name,
                    'layers': [f"{layer.name}" for layer in construction.layers],
                    'layer_obj': list(construction.layers),
                    'partition': construction.partition,
                    'type': construction.type
                }
                seen_construction_names.add(construction_key)

        # Get all unique layers used in the space
        layers = {}
        seen_layer_names = set()
        for construction in constructions.values():
            for layer in construction['layer_obj']:
                layer_key = layer.name
                if layer_key not in seen_layer_names:
                    layers[layer_key] = {
                        'name': layer.name,
                        'thickness': layer.thickness,
                        'material': layer.material.name,
                        'material_obj': layer.material,
                        'color': layer.color
                    }
                seen_layer_names.add(layer_key)

        # Get all unique materials used in the space
        materials = {}
        seen_material_names = set()
        for layer in layers.values():
            material = layer['material_obj']
            material_key = material.name
            if material_key not in seen_material_names:
                materials[material_key] = {
                    'name': material.name,
                    'density': material.density,
                    'specific_heat': material.specific_heat,
                    'thermal_conductivity': material.thermal_conductivity,
                    'vapor_permeability': material.vapor_permeability
                }
            seen_material_names.add(material_key)

        # Create the final dictionary structure
        components = {
            space.name: {
                'name': space.name,
                'width': space.width,
                'height': space.height,
                'depth': space.depth,
                'construction_list': [(description, construction.name)
                                      for description, construction
                                      in space.construction_list],
                'depth_factor': space.depth_factor,
                'deeper_than': space.deeper_than,  # m
                'glass_area_number': space.glass_area_number,
                'window_frame_fraction': space.window_frame_fraction,
                'ceiling_split_fraction': space.ceiling_split_fraction,
                'windows_in_two_facades': space.windows_in_two_facades,
                'roof_space': space.roof_space,
                'jamb_height': space.jamb_height,
                'roof_tilt': space.roof_tilt
            },
            'constructions': constructions,
            'layers': layers,
            'materials': materials
        }

        return components

    def write_components_to_csv(self,
                                spaces: List[Dict[str, Dict]],
                                data_dir: str = "data"):
        r"""Write the provided space components to CSV files in a canonical form.

        This method is mainly intended for creating the initial CSV files from
        existing space definitions, for example in a SIA 180 project.

        Parameters
        ----------
        spaces : list
            List of component dictionaries from multiple spaces.
        data_dir: str (optional, default: "data")
            Directory where the output CSV files should be written.

        """
        # Create data directory if it doesn't exist
        if not os.path.exists(data_dir):
            os.makedirs(data_dir)

        # Initialize dictionaries to collect unique components
        all_materials = {}
        all_layers = {}
        all_constructions = {}

        # Initialize list to collect all space entries
        all_spaces = []

        # Process each space's components
        for components in spaces:
            # Add materials
            for material_name, material_data in components['materials'].items():
                if material_name not in all_materials:
                    all_materials[material_name] = material_data

            # Add layers
            for layer_name, layer_data in components['layers'].items():
                if layer_name not in all_layers:
                    all_layers[layer_name] = layer_data

            # Add constructions
            for construction_name, construction_data in components['constructions'].items():
                if construction_name not in all_constructions:
                    all_constructions[construction_name] = construction_data

            # Collect space properties
            space_name = next(iter(components))  # Get space name from dictionary key
            space_data = components[space_name]

            # Create space entry
            space_entry = {
                'name': space_name,
                'width': space_data['width'],
                'height': space_data['height'],
                'depth': space_data['depth'],
                'construction_list': str(space_data['construction_list']),
                'depth_factor': space_data['depth_factor'],
                'deeper_than': space_data['deeper_than'],
                'glass_area_number': space_data['glass_area_number'],
                'window_frame_fraction': space_data['window_frame_fraction'],
                'ceiling_split_fraction': space_data['ceiling_split_fraction'],
                'windows_in_two_facades': space_data['windows_in_two_facades'],
                'roof_space': space_data['roof_space'],
                'jamb_height': space_data['jamb_height'],
                'roof_tilt': space_data['roof_tilt']
            }
            all_spaces.append(space_entry)

        # Write spaces file
        spaces_file = os.path.join(data_dir, 'spaces.csv')
        spaces_df = pd.DataFrame(all_spaces)
        spaces_df.to_csv(spaces_file, index=False)

        # Write combined materials file
        materials_file = os.path.join(data_dir, 'materials.csv')
        materials_df = pd.DataFrame({
            'name': [data['name'] for data in all_materials.values()],
            'density': [data['density'] for data in all_materials.values()],
            'specific_heat': [data['specific_heat'] for data in all_materials.values()],
            'thermal_conductivity': [data['thermal_conductivity']
                                     for data in all_materials.values()],
            'vapor_permeability': [data['vapor_permeability']
                                   for data in all_materials.values()]
        })
        materials_df.to_csv(materials_file, index=False)

        # Write combined layers file
        layers_file = os.path.join(data_dir, 'layers.csv')
        layers_df = pd.DataFrame({
            'name': [data['name'] for data in all_layers.values()],
            'thickness': [data['thickness'] for data in all_layers.values()],
            'material': [data['material'] for data in all_layers.values()],
            'color': [data['color'] for data in all_layers.values()]
        })
        layers_df.to_csv(layers_file, index=False)

        # Write combined constructions file
        constructions_file = os.path.join(data_dir, 'constructions.csv')
        constructions_df = pd.DataFrame({
            'name': [data['name'] for data in all_constructions.values()],
            'layers': [', '.join(data['layers']) for data in all_constructions.values()],
            'partition': [data['partition'] for data in all_constructions.values()],
            'type': [data['type'] for data in all_constructions.values()]
        })
        constructions_df.to_csv(constructions_file, index=False)

    def list_spaces(self) -> pd.DataFrame:
        """Return a dataframe containing all spaces stored in the database directory.

        Returns
        -------
        DataFrame of spaces with their properties.

        """
        spaces_file = Path(self.data_dir / 'spaces.csv')
        if not Path.exists(spaces_file):
            raise FileNotFoundError(f"No spaces found in directory '{self.data_dir}'")

        return pd.read_csv(spaces_file)

    def get_component_usage(self) -> Dict[str, Dict]:
        """Return usage counts for materials, layers and constructions across all spaces.

        Returns
        -------
        dict of usage statistics for each component type.

        """
        # Get spaces
        spaces_df = self.list_spaces()

        # Read constructions to get layer references
        constructions_df = pd.read_csv(Path(self.data_dir /'constructions.csv'))
        constructions = {
            row['name']: row['layers'].split(', ')  # List of layer names
            for _, row in constructions_df.iterrows()
        }

        # Initialize usage stats
        usage_stats = {
            'materials': {},
            'layers': {},
            'constructions': {}
        }

        # Count usage of each component
        for _, space in spaces_df.iterrows():
            # Get construction list
            construction_list = literal_eval(space['construction_list'])

            # Count constructions
            for _, construction_name in construction_list:
                construction_name = construction_name.strip()  # Remove any whitespace
                if construction_name in constructions:
                    usage_stats['constructions'][construction_name] = (
                        usage_stats['constructions'].get(construction_name, 0) + 1
                    )

                    # Count layers for this construction
                    layers = constructions[construction_name]
                    for layer in layers:
                        layer = layer.strip()
                        usage_stats['layers'][layer] = usage_stats['layers'].get(layer, 0) + 1

                        # Count material for this layer
                        layer_df = pd.read_csv(Path(self.data_dir / 'layers.csv'))
                        layer_row = layer_df[layer_df['name'] == layer]
                        if not layer_row.empty:
                            material = layer_row.iloc[0]['material']
                            usage_stats['materials'][material] = (
                                usage_stats['materials'].get(material, 0) + 1
                            )

        return usage_stats

    def add_space(self, space: Space):
        """Add a new space to the database and persist it."""
        if any(s.name == space.name for s in self.spaces):
            raise ValueError(f"Space with name '{space.name}' already exists")
        self.spaces[space.name] = space
        self.save_data()

    def get_space_by_name(self, name: str) -> Optional[Space]:
        """Return a space by name, or None if it is not present."""
        return next((s for s in self.spaces if s.name == name), None)

    def update_space(self, space: Space):
        """Replace an existing space definition and persist the change."""
        existing = self.get_space_by_name(space.name)
        if not existing:
            raise ValueError(f"Space with name '{space.name}' not found")

        # Replace the existing space with the updated one
        self.spaces[space.name] = space
        self.save_data()

    def delete_space(self, name: str):
        """Delete a space from the database by name."""
        existing = self.get_space_by_name(name)
        if not existing:
            raise ValueError(f"Space with name '{name}' not found")

        del self.spaces[name]
        self.save_data()

    def get_construction_by_name(self, name: str) -> Optional[Dict]:
        """Return a construction by name, if present in the database."""
        return next((c for c in self.constructions if c.name == name), None)

    def get_material_by_name(self, name: str) -> Optional[Dict]:
        """Return a material by name, if present in the database."""
        return next((m for m in self.materials if m.name == name), None)

    def save_data(self):
        """Persist the database state to CSV files."""
        # Ensure data_dir exists (it should from __init__, but good practice)
        self.data_dir.mkdir(parents=True, exist_ok=True)

        # Define column headers to ensure consistency and correct order
        material_cols = ['name', 'density', 'specific_heat',
                         'thermal_conductivity', 'vapor_permeability']
        layer_cols = ['name', 'thickness', 'material', 'color']
        construction_cols = ['name', 'layers', 'partition', 'type']
        space_cols = ['name', 'width', 'height', 'depth', 'construction_list',
                      'depth_factor', 'deeper_than', 'glass_area_number',
                      'window_frame_fraction', 'ceiling_split_fraction',
                      'windows_in_two_facades',
                      'roof_space', 'jamb_height', 'roof_tilt']

        # Save Materials
        materials_data = [{
            'name': mat.name, 'density': mat.density,
            'specific_heat': mat.specific_heat,
            'thermal_conductivity': mat.thermal_conductivity,
            'vapor_permeability': mat.vapor_permeability
        } for mat in self.materials.values()]
        materials_df = pd.DataFrame(materials_data, columns=material_cols)
        materials_df.to_csv(self.data_dir / 'materials.csv', index=False)

        # Save Layers
        layers_data = [{
            'name': layer.name, 'thickness': layer.thickness,
            'material': layer.material.name, # Store material name
            'color': layer.color
        } for layer in self.layers.values()]
        layers_df = pd.DataFrame(layers_data, columns=layer_cols)
        layers_df.to_csv(self.data_dir / 'layers.csv', index=False)

        # Save Constructions
        constructions_data = [{
            'name': constr.name,
            # Comma-separated layer names.
            'layers': ', '.join([layer_obj.name for layer_obj in constr.layers]),
            'partition': constr.partition,
            'type': constr.type
        } for constr in self.constructions.values()]
        constructions_df = pd.DataFrame(constructions_data, columns=construction_cols)
        constructions_df.to_csv(self.data_dir / 'constructions.csv', index=False)

        # Save Spaces
        spaces_data = []
        for space in self.spaces.values():
            construction_list_to_save = [
                (desc, constr_obj.name) for desc, constr_obj in space.construction_list
            ]
            spaces_data.append({
                'name': space.name, 'width': space.width, 'height': space.height,
                'depth': space.depth, 'construction_list': str(construction_list_to_save),
                'depth_factor': space.depth_factor, 'deeper_than': space.deeper_than,
                'glass_area_number': space.glass_area_number,
                'window_frame_fraction': space.window_frame_fraction,
                'ceiling_split_fraction': space.ceiling_split_fraction,
                'windows_in_two_facades': space.windows_in_two_facades,
                'roof_space': space.roof_space,
                'jamb_height': space.jamb_height,
                'roof_tilt': space.roof_tilt
            })
        spaces_df = pd.DataFrame(spaces_data, columns=space_cols)
        spaces_df.to_csv(self.data_dir / 'spaces.csv', index=False)
