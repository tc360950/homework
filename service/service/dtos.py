from typing import Annotated

from pydantic import Field

from service.config import config
from service.core import BaseDTO
from service.statistics import Statistic


class AddBatchRequest(BaseDTO):
    symbol: str
    values: Annotated[
        list[float],
        Field(min_length=0, max_length=config.MAX_BATCH_SIZE),
    ]


class AddBatchResponse(BaseDTO):
    symbol: str
    message: str


class StatsResponse(BaseDTO):
    class Statistics(BaseDTO):
        min: float
        max: float
        last: float
        avg: float
        var: float

    symbol: str
    k: Annotated[int, Field(gt=0, le=config.MAX_K)]
    statistics: Statistics

    @classmethod
    def create(cls, symbol: str, k: int, stats: Statistic) -> "StatsResponse":
        return cls(
            symbol=symbol,
            k=k,
            statistics=cls.Statistics(
                min=stats.min,
                max=stats.max,
                last=stats.last,
                avg=stats.sum / stats.count,
                var=stats.sum_squares / stats.count - (stats.sum / stats.count) ** 2,
            ),
        )
