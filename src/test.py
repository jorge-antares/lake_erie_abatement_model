"""
================================================
        Lake Erie Abatement Optimization
================================================

Testing script.

"""

from numpy import array
from funcs import getModelParams
from runmodel import solveModel
from runmodelAlt import solveModelAlt


def test_model():
    params = getModelParams()
    # Target reduction in [ppb] P = [µg/L] P
    ztarget = array(
        [
            0.5,  #   SCR
            0.5,  #   LSC
            0.5,  #   DR
            0.5,  #   WB
            0.5,  #   CB 212/318.7
            0.5,  #   EB
        ]
    )
    # Solution in [ton P /year]
    sol = solveModel(ztarget, params)
    return True


def test_modelAlt():
    params = getModelParams()

    # Budget in million CAD
    budget = 500

    # Solution in [ton P /year]
    sol = solveModelAlt(budget, params)
    return True


if __name__ == "__main__":
    print("*" * 40)
    print("TEST MODEL 1")
    print("*" * 40)
    test_model()
    print("\n\n\n")
    print("+" * 40)
    print("TEST MODEL 2")
    print("+" * 40)
    test_modelAlt()
