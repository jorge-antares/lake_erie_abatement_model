"""
================================================
            Lake Erie Abatement Model
================================================

October 2025

This script contains the core model functions of
the Lake Erie abatement optimization model.

DECISION VARIABLES
    x - Agro abatement by region (metric tonnes per year)
    v - Binary vector where v[i] = 1 if WWTP i is upgraded,
        0 otherwise (unitless)

    
TARGET-BASED MODEL
    min x^T A x + b^T v
s.t.
    S x + W v >= z_target
    x <= c
    x >= 0
    v binary
    W = (S*L*F)

    
BUDGET-BASED MODEL
    max c^T ( S x + W v )
s.t.
    x^T A x + b^T v <= budget
    x <= c
    x >= 0
    v binary
    W = (S*L*F)

================================================
"""

import cvxpy
import time
import warnings
from numpy import array

warnings.filterwarnings("ignore", category=UserWarning)

def solveTBModel(ztarget:list, fixed_params: dict, calculated_params: dict) -> dict:
    """
        DECISION VARIABLES
        x - Agro abatement by region (metric tonnes per year)
        w - Vector of binary variuables (unitless)

    MODEL
        min x^T A x + b^T v
    s.t.
        S x + W v >= z_target
        x <= c
        x >= 0
        v binary
        W = (S*L*F)

    """
    params = {**fixed_params, **calculated_params}
    ztarget = array(ztarget)

    # DECISION VARIABLES
    x = cvxpy.Variable(shape=params["n_regions"], name="x")
    v = cvxpy.Variable(shape=params["n_wwtps"], integer=True, name="v")

    # SOLVER
    model = cvxpy.Problem(
        cvxpy.Minimize(cvxpy.quad_form(x, params["A"]) + params["b"].T @ v),
        [
            params["S"] @ x + params["W"] @ v >= ztarget,
            v <= params["u_w"],
            v >= 0,
            x <= params["c"],
            x >= 0,
        ],
    )
    
    model.solve(solver="SCIP", verbose=False)
    output = getResponseTemplate()
    output["status"] = model.status

    if model.status not in ["infeasible", "unbounded"]:
        output["solution"]["solve_time"]["value"] = model._solve_time
        output["solution"]["obj"]["value"] = model.value
        output["solution"]["x"]["value"] = x.value.tolist()
        output["solution"]["v"]["value"] = [ int(entry) for entry in v.value.round()]
        output["solution"]["v_regional"]["value"] = [ int(entry) for entry in (params["L"] @ v.value).round()]
        output["solution"]["z"]["value"] = (params["S"] @ x.value + params["W"] @ v.value).tolist()
        output["solution"]["wwtp_abate"]["value"] = (params["L"] @ params["F"] @ v.value).round(4).tolist()
        output["solution"]["cost"]["value"] = model.value
        output["message"] = "Solution found."
        print(f"SUCCESS   TBM\tObjFun: {model.value:.4g} |", time.strftime("%Y-%m-%d %H:%M:%S"))
    else:
        output["message"] = "No solution found."
        print("FAIL   TBM", time.strftime("%Y-%m-%d %H:%M:%S"))
    return output



def solveBCModel(budget: float, fixed_params: dict, calculated_params: dict) -> dict:
    """
        DECISION VARIABLES
        x - Agro abatement by region (metric tonnes per year)
        v - Vector of binary variuables (unitless)

    MODEL
        max c^T ( S x + W v )
    s.t.
        x^T A x + b^T v <= budget
        x <= c
        x >= 0
        v binary
        W = (S*L*F)
    """
    params = {**fixed_params, **calculated_params}

    # DECISION VARIABLES
    x = cvxpy.Variable(shape=params["n_regions"], name="x")
    v = cvxpy.Variable(shape=params["n_wwtps"], integer=True, name="v")

    # SOLVER
    weight = array([1, 8, 1, 60, 600, 300])
    weight = weight / weight.sum()
    model = cvxpy.Problem(
        cvxpy.Maximize(weight.T @ params["S"] @ x + weight.T @ params["W"] @ v),
        [
            cvxpy.quad_form(x, params["A"]) + params["b"].T @ v <= budget,
            v <= params["u_w"],
            v >= 0,
            x <= params["c"],
            x >= 0,
        ],
    )
    model.solve(solver="SCIP", verbose=False)
    output = getResponseTemplate()
    output["status"] = model.status
    output["model_type"] = "Budget-Constrained"

    if model.status not in ["infeasible", "unbounded"]:
        output["solution"]["solve_time"]["value"] = model._solve_time
        output["solution"]["obj"]["value"] = model.value
        output["solution"]["obj"]["units"] = "ppb (weighted average)"
        output["solution"]["x"]["value"] = x.value.tolist()
        output["solution"]["v"]["value"] = [ int(entry) for entry in v.value.round()]
        output["solution"]["v_regional"]["value"] = [ int(entry) for entry in (params["L"] @ v.value).round()]
        output["solution"]["z"]["value"] = (params["S"] @ x.value + params["W"] @ v.value).tolist()
        output["solution"]["wwtp_abate"]["value"] = (params["L"] @ params["F"] @ v.value).round(4).tolist()
        output["solution"]["cost"]["value"] = (x.T @ params["A"] @ x + params["b"].T @ v).value
        output["message"] = "Solution found."
        print(f"SUCCESS   BCM\tObjFun: {model.value:.4g} |", time.strftime("%Y-%m-%d %H:%M:%S"))
    else:
        output["message"] = "No solution found."
        print("FAIL     BCM", time.strftime("%Y-%m-%d %H:%M:%S"))
    return output



def getResponseTemplate() -> dict:
    return {
        "status": "",
        "model_type": "Target-Based",
        "message": "No feasible solution found.",
        "solution": {
            "solve_time": {"units": "sec", "value": 0.0},
            "obj": {"units": "million CAD/year", "value": 0.0},
            "x": {"units": "t/year", "value": []},
            "v": {"units": "unitless", "value": []},
            "v_regional": {"units": "plants", "value": []},
            "z": {"units": "ppb", "value": []},
            "wwtp_abate": {"units": "t/year", "value": []},
            "cost": {"units": "million CAD/year", "value": 0.0},
        }
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
