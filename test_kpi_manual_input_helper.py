import unittest
from unittest.mock import patch, MagicMock
from datetime import datetime
import sys, os, json
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

from src.db import db
from src.models.kpi_bookmark import Bookmark, BookmarkTypeStatic, BookmarkVal, User
from src.app import app
from src.helper.kpi_manual_input_helper import kpi_manual_input
from src.constants.api_messages import api_messages


class TestKpiManualInputHelper(unittest.TestCase):

    def setUp(self):
        # Patch db session and api messages
        self.patcher_db_session = patch('src.helper.kpi_manual_input_helper.db.session')
        self.mock_db_session = self.patcher_db_session.start()

        self.patcher_api_messages = patch('src.helper.kpi_manual_input_helper.api_messages')
        self.mock_api_messages = self.patcher_api_messages.start()

        # Patch Base.metadata.tables to prevent KeyError in CommonHelper
        self.patcher_base = patch('src.common_helper.common_helper.Base')
        self.mock_base = self.patcher_base.start()
        self.mock_base.metadata.tables = {
            "db_nxtgen.Org_Hier_Mapping": MagicMock(),
            "db_nxtgen.Org_Hierarchy": MagicMock(),
            "db_nxtgen.Workflow": MagicMock(),
            "db_nxtgen.Process_Area_Mapping": MagicMock(),
            "db_nxtgen.MappingField_Combo_Table": MagicMock(),
        }

        # Safe to instantiate helper
        self.kpi_manual_input_helper_instance = kpi_manual_input()

        # Patch Base.classes used in the helper
        self.patcher_base_classes = patch('src.helper.kpi_manual_input_helper.Base.classes', new_callable=MagicMock)
        self.mock_base_classes = self.patcher_base_classes.start()
        self.mock_base_classes.Bookmark = Bookmark
        self.mock_base_classes.Bookmark_Type_Static = BookmarkTypeStatic
        self.mock_base_classes.Bookmark_Val = BookmarkVal
        self.mock_base_classes.User = User

    def tearDown(self):
        self.patcher_db_session.stop()
        self.patcher_api_messages.stop()
        self.patcher_base_classes.stop()
        self.patcher_base.stop()

    def test_save_book_mark_no_data(self):
        request_parser = {'attribute': [], 'bookmark_name': 'Test Bookmark'}
        response = self.kpi_manual_input_helper_instance.save_book_mark(request_parser, 'test_token')
        self.mock_api_messages.assert_called_with('no_data', 'Test Bookmark')
        self.assertEqual(response, self.mock_api_messages.return_value)

    def test_save_book_mark_invalid_type(self):
        request_parser = {'attribute': [1], 'bookmark_name': 'Test Bookmark', 'bk_typ_id': 123}
        self.mock_db_session.query().filter_by().first.return_value = None
        response = self.kpi_manual_input_helper_instance.save_book_mark(request_parser, 'test_token')
        self.mock_api_messages.assert_called_with('not_exists', 'bk_typ_id 123')
        self.assertEqual(response, self.mock_api_messages.return_value)

    def test_save_book_mark_user_not_exists(self):
        request_parser = {'attribute': [1], 'bookmark_name': 'Test BM', 'bk_typ_id': 123, 'oid': 456}
        self.mock_db_session.query().filter_by().first.side_effect = [MagicMock(), None, None]
        with patch.object(self.kpi_manual_input_helper_instance, 'save_user') as mock_save_user:
            response = self.kpi_manual_input_helper_instance.save_book_mark(request_parser, 'test_token')
            mock_save_user.assert_called_with('test_token')
            self.assertEqual(response, self.mock_api_messages.return_value)

    def test_save_book_mark_exists(self):
        request_parser = {'attribute': [1], 'bookmark_name': 'Test Bookmark', 'bk_typ_id': 123, 'oid': 456}
        self.mock_db_session.query().filter_by().first.side_effect = [MagicMock(), MagicMock(), None]
        response = self.kpi_manual_input_helper_instance.save_book_mark(request_parser, 'test_token')
        self.mock_api_messages.assert_called_with('exists', 'Test Bookmark')
        self.assertEqual(response, self.mock_api_messages.return_value)

    def test_update_book_mark_not_exists(self):
        request_parser = {'bookmark_id': 123, 'bookmark_name': 'Updated BM'}
        self.mock_db_session.query().filter_by().first.return_value = None
        response = self.kpi_manual_input_helper_instance.update_book_mark(request_parser)
        self.mock_api_messages.assert_called_with('not_exists', 'bookmark_id 123')
        self.assertEqual(response, self.mock_api_messages.return_value)

    def test_delete_book_mark_not_exists(self):
        self.mock_db_session.query().filter_by().first.return_value = None
        response = self.kpi_manual_input_helper_instance.delete_book_mark(123)
        self.mock_api_messages.assert_called_with('not_exists', 'bookmark_id 123')
        self.assertEqual(response, self.mock_api_messages.return_value)

    def test_fetch_book_mark_view_not_exists(self):
        self.mock_db_session.query().filter_by().first.return_value = None
        response = self.kpi_manual_input_helper_instance.fetch_book_mark_view(123)
        self.mock_api_messages.assert_called_with('not_exists', 123)
        self.assertEqual(response, self.mock_api_messages.return_value)

    def test_rename_bookmark_not_exists(self):
        request = {'bookmark_id': 123, 'bookmark_name': 'New Name'}
        self.mock_db_session.query().filter_by().first.return_value = None
        response = self.kpi_manual_input_helper_instance.rename_bookmark(request)
        self.mock_api_messages.assert_called_with('not_exists', 'bookmark_id 123')
        self.assertEqual(response, self.mock_api_messages.return_value)

    def test_rename_bookmark_empty_name(self):
        request = {'bookmark_id': 123, 'bookmark_name': ''}
        self.mock_db_session.query().filter_by().first.return_value = MagicMock()
        response = self.kpi_manual_input_helper_instance.rename_bookmark(request)
        self.mock_api_messages.assert_called_with('renamed', '')
        self.assertEqual(response, self.mock_api_messages.return_value)

if __name__ == '__main__':
    unittest.main()
