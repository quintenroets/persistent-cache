from collections.abc import Callable
from functools import wraps
from typing import Any, cast, overload

from persistent_cache.models import F, Path
from persistent_cache.reducers.base import Reducer

from .cacheslot import CacheSlot


@overload
def cache(
    function: F,
    *,
    key_reducer: type[Reducer] = Reducer,
    cache_path: Path = Path.cache,
) -> F: ...


@overload
def cache(
    function: None = None,
    *,
    key_reducer: type[Reducer] = Reducer,
    cache_path: Path = Path.cache,
) -> Callable[[F], F]: ...


def cache(
    function: F | None = None,
    *,
    key_reducer: type[Reducer] = Reducer,
    cache_path: Path = Path.cache,
) -> F | Callable[[F], F]:
    """A decorator to cache function results. Decorated functions are only executed if
    result is not present in cache. The arguments of the function can be any nested
    complex object.

    Use as:

    from persistent_cache import cache

    @cache
    def long_function(complex_object):
        ...
    """

    def cache_decorator(function: F) -> F:
        @wraps(function)
        def wrapped_function(*args: Any, **kwargs: Any) -> Any:
            cache_slot = CacheSlot(function, args, kwargs, key_reducer, cache_path)
            try:
                value = cache_slot.value
            except KeyError:
                value = function(*args, **kwargs)
                cache_slot.value = value
            return value

        return cast(F, wrapped_function)

    if function is not None:
        cache_decorator = cache_decorator(function)
    return cache_decorator
