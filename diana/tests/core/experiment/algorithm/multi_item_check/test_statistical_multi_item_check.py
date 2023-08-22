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
import unittest

from diana.core.experiment.algorithm.multi_item_check.statistical_multi_item_check import StatisticalCheck


class TestStatisticalMultiItemCheckTestCase(unittest.TestCase):
    """
    test statistical multi-item check algo
    """
    def test_calculate_should_return_true_when_error_rate_acceptable(self):
        algorithm = StatisticalCheck(1)
        data = [{"metric_name": "scrape_duration_seconds", "metric_label": {}},
                {"metric_name": "scrape_samples_scraped", "metric_label": {}}]
        res = algorithm.calculate(data)
        self.assertEqual(res, False)

    def test_calculate_should_return_false_when_error_rate_unacceptable(self):
        algorithm = StatisticalCheck(0.5)
        data = [{"metric_name": "scrape_duration_seconds", "metric_label": {}},
                {"metric_name": "scrape_samples_scraped", "metric_label": {}}]
        res = algorithm.calculate(data)
        self.assertEqual(res, True)
