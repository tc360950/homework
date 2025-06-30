import pytest

from service.dtos import StatsResponse
from service.statistics import Statistic


@pytest.mark.parametrize(
    ("symbol", "k", "stats", "expected_response"),
    [
        (
            "AAPL",
            4,
            Statistic(  # [1,2,3]
                min=1.0,
                max=3.0,
                last=3.0,
                sum=6.0,
                count=3,
                sum_squares=14.0,
            ),
            StatsResponse(
                symbol="AAPL",
                k=4,
                statistics=StatsResponse.Statistics(
                    min=1.0,
                    max=3.0,
                    last=3.0,
                    avg=2.0,
                    var=2 / 3,
                ),
            ),
        ),
    ],
)
@pytest.mark.unit
def test_stats_response_create(
    symbol: str,
    k: int,
    stats: Statistic,
    expected_response: StatsResponse,
) -> None:
    response = StatsResponse.create(symbol=symbol, k=k, stats=stats)
    assert response.k == expected_response.k
    assert response.symbol == expected_response.symbol
    fields = ("min", "max", "last", "avg", "var")
    for field in fields:
        assert getattr(response.statistics, field) == pytest.approx(
            getattr(expected_response.statistics, field),
        )
