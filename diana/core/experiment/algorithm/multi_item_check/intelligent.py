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
from adtk.detector import LevelShiftAD, PersistAD, ThresholdAD

from diana.core.experiment.algorithm.base_algo import BaseMultiItemAlgorithmTwo
from diana.core.experiment.algorithm.preprocess.aggregate import transfer_str_2_series, data_aggregation
from diana.core.experiment.algorithm.preprocess.filter import filtering, adtk_preprocess
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
    def run_adtk(data: pd.Series, algorithm_name: str, **kwargs):
        def kwargs_formatting(kwargs):
            for key, value in kwargs.items():
                if isinstance(value,list):
                    kwargs[key] = tuple(value)
            return kwargs
        
        kwargs = kwargs_formatting(kwargs)
        series = validate_series(data)

        if algorithm_name == 'LevelShiftAD':
            anomaly_detector = LevelShiftAD(**kwargs)
            labels = anomaly_detector.fit_detect(series)
        elif algorithm_name == 'PersistAD':
            anomaly_detector = PersistAD(**kwargs)
            labels = anomaly_detector.fit_detect(series)
        elif algorithm_name == 'ThresholdAD':
            anomaly_detector = ThresholdAD(**kwargs)
            labels = anomaly_detector.detect(series)
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

    def enable_fusion_strategy(
            self, rule_info: dict, temp_result: Dict[str, pd.Series]) -> bool:
        concat_result = pd.concat(temp_result.values(), axis=1)
        fusion_strategy = rule_info['fusion_strategy']
        concat_result['total'] = concat_result[0] & True
        if fusion_strategy == 'intersection':
            for column in concat_result.columns:
                concat_result['total'] = concat_result['total'] & concat_result[column]
        if concat_result[concat_result['total'] == True].shape[0] > 0:
            return True

        return False

    def check(self, model_info: dict,
              preprocessed_data: pd.Series) -> List[bool]:
        check_model_info = model_info['check_model']
        check_model_name = check_model_info['enabled']
        # adtk
        if check_model_name == 'adtk':
            algorithm_name = check_model_info['algorithm_list'][check_model_name]['algorithm_name']
            param = check_model_info['algorithm_list'][check_model_name]['param']
            # adtk need timestamp
            original_labels = self.run_adtk(
                preprocessed_data, algorithm_name, **param)
        else:
            param = check_model_info['algorithm_list']['nsigma']['param']
            original_labels = self.run_nsigma(
                preprocessed_data, param['n'], param['train_length'])
            original_labels = list(
                map(lambda x: True if x > 0 else False, original_labels))
        return original_labels

    @staticmethod
    def preprocess(agg_data: pd.Series, model_info: dict) -> pd.Series:
        # adtk need time index
        agg_data.index = pd.to_datetime(agg_data.index.values, unit='s')
        preprocess_model_info = model_info['preprocess_model']
        preprocess_model_name = preprocess_model_info['enabled']
        if preprocess_model_name == "adtk":
            strategy_name = preprocess_model_info['algorithm_list'][preprocess_model_name]['algorithm_name']
            param = preprocess_model_info['algorithm_list'][preprocess_model_name]['param']
            preprocessed_data = adtk_preprocess(
                agg_data, strategy_name, **param)
        # normalize and filter
        elif preprocess_model_name == "normal":
            normalized_data = normalize(agg_data)
            preprocessed_data = filtering(normalized_data)
        # do nothing
        else:
            preprocessed_data = agg_data
        return preprocessed_data

    def aggregate(
            self, data: Dict[str, Dict[str, list]]) -> Dict[str, pd.Series]:
        """
        Args:
            data: original data from prometheus. e.g.
                {
                    "metric1":
                        {
                            "metric1label1": [[time1, value1], [time2, value2]],
                            "metric1label2": [],
                            "metric1label3": [[time1, value1], [time2, value2], [time3, value3]]
                        }
        Returns:
            dict: e.g.
                {
                    "metric1": pd.Series([value1, value2])
                }
        """
        aggregated_data = {}
        for metric_name, metric_info in self.config['metric_list'].items():
            if not data.get(metric_name):
                continue
            series_list = transfer_str_2_series(data[metric_name])

            filter_rule = metric_info.get('filter_rule')
            agg_data = data_aggregation(series_list, filter_rule)
            # print(agg_data)
            if len(agg_data) == 0:
                continue
            aggregated_data[metric_name] = agg_data
        return aggregated_data

    def run(self, aggregated_data: Dict[str, Dict[str, list]]) -> bool:
        """
        Args:
            aggregated_data, e.g.
            {
                "metric1": pd.Series
                "metric2": pd.Series
            }

        Returns:
            bool
        """
        # run preprocess and check model for each rule
        for _, rule_info in self.config['rule'].items():
            related_metrics = rule_info['related_metrics']
            temp_result = {}
            for metric_name, model_info in related_metrics.items():
                agg_data = aggregated_data.get(metric_name)
                if agg_data is None:
                    continue

                # preprocess data
                preprocessed_data = self.preprocess(agg_data, model_info)
                # do check
                original_labels = self.check(model_info, preprocessed_data)
                temp_result[metric_name] = pd.Series(
                    original_labels, index=preprocessed_data.index)

            # no result
            if not temp_result:
                continue

            # enable fusion strategy
            result = self.enable_fusion_strategy(rule_info, temp_result)
            if result:
                return True

        return False

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
            return False

        # aggregate data
        aggregated_data = self.aggregate(data)

        # run preprocess and check model for each rule
        return self.run(aggregated_data)
