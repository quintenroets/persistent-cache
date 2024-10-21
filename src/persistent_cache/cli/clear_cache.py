import time
from dataclasses import dataclass
from datetime import datetime, timezone
from functools import cached_property
from typing import Annotated

import cli
import typer
from package_utils.cli import create_entry_point

from persistent_cache.models import Path


@dataclass
class Options:
    max_age: Annotated[
        int | None,
        typer.Option(help="Maximal age of entries to delete"),
    ] = None
    cache_path: Annotated[Path, typer.Option(help="Root of cache directory")] = (
        Path.cache
    )
    verbose: Annotated[bool, typer.Option(help="Show removed entries")] = True

    @cached_property
    def min_mtime_to_clear(self) -> float | None:
        return time.time() - self.max_age * 60 if self.max_age else None


def main(options: Options) -> None:
    """
    Clear cached values.
    """

    def should_remove(path_: Path) -> bool:
        return path_.is_file() and (
            options.min_mtime_to_clear is None
            or path_.mtime > options.min_mtime_to_clear
        )

    with cli.status("Removing.."):
        for path in Options.cache_path.find(should_remove, recurse_on_match=True):
            if options.verbose:
                relative_path = path.relative_to(Options.cache_path)
                timestamp = datetime.fromtimestamp(path.mtime).astimezone(
                    tz=timezone.utc,
                )
                message = f"{relative_path} ({timestamp})"
                cli.console.print(message)
            path.unlink()


entry_point = create_entry_point(main)
