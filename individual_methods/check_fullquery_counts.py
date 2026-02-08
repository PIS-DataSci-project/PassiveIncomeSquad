# debug_tests.py
from __future__ import annotations

from collections import Counter, defaultdict
from typing import Iterable, Any

import pandas as pd

# ========= 你需要改这里：导入你实际的 Engine 和 Handlers =========
# 例：from impl import FullQueryEngine, BasicQueryEngine, JournalQueryHandler, CategoryQueryHandler
from River_imply import FullQueryEngine  # 你也可以换成 River_full 里的 FullQueryEngine
# from impl import JournalQueryHandler, CategoryQueryHandler
# ================================================================


# ========= 你需要改这里：创建 handlers 的方式（路径 / endpoint / 参数） =========
def build_engine() -> FullQueryEngine:
    """
    返回一个已经装好 handlers 的 FullQueryEngine。
    你只需要在这里把 JournalQueryHandler / CategoryQueryHandler 实例化并塞进去。
    """
    engine = FullQueryEngine()

    # TODO: 下面两行按你的项目实际情况改：
    # jh = JournalQueryHandler(endpoint_or_path=...)
    # ch = CategoryQueryHandler(dbPathOrUrl=...)

    # engine.journalQuery.append(jh)
    # engine.categoryQuery.append(ch)

    return engine
# ============================================================================


# ========= 小工具：尽量从 Journal 对象里取 identifiers =========
def get_identifiers(j: Any) -> list[str]:
    for attr in ("identifiers", "identifier", "ids"):
        if hasattr(j, attr):
            val = getattr(j, attr)
            if isinstance(val, (list, tuple, set)):
                return [str(x) for x in val]
            if val is not None:
                return [str(val)]
    # 尝试 getter
    for fn in ("getIdentifiers", "getIdentifier", "getId"):
        if hasattr(j, fn) and callable(getattr(j, fn)):
            val = getattr(j, fn)()
            if isinstance(val, (list, tuple, set)):
                return [str(x) for x in val]
            if val is not None:
                return [str(val)]
    return []


def get_apc(j: Any) -> Any:
    for fn in ("hasAPC", "getAPC"):
        if hasattr(j, fn) and callable(getattr(j, fn)):
            return getattr(j, fn)()
    return getattr(j, "apc", None)


def pretty_head(xs: Iterable[Any], n=10) -> list[Any]:
    xs = list(xs)
    return xs[:n]


# ========= 核心检查 =========

def check_getEntityById_has_getLanguages(engine: FullQueryEngine, sample_id: str) -> None:
    print("\n=== check: getEntityById / getLanguages ===")
    j = engine.getEntityById(sample_id)
    if j is None:
        print(f"[WARN] getEntityById({sample_id!r}) returned None (check sample_id)")
        return
    has = hasattr(j, "getLanguages") and callable(getattr(j, "getLanguages"))
    print(f"Journal type: {type(j)}")
    print(f"Has getLanguages(): {has}")
    if not has:
        print("-> FIX: implement Journal.getLanguages() (can return getLanguage() or languages list).")


def check_categories_counts(engine: FullQueryEngine) -> None:
    print("\n=== check: getAllCategories duplicates ===")
    cats = engine.getAllCategories()
    print(f"Returned categories: {len(cats)}")

    # 统计“你返回的 Category 里用什么当唯一键”
    keys = []
    for c in cats:
        # 你们 Category 类通常是 identifiers=set({category_id})
        cid = None
        if hasattr(c, "identifiers"):
            ids = getattr(c, "identifiers")
            if isinstance(ids, set) and ids:
                cid = sorted(list(ids))[0]
        if cid is None and hasattr(c, "getIdentifiers"):
            ids = c.getIdentifiers()
            if isinstance(ids, (set, list)) and ids:
                cid = sorted(list(ids))[0]
        keys.append((cid, getattr(c, "quartile", None)))

    freq = Counter(keys)
    dups = {k: v for k, v in freq.items() if v > 1}
    print(f"Unique keys (cid,quartile): {len(freq)}")
    print(f"Duplicate keys count: {len(dups)}")
    if dups:
        print("Top duplicate keys:", pretty_head(sorted(dups.items(), key=lambda x: -x[1]), 10))
        print("-> FIX idea: de-dup on category_id or (category_id, quartile) before constructing Category objects.")


def check_areas_counts(engine: FullQueryEngine) -> None:
    print("\n=== check: getAllAreas duplicates ===")
    areas = engine.getAllAreas()
    print(f"Returned areas: {len(areas)}")

    # 尝试 area_id/identifiers
    keys = []
    for a in areas:
        aid = None
        if hasattr(a, "identifiers"):
            ids = getattr(a, "identifiers")
            if isinstance(ids, set) and ids:
                aid = sorted(list(ids))[0]
        if aid is None and hasattr(a, "getIdentifiers"):
            ids = a.getIdentifiers()
            if isinstance(ids, (set, list)) and ids:
                aid = sorted(list(ids))[0]
        keys.append(aid)

    freq = Counter(keys)
    dups = {k: v for k, v in freq.items() if v > 1 and k is not None}
    print(f"Unique area ids: {len(freq)}")
    print(f"Duplicate area ids count: {len(dups)}")
    if dups:
        print("Top duplicate ids:", pretty_head(sorted(dups.items(), key=lambda x: -x[1]), 10))
        print("-> FIX idea: de-dup on area_id before constructing Area objects.")


def check_getCategoriesWithQuartile(engine: FullQueryEngine, quartiles: set[str]) -> None:
    print("\n=== check: getCategoriesWithQuartile duplicates ===")
    cats = engine.getCategoriesWithQuartile(quartiles)
    print(f"Quartiles={quartiles} -> returned categories: {len(cats)}")

    keys = []
    for c in cats:
        cid = None
        if hasattr(c, "identifiers"):
            ids = getattr(c, "identifiers")
            if isinstance(ids, set) and ids:
                cid = sorted(list(ids))[0]
        keys.append((cid, getattr(c, "quartile", None)))

    freq = Counter(keys)
    dups = {k: v for k, v in freq.items() if v > 1}
    print(f"Unique (cid,quartile): {len(freq)}")
    print(f"Duplicate keys count: {len(dups)}")
    if dups:
        print("Top duplicate keys:", pretty_head(sorted(dups.items(), key=lambda x: -x[1]), 10))


def check_getCategoriesAssignedToAreas(engine: FullQueryEngine, area_ids: set[str]) -> None:
    print("\n=== check: getCategoriesAssignedToAreas duplicates ===")
    cats = engine.getCategoriesAssignedToAreas(area_ids)
    print(f"Areas={area_ids} -> returned categories: {len(cats)}")

    keys = []
    for c in cats:
        cid = None
        if hasattr(c, "identifiers"):
            ids = getattr(c, "identifiers")
            if isinstance(ids, set) and ids:
                cid = sorted(list(ids))[0]
        keys.append((cid, getattr(c, "quartile", None)))

    freq = Counter(keys)
    dups = {k: v for k, v in freq.items() if v > 1}
    print(f"Unique (cid,quartile): {len(freq)}")
    print(f"Duplicate keys count: {len(dups)}")
    if dups:
        print("Top duplicate keys:", pretty_head(sorted(dups.items(), key=lambda x: -x[1]), 10))


def check_getAreasAssignedToCategories(engine: FullQueryEngine, category_ids: set[str]) -> None:
    print("\n=== check: getAreasAssignedToCategories duplicates ===")
    areas = engine.getAreasAssignedToCategories(category_ids)
    print(f"Categories={category_ids} -> returned areas: {len(areas)}")

    keys = []
    for a in areas:
        aid = None
        if hasattr(a, "identifiers"):
            ids = getattr(a, "identifiers")
            if isinstance(ids, set) and ids:
                aid = sorted(list(ids))[0]
        keys.append(aid)

    freq = Counter(keys)
    dups = {k: v for k, v in freq.items() if v > 1 and k is not None}
    print(f"Unique area ids: {len(freq)}")
    print(f"Duplicate area ids count: {len(dups)}")
    if dups:
        print("Top duplicate ids:", pretty_head(sorted(dups.items(), key=lambda x: -x[1]), 10))


def check_getJournalsInCategoriesWithQuartile_unique_ids(
    engine: FullQueryEngine,
    category_ids: set[str],
    quartiles: set[str],
    expected_unique_identifier_count: int | None = None,
) -> None:
    print("\n=== check: getJournalsInCategoriesWithQuartile unique identifiers ===")
    journals = engine.getJournalsInCategoriesWithQuartile(category_ids, quartiles)
    print(f"Journal count: {len(journals)}")

    all_ids = []
    for j in journals:
        all_ids.extend(get_identifiers(j))

    unique_ids = sorted(set(all_ids))
    print(f"Unique identifier count: {len(unique_ids)}")
    print("First 20 unique ids:", unique_ids[:20])

    if expected_unique_identifier_count is not None:
        if len(unique_ids) != expected_unique_identifier_count:
            print(f"[MISMATCH] expected unique identifiers={expected_unique_identifier_count}, got={len(unique_ids)}")
            # 给出可能的“多出来的那一个”
            # 这里需要你再跑一次，提供 expected 的那一组 ids（测试脚本通常不提供）
            # 所以我们只能提示你去检查是否出现空串/异常 token
            suspicious = [x for x in unique_ids if not x or x.strip() != x]
            if suspicious:
                print("[SUSPECT] suspicious identifiers (empty/space issues):", suspicious)
            # 打印每本 journal 的 ids，方便人工定位
            for j in journals[:40]:
                print("  Journal IDs:", get_identifiers(j))
        else:
            print("[OK] unique identifier count matches expected.")


def check_diamond_filter(engine, area_ids, category_ids, quartiles) -> None:
    print("\n=== check: Diamond subset & APC filtering ===")

    # 可能的 base 方法名（按常见拼写/版本差异列出来）
    base_candidates = [
        "getJournalsInAreasAndCategoriesWithQuartile",
        "getJournalsInAreasAndCategoriesWithQuartiles",
        "getJournalsInAreasAndCategoriesWithQuartile ",  # 防止意外空格（很少见）
        "getJournalsInAreasAndCategories",
        "getJournalsInAreasAndCategoriesWithQ",
        "getJournalsInAreasAndCategoriesWithQuartile",  # 原名再放一次无害
        "getJournalsInAreasAndCategoriesWithQuartile",  # …
    ]
    diamond_candidates = [
        "getDiamondJournalsInAreasAndCategoriesWithQuartile",
        "getDiamondJournalsInAreasAndCategoriesWithQuartiles",
        "getDiamondJournalsInAreasAndCategories",
    ]

    def pick_method(candidates):
        for name in candidates:
            name = name.strip()
            if hasattr(engine, name) and callable(getattr(engine, name)):
                return getattr(engine, name), name
        return None, None

    base_fn, base_name = pick_method(base_candidates)
    diamond_fn, diamond_name = pick_method(diamond_candidates)

    if base_fn is None:
        print("[SKIP] No base mashup method found on this FullQueryEngine.")
        print("Available methods containing 'Areas' / 'Categories' / 'Quartile':")
        for n in dir(engine):
            if "Area" in n or "Categor" in n or "Quart" in n:
                if callable(getattr(engine, n, None)):
                    print(" -", n)
        print("-> FIX: either implement getJournalsInAreasAndCategoriesWithQuartile in your FullQueryEngine "
              "or change the script to call the actual method name you have.")
        return

    if diamond_fn is None:
        print("[SKIP] No diamond method found on this FullQueryEngine.")
        print("Available methods containing 'Diamond':")
        for n in dir(engine):
            if "Diamond" in n and callable(getattr(engine, n, None)):
                print(" -", n)
        print("-> FIX: implement getDiamondJournalsInAreasAndCategoriesWithQuartile or adjust script.")
        return

    print(f"Using base method: {base_name}")
    print(f"Using diamond method: {diamond_name}")

    base = base_fn(area_ids, category_ids, quartiles)
    diamond = diamond_fn(area_ids, category_ids, quartiles)

    print(f"Base count: {len(base)}")
    print(f"Diamond count: {len(diamond)}")

    def get_identifiers(j):
        for attr in ("identifiers", "identifier", "ids"):
            if hasattr(j, attr):
                val = getattr(j, attr)
                if isinstance(val, (list, tuple, set)):
                    return [str(x) for x in val]
                if val is not None:
                    return [str(val)]
        for fn in ("getIdentifiers", "getIdentifier", "getId"):
            if hasattr(j, fn) and callable(getattr(j, fn)):
                val = getattr(j, fn)()
                if isinstance(val, (list, tuple, set)):
                    return [str(x) for x in val]
                if val is not None:
                    return [str(val)]
        return []

    def get_apc(j):
        for fn in ("hasAPC", "getAPC"):
            if hasattr(j, fn) and callable(getattr(j, fn)):
                return getattr(j, fn)()
        return getattr(j, "apc", None)

    base_keys = set("|".join(sorted(set(get_identifiers(j)))) for j in base)
    diamond_keys = set("|".join(sorted(set(get_identifiers(j)))) for j in diamond)

    print(f"Diamond subset of base: {diamond_keys.issubset(base_keys)}")
    if base_keys == diamond_keys:
        print("[BAD] Diamond result equals base result -> APC filter likely not applied.")

    bad = []
    for j in diamond:
        apc = get_apc(j)
        if bool(apc) is True:
            bad.append((get_identifiers(j), apc))
    if bad:
        print("[BAD] Diamond includes APC=True journals (first 10):", bad[:10])
        print("-> FIX: coerce apc to bool and filter apc==False.")
    else:
        print("[OK] No obvious APC=True journals in diamond (based on Journal API).")
