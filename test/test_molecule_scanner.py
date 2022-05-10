import pytest
from molecule_scanner import msc
import numpy as np
import pandas as pd


def test_initialize():
    msc_test = msc(
        # xyz_filepath="../test/data/nhc.xyz",
        xyz_filepath="test/data/mad25_p.xyz",
        sphere_center_atom_ids=[1],
        z_ax_atom_ids=[2],
        xz_plane_atoms_ids=[1, 3, 9],
        atoms_to_delete_ids=[1],
        # working_dir=os.path.join(os.path.abspath("."), "test_directory")
    )


def test_run_single():
    msc_test = msc(
        # xyz_filepath="../test/data/nhc.xyz",
        xyz_filepath="test/data/mad25_p.xyz",
        sphere_center_atom_ids=[1],
        z_ax_atom_ids=[2],
        xz_plane_atoms_ids=[1, 3, 9],
        atoms_to_delete_ids=[1],
        # working_dir=os.path.join(os.path.abspath("."), "test_directory")
    )

    (
        total_results_without_H,
        quadrant_results_without_H,
        octant_results_without_H,
    ) = msc_test.run_single(sphere_radius=3.5)

    (
        total_results_with_H,
        quadrant_results_with_H,
        octant_results_with_H,
    ) = msc_test.run_single(3.5, 1, 0.3, False, False, False)

    assert total_results_without_H == {
        "free_volume": 55.7,
        "buried_volume": 123.8,
        "total_volume": 179.4,
        "exact_volume": 179.6,
        "percent_buried_volume": 69.0,
        "percent_free_volume": 31.0,
        "percent_total_volume": 99.9,
    }
    assert total_results_with_H == {
        "free_volume": 38.7,
        "buried_volume": 141.2,
        "total_volume": 180.0,
        "exact_volume": 179.6,
        "percent_buried_volume": 78.5,
        "percent_free_volume": 21.5,
        "percent_total_volume": 100.2,
    }


def test_run_range():
    msc_test = msc(
        # xyz_filepath="../test/data/nhc.xyz",
        xyz_filepath="test/data/mad25_p.xyz",
        sphere_center_atom_ids=[1],
        z_ax_atom_ids=[2],
        xz_plane_atoms_ids=[1, 3, 9],
        atoms_to_delete_ids=[1],
        # working_dir=os.path.join(os.path.abspath("."), "test_directory")
    )

    df_scan_1_63 = msc_test.run_range(r_min=3, r_max=5, nsteps=40, n_threads=-1)
    assert len(df_scan_1_63) == 40
