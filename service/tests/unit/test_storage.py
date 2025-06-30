import random

import pytest
from tqdm import tqdm

from service.statistics import Statistic
from service.storage import StatsStorage

random.seed(7236218)


@pytest.mark.unit
def test_storage_fuzzy() -> None:
    max_elements = 10**4
    storage = StatsStorage(max_elements, Statistic)
    data = []

    def _generate_input(n: int) -> list[float]:
        return [(random.random() - 0.5) * 100 for _ in range(n)]

    for _ in tqdm(range(10000)):
        input_size = random.randint(1, 1000)
        input_ = _generate_input(input_size)
        storage.add(input_)
        data.extend(input_)
        data = data[-max_elements:]

        query = 10 ** random.randint(1, 4)

        query_result = storage.get(query)
        assert query_result.min == min(data[-query:])
        assert query_result.max == max(data[-query:])
        assert query_result.sum == pytest.approx(sum(data[-query:]))
        assert query_result.count == len(data[-query:])
        assert query_result.sum_squares == pytest.approx(
            sum(x**2 for x in data[-query:]),
        )
        assert query_result.last == data[-1]
