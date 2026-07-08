import time
import uuid

from fastapi import FastAPI, Request, Query
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# Allowed CORS Origin
ALLOWED_ORIGIN = "https://dash-6qebk8.example.com"

# Your IITM email
YOUR_EMAIL = "24f1001951@ds.study.iitm.ac.in"

# ----------------------------
# CORS Middleware
# ----------------------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=[ALLOWED_ORIGIN],
    allow_credentials=False,
    allow_methods=["GET", "OPTIONS"],
    allow_headers=["*"],
)

# ----------------------------
# Middleware for Request ID and Process Time
# ----------------------------
@app.middleware("http")
async def add_custom_headers(request: Request, call_next):
    start_time = time.perf_counter()

    response = await call_next(request)

    process_time = time.perf_counter() - start_time

    response.headers["X-Request-ID"] = str(uuid.uuid4())
    response.headers["X-Process-Time"] = f"{process_time:.6f}"

    return response


# ----------------------------
# GET /stats
# Example:
# /stats?values=1,2,3,4
# ----------------------------
@app.get("/stats")
async def get_stats(
    values: str = Query(..., description="Comma-separated integers")
):
    try:
        nums = [int(x.strip()) for x in values.split(",") if x.strip() != ""]
    except ValueError:
        return {
            "error": "values must contain only integers"
        }

    if len(nums) == 0:
        return {
            "error": "No integers supplied"
        }

    total = sum(nums)
    count = len(nums)

    return {
        "email": YOUR_EMAIL,
        "count": count,
        "sum": total,
        "min": min(nums),
        "max": max(nums),
        "mean": total / count
    }