from aip import AipOcr
from CONFIG import *


class OcrClientBaiDu:
    """ 你的 APPID AK SK  图2的内容"""
    APP_ID = '18613535'
    API_KEY = 'wSgRo3qiR9YbML2MMTqRX4fO'
    SECRET_KEY = '1kbGlOhAgpRtqy8Kp0tSiAC3HMWneNGv'

    def __init__(self, app_id=APP_ID, api_key=API_KEY, scret_key=SECRET_KEY, *args, **kwargs):
        self.app_id = app_id
        self.api_key = api_key
        self.scret_key = scret_key
        self.client = AipOcr(self.APP_ID, self.API_KEY, self.SECRET_KEY)

    def get_text_from_image_file(self, file_name):
        """
        识别图片文字内容
        :param file_name:
        :return: {
                "log_id": 2471272194,
                "words_result_num": 2,
                "words_result":
                    [
                        {"words": " TSINGTAO"},
                        {"words": "青島睥酒"}
                    ]
                 }
        """
        with open(file_name, 'rb') as fp:
           rest_result = self.client.basicGeneral(fp.read())
           #  rest_result = self.client.basicAccurate(fp.read())
        if 'error_code' in rest_result:
            """
             接口错误返回信息如下:
             {
              "error_code": 110,
               "error_msg": "Access token invalid or no longer valid"
            }
            """
            raise OcrError('OCR识别接口调用异常')
        return rest_result
