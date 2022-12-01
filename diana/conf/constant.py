#!/usr/bin/python3
# ******************************************************************************
# Copyright (c) Huawei Technologies Co., Ltd. 2021-2022. All rights reserved.
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
import os

# system config
BASE_CONFIG_PATH = '/etc/aops'
# check config
CHECK_CONFIG_PATH = os.path.join(BASE_CONFIG_PATH, 'diana.ini')
MODEL_FOLDER_PATH = "/opt/aops/models"
HOST_IP_INFO_LIST = os.path.join(BASE_CONFIG_PATH, 'diana_hosts.json')

APP_INDEX = "app"
WORKFLOW_INDEX = "workflow"

# route
QUERY_APP_LIST = "/check/app/list"
QUERY_APP = "/check/app"
CREATE_APP = "/check/app/create"

QUERY_ALGO_LIST = '/check/algo/list'
QUERY_ALGO = '/check/algo'

QUERY_HOST_CHECK_RESULT = '/check/result/host'
QUERY_HOST_CHECK_RESULT_LIST = '/check/result/list'
QUERY_RESULT_TOTAL_COUNT = '/check/result/total/count'
CHECK_RESULT_CONFIRM = '/check/result/confirm'
QUERY_DOMAIN_COUNT = '/check/result/domain/count'

IDENTIFY_SCENE = "/check/scene/identify"
CREATE_WORKFLOW = "/check/workflow/create"
QUERY_WORKFLOW = "/check/workflow"
QUERY_WORKFLOW_LIST = "/check/workflow/list"
EXECUTE_WORKFLOW = "/check/workflow/execute"
STOP_WORKFLOW = "/check/workflow/stop"
DELETE_WORKFLOW = "/check/workflow"
UPDATE_WORKFLOW = "/check/workflow/update"
IF_HOST_IN_WORKFLOW = "/check/workflow/host/exist"
QUERY_MODEL_LIST = "/check/algo/model/list"
DOWNLOAD_HOST_CHECK_RESULT = '/check/report/download'
QUERY_HOST_DETAIL = "/manage/host/info/query"

# a user for built-in algorithm and model
SYSTEM_USER = "system"

# metric config
QUERY_METRIC_NAMES = '/check/host/metric/names'
QUERY_METRIC_DATA = '/check/host/metric/data'
QUERY_METRIC_LIST = '/check/host/metric/list'

ALGO_LIST = [
    {
        "algo_module": "diana.core.experiment.algorithm.multi_item_check.intelligent.Intelligent",
        "models": [{
            "username": SYSTEM_USER,
            "model_id": "intelligent-1",
            "model_name": "intelligent-1",
            "algo_id": "",
            "create_time": 1660471200,
            "tag": "",
            "file_path": "/etc/aops/algorithm/mysql_intelligent.json",
            # "file_path": r"D:\lostway\debugtheworld\diana-debug\aops-diana\conf\algorithm\test.json",
            "precision": None
        }]
    }
]