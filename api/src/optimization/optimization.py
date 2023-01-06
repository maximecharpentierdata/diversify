from fastapi import APIRouter, Cookie, HTTPException
from mongo.allocation import get_allocation_collection
from mongo.assets import get_assets_collection
from mongo.constraints import get_constraints_collection
from optimization.utils import format_result, run_optimization, score_function

optimization_router = APIRouter(prefix="/optimization", tags=["optimization"])


@optimization_router.get("/")
def route_optimize(
    total_amount: int, session_id: str = Cookie()
) -> dict | HTTPException:
    assets = list(get_assets_collection(session_id).find())
    allocation = list(get_allocation_collection(session_id).find())
    constraints = list(get_constraints_collection(session_id).find())

    result = run_optimization(
        assets=assets,
        allocation=allocation,
        constraints=constraints,
        total_amount=total_amount,
    )

    if not result.success:
        return HTTPException(status_code=500)

    transfer = result.x.astype(int).tolist()

    formatted_results = format_result(transfer, assets, allocation)

    return {
        "results": formatted_results,
        "score": score_function(transfer, assets, allocation),
    }
