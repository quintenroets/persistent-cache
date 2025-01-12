from collections.abc import Callable

from persistent_cache.main import decorator
from persistent_cache.models import F, Path
from persistent_cache.reducers import Reducer


def cache(
    function: F | None = None,
    *,
    key_reducer: type[Reducer] | None = None,
    cache_path: Path = Path.cache,
) -> Callable[[F], F]:
    if key_reducer is None:
        from persistent_cache.reducers import speedup_deep_learning

        key_reducer = speedup_deep_learning.Reducer
    return decorator.cache(function, key_reducer=key_reducer, cache_path=cache_path)
