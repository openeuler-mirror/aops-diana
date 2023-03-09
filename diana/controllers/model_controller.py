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
from vulcanus.restful.response import BaseResponse
from diana.database.dao.model_dao import ModelDao
from diana.utils.schema.model import QueryModelListSchema


class QueryModelList(BaseResponse):
    """
    Query model list interface, it's a post request.
    """

    @BaseResponse.handle(schema=QueryModelListSchema, proxy=ModelDao())
    def post(self, callback: ModelDao, **params):
        """
        It's post request, step:
            1.verify token
            2.verify args
            3.get model list from database
        """

        status_code, result = callback.get_model_list(params)
        return self.response(code=status_code, data=result)
