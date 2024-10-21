# Cache
[![PyPI version](https://badge.fury.io/py/persistent-function-cache.svg)](https://badge.fury.io/py/persistent-function-cache)
![PyPI downloads](https://img.shields.io/pypi/dm/persistent-function-cache)
![Python version](https://img.shields.io/badge/python-3.10+-brightgreen)
![Operating system](https://img.shields.io/badge/os-linux%20%7c%20macOS%20%7c%20windows-brightgreen)
![Coverage](https://img.shields.io/badge/coverage-88%25-brightgreen)

## Usage
Use

```shell
from persistent_cache import cache

@cache
def expensive_function(..):
    ..

to cache the result of a function
```

The cache key for the result is determined by:
* the function signature
* the implementation of the function
* the values of the function arguments
  * custom transformations/reductions can be specified

Advantages compared to existing solutions:
* the cache in invalidated when the behavior of the function changes
* Each cache value is saved to a separate location. Only values that are effectively needed are loaded.
* works with function arguments of any complex data type.
* configurable: custom transformations/reductions can be specified based on the object type.
* 3 custom transformation groups available out-of-the-box:
  * from persistent_cache import cache
  * from persistent_cache.caches.deep_learning import cache
  * from persistent_cache.caches.speedup_deep_learning import cache`

## Installation
```shell
pip install persistent-function-cache
```
