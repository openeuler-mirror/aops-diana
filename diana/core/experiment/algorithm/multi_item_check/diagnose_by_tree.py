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
Description: Diagnose related functions
"""
import json
from typing import Tuple, Dict

from vulcanus.log.log import LOGGER

from diana.core.experiment.algorithm.multi_item_check.diag_tree.tree.diag_tree import DiagTree
from diana.core.experiment.algorithm.multi_item_check.diag_tree.leaves.leaves_manager import LeavesManager
from diana.core.experiment.algorithm.multi_item_check.diag_tree.custom_exception import ParseConfigError
from diana.core.experiment.algorithm.base_algo import BaseMultiItemAlgorithmOne


class Diagnose(BaseMultiItemAlgorithmOne):
    def __init__(self, sample_period=15):
        self.sample_period = sample_period
        self.tree = None
        self.leaves_manager = None

    @property
    def info(self) -> Dict[str, str]:
        data = {
            "algo_name": "diag_tree",
            "field": "multicheck",
            "description": "It's an diagnose tree method based on expert experience.",
            "path": "diana.core.experiment.algorithm.multi_item_check.diagnose_by_tree.Diagnose",
        }
        return data

    def load(self, path: str):
        self.tree, self.leaves_manager = self.parse_config(path)

    @staticmethod
    def parse_config(file_path: str) -> Tuple[DiagTree, LeavesManager]:
        """
        init diagnose tree and check item manager
        Args:
            file_path: diagnose tree's config file path

        Returns:
            tuple: DiagTree(), LeavesManager()
        """
        try:
            with open(file_path, 'r') as diag_tree_file:
                data = json.load(diag_tree_file)
                tree = DiagTree(data["tree"])
                leaves_manager = LeavesManager(data["leaves"])
        except (FileNotFoundError, KeyError) as error:
            LOGGER.error(error)
            LOGGER.error("Parse diagnose tree's config file failed.")
            raise ParseConfigError(error)
        return tree, leaves_manager

    @property
    def input_data(self) -> dict:
        """
        input metrics and their forward time shift
        Returns:
            dict:  e.g.
                {
                    "metric1{'cpu'='1'}": 3600,
                    "metric2": 0
                }
        """
        return self.leaves_manager.all_data_time_shift

    def calculate(self, data: dict, time_range: list) -> bool:
        """
        calculate each node of the tree and judge the host has error or not
        Args:
            data: original data,
                e.g.
                    {
                        "metric1{label1=''}": {
                            "metric1{label1='',label2='a'}": [[1660000000, 1], [1660000015, 1]],
                            "metric1{label1='',label2='b'}": [[1660000000, 1], [1660000015, 3]]
                        },
                        "metric2{label1=''}": {
                            "metric2{label1=''}": [[1660000000, 1], [1660000015, 1], [1660000030, 1]]
                        },
                        "metric3": {
                            "metric3": [[1660000000, 1], [1660000015, 1], [1660000030, 1]]
                        }
                    }
            time_range: time range of the diagnose.  e.g. [1660000015, 1660000030]

        Returns:

        """
        check_result = self.leaves_manager.do_check(data, time_range, self.sample_period)
        self.tree.diagnose(check_result)
        return self.tree.root.value
