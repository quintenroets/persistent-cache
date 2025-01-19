from collections.abc import Iterator
from unittest.mock import PropertyMock, patch

import pytest

from persistent_cache.models import Path


@pytest.fixture(autouse=True, scope="session")
def mocked_download_assets() -> Iterator[None]:
    path = Path.tempdir()
    mocked_path = PropertyMock(return_value=path)
    mock = patch.object(Path, "cache", new_callable=mocked_path)
    with mock, path:
        yield
