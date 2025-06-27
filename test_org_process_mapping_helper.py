
import unittest
from unittest.mock import MagicMock, patch
from org_process_mapping_helper import OrgProcessMappingHelper


class TestOrgProcessMappingHelper(unittest.TestCase):

    def setUp(self):
        self.helper = OrgProcessMappingHelper()

    @patch("org_process_mapping_helper.db")
    def test_get_distinct_mapping_ids(self, mock_db):
        mock_result = MagicMock()
        mock_result._mapping = {"mapping_id": 123}
        mock_db.session.execute.return_value.fetchone.return_value = mock_result

        result = self.helper._get_distinct_mapping_ids("SAP", "Finance")
        self.assertEqual(result, {"mapping_id": 123})

    @patch("org_process_mapping_helper.db")
    def test_get_org_record(self, mock_db):
        mock_result = MagicMock()
        mock_result._mapping = {"org_id": 1, "org_name": "Finance"}
        mock_db.session.execute.return_value.fetchone.return_value = mock_result

        result = self.helper._get_org_record(1)
        self.assertEqual(result, {"org_id": 1, "org_name": "Finance"})

    def test_merge_records(self):
        org_record = {"org_id": 1, "org_name": "Finance"}
        process_record = {"status": "Approved"}
        merged = self.helper._merge_records(org_record, process_record)
        self.assertEqual(merged["org_id"], 1)
        self.assertEqual(merged["status"], "Approved")
        self.assertEqual(merged["org_hier_status"], "Approved")

    def test_update_status_in_list_of_records(self):
        records = [
            {"approval_1_status": "Approved", "approval_2_status": "Approved"},
            {"approval_1_status": "Rejected", "approval_2_status": "Approved"},
            {"approval_1_status": "Pending", "approval_2_status": "Approved"},
        ]
        updated = self.helper._update_status_in_list_of_records(records)
        self.assertEqual(updated[0]["status"], "Approved")
        self.assertEqual(updated[1]["status"], "Rejected")
        self.assertEqual(updated[2]["status"], "Pending")

    @patch("org_process_mapping_helper.db")
    def test_validation_organization_match_score(self, mock_db):
        mock_db.session.query.return_value.all.return_value = [("Finance",), ("HR",)]
        result = self.helper.validation_organization_match_score("Finan")
        self.assertIsInstance(result, list)

    def test_construct_hier_org_records(self):
        records = [
            {"org_id": 1, "org_level": "1", "level1": "A", "level2": None},
            {"org_id": 2, "org_level": "2", "level1": "A", "level2": "B"},
        ]
        final = self.helper.construct_hier_org_records(records)
        self.assertEqual(len(final), 2)

    @patch("org_process_mapping_helper.db")
    def test_org_hierarchy_mapping_validation_service(self, mock_db):
        request_data = {
            "prop_val": [
                {"org_name": "Finance", "org_level": 8, "parent_name": "ParentOrg"}
            ]
        }
        mock_db.session.query.return_value.filter.return_value.all.return_value = []
        mock_db.session.query.return_value.filter.return_value.limit.return_value.first.return_value = True

        result = self.helper.org_hierarchy_validation_service(request_data)
        self.assertEqual(result["prop_val"][0]["is_validated"], True)
        self.assertTrue("message" in result)

    @patch("org_process_mapping_helper.db")
    def test_construct_org_name_and_org_id(self, mock_db):
        mock_db.session.query.return_value.order_by.return_value.all.side_effect = [
            [("Finance", 1)], [("Finance", "Pending", "Pending")]
        ]
        names, statuses = self.helper.construct_org_name_and_org_id()
        self.assertEqual(names["Finance"], 1)
        self.assertTrue(statuses["Finance"])

    def test_replace_org_name_by_org_id(self):
        self.helper.construct_org_name_and_org_id = MagicMock(return_value=(
            {"Level1Org": 1, "Level2Org": 2}, {"Level1Org": False, "Level2Org": False}
        ))
        sample = [{"level1": "Level1Org", "level2": "Level2Org"}]
        result = self.helper.replace_org_name_by_org_id(sample)
        self.assertIn("leaf_org_id", result[0])


if __name__ == "__main__":
    unittest.main()
