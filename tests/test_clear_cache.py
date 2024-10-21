from package_dev_utils.tests.args import cli_args

from persistent_cache.cli.clear_cache import entry_point


def test_entry_point() -> None:
    with cli_args("--max-age", 0):
        entry_point()
