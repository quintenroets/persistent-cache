import io
import math
from collections.abc import Callable
from typing import Any, TypeVar

import cli
import pytest

from persistent_cache.caches import base, deep_learning, speedup_deep_learning

F = TypeVar("F", bound=Callable)  # type: ignore[type-arg]


def calculate(*args: Any, **kwargs: Any) -> None:
    cli.console.print("calculation started")
    cli.console.print(args, kwargs)


caches = [base.cache, deep_learning.cache, speedup_deep_learning.cache]


@pytest.mark.parametrize("cache", caches)
def test_cache_with_argument_combination(cache: Callable) -> None:  # type: ignore[type-arg]
    cached_function = cache(calculate)
    with io.BytesIO() as fp:
        cached_function(fp, lambda x: x, math, {})
