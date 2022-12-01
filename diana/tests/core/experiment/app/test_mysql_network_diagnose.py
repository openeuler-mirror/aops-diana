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
import unittest

from diana.core.experiment.app.mysql_network_diagnose import MysqlNetworkDiagnoseApp


class MysqlNetworkDiagnoseTestCase(unittest.TestCase):
    def test_somoke(self):
        model_info = {
            "intelligent-1": {
                "model_name": "intelligent-1",
                "algo_id": "",
                "algo_name": "Intelligent"
            }
        }
        detail = {
            "multicheck": {
                "host1": "intelligent-1",
                "host2": "intelligent-1"
            }
        }
        data = {
            "host1": {
                "metric1": {
                    "label1": [["1", '2'], ['3', '4'], ['5', '4'], ['7', '5'], ['9', '3'], ['11', '20'], ['13', '22'],
                           ['14', '26'], ['15', '99'], ['16', '100'], ['17', '101'], ['18', '102']],
                    "label2": [["1", '2'], ['3', '4'], ['5', '4'], ['7', '5'], ['9', '3'], ['11', '20'], ['13', '22'],
                           ['14', '26'], ['15', '99'], ['16', '100'], ['17', '101'], ['18', '102']]
                },
                "metric2": {
                    "label1": [["1", '2'], ['3', '4'], ['5', '4'], ['7', '5'], ['9', '3'], ['11', '20'], ['13', '22'],
                               ['14', '26'], ['15', '99'], ['16', '100'], ['17', '101'], ['18', '102']],
                    "label2": [["1", '2'], ['3', '4'], ['5', '4'], ['7', '5'], ['9', '3'], ['11', '20'], ['13', '22'],
                               ['14', '26'], ['15', '99'], ['16', '100'], ['17', '101'], ['18', '102']]
                }
            },
            "host2": {
                "metric1": {
                    "label1": [["1", '2'], ['3', '4'], ['5', '4'], ['7', '5'], ['9', '3'], ['11', '20'], ['13', '22'],
                               ['14', '26'], ['15', '99'], ['16', '100'], ['17', '101'], ['18', '102']],
                    "label2": [["1", '2'], ['3', '4'], ['5', '4'], ['7', '5'], ['9', '3'], ['11', '20'], ['13', '22'],
                               ['14', '26'], ['15', '99'], ['16', '100'], ['17', '101'], ['18', '102']]
                },
                "metric2": {
                    "label1": [["1", '2'], ['3', '4'], ['5', '4'], ['7', '5'], ['9', '3'], ['11', '20'], ['13', '22'],
                               ['14', '26'], ['15', '99'], ['16', '100'], ['17', '101'], ['18', '102']],
                    "label2": [["1", '2'], ['3', '4'], ['5', '4'], ['7', '5'], ['9', '3'], ['11', '20'], ['13', '22'],
                               ['14', '26'], ['15', '99'], ['16', '100'], ['17', '101'], ['18', '102']]
                }
            }
        }
        app = MysqlNetworkDiagnoseApp()
        res = app.execute(model_info, detail, data, True)
        print(res)