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
from flask_apscheduler import APScheduler

from vulcanus.manage import init_application
from diana.init import init
from diana.mode import mode
from diana.mode.scheduler import Scheduler
from diana.core.check.check_scheduler.check_scheduler import check_scheduler
from diana.conf import configuration
from diana.url import URLS


@mode.register('configurable')
class ConfigurableScheduler(Scheduler):
    """
    It's a configurable scheduler which needs to configure workflow and app, then start check.
    """

    @property
    def name(self) -> str:
        return "configurable"

    @staticmethod
    def run():
        """
        Init elasticsearch and run a flask app.
        """

        app = init_application(name="diana", settings=configuration, register_urls=URLS)

        init()
        apscheduler = APScheduler()
        apscheduler.init_app(app)
        apscheduler.start()

        check_scheduler.start_all_workflow(app)
        return app
