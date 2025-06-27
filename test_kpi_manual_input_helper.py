import unittest
from unittest.mock import patch, MagicMock
import sys
import os
import datetime
from datetime import datetime
from os import environ
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))
from src.db import db
import json
from src.models.kpi_bookmark import Bookmark, BookmarkTypeStatic, BookmarkVal, User
from src.app import app  # Adjust the import according to your project structure
from src.helper.kpi_manual_input_helper import kpi_manual_input
from src.constants.api_messages import api_messages
import logging

# Configure logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
console_handler.setFormatter(formatter)
logger.addHandler(console_handler)

class TestKpiManualInputHelper(unittest.TestCase):

    def setUp(self):
        self.patcher_db_session = patch('src.helper.kpi_manual_input_helper.db.session')
        self.mock_db_session = self.patcher_db_session.start()
        self.patcher_api_messages = patch('src.helper.kpi_manual_input_helper.api_messages')
        self.mock_api_messages = self.patcher_api_messages.start()
        self.kpi_manual_input_helper_instance = kpi_manual_input()
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
        request_parser = {'attribute': [1], 'bookmark_name': 'Test BookmarkNew1412', 'bk_typ_id': 123, 'oid': 456}
        self.mock_db_session.query().filter_by().first.side_effect = [MagicMock(), None, None]
        patcher_save_user = patch.object(self.kpi_manual_input_helper_instance, 'save_user')
        mock_save_user = patcher_save_user.start()
        response = self.kpi_manual_input_helper_instance.save_book_mark(request_parser, 'test_token')
        mock_save_user.assert_called_with('test_token')
        patcher_save_user.stop()
        # self.mock_api_messages.assert_called_with('insert', 'Test BookmarkNew1412')
        print('reponse....',response)
        self.assertEqual(response, self.mock_api_messages.return_value)

    def test_save_book_mark_exists(self):
        request_parser = {'attribute': [1], 'bookmark_name': 'Test Bookmark', 'bk_typ_id': 123, 'oid': 456}
        self.mock_db_session.query().filter_by().first.side_effect = [MagicMock(), MagicMock(), None]
        response = self.kpi_manual_input_helper_instance.save_book_mark(request_parser, 'test_token')
        self.mock_api_messages.assert_called_with('exists', 'Test Bookmark')
        self.assertEqual(response, self.mock_api_messages.return_value)

    def test_save_book_mark_excption(self):
        request_parser = {'attribute': [1], 'bookmark_name': 'Test Bookmark', '': 123, 'oid': 456}
        self.mock_db_session.query().filter_by().first.side_effect = [MagicMock(), MagicMock(), None]
        response = self.kpi_manual_input_helper_instance.save_book_mark(request_parser, 'test_token')
        self.mock_api_messages.assert_called_with('error', "'bk_typ_id'")
        self.assertEqual(response, self.mock_api_messages.return_value)

    def test_update_book_mark_not_exists(self):
        request_parser = {'bookmark_id': 123, 'bookmark_name': 'Updated Bookmark'}
        self.mock_db_session.query().filter_by().first.return_value = None
        response = self.kpi_manual_input_helper_instance.update_book_mark(request_parser)
        self.mock_api_messages.assert_called_with('not_exists', 'bookmark_id 123')
        self.assertEqual(response, self.mock_api_messages.return_value)

    def test_update_book_mark_success(self):
        request_parser = {'bookmark_id': 123, 'bookmark_name': 'Updated Bookmark'}
        self.mock_db_session.query().filter_by().first.return_value = MagicMock()
        patcher_update_val_record = patch.object(self.kpi_manual_input_helper_instance, 'update_bookmark_val_record')
        mock_update_val_record = patcher_update_val_record.start()
        response = self.kpi_manual_input_helper_instance.update_book_mark(request_parser)
        mock_update_val_record.assert_called_with(request_parser)
        patcher_update_val_record.stop()
        self.mock_api_messages.assert_called_with('update', 'Updated Bookmark')
        self.assertEqual(response, self.mock_api_messages.return_value)

    def test_delete_book_mark_not_exists(self):
        self.mock_db_session.query().filter_by().first.return_value = None
        response = self.kpi_manual_input_helper_instance.delete_book_mark(123)
        self.mock_api_messages.assert_called_with('not_exists', 'bookmark_id 123')
        self.assertEqual(response, self.mock_api_messages.return_value)
        
    def test_update_book_mark_exception(self):
        request_parser = {'bookmark_id': 123, '': 'Updated Bookmark'}
        
        self.mock_db_session.query().filter_by().first.side_effect = [MagicMock(), MagicMock()]
        response = self.kpi_manual_input_helper_instance.update_book_mark(request_parser)
        
        self.mock_api_messages.assert_called_with('error', "'bookmark_name'")
        self.assertEqual(response, self.mock_api_messages.return_value)

    def test_delete_book_mark_success(self):
        bookmark_mock = MagicMock()
        self.mock_db_session.query().filter_by().first.return_value = bookmark_mock
        bookmark_val_mock = [MagicMock()]
        self.mock_db_session.query().filter_by().all.return_value = bookmark_val_mock
        response = self.kpi_manual_input_helper_instance.delete_book_mark(123)
        self.mock_db_session.commit.assert_called()
        self.mock_api_messages.assert_called_with('delete', str(123))
        self.assertEqual(response, self.mock_api_messages.return_value)
        
    def test_delete_book_mark_exception(self):
        bookmark_mock = MagicMock()
        self.mock_db_session.query().filter_by().first.return_value = bookmark_mock
        bookmark_val_mock = [MagicMock()]
        self.mock_db_session.query().filter_by().all.return_value = bookmark_val_mock
        response = self.kpi_manual_input_helper_instance.delete_book_mark()
        self.mock_db_session.commit.assert_called()
        self.mock_api_messages.assert_called_with('delete', 123)
        self.assertEqual(response, self.mock_api_messages.return_value)


    def test_fetch_book_mark_success(self):
        request_parser = {'oid': 456, 'bk_typ_id': 123}
        bookmark_mock = [MagicMock()]
        self.mock_db_session.query().filter_by().all.return_value = bookmark_mock
        patcher_dumps = patch('src.helper.kpi_manual_input_helper.kpi_input_bookmark_fetch_list_schema.dumps', return_value='json_data')
        mock_dumps = patcher_dumps.start()
        response = self.kpi_manual_input_helper_instance.fetch_book_mark(request_parser)
        patcher_dumps.stop()
        self.assertEqual(response, (json.loads('json_data'), 200))

    def test_fetch_book_mark_view_not_exists(self):
        self.mock_db_session.query().filter_by().first.return_value = None
        response = self.kpi_manual_input_helper_instance.fetch_book_mark_view(123)
        self.mock_api_messages.assert_called_with('not_exists', 123)
        self.assertEqual(response, self.mock_api_messages.return_value)

    def test_fetch_book_mark_view_success(self):
        bookmark_mock = MagicMock()
        bookmark_val_mock = [MagicMock()]
        self.mock_db_session.query().filter_by().first.return_value = bookmark_mock
        self.mock_db_session.query().filter_by().all.return_value = bookmark_val_mock
        patcher_serialize = patch('src.helper.kpi_manual_input_helper.serialize_sqlalchemy_object', side_effect=lambda x: x.__dict__)
        mock_serialize = patcher_serialize.start()
        response = self.kpi_manual_input_helper_instance.fetch_book_mark_view(123)
        patcher_serialize.stop()
        self.assertEqual(response[1], 200)

    def test_rename_bookmark_not_exists(self):
        request = {'bookmark_id': 123, 'bookmark_name': 'New Name'}
        self.mock_db_session.query().filter_by().first.return_value = None
        response = self.kpi_manual_input_helper_instance.rename_bookmark(request)
        self.mock_api_messages.assert_called_with('not_exists', 'bookmark_id 123')
        self.assertEqual(response, self.mock_api_messages.return_value)

    def test_rename_bookmark_success(self):
        request = {'bookmark_id': 123, 'bookmark_name': 'New Name'}
        bookmark_mock = MagicMock()
        self.mock_db_session.query().filter_by().first.return_value = bookmark_mock
        response = self.kpi_manual_input_helper_instance.rename_bookmark(request)
        self.mock_db_session.commit.assert_called()
        self.mock_api_messages.assert_called_with('renamed', 'New Name')
        self.assertEqual(response, self.mock_api_messages.return_value)

    def test_update_bookmark_val_record_success(self):
        request_parser = {'bookmark_id': 123, 'bookmark_name': 'Updated Bookmark'}
        patcher_expire = patch.object(self.kpi_manual_input_helper_instance, 'expire_existing_bookmark_vals')
        mock_expire = patcher_expire.start()
        patcher_fetch_columns = patch.object(self.kpi_manual_input_helper_instance, 'fetch_static_type_columns', return_value=('mapping', 5, 'attributes'))
        mock_fetch_columns = patcher_fetch_columns.start()
        patcher_add_records = patch.object(self.kpi_manual_input_helper_instance, 'add_bookmark_val_records')
        mock_add_records = patcher_add_records.start()
        response = self.kpi_manual_input_helper_instance.update_bookmark_val_record(request_parser)
        mock_expire.assert_called_with(123)
        mock_fetch_columns.assert_called_with(request_parser)
        mock_add_records.assert_called_with(123, 'mapping', 5, 'attributes')
        patcher_expire.stop()
        patcher_fetch_columns.stop()
        patcher_add_records.stop()
        self.mock_api_messages.assert_called_with('update', 'Updated Bookmark')
        self.assertEqual(response, self.mock_api_messages.return_value)

    def test_fetch_static_type_columns_success(self):
        request_parser = {'bk_typ_id': 123, 'attribute': {'key': ['value']}}
        bookmark_type_static_mock = MagicMock()
        self.mock_db_session.query().filter_by().first.return_value = bookmark_type_static_mock
        response = self.kpi_manual_input_helper_instance.fetch_static_type_columns(request_parser)
        self.assertEqual(response, (bookmark_type_static_mock.attr, 1, request_parser['attribute']))

    def test_save_user_success(self):
        token = 'test_token'
        user_data = {'user_id': 123}
        patcher_get_user_data = patch('src.helper.kpi_manual_input_helper.get_user_data_from_token', return_value=user_data)
        mock_get_user_data = patcher_get_user_data.start()
        patcher_user = patch('src.helper.kpi_manual_input_helper.User')
        mock_user = patcher_user.start()
        user_mock = MagicMock()
        mock_user.return_value = user_mock
        self.kpi_manual_input_helper_instance.save_user(token)
        mock_get_user_data.stop()
        mock_user.stop()
        self.mock_db_session.add.assert_called_with(user_mock)
        self.mock_db_session.commit.assert_called()

    def test_save_user_exception(self):
        token = 'test_token'
        patcher_get_user_data = patch('src.helper.kpi_manual_input_helper.get_user_data_from_token', return_value=None)
        mock_get_user_data = patcher_get_user_data.start()
        try:
            self.kpi_manual_input_helper_instance.save_user(token)
        except Exception:
            exception_raised = True
        else:
            exception_raised = False
        mock_get_user_data.stop()
        self.assertTrue(exception_raised)

    def test_expire_existing_bookmark_vals_success(self):
        bookmark_id = 123
        bookmark_vals_mock = [MagicMock()]
        self.mock_db_session.query().filter_by().all.return_value = bookmark_vals_mock
        self.kpi_manual_input_helper_instance.expire_existing_bookmark_vals(bookmark_id)
        for val in bookmark_vals_mock:
            val.is_active = 'N'
        self.mock_db_session.commit.assert_called()

    def test_add_bookmark_val_records_success(self):
        bookmark_id = 123
        mapping = {'key': 'value'}
        max_len = 1
        attributes = {'key': ['value']}
        patcher_bookmark_val = patch('src.helper.kpi_manual_input_helper.Bookmark_Val')
        mock_bookmark_val = patcher_bookmark_val.start()
        self.kpi_manual_input_helper_instance.add_bookmark_val_records(bookmark_id, mapping, max_len, attributes)
        patcher_bookmark_val.stop()
        self.assertEqual(self.mock_db_session.add.call_count, 1)
        self.mock_db_session.commit.assert_called()

    def test_fetch_static_type_columns_not_exists(self):
        request_parser = {'bk_typ_id': 123, 'attribute': {'key': ['value']}}
        self.mock_db_session.query().filter_by().first.return_value = None
        try:
            self.kpi_manual_input_helper_instance.fetch_static_type_columns(request_parser)
        except Exception:
            exception_raised = False
        else:
            exception_raised = False
        self.assertTrue(exception_raised)

    # def test_save_user_invalid_token(self):
    #     token = 'invalid_token'
    #     patcher_get_user_data = patch('src.helper.kpi_manual_input_helper.get_user_data_from_token', return_value=None)
    #     mock_get_user_data = patcher_get_user_data.start()
    #     try:
    #         self.kpi_manual_input_helper_instance.save_user(token)
    #     except Exception:
    #         exception_raised = True
    #     else:
    #         exception_raised = False
    #     mock_get_user_data.stop()
    #     self.assertTrue(exception_raised)

    def test_expire_existing_bookmark_vals_no_records(self):
        bookmark_id = 123
        self.mock_db_session.query().filter_by().all.return_value = []
        self.kpi_manual_input_helper_instance.expire_existing_bookmark_vals(bookmark_id)
        self.mock_db_session.commit.assert_called()

    def test_add_bookmark_val_records_no_attributes(self):
        bookmark_id = 123
        mapping = {}
        max_len = 0
        attributes = {}
        patcher_bookmark_val = patch('src.helper.kpi_manual_input_helper.Bookmark_Val')
        mock_bookmark_val = patcher_bookmark_val.start()
        self.kpi_manual_input_helper_instance.add_bookmark_val_records(bookmark_id, mapping, max_len, attributes)
        patcher_bookmark_val.stop()
        self.assertEqual(self.mock_db_session.add.call_count, 0)
        self.mock_db_session.commit.assert_not_called()

    def test_rename_bookmark_empty_name(self):
        request = {'bookmark_id': 123, 'bookmark_name': ''}
        self.mock_db_session.query().filter_by().first.return_value = MagicMock()
        response = self.kpi_manual_input_helper_instance.rename_bookmark(request)
        self.mock_db_session.commit.assert_called()
        self.mock_api_messages.assert_called_with('renamed', '')
        self.assertEqual(response, self.mock_api_messages.return_value)

    def test_fetch_book_mark_view_with_vals(self):
        bookmark_mock = MagicMock()
        bookmark_val_mock = [MagicMock(), MagicMock()]
        self.mock_db_session.query().filter_by().first.return_value = bookmark_mock
        self.mock_db_session.query().filter_by().all.return_value = bookmark_val_mock
        patcher_serialize = patch('src.helper.kpi_manual_input_helper.serialize_sqlalchemy_object', side_effect=lambda x: x.__dict__)
        mock_serialize = patcher_serialize.start()
        response = self.kpi_manual_input_helper_instance.fetch_book_mark_view(123)
        patcher_serialize.stop()
        self.assertEqual(response[1], 200)
    
    @patch('src.helper.kpi_manual_input_helper.db.session.add')  # Update with the correct import path
    def test_add_bookmark_val_records(self, mock_session_add):
        # Prepare test data
        bookmark_id = 1
        dynamic_column_mapping = {
            'column1': 'mapped_column1',
            'column2': 'mapped_column2'
        }
        max_length = 3
        atr_obj = {
            'column1': ['value11', 'value12', 'value13'],
            'column2': ['value21', 'value22']
        }

        # Call the method
        self.kpi_manual_input_helper_instance.add_bookmark_val_records(bookmark_id, dynamic_column_mapping, max_length, atr_obj)

        # Assert the correct calls to session.add
        expected_records = [
            {'bookmark_id': 1, 'rec_start_date': db.func.now(), 'created_date': db.func.now(), 'rec_end_date': datetime(9999, 12, 31), 'is_deleted': 0, 'mapped_column1': 'value11', 'mapped_column2': 'value21'},
            {'bookmark_id': 1, 'rec_start_date': db.func.now(), 'created_date': db.func.now(), 'rec_end_date': datetime(9999, 12, 31), 'is_deleted': 0, 'mapped_column1': 'value12', 'mapped_column2': 'value22'},
            {'bookmark_id': 1, 'rec_start_date': db.func.now(), 'created_date': db.func.now(), 'rec_end_date': datetime(9999, 12, 31), 'is_deleted': 0, 'mapped_column1': 'value13', 'mapped_column2': None}
        ]

        calls = [mock_session_add.call_args_list[i][0][0].__dict__ for i in range(len(mock_session_add.call_args_list))]
        self.assertEqual(calls, expected_records)
        
    @patch('src.helper.kpi_manual_input_helper.db.session.query')  # Update with the correct import path
    @patch('src.helper.kpi_manual_input_helper.db.session.add')  # Update with the correct import path
    def test_expire_existing_bookmark_vals(self, mock_session_add, mock_session_query):
        # Prepare test data
        bookmark_id = 1
        mock_record1 = MagicMock()
        mock_record2 = MagicMock()
        mock_record3 = MagicMock()
        mock_record1.rec_end_date = datetime(9999, 12, 31)
        mock_record2.rec_end_date = datetime(9999, 12, 31)
        mock_record3.rec_end_date = datetime(9999, 12, 31)
        mock_session_query.return_value.filter_by.return_value.all.return_value = [mock_record1, mock_record2, mock_record3]

        # Call the method
        self.manager.expire_existing_bookmark_vals(bookmark_id)

        # Assert the correct calls to session.add
        mock_session_add.assert_any_call(mock_record1)
        mock_session_add.assert_any_call(mock_record2)
        mock_session_add.assert_any_call(mock_record3)

        # Assert rec_end_date update
        self.assertNotEqual(mock_record1.rec_end_date, datetime(9999, 12, 31))
        self.assertNotEqual(mock_record2.rec_end_date, datetime(9999, 12, 31))
        self.assertNotEqual(mock_record3.rec_end_date, datetime(9999, 12, 31))
        
    @patch('src.helper.kpi_manual_input_helper.serialize_sqlalchemy_object')
    @patch('src.helper.kpi_manual_input_helper.db.session.query')
    def test_construct_bookmark_response(self, mock_query, mock_serialize):
        # Mock the behavior of serialize_sqlalchemy_object
        mock_serialize.side_effect = lambda obj: {'mock_serialized': obj}

        # Mock the query and its return value
        mock_query.return_value.filter_by.return_value.first.return_value = self.mock_book_mark_type_static_tbl
        self.mock_book_mark_type_static_tbl.bk_typ_id = 'mock_bk_typ_id'

        # Mock the fetch_bookmark_record and fetch_bookmark_val_record
        self.mock_fetch_bookmark_record.return_value = {'bookmark_id': 1, 'bookmark_name': 'Mock Bookmark', 'bk_typ_id': 'mock_bk_typ_id'}
        self.mock_fetch_bookmark_val_record[0].return_value = {'attr1': 'value1'}
        self.mock_fetch_bookmark_val_record[1].return_value = {'attr2': 'value2'}

        # Call the method under test
        result = self.manager.construct_bookmark_response(self.mock_fetch_bookmark_record, self.mock_fetch_bookmark_val_record)

        # Assert the result
        expected_result = {
            'bookmark_id': 1,
            'bookmark_name': 'Mock Bookmark',
            'bk_typ_id': 'mock_bk_typ_id',
            'attribute': {
                'attr1': ['value1'],
                'attr2': ['value2']
            }
        }
        self.assertEqual(result, expected_result)
        
    @patch('src.helper.kpi_manual_input_helper.db.session.add')
    @patch('src.helper.kpi_manual_input_helper.db.session.commit')
    @patch('src.common_helper.common_helper.get_user_details')
    def test_save_user(self, mock_get_user_details, mock_commit, mock_add):
        # Mock the return value of get_user_details
       
        mock_user_data = {
            'id': 'mock_id',
            'displayName': 'John Doe',
            'surname': 'Doe',
            'role': 'admin',
            'mail': 'john.doe@example.com'
        }
        mock_get_user_details.return_value.json.return_value = mock_user_data

        # Call the method under test
        self.kpi_manual_input_helper_instance.save_user(os.environ.get('TEST_ADMIN_TOKEN'))

        # Assertions
        mock_get_user_details.assert_called_once_with({"Authorization": f"Bearer {os.environ.get('TEST_ADMIN_TOKEN')}"})
        mock_user_tbl_instance = self.mock_user_tbl.return_value
        mock_user_tbl_instance.__init__.assert_called_once_with(
            oid='mock_id',
            fname='John Doe',
            lname='Doe',
            role='admin',
            email_id='john.doe@example.com'
        )
        mock_add.assert_called_once_with(mock_user_tbl_instance)
        mock_commit.assert_called_once()