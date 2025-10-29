"""
================================================
        Lake Erie Abatement Optimization
================================================

Code to run models.

"""

from numpy import array
from erieparams import getFixedParameters, getCalculatedParams
from basemodels import solveTBModel, solveBBModel, saveResults


def runModel1():
    """Change these parameters to run Model 1"""

    # Get parameters
    fixed_params = getFixedParameters()
    calculated_params = getCalculatedParams(fixed_params)

    # TARGET REDUCTION [ppb] P = [µg/L] P
    ztarget = [
        0.0,  #   SCR
        0.0,  #   LSC
        0.0,  #   DR
        0.0,  #   WB
        212 / 318.7,  #   CB 212/318.7
        0.0,  #   EB
    ]

    # SOLUTION [ton P /year]
    sol = solveTBModel(ztarget, fixed_params, calculated_params)
    
    if sol["status"] and sol["status"] not in ["infeasible", "unbounded"]:
        print(f"Solution found! Objective: {sol['solution']['obj']['value']} {sol['solution']['obj']['units']}")
        print(f"Status: {sol['status']}")
        print(f"Message: {sol['message']}")
    else:
        print(f"No solution found. Status: {sol.get('status', 'unknown')}")
    
    return sol


def runModel2():
    """Change these parameters to run Model 2"""
    
    # Get parameters
    fixed_params = getFixedParameters()
    calculated_params = getCalculatedParams(fixed_params)

    # BUDGET [million CAD]
    budget = 500

    # SOLUTION [ton P /year]
    sol = solveBBModel(budget, fixed_params, calculated_params)
    
    if sol["status"] and sol["status"] not in ["infeasible", "unbounded"]:
        print(f"Solution found! Objective: {sol['solution']['obj']['value']} {sol['solution']['obj']['units']}")
        print(f"Status: {sol['status']}")
        print(f"Message: {sol['message']}")
    else:
        print(f"No solution found. Status: {sol.get('status', 'unknown')}")
    
    return sol


if __name__ == "__main__":
    print("=" * 50)
    print("Running Target-Based Model")
    print("=" * 50)
    runModel1()
    print("\n\n")
    print("=" * 50)
    print("Running Budget-Based Model")
    print("=" * 50)
    runModel2()
