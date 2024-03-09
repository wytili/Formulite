import base64
import hashlib
import json
import random
import requests
import string
import time

from tencentcloud.common import credential
from tencentcloud.common.exception.tencent_cloud_sdk_exception import TencentCloudSDKException
from tencentcloud.common.profile.client_profile import ClientProfile
from tencentcloud.common.profile.http_profile import HttpProfile
from tencentcloud.ocr.v20181119 import ocr_client, models as tencent_models

from alibabacloud_ocr_api20210707.client import Client as OcrClient
from alibabacloud_tea_openapi import models as open_api_models
from alibabacloud_ocr_api20210707 import models as ocr_models
from alibabacloud_tea_util import models as util_models


class RecognitionService:
    def recognizeFormula(self, image_data):
        raise NotImplementedError


class SimpleTex(RecognitionService):
    def __init__(self, id, key):
        self.app_id = id
        self.app_secret = key
        self.api_url = "https://server.simpletex.cn/api/latex_ocr"

    @staticmethod
    def generateRandomStr(length=16):
        return ''.join(random.choice(string.ascii_letters + string.digits) for _ in range(length))

    def generateSign(self):
        random_str = self.generateRandomStr()
        timestamp = str(int(time.time()))
        sign_str = f"app-id={self.app_id}&random-str={random_str}&timestamp={timestamp}&secret={self.app_secret}"
        sign = hashlib.md5(sign_str.encode('utf-8')).hexdigest()
        return random_str, timestamp, sign

    def recognizeFormula(self, image_data):
        random_str, timestamp, sign = self.generateSign()
        headers = {"app-id": self.app_id, "random-str": random_str, "timestamp": timestamp, "sign": sign}

        if isinstance(image_data, str):
            files = {"file": (image_data, open(image_data, "rb"), "image/png")}
        elif isinstance(image_data, bytes):
            files = {"file": ("image.png", image_data, "image/png")}
        else:
            raise ValueError("Unsupported image data type")

        response = requests.post(self.api_url, files=files, headers=headers)
        if response.status_code == 200:
            result = response.json()
            if result.get("status"):
                return {"status": True, "result": [result["res"].get("latex", "")]}
            else:
                return {"status": False, "message": result.get("message", "Unknown error")}
        else:
            return {"status": False, "message": f"HTTP Request Failed with status code {response.status_code}"}


class Tencent(RecognitionService):
    def __init__(self, id, key):
        self.secret_id = id
        self.secret_key = key

    def recognizeFormula(self, image_data):
        try:
            cred = credential.Credential(self.secret_id, self.secret_key)
            httpProfile = HttpProfile()
            httpProfile.endpoint = "ocr.tencentcloudapi.com"
            clientProfile = ClientProfile()
            clientProfile.httpProfile = httpProfile
            client = ocr_client.OcrClient(cred, "ap-beijing", clientProfile)
            if isinstance(image_data, str):
                with open(image_data, 'rb') as f:
                    image_bytes = f.read()
            elif isinstance(image_data, bytes):
                image_bytes = image_data
            else:
                raise ValueError("Unsupported image data type")
            image_base64 = base64.b64encode(image_bytes).decode()
            req = tencent_models.FormulaOCRRequest()
            req.ImageBase64 = image_base64
            resp = client.FormulaOCR(req)
            latex = json.loads(resp.to_json_string())
            return {"status": True, "result": latex['FormulaInfos']}
        except TencentCloudSDKException as err:
            return {"status": False, "message": str(err)}


class AliYun(RecognitionService):
    def __init__(self, id, key):
        super().__init__()
        self.access_key_id = id
        self.access_key_secret = key

    def createClient(self):
        config = open_api_models.Config(access_key_id=self.access_key_id, access_key_secret=self.access_key_secret)
        config.endpoint = 'ocr-api.cn-hangzhou.aliyuncs.com'
        return OcrClient(config)

    def recognizeFormula(self, image_data):
        client = self.createClient()
        recognize_request = ocr_models.RecognizeEduFormulaRequest()
        if isinstance(image_data, str):
            with open(image_data, 'rb') as f:
                content = f.read()
        elif isinstance(image_data, bytes):
            content = image_data
        else:
            raise ValueError("Unsupported image data type")

        recognize_request.body = content
        runtime = util_models.RuntimeOptions()
        try:
            response = client.recognize_edu_formula_with_options(recognize_request, runtime)
            response_dict = response.to_map()
            if response_dict['statusCode'] == 200:
                data_json = response_dict['body']['Data']
                data = json.loads(data_json)
                formula_content = data.get('content', 'No content found')
                return {"status": True, "result": [formula_content]}
            else:
                return {"status": False, "message": "HTTP response code: " + str(response_dict['statusCode'])}
        except Exception as e:
            return {"status": False, "message": str(e)}


class OCRClient:
    def __init__(self, service, **kwargs):
        self.client = self._get_client_instance(service, **kwargs)

    def _get_client_instance(self, service, **kwargs):
        if service == 'API.SIMPLETEX':
            return SimpleTex(**kwargs)
        elif service == 'API.TENCENTCLOUD':
            return Tencent(**kwargs)
        elif service == 'API.ALIYUN':
            return AliYun(**kwargs)
        else:
            raise ValueError("Unsupported service")

    def recognizeText(self, image_data):
        result = self.client.recognizeFormula(image_data)

        if result['status']:
            return {"status": True, "results": result['result']}
        else:
            return {"status": False, "message": result['message']}

