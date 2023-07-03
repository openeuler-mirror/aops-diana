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

import pandas as pd
from sklearn.metrics import classification_report


def process_raw_data(df, metric_list):
    # get_ground_truth
    print(df.shape)
    df['time_index'] = pd.to_datetime(df['timestamp'], unit='s')
    df.set_index('time_index', inplace=True)
    data = df[df.columns[3:-3]]
    truth = df['is_anomaly']
    # transfer csv to prometheus
    group_by_metric_name_data = defaultdict(dict)
    for column in data.columns:
        tmp = column.split('{')
        metric_name = tmp[0]
        if metric_name not in metric_list:
            continue
        group_by_metric_name_data[metric_name][column] = data[column]

    print(group_by_metric_name_data.keys())

    return group_by_metric_name_data, truth


def show_result(predict, groundtruth):
    print(classification_report(groundtruth, predict))
