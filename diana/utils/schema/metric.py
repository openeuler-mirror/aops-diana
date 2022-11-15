# from typing_extensions import Required
from urllib import request
from marshmallow import Schema, fields

class QueryHostMetricNamesSchema(Schema):
    query_ip = fields.String(required=True)

class QueryHostMetricDataSchema(Schema):
    time_range = fields.List(fields.Integer, required=True)
    query_ip= fields.String(required=True)
    query_info = fields.Dict()

class QueryHostMetricListSchema(Schema):
    query_ip = fields.String(required=True)
    metric_names = fields.List(fields.String)