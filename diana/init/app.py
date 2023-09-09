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
from vulcanus.log.log import LOGGER
from vulcanus.restful.resp.state import DATA_EXIST, SUCCEED
from diana.core.experiment.app.mysql_network_diagnose import MysqlNetworkDiagnoseApp
from diana.database.dao.app_dao import AppDao

default_app = [MysqlNetworkDiagnoseApp]


def init_app():
    dao = AppDao()

    for app in default_app:
        info = app().info
        status_code = dao.create_app(info)
        if status_code == DATA_EXIST:
            LOGGER.warning(f"The app {info['app_name']} has existed, choose to ignore")
        elif status_code != SUCCEED:
            LOGGER.error(f"Import default app {info['app_name']} fail")

    LOGGER.info("Import default app done")
