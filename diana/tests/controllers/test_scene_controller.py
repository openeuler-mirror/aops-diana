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

from vulcanus.restful.resp.state import SUCCEED, PARAM_ERROR, TOKEN_ERROR

from diana.conf.constant import IDENTIFY_SCENE
from diana.url import SPECIFIC_URLS
from vulcanus.restful.response import BaseResponse


API = Api()
for view, url in SPECIFIC_URLS['SCENE_URLS']:
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


class SceneControllerTestCase(unittest.TestCase):
    """
    SceneController integration tests stubs
    """

    def test_get_scene_should_return_error_when_request_method_is_wrong(self):
        args = {}
        response = client.get(IDENTIFY_SCENE, json=args).json
        self.assertEqual(
            response['message'], 'The method is not allowed for the requested URL.')

    def test_get_scene_should_return_param_error_when_input_wrong_param(self):
        args = {
            "applications": ["nginx", ""],
            "collect_items": {
                "gala-gopher": [
                    {
                        "probe_name": "probe1",
                        "probe_status": "on",
                        "support_auto": True
                    }
                ]
            }
        }
        response = client.post(IDENTIFY_SCENE, json=args,
                               headers=header_with_token).json
        self.assertEqual(response['label'], PARAM_ERROR)

    def test_get_scene_should_return_token_error_when_input_wrong_token(self):
        args = {
            "applications": ["nginx"],
            "collect_items": {
                "gala-gopher": [
                    {
                        "probe_name": "probe1",
                        "probe_status": "on",
                        "support_auto": True
                    }
                ]
            }
        }
        response = client.post(IDENTIFY_SCENE, json=args, headers=header).json
        self.assertEqual(response['label'], TOKEN_ERROR)

    @mock.patch.object(BaseResponse, 'verify_token')
    def test_get_scene_should_return_scene_when_given_correct_params(self, mock_token):
        args = {
            "applications": ["nginx"],
            "collect_items": {
                "gala-gopher": [
                    {
                        "probe_name": "probe1",
                        "probe_status": "on",
                        "support_auto": True
                    }
                ]
            }
        }
        mock_token.return_value = SUCCEED
        response = client.post(IDENTIFY_SCENE, json=args,
                               headers=header_with_token).json
        self.assertEqual(response['label'], SUCCEED)
