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
from flask import Flask
from flask_restful import Api
from flask.blueprints import Blueprint

from vulcanus.restful.status import PARAM_ERROR, TOKEN_ERROR, DATABASE_CONNECT_ERROR, SUCCEED

from diana.conf.constant import QUERY_MODEL_LIST
from diana.url import SPECIFIC_URLS

API = Api()
for view, url in SPECIFIC_URLS['MODEL_URLS']:
    API.add_resource(view, url)

DIANA = Blueprint('diana', __name__)
app = Flask("diana")
API.init_app(DIANA)
app.register_blueprint(DIANA)

app.testing = True
client = app.test_client()
header = {
    "Content-Type": "application/json; charset=UTF-8"
}
header_with_token = {
    "Content-Type": "application/json; charset=UTF-8",
    "access_token": "81fe"
}


class ModelControllerTestCase(unittest.TestCase):
    """
    ModelController integration tests stubs
    """

    def test_query_model_list_should_return_error_when_request_method_is_wrong(self):
        args = {}
        response = client.get(QUERY_MODEL_LIST, json=args).json
        self.assertEqual(
            response['message'], 'The method is not allowed for the requested URL.')

    def test_query_model_list_should_return_param_error_when_input_wrong_param(self):
        args = {
            "sort": "precision",
            "direction": "asc",
            "page": 1,
            "per_page": 2,
            "filter": {
                "tag": 1,
                "field": "singlecheck",
                "model_name": "",
                "algo_name": [""]
            }
        }
        response = client.post(QUERY_MODEL_LIST, json=args, headers=header_with_token).json
        self.assertEqual(response['code'], PARAM_ERROR)

    def test_query_model_list_should_return_token_error_when_input_wrong_token(self):
        args = {
            "sort": "precision",
            "direction": "asc",
            "page": 1,
            "per_page": 2,
            "filter": {
                "tag": "aaa",
                "field": "singlecheck",
                "model_name": "test",
                "algo_name": ["test"]
            }
        }
        response = client.post(QUERY_MODEL_LIST, json=args, headers=header).json
        self.assertEqual(response['code'], TOKEN_ERROR)

    def test_query_model_list_should_return_database_error_when_database_is_wrong(self):
        args = {
            "sort": "precision",
            "direction": "asc",
            "page": 1,
            "per_page": 2,
            "filter": {
                "tag": "aaa",
                "field": "singlecheck",
                "model_name": "test",
                "algo_name": ["test"]
            }
        }
        with mock.patch("vulcanus.restful.response.operate") as mock_operate:
            mock_operate.return_value = DATABASE_CONNECT_ERROR
            response = client.post(QUERY_MODEL_LIST, json=args, headers=header_with_token).json
            self.assertEqual(response['code'], DATABASE_CONNECT_ERROR)

    def test_query_model_list_should_return_successfully_when_given_correct_params(self):
        args = {
            "sort": "precision",
            "direction": "asc",
            "page": 1,
            "per_page": 2,
            "filter": {
                "tag": "aaa",
                "field": "singlecheck",
                "model_name": "test",
                "algo_name": ["test"]
            }
        }
        with mock.patch("vulcanus.restful.response.operate") as mock_operate:
            mock_operate.return_value = SUCCEED
            response = client.post(QUERY_MODEL_LIST, json=args, headers=header_with_token).json
            self.assertEqual(response['code'], SUCCEED)
