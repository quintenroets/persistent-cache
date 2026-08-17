from __future__ import annotations

import hashlib
import inspect
import io
import itertools
import pickle
from types import UnionType
from typing import TYPE_CHECKING, Any, Union, get_args, get_origin, get_type_hints

from persistent_cache.reducers.base import Reducer

if TYPE_CHECKING:
    from collections.abc import Callable, Iterator  # pragma: nocover
    from typing import BinaryIO  # pragma: nocover


def extract_reducers(
    reducer: type[Reducer],
) -> Iterator[tuple[type, Callable[[Any], Any]]]:
    for _, method in inspect.getmembers(reducer, predicate=inspect.ismethod):
        for parameter_type in extract_types(method):
            yield parameter_type, method


def extract_types(method: Callable[[Any], Any]) -> Iterator[type]:
    type_hints = get_type_hints(method)
    type_hints.pop("return", None)
    for annotation in itertools.islice(type_hints.values(), 1):
        yield from extract_annotation_types(annotation)


def extract_annotation_types(annotation: Any) -> Iterator[type]:
    origin = get_origin(annotation)
    resolved_annotation = annotation if origin is None else origin
    if resolved_annotation in (UnionType, Union):
        for argument in get_args(annotation):
            yield from extract_annotation_types(argument)
    elif isinstance(resolved_annotation, type):
        yield resolved_annotation
    else:
        yield from extract_annotation_types(resolved_annotation.__value__)


class HashPickler(pickle.Pickler):
    def __init__(
        self,
        file_pointer: BinaryIO,
        reducer: type[Reducer] = Reducer,
    ) -> None:
        super().__init__(file_pointer)
        self.reducer = reducer
        self.reducers = dict(extract_reducers(reducer))

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
            str_mapping = str(item_to_bytes(self.reducer, mapping))
            reduction = str, (str_mapping,)
        return reduction

    def determine_reducer(self, obj: Any) -> Iterator[Callable[[Any], Any]]:
        if obj is not str:
            for obj_type, reducer in self.reducers.items():
                if isinstance(obj, obj_type):
                    yield reducer


def compute_hash(key_reducer: type[Reducer], items: Iterator[Any]) -> str:
    data = item_to_bytes(key_reducer, tuple(items))
    # use fast hash function because it is not used for security
    return hashlib.new("sha1", data=data, usedforsecurity=False).hexdigest()


def item_to_bytes(key_reducer: type[Reducer], item: Any) -> bytes:
    with io.BytesIO() as fp:
        # Use custom pickler to generate bytes from complex structures
        pickler = HashPickler(fp, key_reducer)
        pickler.dump(item)
        fp.seek(0)
        return fp.read()
