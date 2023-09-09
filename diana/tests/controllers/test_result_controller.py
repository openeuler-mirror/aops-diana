#!/usr/bin/python3
# ******************************************************************************
# Copyright (c) Huawei Technologies Co., Ltd. 2022-2022. All rights reserved.
# licensed under the Mulan PSL v2.
# You can use this software according to the terms and conditions of the Mulan PSL v2.
# You may obtain a copy of Mulan PSL v2 at:
#     http://license.coscl.org.cn/MulanPSL2
# THIS SOFTWARE IS PROVIDED ON AN 'AS IS' BASIS, WITHOUT WARRANTIES OF ANY KIND, EITHER EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO NON-INFRINGEMENT, MERCHANTABILITY OR FIT FOR A PARTICULAR
# PURPOSE.
# See the Mulan PSL v2 for more details.
# ******************************************************************************/
from unittest import mock
from urllib.parse import urlencode

from sqlalchemy.orm import scoping

from vulcanus.restful.resp.state import PARAM_ERROR, TOKEN_ERROR, SUCCEED, NO_DATA
from diana.database.dao.result_dao import ResultDao
from diana.tests import BaseTestCase


header = {"Content-Type": "application/json; charset=UTF-8"}
header_with_token = {"Content-Type": "application/json; charset=UTF-8", "access_token": "123456"}


class TestResultController(BaseTestCase):
    def setUp(self) -> None:
        super().setUp()
        app = self.init_application()
        self.client = app.test_client()

    @mock.patch.object(ResultDao, 'query_result_host')
    @mock.patch.object(ResultDao, 'connect')
    @mock.patch.object(scoping, 'scoped_session')
    def test_get_host_result_should_return_check_result_result_when_input_correct_alert_id(
        self, mock_session, mock_connect, mock_query_result_host
    ):
        mock_result = {
            "result": {
                "sasda": {
                    "host_ip": "hsadghaj",
                    "host_name": "adhj",
                    "is_root": True,
                    "host_check_result": [
                        {"sasda": {"is_root": False, "label": "hadjhsjk", "metric_name": "adsda", "time": 20180106}},
                        {"sasda": {"is_root": True, "label": "assda", "metric_name": "1231", "time": 3}},
                    ],
                }
            }
        }
        mock_session.return_value = ''
        mock_connect.return_value = True
        mock_query_result_host.return_value = SUCCEED, {"result": mock_result}
        mock_alert_id = 'test'
        resp = self.client.get(f'/check/result/host?alert_id={mock_alert_id}', headers=header_with_token)
        self.assertEqual(mock_result, resp.json.get('result'))

    @mock.patch.object(ResultDao, 'query_result_host')
    @mock.patch.object(ResultDao, 'connect')
    @mock.patch.object(scoping, 'scoped_session')
    def test_get_host_result_should_return_empty_result_when_input_incorrect_alert_id(
        self, mock_session, mock_connect, mock_query_result_host
    ):
        mock_result = {"result": {}}
        mock_session.return_value = ''
        mock_connect.return_value = True
        mock_query_result_host.return_value = SUCCEED, {"result": mock_result}
        mock_alert_id = 'test'
        resp = self.client.get(f'/check/result/host?alert_id={mock_alert_id}', headers=header_with_token)
        self.assertEqual(mock_result, resp.json.get('result'))

    def test_get_host_result_should_param_error_result_when_no_input(
        self,
    ):
        resp = self.client.get(f'/check/result/host', headers=header_with_token)
        self.assertEqual(PARAM_ERROR, resp.json.get('label'))

    @mock.patch.object(ResultDao, 'query_result_host')
    @mock.patch.object(ResultDao, 'connect')
    @mock.patch.object(scoping, 'scoped_session')
    def test_get_host_result_should_return_param_error_when_input_alert_id_is_null(
        self, mock_session, mock_connect, mock_query_result_host
    ):
        mock_result = {"result": {}}
        mock_session.return_value = ''
        mock_connect.return_value = True
        mock_query_result_host.return_value = SUCCEED, {"result": mock_result}
        mock_alert_id = ''
        resp = self.client.get(f'/check/result/host?alert_id={mock_alert_id}', headers=header_with_token)
        self.assertEqual(PARAM_ERROR, resp.json.get('label'))

    def test_get_host_result_should_return_token_error_when_input_with_no_token(self):
        mock_alert_id = 'test'
        resp = self.client.get(f'/check/result/host?alert_id={mock_alert_id}', headers=header)
        self.assertEqual(TOKEN_ERROR, resp.json.get('label'))

    def test_get_host_result_should_return_405_when_request_by_other_method(self):
        mock_alert_id = 'test'
        resp = self.client.post(f'/check/result/host?alert_id={mock_alert_id}', headers=header_with_token)
        self.assertEqual(405, resp.status_code)

    @mock.patch.object(ResultDao, '_check_result_host_rows_to_list')
    @mock.patch.object(ResultDao, '_query_check_result_host_list')
    @mock.patch.object(ResultDao, 'connect')
    @mock.patch.object(mock.Mock, 'all', create=True)
    @mock.patch.object(scoping, 'scoped_session')
    @mock.patch('diana.database.dao.result_dao.sort_and_page')
    def test_query_result_list_should_return_result_list_when_input_correct(
        self, mock_sort, mock_session, mock_count, mock_connect, mock_query_from_database, mock_rows_to_list
    ):
        mock_param = {
            'page': '1',
            'per_page': '5',
            'domain': 'test',
            'level': 'test',
            'sort': 'time',
            'direction': 'desc',
        }

        check_result_list = [
            {
                "alert_id": "alert_1",
                "alert_name": "test",
                "confirmed": False,
                "domain": "test",
                "host_num": 1,
                "level": "test",
                "time": 20201111,
                "workflow_id": "workflow_id_1",
                "workflow_name": "workflow_name_1",
            },
            {
                "alert_id": "alert_2",
                "alert_name": "test",
                "confirmed": False,
                "domain": "test",
                "host_num": 2,
                "level": "test",
                "time": 20180102,
                "workflow_id": "workflow_id_2",
                "workflow_name": "workflow_name_2",
            },
        ]

        mock_session.return_value = ''
        mock_connect.return_value = True
        mock_count.return_value = 'a' * 2
        mock_sort.return_value = [], 1
        mock_query_from_database.return_value = mock.Mock
        mock_rows_to_list.return_value = check_result_list
        resp = self.client.get(f'/check/result/list?{urlencode(mock_param)}', headers=header_with_token)
        self.assertEqual(check_result_list, resp.json.get('result'))

    @mock.patch.object(ResultDao, '_check_result_host_rows_to_list')
    @mock.patch.object(ResultDao, '_query_check_result_host_list')
    @mock.patch.object(ResultDao, 'connect')
    @mock.patch.object(mock.Mock, 'all', create=True)
    @mock.patch.object(scoping, 'scoped_session')
    @mock.patch('diana.database.dao.result_dao.sort_and_page')
    def test_query_result_list_should_return_result_list_when_input_with_no_page(
        self, mock_sort, mock_session, mock_count, mock_connect, mock_query_from_database, mock_rows_to_list
    ):
        mock_param = {'per_page': '5', 'domain': 'test', 'level': 'test', 'sort': 'time', 'direction': 'desc'}

        check_result_list = [
            {
                "alert_id": "alert_1",
                "alert_name": "test",
                "confirmed": False,
                "domain": "test",
                "host_num": 1,
                "level": "test",
                "time": 20201111,
                "workflow_id": "workflow_id_1",
                "workflow_name": "workflow_name_1",
            },
            {
                "alert_id": "alert_2",
                "alert_name": "test",
                "confirmed": False,
                "domain": "test",
                "host_num": 2,
                "level": "test",
                "time": 20180102,
                "workflow_id": "workflow_id_2",
                "workflow_name": "workflow_name_2",
            },
        ]

        mock_session.return_value = ''
        mock_connect.return_value = True
        mock_count.return_value = 'a' * 2
        mock_sort.return_value = [], 1
        mock_query_from_database.return_value = mock.Mock
        mock_rows_to_list.return_value = check_result_list
        resp = self.client.get(f'/check/result/list?{urlencode(mock_param)}', headers=header_with_token)
        self.assertEqual(check_result_list, resp.json.get('result'))

    @mock.patch.object(ResultDao, '_check_result_host_rows_to_list')
    @mock.patch.object(ResultDao, '_query_check_result_host_list')
    @mock.patch.object(ResultDao, 'connect')
    @mock.patch.object(mock.Mock, 'all', create=True)
    @mock.patch.object(scoping, 'scoped_session')
    @mock.patch('diana.database.dao.result_dao.sort_and_page')
    def test_query_result_list_should_return_result_list_when_input_with_no_perpage(
        self, mock_sort, mock_session, mock_count, mock_connect, mock_query_from_database, mock_rows_to_list
    ):
        mock_param = {'page': '1', 'domain': 'test', 'level': 'test', 'sort': 'time', 'direction': 'desc'}

        check_result_list = [
            {
                "alert_id": "alert_1",
                "alert_name": "test",
                "confirmed": False,
                "domain": "test",
                "host_num": 1,
                "level": "test",
                "time": 20201111,
                "workflow_id": "workflow_id_1",
                "workflow_name": "workflow_name_1",
            },
            {
                "alert_id": "alert_2",
                "alert_name": "test",
                "confirmed": False,
                "domain": "test",
                "host_num": 2,
                "level": "test",
                "time": 20180102,
                "workflow_id": "workflow_id_2",
                "workflow_name": "workflow_name_2",
            },
        ]

        mock_session.return_value = ''
        mock_connect.return_value = True
        mock_count.return_value = 'a' * 2
        mock_sort.return_value = [], 1
        mock_query_from_database.return_value = mock.Mock
        mock_rows_to_list.return_value = check_result_list
        resp = self.client.get(f'/check/result/list?{urlencode(mock_param)}', headers=header_with_token)
        self.assertEqual(check_result_list, resp.json.get('result'))

    @mock.patch.object(ResultDao, '_check_result_host_rows_to_list')
    @mock.patch.object(ResultDao, '_query_check_result_host_list')
    @mock.patch.object(ResultDao, 'connect')
    @mock.patch.object(mock.Mock, 'all', create=True)
    @mock.patch.object(scoping, 'scoped_session')
    @mock.patch('diana.database.dao.result_dao.sort_and_page')
    def test_query_result_list_should_return_result_list_when_input_with_no_domain(
        self, mock_sort, mock_session, mock_count, mock_connect, mock_query_from_database, mock_rows_to_list
    ):
        mock_param = {'page': '1', 'per_page': '5', 'level': 'test', 'sort': 'time', 'direction': 'desc'}

        check_result_list = [
            {
                "alert_id": "alert_1",
                "alert_name": "test",
                "confirmed": False,
                "domain": "test1",
                "host_num": 1,
                "level": "test",
                "time": 20201111,
                "workflow_id": "workflow_id_1",
                "workflow_name": "workflow_name_1",
            },
            {
                "alert_id": "alert_2",
                "alert_name": "test",
                "confirmed": False,
                "domain": "test2",
                "host_num": 2,
                "level": "test",
                "time": 20180102,
                "workflow_id": "workflow_id_2",
                "workflow_name": "workflow_name_2",
            },
        ]

        mock_session.return_value = ''
        mock_connect.return_value = True
        mock_count.return_value = 'a' * 2
        mock_sort.return_value = [], 1
        mock_query_from_database.return_value = mock.Mock
        mock_rows_to_list.return_value = check_result_list
        resp = self.client.get(f'/check/result/list?{urlencode(mock_param)}', headers=header_with_token)
        self.assertEqual(check_result_list, resp.json.get('result'))

    @mock.patch.object(ResultDao, '_check_result_host_rows_to_list')
    @mock.patch.object(ResultDao, '_query_check_result_host_list')
    @mock.patch.object(ResultDao, 'connect')
    @mock.patch.object(mock.Mock, 'all', create=True)
    @mock.patch.object(scoping, 'scoped_session')
    @mock.patch('diana.database.dao.result_dao.sort_and_page')
    def test_query_result_list_should_return_result_list_when_input_with_no_level(
        self, mock_sort, mock_session, mock_count, mock_connect, mock_query_from_database, mock_rows_to_list
    ):
        mock_param = {'page': '1', 'per_page': '5', 'domain': 'test', 'sort': 'time', 'direction': 'desc'}

        check_result_list = [
            {
                "alert_id": "alert_1",
                "alert_name": "test",
                "confirmed": False,
                "domain": "test",
                "host_num": 1,
                "level": "test1",
                "time": 20201111,
                "workflow_id": "workflow_id_1",
                "workflow_name": "workflow_name_1",
            },
            {
                "alert_id": "alert_2",
                "alert_name": "test",
                "confirmed": False,
                "domain": "test",
                "host_num": 2,
                "level": "test2",
                "time": 20180102,
                "workflow_id": "workflow_id_2",
                "workflow_name": "workflow_name_2",
            },
        ]

        mock_session.return_value = ''
        mock_connect.return_value = True
        mock_count.return_value = 'a' * 2
        mock_sort.return_value = [], 1
        mock_query_from_database.return_value = mock.Mock
        mock_rows_to_list.return_value = check_result_list
        resp = self.client.get(f'/check/result/list?{urlencode(mock_param)}', headers=header_with_token)
        self.assertEqual(check_result_list, resp.json.get('result'))

    @mock.patch.object(ResultDao, '_check_result_host_rows_to_list')
    @mock.patch.object(ResultDao, '_query_check_result_host_list')
    @mock.patch.object(ResultDao, 'connect')
    @mock.patch.object(mock.Mock, 'all', create=True)
    @mock.patch.object(scoping, 'scoped_session')
    @mock.patch('diana.database.dao.result_dao.sort_and_page')
    def test_query_result_list_should_return_result_list_when_input_with_no_sort(
        self, mock_sort, mock_session, mock_count, mock_connect, mock_query_from_database, mock_rows_to_list
    ):
        mock_param = {'page': '1', 'per_page': '5', 'domain': 'test', 'level': 'test', 'direction': 'desc'}

        check_result_list = [
            {
                "alert_id": "alert_1",
                "alert_name": "test",
                "confirmed": False,
                "domain": "test",
                "host_num": 1,
                "level": "test1",
                "time": 20180102,
                "workflow_id": "workflow_id_1",
                "workflow_name": "workflow_name_1",
            },
            {
                "alert_id": "alert_2",
                "alert_name": "test",
                "confirmed": False,
                "domain": "test",
                "host_num": 2,
                "level": "test2",
                "time": 20201111,
                "workflow_id": "workflow_id_2",
                "workflow_name": "workflow_name_2",
            },
        ]

        mock_session.return_value = ''
        mock_connect.return_value = True
        mock_count.return_value = 'a' * 2
        mock_sort.return_value = [], 1
        mock_query_from_database.return_value = mock.Mock
        mock_rows_to_list.return_value = check_result_list
        resp = self.client.get(f'/check/result/list?{urlencode(mock_param)}', headers=header_with_token)
        self.assertEqual(check_result_list, resp.json.get('result'))

    @mock.patch.object(ResultDao, '_check_result_host_rows_to_list')
    @mock.patch.object(ResultDao, '_query_check_result_host_list')
    @mock.patch.object(ResultDao, 'connect')
    @mock.patch.object(mock.Mock, 'all', create=True)
    @mock.patch.object(scoping, 'scoped_session')
    @mock.patch('diana.database.dao.result_dao.sort_and_page')
    def test_query_result_list_should_return_result_list_when_input_with_no_direction(
        self, mock_sort, mock_session, mock_count, mock_connect, mock_query_from_database, mock_rows_to_list
    ):
        mock_param = {
            'page': '1',
            'per_page': '5',
            'domain': 'test',
            'level': 'test',
            'sort': 'time',
        }

        check_result_list = [
            {
                "alert_id": "alert_1",
                "alert_name": "test",
                "confirmed": False,
                "domain": "test",
                "host_num": 1,
                "level": "test1",
                "time": 20180102,
                "workflow_id": "workflow_id_1",
                "workflow_name": "workflow_name_1",
            },
            {
                "alert_id": "alert_2",
                "alert_name": "test",
                "confirmed": False,
                "domain": "test",
                "host_num": 2,
                "level": "test2",
                "time": 20201111,
                "workflow_id": "workflow_id_2",
                "workflow_name": "workflow_name_2",
            },
        ]

        mock_session.return_value = ''
        mock_connect.return_value = True
        mock_count.return_value = 'a' * 2
        mock_sort.return_value = [], 1
        mock_query_from_database.return_value = mock.Mock
        mock_rows_to_list.return_value = check_result_list
        resp = self.client.get(f'/check/result/list?{urlencode(mock_param)}', headers=header_with_token)
        self.assertEqual(check_result_list, resp.json.get('result'))

    @mock.patch.object(ResultDao, '_check_result_host_rows_to_list')
    @mock.patch.object(ResultDao, '_query_check_result_host_list')
    @mock.patch.object(ResultDao, 'connect')
    @mock.patch.object(mock.Mock, 'all', create=True)
    @mock.patch.object(scoping, 'scoped_session')
    @mock.patch('diana.database.dao.result_dao.sort_and_page')
    def test_query_result_list_should_return_result_list_when_input_with_no_direction(
        self, mock_sort, mock_session, mock_count, mock_connect, mock_query_from_database, mock_rows_to_list
    ):
        mock_param = {
            'page': '1',
            'per_page': '5',
            'domain': 'test',
            'level': 'test',
            'sort': 'time',
        }

        check_result_list = [
            {
                "alert_id": "alert_1",
                "alert_name": "test",
                "confirmed": False,
                "domain": "test",
                "host_num": 1,
                "level": "test1",
                "time": 20180102,
                "workflow_id": "workflow_id_1",
                "workflow_name": "workflow_name_1",
            },
            {
                "alert_id": "alert_2",
                "alert_name": "test",
                "confirmed": False,
                "domain": "test",
                "host_num": 2,
                "level": "test2",
                "time": 20201111,
                "workflow_id": "workflow_id_2",
                "workflow_name": "workflow_name_2",
            },
        ]

        mock_session.return_value = ''
        mock_connect.return_value = True
        mock_count.return_value = 'a' * 2
        mock_sort.return_value = [], 1
        mock_query_from_database.return_value = mock.Mock
        mock_rows_to_list.return_value = check_result_list
        resp = self.client.get(f'/check/result/list?{urlencode(mock_param)}', headers=header_with_token)
        self.assertEqual(check_result_list, resp.json.get('result'))

    def test_query_result_list_should_return_token_error_when_input_with_no_token(self):
        mock_param = {}
        resp = self.client.get('/check/result/list', data=mock_param, headers=header)
        self.assertEqual(TOKEN_ERROR, resp.json.get('label'))

    def test_query_result_list_should_return_405_when_input_with_request_by_other_method(self):
        mock_param = {}
        resp = self.client.post('/check/result/list', data=mock_param, headers=header_with_token)
        self.assertEqual(405, resp.status_code)

    def test_query_result_list_should_return_param_error_when_input_with_request_input_error_info(self):
        mock_param = {"test": "test"}
        resp = self.client.get(
            f'/check/result/list?test={mock_param["test"]}', data=mock_param, headers=header_with_token
        )
        self.assertEqual(PARAM_ERROR, resp.json.get('label'))

    @mock.patch.object(ResultDao, 'query_result_total_count')
    @mock.patch.object(ResultDao, 'connect')
    @mock.patch.object(scoping, 'scoped_session')
    def test_query_result_total_count_should_return_result_list_when_request_with_token(
        self, mock_session, mock_connect, mock_query
    ):
        mock_session.return_value = ''
        mock_connect.return_value = True
        mock_query.return_value = SUCCEED, {'count': 6}
        resp = self.client.get('/check/result/total/count', headers=header_with_token)
        self.assertEqual(SUCCEED, resp.json.get('label'))

    def test_query_result_total_count_should_return_token_error_when_request_with_no_token(self):
        resp = self.client.get('/check/result/total/count')
        self.assertEqual(TOKEN_ERROR, resp.json.get('label'))

    def test_query_result_total_count_should_return_405_when_request_with_incorrect_method(self):
        resp = self.client.post('/check/result/total/count')
        self.assertEqual(405, resp.status_code)

    @mock.patch.object(ResultDao, 'confirm_check_result')
    @mock.patch.object(ResultDao, 'connect')
    @mock.patch.object(scoping, 'scoped_session')
    def test_confirm_check_result_should_return_succeed_when_input_correct_alert_id(
        self, mock_session, mock_connect, mock_confirm
    ):
        mock_session.return_value = ''
        mock_connect.return_value = True
        mock_confirm.return_value = SUCCEED
        mock_param = {'alert_id': "test1"}
        resp = self.client.post('/check/result/confirm', json=mock_param, headers=header_with_token)
        self.assertEqual(SUCCEED, resp.json.get('label'))

    @mock.patch.object(ResultDao, 'confirm_check_result')
    @mock.patch.object(ResultDao, 'connect')
    @mock.patch.object(scoping, 'scoped_session')
    def test_confirm_check_result_should_return_no_data_when_input_alert_id_is_not_in_database(
        self, mock_session, mock_connect, mock_confirm
    ):
        mock_session.return_value = ''
        mock_connect.return_value = True
        mock_confirm.return_value = NO_DATA
        mock_param = {'alert_id': "test1"}
        resp = self.client.post('/check/result/confirm', json=mock_param, headers=header_with_token)
        self.assertEqual(NO_DATA, resp.json.get('label'))

    def test_confirm_check_result_should_return_param_error_when_input_alert_id_is_null(self):
        mock_param = {'alert_id': ""}
        resp = self.client.post('/check/result/confirm', json=mock_param, headers=header_with_token)
        self.assertEqual(PARAM_ERROR, resp.json.get('label'))

    def test_confirm_check_result_should_return_400_when_no_input(self):
        resp = self.client.post('/check/result/confirm', headers=header_with_token)
        self.assertEqual(400, resp.status_code)

    def test_confirm_check_result_should_return_405_when_request_by_other_method(self):
        mock_param = {'alert_id': "test"}
        resp = self.client.get('/check/result/confirm', json=mock_param, headers=header_with_token)
        self.assertEqual(405, resp.status_code)

    def test_confirm_check_result_should_return_token_error_when_request_with_no_token(self):
        mock_param = {'alert_id': "test1"}
        resp = self.client.post('/check/result/confirm', json=mock_param, headers=header)
        self.assertEqual(TOKEN_ERROR, resp.json.get('label'))

    @mock.patch.object(ResultDao, '_domain_check_result_count_rows_to_list')
    @mock.patch.object(ResultDao, '_query_all_domain_check_count')
    @mock.patch.object(ResultDao, 'connect')
    @mock.patch.object(mock.Mock, 'all', create=True)
    @mock.patch.object(scoping, 'scoped_session')
    @mock.patch('diana.database.dao.result_dao.sort_and_page')
    def test_query_domain_result_count_should_return_result_count_when_input_all_correct(
        self, mock_sort, mock_session, mock_count, mock_connect, mock_query_from_db, mock_rows_to_list
    ):
        mock_param = {'page': 1, 'per_page': 2, 'sort': 'count', 'direction': 'asc'}
        mock_domain_result_count = [
            {'domain': 'domain_name_1', 'count': 1},
            {'domain': 'domain_name_2', 'count': 2},
        ]
        mock_sort.return_value = [], 3
        mock_session.return_value = ''
        mock_connect.return_value = True
        mock_count.return_value = 'a' * 3
        mock_query_from_db.return_value = mock.Mock
        mock_rows_to_list.return_value = mock_domain_result_count
        resp = self.client.get(f'/check/result/domain/count?{urlencode(mock_param)}', headers=header_with_token)
        self.assertEqual(mock_domain_result_count, resp.json.get('results'))

    @mock.patch.object(ResultDao, '_domain_check_result_count_rows_to_list')
    @mock.patch.object(ResultDao, '_query_all_domain_check_count')
    @mock.patch.object(ResultDao, 'connect')
    @mock.patch.object(mock.Mock, 'all', create=True)
    @mock.patch.object(scoping, 'scoped_session')
    @mock.patch('diana.database.dao.result_dao.sort_and_page')
    def test_query_domain_result_count_should_return_result_count_when_input_with_no_page(
        self, mock_sort, mock_session, mock_count, mock_connect, mock_query_from_db, mock_rows_to_list
    ):
        mock_param = {'per_page': 2, 'sort': 'count', 'direction': 'asc'}
        mock_domain_result_count = [
            {'domain': 'domain_name_2', 'count': 1},
            {'domain': 'domain_name_1', 'count': 2},
            {'domain': 'domain_name_3', 'count': 3},
        ]
        mock_sort.return_value = [], 3
        mock_session.return_value = ''
        mock_connect.return_value = True
        mock_count.return_value = 'a' * 3
        mock_query_from_db.return_value = mock.Mock
        mock_rows_to_list.return_value = mock_domain_result_count
        resp = self.client.get(f'/check/result/domain/count?{urlencode(mock_param)}', headers=header_with_token)
        self.assertEqual(mock_domain_result_count, resp.json.get('results'))

    @mock.patch.object(ResultDao, '_domain_check_result_count_rows_to_list')
    @mock.patch.object(ResultDao, '_query_all_domain_check_count')
    @mock.patch.object(ResultDao, 'connect')
    @mock.patch.object(mock.Mock, 'all', create=True)
    @mock.patch.object(scoping, 'scoped_session')
    @mock.patch('diana.database.dao.result_dao.sort_and_page')
    def test_query_domain_result_count_should_return_result_count_when_input_with_no_per_page(
        self, mock_sort, mock_session, mock_count, mock_connect, mock_query_from_db, mock_rows_to_list
    ):
        mock_param = {'page': 1, 'sort': 'count', 'direction': 'asc'}
        mock_domain_result_count = [
            {'domain': 'domain_name_1', 'count': 1},
            {'domain': 'domain_name_2', 'count': 2},
            {'domain': 'domain_name_3', 'count': 3},
        ]
        mock_sort.return_value = [], 3
        mock_session.return_value = ''
        mock_connect.return_value = True
        mock_count.return_value = 'a' * 3
        mock_query_from_db.return_value = mock.Mock
        mock_rows_to_list.return_value = mock_domain_result_count
        resp = self.client.get(f'/check/result/domain/count?{urlencode(mock_param)}', headers=header_with_token)
        self.assertEqual(mock_domain_result_count, resp.json.get('results'))

    @mock.patch.object(ResultDao, '_domain_check_result_count_rows_to_list')
    @mock.patch.object(ResultDao, '_query_all_domain_check_count')
    @mock.patch.object(ResultDao, 'connect')
    @mock.patch.object(mock.Mock, 'all', create=True)
    @mock.patch.object(scoping, 'scoped_session')
    @mock.patch('diana.database.dao.result_dao.sort_and_page')
    def test_query_domain_result_count_should_return_result_count_when_input_with_no_sort(
        self, mock_sort, mock_session, mock_count, mock_connect, mock_query_from_db, mock_rows_to_list
    ):
        mock_param = {'page': 1, 'per_page': 2, 'direction': 'desc'}
        mock_domain_result_count = [
            {'domain': 'domain_name_1', 'count': 1},
            {'domain': 'domain_name_2', 'count': 2},
        ]
        mock_sort.return_value = [], 3
        mock_session.return_value = ''
        mock_connect.return_value = True
        mock_count.return_value = 'a' * 3
        mock_query_from_db.return_value = mock.Mock
        mock_rows_to_list.return_value = mock_domain_result_count
        resp = self.client.get(f'/check/result/domain/count?{urlencode(mock_param)}', headers=header_with_token)
        self.assertEqual(mock_domain_result_count, resp.json.get('results'))

    @mock.patch.object(ResultDao, '_domain_check_result_count_rows_to_list')
    @mock.patch.object(ResultDao, '_query_all_domain_check_count')
    @mock.patch.object(ResultDao, 'connect')
    @mock.patch.object(mock.Mock, 'all', create=True)
    @mock.patch.object(scoping, 'scoped_session')
    @mock.patch('diana.database.dao.result_dao.sort_and_page')
    def test_query_domain_result_count_should_return_result_count_when_input_with_no_direction(
        self, mock_sort, mock_session, mock_count, mock_connect, mock_query_from_db, mock_rows_to_list
    ):
        mock_param = {'page': 1, 'per_page': 2, 'sort': 'count'}
        mock_domain_result_count = [
            {'domain': 'domain_name_1', 'count': 1},
            {'domain': 'domain_name_2', 'count': 2},
        ]
        mock_sort.return_value = [], 3
        mock_session.return_value = ''
        mock_connect.return_value = True
        mock_count.return_value = 'a' * 3
        mock_query_from_db.return_value = mock.Mock
        mock_rows_to_list.return_value = mock_domain_result_count
        resp = self.client.get(f'/check/result/domain/count?{urlencode(mock_param)}', headers=header_with_token)
        self.assertEqual(mock_domain_result_count, resp.json.get('results'))

    @mock.patch.object(ResultDao, '_domain_check_result_count_rows_to_list')
    @mock.patch.object(ResultDao, '_query_all_domain_check_count')
    @mock.patch.object(ResultDao, 'connect')
    @mock.patch.object(mock.Mock, 'all', create=True)
    @mock.patch.object(scoping, 'scoped_session')
    @mock.patch('diana.database.dao.result_dao.sort_and_page')
    def test_query_domain_result_count_should_return_result_count_when_request_with_no_input(
        self, mock_sort, mock_session, mock_count, mock_connect, mock_query_from_db, mock_rows_to_list
    ):
        mock_domain_result_count = [
            {'domain': 'domain_name_1', 'count': 1},
            {'domain': 'domain_name_2', 'count': 2},
        ]
        mock_sort.return_value = [], 3
        mock_session.return_value = ''
        mock_connect.return_value = True
        mock_count.return_value = 'a' * 3
        mock_query_from_db.return_value = mock.Mock
        mock_rows_to_list.return_value = mock_domain_result_count
        resp = self.client.get('/check/result/domain/count', headers=header_with_token)
        self.assertEqual(mock_domain_result_count, resp.json.get('results'))

    def test_query_domain_result_count_should_return_param_error_when_input_per_page_is_greater_than_50(self):
        mock_param = {
            'per_page': 51,
        }
        resp = self.client.get(f'/check/result/domain/count?{urlencode(mock_param)}', headers=header_with_token)
        self.assertEqual(PARAM_ERROR, resp.json.get('label'))

    def test_query_domain_result_count_should_return_param_error_when_input_sort_is_not_count(self):
        mock_param = {
            'sort': 'test',
        }
        resp = self.client.get(f'/check/result/domain/count?{urlencode(mock_param)}', headers=header_with_token)
        self.assertEqual(PARAM_ERROR, resp.json.get('label'))

    def test_query_domain_result_count_should_return_param_error_when_input_direction_is_not_asc_or_desc(self):
        mock_param = {
            'direction': 'test',
        }
        resp = self.client.get(f'/check/result/domain/count?{urlencode(mock_param)}', headers=header_with_token)
        self.assertEqual(PARAM_ERROR, resp.json.get('label'))

    def test_query_domain_result_count_should_return_param_error_when_input_page_is_less_than_1(self):
        mock_param = {
            'page': '0',
        }
        resp = self.client.get(f'/check/result/domain/count?{urlencode(mock_param)}', headers=header_with_token)
        self.assertEqual(PARAM_ERROR, resp.json.get('label'))

    def test_query_domain_result_count_should_return_token_error_when_request_with_no_token(self):
        resp = self.client.get('/check/result/domain/count', headers=header)
        self.assertEqual(TOKEN_ERROR, resp.json.get('label'))
