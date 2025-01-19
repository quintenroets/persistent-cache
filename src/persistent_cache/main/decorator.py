from collections.abc import Callable, Iterable
from functools import wraps
from typing import Any, TypeVar, cast, overload

from persistent_cache.models import Path
from persistent_cache.reducers.base import Reducer

from .cache_slot import CacheSlot

F = TypeVar("F", bound=Callable[..., Any])


@overload
def cache(
    function: F,
    *,
    cache_directory: Path = Path.cache,
    cache_key_arguments: Iterable[str] | str | None = None,
    extra_cache_keys: Iterable[Any] | None = None,
    key_reducer: type[Reducer] = Reducer,
    deep_learning: bool = False,
    speedup_deep_learning: bool = False,
) -> F: ...


@overload
def cache(
    function: None = None,
    *,
    cache_directory: Path = Path.cache,
    cache_key_arguments: Iterable[str] | str | None = None,
    extra_cache_keys: Any = None,
    key_reducer: type[Reducer] = Reducer,
    deep_learning: bool = False,
    speedup_deep_learning: bool = False,
) -> Callable[[F], F]: ...


def cache(  # noqa: PLR0913
    function: F | None = None,
    *,
    cache_directory: Path = Path.cache,
    cache_key_arguments: Iterable[str] | str | None = None,
    extra_cache_keys: Any = None,
    key_reducer: type[Reducer] | None = None,
    deep_learning: bool = False,
    speedup_deep_learning: bool = False,
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

    def cache_decorator(function_: F) -> F:
        @wraps(function_)
        def wrapped_function(*args: Any, **kwargs: Any) -> Any:
            cache_slot = CacheSlot(
                function_,
                args,
                kwargs,
                cache_directory,
                cache_key_arguments,
                extra_cache_keys,
                key_reducer,
                deep_learning,
                speedup_deep_learning,
            )
            try:
                result = cache_slot.value
            except KeyError:
                result = function_(*args, **kwargs)
                cache_slot.value = result
            return result

        return cast(F, wrapped_function)

    if function is not None:
        cache_decorator = cache_decorator(function)
    return cache_decorator
