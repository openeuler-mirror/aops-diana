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
from collections import defaultdict
from typing import Dict, List

from diana.core.experiment.algorithm import Algorithm
from diana.core.experiment.app import App


class MysqlNetworkDiagnoseApp(App):
    @property
    def info(self):
        info = {
            "app_id": "mysql_network",
            "app_name": "mysql_network",
            "version": "1.0",
            "description": "",
            "username": "admin",
            "api": {"type": "api", "address": "execute"},
            "detail": {"multicheck": {"default_model": "intelligent-for-mysql"}},
        }
        return info

    def do_check(self, detail: Dict[str, str], data: Dict[str, List[str]], time_range: list) -> Dict[str, List[int]]:
        """
        Args:
            detail: it's a map between metric and model. e.g.
                {
                    "host1": "model1",
                    "host2": "model2"
                }
            data: input original data. e.g.
                {
                    'id1': {
                        "metric1": {
                            "metric1{label1='a',label2='a'}": [[1660000000, 1], [1660000015, 1]],
                            "metric1{label1='a',label2='b'}": [[1660000000, 1], [1660000015, 3], [1660000030, 3]]
                        }
                    },
                    "id2": None
                }
            time_range: time_range: time range of this diagnose, only error happened in time range
                will be recorded

        Returns:
            dict, e.g. {
                    "host1": ["metric1", "metric2"]
                }
        """
        result = {}
        for host_id, metrics in data.items():
            if metrics is None or detail.get(host_id) is None:
                continue

            model_id = detail[host_id]
            model: Algorithm = self.model.get(model_id)
            result[host_id] = model.calculate(metrics, time_range)

        return result

    @staticmethod
    def format_result(check_result: Dict[str, List[int]]) -> Dict[str, List[Dict[str, str]]]:
        """
        Args:
            check_result

        Returns:
            dict, e.g.
            {
                "host1": [{
                            "metric_name": "",
                            "metric_label": "",
                            "is_root": False
                        }]
            }
        """
        result = defaultdict(list)
        for host_id, value in check_result.items():
            if value:
                result[host_id].append({"metric_name": "", "metric_label": "", "is_root": False})
        return result

    def execute(
        self,
        model_info: Dict[str, Dict[str, str]],
        detail: dict,
        data: dict,
        time_range: list,
        default_mode: bool = False,
    ) -> dict:
        """
        Args:
            model_info: it's information about model and algorithm. e.g.
                {
                    "model_id": {
                        "model_name": "",
                        "algo_id": "",
                        "algo_name": ""
                    }
                }
            detail: it's a map between metric and model. e.g.
                {
                    "multicheck": {
                        "host1": "model3",
                        "host2": "model4"
                    }
                }
            data: input original data. e.g.
                {
                    'id1': {
                        "metric1": {
                            "metric1{label1='a',label2='a'}": [[1660000000, 1], [1660000015, 1]],
                            "metric1{label1='a',label2='b'}": [[1660000000, 1], [1660000015, 3]]
                        }
                    },
                    "id2": None
                }
            time_range: time range of this diagnose.  If data is in [1660000000, 1660000900],
                and time_range is [1660000000, 1660000060], then only error happened in time range
                will be recorded
            default_mode: load model from database or local, it's used for
                          configurable mode and default mode correspondingly

        Returns:
            dict, e.g. {
                "host_result": {
                    "host1": [
                        {
                            "metric_name": "",
                            "metric_label": "",
                            "is_root": False
                        }
                    ]
                },
                "alert_name": ""
            }
        """
        if not self.load_models(model_info, default_mode):
            return {}

        check_result = self.do_check(detail['multicheck'], data, time_range)
        if not check_result:
            return {}

        format_result = self.format_result(check_result)
        if not format_result:
            return {}

        result = {"host_result": format_result, "alert_name": "network abnormal"}
        return result
