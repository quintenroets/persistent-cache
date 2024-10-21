from persistent_cache.main import decorator
from persistent_cache.reducers.deep_learning import Reducer

cache = decorator.cache(Reducer)
