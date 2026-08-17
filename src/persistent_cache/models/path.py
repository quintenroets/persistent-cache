from typing import Self, cast

import superpathlib
from simple_classproperty import classproperty


class Path(superpathlib.Path):
    @classmethod
    @classproperty
    def source_root(cls) -> Self:
        return cls(__file__).parent.parent

    @classmethod
    @classproperty
    def cache(cls) -> Self:
        path = cls.script_assets / cls.source_root.name
        return cast("Self", path)
