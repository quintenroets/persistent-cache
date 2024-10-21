import inspect
import io
from types import FunctionType, ModuleType


class Reducer:
    """Inherit from this class to implement own custom pickler.

    The result of each function are pickled further with their custom
    pickling function, so make sure to reduce each object to a new
    object in each reduction function in order to avoid infinity
    recursive calls.
    """

    @classmethod
    def reduce_code(cls, code_object: FunctionType | ModuleType | type) -> str:
        """
        custom lambda reduction needed:
            https://www.pythonpool.com/cant-pickle-local-object/
        custom module reduction needed:
            https://stackoverflow.com/questions/2790828/python-cant-pickle-module-objects-error
        name reduction for function/module/class is not enough because we assume
        cache result can change when function/module/class implementation changes
        """

        try:
            reduction = inspect.getsource(code_object)
        except (TypeError, OSError):
            # cannot access source code of builtins or common libraries
            # but no problem because we assume this code does not change
            reduction = code_object.__name__
        return reduction

    @classmethod
    def reduce_file_objects(cls, _: io.BytesIO | io.BufferedWriter) -> str:
        # Closed file pointers cannot and should not be pickled for cache functionality
        return ""
