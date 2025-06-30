import math
from typing import Generic, TypeVar

from typing_extensions import NamedTuple

from service.statistics import StatisticProtocol

StatT = TypeVar("StatT", bound=StatisticProtocol)


class _Node(NamedTuple):
    interval: tuple[int, int]
    stat: StatisticProtocol


class DenaryIntervalTree(Generic[StatT]):
    """Fixed-capacity, denary (base-10) interval tree for rapid computation
    of aggregate statistics over an interval.

    This data structure stores up to `size` values and allows
    efficient querying of aggregate statistics
    (e.g., min, max, average, variance) over arbitrary contiguous intervals
    in sub-linear time.

    Note:
        - This class is **not thread-safe**.
        - The structure is intended to be used as a static buffer:
            values are inserted only at known indices.
        - It can be further optimized using Cython

    Parameters
    ----------
        size (int): Maximum number of leaf nodes.
            Internally rounded up to the next power of 10.
        stats_class (type[StatT]): A class implementing the required
            statistic protocol with:
                - `create(value: float) -> StatT`
                - `merge(*stats: StatT) -> StatT`

    Attributes
    ----------
        _size (int): Logical capacity for values (<= `size`).
        _stats_class: Class used to compute and merge statistics.
        _tree (list[_Node | None]): Internal flat list representing a denary tree.
        _leaves_start_index (int): Start index in `_tree` of the first leaf node.

    Methods
    -------
        add(values: list[float], index: int) -> None:
            Inserts values into the tree starting at the
            specified index, updating internal aggregates.
            Raises ValueError if the values would exceed the tree's logical capacity.

        calculate(start: int, end: int) -> StatT | None:
            Computes and returns the aggregated statistics
            over the specified [start, end] interval.
            Returns None if no values exist in the interval.

    Example:
        >>> tree = DenaryIntervalTree(size=10000, stats_class=OnlineStats)
        >>> tree.add([101.0, 102.5, 103.2], index=0)
        >>> result = tree.calculate(0, 2)
        >>> round(result.avg, 2)
        102.23

    """

    def __init__(self, size: int, stats_class: type[StatT]):
        """Initialize interval tree.

        :param size: Maximum number of leaves in the tree
        :param stats_class: Class implementing `StatisticProtocol`.
        """
        self._size = size
        h = math.ceil(math.log10(self._size))
        leaves = 10**h
        total_nodes = (10 ** (h + 1) - 1) // 9
        self._stats_class = stats_class
        self._tree: list[_Node | None] = [None for _ in range(total_nodes)]
        self._leaves_start_index = total_nodes - leaves

    def add(self, values: list[float], index: int) -> None:
        len_values = len(values)
        if len_values + index > self._size:
            raise ValueError("Index out of range")
        for i in range(index, index + len_values):
            self._tree[i + self._leaves_start_index] = _Node(
                (i, i),
                self._stats_class.create(values[i - index]),
            )

        first_parent = (self._leaves_start_index + index - 1) // 10
        last_parent = (self._leaves_start_index + index + len_values - 2) // 10
        self._repair_tree(first_parent, last_parent)

    def calculate(self, start: int, end: int) -> StatT | None:
        def _query(node_idx: int, interval: tuple[int, int]) -> StatT | None:
            if node_idx >= len(self._tree) or self._tree[node_idx] is None:
                return None
            node = self._tree[node_idx]
            if node.interval[1] < interval[0] or interval[1] < node.interval[0]:
                # Node interval is disjoint from the interval
                return None

            if interval[0] <= node.interval[0] and node.interval[1] <= interval[1]:
                # The node is fully withing the interval
                return node.stat

            # Partial overlap
            children_stats = [
                _query(10 * node_idx + child_idx + 1, interval)
                for child_idx in range(10)
            ]
            children_stats = [stat for stat in children_stats if stat is not None]
            if not children_stats:
                return None
            return self._stats_class.merge(*children_stats)

        root = self._tree[0]
        if root is None:
            return None

        return _query(0, (start, end))

    def _repair_tree(self, start: int, end: int) -> None:
        while start != end or start != 0:
            for i in range(start, end + 1):
                children = [self._tree[10 * i + 1 + idx] for idx in range(10)]
                self._tree[i] = self._create_parent_node(children)
            start = start if start == 0 else (start - 1) // 10
            end = (end - 1) // 10
        self._tree[0] = self._create_parent_node([self._tree[i] for i in range(1, 11)])

    def _create_parent_node(self, children: list[_Node | None]) -> _Node:
        children = [child for child in children if child is not None]
        return _Node(
            interval=(children[0].interval[0], children[-1].interval[1]),
            stat=self._stats_class.merge(*[child.stat for child in children]),
        )
