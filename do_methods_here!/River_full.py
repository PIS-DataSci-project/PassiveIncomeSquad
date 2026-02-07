# River_full.py
from __future__ import annotations

from typing import Set, Dict, List

import pandas as pd

from from_uml_to_files.QueryEngine import BasicQueryEngine
from impl import Journal


class FullQueryEngine(BasicQueryEngine):
    """
    FullQueryEngine = “跨源拼接查询”的 QueryEngine。
    - SQLite（categories/areas/quartile）先筛出 identifiers（ISSN/EISSN）
    - 图数据库（journals）再取回完整 Journal 对象
    """

    def __init__(self, journalQuery=None, categoryQuery=None):
        # ✅ 适配 BasicQueryEngine.__init__() 无参版本
        super().__init__()
        self.journalQuery.extend(journalQuery or [])
        self.categoryQuery.extend(categoryQuery or [])

    # --------------------------
    # Bool helpers（diamond 需要）
    # --------------------------
    def _coerce_bool(self, x) -> bool:
        """把 True/False、'true'/'false'、1/0、'1'/'0' 等统一成 bool。"""
        if isinstance(x, bool):
            return x
        if x is None:
            return False
        if isinstance(x, (int, float)):
            try:
                return bool(int(x))
            except Exception:
                return bool(x)

        s = str(x).strip().lower()
        if s in {"true", "t", "yes", "y", "1"}:
            return True
        if s in {"false", "f", "no", "n", "0", ""}:
            return False
        return True

    def _journal_has_apc(self, journal) -> bool:
        """兼容不同 Journal API：hasAPC / getAPC / .apc"""
        if hasattr(journal, "hasAPC") and callable(getattr(journal, "hasAPC")):
            return bool(journal.hasAPC())
        if hasattr(journal, "getAPC") and callable(getattr(journal, "getAPC")):
            return bool(journal.getAPC())
        return bool(getattr(journal, "apc", False))

    # --------------------------
    # Parse：必须用
    # --------------------------
    def _parse_list_field(self, raw) -> List[str]:
        """
        把数据库/df 里可能出现的“粘连字符串字段”拆成 list。
        支持：None / NaN / list / "a;b" / "a,b"
        """
        if raw is None:
            return []
        if isinstance(raw, (list, tuple, set)):
            return [str(part).strip() for part in raw if str(part).strip()]
        try:
            if pd.isna(raw):
                return []
        except Exception:
            pass

        text = str(raw).strip()
        if not text:
            return []

        text = text.replace(";", ",")
        parts = [p.strip() for p in text.split(",")]
        return [p for p in parts if p]

    # --------------------------------------------
    # 从 categories df 累积 identifiers
    # --------------------------------------------
    def _add_identifiers_from_categories_df(self, df: pd.DataFrame, identifiers: Set[str]) -> None:
        if df is None or df.empty:
            return

        col = "identifiers" if "identifiers" in df.columns else "identifier"
        if col not in df.columns:
            return

        for _, row in df.iterrows():
            for one_id in self._parse_list_field(row.get(col)):
                identifiers.add(one_id)

    # ---------------------------------------------------
    # 从 journals df 中筛出 wanted_identifiers 命中的行，构造 Journal 放入 map
    # ---------------------------------------------------
    def _add_journals_matching_identifiers_from_df(
        self,
        df: pd.DataFrame,
        wanted_identifiers: Set[str],
        journal_map: Dict[str, Journal],
    ) -> None:
        if df is None or df.empty or not wanted_identifiers:
            return

        id_col = "identifier" if "identifier" in df.columns else ("identifiers" if "identifiers" in df.columns else None)
        if id_col is None:
            return

        for _, row in df.iterrows():
            row_ids = self._parse_list_field(row.get(id_col))
            if not row_ids:
                continue

            # 命中判定：任意 id 在 wanted_identifiers 中即可
            if not any(one_id in wanted_identifiers for one_id in row_ids):
                continue

            # ✅ 稳定 key：同一本 journal（ISSN/EISSN）不会因为命中不同 id 而重复
            stable_key = "|".join(sorted(set(row_ids)))

            if stable_key not in journal_map:
                journal_map[stable_key] = Journal(
                    identifiers=row_ids,  # 保留完整 ISSN/EISSN
                    title=row.get("title", ""),
                    language=self._parse_list_field(row.get("language")),
                    seal=self._coerce_bool(row.get("seal", False)),
                    license=row.get("license", ""),
                    apc=self._coerce_bool(row.get("apc", False)),
                    publisher=row.get("publisher", None),
                )

    # ==========================
    # Mashup 查询 1
    # ==========================
    def getJournalsInCategoriesWithQuartile(
        self,
        category_ids: Set[str],
        quartiles: Set[str],
    ) -> List[Journal]:
        if not category_ids or not quartiles:
            return []

        wanted_identifiers: Set[str] = set()

        for handler in self.categoryQuery:
            df = handler.getCategoriesWithQuartile(quartiles)
            if df is None or df.empty:
                continue

            if "category_id" in df.columns:
                df = df[df["category_id"].isin(category_ids)]

            self._add_identifiers_from_categories_df(df, wanted_identifiers)

        if not wanted_identifiers:
            return []

        journal_map: Dict[str, Journal] = {}
        for handler in self.journalQuery:
            df = handler.getAllJournals()
            self._add_journals_matching_identifiers_from_df(df, wanted_identifiers, journal_map)

        return list(journal_map.values())

    # ==========================
    # Mashup 查询 2
    # ==========================
    def getJournalsInAreasWithLicense(
        self,
        area_ids: Set[str],
        licenses: Set[str],
    ) -> List[Journal]:
        if not area_ids or not licenses:
            return []

        wanted_identifiers: Set[str] = set()

        for handler in self.categoryQuery:
            df = handler.getCategoriesAssignedToAreas(area_ids)
            self._add_identifiers_from_categories_df(df, wanted_identifiers)

        if not wanted_identifiers:
            return []

        journal_map: Dict[str, Journal] = {}
        for handler in self.journalQuery:
            df = handler.getJournalsWithLicense(licenses)
            self._add_journals_matching_identifiers_from_df(df, wanted_identifiers, journal_map)

        return list(journal_map.values())

    # ==========================
    # Mashup 查询 3
    # ==========================
    def getJournalsInAreasAndCategoriesWithQuartile(
        self,
        area_ids: Set[str],
        category_ids: Set[str],
        quartiles: Set[str],
    ) -> List[Journal]:
        if not area_ids or not category_ids or not quartiles:
            return []

        wanted_identifiers: Set[str] = set()

        for handler in self.categoryQuery:
            df = handler.getCategoriesAssignedToAreas(area_ids)
            if df is None or df.empty:
                continue

            if "category_id" in df.columns:
                df = df[df["category_id"].isin(category_ids)]
            if "quartile" in df.columns:
                df = df[df["quartile"].isin(quartiles)]

            self._add_identifiers_from_categories_df(df, wanted_identifiers)

        if not wanted_identifiers:
            return []

        journal_map: Dict[str, Journal] = {}
        for handler in self.journalQuery:
            df = handler.getAllJournals()
            self._add_journals_matching_identifiers_from_df(df, wanted_identifiers, journal_map)

        return list(journal_map.values())

    # ==========================
    # Diamond mashup：APC 必须为 False
    # ==========================
    def getDiamondJournalsInAreasAndCategoriesWithQuartile(
        self,
        area_ids: Set[str],
        category_ids: Set[str],
        quartiles: Set[str],
    ) -> List[Journal]:
        journals = self.getJournalsInAreasAndCategoriesWithQuartile(area_ids, category_ids, quartiles)

        diamond: List[Journal] = []
        for j in journals:
            if not self._journal_has_apc(j):
                diamond.append(j)

        return diamond

