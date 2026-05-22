import json
import sqlite3
import sys
from pathlib import Path

import pandas as pd
from rdflib import Graph, Namespace


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from impl import FullQueryEngine, JournalQueryHandler, CategoryQueryHandler

RELATIONAL_DB = ROOT / "relational.db"
SCIMAGO_JSON = ROOT / "data" / "scimago.json"
DOAJ_TTL = ROOT / "doaj.ttl"
GRAPH_ENDPOINT = "http://192.168.78.117:9999/blazegraph/sparql"


def parse_ids(raw):
    return {part.strip() for part in str(raw or "").replace(";", ",").split(",") if part.strip()}


def journal_key(journal):
    return "|".join(sorted(journal.getIds()))


def load_graph_journals():
    schema = Namespace("https://schema.org/")
    rdf = Namespace("http://www.w3.org/1999/02/22-rdf-syntax-ns#")

    graph = Graph()
    graph.parse(DOAJ_TTL, format="turtle")

    rows = []
    for subject in graph.subjects(rdf.type, schema.Periodical):
        ids = parse_ids(graph.value(subject, schema.identifier))
        if not ids:
            continue
        rows.append(
            {
                "key": "|".join(sorted(ids)),
                "ids": ids,
                "license": str(graph.value(subject, schema.license) or ""),
                "apc": str(graph.value(subject, schema.processingFee) or "").lower() in {"true", "1"},
                "title": str(graph.value(subject, schema.title) or ""),
            }
        )
    return rows


def load_scimago_records():
    with open(SCIMAGO_JSON, encoding="utf-8") as file_handle:
        return json.load(file_handle)


def expected_areas_for_identifiers(scimago_records, identifiers):
    identifiers = set(identifiers)
    areas = set()
    for record in scimago_records:
        record_ids = {str(item).strip() for item in record.get("identifiers", []) or []}
        if identifiers & record_ids:
            areas.update(str(area).strip() for area in record.get("areas", []) or [])
    return areas


def sqlite_identifiers_for_category_quartile(category_ids, quartiles):
    conn = sqlite3.connect(RELATIONAL_DB)
    try:
        category_placeholders = ",".join(["?"] * len(category_ids))
        quartile_placeholders = ",".join(["?"] * len(quartiles))
        query = f"""
        SELECT DISTINCT identifiers
        FROM categories
        WHERE category_id IN ({category_placeholders})
          AND quartile IN ({quartile_placeholders})
        """
        df = pd.read_sql_query(query, conn, params=tuple(category_ids) + tuple(quartiles))
        return {str(value).strip() for value in df["identifiers"] if str(value).strip()}
    finally:
        conn.close()


def sqlite_identifiers_for_areas(area_ids):
    conn = sqlite3.connect(RELATIONAL_DB)
    try:
        identifiers = set()
        for area in area_ids:
            query = """
            SELECT DISTINCT identifiers
            FROM categories
            WHERE (areas = ? OR areas LIKE ? OR areas LIKE ? OR areas LIKE ?)
              AND identifiers IS NOT NULL
            """
            df = pd.read_sql_query(
                query,
                conn,
                params=(area, f"{area},%", f"%,{area},%", f"%,{area}"),
            )
            identifiers.update(str(value).strip() for value in df["identifiers"] if str(value).strip())
        return identifiers
    finally:
        conn.close()


def check_entity_areas(engine, scimago_records, entity_id):
    journal = engine.getEntityById(entity_id)
    if journal is None:
        print(f"FAIL getEntityById({entity_id!r}) returned None")
        return

    actual = {area.getIds()[0] for area in journal.getAreas()}
    expected = expected_areas_for_identifiers(scimago_records, journal.getIds())

    if actual == expected:
        print(f"PASS getEntityById({entity_id!r}) areas overlap exactly: {len(actual)}")
    else:
        print(f"FAIL getEntityById({entity_id!r}) areas differ")
        print(f"  extra:   {sorted(actual - expected)}")
        print(f"  missing: {sorted(expected - actual)}")


def check_category_quartile_identifiers(engine, graph_journals, category_ids, quartiles):
    result = engine.getJournalsInCategoriesWithQuartile(category_ids, quartiles)
    actual_ids = set().union(*(journal.getIds() for journal in result)) if result else set()

    wanted = sqlite_identifiers_for_category_quartile(category_ids, quartiles)
    expected_ids = set()
    for graph_journal in graph_journals:
        matching_ids = graph_journal["ids"] & wanted
        if matching_ids:
            expected_ids.update(matching_ids)

    if actual_ids == expected_ids:
        print(
            "PASS getJournalsInCategoriesWithQuartile"
            f" {category_ids}, {quartiles}: {len(result)} journals, {len(actual_ids)} identifiers"
        )
    else:
        print(
            "FAIL getJournalsInCategoriesWithQuartile"
            f" {category_ids}, {quartiles}: {len(result)} journals"
        )
        print(f"  actual identifiers:   {len(actual_ids)}")
        print(f"  expected identifiers: {len(expected_ids)}")
        print(f"  extra:   {sorted(actual_ids - expected_ids)[:10]}")
        print(f"  missing: {sorted(expected_ids - actual_ids)[:10]}")


def check_area_license_journals(engine, graph_journals, area_ids, licenses):
    result = engine.getJournalsInAreasWithLicense(area_ids, licenses)
    actual_keys = {journal_key(journal) for journal in result}

    area_identifiers = sqlite_identifiers_for_areas(area_ids)
    expected_keys = {
        graph_journal["key"]
        for graph_journal in graph_journals
        if graph_journal["license"] in licenses and graph_journal["ids"].issubset(area_identifiers)
    }

    if actual_keys == expected_keys:
        print(
            "PASS getJournalsInAreasWithLicense"
            f" {area_ids}, {licenses}: {len(actual_keys)} journals"
        )
    else:
        print(
            "FAIL getJournalsInAreasWithLicense"
            f" {area_ids}, {licenses}"
        )
        print(f"  actual journals:   {len(actual_keys)}")
        print(f"  expected journals: {len(expected_keys)}")
        print(f"  extra:   {sorted(actual_keys - expected_keys)[:10]}")
        print(f"  missing: {sorted(expected_keys - actual_keys)[:10]}")


def main():
    engine = FullQueryEngine(
        journalQuery=[JournalQueryHandler(GRAPH_ENDPOINT)],
        categoryQuery=[CategoryQueryHandler(str(RELATIONAL_DB))],
    )
    graph_journals = load_graph_journals()
    scimago_records = load_scimago_records()

    print("Professor-style checks")
    check_entity_areas(engine, scimago_records, "2532-8816")

    check_category_quartile_identifiers(engine, graph_journals, {"Oncology"}, {"Q1"})
    check_category_quartile_identifiers(engine, graph_journals, {"Artificial Intelligence"}, {"Q1"})
    check_category_quartile_identifiers(engine, graph_journals, {"Software"}, {"Q1", "Q2"})

    check_area_license_journals(engine, graph_journals, {"Computer Science"}, {"CC BY"})
    check_area_license_journals(engine, graph_journals, {"Medicine"}, {"CC BY"})
    check_area_license_journals(engine, graph_journals, {"Computer Science", "Engineering"}, {"CC BY-SA"})


if __name__ == "__main__":
    main()
