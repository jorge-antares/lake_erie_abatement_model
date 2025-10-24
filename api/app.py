from fastapi import FastAPI, Request, Form, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
import numpy as np
from typing import Optional
import sys
import os

# Add src directory to Python path
current_dir = os.path.dirname(os.path.abspath(__file__))
src_dir = os.path.join(current_dir, 'src')
sys.path.insert(0, src_dir)

try:
    from basemodels import solveModel, solveModelAlt
    from erieparams import getModelParams
except ImportError as e:
    print(f"Import error: {e}")
    # Fallback for development
    import importlib.util
    
    basemodels_path = os.path.join(src_dir, 'basemodels.py')
    spec = importlib.util.spec_from_file_location("basemodels", basemodels_path)
    basemodels = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(basemodels)
    solveModel = basemodels.solveModel
    solveModelAlt = basemodels.solveModelAlt
    
    erieparams_path = os.path.join(src_dir, 'erieparams.py')
    spec = importlib.util.spec_from_file_location("erieparams", erieparams_path)
    erieparams = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(erieparams)
    getModelParams = erieparams.getModelParams

app = FastAPI(title="Lake Erie Abatement Optimization", version="1.0.0")

# Setup templates
templates = Jinja2Templates(directory="templates")

@app.get("/health")
async def health_check():
    """Health check endpoint for monitoring"""
    return {"status": "healthy", "service": "lake_erie_optimization"}

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
    agro_cost_factor: float = Form(0.004),
):
    """Run optimization and display results"""
    try:
        # Get base model parameters
        params = getModelParams()
        
        # Update parameters with user inputs
        # Update filter efficiency
        P_ppm = 2.737
        factor = 1e-3
        F = P_ppm * factor * filter_efficiency * np.diag(params["E"].reshape(-1))
        params["F"] = F
        params["W"] = params["S"] @ params["L"] @ F
        
        # Update maintenance costs
        params["b"] = maintenance_cost * params["E"].reshape(-1)
        
        # Update agriculture costs
        region_areas = [7.20, 0.61, 15.5, 9.24, 2.23, 0.77]  # From erieparams.py
        a = np.array([agro_cost_factor * area for area in region_areas])
        params["A"] = np.diag(a)
        
        if model_type == "target":
            # Target-based optimization
            ztarget = np.array([target_scr, target_lsc, target_dr, target_wb, target_cb, target_eb])
            
            model = solveModel(ztarget, params)
            
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
            zload = [i * j for i, j in zip(zopt, params["volume_km3"].values())]
            
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
            output = solveModelAlt(budget, params)
            
            if not output or "obj" not in output:
                return templates.TemplateResponse("results.html", {
                    "request": request,
                    "error": "No feasible solution found for the given budget constraint."
                })
            
            results = {
                "agricultural_abatement": dict(zip(params["region_names"], output["x"])),
                "wwtp_abatement": dict(zip(params["region_names"], output["wabate"])),
                "wwtp_investments": dict(zip(params["region_names"], output["w"].astype(int))),
                "concentration_changes": dict(zip(params["region_names"], output["z"])),
                "load_changes": dict(zip(params["region_names"], output["z"] * np.array(list(params["volume_km3"].values())))),
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
        return templates.TemplateResponse("results.html", {
            "request": request,
            "error": f"An error occurred during optimization: {str(e)}"
        })

@app.get("/model-docs", response_class=HTMLResponse)
async def model_docs(request: Request):
    """Display mathematical model documentation"""
    return templates.TemplateResponse("model_docs.html", {"request": request})

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)