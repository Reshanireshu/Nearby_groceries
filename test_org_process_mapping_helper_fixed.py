
import unittest
from unittest.mock import MagicMock, patch
from org_process_mapping_helper import OrgProcessMappingHelper


class TestOrgProcessMappingHelper(unittest.TestCase):
    """Unit tests for OrgProcessMappingHelper with full mocking of SQLAlchemy Base & db."""

    @classmethod
    def setUpClass(cls):
        # Patch Base and db *once* for the entire TestCase
        cls.base_patcher = patch('org_process_mapping_helper.Base')
        cls.db_patcher = patch('org_process_mapping_helper.db')
        cls.mock_base = cls.base_patcher.start()
        cls.mock_db = cls.db_patcher.start()

        # Provide fake metadata tables so __init__ doesn't raise KeyError
        cls.mock_tables = {
            "db_nxtgen.Org_Hier_Mapping": MagicMock(),
            "db_nxtgen.Process_Area_Mapping": MagicMock(),
            "db_nxtgen.Org_Hierarchy": MagicMock(),
            "db_nxtgen.MappingField_Combo_Table": MagicMock(),
        }
        cls.mock_base.metadata.tables = cls.mock_tables

    @classmethod
    def tearDownClass(cls):
        # Stop patchers started in setUpClass
        cls.base_patcher.stop()
        cls.db_patcher.stop()

    def setUp(self):
        # Fresh helper instance for each test
        self.helper = OrgProcessMappingHelper()
        # Easier handle to the patched db inside tests
        self.db = self.__class__.mock_db

    # ------------------------------------------------------------------ #
    # _get_distinct_mapping_ids
    # ------------------------------------------------------------------ #
    def test_get_distinct_mapping_ids(self):
        mock_row = MagicMock()
        mock_row._mapping = {{'mapping_id': 123}}
        self.db.session.execute.return_value.fetchone.return_value = mock_row

        result = self.helper._get_distinct_mapping_ids('SAP', 'Finance')
        self.assertEqual(result, {{'mapping_id': 123}})
        self.db.session.execute.assert_called_once()

    # ------------------------------------------------------------------ #
    # _get_org_record
    # ------------------------------------------------------------------ #
    def test_get_org_record(self):
        mock_row = MagicMock()
        mock_row._mapping = {{'org_id': 1, 'org_name': 'Finance'}}
        self.db.session.execute.return_value.fetchone.return_value = mock_row

        result = self.helper._get_org_record(1)
        self.assertEqual(result, {{'org_id': 1, 'org_name': 'Finance'}})

    # ------------------------------------------------------------------ #
    # _merge_records (no db interaction)
    # ------------------------------------------------------------------ #
    def test_merge_records(self):
        org_record = {{'org_id': 1, 'org_name': 'Finance'}}
        proc_record = {{'status': 'Approved'}}
        merged = self.helper._merge_records(org_record, proc_record)

        self.assertEqual(merged['org_id'], 1)
        self.assertEqual(merged['org_name'], 'Finance')
        self.assertEqual(merged['org_hier_status'], 'Approved')

    # ------------------------------------------------------------------ #
    # _update_status_in_list_of_records (no db interaction)
    # ------------------------------------------------------------------ #
    def test_update_status_in_list_of_records(self):
        records = [
            {{'approval_1_status': 'Approved', 'approval_2_status': 'Approved'}},
            {{'approval_1_status': 'Rejected', 'approval_2_status': 'Approved'}},
            {{'approval_1_status': 'Pending',  'approval_2_status': 'Approved'}},
        ]
        updated = self.helper._update_status_in_list_of_records(records)
        self.assertEqual(updated[0]['status'], 'Approved')
        self.assertEqual(updated[1]['status'], 'Rejected')
        self.assertEqual(updated[2]['status'], 'Pending')

    # ------------------------------------------------------------------ #
    # validation_organization_match_score
    # ------------------------------------------------------------------ #
    def test_validation_organization_match_score(self):
        self.db.session.query.return_value.all.return_value = [('Finance',), ('HR',)]
        result = self.helper.validation_organization_match_score('Finan')
        self.assertIsInstance(result, list)
        self.assertTrue(any(r['org_name'] == 'Finan' for r in result))

    # ------------------------------------------------------------------ #
    # construct_hier_org_records
    # ------------------------------------------------------------------ #
    def test_construct_hier_org_records(self):
        sample = [
            {{'org_id': 1, 'org_level': '1', 'level1': 'A', 'level2': None}},
            {{'org_id': 2, 'org_level': '2', 'level1': 'A', 'level2': 'B'}},
            # Duplicate level1 with higher org_level (should win)
            {{'org_id': 3, 'org_level': '3', 'level1': 'A', 'level2': None}},
        ]
        final = self.helper.construct_hier_org_records(sample)
        # Only unique org_id records remain
        self.assertEqual(len(final), 3)
        # Highest level for 'A' should be org_id 3
        highest = next(r for r in final if r['org_id'] == 3)
        self.assertEqual(highest['org_level'], '3')

    # ------------------------------------------------------------------ #
    # org_hierarchy_validation_service (simplified)
    # ------------------------------------------------------------------ #
    def test_org_hierarchy_validation_service(self):
        # Mock DB responses used in the validation function
        # For existing org names query
        self.db.session.query.return_value.filter.return_value.all.return_value = []
        # For parent approved check
        self.db.session.query.return_value.filter.return_value.limit.return_value.first.return_value = True

        request = {{
            'prop_val': [
                {{'org_name': 'Finance', 'org_level': 8, 'parent_name': 'ParentOrg'}},
            ]
        }}

        result = self.helper.org_hierarchy_validation_service(request)
        self.assertFalse(result['prop_val'][0]['is_validated'])  # org_level > 7 invalid
        self.assertTrue(result['message'])

    # ------------------------------------------------------------------ #
    # construct_org_name_and_org_id
    # ------------------------------------------------------------------ #
    def test_construct_org_name_and_org_id(self):
        # Simulate two separate calls to .all(); side_effect list provides result for each
        self.db.session.query.return_value.order_by.return_value.all.side_effect = [
            [('Finance', 1)],                    # First call: org_id mapping
            [('Finance', 'Pending', 'Pending')] # Second call: status mapping
        ]
        mapping, status = self.helper.construct_org_name_and_org_id()
        self.assertEqual(mapping['Finance'], 1)
        self.assertTrue(status['Finance'])

    # ------------------------------------------------------------------ #
    # replace_org_name_by_org_id
    # ------------------------------------------------------------------ #
    def test_replace_org_name_by_org_id(self):
        # Patch helper.construct_org_name_and_org_id to a deterministic map
        self.helper.construct_org_name_and_org_id = MagicMock(return_value=(
            {{'Level1Org': 1, 'Level2Org': 2}},  # name->id
            {{'Level1Org': False, 'Level2Org': False}},  # approval pending status
        ))
        sample = [{{'level1': 'Level1Org', 'level2': 'Level2Org'}}]
        result = self.helper.replace_org_name_by_org_id(sample)
        self.assertEqual(result[0]['leaf_org_id'], 2)
        self.assertIn('each_org_id', result[0])


if __name__ == "__main__":
    unittest.main()
