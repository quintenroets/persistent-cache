import functools

from persistent_cache.main import decorator

cache = functools.partial(decorator.cache, speedup_deep_learning=True)
