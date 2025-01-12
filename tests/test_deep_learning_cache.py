from collections.abc import Callable
from typing import Any

import cli
import numpy as np
import pytest
import torch
from torch.utils.data import TensorDataset

from persistent_cache import deep_learning, speedup_deep_learning
from persistent_cache.reducers.speedup_deep_learning import LARGE_DIMENSION

caches = [deep_learning.cache, speedup_deep_learning.cache]


def calculate(*args: Any, **kwargs: Any) -> None:
    cli.console.print("calculation started")
    cli.console.print(args, kwargs)


def verify_cached_function(function: Callable[..., Any]) -> None:
    array = np.zeros(10)
    large_array = np.zeros((10, LARGE_DIMENSION))
    tensor = torch.tensor(array)
    module = torch.nn.Linear(10, 2)
    dataset = TensorDataset(tensor)
    labeled_dataset = TensorDataset(tensor, tensor)
    function(array, tensor, module, dataset, large_array, labeled_dataset)


@pytest.mark.parametrize("cache_decorator", caches)
def test_cache_with_argument_combination(cache_decorator: Callable[..., Any]) -> None:
    cached_function = cache_decorator(calculate)
    verify_cached_function(cached_function)
