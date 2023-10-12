#!/usr/bin/python3
# ******************************************************************************
# Copyright (c) Huawei Technologies Co., Ltd. 2022-2023. All rights reserved.
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

from typing import Tuple, Dict
from diana.core.experiment.algorithm.multi_item_check.diag_tree.leaves.leaf import Leaf


class LeavesManager:
    """
    manager of leaves of diagnose tree

    Attributes:
        all_data_time_shift (dict): all check items' each data's time shift
            e.g.: {
                    "metric1{'cpu'='1'}": 3600,
                    "metric2": 0
                }
        leaves_cache (dict): leaf objects cache. key is leaf's name
    """

    def __init__(self, leaves: list):
        """
        init leaves manager
        Args:
            leaves: leaves list. e.g.
                [{
                    "check_item":"check_item2",
                    "data_list":[
                        {
                            "metric":"node_cpu_frequency_min_hertz{'cpu'='1'}",
                            "type":"kpi",
                            "method": "avg" // when get multiple data with different labels, use average number;
                                        // if method not given, skip calculate
                        },
                        {
                            "metric":"node_cpu_guest_seconds_total{'cpu'='1', 'mode'='nice'}",
                            "type":"kpi",
                            "method": "avg"
                        }
                    ],
                    "condition":"$0 + $1.max(50s) < 10",
                    "description":"bbb"
                }]
        """
        self.all_data_time_shift = defaultdict(int)
        self.leaves_cache = {}
        self.init_leaves(leaves)

    def init_leaves(self, leaves: list):
        """
        init leaves, store leaf object in cache and get all data's time shift
        """
        for leaf_info in leaves:
            leaf_name = leaf_info["check_item"]
            leaf = Leaf(leaf_name, leaf_info["data_list"], leaf_info["condition"], leaf_info["description"])
            self.leaves_cache[leaf_name] = leaf

            for metric_info in leaf.data_list:
                metric_name = metric_info["metric"]
                self.all_data_time_shift[metric_name] = max(self.all_data_time_shift[metric_name], leaf.time_shift)

    def do_check(self, data: dict, time_range: list, sample_period: int) -> Tuple[Dict[str, set], Dict[str, list]]:
        """
        do all leaves' check
        Args:
            data: original data.
                e.g. {
                        "metric1{label1=''}": {
                            "metric1{label1='',label2='a'}": [[1660000000, 1], [1660000015, 1]],
                            "metric1{label1='',label2='b'}": [[1660000000, 1], [1660000015, 1]]
                        }
                        "metric2{label1=''}": [[1660000000, 1], [1660000015, 1], [1660000030, 1]]
                    }
            time_range: time range of the diagnose.  e.g. [1660000015, 1660000030]
            sample_period: sample period of data.  e.g. 15(second)
        Returns:
            dict: check result.  e.g.
                {
                    "abnormal": abnormal_set,
                    "no data": no_data_set,
                    "internal error": internal_error_set
                }
            dict: metric list of abnormal leaves. e.g {"leaf_name": ["metric1", "metric2"]}

        """
        result = {"abnormal": set(), "no data": set(), "internal error": set()}
        abnormal_leaf_metric = {}
        for leaf in self.leaves_cache.values():
            leaf_data = leaf.get_required_data(data, time_range, sample_period)
            leaf_res = leaf.do_check(leaf_data, time_range)
            if leaf_res == 0:
                continue
            if leaf_res == -1:
                result["no data"].add(leaf.name)
            elif leaf_res == 1:
                result["abnormal"].add(leaf.name)
                metric_list = []
                for metric_info in leaf.data_list:
                    metric_list.append(metric_info["metric"])
                abnormal_leaf_metric[leaf.name] = metric_list
            elif leaf_res == 2:
                result["internal error"].add(leaf.name)
            else:
                result["internal error"].add(leaf.name)

        return result, abnormal_leaf_metric
