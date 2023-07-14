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
from typing import List, Dict, Literal

import pandas as pd


def transfer_str_2_series(data: Dict[str, List]) -> Dict[str, pd.Series]:
    """
    Args:
        data: original data from prometheus. e.g.
                {
                    "label1": [[time1, value1], [time2, value2]],
                    "label2": [],
                    "label3": [[time1, value1], [time2, value2], [time3, value3]]
                }
    Returns:
        dict: e.g.
            {
                "label1": pd.Series([value1, value2]),
                "label3": pd.Series([value1, value2, value3])
            }
    """
    result = {}
    for label, value in data.items():
        temp = {}
        index = []
        for point in value:
            index.append(point[0])
            temp[point[0]] = float(point[1])
        # drop the column when it's empty
        if not index:
            continue
        result[label] = pd.Series(data=temp, index=index)

    return result


def data_aggregation(
    data: Dict[str, pd.Series],
    filter_rule: Dict = None,
    fill_method: Literal["backfill", "bfill", "ffill", "pad"] = 'pad',
    fill_value: int = None,
) -> pd.Series:
    """
    Args:
        data: Dict of pd.Series, e.g.
            {
                "label1": pd.Series([value1, value2]),
                "label3": pd.Series([value1, value2, value3])
            }
        filter_rule
        fill_method
        fill_value: it can not be used with fill_method

    Returns:
        pd.Series, e.g.
            1  5.0
            2  7.0
            3  9.0
            4  10.0

    Raises:
        ValueError
    """

    if filter_rule:
        need_pop = []
        for label in data.keys():
            label_mapping = parse_label_info(label)
            for label_name, label_value in filter_rule.items():
                # if one item don't match, just break
                if label_mapping.get(label_name, '') != label_value:
                    need_pop.append(label)
                    break
        for item in need_pop:
            data.pop(item)

    if not data:
        return pd.Series()

    # concat all the column, there maybe some NaN value
    df = pd.concat(data.values(), axis=1)
    # fill the NaN
    df.fillna(value=fill_value, method=fill_method, inplace=True)
    # agg by the axis(1)
    result = df.sum(axis=1)
    return result


def parse_label_info(label_info: str) -> Dict[str, str]:
    index = label_info.find('{')
    labels = label_info[index + 1 : -1].split(',')
    mapping = {}
    for label in labels:
        equal_index = label.find('=')
        label_name = label[:equal_index]
        label_value = label[equal_index + 2 : -1]
        mapping[label_name] = label_value

    return mapping


if __name__ == "__main__":
    data = {
        '''{instance="172.168.128.164:9100",label1="value2"}''': [
            ['1669278600', '2'],
            ['1669278615', '3'],
            ['1669278630', '4'],
        ],
        "l2": [['1669278600', '3'], ['1669278615', '4'], ['1669278630', '5'], ['1669278645', '6']],
        "l3": [],
    }
    series = transfer_str_2_series(data)
    filter_rule = {"label1": "value2"}
    res = data_aggregation(series, filter_rule)
    print(res)
    print(len(res))

    label_info = '''{instance="172.168.128.164:9100",label1="value2"}'''
    parse_label_info(label_info)
