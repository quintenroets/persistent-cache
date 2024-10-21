import math
from typing import Any

import torch
from numpy.typing import NDArray
from torch.utils.data import Dataset

from . import deep_learning

SEED_VALUE = 493
LARGE_DIMENSION = 10000


class Reducer(deep_learning.Reducer):
    @classmethod
    def reduce_np_array(cls, array: NDArray[Any]) -> Any:
        shape = array.shape
        reduction: Any
        if shape:
            if math.prod(shape) > LARGE_DIMENSION:
                # only use part of array large for speedup
                length = shape[0] if shape else 0
                data = (array[13**17 % length]) if length > 0 else []
                reduction = shape, data
            else:
                reduction = list(array)
        else:
            reduction = array.item()
        return reduction

    @classmethod
    def reduce_model(cls, model: torch.nn.Module) -> tuple[Any, Any]:
        weights: Any
        weights, implementation = super().reduce_model(model)
        length = len(weights)
        if length > 0:
            # only use part of weights for speedup
            values = list(weights.values())
            reduction_indices = (0, length // 2, -1)
            weights = tuple(values[i] for i in reduction_indices)

        return weights, implementation

    @classmethod
    def reduce_dataset(cls, dataset: Dataset[Any]) -> tuple[int, Any, Any]:
        length = len(dataset)  # type: ignore[arg-type]

        # fix random seed to have deterministic hash
        # for datasets with random augmentation
        torch.random.manual_seed(SEED_VALUE)

        # only use part of dataset for speedup
        data = dataset[13**17 % length] if length > 0 else []
        if isinstance(data, tuple):
            data, label = data
        else:
            label = None

        return length, data, label

    @classmethod
    def reduce_tensor(cls, tensor: torch.Tensor) -> NDArray[Any]:
        return tensor.detach().cpu().numpy()
