from persistent_cache.main import decorator
from persistent_cache.reducers.base import Reducer

cache = decorator.cache(Reducer)
