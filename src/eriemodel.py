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


def solveModel(ztarget, params: dict) -> cvxpy.Problem:
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

        print("\nConcentration [ppb/year]\tResponse ∆ Load")
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


def saveResults(model, params: dict, filename: str) -> bool:
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


def solveModelAlt(budget: float, params: dict) -> cvxpy.Problem:
    """
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
