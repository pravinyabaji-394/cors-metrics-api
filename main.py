import time
import uuid
from typing import Annotated

from fastapi import FastAPI, Request, Response, Header, HTTPException, Query
from fastapi.responses import JSONResponse

app = FastAPI()

# CORS: only this origin is allowed
ALLOWED_ORIGIN = "https://dash-6qebk8.example.com"

# Your course/grader email
YOUR_EMAIL = "24f1001951@ds.study.iitm.ac.in"


# 1) Middleware: add X-Request-ID and X-Process-Time
@app.middleware("http")
async def add_request_headers(request: Request, call_next):
    start_time = time.time()
    request_id = str(uuid.uuid4())

    response: Response = await call_next(request)

    process_time = time.time() - start_time
    response.headers["X-Request-ID"] = request_id
    response.headers["X-Process-Time"] = f"{process_time:.6f}"

    return response


# Helper to apply CORS only for the allowed origin
def apply_cors_if_allowed(origin: str | None, response: Response):
    if origin == ALLOWED_ORIGIN:
        response.headers["Access-Control-Allow-Origin"] = ALLOWED_ORIGIN


# 2) Preflight handler: OPTIONS /stats
@app.options("/stats")
async def stats_preflight(
    request: Request,
    response: Response,
    origin: str | None = Header(default=None, alias="Origin"),
    access_control_request_method: str | None = Header(
        default=None, alias="Access-Control-Request-Method"
    ),
    access_control_request_headers: str | None = Header(
        default=None, alias="Access-Control-Request-Headers"
    ),
):
    # Make sure we have origin (some clients might use lowercase)
    if origin is None:
        origin = request.headers.get("origin")

    # Only allowed origin gets ACAO header
    apply_cors_if_allowed(origin, response)

    if origin == ALLOWED_ORIGIN:
        # Tell browser what is allowed
        response.headers["Access-Control-Allow-Methods"] = "GET, OPTIONS"
        # Allow headers that browser asked for, or all
        response.headers["Access-Control-Allow-Headers"] = (
            access_control_request_headers or "*"
        )

    # IMPORTANT: return the same response object (NOT a new Response())
    return response


# 3) Main endpoint: GET /stats?values=1,2,3
@app.get("/stats")
async def get_stats(
    request: Request,
    response: Response,
    values: Annotated[str, Query(..., description="Comma-separated integers, e.g. 1,2,3")],
):
    # Apply CORS header conditionally
    origin = request.headers.get("origin")
    apply_cors_if_allowed(origin, response)

    # Validate presence of values
    if not values:
        raise HTTPException(status_code=400, detail="values query parameter is required")

    # Parse comma-separated integers
    try:
        str_numbers = [v.strip() for v in values.split(",") if v.strip() != ""]
        nums = [int(v) for v in str_numbers]
    except ValueError:
        raise HTTPException(status_code=400, detail="values must be comma-separated integers")

    if len(nums) == 0:
        raise HTTPException(status_code=400, detail="at least one integer is required")

    # Compute statistics
    n = len(nums)
    s = sum(nums)
    mn = min(nums)
    mx = max(nums)
    mean = s / n

    # Build and return JSON response
    result = {
        "email": YOUR_EMAIL,
        "count": n,
        "sum": s,
        "min": mn,
        "max": mx,
        "mean": round(mean, 4),  # accurate within ±0.01
    }

    return JSONResponse(content=result)