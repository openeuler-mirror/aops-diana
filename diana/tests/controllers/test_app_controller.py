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
"""
Time:
Author:
Description:
"""
import unittest
from unittest import mock

from vulcanus.restful.resp.state import PARAM_ERROR, TOKEN_ERROR, DATABASE_CONNECT_ERROR, SUCCEED

from vulcanus.restful.response import BaseResponse
from diana.database.dao.app_dao import AppDao
from diana.conf.constant import CREATE_APP, QUERY_APP, QUERY_APP_LIST
from diana.tests import BaseTestCase


header = {"Content-Type": "application/json; charset=UTF-8"}
header_with_token = {"Content-Type": "application/json; charset=UTF-8", "access_token": "81fe"}


class AppControllerTestCase(BaseTestCase):
    """
    AppController integration tests stubs
    """

    def setUp(self) -> None:
        super().setUp()
        app = self.init_application()
        self.client = app.test_client()

    def test_create_app_should_return_error_when_request_method_is_wrong(self):
        args = {}
        response = self.client.get(CREATE_APP, json=args).json
        self.assertEqual(response['message'], 'The method is not allowed for the requested URL.')

    def test_create_app_should_return_param_error_when_input_wrong_param(self):
        args = {"app_name": "app1", "description": "", "api": {"type": 1, "address1": "sx"}}
        response = self.client.post(CREATE_APP, json=args, headers=header_with_token).json
        self.assertEqual(response['label'], PARAM_ERROR)

    def test_create_app_should_return_token_error_when_input_wrong_token(self):
        args = {"app_name": "app1", "description": "xx", "api": {"type": "api", "address": "execute"}, "detail": {}}
        response = self.client.post(CREATE_APP, json=args, headers=header).json
        self.assertEqual(response['label'], TOKEN_ERROR)

    @mock.patch.object(BaseResponse, 'verify_token')
    @mock.patch.object(AppDao, 'connect')
    def test_create_app_should_return_database_error_when_database_is_wrong(self, mock_connect, mock_token):
        args = {
            "app_name": "app1",
            "description": "xx",
            "api": {"type": "api", "address": "execute"},
            "detail": {},
        }
        mock_connect.return_value = False
        mock_token.return_value = SUCCEED
        response = self.client.post(CREATE_APP, json=args, headers=header_with_token).json
        self.assertEqual(response['label'], DATABASE_CONNECT_ERROR)

    @mock.patch.object(BaseResponse, 'verify_args')
    @mock.patch.object(BaseResponse, 'verify_token')
    def test_create_app_should_return_app_id_when_correct(self, mock_token, mock_args):
        args = {
            "app_name": "app1",
            "description": "xx",
            "api": {"type": "api", "address": "execute"},
            "detail": {},
            "username": "admin",
        }
        mock_token.return_value = SUCCEED
        mock_args.return_value = SUCCEED
        response = self.client.post(CREATE_APP, json=args, headers=header_with_token).json
        self.assertEqual(response['label'], SUCCEED)
        self.assertIn('app_id', response.keys())

    def test_query_app_list_should_return_error_when_request_method_is_wrong(self):
        response = self.client.post(QUERY_APP_LIST).json
        self.assertEqual(response['message'], 'The method is not allowed for the requested URL.')

    def test_query_app_list_should_return_param_error_when_input_wrong_param(self):
        response = self.client.get(QUERY_APP_LIST + "?page=1&per_page='1'", headers=header_with_token).json
        self.assertEqual(response['label'], PARAM_ERROR)

    def test_query_app_list_should_return_token_error_when_input_wrong_token(self):
        response = self.client.get(QUERY_APP_LIST + "?page=1&per_page=2", headers=header).json
        self.assertEqual(response['label'], TOKEN_ERROR)

    def test_query_app_list_should_return_database_error_when_database_is_wrong(self):
        with mock.patch("vulcanus.restful.response.operate") as mock_operate:
            mock_operate.return_value = DATABASE_CONNECT_ERROR
            response = self.client.get(QUERY_APP_LIST + "?page=1&per_page=2", headers=header_with_token).json
            self.assertEqual(response['label'], DATABASE_CONNECT_ERROR)

    def test_query_app_list_should_return_succeed_when_correct(self):
        with mock.patch("vulcanus.restful.response.operate") as mock_operate:
            mock_operate.return_value = SUCCEED
            response = self.client.get(QUERY_APP_LIST + "?page=1&per_page=2", headers=header_with_token).json
            self.assertEqual(response['label'], SUCCEED)

    def test_query_app_should_return_error_when_request_method_is_wrong(self):
        response = self.client.post(QUERY_APP).json
        self.assertEqual(response['message'], 'The method is not allowed for the requested URL.')

    def test_query_app_should_return_param_error_when_input_wrong_param(self):
        response = self.client.get(QUERY_APP + "?app=1", headers=header_with_token).json
        self.assertEqual(response['label'], PARAM_ERROR)

    def test_query_app_should_return_token_error_when_input_wrong_token(self):
        response = self.client.get(QUERY_APP + "?app_id='1'", headers=header).json
        self.assertEqual(response['label'], TOKEN_ERROR)

    @mock.patch.object(BaseResponse, 'verify_token')
    def test_query_app_should_return_database_error_when_database_is_wrong(self, mock_token):
        mock_token.return_value = SUCCEED
        response = self.client.get(QUERY_APP + "?app_id='2'", headers=header_with_token).json
        self.assertEqual(response['label'], DATABASE_CONNECT_ERROR)

    @mock.patch.object(BaseResponse, 'verify_token')
    @mock.patch.object(AppDao, 'connect')
    def test_query_app_should_return_succeed_when_correct(self, mock_connect, mock_token):
        mock_connect.return_value = True
        mock_token.return_value = SUCCEED
        response = self.client.get(QUERY_APP + "?app_id='3'", headers=header_with_token).json
        self.assertEqual(response['label'], SUCCEED)


if __name__ == '__main__':
    import unittest

    unittest.main()
