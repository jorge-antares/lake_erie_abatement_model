"""
================================================
            Lake Erie Abatement Model
================================================

October 2025

This script contains the parameters of the Lake
Erie abatement model.

================================================
"""

import pandas as pd
from pathlib import Path
from numpy import diag, array, ones, ceil


def getFixedParameters() -> dict:
    """
    Reads L matrix and fvec vector from CSV files.
    
    Returns:
        L: array     Matrix that assigns WWTPs to regions. 
        fvec: array  Vector of WWTP annual flow rates.
        S: array     Matrix of sedimentation rates.
    """
    base_dir = Path(__file__).resolve().parent / "wwtpdata"
    lmat_path = base_dir / "Lmat.csv"
    fvec_path = base_dir / "fvec.csv"

    if not lmat_path.exists() or not fvec_path.exists():
        raise FileNotFoundError(
            f"Required CSV files not found. Checked:\n  {lmat_path}\n  {fvec_path}"
        )
    
    L, fvec = pd.read_csv(lmat_path).values.T, pd.read_csv(fvec_path).values
    
    S = array(
            [
                [6.25, 0.00, 0.00, 0.00, 0.00, 0.00],
                [4.92, 4.92, 0.00, 0.00, 0.00, 0.00],
                [4.90, 4.90, 6.05, 0.00, 0.00, 0.00],
                [2.51, 2.51, 3.10, 3.10, 0.00, 0.00],
                [0.73, 0.73, 0.90, 0.90, 1.48, 0.00],
                [0.36, 0.36, 0.44, 0.44, 0.73, 1.30],
            ]
    ) * 1e-3

    return {
        "region_names": ["SCR", "LSC", "DR", "WB", "CB", "EB"],
        "max_wwtp_effl": ceil(fvec.max()),
        "n_wwtps": L.shape[1],
        "n_regions": 6,
        "fvec": fvec,
        "S": S,
        "L": L,
        "volume_km3": {
            "SCR": 0.4,
            "LSC": 4.6,
            "DR": 0.4,
            "WB": 27.8,
            "CB": 318.7,
            "EB": 159.3
        }
    }


def getCalculatedParams(
        fixed_params:dict,
        P_ppm:float = 2.737,            # P concentration in WWTP [mg/L]
        filter_eff:float = 0.4,         # unitless
        maintenance_cost:float = 1e-4,  # [million CAD / (thousand m3 * year)]
        wwtp_effluent_threshold:float = 1e8,    # thousand m3 / year
        agro_abatecost:list = [2.88e-2, 2.44e-3, 6.2e-2, 3.69e-2, 8.92e-3, 3.08e-3] # [million CAD / t^2-year]
        ) -> dict:
    """
    Agriculture abatement default cost matrix A
    A = diag(array(
        [
            (0.004) * 7.20,  #  SCR
            (0.004) * 0.61,  #  LCS
            (0.004) * 15.5,  #   DR
            (0.004) * 9.24,  #   WB
            (0.004) * 2.23,  #   CB
            (0.004) * 0.77,  #   EB
        ]
    ))
    """
    # Factor that converts mg/L to t/thousand m3: [1e9 mg = 1 t] [1e3 L = 1 m3]
    factor = 1e-3

    # Emissions: [filter eff] * [t/thousand m3]] * [thousand m3/year] = [t/year]
    F = P_ppm * factor * filter_eff * diag(fixed_params["fvec"].reshape(-1))
    
    return {
        "b": maintenance_cost * fixed_params["fvec"].reshape(-1),
        "u_w": fixed_params["fvec"] <= wwtp_effluent_threshold,
        "W": fixed_params["S"] @ fixed_params["L"] @ F,
        "A": diag(array(agro_abatecost)),
        "F": F
    }


if __name__ == "__main__":
    pass
