"""
================================================
        Lake Erie Abatement Optimization
================================================

Code to run models.

"""

from numpy import array



def runModel1():
    """Change these parameters to run Model 1"""

    # PARAMETERS
    params = getModelParams()

    # TARGET REDUCTION [ppb] P = [µg/L] P
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

    # SOLUTION [ton P /year]
    sol = solveModel(ztarget, params)
    # saveResults(sol, params, "results/test")
    return True


def runModel2():
    """Change these parameters to run Model 2"""
    # PARAMETERS
    params = getModelParams()

    # BUDGET [million CAD]
    budget = 500

    # SOLUTION [ton P /year]
    sol = solveModelAlt(budget, params)
    return True


if __name__ == "__main__":
    runModel1()
    runModel2()
