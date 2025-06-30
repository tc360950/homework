import threading
from typing import Generic, TypeVar

from service.statistics import StatisticProtocol
from service.utils.interval_tree import DenaryIntervalTree

StatT = TypeVar("StatT", bound=StatisticProtocol)

symbol_store_lock = threading.Lock()


class StatsStorage(Generic[StatT]):
    """In-memory circular storage for calculating aggregates over time series data.

    This class stores a fixed number of the most recent
    floating-point values and supports fast computation of aggregate
    statistics (e.g., min, max, average, variance)
    over the last `n` data points using an interval tree.


    Attributes:
        _max_size (int): Maximum number of latest values to
            retain (circular buffer capacity).
        _stats_class (type[StatT]): Class implementing `StatisticProtocol`.
        _interval_tree (DenaryIntervalTree): Efficient interval-based
            structure for O(log n) stats.
        _index (int): Current index in the circular buffer
            where the next data point will be inserted.

    Methods:
        add(values: list[float]) -> None:
            Inserts a batch of new data points into the circular
            buffer and updates internal structures.

        get(last_n: int) -> StatT | None:
            Retrieves aggregated statistics over the last `last_n` data points.
            Returns `None` if no points are available.

    Example:
        >>> stats_storage = StatsStorage(max_size=10000, stats_class=OnlineStats)
        >>> stats_storage.add([101.2, 102.5, 100.1, 99.7])
        >>> stats = stats_storage.get(3)
        >>> print(stats.min, stats.max, stats.avg, stats.var)
        100.1 102.5 100.766... 2.156...

    This class is not thread-safe.

    """

    def __init__(self, max_size: int, stats_class: type[StatT]):
        """Initialize storage.

        :param max_size: Maximum number of latest data points to retain
        :param stats_class: Class implementing `StatisticProtocol`.
        """
        self._max_size = max_size
        self._stats_class = stats_class
        self._interval_tree = DenaryIntervalTree[StatT](max_size, self._stats_class)
        # Index of last inserted data point plus one modulo max_size,
        # i.e. the index of the next data point
        self._index = 0

    def add(self, values: list[float]) -> None:
        len_values = len(values)
        if self._index + len_values > self._max_size:
            self._interval_tree.add(values[: self._max_size - self._index], self._index)
            self._interval_tree.add(values[self._max_size - self._index :], 0)
        else:
            self._interval_tree.add(values, self._index)
        self._index = (self._index + len_values) % self._max_size

    def get(self, last_n: int) -> StatT | None:
        end = (self._index - 1) % self._max_size
        if end - last_n + 1 < 0:
            # The order of queries is very important here if any statistic relies on
            # ordering
            queries = [
                (self._max_size - (last_n - end - 1), self._max_size),
                (0, end),
            ]
        else:
            queries = [(end - last_n + 1, end)]
        stats = [self._interval_tree.calculate(start, end) for start, end in queries]
        stats = [stat for stat in stats if stat is not None]
        if not stats:
            return None
        return self._stats_class.merge(*stats)


symbol_store: dict[str, StatsStorage] = {}


def get_storage_for_symbol(
    symbol: str,
    max_size: int,
    stats_class: type[StatisticProtocol],
) -> StatsStorage:
    with symbol_store_lock:
        if symbol not in symbol_store:
            symbol_store[symbol] = StatsStorage[stats_class](
                max_size=max_size,
                stats_class=stats_class,
            )
        return symbol_store[symbol]
