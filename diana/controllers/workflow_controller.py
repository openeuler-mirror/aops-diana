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
import uuid
import time
from typing import Dict, Tuple
from flask import request
import sqlalchemy
from vulcanus.restful.response import BaseResponse
from vulcanus.restful.resp.state import SUCCEED, WORKFLOW_ASSIGN_MODEL_FAIL, DATABASE_CONNECT_ERROR
from vulcanus.log.log import LOGGER

from diana.database.dao.workflow_dao import WorkflowDao
from diana.core.rule.workflow import Workflow
from diana.utils.schema.workflow import (
    CreateWorkflowSchema,
    QueryWorkflowSchema,
    QueryWorkflowListSchema,
    DeleteWorkflowSchema,
    UpdateWorkflowSchema,
    IfHostInWorkflowSchema,
    ExecuteWorkflowSchema,
    StopWorkflowSchema,
)
from diana.errors.workflow_error import WorkflowModelAssignError
from diana.core.check.check_scheduler.check_scheduler import check_scheduler


class CreateWorkflow(BaseResponse):
    """
    Create workflow interface, it's a post request.
    """

    def _handle(self, args: dict) -> Tuple[int, Dict[str, str]]:
        """
        Args:
            args: dict of workflow info, e.g.
                {
                    "username": "admin",
                    "workflow_name": "workflow1",
                    "description": "a long description",
                    "app_name": "app1",
                    "app_id": "asd",
                    "input": {
                        "domain": "host_group_1",
                        "hosts": [1, 2]     // host id list
                    },
                    "step": 60,  // optional
                    "period": 900,  // optional
                    "alert": {}  // optional
                }
        """
        result = {}

        access_token = request.headers.get('access_token')
        try:
            host_infos, detail = Workflow.assign_model(
                args["username"], access_token, args["app_id"], args["input"]["hosts"], "app"
            )
        except (WorkflowModelAssignError, KeyError) as error:
            LOGGER.debug(error)
            return WORKFLOW_ASSIGN_MODEL_FAIL, result

        model_info = Workflow.get_model_info(detail)

        args['step'] = args.get('step', 60)
        args["period"] = args.get("period", 60)
        args["alert"] = args.get("alert", {})
        args["create_time"] = int(time.time())
        args["status"] = "hold"
        workflow_id = str(uuid.uuid1()).replace('-', '')
        args['workflow_id'] = workflow_id
        args["detail"] = detail
        args["model_info"] = model_info
        # change host id list to host info dict
        args["input"]["hosts"] = host_infos
        try:
            with WorkflowDao() as workflow_proxy:
                status = workflow_proxy.insert_workflow(args)
        except sqlalchemy.exc.SQLAlchemyError:
            return DATABASE_CONNECT_ERROR, result

        if status != SUCCEED:
            return status, result

        result['workflow_id'] = workflow_id
        return status, result

    @BaseResponse.handle(schema=CreateWorkflowSchema)
    def post(self, **params):
        """
        It's post request, step:
            1.verify token;
            2.verify args;
            3.add default args
            4.insert into database
        """
        status_code, result = self._handle(params)
        return self.response(code=status_code, data=result)


class QueryWorkflow(BaseResponse):
    """
    Query workflow interface, it's a get request.
    """

    @BaseResponse.handle(schema=QueryWorkflowSchema)
    def get(self, **params):
        """
        It's get request, step:
            1.verify token
            2.verify args
            3.get workflow from database
        """
        try:
            with WorkflowDao() as workflow_proxy:
                status_code, result = workflow_proxy.get_workflow(params)

            return self.response(code=status_code, data=result)
        except sqlalchemy.exc.SQLAlchemyError:
            return self.response(code=DATABASE_CONNECT_ERROR)


class QueryWorkflowList(BaseResponse):
    """
    Query workflow interface, it's a post request.
    """

    @BaseResponse.handle(schema=QueryWorkflowListSchema)
    def post(self, **params):
        """
        It's post request, step:
            1.verify token
            2.verify args
            3.get workflow list from database
        """
        try:
            with WorkflowDao() as workflow_proxy:
                status_code, result = workflow_proxy.get_workflow_list(params)

            return self.response(code=status_code, data=result)
        except sqlalchemy.exc.SQLAlchemyError:
            return self.response(code=DATABASE_CONNECT_ERROR)


class ExecuteWorkflow(BaseResponse):
    """
    Execute workflow interface, it's a post request
    """

    def _handle(self, args: dict) -> int:
        """
        Args:
            args: dict of workflow id, e.g.
                {
                    "username": "admin",
                    "workflow_id": "workflow_id1"
                }
        """
        workflow_id = args["workflow_id"]
        username = args["username"]
        try:
            with WorkflowDao() as workflow_proxy:
                status_code, result = workflow_proxy.get_workflow(args)

                if status_code != SUCCEED:
                    return status_code

                workflow_info = result["result"]
                if workflow_info["status"] != "hold":
                    LOGGER.info(
                        "Workflow '%s' cannot execute with status '%s'." % (workflow_id, workflow_info["status"])
                    )
                    return SUCCEED

                workflow_proxy.update_workflow_status(workflow_id, "running")
                check_scheduler.start_workflow(workflow_id, username, workflow_info["step"])

        except sqlalchemy.exc.SQLAlchemyError:
            return DATABASE_CONNECT_ERROR

        return SUCCEED

    @BaseResponse.handle(schema=ExecuteWorkflowSchema)
    def post(self, **params):
        """
        It's a post request, step
            1.verify token
            2.verify args
            3.check workflow exists or not, check status and change to running
            4.execute workflow
        """
        return self.response(code=self._handle(params))


class StopWorkflow(BaseResponse):
    """
    Stop workflow interface, it's a post request
    """

    def _handle(self, args: dict) -> int:
        """
        Args:
            args: dict of workflow id, e.g.
                {
                    "username": "admin",
                    "workflow_id": "workflow_id1"
                }
        """
        workflow_id = args["workflow_id"]
        try:
            with WorkflowDao() as workflow_proxy:
                status_code, result = workflow_proxy.get_workflow(args)

                if status_code != SUCCEED:
                    return status_code

                workflow_info = result["result"]
                if workflow_info["status"] != "running":
                    LOGGER.info("Workflow '%s' cannot stop with status '%s'." % (workflow_id, workflow_info["status"]))
                    return SUCCEED

                workflow_proxy.update_workflow_status(workflow_id, "hold")
                check_scheduler.stop_workflow(workflow_id)

        except sqlalchemy.exc.SQLAlchemyError:
            return DATABASE_CONNECT_ERROR
        else:
            return SUCCEED

    @BaseResponse.handle(schema=StopWorkflowSchema)
    def post(self, **params):
        """
        It's a post request, step
            1.verify token
            2.verify args
            3.check workflow exists or not, check status and change to hold
            4.stop workflow
        """
        return self.response(code=self._handle(params))


class DeleteWorkflow(BaseResponse):
    """
    Delete workflow interface, it's a delete request.
    """

    @BaseResponse.handle(schema=DeleteWorkflowSchema)
    def delete(self, **params):
        """
        It's delete request, step:
            1.verify token
            2.verify args
            3.check if workflow running
            4.delete workflow from database
        """
        try:
            with WorkflowDao() as workflow_proxy:
                status = workflow_proxy.delete_workflow(params)
            return self.response(code=status)

        except sqlalchemy.exc.SQLAlchemyError:
            return self.response(code=DATABASE_CONNECT_ERROR)


class UpdateWorkflow(BaseResponse):
    """
    Update workflow interface, it's a post request.
    """

    def _handle(self, args: dict):
        """
        create new model info based on the detail info given by request
        Args:
            args:  e.g.
                {
                    "username": "admin",
                    "workflow_id": "id1",
                    "workflow_name": "new_name",
                    "description": "new description",
                    "step": 10,
                    "period": 10,
                    "alert": {},
                    "detail": {...}
                }

        Returns:
            dict: a dict with detail info and model info
        """
        model_info = Workflow.get_model_info(args["detail"])
        args["model_info"] = model_info
        try:
            with WorkflowDao() as workflow_proxy:
                status = workflow_proxy.update_workflow(args)
            return status

        except sqlalchemy.exc.SQLAlchemyError:
            return DATABASE_CONNECT_ERROR

    @BaseResponse.handle(schema=UpdateWorkflowSchema)
    def post(self, **params):
        """
        It's post request, step:
            1.verify token
            2.verify args
            3.update workflow in database
        """
        return self.response(code=self._handle(params))


class IfHostInWorkflow(BaseResponse):
    """
    if hosts exist workflow
    """

    @BaseResponse.handle(schema=IfHostInWorkflowSchema)
    def post(self, **params):
        """
        It's get request, step:
            1.verify token
            2.verify args
            3.check if host in a workflow
        """

        try:
            with WorkflowDao() as workflow_proxy:
                status_code, result = workflow_proxy.if_host_in_workflow(params)

            return self.response(code=status_code, data=result)

        except sqlalchemy.exc.SQLAlchemyError:
            return self.response(code=DATABASE_CONNECT_ERROR)
