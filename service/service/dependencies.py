from service import storage
from service.config import config
from service.dtos import AddBatchRequest
from service.statistics import Statistic


def get_storage(request: AddBatchRequest | str) -> storage.StatsStorage:
    symbol = request.symbol if isinstance(request, AddBatchRequest) else request
    return storage.get_storage_for_symbol(
        symbol=symbol,
        max_size=config.MAX_LEN,
        stats_class=Statistic,
    )
