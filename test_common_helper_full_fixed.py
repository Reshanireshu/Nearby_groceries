import unittest
from unittest.mock import patch, MagicMock
from datetime import datetime
import pandas as pd
from src.common_helper import CommonHelper


@patch("src.common_helper.Base")
@patch("src.common_helper.db")
class TestCommonHelper(unittest.TestCase):

    def setUp(self):
        # Provide all expected mocked tables here
        self.mock_tables = {
            "db_nxtgen.Org_Hier_Mapping": MagicMock(),
            "db_nxtgen.Org_Hierarchy": MagicMock(),
            "db_nxtgen.Workflow": MagicMock(),
        }
        self.helper = None

    def test_find_max_length(self, mock_db, mock_base):
        mock_base.metadata.tables = self.mock_tables
        self.helper = CommonHelper()
        data = {"a": "one", "b": "three", "c": "sevenchars"}
        result = self.helper.find_max_length(data)
        self.assertEqual(result, 10)

    def test_cleaned_dict(self, mock_db, mock_base):
        mock_base.metadata.tables = self.mock_tables
        self.helper = CommonHelper()
        input_data = [{"a": 1, "b": None}, {"a": "", "b": 2}]
        result = self.helper.cleaned_dict(input_data)
        self.assertEqual(result, [{"a": 1}, {"b": 2}])

    def test_remove_unnecessary_keys_in_list_of_dict(self, mock_db, mock_base):
        mock_base.metadata.tables = self.mock_tables
        self.helper = CommonHelper()
        sample = [{"a": 1, "b": 2, "c": 3}]
        result = self.helper.remove_unnecessary_keys_in_list_of_dict(sample, ["b", "c"])
        self.assertEqual(result, [{"a": 1}])

    def test_serialize_row(self, mock_db, mock_base):
        mock_base.metadata.tables = self.mock_tables
        self.helper = CommonHelper()
        row = {
            "dyn_col_1": "approve",
            "dyn_col_2": "from_val",
            "dyn_col_3": "to_val",
            "date": datetime(2024, 5, 1, 12, 30),
        }
        result = self.helper.serialize_row(row)
        self.assertEqual(result["request_details"], "approve")
        self.assertEqual(result["from"], "from_val")
        self.assertEqual(result["to"], "to_val")
        self.assertEqual(result["date"], "2024-05-01T12:30:00")

    def test_build_tree_view_json_simple(self, mock_db, mock_base):
        mock_base.metadata.tables = self.mock_tables
        self.helper = CommonHelper()
        input_data = [
            {
                "org_id": 1,
                "org_name": "Finance",
                "org_level": 2,
                "level1": "Company",
                "level2": "Finance"
            }
        ]
        result = self.helper.build_tree_view_json(input_data)
        self.assertEqual(result[0]["orgName"], "Company")
        self.assertEqual(result[0]["children"][0]["orgName"], "Finance")

    def test_groupby_field_empty(self, mock_db, mock_base):
        mock_base.metadata.tables = self.mock_tables
        self.helper = CommonHelper()
        self.assertEqual(self.helper.groupby_field([]), [])

    def test_process_group_no_mapping_id(self, mock_db, mock_base):
        mock_base.metadata.tables = self.mock_tables
        mock_db.session.execute.return_value.fetchone.return_value = MagicMock(_mapping={})
        self.helper = CommonHelper()

        sample_data = pd.DataFrame([{
            "wid": "wf_1",
            "typeof_action": "create",
            "typeof_cr": "new",
            "wf_reviewer_1_name": "Alice",
            "wf_reviewer_1_status_date": "2024-01-01",
            "wf_reviewer_1_status": "Approved",
            "wf_reviewer_2_name": "Bob",
            "wf_reviewer_2_status_date": "2024-01-02",
            "wf_reviewer_2_status": "Pending",
            "requested_by": "John",
            "created_date": "2024-01-01",
            "Comments": "Some comment",
            "depedent_workflow_id": None,
            "mapping_record_id": None,
            "org_hierarchy_record_id": [123],
            "from": "Old",
            "to": "New",
            "request_details": {"id": "abc", "level": "Finance"}
        }])

        result = self.helper.process_group(sample_data)
        self.assertIsInstance(result, dict)
        self.assertIn("wid", result)

    @patch("src.common_helper.requests.get")
    def test_get_user_details(self, mock_get, mock_db, mock_base):
        mock_base.metadata.tables = self.mock_tables
        mock_get.return_value = MagicMock(status_code=200, json=lambda: {"user": "mocked"})
        self.helper = CommonHelper()
        headers = {"Authorization": "Bearer token"}
        result = self.helper.get_user_details(headers)
        self.assertEqual(result.status_code, 200)


if __name__ == "__main__":
    unittest.main()
