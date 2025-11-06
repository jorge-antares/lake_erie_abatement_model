"""
================================================
        Lake Erie Abatement Optimization
================================================

Testing script.

"""

try:
    from erieparams import getFixedParameters, getCalculatedParams
    from basemodels import solveTBModel, solveBBModel
except ImportError:
    from eriemodel.erieparams import getFixedParameters, getCalculatedParams
    from eriemodel.basemodels import solveTBModel, solveBBModel


fixed_params = getFixedParameters()
calculated_params = getCalculatedParams(fixed_params)


def test_model():
    
    # Target reduction in [ppb] P = [µg/L] P
    ztarget = [
            0.5,  #   SCR
            0.5,  #   LSC
            0.5,  #   DR
            0.5,  #   WB
            0.5,  #   CB 212/318.7
            0.5,  #   EB
        ]
    sol = solveTBModel(ztarget, fixed_params, calculated_params)
    return True


def test_modelAlt():
    # Budget in million CAD
    budget = 500
    sol = solveBBModel(budget, fixed_params, calculated_params)
    #print(json.dumps(sol, indent=4))
    return True


if __name__ == "__main__":
    print("*" * 40)
    print("TEST TARGET_BASED MODEL")
    print("*" * 40)
    test_model()
    print("\n\n")
    print("+" * 40)
    print("TEST BUDGET-BASED MODEL")
    print("+" * 40)
    test_modelAlt()
