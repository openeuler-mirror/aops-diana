import unittest
from collections import defaultdict

import pandas as pd

from diana.core.experiment.algorithm.multi_item_check.intelligent import Intelligent


class IntelligentTestCase(unittest.TestCase):
    def setUp(self) -> None:
        self.algo = Intelligent()
        self.algo.load(r"D:\lostway\debugtheworld\diana-debug\aops-diana\conf\algorithm\test.json")
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
                "label1": [["1", '2'], ['3', '4'], ['5', '4'], ['7', '5'], ['9', '3'], ['11', '20'], ['13', '22'],
                           ['14', '26'], ['15', '99'], ['16', '100'], ['17', '101'], ['18', '102']]
            }
        }
        res = self.algo.calculate(data)
        print(res)

    def test_csv_smoke(self):
        self.algo.load(r"D:\lostway\debugtheworld\diana-debug\aops-diana\conf\algorithm\test1.json")
        df = pd.read_csv(r'D:\lostway\debugtheworld\diana-debug\data\data.csv')

        # get_ground_truth
        print(df.shape)
        timestamp = df['timestamp']
        label = df['is_anomaly']
        data = df[df.columns[3:-3]]
        data['time_index'] = pd.to_datetime(timestamp, unit='s')
        data.set_index('time_index', inplace=True)
        print(data.shape)
        group_by_metric_name_data = defaultdict(dict)
        for column in data.columns:
            tmp = column.split('{')
            # print(tmp)
            metric_name = tmp[0]
            metric_label = '{' + tmp[1]
            group_by_metric_name_data[metric_name][metric_label] = data[column]

        print(group_by_metric_name_data.keys())
        print(group_by_metric_name_data['11'])
        length = df.shape[0]
        print(length)
        cursor = 0
        window = 100
        step = 20
        result = []
        while cursor + window < length:
            result.append([])
            for metric_name, metric_info in self.algo.config['metric_list'].items():
                if group_by_metric_name_data[metric_name] is None:
                    result[-1].append(0)
                    continue
                tmp_data = {}
                for label, value in group_by_metric_name_data[metric_name].items():
                    tmp_data[label] = value[cursor:cursor+window]
                    # print(tmp_data[label])
                    # return
                tmp_res = self.algo.run(metric_info, tmp_data)
                result[-1].append(tmp_res[-1])

            cursor = cursor + step

        print(result)
        print(len(result))


if __name__ == '__main__':
    unittest.main()
