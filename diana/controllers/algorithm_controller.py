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
from diana.database.dao.algo_dao import AlgorithmDao
from diana.utils.schema.algorithm import QueryAlgorithmListSchema, QueryAlgorithmSchema
from diana.conf import configuration


class QueryAlgorithmList(BaseResponse):
    """
    Interface for get algorithm list.
    Restful API: GET
    """

    @BaseResponse.handle(schema=QueryAlgorithmListSchema, proxy=AlgorithmDao, config=configuration)
    def get(self, callback: AlgorithmDao, **params):
        """
            Get algorithm info list
        Returns:
            Response:
                {
                    'code': int,
                    'msg': string,
                    'total_count': int,
                    'total_page': int,
                    'algo_list':[
                            {
                            'algo_id': 'xxx',
                            'algo_name': 'xxx',
                            "description": 'xxx',
                            'field': 'xxx'
                            }
                            ...
                    ]
                }
        """
        status_code, result = callback.query_algorithm_list(params)
        return self.response(code=status_code, data=result)


class QueryAlgorithm(BaseResponse):
    """
    Interface for get algorithm list.
    Restful API: GET
    """

    @BaseResponse.handle(schema=QueryAlgorithmSchema, proxy=AlgorithmDao, config=configuration)
    def get(self, callback: AlgorithmDao, **params):
        """
            Get algorithm info
        Returns:
            Response:
                    {
                        "code": int,
                        "msg": "string",
                        "result": {
                            "algo_id": "string",
                            "algo_name": "string",
                            "description": "string",
                            "field": "string"
                        }
                    }
        """
        status_code, result = callback.query_algorithm(params)
        return self.response(code=status_code, data=result)
