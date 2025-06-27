import unittest
from unittest.mock import patch, MagicMock
from datetime import date, datetime
import sys,os
# Adjust the import path as needed
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))
from src.helper.org_hierarchy_mapping_helper import OrgHierarchyMappingHelper

class TestOrgHierarchyMappingHelper(unittest.TestCase):
    def setUp(self):
        self.helper = OrgHierarchyMappingHelper()

    def test_calculate_status(self):
        self.assertEqual(self.helper.calculate_status("Approved", "Approved"), "Approved")
        self.assertEqual(self.helper.calculate_status("Rejected", "Approved"), "Rejected")
        self.assertEqual(self.helper.calculate_status("Pending", "Approved"), "Pending")
        self.assertIsNone(self.helper.calculate_status("None", "None"))

    @patch("org_hierarchy_mapping_helper.db")
    def test_generate_workflow_id(self, mock_db):
        mock_db.session.execute.return_value.scalar.return_value = 5
        self.assertEqual(self.helper.generate_workflow_id(), "wf_6")

    @patch("org_hierarchy_mapping_helper.db")
    def test_generate_workflow_id_none(self, mock_db):
        mock_db.session.execute.return_value.scalar.return_value = None
        self.assertEqual(self.helper.generate_workflow_id(), "wf_1")

    @patch("org_hierarchy_mapping_helper.db")
    def test_generate_hier_mapping_id(self, mock_db):
        mock_db.session.execute.return_value.scalar.return_value = 10
        self.assertEqual(self.helper.generate_hier_mapping_id(), 11)

    @patch("org_hierarchy_mapping_helper.db")
    def test_generate_hier_mapping_id_none(self, mock_db):
        mock_db.session.execute.return_value.scalar.return_value = None
        self.assertEqual(self.helper.generate_hier_mapping_id(), 1)

    @patch("org_hierarchy_mapping_helper.get_user_from_token")
    def test_prepare_record_copy(self, mock_token):
        mock_token.return_value = ("user", "test_user", "role", "email@example.com")
        original_record = {
            "record_id": 1,
            "org_id": "ORG1",
            "org_name": "Test Org",
            "org_level": 2,
        }
        result = self.helper.prepare_record_copy(original_record)
        self.assertEqual(result["updated_by"], "test_user")
        self.assertEqual(result["approval_1_status"], "Pending")
        self.assertNotIn("record_id", result)

    @patch("org_hierarchy_mapping_helper.db")
    @patch("org_hierarchy_mapping_helper.get_user_from_token")
    def test_work_flow_creation(self, mock_token, mock_db):
        mock_token.return_value = ("user", "test_user", "role", "email@example.com")
        mock_db.session.execute.side_effect = [
            MagicMock(scalar=MagicMock(return_value=1)),  # max_wid
            MagicMock(fetchone=MagicMock(return_value=MagicMock(prop_id=123)))
        ]
        mock_db.func.now.return_value = datetime.now()

        self.helper.work_flow_creation(1, {"org_name": "Org1", "updated_by": "user1"}, {"action": "update", "prop_val": [1]})
        self.assertTrue(mock_db.session.execute.called)

    @patch("org_hierarchy_mapping_helper.db")
    def test_fetch_associated_records_not_found(self, mock_db):
        mock_db.session.execute.return_value.fetchone.return_value = None
        result, code = self.helper.fetch_associated_records("INVALID")
        self.assertEqual(code, 404)
        self.assertIn("org_id", result)

    @patch("org_hierarchy_mapping_helper.db")
    def test_construct_hier_table_response(self, mock_db):
        mock_record = MagicMock()
        mock_record.org_id = "ORG1"
        mock_record.record_id = 1
        mock_record.org_name = "Org1"
        mock_record.hier_type = "Type"
        mock_record.org_level = 2
        mock_record.is_deleted = 0
        mock_record.h_id = "H1"
        for level in range(1, 8):
            setattr(mock_record, f"level{level}", f"L{level}")

        with patch.object(self.helper.org_process_mapping_helper, 'replace_org_name_by_org_id', return_value='ORG_ID_MOCK'):
            self.helper.construct_hier_table_response(mock_record, "Approved")
            self.assertTrue(True)  # if no exception, test passes

    @patch("org_hierarchy_mapping_helper.db")
    @patch("org_hierarchy_mapping_helper.get_user_from_token")
    def test_prepare_mapping_workflow_records(self, mock_token, mock_db):
        mock_token.return_value = ("user", "test_user", "role", "email@example.com")
        mock_db.session.execute.return_value = None
        mock_db.func.now.return_value = date.today()

        with patch.object(self.helper.workflow_table, 'columns', [MagicMock(name='wid'), MagicMock(name='wf_status')]), \
             patch.object(self.helper.org_hier_mapping_table, 'columns', [MagicMock(name='id'), MagicMock(name='org_id')]):
            self.helper.prepare_mapping_workflow_records({"record_id": 1}, "wf_100")
            self.assertTrue(mock_db.session.execute.called)
