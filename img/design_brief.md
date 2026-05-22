# Design Brief — PassiveIncomeSquad Data Science Project

## Table of Contents

1. [Project Overview](#1-project-overview)
2. [Data Sources](#2-data-sources)
3. [Languages, Tools & Libraries](#3-languages-tools--libraries)
4. [Data Model](#4-data-model)
5. [Software Architecture](#5-software-architecture)
6. [Class Descriptions](#6-class-descriptions)
7. [Methodology](#7-methodology)
8. [Workflow](#8-workflow)
9. [Query Reference](#9-query-reference)
10. [Testing](#10-testing)
11. [Known Issues & Limitations](#11-known-issues--limitations)
12. [Potential Future Improvements](#12-potential-future-improvements)

---

## 1. Project Overview

This software was developed as the final project for the **Data Science** course (A.Y. 2024/25) taught by [Silvio Peroni](https://www.unibo.it/sitoweb/silvio.peroni) within the **Digital Humanities and Digital Knowledge** Master's degree at the **University of Bologna**. The project was built by the team *PassiveIncomeSquad*: Claudia Romanello, Fahmida Islam, QingHao Chen, and Polina Khromtcova.

The core objective is to build a **multi-source data integration system** that:

- Ingests academic journal metadata from two heterogeneous sources (CSV and JSON);
- Loads that data into two structurally different databases — a **graph database** (Blazegraph, accessed via SPARQL) and a **relational database** (SQLite);
- Exposes a unified, object-oriented **query layer** that abstracts over both backends;
- Supports **mashup queries** that combine data across both databases to answer complex questions that neither source alone could answer.

The system is entirely written in Python and follows a handler-based architecture derived from a formal UML class diagram provided as part of the course specification.

The real-world domain is **open-access academic publishing**: the software lets users query which journals belong to which subject categories and areas, what their publishing conditions are (APC, DOAJ Seal, license type), and who publishes them — all from a single programmatic interface.

---

## 2. Data Sources

### 2.1 DOAJ — Directory of Open Access Journals (`data/doaj.csv`)

The **DOAJ** is an online index that curates open-access peer-reviewed journals. The dataset is provided as a CSV file and contains one row per journal. The fields used by this software are:

| CSV Column | Description |
|---|---|
| `Journal title` | The full title of the journal |
| `Journal ISSN (print version)` | Print ISSN (may be empty) |
| `Journal EISSN (online version)` | Electronic ISSN (may be empty) |
| `Languages in which the journal accepts manuscripts` | Comma-separated list of languages |
| `Publisher` | Name of the publishing organization |
| `Journal license` | Open-access license type (e.g., CC BY, CC BY-NC) |
| `DOAJ Seal` | Whether the journal holds the DOAJ Seal of quality (`Yes`/`No`) |
| `APC` | Whether the journal charges Article Processing Charges (`Yes`/`No`) |

Each journal is identified by its ISSN and/or EISSN, which are stored together as a semicolon-separated string in the graph database (e.g., `"1234-5678; 8765-4321"`).

### 2.2 Scimago Journal Rankings (`data/scimago.json`)

The **Scimago** dataset is provided as a JSON file and contains subject classification metadata for academic journals. Each record in the JSON array corresponds to a set of journal identifiers linked to one or more subject categories and broad subject areas.

The JSON structure is:
```json
[
  {
    "identifiers": ["1234-5678", "8765-4321"],
    "categories": [
      { "id": "Oncology", "quartile": "Q1", "areas": ["Medicine"] }
    ],
    "areas": ["Medicine"]
  }
]
```

The `quartile` field ranks a journal's category on a scale of Q1 (top 25%) to Q4 (bottom 25%) based on citation impact within that subject area. The 27 recognized broad subject areas are standard Scimago classifications (e.g., "Computer Science", "Medicine", "Engineering").

---

## 3. Languages, Tools & Libraries

### Language

- **Python 3** — the entire project is implemented in Python, using object-oriented design with class inheritance, type hints, and no external frameworks beyond standard data and database libraries.

### Core Libraries

| Library | Version requirement | Role |
|---|---|---|
| `pandas` | ≥ 1.3 | Reading CSV/JSON, in-memory DataFrame manipulation, SQL query result wrapping |
| `rdflib` | ≥ 6.0 | Building RDF graphs from CSV data, serializing to Turtle (`.ttl`) |
| `rdflib.plugins.stores.sparqlstore` | (bundled with rdflib) | Connecting to Blazegraph's SPARQL Update endpoint to upload triples |
| `requests` | ≥ 2.25 | Sending HTTP GET requests to the SPARQL endpoint for querying |
| `sqlite3` | (Python standard library) | Creating and querying the local relational database |
| `json` | (Python standard library) | Parsing the Scimago JSON file |
| `unittest` | (Python standard library) | Running the test suite in `test.py` |

### External Services

| Service | Role |
|---|---|
| **Blazegraph** | A graph (triple store) database accessed via a SPARQL 1.1 endpoint. Journal data is stored here as RDF triples using `schema.org` vocabulary. Blazegraph must be running locally or on a network host before the upload and query steps. |
| **SQLite** | A file-based relational database (`.db` file). Category and area data from Scimago is stored here in a `categories` table. No server process is required. |

### RDF Vocabulary

All RDF triples use **schema.org** URIs as predicates, with `https://github.com/PassiveIncomeSquad/PIS-DataSci-project` as the base URI for journal subjects:

| schema.org predicate | Maps to |
|---|---|
| `schema:Periodical` | RDF type for journals |
| `schema:title` | Journal title |
| `schema:identifier` | Combined ISSN/EISSN string |
| `schema:inLanguage` | Accepted manuscript languages |
| `schema:publishedBy` | Publisher name |
| `schema:license` | License string |
| `schema:award` | DOAJ Seal (boolean) |
| `schema:processingFee` | APC (boolean) |

---

## 4. Data Model

The domain is modelled as a hierarchy of identifiable entities, derived directly from the UML class diagram specified in the course project brief.

### `IdentifiableEntity` (abstract base)

Every domain object has one or more string identifiers and exposes `getIds() → list[str]`.

### `Journal` (subclass of `IdentifiableEntity`)

Represents a single academic journal. Identified by its ISSN and/or EISSN.

Attributes: `title`, `languages` (list), `publisher` (optional), `seal` (boolean), `license`, `apc` (boolean), `categories` (list of `Category`), `areas` (list of `Area`).

Key methods: `getTitle()`, `getLanguages()`, `getPublisher()`, `hasPublisher()`, `hasDOAJSeal()`, `getLicense()`, `hasAPC()`, `getCategories()`, `hasCategory()`, `getAreas()`, `hasArea()`.

### `Category` (subclass of `IdentifiableEntity`)

Represents a Scimago subject category (e.g., "Oncology", "Machine Learning"). Identified by the category name string. Carries an optional `quartile` field (`Q1`–`Q4` or `None`).

Key methods: `getQuartile()`.

### `Area` (subclass of `IdentifiableEntity`)

Represents one of the 27 broad Scimago subject areas (e.g., "Medicine", "Computer Science"). Identified by the area name. Has no additional attributes beyond the inherited identifiers.

### Relationships

- A `Journal` can belong to zero or more `Category` objects (`hasCategory`, 0..*).
- A `Journal` can be associated with zero or more `Area` objects (`hasArea`, 0..*).
- A `Category` belongs to exactly one `Area` (encoded in the Scimago JSON's `areas` field per category).
- The link between a journal and its categories/areas is stored in SQLite (via the shared ISSN/EISSN identifier), not in the graph database.

---

## 5. Software Architecture

The software is organized into three conceptual layers:

```
┌─────────────────────────────────────────────────────────┐
│                    QUERY ENGINE LAYER                   │
│         BasicQueryEngine / FullQueryEngine              │
│  Combines DataFrames from both databases into           │
│  domain objects (Journal, Category, Area)               │
└────────────────────────┬────────────────────────────────┘
                         │
         ┌───────────────┴───────────────┐
         ▼                               ▼
┌─────────────────┐             ┌─────────────────────┐
│   QUERY HANDLER │             │    QUERY HANDLER     │
│     LAYER       │             │       LAYER          │
│ JournalQuery-   │             │ CategoryQuery-       │
│ Handler         │             │ Handler              │
│ (returns        │             │ (returns             │
│  DataFrames     │             │  DataFrames          │
│  from SPARQL)   │             │  from SQLite)        │
└────────┬────────┘             └────────┬─────────────┘
         │                               │
         ▼                               ▼
┌─────────────────┐             ┌─────────────────────┐
│  GRAPH DATABASE │             │  RELATIONAL DATABASE │
│   (Blazegraph)  │             │     (SQLite .db)     │
│   RDF triples   │             │  `categories` table  │
│   SPARQL 1.1    │             │                      │
└────────┬────────┘             └────────┬─────────────┘
         ▲                               ▲
         │                               │
┌─────────────────┐             ┌─────────────────────┐
│ UPLOAD HANDLER  │             │   UPLOAD HANDLER     │
│     LAYER       │             │       LAYER          │
│ JournalUpload-  │             │ CategoryUpload-      │
│ Handler         │             │ Handler              │
│ (CSV → RDF →   │             │ (JSON → SQLite)      │
│  Blazegraph)    │             │                      │
└────────┬────────┘             └────────┬─────────────┘
         │                               │
         ▼                               ▼
    doaj.csv                      scimago.json
```

All classes share a common `Handler` base that manages the database path or URL (`dbPathOrUrl`). Upload handlers write data; query handlers read it. The engine layer sits above both and exposes a single unified API.

---

## 6. Class Descriptions

### `Handler` (base class)

Holds a single `dbPathOrUrl: str` attribute. Provides `getDbPathOrUrl()` and `setDbPathOrUrl(path)` (which validates that the string is non-empty and returns a boolean). Both upload and query handlers inherit from this class.

### `UploadHandler(Handler)`

Abstract intermediate class. Defines the interface `pushDataToDb(path: str) → bool` which subclasses must implement.

### `JournalUploadHandler(UploadHandler)`

Reads `doaj.csv` and uploads journal data to Blazegraph.

- `createGraph(path) → rdflib.Graph`: Reads the CSV with pandas, normalizes column names, converts `DOAJ Seal` and `APC` columns to boolean, and builds an RDF graph where each journal becomes a `schema:Periodical` subject with triples for all its attributes. Each journal is assigned a local URI of the form `https://github.com/.../journal-{idx}`.
- `pushDataToDb(path) → bool`: Calls `createGraph`, opens the SPARQL Update store, and uploads all triples one by one.
- `serializeToTTL(csv_path, output_path) → str`: Saves the RDF graph to a Turtle (`.ttl`) file for inspection or archival. Output path defaults to the same directory as the CSV with a `.ttl` extension.

### `CategoryUploadHandler(UploadHandler)`

Reads `scimago.json` and loads category/area data into SQLite.

- `pushDataToDb(path) → bool`: Opens the JSON, creates (if not exists) a `categories` table with columns `(category_id TEXT, quartile TEXT, identifiers TEXT, areas TEXT)` and a composite primary key on all four columns (enforcing `INSERT OR IGNORE` deduplication). Iterates all records → all categories → all identifiers, flattening the nested structure into one row per (identifier, category, quartile, areas) combination. Returns `True` on success.

The SQLite table schema:
```sql
CREATE TABLE IF NOT EXISTS categories (
    category_id TEXT,
    quartile    TEXT,
    identifiers TEXT,
    areas       TEXT,
    PRIMARY KEY (category_id, quartile, identifiers, areas)
)
```

### `QueryHandler(Handler)`

Abstract base for query handlers. Defines `getById(entity_id: str) → pd.DataFrame` which subclasses must implement.

### `JournalQueryHandler(QueryHandler)`

Issues SPARQL queries against the Blazegraph endpoint. All query methods return `pd.DataFrame` instances (empty DataFrame on no results or error).

Internal helpers:
- `_escape_literal(value)`: Escapes backslashes and double quotes to prevent SPARQL injection.
- `_execute_sparql_query(sparql_query)`: Sends an HTTP GET to the endpoint with `format=json`, parses the SPARQL JSON response, and converts `bindings` into a DataFrame.

Public query methods:

| Method | Description |
|---|---|
| `getById(entity_id)` | Finds journals whose `schema:identifier` contains the given ISSN/EISSN string |
| `getAllJournals()` | Retrieves all `schema:Periodical` subjects |
| `getJournalsWithTitle(partial_title)` | Case-insensitive partial title match using `CONTAINS(LCASE(...))` |
| `getJournalsPublishedBy(partial_publisher)` | Case-insensitive partial publisher match |
| `getJournalsWithLicense(licenses)` | Exact match against a set of license strings, joined with `||` in FILTER |
| `getJournalsWithAPC()` | Journals where `schema:processingFee = true` |
| `getJournalsWithDOAJSeal()` | Journals where `schema:award = true` |

### `CategoryQueryHandler(QueryHandler)`

Issues SQL queries against the SQLite `categories` table. All query methods return `pd.DataFrame` instances.

Public query methods:

| Method | Description |
|---|---|
| `getById(category_id)` | Exact match on `category_id` column |
| `getAllCategories()` | All rows, grouped to one row per `category_id` with `MIN(quartile)` |
| `getAllAreas()` | Parses the `areas` column using a known set of the 27 Scimago area names (matching longest first to avoid substring collisions), returns distinct area names |
| `getCategoriesWithQuartile(quartiles)` | Filters by a set of quartile strings |
| `getCategoriesAssignedToAreas(area_ids)` | Matches area name at start, middle, or end of comma-separated `areas` string |
| `getAreasAssignedToCategories(category_ids)` | Returns distinct area names for a set of category IDs |
| `getCategoriesByJournalId(journal_id)` | Returns category rows where `identifiers = journal_id` |
| `getAreasByJournalId(journal_id)` | Returns area names for rows where `identifiers = journal_id`, parsed using the known-areas set |

### `BasicQueryEngine`

Holds a list of `JournalQueryHandler` objects (`self.journalQuery`) and a list of `CategoryQueryHandler` objects (`self.categoryQuery`). Supports multiple handlers per type so that multiple database endpoints can be queried and results merged.

Handler management methods: `addJournalHandler()`, `addCategoryHandler()`, `cleanJournalHandlers()`, `cleanCategoryHandlers()`.

Journal query methods (`getAllJournals`, `getJournalsWithTitle`, `getJournalsPublishedBy`, `getJournalsWithLicense`, `getJournalsWithAPC`, `getJournalsWithDOAJSeal`): Each calls the same method on all registered `JournalQueryHandler` objects, concatenates and deduplicates the resulting DataFrames, and converts each row into a `Journal` object (with boolean coercion for `seal` and `apc` fields).

Category/Area query methods (`getAllCategories`, `getAllAreas`, `getCategoriesWithQuartile`, `getCategoriesAssignedToAreas`, `getAreasAssignedToCategories`): Same pattern — call all `CategoryQueryHandler` objects, merge DataFrames, convert rows into `Category` or `Area` objects.

`getEntityById(entity_id)`: Searches first in all journal handlers (by ISSN/EISSN), then in all category handlers (by category name). Returns the appropriate domain object (`Journal`, `Category`, or `Area`) or `None`. When a `Journal` is found, it automatically fetches its linked `Category` and `Area` objects from the SQLite database using `getCategoriesByJournalId` and `getAreasByJournalId`.

### `FullQueryEngine(BasicQueryEngine)`

Extends `BasicQueryEngine` with three **mashup query** methods that combine the relational and graph databases. The core pattern is:

1. Query SQLite to find journal identifiers (ISSN/EISSN) that satisfy the category/area/quartile constraints.
2. Query Blazegraph to find the full journal records for those identifiers.
3. Return matched journals as `Journal` objects.

Internal helpers:
- `_coerce_bool(x)`: Normalizes boolean values from various formats (`True`, `"true"`, `1`, `"yes"`, etc.).
- `_parse_list_field(raw)`: Splits a string field (ISSN/EISSN, languages) using `;` or `,` as delimiters.
- `_add_identifiers_from_categories_df(df, identifiers)`: Extracts all identifier strings from a categories DataFrame into a set.
- `_add_journals_matching_identifiers_from_df(df, wanted_identifiers, journal_map)`: Scans a journals DataFrame and adds rows whose identifiers intersect with a wanted set into a deduplication map keyed by sorted identifier tuple.

Mashup methods:

| Method | Databases combined | Logic |
|---|---|---|
| `getJournalsInCategoriesWithQuartile(category_ids, quartiles)` | SQLite + Blazegraph | Finds ISSN/EISSNs from SQLite for journals in the given categories at the given quartiles; retrieves those journals from Blazegraph |
| `getJournalsInAreasWithLicense(area_ids, licenses)` | SQLite + Blazegraph | Finds identifiers from SQLite for journals in the given areas; retrieves from Blazegraph only those journals also matching the license filter |
| `getJournalsInAreasAndCategoriesWithQuartile(area_ids, category_ids, quartiles)` | SQLite + Blazegraph | Finds categories that both belong to the given areas AND are in the given `category_ids` set, then queries SQLite for identifiers at the given quartiles, then fetches from Blazegraph |
| `getDiamondJournalsInAreasAndCategoriesWithQuartile(area_ids, category_ids, quartiles)` | SQLite + Blazegraph | Same as above, then filters the result to only journals where `hasAPC() == False` (Diamond Open Access) |

---

## 7. Methodology

### Object-Oriented Design from UML

The class hierarchy is derived directly from UML diagrams provided in the course specification. The design enforces a strict separation of concerns:

- **Entities** model the domain (journals, categories, areas).
- **Upload handlers** are responsible only for writing data to a database.
- **Query handlers** are responsible only for reading data and returning raw DataFrames.
- **Query engines** are responsible only for orchestrating handlers and translating DataFrames into domain objects.

This separation means that each class has a single responsibility and can be replaced or extended independently — for example, a different graph database could be supported by writing a new `JournalQueryHandler` subclass without changing any other code.

### Two-Database Strategy

The split between the graph database and the relational database is intentional and reflects the nature of the data:

- Journal metadata (title, publisher, license, seal, APC) is a set of properties about a named entity — a natural fit for **RDF triples** and a graph store. Each journal is a subject node; each property is a predicate-object pair. This also makes the data interoperable with Linked Open Data.
- Category and area classifications are tabular and relational — a many-to-many relationship between identifiers and categories, each row having a quartile and an area. **SQLite** handles this efficiently and without requiring a running server.

### Identifier Linking

The bridge between the two databases is the ISSN/EISSN identifier. The graph database stores the combined identifier string; the relational database stores individual ISSN values in the `identifiers` column. Mashup queries retrieve ISSN/EISSN values from SQLite and use them to filter results from the SPARQL endpoint (or vice versa).

### Boolean Normalization

The DOAJ CSV stores `Yes`/`No` strings for `DOAJ Seal` and `APC`. These are converted to `True`/`False` Python booleans using vectorized pandas operations during upload, and stored in the RDF graph as `xsd:boolean` typed literals. On the query side, SPARQL returns boolean values as the strings `"true"` or `"false"`, which are coerced back to Python `bool` values by the query engine.

### Deduplication

Each query method that merges DataFrames from multiple handlers calls `drop_duplicates()` before building domain objects. Within mashup queries, a dictionary keyed by a stable identifier tuple (`"|".join(sorted(ids))`) prevents the same journal from appearing twice even if matched by different identifiers from SQLite.

---

## 8. Workflow

The intended execution sequence is as follows:

### Step 1 — Upload journal data to Blazegraph
```python
jou = JournalUploadHandler()
jou.setDbPathOrUrl("http://<host>:9999/blazegraph/sparql")
jou.pushDataToDb("data/doaj.csv")
# Optionally serialize to inspect:
jou.serializeToTTL("data/doaj.csv", "doaj.ttl")
```

Blazegraph must already be running. The handler reads the CSV, builds an RDF graph in memory (~17,000 journals from the full DOAJ dataset), and uploads each triple to the SPARQL Update endpoint. A serialized `.ttl` file can be inspected to verify the RDF output before uploading.

### Step 2 — Upload category data to SQLite
```python
cat = CategoryUploadHandler()
cat.setDbPathOrUrl("relational.db")
cat.pushDataToDb("data/scimago.json")
```

This creates (or reuses) `relational.db` in the working directory. The `categories` table is created if it does not exist. Records from the JSON are inserted with `INSERT OR IGNORE` to allow re-running without duplication.

### Step 3 — Create query handlers
```python
jou_qh = JournalQueryHandler()
jou_qh.setDbPathOrUrl("http://<host>:9999/blazegraph/sparql")

cat_qh = CategoryQueryHandler()
cat_qh.setDbPathOrUrl("relational.db")
```

### Step 4 — Create the query engine and register handlers
```python
engine = FullQueryEngine()
engine.addJournalHandler(jou_qh)
engine.addCategoryHandler(cat_qh)
```

Multiple handlers of either type can be added; the engine queries all of them and merges results.

### Step 5 — Query
```python
# Single-source queries (BasicQueryEngine methods)
journals = engine.getAllJournals()
journals = engine.getJournalsWithTitle("ecology")
journals = engine.getJournalsPublishedBy("Elsevier")
journals = engine.getJournalsWithLicense({"CC BY", "CC BY-NC"})
journals = engine.getJournalsWithAPC()
journals = engine.getJournalsWithDOAJSeal()
entity   = engine.getEntityById("0000-0000")

categories = engine.getAllCategories()
areas      = engine.getAllAreas()
categories = engine.getCategoriesWithQuartile({"Q1", "Q2"})
categories = engine.getCategoriesAssignedToAreas({"Medicine"})
areas      = engine.getAreasAssignedToCategories({"Oncology"})

# Cross-database mashup queries (FullQueryEngine methods)
journals = engine.getJournalsInCategoriesWithQuartile({"Oncology"}, {"Q1"})
journals = engine.getJournalsInAreasWithLicense({"Medicine"}, {"CC BY"})
journals = engine.getJournalsInAreasAndCategoriesWithQuartile(
               {"Medicine"}, {"Oncology"}, {"Q1", "Q2"})
journals = engine.getDiamondJournalsInAreasAndCategoriesWithQuartile(
               {"Medicine"}, {"Oncology"}, {"Q1"})
```

All engine methods return lists of domain objects (`Journal`, `Category`, or `Area`). Each object exposes getter methods (`getTitle()`, `getIds()`, `getQuartile()`, etc.) that the calling code can use without knowing anything about the underlying database.

---

## 9. Query Reference

### Journal fields returned by all `Journal` objects

| Getter | Return type | Source |
|---|---|---|
| `getIds()` | `list[str]` | ISSN and/or EISSN |
| `getTitle()` | `str` | DOAJ CSV |
| `getLanguages()` | `list[str]` | DOAJ CSV |
| `getPublisher()` | `str` | DOAJ CSV |
| `hasPublisher(name)` | `bool` | DOAJ CSV |
| `hasDOAJSeal()` | `bool` | DOAJ CSV |
| `getLicense()` | `str` | DOAJ CSV |
| `hasAPC()` | `bool` | DOAJ CSV |
| `getCategories()` | `list[Category]` | Scimago JSON via SQLite |
| `hasCategory(category)` | `bool` | Scimago JSON via SQLite |
| `getAreas()` | `list[Area]` | Scimago JSON via SQLite |
| `hasArea(area)` | `bool` | Scimago JSON via SQLite |

### Category fields

| Getter | Return type | Source |
|---|---|---|
| `getIds()` | `list[str]` | Scimago category name |
| `getQuartile()` | `str or None` | Scimago JSON |

### Area fields

| Getter | Return type | Source |
|---|---|---|
| `getIds()` | `list[str]` | Scimago area name |

---

## 10. Testing

The project includes a formal test suite in `test.py` using Python's `unittest` framework (originally authored as part of the course specification by Silvio Peroni). Tests are organized into five test cases:

| Test | What it checks |
|---|---|
| `test_01_JournalUploadHandler` | `setDbPathOrUrl` returns `True`, `getDbPathOrUrl` returns the set path, `pushDataToDb` returns `True` |
| `test_02_CategoryUploadHandler` | Same pattern for the relational upload handler |
| `test_03_JournalQueryHandler` | All SPARQL query methods return `pd.DataFrame` instances |
| `test_04_ProcessDataQueryHandler` | All SQLite query methods return `pd.DataFrame` instances |
| `test_05_FullQueryEngine` | All engine methods return lists of the correct domain object types; handler management methods return booleans; `getEntityById` on a non-existent ID returns `None` |

An extended test and debugging suite lives in the `tests/` directory and includes:
- `testing_errors.py` — checks specific field values and types on returned objects
- `test_with_expectations.py`, `verify_expected.py` — cross-checks query results against expected values
- `inspect_qh.py`, `testing_jqh.py`, `testing_cqh.py` — targeted handler-level debugging
- `sim_mashup.py`, `sim_mashup_test4.py` — simulates the full mashup query workflow
- `compare_db_json.py`, `count_data.py` — data consistency checks between source files and databases

Running the main test suite requires a live Blazegraph instance; the SPARQL endpoint URL must be updated in `test.py` (`self.graph`) to match the local or network address.

---

## 11. Known Issues & Limitations

1. **`CategoryUploadHandler` skips entries with a null quartile** — `if not (category_id and quartile): continue` silently drops valid category entries that have no quartile assigned, causing data loss relative to the Scimago source.

2. **`JournalQueryHandler.getJournalsWithLicense` type annotation is wrong** — The method signature declares `licenses: str` but the body iterates over the parameter as a collection. Passing a plain string would iterate over individual characters.

3. **`Journal` has both `getLicence()` and `getLicense()`** — Both methods exist and return the same value. `getLicence()` is a British-spelling duplicate and causes ambiguity.

4. **`CategoryQueryHandler.getAllCategories` collapses multi-quartile categories** — Uses `MIN(quartile) GROUP BY category_id`, so a category ranked in both Q1 and Q2 becomes a single Q1 entry.

5. **`getCategoriesAssignedToAreas` in `Handlers.py` uses `LIKE '%area%'`** — This produces false positive matches: searching for "Chemistry" would also return rows whose area string contains "Biochemistry, Genetics and Molecular Biology".

6. **`FullQueryEngine.getJournalsInCategoriesWithQuartile` mutates returned Journal objects** — After building the journal map it filters `journal.identifiers` in-place, permanently modifying the objects.

7. **`QueryEngine.py` uses set literals for `identifiers`** — `Category(identifiers={row["category_id"]}, ...)` passes a `set` where a `list` is expected throughout the rest of the codebase.

8. **Blazegraph dependency** — The graph database side of the system requires a running Blazegraph instance with a correctly configured SPARQL endpoint URL. There is no fallback or mock mode for offline use.

9. **Large upload is slow** — Triples are uploaded one by one to Blazegraph inside a loop. For the full DOAJ dataset this results in tens of thousands of individual `store.add()` calls, which is significantly slower than a bulk upload or SPARQL INSERT DATA statement.

---

## 12. Potential Future Improvements

### Architecture

- **Bulk RDF upload**: Replace the per-triple `store.add()` loop with a single SPARQL `INSERT DATA` statement or upload the serialized `.ttl` file directly to Blazegraph's REST API. This would reduce upload time from minutes to seconds for the full dataset.
- **Abstract database interface**: Introduce a formal interface (Python `Protocol` or abstract base class) for the query handlers so that alternative backends (e.g., PostgreSQL, another triple store) can be plugged in without changing the engine layer.
- **Configuration file**: Externalize the database path/URL, data file paths, and other runtime parameters into a configuration file (YAML or TOML) instead of hardcoding them in scripts.

### Data Quality

- **Fix quartile-null data loss**: Change the skip condition in `CategoryUploadHandler` from `if not (category_id and quartile)` to `if not category_id` so that entries without a quartile are still persisted.
- **Canonical `getLicense()` method**: Remove `getLicence()` and standardize all call sites to `getLicense()`.
- **Stricter area matching in `Handlers.py`**: Replace `LIKE '%area%'` in `getCategoriesAssignedToAreas` with the boundary-aware matching already implemented in `impl.py` (matching at start, middle with comma delimiters, and end of string).
- **Consistent identifier storage**: Normalize whether identifiers are stored as single values or semicolon-joined strings across SQLite and the graph database so that join logic does not require special parsing on every query.

### Query Capabilities

- **Full-text search on journals**: Add a SPARQL-based free-text search across title and publisher using Blazegraph's built-in Lucene search service.
- **Journal-to-category cross-lookup from the graph side**: Currently, the link from journals to categories only works from the SQLite side. Adding the category/quartile data to the graph database as well would enable fully graph-native queries.
- **Pagination support**: Add `limit`/`offset` parameters to the `getAllJournals()` and similar methods to support working with large result sets without loading everything into memory.
- **Aggregation queries**: Expose methods such as "count journals per license type" or "count journals per quartile" that are currently only possible by loading all results and post-processing in Python.

### Testing & Reliability

- **Mock database layer for offline testing**: Create in-memory SQLite and mock SPARQL responses so that the test suite can run without a live Blazegraph instance.
- **Property-based testing**: Use a library like `hypothesis` to generate edge-case inputs (empty strings, special characters in ISSNs, journals with no categories) and verify that all methods handle them gracefully.
- **Type checking**: Add `mypy` to the CI workflow to catch type annotation mismatches (such as the `licenses: str` / set mismatch in `JournalQueryHandler`) before they reach runtime.
- **Continuous integration**: Add a GitHub Actions workflow that runs the test suite (at minimum the offline-compatible parts) on every pull request.

### Usability

- **Command-line interface**: Expose common queries as a CLI using `argparse` or `click`, allowing non-programmer users to run queries without editing Python scripts.
- **REST API wrapper**: Wrap the query engine in a lightweight Flask or FastAPI server to expose the query functionality as HTTP endpoints, enabling integration with other tools or web frontends.
- **Result export**: Add methods to export query results directly to CSV or JSON, rather than requiring callers to serialize domain objects manually.
