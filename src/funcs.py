"""
================================================
        Lake Erie Abatement Optimization
================================================

This script contains model parameters.
"""

import pandas as pd
import os
from numpy import diag, array, ones


def getMatrixAndVector():
    return (
        pd.read_csv("inputdata/Lmat.csv").values.T,
        pd.read_csv("inputdata/fvec.csv").values,
    )


def getModelParams():
    regions = 6
    L, E = getMatrixAndVector()
    P_ppm = 2.737  # mg/L
    factor = 1e-3  # converts mg/L to t/thousand m3: [1e9 mg = 1 t] [1e3 L = 1 m3]
    filter_eff = 0.4  # unitless
    F = (
        P_ppm * factor * filter_eff * diag(E.reshape(-1))
    )  # [filter eff] * [t/thousand m3]] * [thousand m3/year] = [t/year]
    wwtps = F.shape[0]
    S = (
        array(
            [
                [6.25, 0.00, 0.00, 0.00, 0.00, 0.00],
                [4.92, 4.92, 0.00, 0.00, 0.00, 0.00],
                [4.90, 4.90, 6.05, 0.00, 0.00, 0.00],
                [2.51, 2.51, 3.10, 3.10, 0.00, 0.00],
                [0.73, 0.73, 0.90, 0.90, 1.48, 0.00],
                [0.36, 0.36, 0.44, 0.44, 0.73, 1.30],
            ]
        )
        * 1e-3
    )
    W = S @ L @ F
    # Agriculture abatement
    a = array(
        [
            (0.004) * 7.20,  #  SCR
            (0.004) * 0.61,  #  LCS
            (0.004) * 15.5,  #   DR
            (0.004) * 9.24,  #   WB
            (0.004) * 2.23,  #   CB
            (0.004) * 0.77,  #   EB
        ]
    )
    A = diag(a)
    # Positive externality
    c = 1.0e-3 * ones(regions)  # million CAD / ppb
    # WWTP costs
    maintenance_cost = 1e-4  # million CAD / (thousand m3 * year)
    b = maintenance_cost * E.reshape(-1)

    return {
        "region_names": ["SCR", "LSC", "DR", "WB", "CB", "EB"],
        "n_regions": regions,
        "n_wwtps": wwtps,
        "E": E,
        "F": F,
        "L": L,
        "S": S,
        "W": W,
        "A": A,
        "b": b,
        "c": c,
        "volume_km3": {
            "SCR": 0.4,
            "LSC": 4.6,
            "DR": 0.4,
            "WB": 27.8,
            "CB": 318.7,
            "EB": 159.3,
        },
    }


if __name__ == "__main__":
    pass
