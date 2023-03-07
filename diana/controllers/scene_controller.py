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
from vulcanus.restful.response import BaseResponse
from vulcanus.restful.resp.state import SUCCEED

from diana.core.experiment.algorithm.scene_identify.package_weight import PackageWeightIdentify
from diana.utils.schema.scene import IdentifySceneSchema


class RecognizeScene(BaseResponse):

    @BaseResponse.handle(schema=IdentifySceneSchema)
    def post(self, **params):
        """
        call scene identification algorithm to identify a host's scene
        identify scene and recommend collect items
        Args:
            args: host info. e.g.
                {
                    "applications": ["nginx"],
                    "collect_items": {
                        "gala-gopher": [
                            {
                                "probe_name": "probe1",
                                "probe_status": "on",
                                "support_auto": True
                            }
                        ]
                    }
                }
        """
        result = dict()
        applications = params["applications"]
        collect_items = params["collect_items"]
        identify_algo = PackageWeightIdentify(applications, collect_items)
        scene, reco_collect_items = identify_algo.get_scene()
        result["scene_name"] = scene
        result["collect_items"] = reco_collect_items
        return self.response(code=SUCCEED, data=result)
