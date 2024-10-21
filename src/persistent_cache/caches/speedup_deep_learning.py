from persistent_cache.main import decorator
from persistent_cache.reducers.speedup_deep_learning import Reducer

cache = decorator.cache(Reducer)
