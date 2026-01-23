# River_full.py
from __future__ import annotations

from typing import Set, Dict, List

import pandas as pd

from QueryEngine import BasicQueryEngine
from impl import Journal


class FullQueryEngine(BasicQueryEngine):
    """
    FullQueryEngine = “跨源拼接查询”的 QueryEngine。

    它做的事不是“替代” BasicQueryEngine，而是在 BasicQueryEngine 的基础上做 mashup：
    1) 先用 CategoryQueryHandler（SQLite）查出一批 journal identifiers（ISSN/EISSN）。
    2) 再用 JournalQueryHandler（图数据库 / SPARQL）把这些 identifiers 对应的 journals 查出来。
    3) 最后返回 Journal 对象列表（领域对象），而不是 DataFrame。

    设计风格对齐 BasicQueryEngine：
    - handler 负责查 df
    - engine 负责把 df 变成对象（复用类似 _add_journals_from_df 的“翻译器”思路）
    """

    def __init__(self, journalQuery=None, categoryQuery=None):
        super().__init__(journalQuery or [], categoryQuery or [])

    # --------------------------
    # 1) Parse：你要求“必须用”
    # --------------------------
    def _parse_list_field(self, raw) -> List[str]:
        """
        把数据库/df 里可能出现的“粘连字符串字段”拆成 list。

        为什么需要：
        - identifiers 可能是 "1234-5678; 8765-4321" 或 "1234-5678,8765-4321"
        - language 可能是 "English; Italian"
        - 有时也可能是 None / 空串

        我们不处理 bool（按你的要求），这里只做“字符串拆分”。
        """
        if raw is None:
            return []
        text = str(raw).strip()
        if not text:
            return []

        # 兼容两种常见分隔符：; 和 ,
        text = text.replace(";", ",")
        parts = [p.strip() for p in text.split(",")]
        return [p for p in parts if p]

    # --------------------------------------------
    # 2) 辅助：从 categories df “翻译”出 identifiers 集合
    #    （复杂度类似 _add_journals_from_df，可接受）
    # --------------------------------------------
    def _add_identifiers_from_categories_df(self, df: pd.DataFrame, identifiers: Set[str]) -> None:
        """
        把 categories 的查询结果 df 中的 identifiers 列解析出来，加入到 identifiers set。

        为什么不做 _extract_identifier_set：
        - 你说如果 QueryEngine 里没有那种风格就弃用。
        - 这里用“add_xxx_from_df”的形态，跟 _add_journals_from_df 同一血统：
          也是“拿 df → 往某个容器里累加结果”的翻译器。
        """
        if df is None or df.empty:
            return

        # 兼容列名：有的地方叫 identifiers，有的地方可能叫 identifier
        col = "identifiers" if "identifiers" in df.columns else "identifier"
        if col not in df.columns:
            return

        for _, row in df.iterrows():
            for one_id in self._parse_list_field(row.get(col)):
                identifiers.add(one_id)

    # ---------------------------------------------------
    # 3) 辅助：从 journals df 中挑出“匹配 identifiers 的行”
    #    然后构造 Journal 对象放入 journal_map（去重容器）
    # ---------------------------------------------------
    def _add_journals_matching_identifiers_from_df(
        self,
        df: pd.DataFrame,
        wanted_identifiers: Set[str],
        journal_map: Dict[str, Journal],
    ) -> None:
        """
        这一步相当于 mashup 版的 _add_journals_from_df：

        - _add_journals_from_df：把 df 全部转成 Journal
        - 这里：只把 “identifier 与 wanted_identifiers 有交集” 的行转成 Journal

        为什么还要 journal_map（去重）：
        - 你们 UML/接口允许多个 handler（即使当前只有一个，代码结构仍按可扩展写）
        - SPARQL/df 在某些情况下也可能返回重复行
        - map 去重成本低，结果更稳定
        """
        if df is None or df.empty or not wanted_identifiers:
            return

        # JournalQueryHandler 里常见列名是 identifier（单数）
        id_col = "identifier" if "identifier" in df.columns else "identifiers"
        if id_col not in df.columns:
            return

        for _, row in df.iterrows():
            row_ids = self._parse_list_field(row.get(id_col))
            if not row_ids:
                continue

            # 只要这一行的任意 identifier 在 wanted_identifiers 里，就认为“命中”
            hit = any(one_id in wanted_identifiers for one_id in row_ids)
            if not hit:
                continue

            # 选一个稳定的 key：用“第一条 identifier”作为 map key（去重用）
            # 为什么不用 row["journal"]（URI）：
            # - 你们 mashup 的桥梁是 identifiers（ISSN/EISSN）
            # - categories 侧提供的也是 identifiers
            key = row_ids[0]

            if key not in journal_map:
                journal_map[key] = Journal(
                    identifiers=row_ids,
                    title=row.get("title", ""),
                    language=self._parse_list_field(row.get("language")),
                    seal=row.get("seal", False),      # bool 暂且不处理，直接传
                    license=row.get("license", ""),
                    apc=row.get("apc", False),        # bool 暂且不处理，直接传
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
        """
        人类经验解释：
        - 先从“学科分类数据库”里筛：这些 category + 这些 quartile 对应哪些期刊 ISSN？
        - 再从“期刊知识库（DOAJ 图）”里把这些 ISSN 对应的期刊对象拿出来。

        返回的是 Journal 对象列表，不是 DataFrame。
        """
        if not category_ids or not quartiles:
            return []

        # 1) categories → wanted_identifiers
        wanted_identifiers: Set[str] = set()

        for handler in self.categoryQuery:
            df = handler.getCategoriesWithQuartile(quartiles)
            if df is None or df.empty:
                continue

            # 只留目标 category
            if "category_id" in df.columns:
                df = df[df["category_id"].isin(category_ids)]

            self._add_identifiers_from_categories_df(df, wanted_identifiers)

        if not wanted_identifiers:
            return []

        # 2) journals → 只取匹配 wanted_identifiers 的 journals
        journal_map: Dict[str, Journal] = {}

        for handler in self.journalQuery:
            # 为了保持与你们 BasicQueryEngine 风格一致：从 handler 拿 df，再交给 helper 翻译
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
        """
        先从 categories/areas 的关系里拿到 identifiers，
        再到 journals 知识库里按 license 过滤后，取交集。

        注意：这里的“license 过滤”交给 JournalQueryHandler 来做（下推到数据源）。
        这样符合你们 QueryEngine 的设计：handler 负责查什么，engine 负责合并与对象化。
        """
        if not area_ids or not licenses:
            return []

        wanted_identifiers: Set[str] = set()

        # 1) areas → identifiers
        for handler in self.categoryQuery:
            df = handler.getCategoriesAssignedToAreas(area_ids)
            self._add_identifiers_from_categories_df(df, wanted_identifiers)

        if not wanted_identifiers:
            return []

        # 2) journals filtered by license → intersect with wanted_identifiers
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
        """
        更像“组合筛选”：
        - 在 SQLite 侧做：areas ∩ categories ∩ quartiles → identifiers
        - 在图数据库侧做：identifiers → journals

        这里不做 bool 过滤（按你的要求）。
        """
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
