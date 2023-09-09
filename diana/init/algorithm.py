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
import sqlalchemy
import uuid
from copy import deepcopy
from importlib import import_module

from vulcanus.log.log import LOGGER
from vulcanus.restful.resp.state import DATABASE_INSERT_ERROR
from diana.conf.constant import SYSTEM_USER, ALGO_LIST
from diana.database.dao.algo_dao import AlgorithmDao
from diana.database.dao.model_dao import ModelDao


def init_algo_and_model():
    """
    add built in algorithm info into database
    """
    algo_proxy = AlgorithmDao()
    if not algo_proxy.connect():
        LOGGER.error("Connect mysql fail when insert built-in algorithm.")
        raise sqlalchemy.exc.SQLAlchemyError("Connect mysql failed.")

    model_proxy = ModelDao()
    if not model_proxy.connect():
        LOGGER.error("Connect mysql fail when insert built-in model.")
        raise sqlalchemy.exc.SQLAlchemyError("Connect mysql failed.")

    for algo in ALGO_LIST:
        module_path, class_name = algo["algo_module"].rsplit('.', 1)
        algo_module = import_module('.', module_path)
        class_ = getattr(algo_module, class_name)
        algo_info = deepcopy(class_().info)
        algo_id = str(uuid.uuid1()).replace('-', '')
        algo_info["algo_id"] = algo_id
        algo_info["username"] = SYSTEM_USER

        status_code = algo_proxy.insert_algo(algo_info)
        if status_code == DATABASE_INSERT_ERROR:
            LOGGER.error("Insert built-in algorithm '%s' into mysql failed." % algo_info["algo_name"])
            raise sqlalchemy.exc.SQLAlchemyError("Insert mysql failed.")

        model_list = algo["models"]
        for model_info in model_list:
            model_info["algo_id"] = algo_id
            status_code = model_proxy.insert_model(model_info)
            if status_code == DATABASE_INSERT_ERROR:
                LOGGER.error("Insert built-in model '%s' into mysql failed." % model_info["model_name"])
                raise sqlalchemy.exc.SQLAlchemyError("Insert mysql failed.")

        LOGGER.info("Init built-in algorithm and model succeed.")
