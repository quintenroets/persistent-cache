import functools

from persistent_cache.main import decorator

cache = functools.partial(decorator.cache, deep_learning=True)
