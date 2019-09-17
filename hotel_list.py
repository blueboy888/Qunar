# -*- coding: utf-8 -*-
# @Time    : 2019/9/17 18:30
# @Author  : xuzhihai0723
# @Email   : 18829040039@163.com
# @File    : hotel_list.py
# @Software: PyCharm

import requests
import re
import math
import json
import time
import execjs
from bs4 import BeautifulSoup
from urllib.parse import urlencode
from pypinyin import lazy_pinyin
from settings import *


class QnrHotelListSpider:

    def __init__(self):
        self.city = input('城市(如西安)>> ')
        self.from_data = input('入住日期(如2019-09-20)>> ')
        self.to_data = input('离店日期(如2019-09-21)>> ')
        self._process_city()
        self.headers = {
            'Referer': f'https://hotel.qunar.com/city/{self.city}/',
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; WOW64; rv:68.0) Gecko/20100101 Firefox/68.0",
            'Cookie': '; '.join([key + '=' + value for key, value in cookies.items()])
        }
        with open('decrypter.js', 'rb') as f:
            js = f.read().decode()
        self.ctx = execjs.compile(js)

    def _process_city(self):
        """
        将输入的城市名转化为拼音, 其中直辖市格式为: beijing_city
        :return:
        """
        if self.city in special_city_set:
            self.city = ''.join(lazy_pinyin(self.city)) + '_city'
        else:
            self.city = ''.join(lazy_pinyin(self.city))

    def _get_params(self):
        res = requests.get(f'https://hotel.qunar.com/city/{self.city}/')
        bsobj = BeautifulSoup(res.text, 'lxml')
        mixKey = bsobj.select('#eyKxim')[0].get_text()
        filterId = re.search('var filterid = "(.*?)"', res.text, re.S).group(1)

        QN1 = cookies['QN1']
        qan = self.ctx.call('feature', QN1, "", "")
        return mixKey, filterId, qan

    def _req_api(self, mixKey, filterId, qan, page: int = 1):
        """
        请求接口
        :param mixKey:
        :param filterId:
        :param qan:
        :param page:
        :return:
        """
        url = 'https://qant.qunar.com/render/renderAPIList.jsp?'
        timestamp = int(time.time() * 1000)
        params = {
            'attrs': '0FA456A3,L0F4L3C1,ZO1FcGJH,J6TkcChI,HCEm2cI6,08F7hM4i,8dksuR_,YRHLp-jc,pl6clDL0,HFn32cI6,vf_x4Gjt,2XkzJryU,vNfnYBK6,TDoolO-H,pk4QaDyF,x0oSHP6u,z4VVfNJo,5_VrVbqO,VAuXapLv,U1ur4rJN,px3FxFdF,xaSZV4wU,ZZY89LZZ,ZYCXZYHIRU,sYWEvpo,er8Eevr,ha6ozyf,d90e9bb,HGYGeXFY,ownT_WG6,0Ie44fNU,yYdMIL83,MMObDrW4,dDjWmcqr,Y0LTFGFh,6X7_yoo3,8F2RFLSO,U3rHP23d,cGlja1Vw,7b4bfd15,yamiYIN,6bf51de0',
            'showAllCondition': '1',
            'showBrandInfo': '1',
            'showNonPrice': '1',
            'showFullRoom': '1',
            'showPromotion': '1',
            'showTopHotel': '1',
            'useCommend': '1',
            'output': 'json1.1',
            'v': '0.1966561812086547',
            'requestTime': timestamp,
            'mixKey': mixKey,
            'requestor': 'RT_HSLIST',
            'cityurl': self.city,
            'fromDate': self.from_data,
            'toDate': self.to_data,
            'limit': '{},15'.format(page-1),  # 页码, page * 15, 第一页为0
            'filterid': filterId,
            'qan': qan,
            'antiCallback': 'antiCallback{}'.format(timestamp + 10),
            'isMainland': 'true',
            '__jscallback': 'XQScript_45'
        }

        api = url + urlencode(params)

        res = requests.get(api, headers=self.headers)
        return res.text, params['antiCallback']

    def _decrypt(self, response, antiCallback):
        """
        解密
        :param response:
        :param antiCallback:
        :return:
        """
        encrypt_content = re.search(r'{}\("(.*?)"'.format(antiCallback), response).group(1)
        key = re.search(r", '(\d+)'\)", response, re.S).group(1)
        decrypt_json = self.ctx.call('decrypt', encrypt_content, key)
        result = json.loads(decrypt_json)
        return result

    @staticmethod
    def _get_total_page(result):
        """
        获取最大页码
        :param result:
        :return:
        """
        total_num = int(result['queryInfo']['ranges'][0][1])
        total_page = math.ceil(total_num / 15)
        return total_page

    @staticmethod
    def parse(result):
        """
        解析获取酒店信息
        :param result:
        :return:
        """
        hotels = result['hotels']
        for hotel in hotels:
            item = {
                'id': hotel['id'],
                'name': hotel['attrs']['hotelName'],
                'area': hotel['attrs']['HotelArea'],
                'trading_area': hotel['attrs']['tradingArea'],
                'address': hotel['attrs']['hotelAddress'],
                'scale': hotel['attrs']['scale'],
                'status': hotel['os'],
                'star': hotel['attrs']['hotelStars'],
                'price': hotel['price'],
                'comment_score': hotel['attrs']['CommentScore'],
                'comment_count': hotel['attrs']['CommentCount'],
                'has_wifi': hotel['attrs']['WifiAccess'],
                'is_web_free': hotel['attrs']['isWebFree'],
                'park_info': hotel['attrs']['parkInfo']
            }
            print(item)

    def run(self):
        """
        跑起来
        :return:
        """
        mixKey, filterId, qan = self._get_params()
        response, antiCallback = self._req_api(mixKey, filterId, qan)
        result = self._decrypt(response, antiCallback)
        total_page = self._get_total_page(result)
        print(f'共有{total_page}页')
        print('=' * 100)
        print('正在采集第1页')
        self.parse(result)
        for page in range(2, total_page + 1):
            print('=' * 100)
            print(f'正在采集第{page}页')
            response, antiCallback = self._req_api(mixKey, filterId, qan, page)
            result = self._decrypt(response, antiCallback)
            self.parse(result)


if __name__ == '__main__':
    QnrHotelListSpider().run()

