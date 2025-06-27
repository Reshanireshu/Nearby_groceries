
import unittest
from unittest.mock import patch, MagicMock
from org_process_mapping_helper import OrgProcessMappingHelper


@patch("org_process_mapping_helper.db")
@patch("org_process_mapping_helper.Base")
class TestOrgProcessMappingHelper(unittest.TestCase):

    def setUp(self):
        self.mock_tables = {
            "db_nxtgen.Org_Hier_Mapping": MagicMock(),
            "db_nxtgen.Process_Area_Mapping": MagicMock(),
            "db_nxtgen.Org_Hierarchy": MagicMock(),
            "db_nxtgen.MappingField_Combo_Table": MagicMock(),
        }

    def test_init(self, mock_base, mock_db):
        mock_base.metadata.tables = self.mock_tables
        helper = OrgProcessMappingHelper()
        self.assertIsInstance(helper, OrgProcessMappingHelper)

    def test_update_status_in_list_of_records(self, mock_base, mock_db):
        mock_base.metadata.tables = self.mock_tables
        helper = OrgProcessMappingHelper()
        records = [
            {"approval_1_status": "Approved", "approval_2_status": "Approved"},
            {"approval_1_status": "Rejected", "approval_2_status": "Approved"},
            {"approval_1_status": "Pending", "approval_2_status": "Approved"},
        ]
        result = helper._update_status_in_list_of_records(records)
        self.assertEqual(result[0]["status"], "Approved")
        self.assertEqual(result[1]["status"], "Rejected")
        self.assertEqual(result[2]["status"], "Pending")

    def test_validation_organization_match_score(self, mock_base, mock_db):
        mock_base.metadata.tables = self.mock_tables
        mock_db.session.query.return_value.all.return_value = [("Finance",), ("HR",)]
        helper = OrgProcessMappingHelper()
        result = helper.validation_organization_match_score("Finan")
        self.assertIsInstance(result, list)


if __name__ == "__main__":
    unittest.main()
