import logging
from typing import Annotated

from fastapi import APIRouter, Depends, status
from fastapi.exceptions import HTTPException
from pydantic import Field

from service.config import config
from service.dependencies import get_storage
from service.dtos import AddBatchRequest, AddBatchResponse, StatsResponse
from service.statistics import Statistic
from service.storage import StatsStorage

logger = logging.getLogger(__name__)
router = APIRouter(prefix="", tags=["statistics"])


@router.post(
    "/add_batch/",
    name="Add batch",
    description="Allows the bulk addition of consecutive "
    "trading data points for a specific symbol.",
    responses={
        status.HTTP_200_OK: {
            "model": AddBatchResponse,
        },
        status.HTTP_422_UNPROCESSABLE_ENTITY: {
            "model": dict,
            "description": "Unprocessable content in the request",
        },
    },
)
def add_batch_controller(
    request: AddBatchRequest,
    storage: Annotated[StatsStorage, Depends(get_storage)],
) -> AddBatchResponse:
    try:
        storage.add(request.values)
        return AddBatchResponse(symbol=request.symbol, message="OK")
    except HTTPException:
        raise
    except Exception as e:
        logger.exception("Unknown error adding batch")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error: {e}",
        ) from e


@router.get(
    "/stats/",
    name="Get stats",
    description="Rapid statistical analyses of recent "
    "trading data for specified symbol.",
    responses={
        status.HTTP_200_OK: {
            "model": StatsResponse,
        },
        status.HTTP_404_NOT_FOUND: {
            "model": dict,
            "description": "No data points found for the symbol",
        },
        status.HTTP_422_UNPROCESSABLE_ENTITY: {
            "model": dict,
            "description": "Unprocessable content in the request",
        },
    },
)
def get_stats_controller(
    symbol: str,
    k: Annotated[
        int,
        Field(gt=0, le=config.MAX_K),
    ],
) -> StatsResponse:
    try:
        storage = get_storage(symbol)
        stats: Statistic | None = storage.get(10**k)
        if stats is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No data points found for the symbol",
            )
        return StatsResponse.create(symbol=symbol, k=k, stats=stats)
    except HTTPException:
        raise
    except Exception as e:
        logger.exception("Unknown error retrieving stats")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error: {e}",
        ) from e
