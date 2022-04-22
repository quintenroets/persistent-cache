import argparse
import sys
import time

import cli

from .path import Path


def clear(args):
    min_mtime_to_clear = time.time() - int(args.max_age) * 60 if args.max_age else None

    def remove_entry(path: Path):
        return (
            min_mtime_to_clear is not None
            and path.mtime > min_mtime_to_clear
            and path.is_file()
        )

    with cli.status("Removing.."):
        for path in Path.cache.find(remove_entry, recurse_on_match=True):
            if args.verbose:
                pprint(
                    f"{path.relative_to(Path.cache)} ({datetime.fromtimestamp(path.mtime)})"
                )
            path.unlink()


def main():
    parser = argparse.ArgumentParser(description="Clear cached values")

    parser.add_argument(
        "--max-age",
        default=None,
        help=f"Maximal age of cache entries to delete (minutes)",
    )
    parser.add_argument("--verbose", default=True, help=f"Show removed entries")
    args = parser.parse_args()
    clear(args)


if __name__ == "__main__":
    main()
