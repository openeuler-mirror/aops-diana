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
import time
from typing import Dict, Optional, Tuple
from collections import defaultdict
import sqlalchemy
from sqlalchemy import func
from sqlalchemy.exc import SQLAlchemyError
from elasticsearch import ElasticsearchException

from vulcanus.database.helper import sort_and_page
from vulcanus.database.proxy import ElasticsearchProxy, MysqlProxy
from vulcanus.log.log import LOGGER
from vulcanus.restful.resp.state import (
    SUCCEED,
    DATABASE_INSERT_ERROR,
    DATABASE_QUERY_ERROR,
    NO_DATA,
    DATABASE_UPDATE_ERROR,
    DATABASE_DELETE_ERROR,
    DATA_EXIST,
)

from diana.database.factory.table import WorkflowHostAssociation, Workflow
from diana.conf.constant import WORKFLOW_INDEX


class WorkflowDao(MysqlProxy, ElasticsearchProxy):
    """
    Workflow related database operation
    """

    def __init__(self, host=None, port=None):
        """
        Instance initialization

        Args:
            configuration (Config)
            host(str)
            port(int)
        """
        MysqlProxy.__init__(self)
        ElasticsearchProxy.__init__(self, host, port)

    def insert_workflow(self, data: dict) -> str:
        """
        Insert workflow basic info into mysql and elasticsearch
        Args:
            data: parameter, e.g.
                {
                    "username": "admin",
                    "workflow_id": "id1",
                    "workflow_name": "workflow1",
                    "description": "a long description",
                    "status": "hold",
                    "app_name": "app1",
                    "app_id": "asd",
                    "input": {
                        "domain": "host_group_1",
                        "hosts": {"host1": {"host_ip": "127.0.0.1", "scene": "big_data",
                                  "host_name": "host1"}}
                    },
                    "step": 60,
                    "period": 900,
                    "alert": {},
                    "detail": {
                        "singlecheck": {
                            "host_id1": {
                                "metric1": "3sigma"
                            }
                        },
                        "multicheck": {
                            "host_id1": "statistic"
                        },
                        "diag": "statistic"
                    },
                    "model_info": {
                        "model_id1": {
                            "model_name": "model name1",
                            "algo_name": "algo1",
                            "algo_id": "algo_id1"
                        }
                    }
                }
        Returns:
            str: status code
        """
        try:
            status_code = self._insert_workflow(data)
            self.session.commit()
            LOGGER.debug("Finished inserting new workflow.")
            return status_code
        except (SQLAlchemyError, ElasticsearchException) as error:
            self.session.rollback()
            LOGGER.error(error)
            LOGGER.error("Insert new workflow failed due to internal error.")
            return DATABASE_INSERT_ERROR

    def _insert_workflow(self, data: dict) -> str:
        """
        insert a workflow into database。
        1. insert workflow basic info into mysql workflow table
        2. isnert host workflow relationship into mysql workflow_host table
        3. insert workflow's detail and model info into elasticsearch
        Args:
            data: workflow info

        Returns:

        """
        workflow_name = data["workflow_name"]
        username = data["username"]

        if self._if_workflow_name_exists(workflow_name, username):
            LOGGER.debug("Insert workflow failed due to workflow name already exists.")
            return DATA_EXIST

        data.pop("alert")
        input_hosts = data.pop("input")
        hosts_info = input_hosts["hosts"]
        detail = data.pop("detail")
        model_info = data.pop("model_info")

        data["domain"] = input_hosts["domain"]

        # workflow table need commit after add, otherwise following insertion will fail due to
        # workflow.workflow_id foreign key constraint.
        workflow = Workflow(**data)
        self.session.add(workflow)
        self.session.commit()

        workflow_id = data["workflow_id"]
        try:
            self._insert_workflow_host_table(workflow_id, hosts_info)
            status_code = self._insert_workflow_into_es(username, workflow_id, detail, model_info)
            if status_code != SUCCEED:
                raise ElasticsearchException("Insert workflow '%s' in to elasticsearch failed." % workflow_id)

        except (SQLAlchemyError, ElasticsearchException):
            self.session.rollback()
            self.session.query(Workflow).filter(Workflow.workflow_id == workflow_id).delete()
            self.session.commit()
            raise
        return SUCCEED

    def _insert_workflow_host_table(self, workflow_id: str, hosts_info: dict):
        """
        insert workflow and host's relationship into workflow_host_association table
        Args:
            workflow_id: workflow id
            hosts_info: host info dict

        """
        rows = []
        for host_id, host_info in hosts_info.items():
            row = {
                "workflow_id": workflow_id,
                "host_id": host_id,
                "host_ip": host_info["host_ip"],
                "host_name": host_info["host_name"],
            }
            rows.append(row)

        self.session.bulk_insert_mappings(WorkflowHostAssociation, rows)

    def _if_workflow_name_exists(self, workflow_name: str, username: str):
        """
        if the workflow name already exists in mysql
        Args:
            workflow_name: workflow name
            username: user name

        Returns:
            bool
        """
        workflow_count = (
            self.session.query(func.count(Workflow.workflow_name))
            .filter(Workflow.workflow_name == workflow_name, Workflow.username == username)
            .scalar()
        )
        if workflow_count:
            return True
        return False

    def _if_workflow_id_exists(self, workflow_id: str, username: str):
        """
        if the workflow exists in mysql
        Args:
            workflow_id: workflow id
            username: user name

        Returns:
            bool
        """
        workflow = self.session.query(Workflow).filter(
            Workflow.workflow_id == workflow_id, Workflow.username == username
        )
        if len(workflow.all()):
            return True
        return False

    def _insert_workflow_into_es(
        self, username: str, workflow_id: str, detail: dict, model_info: dict, index: Optional[str] = WORKFLOW_INDEX
    ) -> str:
        """
        insert workflow's detail info and model info into elasticsearch
        """
        data = {"workflow_id": workflow_id, "username": username, "detail": detail, "model_info": model_info}

        res = ElasticsearchProxy.insert(self, index, data, document_id=workflow_id)
        if res:
            LOGGER.info("Add workflow '%s' info into es succeed.", workflow_id)
            return SUCCEED
        LOGGER.error("Add workflow '%s' info into es failed", workflow_id)
        return DATABASE_INSERT_ERROR

    def get_workflow_list(self, data: dict) -> Tuple[str, Dict]:
        """
        Get workflow list of a user

        Args:
            data(dict): parameter, e.g.
                {
                    "page": 1,
                    "per_page": 10,
                    "username": "admin",
                    "filter": {
                        "app": ["app1"],
                        "domain": ["host_group1"],
                        "status": ["hold","running","recommending"]
                    }
                }

        Returns:
            str: status code
            dict: query result. e.g.
                {
                    "total_count": 1,
                    "total_page": 1,
                    "workflows": [
                        {
                            "workflow_id": "123456",
                            "workflow_name": "workflow1",
                            "description": "a long description",
                            "status": "hold",
                            "app_name": "app1",
                            "app_id": "app_id",
                            "input": {
                                "domain": "host_group1",
                                "hosts": {"host1": {"host_ip": "127.0.0.1", "scene": "big_data",
                                          "host_name": "host1"}}
                            }
                        }
                    ]
                }
        """
        result = {}
        try:
            result = self._get_workflow_list(data)
            self.session.commit()
            LOGGER.debug("Finished getting workflow list.")
            return SUCCEED, result
        except SQLAlchemyError as error:
            LOGGER.error(error)
            LOGGER.error("Get workflow list failed due to internal error.")
            return DATABASE_QUERY_ERROR, result

    def _get_workflow_list(self, data: dict) -> Dict:
        """
        get workflow from database
        Args:
            data: query info

        Returns:
            dict: query result
        """
        result = {"total_count": 0, "total_page": 1, "result": []}

        workflow_query = self._query_workflow_list(data["username"], data.get("filter"))
        total_count = len(workflow_query.all())
        if not total_count:
            return result

        direction, page, per_page = data.get('direction'), data.get('page'), data.get('per_page')
        if data.get("sort"):
            sort_column = getattr(Workflow, data["sort"])
        else:
            sort_column = None
        processed_query, total_page = sort_and_page(workflow_query, sort_column, direction, per_page, page)

        workflow_id_list = [row.workflow_id for row in processed_query]
        workflow_host = self._get_workflow_hosts(workflow_id_list)
        result['result'] = self.__process_workflow_list_info(processed_query, workflow_host)
        result['total_page'] = total_page
        result['total_count'] = total_count
        return result

    def _query_workflow_list(self, username: str, filter_dict: Optional[dict]) -> sqlalchemy.orm.query.Query:
        """
        query needed workflow basic info list
        Args:
            username: user name
            filter_dict: dict.  e.g.
                {
                    "app": ["app1"],
                    "domain": ["host_group1"],
                    "status": ["running", "recommending"]
                }

        Returns:
            sqlalchemy.orm.query.Query
        """
        filters = set()
        filters.add(Workflow.username == username)
        if filter_dict:
            if filter_dict.get("domain"):
                filters.add(Workflow.domain.in_(filter_dict["domain"]))
            if filter_dict.get("status"):
                filters.add(Workflow.status.in_(filter_dict["status"]))
            if filter_dict.get("app"):
                filters.add(Workflow.app_name.in_(filter_dict["app"]))

        workflow_query = self.session.query(
            Workflow.workflow_name,
            Workflow.workflow_id,
            Workflow.description,
            Workflow.create_time,
            Workflow.status,
            Workflow.app_name,
            Workflow.app_id,
            Workflow.domain,
        ).filter(*filters)
        return workflow_query

    def _get_workflow_hosts(self, workflow_id_list: list) -> Dict:
        """
        get workflow host list
        Args:
            workflow_id_list: workflow id list

        Returns:
            dict: workflow's hosts, e.g.
                {
                    "workflow1": {
                        "host_id1": {
                            "host_ip": "127.0.0.1",
                            "host_name": "host1"
                        }
                    }
                }
        """
        hosts_query = self.session.query(
            WorkflowHostAssociation.workflow_id,
            WorkflowHostAssociation.host_id,
            WorkflowHostAssociation.host_ip,
            WorkflowHostAssociation.host_name,
        ).filter(WorkflowHostAssociation.workflow_id.in_(workflow_id_list))

        workflow_host = defaultdict(dict)
        for row in hosts_query:
            workflow_host[row.workflow_id][row.host_id] = {"host_ip": row.host_ip, "host_name": row.host_name}

        return dict(workflow_host)

    @staticmethod
    def __process_workflow_list_info(workflow_info: sqlalchemy.orm.query.Query, workflow_host: dict) -> list:
        """
        combine workflow info and workflow's host together.
        In some abnormal circumstance, workflow may has no hosts, here we give empty host
        list to the workflow
        """
        result = []
        for row in workflow_info:
            workflow_info = {
                "workflow_name": row.workflow_name,
                "description": row.description,
                "create_time": row.create_time,
                "status": row.status,
                "app_name": row.app_name,
                "app_id": row.app_id,
                "input": {"domain": row.domain, "hosts": workflow_host.get(row.workflow_id, {})},
                "workflow_id": row.workflow_id,
            }
            result.append(workflow_info)
        return result

    def get_all_workflow_list(self, status: str) -> Tuple[str, dict]:
        """
        get all users' workflow list. It's a internal interface for scheduler
        Args:
            status: needed workflow status

        Returns:
            dict,  e.g.
            {
                "workflow_id1": {
                    "workflow_name": "workflow1",
                    "username": "admin",
                    "step": 5
                }
            }
        """
        result = {}
        try:
            status_code, result = self._get_all_workflow_list(status)
            LOGGER.debug("Finished getting all users' workflow list.")
            return status_code, result
        except SQLAlchemyError as error:
            LOGGER.error(error)
            LOGGER.error("Get all users' workflow list failed due to internal error.")
            return DATABASE_QUERY_ERROR, result

    def _get_all_workflow_list(self, status: str) -> Tuple[str, dict]:
        """
        get all users' workflow from mysql
        """
        result = {}
        workflow_query = self.session.query(
            Workflow.username, Workflow.workflow_id, Workflow.workflow_name, Workflow.step
        ).filter(Workflow.status == status)

        if not workflow_query.count():
            return NO_DATA, result

        result = {}
        for row in workflow_query:
            result[row.workflow_id] = {"workflow_name": row.workflow_name, "username": row.username, "step": row.step}
        return SUCCEED, result

    def get_workflow(self, data) -> Tuple[str, dict]:
        """
        get workflow's detail info
        Args:
            data:  e.g. {"username": "admin", "workflow_id": ""}

        Returns:
            dict: workflow detail info  e.g.
                {
                    "result": {
                        "workflow_id": "workflow_id1",
                        "workflow_name": "workflow_name1",
                        "description": "a long description",
                        "create_time": 1662533585,
                        "status": "running/hold/recommending",
                        "app_name": "app1",
                        "app_id": "app_id1",
                        "input": {
                            "domain": "host_group1",
                            "hosts": {
                                "host_id1": {
                                    "host_ip": "127.0.0.1",
                                    "host_name": "host1"
                                }
                            }
                        },
                        "step": 60,
                        "period": 900,
                        "alert": {},
                        "detail": {
                            {
                                "singlecheck": {
                                    "host_id1": {
                                        "metric1": "3sigma"
                                    }
                                },
                                "multicheck": {
                                    "host_id1": "statistic"
                                },
                                "diag": "statistic"
                            }
                        },
                        "model_info": {
                            "model_id1": {
                                "model_name": "model_name1",
                                "algo_id": "algo_id1",
                                "algo_name": "algo_name1"
                            }
                        }
                    }
                }
        """
        result = {}
        try:
            status_code, result = self._get_workflow_info(data)
            self.session.commit()
            LOGGER.debug("Finished getting workflow info.")
            return status_code, result
        except (SQLAlchemyError, ElasticsearchException) as error:
            LOGGER.error(error)
            LOGGER.error("Get workflow info failed due to internal error.")
            return DATABASE_QUERY_ERROR, result

    def _get_workflow_info(self, data) -> Tuple[str, dict]:
        """
        get workflow basic info from mysql and detail info from elasticsearch
        Args:
            data: e.g. {"username": "admin", "workflow_id": ""}

        Returns:
            str, dict
        """
        basic_info = self._get_workflow_basic_info(data["username"], data["workflow_id"])
        status_code, detail_info = self._get_workflow_detail_info(data)
        if status_code != SUCCEED:
            return status_code, {}

        basic_info.update(detail_info)
        return SUCCEED, {"result": basic_info}

    def _get_workflow_basic_info(self, username: str, workflow_id: str) -> dict:
        """
        get workflow basic info such as name, description, app_id... from mysql table
        Args:
            username: user name
            workflow_id: workflow id
        Returns:
            dict
        """
        filters = set()
        filters.add(Workflow.username == username)
        filters.add(Workflow.workflow_id == workflow_id)

        workflow_query = (
            self.session.query(
                Workflow.workflow_name,
                Workflow.workflow_id,
                Workflow.description,
                Workflow.create_time,
                Workflow.status,
                Workflow.app_name,
                Workflow.app_id,
                Workflow.domain,
                Workflow.step,
                Workflow.period,
            )
            .filter(*filters)
            .one()
        )

        workflow_host = self._get_workflow_hosts([workflow_id])

        workflow_info = {
            "workflow_name": workflow_query.workflow_name,
            "description": workflow_query.description,
            "create_time": workflow_query.create_time,
            "status": workflow_query.status,
            "app_name": workflow_query.app_name,
            "app_id": workflow_query.app_id,
            "input": {"domain": workflow_query.domain, "hosts": workflow_host.get(workflow_query.workflow_id, {})},
            "step": workflow_query.step,
            "period": workflow_query.period,
            "workflow_id": workflow_query.workflow_id,
        }
        return workflow_info

    def _get_workflow_detail_info(self, data, index: str = WORKFLOW_INDEX) -> Tuple[str, dict]:
        """
        Get workflow detail info from elasticsearch
        Args:
            data:  e.g. {"workflow_id": ""}
        Returns:
            dict:  e.g. {"detail": {}}
        """
        result = {}
        query_body = self._general_body(data)
        query_body["query"]["bool"]["must"].append({"term": {"workflow_id": data["workflow_id"]}})
        status, res = self.query(index, query_body)
        if status:
            if len(res['hits']['hits']) == 0:
                return NO_DATA, result
            LOGGER.debug("query workflow %s succeed", data['workflow_id'])
            result = res['hits']['hits'][0]['_source']
            return SUCCEED, result

        LOGGER.error("query workflow %s fail", data['workflow_id'])
        return DATABASE_QUERY_ERROR, result

    def update_workflow(self, data) -> str:
        """
        Update workflow
        Args:
            data: workflow's info.  e.g.
                {
                    "username": "admin",
                    "workflow_id": "",
                    "workflow_name": "new_name",
                    "description": "new description",
                    "step": 10,
                    "period": 10,
                    "alert": {},
                    "detail": {
                        {
                            "singlecheck": {
                                "host_id1": {
                                    "metric1": "3sigma"
                                }
                            },
                            "multicheck": {
                                "host_id1": "statistic"
                            },
                            "diag": "statistic"
                        }
                    }
                }

        Returns:

        """
        try:
            status_code = self._update_workflow(data)
            LOGGER.debug("Finished updating workflow info.")
            self.session.commit()
            return status_code
        except (SQLAlchemyError, ElasticsearchException) as error:
            self.session.rollback()
            LOGGER.error(error)
            LOGGER.error("Updating workflow info failed due to internal error.")
            return DATABASE_UPDATE_ERROR

    def _update_workflow(self, data):
        """
        update workflow basic info into mysql, detail info into elasticsearch
        """
        workflow_exist = self._if_workflow_id_exists(data["workflow_id"], data["username"])
        if not workflow_exist:
            return NO_DATA

        self._update_workflow_basic_info(data)
        status_code = self._update_workflow_detail_info(data)
        time.sleep(1)
        return status_code

    def _update_workflow_basic_info(self, data):
        """
        update workflow's basic info in mysql
        """
        basic_info_row = {}
        if "workflow_name" in data:
            basic_info_row["workflow_name"] = data["workflow_name"]
        if "description" in data:
            basic_info_row["description"] = data["description"]
        if "step" in data:
            basic_info_row['step'] = data["step"]
        if "period" in data:
            basic_info_row['period'] = data["period"]

        if not basic_info_row:
            return
        self.session.query(Workflow).filter(
            Workflow.username == data["username"], Workflow.workflow_id == data["workflow_id"]
        ).update(basic_info_row)

    def _update_workflow_detail_info(self, data: dict, index: str = WORKFLOW_INDEX) -> str:
        """
        update workflow's detail info in es
        """
        workflow_id = data["workflow_id"]
        action = [{"_id": workflow_id, "_source": data, "_index": index}]
        update_res = self._bulk(action)

        if not update_res:
            return DATABASE_UPDATE_ERROR
        return SUCCEED

    def delete_workflow(self, data: dict) -> str:
        """
        delete workflow by id
        Args:
            data (dict): parameter, e.g.
                {
                    "username": "admin",
                    "workflow_id": "workflow_id1"
                }

        Returns:
            str: status code
        """
        try:
            status_code = self._delete_workflow(data)
            self.session.commit()
            LOGGER.debug("Finished deleting workflow.")
            return status_code
        except (SQLAlchemyError, ElasticsearchException) as error:
            self.session.rollback()
            LOGGER.error(error)
            LOGGER.error("Deleting workflow failed due to internal error.")
            return DATABASE_DELETE_ERROR

    def _delete_workflow(self, data, index: str = WORKFLOW_INDEX) -> str:
        if self._if_workflow_running(data):
            return DATABASE_DELETE_ERROR

        username = data["username"]
        workflow_id = data["workflow_id"]
        filters = {Workflow.workflow_id == workflow_id, Workflow.username == username}
        self.session.query(Workflow).filter(*filters).delete()

        query_body = self._general_body()
        query_body["query"]["bool"]["must"].extend(
            [{"term": {"username": data["username"]}}, {"term": {"workflow_id": workflow_id}}]
        )

        res = ElasticsearchProxy.delete(self, index, query_body)
        if res:
            LOGGER.debug("Delete workflow from elasticsearch succeed.")
            return SUCCEED

        LOGGER.error("Delete workflow from elasticsearch failed due to internal error.")
        return DATABASE_DELETE_ERROR

    def _if_workflow_running(self, data) -> bool:
        """
        check if workflow running or recommending
        """
        username = data["username"]
        workflow_id = data["workflow_id"]

        filters = {Workflow.username == username, Workflow.workflow_id == workflow_id}
        workflow_query = self.session.query(Workflow.status).filter(*filters).one()

        if workflow_query.status in ("running", "recommending"):
            LOGGER.info("Delete workflow '%s' failed because it's still %s" % (workflow_id, workflow_query.status))
            return True
        return False

    def update_workflow_status(self, workflow_id, status):
        """
        update workflow status
        """
        self.session.query(Workflow).filter(Workflow.workflow_id == workflow_id).update({"status": status})
        self.session.commit()

    def if_host_in_workflow(self, data: dict) -> Tuple[str, dict]:
        """
        if host exist workflow
        Args:
            data (dict): parameter, e.g.
                {
                    "username": "admin",
                    "host_list": ["host_id1", "host_id2"]
                }

        Returns:
            str: status code
            bool: if host exists or not:  {"host_id1": True, "host_id2": False}
        """
        result = {}
        try:
            result = self._query_host_in_workflow(data)
            LOGGER.debug("Query if a host exists in a workflow succeed.")
            return SUCCEED, {"result": result}
        except SQLAlchemyError as error:
            LOGGER.error(error)
            LOGGER.error("Query if a host exists in a workflow failed due to internal error.")
            return DATABASE_QUERY_ERROR, result

    def _query_host_in_workflow(self, data):
        host_query = (
            self.session.query(
                WorkflowHostAssociation.host_id, func.count(WorkflowHostAssociation.workflow_id).label("workflow_num")
            )
            .join(Workflow, Workflow.workflow_id == WorkflowHostAssociation.workflow_id)
            .filter(WorkflowHostAssociation.host_id.in_(data["host_list"]), Workflow.username == data["username"])
            .group_by(WorkflowHostAssociation.host_id)
        )

        result = {host_id: False for host_id in data["host_list"]}
        for row in host_query.all():
            if row.workflow_num:
                result[row.host_id] = True

        return result
