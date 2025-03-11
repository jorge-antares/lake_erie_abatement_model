#Lake Erie Abatement Optimization#

We present an optimization model for the Canadian side of Lake Erie (LE) that determines the required abatement level of total phosphorus (TP), targeting agricultural activities and additional investments in end-of-pipe technologies in wastewater treatment plants across the Canadian LE watersheds, such that a target reduction in P concentration is achieved at the lowest cost.

The hydrological model used in this study considers the interdependence among six regions: St. Claire River and Lake, the Detroit River, and the Western, Central and Eastern Basins of LE.

**Model**
The optimization model is:

min_(x,w) x^T A x + b^T w

subject to:
- Sx + Ww ≥ z_Target
- x ≥ 0
- w_i ∈ {0,1} ∀i

and its parameters are:

- A: diagonal matrix of size R × R containing the quadratic terms of the cost function in equation 4 in [CAD year/t^2].
- S: the system matrix of equation 1 in [10^-15 year/L].
- z_Target: the target concentration reduction in [ppb].
- b_i = m + (1/T)∑_(τ=0)^T C_τ(1+i)^(-τ): the annual maintenance and annual prorated net present value of the investment of installing the filter on WWTP i for a period of one year considering a filter lifetime of T years in [CAD/year].
- L: an indicator matrix of size R × I whose elements l_(r,i)=1 if WWTP i is located in region r and zero otherwise [unitless].
- F: a diagonal matrix of size I × I whose diagonal elements f_(i,i) are the TP decrease on the discharge of WWTP i in [t/year].

