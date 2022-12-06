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
from collections import defaultdict


def reformat_queried_data(queried_data: dict) -> dict:
    """
    reformat queried data
    Args:
        queried_data: queried data from data dao.  e.g.
            {
                'id1': {
                    'metric1'{label1="a",label2="a"}':[[time1, 'value1'], [time2, 'value2']],
                    'metric1'{label1="a",label2="b"}':[[time1, 'value1'], [time2, 'value2']],
                    'metric1'{label1="a",label2="c"}':[],
                    'metric2{label1="a"}': [], => get data list is empty
                    'metric2{label1="b"}': None => get no data
                },
                'id2': None => get no metric list of this host
            }

    Returns:
        dict: e.g.
        {
            'id1': {
                "metric1": {
                    "metric1{label1='a',label2='a'}": [[1660000000, 1], [1660000015, 1]],
                    "metric1{label1='a',label2='b'}": [[1660000000, 1], [1660000015, 3]]
                }
            },
            "id2": None
        }
    """
    reformat_data = defaultdict(dict)
    for host_id, data_info in queried_data.items():
        if not data_info:
            reformat_data[host_id] = None
            continue
        for metric_with_label, data_list in data_info.items():
            if not data_list:
                continue
            metric_name = metric_with_label.split("{")[0]
            if metric_name not in reformat_data[host_id]:
                reformat_data[host_id][metric_name] = {}
            reformat_data[host_id][metric_name][metric_with_label] = data_list
    return dict(reformat_data)
