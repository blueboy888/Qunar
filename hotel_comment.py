# -*- coding: utf-8 -*-
# @Time    : 2019/9/17 18:32
# @Author  : Esbiya
# @Email   : 18829040039@163.com
# @File    : hotel_comment.py
# @Software: PyCharm

import requests
import time
import re
import execjs
import json
import math
from settings import *


class QnrHotelComment:

    def __init__(self, hotel_seq):
        self.hotel_seq = hotel_seq
        self._process_seq()
        self.headers = {
            "Host": "qant.qunar.com",
            "Referer": "https://hotel.qunar.com/city/{}/dt-{}/?tag={}".format(self.city, self.id, self.city),
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; WOW64; rv:68.0) Gecko/20100101 Firefox/68.0",
            'Cookie': '; '.join([key + '=' + value for key, value in cookies.items()])
        }
        self.api = 'https://qant.qunar.com/anticraw/api/h/{}/detail/rank/v1/page/{}?'
        with open('decrypter.js', 'rb') as f:
            js = f.read().decode()
        self.ctx = execjs.compile(js)
        self.qan = self._encrypt_qan()

    def _process_seq(self):
        if 'city' in self.hotel_seq:
            self.city = self.hotel_seq.split('_')[0] + '_city'
            self.id = self.hotel_seq.split('_')[2]
        else:
            self.city = self.hotel_seq.split('_')[0]
            self.id = self.hotel_seq.split('_')[1]

    def _encrypt_qan(self):
        QN1 = cookies['QN1']
        qan = self.ctx.call('feature', QN1, self.hotel_seq)
        return qan

    def _req_api(self, page: int = 1):
        url = self.api.format(self.hotel_seq, page)
        timestamp = int(time.time() * 1000)
        params = {
            'qan': self.qan,
            'antiCallback': 'antiCallback{}'.format(timestamp),
            'isMainland': 'true',
            '__jscallback': 'jQuery17206552468476502087_1563275234307',
            'rate': 'all',
            'onlyGuru': 'false',
            '_': timestamp + 1,
        }
        res = requests.get(url, params=params, headers=self.headers, cookies=cookies)
        return res.text, params['antiCallback']

    def _decrypt(self, response, antiCallback):
        encrypt_content = re.search(r'{}\("(.*?)"'.format(antiCallback), response).group(1)
        key = re.search(r", '(\d+)'\)", response, re.S).group(1)
        decrypt_json = self.ctx.call('decrypt', encrypt_content, key)
        result = json.loads(decrypt_json)
        if result['errcode'] == 0:
            total_count = result['data']['count']
            if int(total_count) > 0:
                total_page = math.ceil(int(total_count) / 10)
                positive_count = result['data']['ratingStat']['positiveCount']
                neutral_count = result['data']['ratingStat']['neutralCount']
                negative_count = result['data']['ratingStat']['negativeCount']
                return total_page, total_count, positive_count, neutral_count, negative_count, result
            print('该酒店无评论! ')
            return False
        print('Something is wrong! ')
        return False

    def parse(self, result):
        """
        解析获取数据
        :param result:
        :return:
        """
        comments = result['data']['list']
        for comment in comments:
            content = json.loads(comment['content'])
            item = {
                'nickname': comment['nickName'],
                'room_type': content['roomType'],
                'trip_type': content['tripType'],
                'title': content['title'],
                'date': content['checkInDate'],
                'modtime': content['modtime'],
                'score': content['subScores'],
                'content': content['feedContent']
            }
            print(item)

    def run(self):
        """
        Gump, Run!!!
        :return:
        """
        response, timestamp = self._req_api()
        total_page, total_count, positive_count, neutral_count, negative_count, _ = self._decrypt(response, timestamp)
        if total_page:
            print(f'该酒店共有{total_count}条点评, 其中好评{positive_count}条, 中评{neutral_count}条, 差评{negative_count}条')
            for page in range(1, total_page + 1):
                print(f'采集第{page}页')
                resp, timestamp_ = self._req_api(page)
                _, _, _, _, _, result = self._decrypt(resp, timestamp_)
                self.parse(result)


if __name__ == '__main__':
    QnrHotelComment("tianjin_city_4843").run()
