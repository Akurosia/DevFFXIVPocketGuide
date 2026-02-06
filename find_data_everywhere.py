#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# coding: utf8

import glob
import json
import sys
import argparse

def run(args: argparse.Namespace)-> None :
    files: list[str] = glob.glob("**/*.md", recursive=True)
    print(f"There are a total of {len(files)} Files!")
    counter = 0
    results: list[str] = []
    for file in sorted(files):
        counter += 1
        print(f"Work on file {file}: {counter}/{len(files)}!")
        with open(file, "r", encoding="utf8") as f:
            data = f.readlines()
        if not args.case_sensitive:
            args.searchterm = args.searchterm.lower()
            data = str(data).lower()
        if args.searchterm in str(data):
            results.append(file)
            print("Found your data in " + file)

    print("\n\n")
    for file in sorted(results):
        print("Found your data in " + file)


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
