from collections.abc import Callable
from functools import wraps
from typing import Any, TypeVar, cast

from persistent_cache.models import Path
from persistent_cache.reducers.base import Reducer

from .cacheslot import CacheSlot

T = TypeVar("T")
F = TypeVar("F", bound=Callable[..., Any])


def cache(
    key_reducer: type[Reducer] = Reducer,
    cache_path: Path = Path.cache,
) -> Callable[[F], F]:
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

    return cache_decorator
