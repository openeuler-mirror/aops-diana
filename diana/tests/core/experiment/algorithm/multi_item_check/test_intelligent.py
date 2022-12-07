import unittest
from collections import defaultdict

import pandas as pd
from sklearn.metrics import classification_report

from diana.core.experiment.algorithm.multi_item_check.intelligent import Intelligent
from diana.core.experiment.algorithm.preprocess.aggregate import transfer_str_2_series, data_aggregation

class Test:
    def __init__(self, config_path):
        self.algo = Intelligent()
        self.algo.load(config_path)
        print(self.algo.config)

    @staticmethod
    def read_data(path):
        return pd.read_csv(path, low_memory=False)

    def run(self, df):
        group_by_metric_name_data, truth = self.process_raw_data(df)

        length = df.shape[0]
        cursor = 0
        window = 100
        step = 10
        result = []
        labels = []

        # generate dataset every step
        while cursor + window < length:
            self.run_algorithm(
                cursor, window, group_by_metric_name_data, result)
            # generate labels
            self.attach_label(truth, labels, step, cursor, window)

            cursor = cursor + step

        print("dataset generated done")
        # print(result)
        print("number of sample:")
        print(len(result))
        # print(labels)
        self.show_result(result, labels)

    @staticmethod
    def predict_result(result):
        predict = []
        for oneset in result:
            if sum(oneset) > 0:
                predict.append(1)
            else:
                predict.append(0)
        return predict

    @staticmethod
    def attach_label(truth, labels, step, cursor, window):
        if truth[cursor + window - step:cursor + window].sum() >= 1:
            labels.append(1)
        else:
            labels.append(0)

    def run_algorithm(self, cursor, window, group_by_metric_name_data, result):
        tmp_data = defaultdict(dict)
        for metric_name, metric_info in self.algo.config['metric_list'].items():
            if group_by_metric_name_data[metric_name] is None:
                continue
            for label, value in group_by_metric_name_data[metric_name].items():
                tmp_data[metric_name][label] = value[cursor:cursor + window]
                # print(tmp_data[label])
                # return
        
        agg_data = self.tmp_aggregate(tmp_data, self.algo.config)
        # TODO
        # time range to be used
        tmp_res = self.algo.run(agg_data, [1,2])
        result.append(1 if tmp_res else 0)

    def process_raw_data(self, df):
        # get_ground_truth
        print(df.shape)
        df['time_index'] = pd.to_datetime(df['timestamp'], unit='s')
        df.set_index('time_index', inplace=True)
        print(df.shape)
        data = df[df.columns[3:-3]]
        truth = df['is_anomaly']
        # transfer csv to prometheus
        group_by_metric_name_data = defaultdict(dict)
        for column in data.columns:
            tmp = column.split('{')
            # print(tmp)
            metric_name = tmp[0]
            if metric_name not in self.algo.config['metric_list']:
                continue
            group_by_metric_name_data[metric_name][column] = data[column]

        print(group_by_metric_name_data.keys())

        return group_by_metric_name_data, truth

    @staticmethod
    def show_result(predict, groundtruth):
        print(classification_report(groundtruth, predict))
    
    # for csv test
    @staticmethod
    def tmp_aggregate(data, config):
        aggregated_data = {}
        for metric_name, metric_info in config['metric_list'].items():
            if not data.get(metric_name):
                continue

            filter_rule = metric_info.get('filter_rule')
            agg_data = data_aggregation(data[metric_name], filter_rule)
            # print(agg_data)
            if len(agg_data) == 0:
                continue
            aggregated_data[metric_name] = agg_data
        return aggregated_data

class IntelligentTestCase(unittest.TestCase):
    def setUp(self) -> None:
        self.algo = Intelligent()
        self.algo.load(r"/home/project/aops/aops-diana/conf/algorithm/ai_template1.json")

    def test_smoke(self):
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

    def test_csv_smoke(self):
        config_path = r'/home/project/aops/aops-diana/conf/algorithm/tpcc_intelligent.json'
        test = Test(config_path)
        raw_data = test.read_data(r'/home/project/aops/aops-diana/data/tpcc.csv')
        test.run(raw_data)


if __name__ == '__main__':
    unittest.main()
