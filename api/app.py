from fastapi import FastAPI, Request, Form, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
import numpy as np
from typing import Optional
import os
import sys

try:
    from eriemodel.basemodels import solveBBModel, solveTBModel
    from eriemodel.erieparams import getFixedParameters, getCalculatedParams
except ModuleNotFoundError:
    sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../eriemodel')))
    from basemodels import solveBBModel, solveTBModel
    from erieparams import getFixedParameters, getCalculatedParams

app = FastAPI(
    title="Lake Erie Phosphorus Abatement Model API",
    version="1.0.0"
)

# Templates
templates = Jinja2Templates(directory="templates")
# Static files
app.mount("/static", StaticFiles(directory="static"), name="static")

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
            ztarget = [target_scr, target_lsc, target_dr, target_wb, target_cb, target_eb]
            
            output = solveTBModel(ztarget, fixed_params, calc_params)
            
            # Check if solution was found
            if not output["status"] or output["status"] in ["infeasible", "unbounded"]:
                return templates.TemplateResponse("results.html", {
                    "request": request,
                    "error": f"No feasible solution found. Status: {output.get('status', 'unknown')}. {output.get('message', '')}"
                })
            
            model_info = {
                "type": "Target-Based",
                "status": output["status"],
                "objective": output["solution"]["obj"]["value"],
                "objective_units": output["solution"]["obj"]["units"]
            }
            
        else:  # budget model
            # Budget-based optimization
            output = solveBBModel(budget, fixed_params, calc_params)
            
            # Check if solution was found
            if not output["status"] or output["status"] in ["infeasible", "unbounded"]:
                return templates.TemplateResponse("results.html", {
                    "request": request,
                    "error": f"No feasible solution found. Status: {output.get('status', 'unknown')}. {output.get('message', '')}"
                })
            
            model_info = {
                "type": "Budget-Based",
                "status": output["status"],
                "objective": output["solution"]["obj"]["value"],
                "objective_units": output["solution"]["obj"]["units"],
                "budget": budget
            }
        
        # Build unified results from output (works for both models)
        volume_array = np.array([params["volume_km3"][region] for region in params["region_names"]])
        z_values = np.array(output["solution"]["z"]["value"])
        zload = z_values * volume_array
        
        results = {
            "agricultural_abatement": dict(zip(params["region_names"], output["solution"]["x"]["value"])),
            "wwtp_abatement": dict(zip(params["region_names"], output["solution"]["wabate"]["value"])),
            "wwtp_investments": dict(zip(params["region_names"], output["solution"]["w"]["value"])),
            "concentration_changes": dict(zip(params["region_names"], output["solution"]["z"]["value"])),
            "load_changes": dict(zip(params["region_names"], zload.tolist())),
            "total_agro_abatement": float(np.sum(output["solution"]["x"]["value"])),
            "total_wwtp_abatement": float(np.sum(output["solution"]["wabate"]["value"])),
            "total_wwtps": int(np.sum(output["solution"]["w"]["value"]))
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
