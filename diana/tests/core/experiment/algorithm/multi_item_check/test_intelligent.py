import unittest

import pandas as pd

from diana.core.experiment.algorithm.multi_item_check.intelligent import Intelligent
from diana.core.experiment.algorithm.preprocess.train import process_raw_data, show_result


class IntelligentTestCase(unittest.TestCase):
    def setUp(self) -> None:
        self.algo = Intelligent()

    def test_smoke(self):
        self.algo.load(r"/home/project/aops/aops-diana/conf/algorithm/ai_template1.json")
        data = {
            "metric1": {
                "label1": [["1", '2'], ['3', '4'], ['5', '4'], ['7', '5'], ['9', '3'], ['11', '20'], ['13', '22'],
                           ['14', '26'], ['15', '26'], ['16', '26'], ['17', '26'], ['18', '26'], ['19', '26'], ['20', '26'],
                           ['21', '26'], ['22', '26'], ['23', '26'], ['24', '26'], ['25', '26'], ['26', '26'], ['27', '26'], ['28', '26'], ['29', '26'], ['30', '26'],
                           ['31', '26'], ['32', '26'], ['33', '26'], ['34', '26'], ['35', '26'],
                           ['36', '26'], ['37', '26'], ['38', '26'], ['39', '26'], ['40', '26'], ['41', '26'], ['42', '26'],
                           ['43', '26'], ['44', '26'], ['45', '26'], ['46', '26'], ['47', '26'], ['48', '26'],
                           ['49', '26'], ['50', '26'], ['51', '26'], ['52', '26'], ['53', '26'], ['54', '26'],
                           ['55', '26'], ['56', '26'], ['57', '26'], ['58', '26'], ['59', '26'], ['60', '26'],
                           ['61', '26'], ['62', '26'], ['63', '26'], ['64', '26'], ['65', '26'], ['66', '26']],
                "label2": [["1", '2'], ['3', '4'], ['5', '4'], ['7', '5'], ['9', '3'], ['11', '20'], ['13', '22'],
                           ['14', '26'], ['15', '26'], ['16', '26'], ['17', '26'], ['18', '26'], ['19', '26'], ['20', '26'],
                           ['21', '26'], ['22', '26'], ['23', '26'], ['24', '26'], ['25', '26'], ['26', '26'], ['27', '26'], ['28', '26'], ['29', '26'], ['30', '26'],
                           ['31', '26'], ['32', '26'], ['33', '26'], ['34', '26'], ['35', '26'],
                           ['36', '26'], ['37', '26'], ['38', '26'], ['39', '26'], ['40', '26'], ['41', '26'], ['42', '26'],
                           ['43', '26'], ['44', '26'], ['45', '26'], ['46', '26'], ['47', '26'], ['48', '26'],
                           ['49', '26'], ['50', '26'], ['51', '26'], ['52', '26'], ['53', '26'], ['54', '26'],
                           ['55', '26'], ['56', '26'], ['57', '26'], ['58', '26'], ['59', '26'], ['60', '26'],
                           ['61', '26'], ['62', '26'], ['63', '26'], ['64', '26'], ['65', '26'], ['66', '26']]
            },
            "metric2": {
                "label1": [["1", '2'], ['3', '4'], ['5', '4'], ['7', '5'], ['9', '3'], ['11', '20'], ['13', '22'],
                           ['14', '26'], ['15', '26'], ['16', '26'], ['17', '26'], ['18', '26'], ['19', '26'],
                           ['20', '26'],
                           ['21', '26'], ['22', '26'], ['23', '26'], ['24', '26'], ['25', '26'], ['26', '26'],
                           ['27', '26'], ['28', '26'], ['29', '26'], ['30', '26'],
                           ['31', '26'], ['32', '26'], ['33', '26'], ['34', '26'], ['35', '26'],
                           ['36', '26'], ['37', '26'], ['38', '26'],
                           ['39', '26'], ['40', '26'], ['41', '26'],
                           ['43', '26'], ['44', '26'], ['45', '26'], ['46', '26'], ['47', '26'], ['48', '26'],
                           ['49', '26'], ['50', '26'], ['51', '26'], ['52', '26'], ['53', '26'], ['54', '26'],
                           ['55', '26'], ['56', '26'], ['57', '26'], ['58', '26'], ['59', '26'], ['60', '26'],
                           ['61', '26'], ['62', '26'], ['63', '26'], ['64', '26'], ['65', '26'], ['66', '26']]}
        }
        res = self.algo.calculate(data, [1, 2])
        print(res)

    def test_csv_smoke(self, train=True, test=True):
        raw_data = pd.read_csv(r'/home/project/aops/aops-diana/data/mysql.csv')
        self.algo.load(r'/home/project/aops/aops-diana/conf/algorithm/mysql_intelligent.json')
        data, truth = process_raw_data(raw_data, self.algo.config['metric_list'])
        if train:
            self.algo.train(data, '/home/project/aops/aops-diana/conf/tmp', 'mysql_intelligent_train.json')
            print("training done")
        if test:
            print("start testing")
            self.algo.load(r'/home/project/aops/aops-diana/conf/tmp/mysql_intelligent_train.json')
            result, labels = self.algo.test(data, truth)
            show_result(result, labels)


if __name__ == '__main__':
    unittest.main()
