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
"""
Author: YangYunYi
Date: 2022/12/1 17:10
docs: data_backpack.py
description: data cache of expression
"""
import ast
import unicodedata

from diana.core.experiment.algorithm.multi_item_check.diag_tree.custom_exception import CheckExpressionError


class DataBackpack:
    """
    data cache of expression

    Attributes:
        target_data_name (str): In the case of multiple data items,
                                indicate which item is the primary data item.
        target_index (int): index of target data list
        data_vector (dict): data list

    """

    def __init__(self, target_data_name, target_index, data_vector):
        """
        Constructor
        Args:
            target_data_name (str): In the case of multiple data items,
                                indicate which item is the primary data item.
            target_index (int): index of target data list
            data_vector (dict): data  e.g.
                {
                    "$0": [[1630422080.526, '3207113320'], [1630422095.526, '3207113320'],
                           [1630422110.526, '3207113320']],
                    "$1": [[1630422082.931, '89588736'], [1630422097.931, '89588736'],
                           [1630422112.931, '89588736']]
                }

        Returns:
            None

        """
        self.target_data_name = target_data_name
        self.target_index = target_index
        self.data_vector = data_vector

    def get_key_data_name(self, target):
        """
        Constructor
        Args:
            target (str): In the case of multiple data items,
                                indicate which item is the primary data item.

        Returns:
            data name (str)

        Raises:
            CheckExpressionError

        """
        if target == "default":
            data_name = self.target_data_name
        else:
            data_name = target

        if data_name not in self.data_vector.keys():
            raise CheckExpressionError("Invalid data %s" % data_name)

        return data_name

    def _pre_check(self, index, data_name):
        """
        Pre check when get data from data vector
        Args:
            index (int): index of data
            data_name (str): data name

        Returns:
            True/False (bool)

        """
        if data_name not in self.data_vector.keys():
            return False
        if index < 0 or index >= len(self.data_vector[data_name]):
            return False
        return True

    def get_time_stamp(self, index, data_name):
        """
        Get time stamp of data with index
        Args:
            index (int): index of data
            data_name (str): data name

        Returns:
            time stamp (int)

        Raises:
            CheckExpressionError

        """
        if self._pre_check(index, data_name):
            return self.data_vector[data_name][index][0]
        raise CheckExpressionError("Invalid index %s and data_name %s "
                                   "to find timestamp" % (index, data_name))

    def get_data_value(self, index, data_name):
        """
        Get time stamp of data with index
        Args:
            index (int): index of data
            data_name (str): data name

        Returns:
            data_value

        Raises:
            CheckExpressionError

        """
        if not self._pre_check(index, data_name):
            raise CheckExpressionError("Invalid index %s and data_name %s "
                                       "to find data value" % (index, data_name))

        value = self.data_vector[data_name][index][1]
        if isinstance(value, str) and DataBackpack._is_number(value):
            return ast.literal_eval(value)
        return self.data_vector[data_name][index][1]

    @staticmethod
    def _is_number(string):
        """
        Judge if a str is number
        Args:
            string (str) : the string to be judge

        Returns:
            True/False
        """
        try:
            float(string)
            return True
        except ValueError:
            pass

        try:
            unicodedata.numeric(string)
            return True
        except (TypeError, ValueError):
            pass

        return False
