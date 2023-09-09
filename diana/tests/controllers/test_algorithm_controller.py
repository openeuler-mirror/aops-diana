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

from sqlalchemy.orm import scoping

from diana.database.dao.algo_dao import AlgorithmDao
from vulcanus.restful.resp.state import TOKEN_ERROR, SUCCEED, NO_DATA, PARAM_ERROR
from vulcanus.restful.response import BaseResponse
from diana.tests import BaseTestCase


header = {"Content-Type": "application/json; charset=UTF-8"}
header_with_token = {"Content-Type": "application/json; charset=UTF-8", "access_token": "123456"}


class TestQueryAlgorithmList(BaseTestCase):
    def setUp(self) -> None:
        super().setUp()
        app = self.init_application()
        self.client = app.test_client()

    @mock.patch.object(AlgorithmDao, '_query_algo_list')
    @mock.patch.object(AlgorithmDao, '_algo_rows_to_dict')
    @mock.patch.object(AlgorithmDao, 'connect')
    @mock.patch.object(mock.Mock, 'all', create=True)
    @mock.patch.object(BaseResponse, 'verify_token')
    @mock.patch.object(scoping, 'scoped_session')
    @mock.patch('diana.database.dao.algo_dao.sort_and_page')
    def test_query_algorithm_list_should_return_algo_list_when_all_input_correct(
        self,
        mock_sort_and_page,
        mock_session,
        mock_token,
        mock_count,
        mock_connect,
        mock_query_to_dict,
        mock_query_algo_list,
    ):
        mock_param = {'page': 2, 'per_page': 2, 'field': 'abc'}
        algo_list = [{"algo_id": "test_3", "algo_name": "xxx", "description": "xxx", "field": "abc"}]
        mock_sort_and_page.return_value = [], 3
        mock_count.return_value = 'a' * 3
        mock_connect.return_value = True
        mock_session.return_value = ''
        mock_token.return_value = SUCCEED
        mock_query_algo_list.return_value = mock.Mock
        mock_query_to_dict.return_value = algo_list
        resp = self.client.get(
            f'/check/algo/list?page={mock_param["page"]}&per_page='
            f'{mock_param["per_page"]}&field={mock_param["field"]}',
            headers=header_with_token,
        )
        self.assertEqual(algo_list, resp.json["data"].get('algo_list'))

    @mock.patch.object(AlgorithmDao, '_query_algo_list')
    @mock.patch.object(AlgorithmDao, '_algo_rows_to_dict')
    @mock.patch.object(AlgorithmDao, 'connect')
    @mock.patch.object(mock.Mock, 'all', create=True)
    @mock.patch.object(BaseResponse, 'verify_token')
    @mock.patch.object(scoping, 'scoped_session')
    @mock.patch('diana.database.dao.algo_dao.sort_and_page')
    def test_query_algorithm_list_should_return_algo_list_when_input_with_no_field(
        self,
        mock_sort_and_page,
        mock_session,
        mock_token,
        mock_count,
        mock_connect,
        mock_query_to_dict,
        mock_query_algo_list,
    ):
        mock_param = {
            'page': 2,
            'per_page': 2,
        }
        algo_list = [{"algo_id": "test_3", "algo_name": "xxx", "description": "xxx", "field": "xxx"}]

        mock_sort_and_page.return_value = [], 3
        mock_count.return_value = 'a' * 3
        mock_connect.return_value = True
        mock_session.return_value = ''
        mock_token.return_value = SUCCEED
        mock_query_algo_list.return_value = mock.Mock
        mock_query_to_dict.return_value = algo_list
        resp = self.client.get(
            f'/check/algo/list?page={mock_param["page"]}&per_page={mock_param["per_page"]}', headers=header_with_token
        )
        self.assertEqual(algo_list, resp.json["data"].get('algo_list'))

    @mock.patch.object(AlgorithmDao, '_query_algo_list')
    @mock.patch.object(AlgorithmDao, '_algo_rows_to_dict')
    @mock.patch.object(AlgorithmDao, 'connect')
    @mock.patch.object(mock.Mock, 'all', create=True)
    @mock.patch.object(BaseResponse, 'verify_token')
    @mock.patch.object(scoping, 'scoped_session')
    @mock.patch('diana.database.dao.algo_dao.sort_and_page')
    def test_query_algorithm_list_should_return_algo_list_when_with_no_page(
        self,
        mock_sort_and_page,
        mock_session,
        mock_token,
        mock_count,
        mock_connect,
        mock_query_to_dict,
        mock_query_algo_list,
    ):
        mock_param = {'per_page': 2, 'field': 'abc'}
        algo_list = [
            {"algo_id": "test_1", "algo_name": "xxx", "description": "xxx", "field": "abc"},
            {"algo_id": "test_2", "algo_name": "xxx", "description": "xxx", "field": "abc"},
            {"algo_id": "test_3", "algo_name": "xxx", "description": "xxx", "field": "abc"},
        ]

        mock_sort_and_page.return_value = [], 3
        mock_count.return_value = 'a' * 3
        mock_connect.return_value = True
        mock_session.return_value = ''
        mock_token.return_value = SUCCEED
        mock_query_algo_list.return_value = mock.Mock
        mock_query_to_dict.return_value = algo_list
        resp = self.client.get(
            f'/check/algo/list?per_page={mock_param["per_page"]}&field={mock_param["field"]}', headers=header_with_token
        )
        self.assertEqual(algo_list, resp.json["data"].get('algo_list'))

    @mock.patch.object(AlgorithmDao, '_query_algo_list')
    @mock.patch.object(AlgorithmDao, '_algo_rows_to_dict')
    @mock.patch.object(AlgorithmDao, 'connect')
    @mock.patch.object(mock.Mock, 'all', create=True)
    @mock.patch.object(BaseResponse, 'verify_token')
    @mock.patch.object(scoping, 'scoped_session')
    @mock.patch('diana.database.dao.algo_dao.sort_and_page')
    def test_query_algorithm_list_should_return_algo_list_when_input_with_no_per_page(
        self,
        mock_sort_and_page,
        mock_session,
        mock_token,
        mock_count,
        mock_connect,
        mock_query_to_dict,
        mock_query_algo_list,
    ):
        mock_param = {'page': 2, 'field': "abc"}
        algo_list = [
            {"algo_id": "test_1", "algo_name": "xxx", "description": "xxx", "field": "abc"},
            {"algo_id": "test_2", "algo_name": "xxx", "description": "xxx", "field": "abc"},
            {"algo_id": "test_3", "algo_name": "xxx", "description": "xxx", "field": "abc"},
        ]

        mock_sort_and_page.return_value = [], 3
        mock_count.return_value = 'a' * 3
        mock_connect.return_value = True
        mock_session.return_value = ''
        mock_token.return_value = SUCCEED
        mock_query_algo_list.return_value = mock.Mock
        mock_query_to_dict.return_value = algo_list
        resp = self.client.get(
            f'/check/algo/list?page={mock_param["page"]}&field={mock_param["field"]}', headers=header_with_token
        )
        self.assertEqual(algo_list, resp.json["data"].get('algo_list'))

    @mock.patch.object(AlgorithmDao, '_query_algo_list')
    @mock.patch.object(AlgorithmDao, '_algo_rows_to_dict')
    @mock.patch.object(AlgorithmDao, 'connect')
    @mock.patch.object(mock.Mock, 'all', create=True)
    @mock.patch.object(BaseResponse, 'verify_token')
    @mock.patch.object(scoping, 'scoped_session')
    @mock.patch('diana.database.dao.algo_dao.sort_and_page')
    def test_query_algorithm_list_should_return_algo_list_when_input_with_no_input(
        self,
        mock_sort_and_page,
        mock_session,
        mock_token,
        mock_count,
        mock_connect,
        mock_query_to_dict,
        mock_query_algo_list,
    ):
        algo_list = [
            {"algo_id": "test_1", "algo_name": "xxx", "description": "xxx", "field": "xxx"},
            {"algo_id": "test_2", "algo_name": "xxx", "description": "xxx", "field": "xxx"},
            {"algo_id": "test_3", "algo_name": "xxx", "description": "xxx", "field": "xxx"},
        ]
        mock_sort_and_page.return_value = [], 3
        mock_count.return_value = 'a' * 3
        mock_connect.return_value = True
        mock_session.return_value = ''
        mock_token.return_value = SUCCEED
        mock_query_algo_list.return_value = mock.Mock
        mock_query_to_dict.return_value = algo_list
        resp = self.client.get(f'/check/algo/list', headers=header_with_token)
        self.assertEqual(algo_list, resp.json["data"].get('algo_list'))

    def test_query_algorithm_list_should_return_token_error_when_input_with_no_token(self):
        resp = self.client.get(f'/check/algo/list', headers=header)
        self.assertEqual(TOKEN_ERROR, resp.json.get('label'), resp.json)

    def test_query_algorithm_list_should_return_method_error_when_request_by_incorrect_method(self):
        resp = self.client.post(f'/check/algo/list', headers=header)
        self.assertEqual(405, resp.status_code, resp.json)

    @mock.patch.object(AlgorithmDao, "query_algorithm")
    @mock.patch.object(AlgorithmDao, 'connect')
    @mock.patch.object(BaseResponse, 'verify_token')
    @mock.patch.object(scoping, 'scoped_session')
    def test_query_algorithm_should_return_algorithm_info_when_input_correct_with_token(
        self, mock_session, mock_token, mock_connect, mock_query_algo
    ):
        mock_session.return_value = ''
        mock_connect.return_value = True
        mock_token.return_value = SUCCEED
        mock_query_algo.return_value = SUCCEED, {
            'result': {"algo_id": "test", "algo_name": "xxx", "description": "xxx", "field": "xxx"}
        }

        input_data = 'test'
        resp = self.client.get(f'/check/algo?algo_id={input_data}', headers=header_with_token)
        self.assertEqual(SUCCEED, resp.json.get('label'))

    def test_query_algorithm_should_return_405_when_request_by_other_method(self):
        input_data = 'test'
        resp = self.client.post(f'/check/algo?algo_id={input_data}', headers=header_with_token)
        self.assertEqual(405, resp.status_code)

    def test_query_algorithm_should_return_token_error_when_input_correct_with_no_token(self):
        input_data = 'test'
        resp = self.client.get(f'/check/algo?algo_id={input_data}', headers=header)
        self.assertEqual(TOKEN_ERROR, resp.json.get('label'))

    @mock.patch.object(AlgorithmDao, "query_algorithm")
    @mock.patch.object(BaseResponse, 'verify_token')
    @mock.patch.object(AlgorithmDao, 'connect')
    @mock.patch.object(scoping, 'scoped_session')
    def test_query_algorithm_should_return_no_data_when_input_incorrect_with_token(
        self, mock_session, mock_connect, mock_token, mock_query_algo
    ):
        mock_session.return_value = ''
        mock_connect.return_value = True
        mock_token.return_value = SUCCEED
        mock_query_algo.return_value = NO_DATA, {}
        input_data = 123456
        resp = self.client.get(f'/check/algo?algo_id={input_data}', headers=header_with_token)
        self.assertEqual(NO_DATA, resp.json.get('label'))

    def test_query_algorithm_should_return_param_error_when_no_input(self):
        resp = self.client.get('/check/algo', headers=header_with_token)
        self.assertEqual(PARAM_ERROR, resp.json.get('label'))

    def test_query_algorithm_should_return_param_error_when_input_algo_id_is_null(self):
        input_data = ''
        resp = self.client.get(f'/check/algo?algo_id={input_data}', headers=header_with_token)
        self.assertEqual(PARAM_ERROR, resp.json.get('label'))
