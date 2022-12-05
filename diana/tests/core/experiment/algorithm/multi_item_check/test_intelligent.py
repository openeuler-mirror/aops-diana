import unittest
from collections import defaultdict

import pandas as pd

from diana.core.experiment.algorithm.multi_item_check.intelligent import Intelligent


class IntelligentTestCase(unittest.TestCase):
    def setUp(self) -> None:
        self.algo = Intelligent()
        self.algo.load(r"/home/project/aops/aops-diana/conf/algorithm/ai_template1.json")
        print(self.algo.config)

    def test_somoke(self):
        data = {
            "metric1": {
                "label1": [["1", '2'], ['3', '4'], ['5', '4'], ['7', '5'], ['9', '3'], ['11', '20'], ['13', '22'],
                           ['14', '26']],
                "label2": [["1", '2'], ['3', '4'], ['5', '4'], ['7', '5'], ['9', '3'], ['11', '20'], ['13', '22'],
                           ['14', '26']]
            },
            "metric2": {
                '''metric2{label1="value2"}''': [["1", '2'], ['3', '4'], ['5', '4'], ['7', '5'], ['9', '3'], ['11', '20'], ['13', '22'],
                           ['14', '26'], ['15', '99'], ['16', '100'], ['17', '101'], ['18', '102']]
            }
        }
        res = self.algo.calculate(data)
        print(res)


if __name__ == '__main__':
    unittest.main()
