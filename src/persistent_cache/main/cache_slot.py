import inspect
import pickle
from collections.abc import Callable, Iterable, Iterator
from dataclasses import dataclass
from functools import cached_property
from inspect import BoundArguments
from typing import Any

from persistent_cache.models import Path
from persistent_cache.reducers.base import Reducer

from . import hashing


@dataclass
class CacheSlot:
    function: Callable[..., Any]
    args: tuple[Any, ...]
    kwargs: dict[str, Any]
    directory: Path
    key_arguments: Iterable[str] | str | None
    argument_reducers: dict[str, Callable[[Any], Any]] | None
    extra_keys: Any
    key_reducer: type[Reducer] | None
    deep_learning: bool
    speedup_deep_learning: bool

    @property
    def value(self) -> Any:
        try:
            with self.path.open("rb") as fp:
                return pickle.Unpickler(fp).load()  # noqa: S301
        except (pickle.UnpicklingError, EOFError):
            # discard values of corrupted or empty slots
            raise KeyError from None

    @value.setter
    def value(self, value: Any) -> None:
        self.path.byte_content = pickle.dumps(value)

    @cached_property
    def path(self) -> Path:
        return (
            self.directory
            / self.function.__module__.replace(".", "_")
            / self.function.__name__
            / hashing.compute_hash(self.reducer, self.keys)
        )

    @property
    def keys(self) -> Iterator[Any]:
        yield self.function
        is_iterable = isinstance(self.extra_keys, Iterable) and not isinstance(
            self.extra_keys,
            str | bytes | bytearray,
        )
        if is_iterable:
            yield from self.extra_keys
        else:
            yield self.extra_keys
        yield from self.argument_values

    @property
    def argument_values(self) -> Iterator[Any]:
        if self.key_arguments is None and self.argument_reducers is None:
            yield from self.args
            yield from self.kwargs.values()
        else:
            arguments = inspect.signature(self.function).bind(*self.args, **self.kwargs)
            arguments.apply_defaults()
            yield from self.extract_argument_values(arguments)

    def extract_argument_values(self, arguments: BoundArguments) -> Iterator[Any]:
        if self.key_arguments is not None:
            if isinstance(self.key_arguments, str):
                yield arguments.arguments.get(self.key_arguments)
            else:
                for name in self.key_arguments:
                    yield arguments.arguments.get(name)
        if self.argument_reducers is not None:
            for argument_name, reducer in self.argument_reducers.items():
                argument = arguments.arguments.get(argument_name)
                yield reducer(argument)

    @property
    def reducer(self) -> type[Reducer]:
        if self.key_reducer is not None:
            return self.key_reducer
        if self.deep_learning:
            from persistent_cache.reducers.deep_learning import Reducer as Reducer_

            return Reducer_
        if self.speedup_deep_learning:
            from persistent_cache.reducers.speedup_deep_learning import (
                Reducer as Reducer_,
            )

            return Reducer_

        return Reducer
