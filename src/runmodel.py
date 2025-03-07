"""
================================================
        Lake Erie Abatement Optimization
================================================

Main optimization model.

DECISION VARIABLES
    x - Agro abatement by region (metric tonnes per year)
    w - Vector of binary variuables (unitless)

MODEL
    min x^T A x + b^T w
s.t.
    S x + W w >= z_target
    x >= 0
    w binary
    W = (S*L*F)

"""

import cvxpy

from numpy import array
from funcs import getModelParams


def solveModel(ztarget, params):
    # DECISION VARIABLES
    x = cvxpy.Variable(shape=params["n_regions"], name="x")
    w = cvxpy.Variable(shape=params["n_wwtps"], integer=True, name="w")

    # SOLVER
    model = cvxpy.Problem(
        cvxpy.Minimize(cvxpy.quad_form(x, params["A"]) + params["b"].T @ w),
        [
            params["S"] @ x + params["W"] @ w >= ztarget,
            w <= 1,
            w >= 0,
            x >= 0,
        ],
    )
    model.solve(solver="SCIP", verbose=False)

    if model.status not in ["infeasible", "unbounded"]:
        print(f"\nCost:\t {model.value:.4g} millions per year")
        print("\n∆ Load [t/year]:")
        for reg, entry in zip(params["region_names"], x.value):
            print(reg, f"\t{round(entry,2)}")

        print("\n∆ Load WWTPs [t/year]:")
        for reg, entry in zip(
            params["region_names"], params["L"] @ params["F"] @ w.value
        ):
            print(reg, f"\t{round(entry,2)}")

        print("\nConcentration [ppb/year]\tResponse ∆Load")
        zopt = params["S"] @ x.value + params["W"] @ w.value
        for reg, entry in zip(params["region_names"], zopt):
            deltaz = round(entry * params["volume_km3"][reg], 4)
            print(reg, f"\t{round(entry,4)}\t\t\t{deltaz}")

        print("\nWWTPs that need investment:")
        www = params["L"] @ w.value
        for j in range(len(www)):
            print(params["region_names"][j], "\t", int(www[j]))
    else:
        print("No solution found... :(")
    return model


def saveResults(model, params, filename):
    x = model.variables()[0].value
    w = model.variables()[1].value
    load_w = params["L"] @ params["F"] @ w
    total_load = [i + j for i, j in zip(x, load_w)]
    n_wwtp = params["L"] @ w
    zopt = params["S"] @ x + params["W"] @ w
    zload = [i * j for i, j in zip(zopt, params["volume_km3"].values())]

    with open(f"{filename}.csv", "w") as outfile:
        outfile.write(
            "REGION,AGRO_ABATE_t,WWTP_ABATE_t,TOTAL_ABATE_t,NUMBER_WWTP,DELTA_PPB,DELTA_LOAD_t\n"
        )
        for n in range(params["n_regions"]):
            var1 = params["region_names"][n]
            var2 = x[n]
            var3 = load_w[n]
            var4 = total_load[n]
            var5 = n_wwtp[n]
            var6 = zopt[n]
            var7 = zload[n]
            line = (
                f"{var1},{var2:.4g},{var3:.4g},{var4:.4g},{var5},{var6:.4g},{var7:.4g}"
            )
            outfile.write(line + "\n")
    return True


def main():
    params = getModelParams()

    # Target reduction in [ppb] P = [µg/L] P
    ztarget = array(
        [
            0.0,  #   SCR
            0.0,  #   LSC
            0.0,  #   DR
            0.0,  #   WB
            212 / 318.7,  #   CB 212/318.7
            0.0,  #   EB
        ]
    )
    # Solution in [ton P /year]
    sol = solveModel(ztarget, params)
    saveResults(sol, params, "results/test")
    return True


if __name__ == "__main__":
    main()
