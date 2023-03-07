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
from vulcanus.restful.response import BaseResponse
from diana.database.dao.data_dao import DataDao
from diana.utils.schema.metric import QueryHostMetricDataSchema, QueryHostMetricListSchema, QueryHostMetricNamesSchema
from diana.conf import configuration


class QueryHostMetricNames(BaseResponse):

    @BaseResponse.handle(schema=QueryHostMetricNamesSchema, proxy=DataDao(configuration))
    def get(self, callback: DataDao, **params):
        status_code, result = callback.query_metric_names(params)
        return self.response(code=status_code, data=result)


class QueryHostMetricData(BaseResponse):

    @BaseResponse.handle(schema=QueryHostMetricDataSchema, proxy=DataDao(configuration))
    def post(self, callback: DataDao, **params):
        status_code, result = callback.query_metric_data(params)
        return self.response(code=status_code, data=result)


class QueryHostMetricList(BaseResponse):

    @BaseResponse.handle(schema=QueryHostMetricListSchema, proxy=DataDao(configuration))
    def post(self, callback: DataDao, **params):
        status_code, result = callback.query_metric_list(params)
        return self.response(code=status_code, data=result)
