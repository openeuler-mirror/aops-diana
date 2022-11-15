from flask import jsonify
from vulcanus.restful.response import BaseResponse
from diana.database.dao.data_dao import DataDao
from diana.utils.schema.metric import QueryHostMetricDataSchema, QueryHostMetricListSchema, QueryHostMetricNamesSchema
from diana.conf import configuration


class QueryHostMetricNames(BaseResponse):
    def get(self):
        return jsonify(self.handle_request_db(QueryHostMetricNamesSchema,
                                              DataDao(configuration),
                                              'query_metric_names',
                                              ))


class QueryHostMetricData(BaseResponse):
    def post(self):
        return jsonify(self.handle_request_db(QueryHostMetricDataSchema,
                                              DataDao(configuration),
                                              'query_metric_data',
                                              ))


class QueryHostMetricList(BaseResponse):
    def post(self):
        return jsonify(self.handle_request_db(QueryHostMetricListSchema,
                                              DataDao(configuration),
                                              'query_metric_list',
                                              ))