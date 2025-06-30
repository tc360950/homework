from typing import NamedTuple, Protocol


class StatisticProtocol(Protocol):
    @classmethod
    def create(cls, value: float) -> "StatisticProtocol": ...

    @classmethod
    def merge(cls, *statistics: "StatisticProtocol") -> "StatisticProtocol": ...


class Statistic(NamedTuple):
    min: float
    max: float
    last: float
    sum: float
    count: int
    sum_squares: float

    @classmethod
    def create(cls, value: float) -> "Statistic":
        return cls(
            min=value,
            max=value,
            last=value,
            sum=value,
            count=1,
            sum_squares=value**2,
        )

    @classmethod
    def merge(cls, *statistics: "Statistic") -> "Statistic":
        return cls(
            min=min(stat.min for stat in statistics),
            max=max(stat.max for stat in statistics),
            last=statistics[-1].last,
            sum=sum(stat.sum for stat in statistics),
            count=sum(stat.count for stat in statistics),
            sum_squares=sum(stat.sum_squares for stat in statistics),
        )
