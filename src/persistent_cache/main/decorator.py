import inspect
from collections.abc import Callable, Iterator
from functools import wraps
from typing import Any, cast, overload

from persistent_cache.models import F, Path
from persistent_cache.reducers.base import Reducer

from .cacheslot import CacheSlot


@overload
def cache(
    function: F,
    *,
    cache_path: Path = Path.cache,
    cache_key_arguments: tuple[str, ...] | str | None = None,
    key_reducer: type[Reducer] = Reducer,
    deep_learning: bool = False,
    speedup_deep_learning: bool = False,
) -> F: ...


@overload
def cache(
    function: None = None,
    *,
    cache_path: Path = Path.cache,
    cache_key_arguments: tuple[str, ...] | str | None = None,
    key_reducer: type[Reducer] = Reducer,
    deep_learning: bool = False,
    speedup_deep_learning: bool = False,
) -> Callable[[F], F]: ...


def cache(  # noqa: PLR0913
    function: F | None = None,
    *,
    cache_path: Path = Path.cache,
    cache_key_arguments: tuple[str, ...] | str | None = None,
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

    reducer = extract_reducer(
        key_reducer,
        deep_learning=deep_learning,
        speedup_deep_learning=speedup_deep_learning,
    )

    def cache_decorator(function: F) -> F:
        @wraps(function)
        def wrapped_function(*args: Any, **kwargs: Any) -> Any:
            arguments = tuple(
                extract_argument_values(function, args, kwargs, cache_key_arguments),
            )
            cache_slot = CacheSlot(function, arguments, reducer, cache_path)
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


def extract_argument_values(
    function: F,
    args: tuple[Any, ...],
    kwargs: dict[str, Any],
    cache_key_arguments: tuple[str, ...] | str | None = None,
) -> Iterator[Any]:
    if cache_key_arguments is None:
        yield from (args, kwargs)
    else:
        arguments = inspect.signature(function).bind(*args, **kwargs)
        arguments.apply_defaults()
        if isinstance(cache_key_arguments, str):
            yield arguments.arguments.get(cache_key_arguments)
        else:
            for name in cache_key_arguments:
                yield arguments.arguments.get(name)


def extract_reducer(
    reducer: type[Reducer] | None,
    *,
    deep_learning: bool,
    speedup_deep_learning: bool,
) -> type[Reducer]:
    if reducer is None:
        if deep_learning:
            from persistent_cache.reducers.deep_learning import Reducer as Reducer_

            reducer = Reducer_
        elif speedup_deep_learning:
            from persistent_cache.reducers.speedup_deep_learning import (
                Reducer as Reducer_,
            )

            reducer = Reducer_
        else:
            reducer = Reducer
    return reducer
