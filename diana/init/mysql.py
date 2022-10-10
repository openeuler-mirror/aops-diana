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
from diana.database import ENGINE
from diana.database.factory.table import create_check_tables
from vulcanus.log.log import LOGGER


def init_mysql():
    """
    Initialize user, add a default user: admin
    """
    try:
        create_check_tables(ENGINE)
        LOGGER.info("initialize mysql tables for aops-diana succeed.")
    except sqlalchemy.exc.SQLAlchemyError:
        LOGGER.error("initialize mysql tables for aops-diana failed.")
        raise sqlalchemy.exc.SQLAlchemyError("create tables fail")
