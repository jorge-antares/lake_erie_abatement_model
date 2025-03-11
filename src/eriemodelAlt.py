#! /Users/ja4garci/opt/myenvs/cvx_env/bin/python
"""
================================================
        Lake Erie Abatement Optimization
================================================

Main optimization model.

DECISION VARIABLES
    x - Agro abatement by region (metric tonnes per year)
    w - Vector of binary variuables (unitless)

MODEL
    min x^T A x + b^T w - c^T zpw
s.t.
    S x + W w - z >= z_target
    x, z >= 0
    w binary
    W = (S*L*F)
"""

import cvxpy
from numpy import array


def solveModelAlt(budget: float, params: dict) -> cvxpy.Problem:
    # DECISION VARIABLES
    x = cvxpy.Variable(shape=params["n_regions"], name="x")
    w = cvxpy.Variable(shape=params["n_wwtps"], integer=True, name="w")

    # SOLVER
    weight = array([1, 1, 1, 100, 100, 1])
    model = cvxpy.Problem(
        cvxpy.Maximize(weight.T @ params["S"] @ x + weight.T @ params["W"] @ w),
        [
            cvxpy.quad_form(x, params["A"]) + params["b"].T @ w <= budget,
            w <= 1,
            w >= 0,
            x >= 0,
        ],
    )
    model.solve(solver="SCIP", verbose=False)
    output = {}
    if model.status not in ["infeasible", "unbounded"]:
        output["obj"] = model.value
        output["x"] = x.value
        output["z"] = params["S"] @ x.value + params["W"] @ w.value
        output["w"] = params["L"] @ w.value
        output["wabate"] = params["L"] @ params["F"] @ w.value
        output["allw"] = w.value

        print(f"\nObjective function:\t {model.value:.4g}")

        print("\nLoad reduction [t/year]:")
        for reg, entry in zip(params["region_names"], x.value):
            print(reg, f"\t{round(entry,2)}")

        print("\nLoad reduction WWTPs [t/year]:")
        for reg, entry in zip(params["region_names"], output["wabate"]):
            print(reg, f"\t{round(entry,2)}")

        print("\nConcentration reduction [t/year]:")
        for reg, entry in zip(params["region_names"], output["z"]):
            print(reg, f"\t{round(entry,4)}")
        print("\nWWTPs that need investment:")

        for n, i in enumerate(params["region_names"]):
            print(i, "\t", output["w"][n])
    else:
        print("No solution found... :(")
    return output


if __name__ == "__main__":
    pass
