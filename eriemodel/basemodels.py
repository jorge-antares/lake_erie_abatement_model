"""
================================================
            Lake Erie Abatement Model
================================================

October 2025

This script contains the core model functions of
the Lake Erie abatement optimization model.

DECISION VARIABLES
    x - Agro abatement by region (metric tonnes per year)
    w - Binary vector where w[i] = 1 if WWTP i is upgraded,
        0 otherwise (unitless)

    
TARGET-BASED MODEL
    min x^T A x + b^T w
s.t.
    S x + W w >= z_target
    x >= 0
    w binary
    W = (S*L*F)

    
BUDGET-BASED MODEL
    max c^T ( S x + W w )
s.t.
    x^T A x + b^T w <= budget
    x >= 0
    w binary
    W = (S*L*F)

================================================
"""

import cvxpy
import time
from numpy import array


def solveTBModel(ztarget:list, fixed_params: dict, calculated_params: dict) -> dict:
    """
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
    params = {**fixed_params, **calculated_params}
    ztarget = array(ztarget)

    # DECISION VARIABLES
    x = cvxpy.Variable(shape=params["n_regions"], name="x")
    w = cvxpy.Variable(shape=params["n_wwtps"], integer=True, name="w")

    # SOLVER
    model = cvxpy.Problem(
        cvxpy.Minimize(cvxpy.quad_form(x, params["A"]) + params["b"].T @ w),
        [
            params["S"] @ x + params["W"] @ w >= ztarget,
            w <= params["u_w"],
            w >= 0,
            x >= 0,
        ],
    )
    model.solve(solver="SCIP", verbose=False)
    output = getResponseTemplate()

    if model.status not in ["infeasible", "unbounded"]:
        output["status"] = model.status
        output["solution"]["solve_time"]["value"] = model._solve_time
        output["solution"]["obj"]["value"] = model.value
        output["solution"]["x"]["value"] = x.value.tolist()
        output["solution"]["z"]["value"] = (params["S"] @ x.value).tolist()
        output["solution"]["w"]["value"] = [ int(entry) for entry in (params["L"] @ w.value).round()]
        output["solution"]["wabate"]["value"] = (params["L"] @ params["F"] @ w.value).round(4).tolist()
        output["solution"]["allw"]["value"] =  [int(entry) for entry in w.value.round()]
        output["message"] = "Solution found."
        print(f"SUCCESS   TBM\tObjFun: {model.value:.4g} | Solve time: {model._solve_time:4g} sec | ", time.strftime("%Y-%m-%d %H:%M:%S"))
    else:
        print("FAIL   TBM", time.strftime("%Y-%m-%d %H:%M:%S"))
    return output



def solveBBModel(budget: float, fixed_params: dict, calculated_params: dict) -> dict:
    """
        DECISION VARIABLES
        x - Agro abatement by region (metric tonnes per year)
        w - Vector of binary variuables (unitless)

    MODEL
        max c^T ( S x + W w )
    s.t.
        x^T A x + b^T w <= budget
        x >= 0
        w binary
        W = (S*L*F)
    """
    params = {**fixed_params, **calculated_params}

    # DECISION VARIABLES
    x = cvxpy.Variable(shape=params["n_regions"], name="x")
    w = cvxpy.Variable(shape=params["n_wwtps"], integer=True, name="w")

    # SOLVER
    weight = array([1, 1, 1, 100, 50, 100])
    weight = weight / weight.sum()
    model = cvxpy.Problem(
        cvxpy.Maximize(weight.T @ params["S"] @ x + weight.T @ params["W"] @ w),
        [
            cvxpy.quad_form(x, params["A"]) + params["b"].T @ w <= budget,
            w <= params["u_w"],
            w >= 0,
            x >= 0,
        ],
    )
    model.solve(solver="SCIP", verbose=False)
    output = getResponseTemplate()

    if model.status not in ["infeasible", "unbounded"]:
        output["status"] = model.status
        output["solution"]["solve_time"]["value"] = model._solve_time
        output["solution"]["obj"]["value"] = model.value
        output["solution"]["obj"]["units"] = "ppb (weighted average)"
        output["solution"]["x"]["value"] = x.value.tolist()
        output["solution"]["z"]["value"] = (params["S"] @ x.value).tolist()
        output["solution"]["w"]["value"] = [ int(entry) for entry in (params["L"] @ w.value).round()]
        output["solution"]["wabate"]["value"] = (params["L"] @ params["F"] @ w.value).round(4).tolist()
        output["solution"]["allw"]["value"] =  [int(entry) for entry in w.value.round()]
        output["message"] = "Solution found."
        print(f"SUCCESS   BBM\tObjFun: {model.value:.4g} |", time.strftime("%Y-%m-%d %H:%M:%S"))
    else:
        output["status"] = model.status
        print("FAIL   BBM", time.strftime("%Y-%m-%d %H:%M:%S"))
    return output



def getResponseTemplate() -> dict:
    return {
        "status": False,
        "solution": {
            "solve_time": {"units": "sec", "value": 0.0},
            "obj": {"units": "million CAD/year", "value": 0.0},
            "x": {"units": "t/year", "value": []},
            "z": {"units": "ppb", "value": []},
            "w": {"units": "plants", "value": []},
            "wabate": {"units": "t/year", "value": []},
            "allw": {"units": "unitless", "value": []}
        },
        "message": "No feasible solution found."
    }



def saveResults(model: cvxpy.Problem, params: dict, filename: str) -> bool:
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

if __name__ == "__main__":
    pass
