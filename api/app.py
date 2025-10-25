from fastapi import FastAPI, Request, Form, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
import numpy as np
from typing import Optional


from eriemodel.basemodels import solveBBModel, solveTBModel
from eriemodel.erieparams import getFixedParameters, getCalculatedParams

app = FastAPI(
    title="Lake Erie Phosphorus Abatement Model API",
    version="1.0.0"
)

# Setup templates
templates = Jinja2Templates(directory="templates")

# Optional: Mount static files if you have CSS/JS/images
# app.mount("/static", StaticFiles(directory=str(settings.STATIC_DIR)), name="static")

@app.get("/health")
async def health_check():
    """Health check endpoint for monitoring"""
    return {
        "status": "healthy",
        "service": "lake_erie_optimization",
        "version": "1.0.0"
    }


@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    """Home page with model overview"""
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/optimize", response_class=HTMLResponse)
async def optimize_form(request: Request):
    """Display optimization parameters form"""
    return templates.TemplateResponse("optimize.html", {"request": request})

@app.post("/run-optimization")
async def run_optimization(
    request: Request,
    model_type: str = Form(...),
    # Target model parameters
    target_scr: Optional[float] = Form(0.0),
    target_lsc: Optional[float] = Form(0.0),
    target_dr: Optional[float] = Form(0.0),
    target_wb: Optional[float] = Form(0.0),
    target_cb: Optional[float] = Form(0.665),
    target_eb: Optional[float] = Form(0.0),
    # Budget model parameters
    budget: Optional[float] = Form(500),
    # Advanced parameters
    filter_efficiency: float = Form(0.4),
    maintenance_cost: float = Form(0.0001),
    agro_cost_scr: float = Form(0.0288),
    agro_cost_lsc: float = Form(0.00244),
    agro_cost_dr: float = Form(0.062),
    agro_cost_wb: float = Form(0.0369),
    agro_cost_cb: float = Form(0.00892),
    agro_cost_eb: float = Form(0.00308),
):
    """Run optimization and display results"""
    try:
        # Get fixed parameters
        fixed_params = getFixedParameters()
        
        # Prepare agriculture costs
        agro_costs = [
            agro_cost_scr,
            agro_cost_lsc,
            agro_cost_dr,
            agro_cost_wb,
            agro_cost_cb,
            agro_cost_eb
        ]
        
        # Get calculated parameters with user inputs
        calc_params = getCalculatedParams(
            fixed_params=fixed_params,
            filter_eff=filter_efficiency,
            maintenance_cost=maintenance_cost,
            agro_abatecost=agro_costs
        )
        
        # Combine parameters
        params = {**fixed_params, **calc_params}
        
        if model_type == "target":
            # Target-based optimization
            ztarget = np.array([target_scr, target_lsc, target_dr, target_wb, target_cb, target_eb])
            
            model = solveTBModel(ztarget, params)
            
            if model.status in ["infeasible", "unbounded"]:
                return templates.TemplateResponse("results.html", {
                    "request": request,
                    "error": f"No feasible solution found. Model status: {model.status}"
                })
            
            # Extract results
            x = model.variables[0].value  # Agricultural abatement
            w = model.variables[1].value  # WWTP binary variables
            
            # Calculate derived results
            load_w = params["L"] @ params["F"] @ w
            n_wwtp = params["L"] @ w
            zopt = params["S"] @ x + params["W"] @ w
            volume_array = np.array([params["volume_km3"][region] for region in params["region_names"]])
            zload = zopt * volume_array
            
            results = {
                "agricultural_abatement": dict(zip(params["region_names"], x)),
                "wwtp_abatement": dict(zip(params["region_names"], load_w)),
                "wwtp_investments": dict(zip(params["region_names"], n_wwtp.astype(int))),
                "concentration_changes": dict(zip(params["region_names"], zopt)),
                "load_changes": dict(zip(params["region_names"], zload)),
                "total_agro_abatement": float(np.sum(x)),
                "total_wwtp_abatement": float(np.sum(load_w)),
                "total_wwtps": int(np.sum(n_wwtp))
            }
            
            model_info = {
                "type": "Target-Based",
                "status": model.status,
                "objective": float(model.value)
            }
            
        else:  # budget model
            # Budget-based optimization
            output = solveBBModel(budget, params)
            
            if not output or "obj" not in output:
                return templates.TemplateResponse("results.html", {
                    "request": request,
                    "error": "No feasible solution found for the given budget constraint."
                })
            
            volume_array = np.array([params["volume_km3"][region] for region in params["region_names"]])
            
            results = {
                "agricultural_abatement": dict(zip(params["region_names"], output["x"])),
                "wwtp_abatement": dict(zip(params["region_names"], output["wabate"])),
                "wwtp_investments": dict(zip(params["region_names"], output["w"].astype(int))),
                "concentration_changes": dict(zip(params["region_names"], output["z"])),
                "load_changes": dict(zip(params["region_names"], output["z"] * volume_array)),
                "total_agro_abatement": float(np.sum(output["x"])),
                "total_wwtp_abatement": float(np.sum(output["wabate"])),
                "total_wwtps": int(np.sum(output["w"]))
            }
            
            model_info = {
                "type": "Budget-Based",
                "status": "optimal",
                "objective": float(output["obj"]),
                "budget": budget
            }
        
        return templates.TemplateResponse("results.html", {
            "request": request,
            "results": results,
            "model_info": model_info
        })
        
    except Exception as e:
        import traceback
        error_detail = traceback.format_exc()
        return templates.TemplateResponse("results.html", {
            "request": request,
            "error": f"An error occurred during optimization: {str(e)}",
            "error_detail": error_detail
        })

@app.get("/model-docs", response_class=HTMLResponse)
async def model_docs(request: Request):
    """Display mathematical model documentation"""
    return templates.TemplateResponse("model_docs.html", {"request": request})

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000
    )
