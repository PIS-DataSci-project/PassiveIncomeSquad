#!/usr/bin/env python3
"""
Interactive smoke-test for the (River) BasicQueryEngine implementation.

This script is meant to be a hands-on check where you can type input and
see actual query results printed in the terminal.

Typical usage:
  1) Start Blazegraph and load data if you want journal queries:
     java -server -Xmx1g -jar blazegraph.jar
     (then load doaj.ttl into the Blazegraph namespace)
  2) Run this script:
     python river_engine_live_test.py --sparql http://127.0.0.1:9999/blazegraph/sparql \
         --sqlite relational.db

If you skip --sparql, journal queries will be disabled, but category/area
queries (SQLite) will still work.
"""
from __future__ import annotations

import argparse
from typing import Iterable, Optional

from impl import (
    BasicQueryEngine,
    JournalQueryHandler,
    CategoryQueryHandler,
    Journal,
    Category,
    Area,
)


def _format_journal(journal: Journal) -> str:
    return (
        "Journal(\n"
        f"  ids={journal.getIds()},\n"
        f"  title={journal.getTitle()!r},\n"
        f"  publisher={journal.getPublisher()!r},\n"
        f"  language={journal.getLanguage()},\n"
        f"  license={journal.getLicense()!r},\n"
        f"  apc={journal.hasAPC()},\n"
        f"  seal={journal.hasDOAJSeal()},\n"
        f"  categories={[c.getIds() for c in journal.getCategories()]},\n"
        f"  areas={[a.getIds() for a in journal.getAreas()]},\n"
        ")"
    )


def _format_category(category: Category) -> str:
    return f"Category(ids={category.getIds()}, quartile={category.getQuartile()!r})"


def _format_area(area: Area) -> str:
    return f"Area(ids={area.getIds()})"


def _print_list(label: str, items: Iterable[str]) -> None:
    print(f"\n{label}")
    for index, item in enumerate(items, start=1):
        print(f"  {index}. {item}")


def _print_entities(entities: Iterable[object]) -> None:
    formatted = []
    for entity in entities:
        if isinstance(entity, Journal):
            formatted.append(_format_journal(entity))
        elif isinstance(entity, Category):
            formatted.append(_format_category(entity))
        elif isinstance(entity, Area):
            formatted.append(_format_area(entity))
        else:
            formatted.append(repr(entity))
    if not formatted:
        print("\n(no results)")
        return
    _print_list("Results:", formatted)


def _parse_csv(text: str) -> list[str]:
    return [item.strip() for item in text.split(",") if item.strip()]


def _add_handlers(engine: BasicQueryEngine, sparql_url: Optional[str], sqlite_path: str) -> None:
    if sparql_url:
        journal_handler = JournalQueryHandler(sparql_url)
        engine.addJournalHandler(journal_handler)
    else:
        print("[info] No --sparql provided, journal queries will be skipped.")

    category_handler = CategoryQueryHandler(sqlite_path)
    engine.addCategoryHandler(category_handler)


def _menu() -> None:
    print(
        "\nChoose a query:\n"
        "  1) getEntityById (ISSN/EISSN or category_id)\n"
        "  2) getJournalsWithTitle\n"
        "  3) getJournalsPublishedBy\n"
        "  4) getJournalsWithLicense (comma-separated)\n"
        "  5) getJournalsWithAPC\n"
        "  6) getJournalsWithDOAJSeal\n"
        "  7) getCategoriesWithQuartile (comma-separated)\n"
        "  8) getCategoriesAssignedToAreas (comma-separated)\n"
        "  9) getAreasAssignedToCategories (comma-separated)\n"
        "  a) getAllCategories\n"
        "  b) getAllAreas\n"
        "  q) quit\n"
    )


def run_cli(sparql_url: Optional[str], sqlite_path: str) -> None:
    engine = BasicQueryEngine()
    _add_handlers(engine, sparql_url, sqlite_path)

    while True:
        _menu()
        choice = input("Enter choice: ").strip().lower()
        if choice == "q":
            print("Bye!")
            return

        if choice == "1":
            entity_id = input("Enter ISSN/EISSN or category_id: ").strip()
            result = engine.getEntityById(entity_id)
            if result is None:
                print("\n(no results)")
            else:
                _print_entities([result])
        elif choice == "2":
            title = input("Enter partial journal title: ").strip()
            _print_entities(engine.getJournalsWithTitle(title))
        elif choice == "3":
            publisher = input("Enter partial publisher name: ").strip()
            _print_entities(engine.getJournalsPublishedBy(publisher))
        elif choice == "4":
            licenses = input("Enter licenses (comma-separated): ").strip()
            _print_entities(engine.getJournalsWithLicense(set(_parse_csv(licenses))))
        elif choice == "5":
            _print_entities(engine.getJournalsWithAPC())
        elif choice == "6":
            _print_entities(engine.getJournalsWithDOAJSeal())
        elif choice == "7":
            quartiles = input("Enter quartiles (comma-separated, e.g. Q1,Q2): ").strip()
            _print_entities(engine.getCategoriesWithQuartile(set(_parse_csv(quartiles))))
        elif choice == "8":
            areas = input("Enter areas (comma-separated): ").strip()
            _print_entities(engine.getCategoriesAssignedToAreas(set(_parse_csv(areas))))
        elif choice == "9":
            category_ids = input("Enter category IDs (comma-separated): ").strip()
            _print_entities(engine.getAreasAssignedToCategories(set(_parse_csv(category_ids))))
        elif choice == "a":
            _print_entities(engine.getAllCategories())
        elif choice == "b":
            _print_entities(engine.getAllAreas())
        else:
            print("Unknown option, try again.")


def main() -> None:
    parser = argparse.ArgumentParser(description="Interactive test for BasicQueryEngine.")
    parser.add_argument(
        "--sparql",
        dest="sparql_url",
        help="SPARQL endpoint URL (e.g. http://127.0.0.1:9999/blazegraph/sparql)",
    )
    parser.add_argument(
        "--sqlite",
        dest="sqlite_path",
        default="relational.db",
        help="Path to the SQLite database (default: relational.db)",
    )
    args = parser.parse_args()

    run_cli(args.sparql_url, args.sqlite_path)


if __name__ == "__main__":
    main()



