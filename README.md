# Lake Erie Abatement Optimization #

We present an optimization model for the Canadian side of Lake Erie (LE) that determines the required abatement of total phosphorus (TP) on agricultural activities or end-of-pipe investments in wastewater treatment plants across the Canadian LE watersheds, such that a target reduction in P concentration is achieved at the lowest cost.

The hydrological model used in this study considers the interdependence among six regions: St. Claire River and Lake, the Detroit River, and the Western, Central and Eastern Basins of LE.

# Model I
The optimization model is:

$$\min_{x,w}\quad x^T A x + b^T w$$

subject to:

$$Sx + Ww ≥ z_{\rm Target}$$

$$x \geq 0$$

$$w_i \in \{0,1\}\quad \forall\ i$$

and its parameters are:

- $A$: diagonal matrix of size $R \times R$ containing the quadratic terms of the cost function in equation 4 in [CAD year/$t^2$].
- $S$: the system matrix of equation 1 in [$10^{-15}$ year/L].
- $z_{\rm Target}$: the target concentration reduction in [ppb].
- $b_i$: the annual maintenance and annual prorated net present value of the investment of installing the filter on WWTP i for a period of one year considering a filter lifetime of T years in [CAD/year].
- $L$: an indicator matrix of size $R \times I$ whose elements $l_{r,i}=1$ if WWTP i is located in region r and zero otherwise [unitless].
- $F$: a diagonal matrix of size $I \times I$ whose diagonal elements $f_{i,i}$ are the TP decrease on the discharge of WWTP i in [t/year].

# Model II (Alt)
This model has the same variables and parameters as Model I but has an additional parameter, $\alpha$, which expresses the relative weight or importance of concentration reductions on each region of the model. The objective function of Model I is introduced here as a constraint, and the phosphorus concentration constraint of Model I is introduced as the objective function.

$$\max_{x,w}\quad \alpha^{\rm T} \big( Sx + Ww \big)$$

subject to:

$$x^{T} A x + b^{T} w  \leq \text{budget}$$

$$x \geq 0$$

$$w_{i} \in \{0,1\}\quad \forall i.$$

