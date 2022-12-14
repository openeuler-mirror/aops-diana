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

from vulcanus.restful.status import PARAM_ERROR, TOKEN_ERROR, DATABASE_CONNECT_ERROR, SUCCEED, DATABASE_QUERY_ERROR

from diana.core.rule.workflow import Workflow, WorkflowDao
from diana.core.check.check_scheduler.check_scheduler import check_scheduler
from diana.conf.constant import CREATE_WORKFLOW, QUERY_WORKFLOW, QUERY_WORKFLOW_LIST, EXECUTE_WORKFLOW, \
    STOP_WORKFLOW, DELETE_WORKFLOW, UPDATE_WORKFLOW
from diana.url import SPECIFIC_URLS


API = Api()
for view, url in SPECIFIC_URLS['WORKFLOW_URLS']:
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


class CreateWorkflowTestCase(unittest.TestCase):
    """
    Create Workflow interface test cases
    """

    def test_create_workflow_should_return_error_when_request_method_is_wrong(self):
        args = {}
        response = client.get(CREATE_WORKFLOW, json=args).json
        self.assertEqual(
            response['message'], 'The method is not allowed for the requested URL.')

    def test_create_workflow_should_return_error_when_input_wrong_params(self):
        args = {
            "workflow_name": "",
            "description": "a long description",
            "app_name": "app1",
            "app_id": "asd",
            "input": {
                "domain": "host_group_1",
                "hosts": ["host_id1", "host_id2"]
            },
            "step": 5,
            "period": 15,
            "alert": {}
        }
        response = client.post(CREATE_WORKFLOW, json=args, headers=header_with_token).json
        self.assertEqual(response['code'], PARAM_ERROR)

    def test_create_workflow_should_return_token_error_when_input_wrong_token(self):
        args = {
            "workflow_name": "workflow1",
            "description": "a long description",
            "app_name": "app1",
            "app_id": "asd",
            "input": {
                "domain": "host_group_1",
                "hosts": ["host_id1", "host_id2"]
            },
            "step": 5,
            "period": 15,
            "alert": {}
        }
        response = client.post(CREATE_WORKFLOW, json=args, headers=header).json
        self.assertEqual(response['code'], TOKEN_ERROR)

    @mock.patch.object(Workflow, 'get_model_info')
    @mock.patch.object(Workflow, 'assign_model')
    @mock.patch("diana.controllers.workflow_controller.operate")
    def test_create_workflow_should_return_database_error_when_database_is_wrong(self, mock_operate, mock_assign, mock_info):
        mock_operate.return_value = DATABASE_CONNECT_ERROR
        mock_assign.return_value = {}, {}
        mock_info.return_value = {}
        args = {
            "workflow_name": "workflow1",
            "description": "a long description",
            "app_name": "app1",
            "app_id": "asd",
            "input": {
                "domain": "host_group_1",
                "hosts": ["host_id1", "host_id2"]
            },
            "step": 5,
            "period": 15,
            "alert": {}
        }
        response = client.post(CREATE_WORKFLOW, json=args, headers=header_with_token).json
        self.assertEqual(response['code'], DATABASE_CONNECT_ERROR)

    @mock.patch.object(Workflow, 'get_model_info')
    @mock.patch.object(Workflow, 'assign_model')
    @mock.patch("diana.controllers.workflow_controller.operate")
    def test_create_workflow_should_return_workflow_id_when_correct(self, mock_operate, mock_assign, mock_info):
        mock_operate.return_value = DATABASE_CONNECT_ERROR
        mock_assign.return_value = {}, {}
        mock_info.return_value = {}
        args = {
            "workflow_name": "workflow1",
            "description": "a long description",
            "app_name": "app1",
            "app_id": "asd",
            "input": {
                "domain": "host_group_1",
                "hosts": ["host_id1", "host_id2"]
            },
            "step": 5,
            "period": 15,
            "alert": {}
        }
        mock_operate.return_value = SUCCEED
        response = client.post(CREATE_WORKFLOW, json=args, headers=header_with_token).json
        self.assertEqual(response['code'], SUCCEED)
        self.assertIn('workflow_id', response.keys())


class QueryWorkflowTestCase(unittest.TestCase):
    """
    Query Workflow interface test cases
    """

    def test_query_workflow_should_return_error_when_request_method_is_wrong(self):
        args = {}
        response = client.post(QUERY_WORKFLOW, json=args).json
        self.assertEqual(response['message'], 'The method is not allowed for the requested URL.')

    def test_query_workflow_should_return_param_error_when_input_wrong_param(self):
        response = client.get(QUERY_WORKFLOW + "?workflow=1",
                              headers=header_with_token).json
        self.assertEqual(response['code'], PARAM_ERROR)

    def test_query_workflow_should_return_token_error_when_input_wrong_token(self):
        response = client.get(QUERY_WORKFLOW + "?workflow_id='1'", headers=header).json
        self.assertEqual(response['code'], TOKEN_ERROR)

    def test_query_workflow_should_return_database_error_when_database_is_wrong(self):
        with mock.patch("vulcanus.restful.response.operate") as mock_operate:
            mock_operate.return_value = DATABASE_CONNECT_ERROR
            response = client.get(QUERY_WORKFLOW + "?workflow_id='2'",
                                  headers=header_with_token).json
            self.assertEqual(response['code'], DATABASE_CONNECT_ERROR)

    def test_query_workflow_should_return_succeed_when_correct(self):
        with mock.patch("vulcanus.restful.response.operate") as mock_operate:
            mock_operate.return_value = SUCCEED
            response = client.get(QUERY_WORKFLOW + "?workflow_id='3'",
                                  headers=header_with_token).json
            self.assertEqual(response['code'], SUCCEED)


class QueryWorkflowListTestCase(unittest.TestCase):
    """
    Query Workflow list interface test cases
    """

    def test_query_workflow_list_should_return_error_when_request_method_is_wrong(self):
        args = {}
        response = client.get(QUERY_WORKFLOW_LIST, json=args).json
        self.assertEqual(response['message'], 'The method is not allowed for the requested URL.')

    def test_query_workflow_list_should_return_param_error_when_input_wrong_param(self):
        args = {"test": []}
        response = client.post(QUERY_WORKFLOW_LIST, json=args, headers=header_with_token).json
        self.assertEqual(response['code'], PARAM_ERROR)

    def test_query_workflow_list_should_return_token_error_when_input_wrong_token(self):
        args = {}
        response = client.post(QUERY_WORKFLOW_LIST, json=args, headers=header).json
        self.assertEqual(response['code'], TOKEN_ERROR)

    def test_query_workflow_list_should_return_database_error_when_database_is_wrong(self):
        args = {}
        with mock.patch("vulcanus.restful.response.operate") as mock_operate:
            mock_operate.return_value = DATABASE_CONNECT_ERROR
            response = client.post(QUERY_WORKFLOW_LIST, json=args, headers=header_with_token).json
            self.assertEqual(response['code'], DATABASE_CONNECT_ERROR)

    def test_query_workflow_list_should_return_successfully_when_given_correct_params(self):
        args = {
            "sort": "create_time",
            "direction": "asc",
            "page": 1,
            "per_page": 2,
            "filter": {
                "domain": ["test"],
                "app": ["test"],
                "status": ["hold"]
            }
        }
        with mock.patch("vulcanus.restful.response.operate") as mock_operate:
            mock_operate.return_value = SUCCEED
            response = client.post(QUERY_WORKFLOW_LIST, json=args, headers=header_with_token).json
            self.assertEqual(response['code'], SUCCEED)


class ExecuteWorkflowTestCase(unittest.TestCase):
    """
    Execute Workflow list interface test cases
    """

    def test_execute_workflow_should_return_error_when_request_method_is_wrong(self):
        args = {"workflow_id": "123456789"}
        response = client.get(EXECUTE_WORKFLOW, json=args).json
        self.assertEqual(response['message'], 'The method is not allowed for the requested URL.')

    def test_execute_workflow_should_return_param_error_when_input_wrong_param(self):
        args = {"test": []}
        response = client.post(EXECUTE_WORKFLOW, json=args, headers=header_with_token).json
        self.assertEqual(response['code'], PARAM_ERROR)

    def test_execute_workflow_should_return_token_error_when_input_wrong_token(self):
        args = {"workflow_id": "123456789"}
        response = client.post(EXECUTE_WORKFLOW, json=args, headers=header).json
        self.assertEqual(response['code'], TOKEN_ERROR)

    def test_execute_workflow_should_return_database_error_when_database_is_wrong(self):
        args = {"workflow_id": "123456789"}
        with mock.patch("diana.database.dao.workflow_dao.WorkflowDao.connect") as mock_connect:
            mock_connect.return_value = False
            response = client.post(EXECUTE_WORKFLOW, json=args, headers=header_with_token).json
            self.assertEqual(response['code'], DATABASE_CONNECT_ERROR)

    @mock.patch.object(WorkflowDao, 'get_workflow')
    @mock.patch.object(WorkflowDao, "connect")
    def test_execute_workflow_should_return_error_when_get_workflow_failed(self, mock_connect, mock_get):
        mock_connect.return_value = True
        mock_get.return_value = DATABASE_QUERY_ERROR, {}
        args = {"workflow_id": "123456789"}
        response = client.post(EXECUTE_WORKFLOW, json=args, headers=header_with_token).json
        self.assertEqual(response['code'], DATABASE_QUERY_ERROR)

    @mock.patch.object(check_scheduler, "start_workflow")
    @mock.patch.object(WorkflowDao, "update_workflow_status")
    @mock.patch.object(WorkflowDao, 'get_workflow')
    @mock.patch.object(WorkflowDao, "connect")
    def test_execute_workflow_should_return_succeed_when_workflow_is_onhold(self, mock_connect, mock_get, mock_update, mock_start):
        mock_connect.return_value = True
        mock_get.return_value = SUCCEED, {"result": {"status": "hold", "step": 10}}
        mock_update.return_value = None
        mock_start.return_value = None
        args = {"workflow_id": "123456789"}
        response = client.post(EXECUTE_WORKFLOW, json=args, headers=header_with_token).json
        self.assertEqual(response['code'], SUCCEED)

    @mock.patch.object(WorkflowDao, 'get_workflow')
    @mock.patch.object(WorkflowDao, "connect")
    def test_execute_workflow_should_return_succeed_when_workflow_isnot_onhold(self, mock_connect, mock_get):
        mock_connect.return_value = True
        mock_get.return_value = SUCCEED, {"result": {"status": "not_hold"}}
        args = {"workflow_id": "123456789"}
        response = client.post(EXECUTE_WORKFLOW, json=args, headers=header_with_token).json
        self.assertEqual(response['code'], SUCCEED)


class StopWorkflowTestCase(unittest.TestCase):
    """
    Stop Workflow list interface test cases
    """

    def test_stop_workflow_should_return_error_when_request_method_is_wrong(self):
        args = {"workflow_id": "123456789"}
        response = client.get(STOP_WORKFLOW, json=args).json
        self.assertEqual(response['message'], 'The method is not allowed for the requested URL.')

    def test_stop_workflow_should_return_param_error_when_input_wrong_param(self):
        args = {"test": []}
        response = client.post(STOP_WORKFLOW, json=args, headers=header_with_token).json
        self.assertEqual(response['code'], PARAM_ERROR)

    def test_execute_workflow_should_return_token_error_when_input_wrong_token(self):
        args = {"workflow_id": "123456789"}
        response = client.post(STOP_WORKFLOW, json=args, headers=header).json
        self.assertEqual(response['code'], TOKEN_ERROR)

    def test_execute_workflow_should_return_database_error_when_database_is_wrong(self):
        args = {"workflow_id": "123456789"}
        with mock.patch("diana.database.dao.workflow_dao.WorkflowDao.connect") as mock_connect:
            mock_connect.return_value = False
            response = client.post(STOP_WORKFLOW, json=args, headers=header_with_token).json
            self.assertEqual(response['code'], DATABASE_CONNECT_ERROR)

    @mock.patch.object(WorkflowDao, 'get_workflow')
    @mock.patch.object(WorkflowDao, "connect")
    def test_stop_workflow_should_return_error_when_get_workflow_failed(self, mock_connect, mock_get):
        mock_connect.return_value = True
        mock_get.return_value = DATABASE_QUERY_ERROR, {}
        args = {"workflow_id": "123456789"}
        response = client.post(STOP_WORKFLOW, json=args, headers=header_with_token).json
        self.assertEqual(response['code'], DATABASE_QUERY_ERROR)

    @mock.patch.object(check_scheduler, "stop_workflow")
    @mock.patch.object(WorkflowDao, "update_workflow_status")
    @mock.patch.object(WorkflowDao, 'get_workflow')
    @mock.patch.object(WorkflowDao, "connect")
    def test_stop_workflow_should_return_succeed_when_workflow_is_onhold(self, mock_connect, mock_get, mock_update, mock_start):
        mock_connect.return_value = True
        mock_get.return_value = SUCCEED, {"result": {"status": "running"}}
        mock_update.return_value = None
        mock_start.return_value = None
        args = {"workflow_id": "123456789"}
        response = client.post(STOP_WORKFLOW, json=args, headers=header_with_token).json
        self.assertEqual(response['code'], SUCCEED)

    @mock.patch.object(WorkflowDao, 'get_workflow')
    @mock.patch.object(WorkflowDao, "connect")
    def test_stop_workflow_should_return_succeed_when_workflow_isnot_onhold(self, mock_connect, mock_get):
        mock_connect.return_value = True
        mock_get.return_value = SUCCEED, {"result": {"status": "not_running"}}
        args = {"workflow_id": "123456789"}
        response = client.post(STOP_WORKFLOW, json=args, headers=header_with_token).json
        self.assertEqual(response['code'], SUCCEED)


class DeleteWorkflowTestCase(unittest.TestCase):
    """
    Delete Workflow list interface test cases
    """

    def test_delete_workflow_should_return_error_when_request_method_is_wrong(self):
        args = {"workflow_id": "123456789"}
        response = client.post(DELETE_WORKFLOW, json=args, headers=header_with_token).json
        self.assertEqual(response['message'], 'The method is not allowed for the requested URL.')

    def test_delete_workflow_should_return_param_error_when_input_wrong_param(self):
        args = {"test": []}
        response = client.delete(DELETE_WORKFLOW, json=args, headers=header_with_token).json
        self.assertEqual(response['code'], PARAM_ERROR)

    def test_delete_workflow_should_return_token_error_when_input_wrong_token(self):
        args = {"workflow_id": "123456789"}
        response = client.delete(DELETE_WORKFLOW, json=args, headers=header).json
        self.assertEqual(response['code'], TOKEN_ERROR)

    def test_delete_workflow_should_return_database_error_when_database_is_wrong(self):
        args = {"workflow_id": "123456789"}
        with mock.patch("diana.database.dao.workflow_dao.WorkflowDao.connect") as mock_connect:
            mock_connect.return_value = False
            response = client.delete(DELETE_WORKFLOW, json=args, headers=header_with_token).json
            self.assertEqual(response['code'], DATABASE_CONNECT_ERROR)

    def test_delete_workflow_should_return_succeed_when_given_correct_params(self):
        args = {"workflow_id": "123456789"}
        with mock.patch("vulcanus.restful.response.operate") as mock_operate:
            mock_operate.return_value = SUCCEED
            response = client.delete(DELETE_WORKFLOW, json=args, headers=header_with_token).json
            self.assertEqual(response['code'], SUCCEED)


class UpdateWorkflowTestCase(unittest.TestCase):
    """
    Update Workflow list interface test cases
    """

    def test_update_workflow_should_return_error_when_request_method_is_wrong(self):
        args = {"detail": {}, "workflow_id": "123"}
        response = client.get(UPDATE_WORKFLOW, json=args, headers=header_with_token).json
        self.assertEqual(response['message'], 'The method is not allowed for the requested URL.')

    def test_update_workflow_should_return_param_error_when_input_wrong_param(self):
        args = {"test": []}
        response = client.post(UPDATE_WORKFLOW, json=args, headers=header_with_token).json
        self.assertEqual(response['code'], PARAM_ERROR)

    def test_update_workflow_should_return_token_error_when_input_wrong_token(self):
        args = {"detail": {}, "workflow_id": "123"}
        response = client.post(UPDATE_WORKFLOW, json=args, headers=header).json
        self.assertEqual(response['code'], TOKEN_ERROR)

    @mock.patch.object(Workflow, 'get_model_info')
    def test_update_workflow_should_return_database_error_when_database_is_wrong(self, mock_info):
        mock_info.return_value = {}
        args = {"detail": {}, "workflow_id": "123"}
        with mock.patch("diana.database.dao.workflow_dao.WorkflowDao.connect") as mock_connect:
            mock_connect.return_value = False
            response = client.post(UPDATE_WORKFLOW, json=args, headers=header_with_token).json
            self.assertEqual(response['code'], DATABASE_CONNECT_ERROR)

    @mock.patch.object(Workflow, 'get_model_info')
    def test_update_workflow_should_return_succeed_when_given_correct_params(self, mock_info):
        mock_info.return_value = {}
        args = {"detail": {}, "workflow_id": "123"}
        with mock.patch("vulcanus.restful.response.operate") as mock_operate:
            mock_operate.return_value = SUCCEED
            response = client.post(UPDATE_WORKFLOW, json=args, headers=header_with_token).json
            self.assertEqual(response['code'], SUCCEED)
