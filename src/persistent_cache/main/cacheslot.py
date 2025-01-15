import pickle
from collections.abc import Callable
from typing import Any, Generic, TypeVar, cast

from persistent_cache.models import Path
from persistent_cache.reducers.base import Reducer

from . import hashing

T = TypeVar("T")


class CacheSlot(Generic[T]):
    def __init__(
        self,
        function: Callable[..., T],
        args: tuple[Any, ...],
        key_reducer: type[Reducer] = Reducer,
        cache_path: Path = Path.cache,
    ) -> None:
        # change cache key when implementation changes
        cache_keys = (function, args)
        self.location = (
            cache_path
            / function.__module__.replace(".", "_")
            / function.__name__
            / hashing.compute_hash(key_reducer, cache_keys)
        )

    @property
    def value(self) -> T:
        try:
            with self.location.open("rb") as fp:
                value = pickle.Unpickler(fp).load()  # noqa: S301
        except (pickle.UnpicklingError, EOFError):
            # discard values of corrupted or empty slots
            raise KeyError from None
        return cast(T, value)

    @value.setter
    def value(self, value: T) -> None:
        self.location.byte_content = pickle.dumps(value)
