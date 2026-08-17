from __future__ import annotations

import hashlib
import inspect
import io
import pickle
from functools import cache
from typing import TYPE_CHECKING, Any

from package_utils.annotations import first_parameter_types

if TYPE_CHECKING:
    from collections.abc import Callable, Iterator  # pragma: nocover
    from typing import BinaryIO  # pragma: nocover

    from persistent_cache.reducers.base import Reducer  # pragma: nocover


def compute_hash(key_reducer: type[Reducer], items: Iterator[Any]) -> str:
    with io.BytesIO() as fp:
        HashPickler(fp, key_reducer).dump(tuple(items))
        data = fp.getvalue()
    # use fast hash function because it is not used for security
    return hashlib.new("sha1", data=data, usedforsecurity=False).hexdigest()


class HashPickler(pickle.Pickler):
    def __init__(self, file_pointer: BinaryIO, reducer: type[Reducer]) -> None:
        super().__init__(file_pointer)
        self.reducers = load_reducers(reducer)  # type: ignore[arg-type]

    def reducer_override(self, obj: Any) -> Any:
        """The goal of this pickler is to create hashes of complex objects, not to
        reconstruct complex objects.

        So mapping does not need to be reversible.
        """
        reducer = next(self.determine_reducer(obj), None)
        return NotImplemented if reducer is None else (tuple, (reducer(obj),))

    def determine_reducer(self, obj: Any) -> Iterator[Callable[[Any], Any]]:
        if obj is not tuple:
            for obj_type, reducer in self.reducers.items():
                if isinstance(obj, obj_type):
                    yield reducer


@cache
def load_reducers(reducer: type[Reducer]) -> dict[type, Callable[[Any], Any]]:
    return {
        parameter_type: method
        for _, method in inspect.getmembers(reducer, predicate=inspect.ismethod)
        for parameter_type in first_parameter_types(method)
    }
