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
import pandas as pd
from adtk.data import validate_series
from adtk.transformer import DoubleRollingAggregate


def filtering(series: pd.Series, moving_window: int = 30, min_periods: int = 1) -> pd.Series:
    series.values[:] = abs(series - series.rolling(window=moving_window, min_periods=min_periods).median())

    return series


def adtk_preprocess(series: pd.Series, strategy_name, **kwargs):
    if strategy_name == 'DoubleRollingAggregate':
        preprocessed_series = DoubleRollingAggregate(**kwargs).transform(series)
        return preprocessed_series
    else:
        raise Exception("strategy_name is not 'DoubleRollingAggregate'")
