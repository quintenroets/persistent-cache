import io
import math
from collections.abc import Callable
from typing import Any

import cli
import pytest

from persistent_cache import cache, deep_learning, speedup_deep_learning
from persistent_cache.reducers import Reducer

caches = [cache, deep_learning.cache, speedup_deep_learning.cache]


def calculate_with_name(value: str) -> None:
    cli.console.print(value)


def calculate(*args: Any, **kwargs: Any) -> None:
    cli.console.print("calculation started")
    cli.console.print(args, kwargs)


def verify_cached_function(function: Callable[..., Any]) -> None:
    with io.BytesIO() as fp:
        function(fp, lambda x: x, math, {})


@pytest.mark.parametrize("cache_decorator", caches)
def test_cache_with_argument_combination(cache_decorator: Callable[..., Any]) -> None:
    cached_function = cache_decorator(calculate)
    verify_cached_function(cached_function)


@pytest.mark.parametrize("cache_decorator", caches)
def test_cache_as_function(cache_decorator: Callable[..., Any]) -> None:
    cached_function = cache_decorator()(calculate)
    verify_cached_function(cached_function)


@pytest.mark.parametrize("cache_decorator", caches)
def test_cache_with_argument_name(
    cache_decorator: Callable[..., Any],
) -> None:
    cached_function = cache_decorator(calculate_with_name, cache_key_arguments="value")
    cached_function("test")


@pytest.mark.parametrize("cache_decorator", caches)
def test_cache_with_argument_names(cache_decorator: Callable[..., Any]) -> None:
    cache_key_arguments = ("value",)
    cached_function = cache_decorator(
        calculate_with_name,
        cache_key_arguments=cache_key_arguments,
    )
    cached_function("test")


@pytest.mark.parametrize("cache_decorator", caches)
def test_cache_with_extra_cache_key(
    cache_decorator: Callable[..., Any],
) -> None:
    cached_function = cache_decorator(calculate_with_name, extra_cache_keys="value")
    cached_function("test")


@pytest.mark.parametrize("cache_decorator", caches)
def test_cache_with_extra_cache_keys(
    cache_decorator: Callable[..., Any],
) -> None:
    cached_function = cache_decorator(
        calculate_with_name,
        extra_cache_keys=("value",),
    )
    cached_function("test")


@pytest.mark.parametrize("cache_decorator", caches)
def test_cache_with_reducer(
    cache_decorator: Callable[..., Any],
) -> None:
    cached_function = cache_decorator(
        calculate_with_name,
        key_reducer=Reducer,
    )
    cached_function("test")


@pytest.mark.parametrize("cache_decorator", caches)
def test_cache_with_argument_reducer(
    cache_decorator: Callable[..., Any],
) -> None:
    cached_function = cache_decorator(
        calculate_with_name,
        argument_reducers={"value": lambda x: x.strip()},
    )
    cached_function("test")
