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
import copy
import functools
import json
import os
import pickle
import time
from collections import defaultdict
from typing import Dict, List, Tuple, NoReturn

import numpy as np
import pandas as pd
from adtk.data import validate_series
from adtk.detector import LevelShiftAD, PersistAD, ThresholdAD

from diana.core.experiment.algorithm import Algorithm
from diana.core.experiment.algorithm.preprocess.aggregate import transfer_str_2_series, data_aggregation
from diana.core.experiment.algorithm.preprocess.filter import filtering, adtk_preprocess
from diana.core.experiment.algorithm.preprocess.normalize import normalize


@functools.lru_cache()
def load_model(model_path: str) -> object:
    with open(model_path, "rb") as file_io:
        model = pickle.load(file_io)

    return model


class Intelligent(Algorithm):
    def __init__(self):
        self.config = None

    @property
    def info(self) -> Dict[str, str]:
        data = {
            "algo_name": "Intelligent",
            "field": "multicheck",
            "description": "It's an intelligent method.",
            "path": "diana.core.experiment.algorithm.multi_item_check.intelligent.Intelligent",
        }
        return data

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

    def load(self, path: str):
        try:
            with open(path, 'r') as file_io:
                self.config = json.load(file_io)
        except Exception as error:
            print(error)
            return

    @staticmethod
    def run_adtk(data: pd.Series, model_path: str) -> pd.Series:
        anomaly_detector = load_model(model_path)
        labels = anomaly_detector.detect(data)

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

        result = (
            ((data - up) / (std + 1e-3)).apply(lambda x: max(0, x))
            + ((down - data) / (std + 1e-3)).apply(lambda x: max(0, x))
        ).values.tolist()

        return result

    def _enable_fusion_strategy(
        self, rule_info: dict, temp_result: Dict[str, pd.Series], time_range: List[int]
    ) -> bool:
        concat_result = pd.concat(temp_result.values(), axis=1)
        fusion_strategy = rule_info['fusion_strategy']
        concat_result['total'] = concat_result[0] & True
        if fusion_strategy == 'intersection':
            for column in concat_result.columns:
                concat_result['total'] = concat_result['total'] & concat_result[column]

        time = pd.to_datetime(time_range[1] - 600, unit='s') + pd.to_timedelta('8h')
        index = concat_result.index
        select_index = index[index > time]
        select_result = concat_result.loc[select_index]

        if select_result[select_result['total'] == True].shape[0] > 0:
            return True

        return False

    def _check(self, model_info: dict, preprocessed_data: pd.Series) -> List[bool]:
        check_model_info = model_info['check_model']
        check_model_name = check_model_info['enabled']
        # adtk
        if check_model_name == 'adtk':
            model_path = check_model_info['algorithm_list'][check_model_name]['model_path']
            original_labels = self.run_adtk(preprocessed_data, model_path)
        else:
            param = check_model_info['algorithm_list']['nsigma']['param']
            original_labels = self.run_nsigma(preprocessed_data, param['n'], param['train_length'])
            original_labels = list(map(lambda x: True if x > 0 else False, original_labels))
        return original_labels

    @staticmethod
    def _preprocess(agg_data: pd.Series, model_info: dict) -> pd.Series:
        # adtk need time index
        agg_data.index = pd.to_datetime(agg_data.index.values, unit='s') + pd.to_timedelta('8h')
        preprocess_model_info = model_info['preprocess_model']
        preprocess_model_name = preprocess_model_info['enabled']
        if preprocess_model_name == "adtk":
            strategy_name = preprocess_model_info['algorithm_list'][preprocess_model_name]['algorithm_name']
            param = preprocess_model_info['algorithm_list'][preprocess_model_name]['param']
            preprocessed_data = adtk_preprocess(agg_data, strategy_name, **param)
        # normalize and filter
        elif preprocess_model_name == "normal":
            normalized_data = normalize(agg_data)
            preprocessed_data = filtering(normalized_data)
        # do nothing
        else:
            preprocessed_data = agg_data
        return preprocessed_data

    def _aggregate(self, data: Dict[str, Dict[str, list]], need_transform: bool = True) -> Dict[str, pd.Series]:
        """
        Args:
            data: original data from prometheus or csv. e.g.
                {
                    "metric1":
                        {
                            "metric1label1": [[time1, value1], [time2, value2]],
                            "metric1label2": [],
                            "metric1label3": [[time1, value1], [time2, value2], [time3, value3]]
                        }
                } # from prometheus
                or
                {
                    "metric1":
                        {
                            "metric1label1": pd.Series([value1, value2]),
                            "metric1label2": pd.Series([]),
                            "metric1label3": pd.Series([value1, value2, value3])
                        }
                } # from csv
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
            if need_transform:
                data[metric_name] = transfer_str_2_series(data[metric_name])

            filter_rule = metric_info.get('filter_rule')
            agg_data = data_aggregation(data[metric_name], filter_rule)
            # print(agg_data)
            if len(agg_data) == 0:
                continue
            aggregated_data[metric_name] = agg_data
        return aggregated_data

    def run(self, aggregated_data: Dict[str, pd.Series], time_range: List[int]) -> bool:
        """
        Args:
            aggregated_data, e.g.
            {
                "metric1": pd.Series
                "metric2": pd.Series
            }
            time_range

        Returns:
            bool
        """
        # run preprocess and check model for each rule
        for rule_name, rule_info in self.config['rule'].items():
            related_metrics = rule_info['related_metrics']
            temp_result = {}
            for metric_name, model_info in related_metrics.items():
                agg_data = aggregated_data.get(metric_name)
                if agg_data is None:
                    continue

                # preprocess data
                preprocessed_data = self._preprocess(agg_data, model_info)
                # do check
                original_labels = self._check(model_info, preprocessed_data)
                temp_result[metric_name] = pd.Series(original_labels, index=preprocessed_data.index)

            # no result
            if not temp_result:
                continue

            # enable fusion strategy
            result = self._enable_fusion_strategy(rule_info, temp_result, time_range)
            if result:
                return True

        return False

    def calculate(self, data: Dict[str, Dict[str, list]], time_range: List[int]) -> bool:
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
            time_range

        Returns:
            bool
        """
        if self.config is None:
            return False

        # aggregate data
        aggregated_data = self._aggregate(data)

        # run preprocess and check model for each rule
        return self.run(aggregated_data, time_range)

    @staticmethod
    def __train_adtk(data: pd.Series, algorithm_name: str, file_path, **kwargs):
        def kwargs_formatting(kwargs):
            for key, value in kwargs.items():
                if isinstance(value, list):
                    kwargs[key] = tuple(value)
            return kwargs

        kwargs = kwargs_formatting(kwargs)
        series = validate_series(data)

        if algorithm_name == 'LevelShiftAD':
            anomaly_detector = LevelShiftAD(**kwargs)
            anomaly_detector.fit(series)
        elif algorithm_name == 'PersistAD':
            anomaly_detector = PersistAD(**kwargs)
            anomaly_detector.fit(series)
        elif algorithm_name == 'ThresholdAD':
            anomaly_detector = ThresholdAD(**kwargs)

        with open(file_path, "wb") as file_io:
            pickle.dump(anomaly_detector, file_io)

    @staticmethod
    def __attach_label(truth, labels, step, cursor, window):
        if truth[cursor + window - step : cursor + window].sum() >= 1:
            labels.append(1)
        else:
            labels.append(0)

    def __run_algorithm(self, cursor, window, group_by_metric_name_data, result):
        tmp_data = defaultdict(dict)
        for metric_name, metric_info in self.config['metric_list'].items():
            if group_by_metric_name_data[metric_name] is None:
                continue
            for label, value in group_by_metric_name_data[metric_name].items():
                tmp_data[metric_name][label] = value[cursor : cursor + window]

        agg_data = self._aggregate(tmp_data, False)
        temp = list(agg_data.values())[0]
        end_index = temp.index[-1]
        time_array = time.strptime(str(end_index), "%Y-%m-%d %H:%M:%S")
        timestamp = int(time.mktime(time_array))

        tmp_res = self.run(agg_data, [timestamp - 60, timestamp])
        result.append(1 if tmp_res else 0)

    def train(self, data: Dict[str, Dict[str, pd.Series]], train_config_dir: str, config_name: str) -> NoReturn:
        """
        Train adtk algorithm, all config will be written to train_config_dir
        the global config name is train_config_dir/config_name
        the adtk config name is train_config_dir/{}_{}.format(rule_name, metric_name)

        Args:
            data: raw data read from csv, thus it's not needed to transfer to pd.Series
            train_config_dir: config directory
            config_name
        """
        config = copy.deepcopy(self.config)
        # aggregate data
        aggregated_data = self._aggregate(data, False)

        # run preprocess and check model for each rule
        for rule_name, rule_info in config['rule'].items():
            related_metrics = rule_info['related_metrics']
            for metric_name, model_info in related_metrics.items():
                agg_data = aggregated_data.get(metric_name)
                if agg_data is None:
                    continue

                # preprocess data
                preprocessed_data = self._preprocess(agg_data, model_info)
                # do check
                check_model_info = model_info['check_model']
                check_model_name = check_model_info['enabled']
                # adtk
                if check_model_name == 'adtk':
                    algorithm_name = check_model_info['algorithm_list'][check_model_name]['algorithm_name']
                    param = check_model_info['algorithm_list'][check_model_name]['param']
                    file_path = train_config_dir + '/' + rule_name + '_' + metric_name
                    self.__train_adtk(preprocessed_data, algorithm_name, file_path, **param)
                    check_model_info['algorithm_list'][check_model_name]['model_path'] = file_path
                else:
                    param = check_model_info['algorithm_list']['nsigma']['param']
                    self.run_nsigma(preprocessed_data, param['n'], param['train_length'])

        config_path = os.path.join(train_config_dir, config_name)
        with open(config_path, 'w') as file_io:
            json.dump(config, file_io)

        print("The global config has been written to", config_path)

    def test(
        self, data: Dict[str, Dict[str, pd.Series]], truth: pd.Series, window: int = 100, step: int = 40
    ) -> Tuple[List[int], List[int]]:
        """
        Test the algorithm, split the dataset first

        Args:
            data
            truth
            window: check window
            step: step between every dataset

        Returns:
            list: predict labels
            list: actual labels
        """
        length = truth.shape[0]
        cursor = 0
        result = []
        labels = []

        # generate dataset every step
        while cursor + window < length:
            self.__run_algorithm(cursor, window, data, result)
            # generate labels
            self.__attach_label(truth, labels, step, cursor, window)

            cursor = cursor + step

        print("dataset generated done")
        print("number of sample:")
        print(len(result))
        return result, labels
