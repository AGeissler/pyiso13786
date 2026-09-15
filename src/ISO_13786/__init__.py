from .__about__ import __version__

__all__ = [
   "material_db",
   "Database",
   "Material",
   "Layer",
   "Construction",
   "Space",
   "plot_bar_chart_comparison",
   "unit_normals",
   "create_dimension_dict",
   "poly_area",
   "poly_side_lengths",
   "d2_fun",
   "tilted_window_vertices"
]


def __getattr__(name):
    if name in {"material_db"}:
        from .material_db import material_db
        return {
            "material_db": material_db
        }[name]
    if name in {"Database"}:
        from .database import Database
        return {
            "Database": Database
        }[name]
    if name in {"Material", "Layer"}:
        from .layer import Material, Layer
        return {
            "Material": Material,
            "Layer": Layer
        }[name]
    if name in {"Construction"}:
        from .construction import Construction
        return {
            "Construction": Construction
        }[name]
    if name in {"Space"}:
        from .space import Space
        return {
            "Space": Space
        }[name]
    if name in {"plot_bar_chart_comparison", "unit_normals", "create_dimension_dict",
                "poly_area", "poly_side_lengths", "d2_fun", "tilted_window_vertices"}:
        from .utils import (
            plot_bar_chart_comparison,
            unit_normals,
            create_dimension_dict,
            poly_area,
            poly_side_lengths,
            d2_fun,
            tilted_window_vertices
        )
        return {
            "plot_bar_chart_comparison": plot_bar_chart_comparison,
            "unit_normals": unit_normals,
            "create_dimension_dict": create_dimension_dict,
            "poly_area": poly_area,
            "poly_side_lengths": poly_side_lengths,
            "d2_fun": d2_fun,
            "tilted_window_vertices": tilted_window_vertices
        }[name]
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
