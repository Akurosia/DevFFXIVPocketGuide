#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# coding: utf8

import argparse
from pathlib import Path

def run(args: argparse.Namespace)-> None :
    files: list[Path] = sorted(Path(".").rglob("*.md"))
    print(f"There are a total of {len(files)} Files!")
    results: list[Path] = []
    searchterm = args.searchterm if args.case_sensitive else args.searchterm.lower()
    for counter, file in enumerate(files, start=1):
        print(f"Work on file {file}: {counter}/{len(files)}!")
        data = file.read_text(encoding="utf8")
        if not args.case_sensitive:
            data = data.lower()
        if searchterm in data:
            results.append(file)
            print(f"Found your data in {file}")

    print("\n\n")
    for file in results:
        print(f"Found your data in {file}")


if __name__ == "__main__":
    example_usage = ""
    parser = argparse.ArgumentParser(
        description="Recreates the logdata json file",
        epilog=example_usage,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("-c", "--case-sensitive", action='store_true', help="Pay attention to the case")
    parser.add_argument("-s", "--searchterm", help="search term")
    parser.add_argument('deprecated',nargs='?', default=None)
    args: argparse.Namespace = parser.parse_args()

    if not args.searchterm and args.deprecated:
        args.searchterm = args.deprecated
    elif not args.searchterm and not args.deprecated:
        args.searchterm = "112338"
    print(args)
    run(args)
