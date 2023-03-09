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
from typing import NoReturn

from flask import Flask, g
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm.scoping import scoped_session
from flask_apscheduler import APScheduler
from diana import BLUE_POINT
from diana.conf import configuration
from diana.init import init
from diana.mode import mode
from diana.mode.scheduler import Scheduler
from diana.core.check.check_scheduler.check_scheduler import check_scheduler
from diana.database import ENGINE


@mode.register('configurable')
class ConfigurableScheduler(Scheduler):
    """
    It's a configurable scheduler which needs to configure workflow and app, then start check.
    """

    @property
    def name(self) -> str:
        return "configurable"

    @staticmethod
    def run() -> NoReturn:
        """
        Init elasticsearch and run a flask app.
        """

        app = Flask(__name__)

        @app.before_request
        def create_dbsession():
            g.session = scoped_session(sessionmaker(bind=ENGINE))

        @app.teardown_request
        def remove_dbsession(response):
            g.session.remove()
            return response

        @app.before_first_request
        def init_service():
            g.session = scoped_session(sessionmaker(bind=ENGINE))
            init()
            check_scheduler.start_all_workflow(app)

        apscheduler = APScheduler()
        apscheduler.init_app(app)
        apscheduler.start()

        for blue, api in BLUE_POINT:
            api.init_app(app)
            app.register_blueprint(blue)

        ip = configuration.diana.get('IP')
        port = configuration.diana.get('PORT')
        app.run(port=port, host=ip)
