import inspect
import io
from types import FunctionType, ModuleType
from typing import Callable, Union

from .. import decorator


class Reducer:
    @classmethod
    def reduce_code(cls, code_object: Union[FunctionType, ModuleType]) -> str:
        """
        custom lambda reduction needed:
            https://www.pythonpool.com/cant-pickle-local-object/
        custom module reduction needed:
            https://stackoverflow.com/questions/2790828/python-cant-pickle-module-objects-error
        name reduction for function/module is not enough because we assume
        cache result can change when function/module implementation changes
        """

        try:
            reduction = inspect.getsource(code_object)
        except:
            # cannot access source code of builtins
            # but no problem because we assume this code does not change
            reduction = code_object.__name__
        return reduction

    @classmethod
    def reduce_file_objects(cls, _: Union[io.BytesIO, io.BufferedWriter]) -> str:
        # Closed file pointers cannot and do not need to be pickled for cache functionality
        return ""


cache = decorator.cache(Reducer)
