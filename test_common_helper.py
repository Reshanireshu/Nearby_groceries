
import unittest
from unittest.mock import patch, MagicMock
from helper.common_helper import CommonHelper
from datetime import datetime

class TestCommonHelper(unittest.TestCase):

    def setUp(self):
        self.helper = CommonHelper()

    def test_find_max_length(self):
        data = {"a": "one", "b": "three", "c": "sevenchars"}
        result = self.helper.find_max_length(data)
        self.assertEqual(result, 10)

    def test_cleaned_dict(self):
        input_data = [{"a": 1, "b": None}, {"a": "", "b": 2}]
        result = self.helper.cleaned_dict(input_data)
        self.assertEqual(result, [{"a": 1}, {"b": 2}])

    def test_remove_unnecessary_keys_in_list_of_dict(self):
        sample = [{"a": 1, "b": 2, "c": 3}]
        result = self.helper.remove_unnecessary_keys_in_list_of_dict(sample, ["b", "c"])
        self.assertEqual(result, [{"a": 1}])

    def test_serialize_row(self):
        row = {
            "dyn_col_1": "approve",
            "dyn_col_2": "from_val",
            "dyn_col_3": "to_val",
            "date": datetime(2024, 5, 1, 12, 30)
        }
        result = self.helper.serialize_row(row)
        self.assertEqual(result["request_details"], "approve")
        self.assertEqual(result["from"], "from_val")
        self.assertEqual(result["to"], "to_val")
        self.assertEqual(result["date"], "2024-05-01T12:30:00")

    def test_build_tree_view_json_simple(self):
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

    @patch("helper.common_helper.requests.get")
    def test_get_user_details(self, mock_get):
        mock_get.return_value = MagicMock(status_code=200, json=lambda: {"user": "mocked"})
        headers = {"Authorization": "Bearer token"}
        result = self.helper.get_user_details(headers)
        self.assertEqual(result.status_code, 200)

if __name__ == '__main__':
    unittest.main()
