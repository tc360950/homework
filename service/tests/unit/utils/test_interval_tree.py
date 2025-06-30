from typing import NamedTuple

import pytest

from service.utils.interval_tree import DenaryIntervalTree


class SumAndLastStatistic(NamedTuple):
    sum: float
    last: float

    @classmethod
    def create(cls, value: float) -> "SumAndLastStatistic":
        return cls(sum=value, last=value)

    @classmethod
    def merge(cls, *statistics: "SumAndLastStatistic") -> "SumAndLastStatistic":
        return cls(sum=sum(stat.sum for stat in statistics), last=statistics[-1].last)


def _create_interval_tree(max_size: int) -> DenaryIntervalTree[SumAndLastStatistic]:
    return DenaryIntervalTree[SumAndLastStatistic](max_size, SumAndLastStatistic)


@pytest.mark.unit
def test_reading_from_empty_tree() -> None:
    assert _create_interval_tree(1).calculate(0, 0) is None


@pytest.mark.unit
def test_reading_from_empty_range() -> None:
    tree = _create_interval_tree(10)
    tree.add([1, 2, 3], 0)
    assert tree.calculate(9, 9) is None


@pytest.mark.unit
def test_adding_more_values_than_supported() -> None:
    with pytest.raises(ValueError):
        _create_interval_tree(10).add([1, 2, 3], 9)


@pytest.mark.unit
@pytest.mark.parametrize(
    ("inserts", "query", "expected_result", "max_size"),
    [
        (
            [
                ([1, 2, 3], 0),
                ([4, 5, 6], 1),
                ([7, 8, 9], 2),
            ],
            (0, 2),
            (12.0, 7.0),
            5,
        ),
        (
            [
                (list(range(1000)), 25),
            ],
            (0, 1000),
            (sum(range(1000 - 25 + 1)), 1000 - 25),
            10000,
        ),
        (
            [
                ([0, 0, 0, 0, 0, 0, 0, 0, 0, 0], 1),
                ([1, 1, 1, 1, 1, 1, 1, 1, 1, 1], 1),
                ([2, 2, 2, 2, 2, 2, 2, 2, 2, 2], 1),
                ([3, 3, 3, 3, 3, 3, 3, 3, 3, 3], 1),
                ([4, 4, 4, 4, 4, 4, 4, 4, 4, 4], 1),
                ([5, 5, 5, 5, 5, 5, 5, 5, 5, 5], 1),
                ([6, 6, 6, 6, 6, 6, 6, 6, 6, 6], 1),
                ([7, 7, 7, 7, 7, 7, 7, 7, 7, 7], 1),
                ([8, 8, 8, 8, 8, 8, 8, 8, 8, 8], 1),
                ([9, 9, 9, 9, 9, 9, 9, 9, 9, 9], 1),
            ],
            (0, 5),
            (5 * 9, 9),
            1000000,
        ),
    ],
)
def test_interval_tree(
    inserts: list[tuple[list[float], int]],
    query: tuple[int, int],
    expected_result: tuple[float, float],
    max_size: int,
) -> None:
    interval_tree = _create_interval_tree(max_size)
    for values, index in inserts:
        interval_tree.add(values, index)

    result = interval_tree.calculate(*query)
    assert tuple(result) == expected_result
