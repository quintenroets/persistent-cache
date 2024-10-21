from __future__ import annotations

import hashlib
import inspect
import io
import pickle
from typing import TYPE_CHECKING, Any, get_args, get_type_hints

from persistent_cache.reducers.base import Reducer

if TYPE_CHECKING:
    from collections.abc import Callable, Iterator
    from typing import BinaryIO


class HashPickler(pickle.Pickler):
    def __init__(
        self,
        file_pointer: BinaryIO,
        reducer: type[Reducer] = Reducer,
    ) -> None:
        super().__init__(file_pointer)
        self.reducer = reducer
        self.reducers = {}
        for _, method in inspect.getmembers(reducer, predicate=inspect.ismethod):
            type_hints = get_type_hints(method).values()
            if type_hints:
                argument_type = next(iter(type_hints))
                argument_types = get_args(argument_type) or (argument_type,)
                for argument_type in argument_types:
                    self.reducers[argument_type] = method
        self.reducers.pop(Any, None)

    def reducer_override(self, obj: Any) -> Any:
        """The goal of this pickler is to create hashes of complex objects, not to
        reconstruct complex objects.

        So mapping does not need to be reversible.
        """
        reducer = next(self.determine_reducer(obj), None)
        reduction: Any
        if reducer is None:
            reduction = NotImplemented
        else:
            mapping = reducer(obj)
            str_mapping = str(object_to_bytes(self.reducer, mapping))
            reduction = str, (str_mapping,)
        return reduction

    def determine_reducer(self, obj: Any) -> Iterator[Callable[[Any], Any]]:
        if obj is not str:
            for obj_type, reducer in self.reducers.items():
                if isinstance(obj, obj_type):
                    yield reducer


def compute_hash(key_reducer: type[Reducer], *args: Any) -> str:
    data = object_to_bytes(key_reducer, args)
    # use fast hash function because it is not used for security
    return hashlib.new("sha1", data=data, usedforsecurity=False).hexdigest()


def object_to_bytes(key_reducer: type[Reducer], args: Any) -> bytes:
    with io.BytesIO() as fp:
        # Use custom pickler to generate bytes from complex structures
        HashPickler(fp, key_reducer).dump(args)
        fp.seek(0)
        return fp.read()
