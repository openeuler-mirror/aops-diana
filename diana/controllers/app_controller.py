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

from vulcanus.restful.response import BaseResponse
from vulcanus.restful.resp.state import SUCCEED

from diana.conf import configuration
from diana.database.dao.app_dao import AppDao
from diana.utils.schema.app import CreateAppSchema, QueryAppListSchema, QueryAppSchema


class CreateApp(BaseResponse):
    """
    Create app interface, it's a post request.
    """

    @BaseResponse.handle(schema=CreateAppSchema, proxy=AppDao, config=configuration)
    def post(self, callback: AppDao, **params):
        """
        It's post request, step:
            1.verify token;
            2.verify args;
            3.generate uuid
            4.insert into database
        """
        result = dict()
        app_id = str(uuid.uuid1()).replace('-', '')
        params['app_id'] = app_id
        status = callback.create_app(params)
        if status == SUCCEED:
            result['app_id'] = app_id

        return self.response(code=status, data=result)


class QueryAppList(BaseResponse):
    """
    Query app list interface, it's a get request.
    """

    @BaseResponse.handle(schema=QueryAppListSchema, proxy=AppDao, config=configuration)
    def get(self, callback: AppDao, **params):
        """
        It's get request, step:
            1.verify token
            2.verify args
            3.insert into database
        """
        status_code, result = callback.query_app_list(params)
        return self.response(code=status_code, data=result)


class QueryApp(BaseResponse):
    """
    Query app interface, it's a get request.
    """

    @BaseResponse.handle(schema=QueryAppSchema, proxy=AppDao, config=configuration)
    def get(self, callback: AppDao, **param):
        """
        It's get request, step:
            1.verify token
            2.verify args
            3.insert into database
        """
        status_code, result = callback.query_app(param)
        return self.response(code=status_code, data=result)
