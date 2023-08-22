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
from elasticsearch import ElasticsearchException

from vulcanus.log.log import LOGGER
from diana.conf import configuration
from diana.database.dao.app_dao import AppDao
from diana.database.factory.mapping import MAPPINGS


def init_es():
    dao = AppDao()

    for index_name, body in MAPPINGS.items():
        res = dao.create_index(index_name, body)
        if not res:
            raise ElasticsearchException("create elasticsearch index %s fail", index_name)

    LOGGER.info("create check related elasticsearch index succeed")

    # update es settings
    config = {"max_result_window": configuration.elasticsearch.get('MAX_ES_QUERY_NUM')}
    dao.update_settings(**config)
