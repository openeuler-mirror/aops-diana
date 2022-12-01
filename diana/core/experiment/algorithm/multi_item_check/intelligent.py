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
import json
from collections import Counter
from typing import Dict, List

import numpy as np
import pandas as pd
from adtk.data import validate_series
from adtk.detector import LevelShiftAD, PersistAD, SeasonalAD

from diana.core.experiment.algorithm.base_algo import BaseMultiItemAlgorithmTwo
from diana.core.experiment.algorithm.preprocess.aggregate import transfer_str_2_series, data_aggregation
from diana.core.experiment.algorithm.preprocess.filter import filtering
from diana.core.experiment.algorithm.preprocess.normalize import normalize


class Intelligent(BaseMultiItemAlgorithmTwo):
    def __init__(self):
        self.config = None

    @property
    def info(self) -> Dict[str, str]:
        data = {
            "algo_name": "Intelligent",
            "field": "multicheck",
            "description": "It's an intelligent method.",
            "path": "diana.core.experiment.algorithm.multi_item_check.intelligent.Intelligent"
        }
        return data

    def load(self, path: str):
        try:
            with open(path, 'r') as file_io:
                self.config = json.load(file_io)
        except Exception as error:
            print(error)
            return

    @staticmethod
    def vote(data: Dict[str, int]) -> bool:
        weight = Counter(data.values())
        print(weight)
        return weight[1] >= 1
        # return True

    @staticmethod
    def fix_result(original_labels: pd.Series) -> List[int]:
        """
        Args:
            original_labels

        Returns:
            list, e.g. [1, 0, 0, 1]
        """
        label_length = len(original_labels)
        labels = [0] * label_length

        for i in range(1, label_length):
            if original_labels[i - 1] > 0 and original_labels[i] > 0:
                labels[i - 1] = 1
                labels[i] = 1

        return labels

    @staticmethod
    def run_adtk(data: pd.Series, algorithm_name, **kwargs):
        series = validate_series(data)

        if algorithm_name == 'LevelShiftAD':
            anomaly_detector = LevelShiftAD(**kwargs)
        elif algorithm_name == 'SeasonlAD':
            anomaly_detector = SeasonalAD(**kwargs)
        else:
            anomaly_detector = PersistAD(**kwargs)

        labels = anomaly_detector.fit_detect(series)

        return labels

    @staticmethod
    def run_nsigma(data: pd.Series, n: int, train_length: int) -> list:
        """
        overload calculate function
        Args:
            data: single item data with timestamp, like [[1658544527, 100], [1658544527, 100]...]
        Returns:
            list: abnormal data with timestamp, like [1, 2, 3]
        """
        if len(data) > train_length:
            data = data[:train_length]

        std = np.nanstd(data)
        mean = np.nanmean(data)
        up = mean + n * std + 1e-5
        down = mean - n * std - 1e-5

        result = (((data - up) / (std + 1e-3)).apply(lambda x: max(0, x)) +
                  ((down - data) / (std + 1e-3)).apply(lambda x: max(0, x))).values.tolist()

        return result

    def run(self, metric_info: dict, series_list: Dict[str, pd.Series]) -> List[int]:
        """
        Args:
            metric_info
            series_list

        Returns:
            pd.Series
        """
        filter_rule = metric_info.get('filter_rule')
        agg_data = data_aggregation(series_list, filter_rule)
        # print(agg_data)
        if len(agg_data) == 0:
            return [0]
        normalized_data = normalize(agg_data)
        # print(normalized_data)
        filtered_data = filtering(normalized_data)
        # print(filtered_data)
        # load model param
        algo = metric_info['model']['enabled']
        if algo == 'nsigma':
            params = metric_info['model']['algorithm_list']['nsigma']
            original_labels = self.run_nsigma(
                filtered_data, params['n'], params['train_length'])
        # adtk
        else:
            algorithm_name = metric_info['model']['algorithm_list']['adtk']['algorithm_name']
            param = metric_info['model']['algorithm_list']['adtk']['param']
            # adtk need timestemp
            filtered_data.index = pd.to_datetime(filtered_data.index.values, unit='s')
            original_labels = self.run_adtk(
                filtered_data, algorithm_name, **param)
        # print(original_labels)
        fixed_labels = self.fix_result(original_labels)
        # print(fixed_labels)
        return fixed_labels

    def calculate(self, data: Dict[str, Dict[str, list]]) -> bool:
        """
        Args:
            data, original data from prometheus. e.g.
            {
                "metric1": {
                    "label1": [[time1, value1], [time2, value2]],
                    "label11": []
                },
                "metric2": {
                    "label2": [[time1, value1], [time2, value2]]
                }
                "metric3": {}
            }

        Returns:
            bool
        """
        if self.config is None:
            return []

        result = {}

        for metric_name, metric_info in self.config['metric_list'].items():
            if not data.get(metric_name):
                result[metric_name] = 0
                continue
            series_list = transfer_str_2_series(data[metric_name])
            fixed_labels = self.run(metric_info, series_list)
            result[metric_name] = fixed_labels[-1]

        # print(result)
        # apply rule
        vote_res = self.vote(result)
        return vote_res
