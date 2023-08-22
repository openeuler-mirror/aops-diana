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
from unittest import mock

from vulcanus.restful.resp.state import SUCCEED, PARAM_ERROR, TOKEN_ERROR, DATABASE_CONNECT_ERROR
from vulcanus.restful.response import BaseResponse
from diana.database.dao.model_dao import ModelDao
from diana.conf.constant import QUERY_MODEL_LIST
from diana.tests import BaseTestCase


header = {"Content-Type": "application/json; charset=UTF-8"}
header_with_token = {"Content-Type": "application/json; charset=UTF-8", "access_token": "81fe"}


class ModelControllerTestCase(BaseTestCase):
    """
    ModelController integration tests stubs
    """

    def setUp(self) -> None:
        super().setUp()
        app = self.init_application()
        self.client = app.test_client()

    def test_query_model_list_should_return_error_when_request_method_is_wrong(self):
        args = {}
        response = self.client.get(QUERY_MODEL_LIST, json=args).json
        self.assertEqual(response['message'], 'The method is not allowed for the requested URL.')

    def test_query_model_list_should_return_param_error_when_input_wrong_param(self):
        args = {
            "sort": "precision",
            "direction": "asc",
            "page": 1,
            "per_page": 2,
            "filter": {"tag": 1, "field": "singlecheck", "model_name": "", "algo_name": [""]},
        }
        response = self.client.post(QUERY_MODEL_LIST, json=args, headers=header_with_token).json
        self.assertEqual(response['label'], PARAM_ERROR)

    def test_query_model_list_should_return_token_error_when_input_wrong_token(self):
        args = {
            "sort": "precision",
            "direction": "asc",
            "page": 1,
            "per_page": 2,
            "filter": {"tag": "aaa", "field": "singlecheck", "model_name": "test", "algo_name": ["test"]},
        }
        response = self.client.post(QUERY_MODEL_LIST, json=args, headers=header).json
        self.assertEqual(response['label'], TOKEN_ERROR)

    @mock.patch.object(BaseResponse, 'verify_token')
    @mock.patch.object(ModelDao, 'connect')
    def test_query_model_list_should_return_database_error_when_database_is_wrong(self, mock_connect, mock_token):
        args = {
            "sort": "precision",
            "direction": "asc",
            "page": 1,
            "per_page": 2,
            "filter": {"tag": "aaa", "field": "singlecheck", "model_name": "test", "algo_name": ["test"]},
        }
        mock_connect.return_value = False
        mock_token.return_value = SUCCEED
        response = self.client.post(QUERY_MODEL_LIST, json=args, headers=header_with_token).json
        self.assertEqual(response['label'], DATABASE_CONNECT_ERROR)

    def test_query_model_list_should_return_successfully_when_given_correct_params(self):
        args = {
            "sort": "precision",
            "direction": "asc",
            "page": 1,
            "per_page": 2,
            "filter": {"tag": "aaa", "field": "singlecheck", "model_name": "test", "algo_name": ["test"]},
        }
        response = self.client.post(QUERY_MODEL_LIST, json=args, headers=header_with_token).json
        self.assertEqual(response['label'], TOKEN_ERROR)
