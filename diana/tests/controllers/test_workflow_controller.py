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

from vulcanus.restful.resp.state import PARAM_ERROR, TOKEN_ERROR, DATABASE_CONNECT_ERROR, SUCCEED, DATABASE_QUERY_ERROR

from diana.core.rule.workflow import Workflow, WorkflowDao
from diana.core.check.check_scheduler.check_scheduler import check_scheduler
from diana.conf.constant import (
    CREATE_WORKFLOW,
    QUERY_WORKFLOW,
    QUERY_WORKFLOW_LIST,
    EXECUTE_WORKFLOW,
    STOP_WORKFLOW,
    DELETE_WORKFLOW,
    UPDATE_WORKFLOW,
)
from diana.url import SPECIFIC_URLS
from vulcanus.restful.response import BaseResponse
from diana.tests import BaseTestCase


header = {"Content-Type": "application/json; charset=UTF-8"}
header_with_token = {"Content-Type": "application/json; charset=UTF-8", "access_token": "81fe"}


class CreateWorkflowTestCase(BaseTestCase):
    """
    Create Workflow interface test cases
    """

    def setUp(self) -> None:
        super().setUp()
        app = self.init_application()
        self.client = app.test_client()

    def test_create_workflow_should_return_error_when_request_method_is_wrong(self):
        args = {}
        response = self.client.get(CREATE_WORKFLOW, json=args).json
        self.assertEqual(response['message'], 'The method is not allowed for the requested URL.')

    def test_create_workflow_should_return_error_when_input_wrong_params(self):
        args = {
            "workflow_name": "",
            "description": "a long description",
            "app_name": "app1",
            "app_id": "asd",
            "input": {"domain": "host_group_1", "hosts": [1, 2]},
            "step": 5,
            "period": 15,
            "alert": {},
        }
        response = self.client.post(CREATE_WORKFLOW, json=args, headers=header_with_token).json
        self.assertEqual(response['label'], PARAM_ERROR)

    def test_create_workflow_should_return_token_error_when_input_wrong_token(self):
        args = {
            "workflow_name": "workflow1",
            "description": "a long description",
            "app_name": "app1",
            "app_id": "asd",
            "input": {"domain": "host_group_1", "hosts": [1, 2]},
            "step": 5,
            "period": 15,
            "alert": {},
        }
        response = self.client.post(CREATE_WORKFLOW, json=args, headers=header).json
        self.assertEqual(response['label'], TOKEN_ERROR)

    @mock.patch.object(Workflow, 'get_model_info')
    @mock.patch.object(Workflow, 'assign_model')
    @mock.patch.object(BaseResponse, 'verify_token')
    def test_create_workflow_should_return_database_error_when_database_is_wrong(
        self, mock_token, mock_assign, mock_info
    ):
        mock_assign.return_value = {}, {}
        mock_token.return_value = SUCCEED
        mock_info.return_value = {}
        args = {
            "workflow_name": "workflow1",
            "description": "a long description",
            "app_name": "app1",
            "app_id": "asd",
            "input": {"domain": "host_group_1", "hosts": [1, 2]},
            "step": 5,
            "period": 15,
            "alert": {},
        }
        response = self.client.post(CREATE_WORKFLOW, json=args, headers=header_with_token).json
        self.assertEqual(response['label'], DATABASE_CONNECT_ERROR)

    @mock.patch.object(Workflow, 'get_model_info')
    @mock.patch.object(Workflow, 'assign_model')
    @mock.patch.object(BaseResponse, 'verify_token')
    def test_create_workflow_should_return_workflow_id_when_correct(self, mock_token, mock_assign, mock_info):
        mock_assign.return_value = {}, {}
        mock_token.return_value = SUCCEED
        mock_info.return_value = {}
        args = {
            "workflow_name": "workflow1",
            "description": "a long description",
            "app_name": "app1",
            "app_id": "asd",
            "input": {"domain": "host_group_1", "hosts": [1, 2]},
            "step": 5,
            "period": 15,
            "alert": {},
        }
        response = self.client.post(CREATE_WORKFLOW, json=args, headers=header_with_token).json
        self.assertEqual(response['label'], SUCCEED)
        self.assertIn('workflow_id', response.keys())


class QueryWorkflowTestCase(BaseTestCase):
    """
    Query Workflow interface test cases
    """

    def setUp(self) -> None:
        super().setUp()
        app = self.init_application()
        self.client = app.test_client()

    def test_query_workflow_should_return_error_when_request_method_is_wrong(self):
        args = {}
        response = self.client.post(QUERY_WORKFLOW, json=args).json
        self.assertEqual(response['message'], 'The method is not allowed for the requested URL.')

    def test_query_workflow_should_return_param_error_when_input_wrong_param(self):
        response = self.client.get(QUERY_WORKFLOW + "?workflow=1", headers=header_with_token).json
        self.assertEqual(response['label'], PARAM_ERROR)

    def test_query_workflow_should_return_token_error_when_input_wrong_token(self):
        response = self.client.get(QUERY_WORKFLOW + "?workflow_id='1'", headers=header).json
        self.assertEqual(response['label'], TOKEN_ERROR)

    @mock.patch.object(BaseResponse, 'verify_args')
    @mock.patch.object(BaseResponse, 'verify_token')
    def test_query_workflow_should_return_database_error_when_database_is_wrong(self, mock_token, mock_args):
        mock_token.return_value = SUCCEED
        mock_args.return_value = SUCCEED
        response = self.client.get(QUERY_WORKFLOW + "?workflow_id='2'&username=admin", headers=header_with_token).json
        self.assertEqual(response['label'], DATABASE_CONNECT_ERROR)

    @mock.patch.object(BaseResponse, 'verify_args')
    @mock.patch.object(BaseResponse, 'verify_token')
    def test_query_workflow_should_return_succeed_when_correct(self, mock_token, mock_args):
        mock_token.return_value = SUCCEED
        mock_args.return_value = SUCCEED
        response = self.client.get(QUERY_WORKFLOW + "?workflow_id='3'&username=admin", headers=header_with_token).json
        self.assertEqual(response['label'], SUCCEED)


class QueryWorkflowListTestCase(BaseTestCase):
    """
    Query Workflow list interface test cases
    """

    def setUp(self) -> None:
        super().setUp()
        app = self.init_application()
        self.client = app.test_client()

    def test_query_workflow_list_should_return_error_when_request_method_is_wrong(self):
        args = {}
        response = self.client.get(QUERY_WORKFLOW_LIST, json=args).json
        self.assertEqual(response['message'], 'The method is not allowed for the requested URL.')

    def test_query_workflow_list_should_return_param_error_when_input_wrong_param(self):
        args = {"test": []}
        response = self.client.post(QUERY_WORKFLOW_LIST, json=args, headers=header_with_token).json
        self.assertEqual(response['label'], PARAM_ERROR)

    def test_query_workflow_list_should_return_token_error_when_input_wrong_token(self):
        args = {}
        response = self.client.post(QUERY_WORKFLOW_LIST, json=args, headers=header).json
        self.assertEqual(response['label'], TOKEN_ERROR)

    @mock.patch.object(BaseResponse, 'verify_args')
    @mock.patch.object(BaseResponse, 'verify_token')
    def test_query_workflow_list_should_return_database_error_when_database_is_wrong(self, mock_token, mock_args):
        args = {"username": "admin"}
        mock_args.return_value = SUCCEED
        mock_token.return_value = SUCCEED
        response = self.client.post(QUERY_WORKFLOW_LIST, json=args, headers=header_with_token).json
        self.assertEqual(response['label'], DATABASE_CONNECT_ERROR)

    @mock.patch.object(BaseResponse, 'verify_args')
    @mock.patch.object(BaseResponse, 'verify_token')
    def test_query_workflow_list_should_return_successfully_when_given_correct_params(self, mock_token, mock_args):
        args = {
            "sort": "create_time",
            "direction": "asc",
            "page": 1,
            "per_page": 2,
            "filter": {"domain": ["test"], "app": ["test"], "status": ["hold"]},
            "username": "admin",
        }
        mock_args.return_value = SUCCEED
        mock_token.return_value = SUCCEED
        response = self.client.post(QUERY_WORKFLOW_LIST, json=args, headers=header_with_token).json
        self.assertEqual(response['label'], SUCCEED)


class ExecuteWorkflowTestCase(BaseTestCase):
    """
    Execute Workflow list interface test cases
    """

    def setUp(self) -> None:
        super().setUp()
        app = self.init_application()
        self.client = app.test_client()

    def test_execute_workflow_should_return_error_when_request_method_is_wrong(self):
        args = {"workflow_id": "123456789"}
        response = self.client.get(EXECUTE_WORKFLOW, json=args).json
        self.assertEqual(response['message'], 'The method is not allowed for the requested URL.')

    def test_execute_workflow_should_return_param_error_when_input_wrong_param(self):
        args = {"test": []}
        response = self.client.post(EXECUTE_WORKFLOW, json=args, headers=header_with_token).json
        self.assertEqual(response['label'], PARAM_ERROR)

    def test_execute_workflow_should_return_token_error_when_input_wrong_token(self):
        args = {"workflow_id": "123456789"}
        response = self.client.post(EXECUTE_WORKFLOW, json=args, headers=header).json
        self.assertEqual(response['label'], TOKEN_ERROR)

    @mock.patch.object(BaseResponse, 'verify_args')
    @mock.patch.object(BaseResponse, 'verify_token')
    def test_execute_workflow_should_return_database_error_when_database_is_wrong(self, mock_token, mock_args):
        args = {"workflow_id": "123456789", "username": "admin"}
        mock_token.return_value = SUCCEED
        mock_args.return_value = SUCCEED
        with mock.patch("diana.database.dao.workflow_dao.WorkflowDao.connect") as mock_connect:
            mock_connect.return_value = False
            response = self.client.post(EXECUTE_WORKFLOW, json=args, headers=header_with_token).json
            self.assertEqual(response['label'], DATABASE_CONNECT_ERROR)

    @mock.patch.object(WorkflowDao, 'get_workflow')
    @mock.patch.object(WorkflowDao, "connect")
    @mock.patch.object(BaseResponse, 'verify_args')
    @mock.patch.object(BaseResponse, 'verify_token')
    def test_execute_workflow_should_return_error_when_get_workflow_failed(
        self, mock_token, mock_args, mock_connect, mock_get
    ):
        mock_connect.return_value = True
        mock_token.return_value = SUCCEED
        mock_args.return_value = SUCCEED
        mock_get.return_value = DATABASE_QUERY_ERROR, {}
        args = {"workflow_id": "123456789", "username": "admin"}
        response = self.client.post(EXECUTE_WORKFLOW, json=args, headers=header_with_token).json
        self.assertEqual(response['label'], DATABASE_QUERY_ERROR)

    @mock.patch.object(check_scheduler, "start_workflow")
    @mock.patch.object(WorkflowDao, "update_workflow_status")
    @mock.patch.object(WorkflowDao, 'get_workflow')
    @mock.patch.object(BaseResponse, 'verify_args')
    @mock.patch.object(BaseResponse, 'verify_token')
    def test_execute_workflow_should_return_succeed_when_workflow_is_onhold(
        self, mock_token, mock_args, mock_get, mock_update, mock_start
    ):
        mock_token.return_value = SUCCEED
        mock_args.return_value = SUCCEED
        mock_get.return_value = SUCCEED, {"result": {"status": "hold", "step": 10}}
        mock_update.return_value = None
        mock_start.return_value = None
        args = {"workflow_id": "123456789", "username": "admin"}
        response = self.client.post(EXECUTE_WORKFLOW, json=args, headers=header_with_token).json
        self.assertEqual(response['label'], SUCCEED)

    @mock.patch.object(WorkflowDao, 'get_workflow')
    @mock.patch.object(WorkflowDao, "connect")
    @mock.patch.object(BaseResponse, 'verify_args')
    @mock.patch.object(BaseResponse, 'verify_token')
    def test_execute_workflow_should_return_succeed_when_workflow_isnot_onhold(
        self, mock_token, mock_args, mock_connect, mock_get
    ):
        mock_connect.return_value = True
        mock_token.return_value = SUCCEED
        mock_args.return_value = SUCCEED
        mock_get.return_value = SUCCEED, {"result": {"status": "not_hold"}}
        args = {"workflow_id": "123456789", "username": "admin"}
        response = self.client.post(EXECUTE_WORKFLOW, json=args, headers=header_with_token).json
        self.assertEqual(response['label'], SUCCEED)


class StopWorkflowTestCase(BaseTestCase):
    """
    Stop Workflow list interface test cases
    """

    def setUp(self) -> None:
        super().setUp()
        app = self.init_application()
        self.client = app.test_client()

    def test_stop_workflow_should_return_error_when_request_method_is_wrong(self):
        args = {"workflow_id": "123456789"}
        response = self.client.get(STOP_WORKFLOW, json=args).json
        self.assertEqual(response['message'], 'The method is not allowed for the requested URL.')

    def test_stop_workflow_should_return_param_error_when_input_wrong_param(self):
        args = {"test": []}
        response = self.client.post(STOP_WORKFLOW, json=args, headers=header_with_token).json
        self.assertEqual(response['label'], PARAM_ERROR)

    def test_execute_workflow_should_return_token_error_when_input_wrong_token(self):
        args = {"workflow_id": "123456789"}
        response = self.client.post(STOP_WORKFLOW, json=args, headers=header).json
        self.assertEqual(response['label'], TOKEN_ERROR)

    @mock.patch.object(BaseResponse, 'verify_token')
    def test_execute_workflow_should_return_database_error_when_database_is_wrong(self, mock_token):
        args = {"workflow_id": "123456789"}
        mock_token.return_value = SUCCEED
        with mock.patch("diana.database.dao.workflow_dao.WorkflowDao.connect") as mock_connect:
            mock_connect.return_value = False
            response = self.client.post(STOP_WORKFLOW, json=args, headers=header_with_token).json
            self.assertEqual(response['label'], DATABASE_CONNECT_ERROR)

    @mock.patch.object(WorkflowDao, 'get_workflow')
    @mock.patch.object(WorkflowDao, "connect")
    @mock.patch.object(BaseResponse, 'verify_token')
    def test_stop_workflow_should_return_error_when_get_workflow_failed(self, mock_token, mock_connect, mock_get):
        mock_connect.return_value = True
        mock_token.return_value = SUCCEED
        mock_get.return_value = DATABASE_QUERY_ERROR, {}
        args = {"workflow_id": "123456789"}
        response = self.client.post(STOP_WORKFLOW, json=args, headers=header_with_token).json
        self.assertEqual(response['label'], DATABASE_QUERY_ERROR)

    @mock.patch.object(check_scheduler, "stop_workflow")
    @mock.patch.object(WorkflowDao, "update_workflow_status")
    @mock.patch.object(WorkflowDao, 'get_workflow')
    @mock.patch.object(WorkflowDao, "connect")
    @mock.patch.object(BaseResponse, 'verify_token')
    def test_stop_workflow_should_return_succeed_when_workflow_is_onhold(
        self, mock_token, mock_connect, mock_get, mock_update, mock_start
    ):
        mock_connect.return_value = True
        mock_token.return_value = SUCCEED
        mock_get.return_value = SUCCEED, {"result": {"status": "running"}}
        mock_update.return_value = None
        mock_start.return_value = None
        args = {"workflow_id": "123456789"}
        response = self.client.post(STOP_WORKFLOW, json=args, headers=header_with_token).json
        self.assertEqual(response['label'], SUCCEED)

    @mock.patch.object(WorkflowDao, 'get_workflow')
    @mock.patch.object(WorkflowDao, "connect")
    @mock.patch.object(BaseResponse, 'verify_token')
    def test_stop_workflow_should_return_succeed_when_workflow_isnot_onhold(self, mock_token, mock_connect, mock_get):
        mock_connect.return_value = True
        mock_token.return_value = SUCCEED
        mock_get.return_value = SUCCEED, {"result": {"status": "not_running"}}
        args = {"workflow_id": "123456789"}
        response = self.client.post(STOP_WORKFLOW, json=args, headers=header_with_token).json
        self.assertEqual(response['label'], SUCCEED)


class DeleteWorkflowTestCase(BaseTestCase):
    """
    Delete Workflow list interface test cases
    """

    def setUp(self) -> None:
        super().setUp()
        app = self.init_application()
        self.client = app.test_client()

    def test_delete_workflow_should_return_error_when_request_method_is_wrong(self):
        args = {"workflow_id": "123456789"}
        response = self.client.post(DELETE_WORKFLOW, json=args, headers=header_with_token).json
        self.assertEqual(response['message'], 'The method is not allowed for the requested URL.')

    def test_delete_workflow_should_return_param_error_when_input_wrong_param(self):
        args = {"test": []}
        response = self.client.delete(DELETE_WORKFLOW, json=args, headers=header_with_token).json
        self.assertEqual(response['label'], PARAM_ERROR)

    def test_delete_workflow_should_return_token_error_when_input_wrong_token(self):
        args = {"workflow_id": "123456789"}
        response = self.client.delete(DELETE_WORKFLOW, json=args, headers=header).json
        self.assertEqual(response['label'], TOKEN_ERROR)

    @mock.patch.object(BaseResponse, 'verify_token')
    def test_delete_workflow_should_return_database_error_when_database_is_wrong(self, mock_token):
        args = {"workflow_id": "123456789"}
        mock_token.return_value = SUCCEED
        with mock.patch("diana.database.dao.workflow_dao.WorkflowDao.connect") as mock_connect:
            mock_connect.return_value = False
            response = self.client.delete(DELETE_WORKFLOW, json=args, headers=header_with_token).json
            self.assertEqual(response['label'], DATABASE_CONNECT_ERROR)

    @mock.patch.object(BaseResponse, 'verify_args')
    @mock.patch.object(BaseResponse, 'verify_token')
    def test_delete_workflow_should_return_succeed_when_given_correct_params(self, mock_token, mock_args):
        args = {"workflow_id": "123456789", "username": "admin"}
        mock_token.return_value = SUCCEED
        mock_args.return_value = SUCCEED
        response = self.client.delete(DELETE_WORKFLOW, json=args, headers=header_with_token).json
        self.assertEqual(response['label'], SUCCEED)


class UpdateWorkflowTestCase(BaseTestCase):
    """
    Update Workflow list interface test cases
    """

    def setUp(self) -> None:
        super().setUp()
        app = self.init_application()
        self.client = app.test_client()

    def test_update_workflow_should_return_error_when_request_method_is_wrong(self):
        args = {"detail": {}, "workflow_id": "123"}
        response = self.client.get(UPDATE_WORKFLOW, json=args, headers=header_with_token).json
        self.assertEqual(response['message'], 'The method is not allowed for the requested URL.')

    def test_update_workflow_should_return_param_error_when_input_wrong_param(self):
        args = {"test": []}
        response = self.client.post(UPDATE_WORKFLOW, json=args, headers=header_with_token).json
        self.assertEqual(response['label'], PARAM_ERROR)

    def test_update_workflow_should_return_token_error_when_input_wrong_token(self):
        args = {"detail": {}, "workflow_id": "123"}
        response = self.client.post(UPDATE_WORKFLOW, json=args, headers=header).json
        self.assertEqual(response['label'], TOKEN_ERROR)

    @mock.patch.object(Workflow, 'get_model_info')
    def test_update_workflow_should_return_database_error_when_database_is_wrong(self, mock_info):
        mock_info.return_value = {}
        args = {"detail": {}, "workflow_id": "123"}
        with mock.patch("diana.database.dao.workflow_dao.WorkflowDao.connect") as mock_connect:
            mock_connect.return_value = False
            response = self.client.post(UPDATE_WORKFLOW, json=args, headers=header_with_token).json
            self.assertEqual(response['label'], DATABASE_CONNECT_ERROR)

    @mock.patch.object(Workflow, 'get_model_info')
    def test_update_workflow_should_return_succeed_when_given_correct_params(self, mock_info):
        mock_info.return_value = {}
        args = {"detail": {}, "workflow_id": "123"}
        with mock.patch("diana.controllers.workflow_controller.operate") as mock_operate:
            mock_operate.return_value = SUCCEED
            response = self.client.post(UPDATE_WORKFLOW, json=args, headers=header_with_token).json
            self.assertEqual(response['label'], SUCCEED)
