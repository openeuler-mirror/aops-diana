#!/usr/bin/python3
# ******************************************************************************
# Copyright (c) Huawei Technologies Co., Ltd. 2021-2021. All rights reserved.
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
Description: Manager that start check
"""
from diana.conf import configuration
from diana.errors.startup_error import StartupError
from diana.mode import mode
from diana.mode.configurable_scheduler import ConfigurableScheduler
from diana.mode.default_scheduler import DefaultScheduler
from diana.mode.executor import Executor


def run(mode_name: str):
    try:
        app = mode.build(mode_name)
        app.run()
    except StartupError as error:
        print(error)


def main():
    run(configuration.check.get('MODE'))


if __name__ == "__main__":
    main()
