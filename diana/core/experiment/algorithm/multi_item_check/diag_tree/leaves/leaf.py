#!/usr/bin/python3
# ******************************************************************************
# Copyright (c) Huawei Technologies Co., Ltd. 2021-2021. All rights reserved.
# licensed under the Mulan PSL v2.
# You can use this software according to the terms and conditions of the Mulan PSL v2.
# You may obtain a copy of Mulan PSL v2 at:
#     http://license.coscl.org.cn/MulanPSL2
# THIS SOFTWARE IS PROVIDED ON AN 'AS IS' BASIS, WITHOUT WARRANTIES OF ANY KIND, EITHER EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO NON-INFRINGEMENT, MERCHANTABILITY OR FIT FOR A PARTICULAR
# PURPOSE.
# See the Mulan PSL v2 for more details.
# ******************************************************************************/
from typing import List, Dict, Optional
from collections import defaultdict

from diana.core.experiment.algorithm.multi_item_check.diag_tree.custom_exception import CheckError, CheckExpressionError
from diana.core.experiment.algorithm.multi_item_check.diag_tree.leaves import MAIN_DATA_MACRO
from diana.core.experiment.algorithm.multi_item_check.diag_tree.leaves.data_backpack import DataBackpack
from diana.core.experiment.algorithm.multi_item_check.diag_tree.leaves.element import TimeFilter
from diana.core.experiment.algorithm.multi_item_check.diag_tree.leaves.parser import Parser
from vulcanus.preprocessing.alignment import align
from vulcanus.preprocessing.deduplicate import deduplicate


class ShiftVisitor:
    """
    Visitor to get time shift of a check items' metrics.
    For now, only function element need shift time forward, and to make it easy to align data,
    the time shift of metrics in the check item choose the biggest one, even if a metric doesn't need
    to shift time.

    Attributes:
        time_shift (int): get the time shift of the check item
    """

    def __init__(self):
        """
        Constructor
        """
        self.time_shift = 0

    def visit(self, time_filter: TimeFilter):
        """
        visit time filter element and update the time shift
        Args:
            time_filter (time_filter): time filter element

        Returns:
            None
        """
        self.time_shift = max(self.time_shift, time_filter.calculate())


class Calculator:
    """
    Calculator of check item's expression

    Attributes:
        condition (str): check item's condition
        time_shift (dict): each data's time shift seconds.  e.g. {"$0": 3600}
    """

    def __init__(self, condition):
        """
        Constructor

        Args:
            condition: condition
        """
        self.condition = condition
        self._syntax_tree = None
        self.time_shift = 0
        self._analysis_expression()

    def _analysis_expression(self):
        """
        Analysis expression

        Returns:
            None

        """
        expression_parser = Parser()
        visitor = ShiftVisitor()
        self._syntax_tree = expression_parser.parse_string(self.condition)
        self._syntax_tree.traverse(visitor)
        self.time_shift = visitor.time_shift

    def judge_condition(self, main_data_macro: str, index: int, data_vector: dict) -> bool:
        """
        Judge the condition is matched
        Args:
            main_data_macro: main data macro.  e.g. $0
            index: the data item list to be checked
            data_vector: check item

        Returns:
            True-matched;False-unmatched

        Raises:
            CheckItemError
        """
        data_backpack = DataBackpack(main_data_macro, index, data_vector)
        if not self._syntax_tree:
            raise CheckExpressionError("syntax tree is None")
        ret = self._syntax_tree.calculate(data_backpack)
        return ret


class Leaf:
    """
    leaf of diagnose tree
    """

    def __init__(self, name: str, data_list: List[dict], condition: str, description: str):
        """
        Constructor
        Args:
            name: check item's name
            data_list: data list, e.g.
                [
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
                ]
            condition: check item's condition expression
            description: description of the check item

        Raise:
            CheckItemError
        """
        self.name = name
        self.data_list = data_list
        self.condition = condition
        self.description = description
        self.data_name_map = {}
        self.data_type = "kpi"
        self._parse_data_list()
        self._calculator = Calculator(condition)
        self.time_shift = self._calculator.time_shift

    def _parse_data_list(self):
        """
        Parse data list. Add macro attribute
        """
        # $index mean the num index data item in list
        index = 0
        has_log = False
        for data_info in self.data_list:
            data_info["macro"] = "${}".format(index)
            self.data_name_map[data_info["metric"]] = data_info["macro"]
            if data_info.get("type") == "log":
                has_log = True
            index += 1
        self.data_type = "log" if has_log else "kpi"

    def get_required_data(self, all_data: dict, time_range: list, sample_period: int) -> dict:
        """
        get required data items in specific time range from all data.
        Args:
            all_data: all data items.  e.g.
                {
                    "metric1{label1=''}": {
                        "metric1{label1='',label2='a'}": [[1660000000, 1], [1660000015, 1]],
                        "metric1{label1='',label2='b'}": [[1660000000, 1], [1660000015, 3]]
                    }
                    "metric2{label1=''}": {
                        "metric2{label1=''}": [[1660000000, 1], [1660000015, 1], [1660000030, 1]]
                    },
                    "metric3: {
                        "metric3": [[1660000000, 1], [1660000015, 1], [1660000030, 1]]
                    }
                }
            time_range: time range of the diagnose.  e.g. [1660000015, 1660000030]
            sample_period: sample period
        Returns:
            dict: filtered and processed metric data. metrics' data has same length and timestamp
                after aligned, and metric which has multiple labels will extract to one data list by
                assigned method like 'avg'.
                e.g.
                    {
                        "$0": [[1660000000, 1], [1660000015, 2]],
                        "$1": [[1660000000, 1], [1660000015, 1]]
                    }
        """
        tmp_data = {}
        processed_data = {}
        new_time_range = [time_range[0] - self.time_shift, time_range[1]]

        for data_info in self.data_list:
            metric_with_label = data_info["metric"]
            data_macro = self.data_name_map[metric_with_label]
            if metric_with_label not in all_data:
                tmp_data[data_macro] = []
                continue

            # right now only support kpi data.
            merged_data = self._merge_data_list_by_method(all_data[metric_with_label], data_info.get("method"))
            start_index = self.find_start_index(merged_data, time_range[0] - self.time_shift)
            tmp_data[data_macro] = merged_data[start_index:]

        if self.data_type == "kpi":
            processed_data = align(sample_period, new_time_range, tmp_data)
        elif self.data_type == "log":
            processed_data = deduplicate(tmp_data)
        return processed_data

    @staticmethod
    def _merge_data_list_by_method(metric_data: Dict[str, list], method: Optional[str]) -> List[list]:
        """
        merge multiple labels data list into one data list
        Args:
            metric_data: a metric's all labels' data.  e.g.
                {
                    "metric1{label1='',label2='a'}": [[1660000000, 1], [1660000015, 1]],
                    "metric1{label1='',label2='b'}": [[1660000000, 1], [1660000015, 3]]
                }
            method: method to merge data.  for now only support 'avg', 'sum'

        Returns:
            list: e.g. [[1660000000, 1], [1660000015, 2]]
        """
        merged_data = []
        if not method:
            if len(metric_data.keys()) == 1:
                merged_data, = metric_data.values()
            return merged_data

        if method not in ["avg", "sum"]:
            return merged_data

        new_metric_data = defaultdict(list)
        for data_list in metric_data.values():
            for timestamp, value in data_list:
                new_metric_data[timestamp].append(value)
        if method == "avg":
            for timestamp, value in sorted(new_metric_data.items(), key=lambda x: x[0]):
                merged_data.append([timestamp, round(sum(value)/len(value), 3)])
        else:
            for timestamp, value in sorted(new_metric_data.items(), key=lambda x: x[0]):
                merged_data.append([timestamp, sum(value)])
        return merged_data

    @staticmethod
    def find_start_index(data: list, start_time_stamp: int) -> int:
        """
        Get the first data index which time stamp >= the start time stamp
        Args:
            data: one metric's data.  e.g. [[1660000000, 1], [1660000015, 2]]
            start_time_stamp: the target start time stamp

        Return:
            index (int)

        """
        if not data:
            return -1

        left = 0
        right = len(data) - 1
        if data[left][0] >= start_time_stamp:
            return left
        if data[right][0] < start_time_stamp:
            return -1

        while left <= right:
            mid = left + (right - left) // 2
            if data[mid][0] == start_time_stamp:
                return mid
            if data[mid][0] <= start_time_stamp:
                left = mid + 1
            elif data[mid][0] > start_time_stamp:
                right = mid - 1

        ret = -1 if left == len(data) else left
        return ret

    def do_check(self, data: dict, time_range: list) -> int:
        """
        do check
        Args:
            data: original data.  e.g.
                {
                    "$0": [[1660000000, 1], [1660000015, 1]],
                    "$1": [[1660000000, 1], [1660000015, 1]]
                }
            time_range: time range to check.  e.g.
                [1660000000, 1660000030]
        Returns:
            int: check result.
                -1: no data, 0: normal, 1: abnormal, 2: internal error
        """
        start_index = self.find_start_index(data.get(MAIN_DATA_MACRO, None), time_range[0])
        if start_index == -1:
            return -1

        for index in range(start_index, len(data[MAIN_DATA_MACRO])):
            try:
                if not self._calculator.judge_condition(MAIN_DATA_MACRO, index, data):
                    continue
                return 1
            except CheckError:
                return 2
        return 0
