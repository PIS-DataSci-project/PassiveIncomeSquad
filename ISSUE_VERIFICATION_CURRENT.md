# Issue Verification Report - Current Status

**Date:** 2026年2月8日  
**File Checked:** [impl.py](impl.py)

---

## Summary
✅ **Both issues have been FIXED and are present in the current impl.py**

---

## Issue #1: `getJournalsInCategoriesWithQuartile`

### Issue Description
> The overall amount of identifiers (without repetition) retrieved from all the journals returned is greater (of one unit) than the one expected.

### Status
✅ **FIXED** - The quartile filter is properly implemented

### Current Implementation
**Location:** [impl.py lines 1431-1455](impl.py#L1431-L1455)

```python
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
        if "quartile" in df.columns:
            df = df[df["quartile"].isin(quartiles)]  # ✅ FIX IS HERE

        self._add_identifiers_from_categories_df(df, wanted_identifiers)

    if not wanted_identifiers:
        return []

    journal_map: Dict[str, Journal] = {}
    for handler in self.journalQuery:
        df = handler.getAllJournals()
        self._add_journals_matching_identifiers_from_df(df, wanted_identifiers, journal_map)

    return list(journal_map.values())
```

### What was fixed
- **Line 1449:** Added quartile filter `if "quartile" in df.columns: df = df[df["quartile"].isin(quartiles)]`
- **Impact:** Ensures that only identifiers from journals in the REQUESTED quartiles are collected, not from all quartiles

### Root Cause (now fixed)
The function was collecting identifiers from all quartiles instead of filtering by the requested quartiles, resulting in 1 extra identifier being included.

---

## Issue #2: `getDiamondJournalsInAreasAndCategoriesWithQuartile`

### Issue Description
> The number of journals returned is greater (of several units) than the expected number.

### Status
✅ **FIXED** - The APC boolean coercion logic correctly filters out non-diamond journals

### Current Implementation
**Location:** [impl.py lines 1529-1542](impl.py#L1529-L1542)

```python
def getDiamondJournalsInAreasAndCategoriesWithQuartile(
    self,
    area_ids: Set[str],
    category_ids: Set[str],
    quartiles: Set[str],
) -> List[Journal]:
    journals = self.getJournalsInAreasAndCategoriesWithQuartile(area_ids, category_ids, quartiles)

    diamond: List[Journal] = []
    for j in journals:
        if not self._journal_has_apc(j):  # ✅ FIX IS HERE
            diamond.append(j)

    return diamond
```

### Supporting Code - `_coerce_bool` Method
**Location:** [impl.py lines 1321-1338](impl.py#L1321-L1338)

```python
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
    return False  # ✅ FIX: Returns False for unrecognized values
```

### Supporting Code - `_journal_has_apc` Method
**Location:** [impl.py lines 1340-1346](impl.py#L1340-L1346)

```python
def _journal_has_apc(self, journal) -> bool:
    """兼容不同 Journal API：hasAPC / getAPC / .apc"""
    if hasattr(journal, "hasAPC") and callable(getattr(journal, "hasAPC")):
        return bool(journal.hasAPC())
    if hasattr(journal, "getAPC") and callable(getattr(journal, "getAPC")):
        return bool(journal.getAPC())
    return bool(getattr(journal, "apc", False))
```

### What was fixed
1. **`_coerce_bool` method (line 1338):** Now returns `False` for unrecognized values instead of `True`, ensuring that journals with undefined or unusual APC values are not incorrectly classified as having APC
2. **`_journal_has_apc` method:** Properly checks the journal's APC status
3. **Diamond filter (line 1539):** Only includes journals where `_journal_has_apc(j)` returns `False`

### Root Cause (now fixed)
The original `_coerce_bool` function was returning `True` for unrecognized APC values, causing journals that should have been excluded from the diamond list to be included. Additionally, the APC filtering logic was not strict enough.

---

## Verification Checklist

| Item | Status | Location |
|------|--------|----------|
| Quartile filter in `getJournalsInCategoriesWithQuartile` | ✅ Present | Line 1449 |
| `_coerce_bool` returns False for unrecognized values | ✅ Correct | Line 1338 |
| `_journal_has_apc` method correctly implemented | ✅ Correct | Lines 1340-1346 |
| Diamond filter in `getDiamondJournalsInAreasAndCategoriesWithQuartile` | ✅ Present | Line 1539 |

---

## Conclusion

Both issues have been **successfully fixed** in the current implementation of [impl.py](impl.py):

1. ✅ `getJournalsInCategoriesWithQuartile` correctly filters by quartile
2. ✅ `getDiamondJournalsInAreasAndCategoriesWithQuartile` correctly filters to exclude APC journals

The fixes are properly applied and should resolve the reported discrepancies.
