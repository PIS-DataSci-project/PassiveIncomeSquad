import json
import tempfile
import unittest
from pathlib import Path

import pandas as pd

from impl import CategoryUploadHandler


class TestCategoryUploadHandlerVisual(unittest.TestCase):
    def test_category_upload_with_visual_output(self):
        sample_payload = [
            {
                "identifiers": ["1234-5678", "8765-4321"],
                "categories": [
                    {
                        "id": "BUSINESS",
                        "quartile": "Q1",
                        "areas": ["Economics", "Management"],
                    },
                    {"id": "SOCIAL", "quartile": "Q2", "areas": ["Sociology"]},
                ],
            },
            {
                "identifiers": ["1111-2222"],
                "categories": [
                    {
                        "id": "ENGINEERING",
                        "quartile": "Q3",
                        "areas": ["Mechanical"],
                    }
                ],
            },
        ]

        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            json_path = temp_path / "sample_categories.json"
            db_path = temp_path / "category_test.db"

            json_path.write_text(json.dumps(sample_payload, indent=2), encoding="utf-8")

            handler = CategoryUploadHandler()
            self.assertTrue(handler.setDbPathOrUrl(str(db_path)))

            result_df = handler.pushDataToDb(str(json_path))
            self.assertIsInstance(result_df, pd.DataFrame)
            self.assertGreaterEqual(len(result_df), 3)
            self.assertTrue({"identifier", "category_id", "quartile", "areas"}.issubset(result_df.columns))

        output_path = Path("category_upload_visual.html")
        styled = (
            result_df.sort_values(["category_id", "identifier"]).reset_index(drop=True)
        )
        output_path.write_text(
            styled.to_html(index=False, border=0, justify="center"), encoding="utf-8"
        )
        self.assertTrue(output_path.exists())


if __name__ == "__main__":
    unittest.main()
