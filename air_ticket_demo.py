# -*- coding: utf-8 -*-
# @Time    : 2019/9/17 18:34
# @Author  : Esbiya
# @Email   : 18829040039@163.com
# @File    : air_ticket_demo.py
# @Software: PyCharm

import re
import time
import execjs
import requests
from urllib.parse import urlencode
from selenium import webdriver
from selenium.webdriver.chrome.options import Options


class QnrAirplanTicketSpider:

    def __init__(self):
        self.departure_airport = input('请输入出发地(如长沙)>> \n')
        self.arrival_airport = input('请输入目的地(如西安)>> \n')
        self.departure_time = input('请输入出发日期(如2019-09-20)>> \n')
        self.headers = {
            'accept': 'text/javascript, text/html, application/xml, text/xml, */*',
            'accept-encoding': 'gzip, deflate, br',
            'accept-language': 'zh-CN,zh;q=0.9',
            'content-type': 'application/x-www-form-urlencoded',
            'w': '0',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.80 Safari/537.36',
            'x-requested-with': 'XMLHttpRequest'
        }

    def _make_url(self):
        params = {
            'searchDepartureAirport': self.departure_airport,
            'searchArrivalAirport': self.arrival_airport,
            'searchDepartureTime': self.departure_time,
            'nextNDays': '0',
            'startSearch': 'true',
            'from': 'qunarindex',
            'lowestPrice': 'null'
        }
        url = 'https://flight.qunar.com/site/oneway_list.htm?' + urlencode(params)
        return url

    @staticmethod
    def _get_cookie_pre(url):
        """
        获取加密所需的 cookie 和 pre 参数
        js 中 pre = winidow._pt_
        找了很久没找到 window._pt_ 的生成函数, 源码里也没有, 就直接用浏览器拿了, 一点都不优雅...
        :param url:
        :return:
        """
        # 进入浏览器设置
        options = Options()
        # 设置中文
        options.add_argument('lang=zh_CN.UTF-8')
        options.add_argument('--headless')
        options.add_argument(
            'user-agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/68.0.3440.106 Safari/537.36"'
        )
        browser = webdriver.Chrome(options=options)

        browser.get(url)
        pre = browser.execute_script('return window._pt_')

        """获取cookie"""
        cookie = browser.get_cookies()
        cookie = [item['name'] + "=" + item['value'] for item in cookie]
        cookies = '; '.join(item for item in cookie)
        browser.quit()
        return pre, cookies

    @staticmethod
    def _get__m__(cookie):
        """
        运行 js 加密函数生成headers中的加密参数和 __m__
        :param cookie:
        :return:
        """
        with open('encrypt.js', 'rb') as f:
            js = f.read().decode()
        ctx = execjs.compile(js)
        item = ctx.call('get__m__', cookie)
        return item

    def _req_api(self, item):
        """
        拿到所有加密参数, 请求 api 接口
        :param item:
        :return:
        """
        api = 'https://flight.qunar.com/touch/api/domestic/wbdflightlist?'
        params = {
            'departureCity': self.departure_airport,
            'arrivalCity': self.arrival_airport,
            'departureDate': self.departure_time,
            'ex_track': '',
            '__m__': item['__m__'],
            'st': int(time.time() * 1000),
            'sort': '',
            '_v': '4'
        }
        self.headers.update(item['header'])
        resp = requests.get(api, params=params, headers=self.headers).json()
        return resp

    @staticmethod
    def get_price_offset(result):
        """
        获取价格偏移量
        :return:
        """
        offset_js = result['t1000'].replace('(0||(', '').replace('));', '')
        func_name = re.search(r'function (.*?)\(a\)', offset_js).group(1)
        replace_js = re.findall(r'\]\+.*?;for\((.*)', offset_js)[-1]
        offset_x = re.findall(r'\]\+(.*?);for\(.*', offset_js)[-1].replace('=', '').replace(')', '')
        offset_js = offset_js.replace(replace_js, '); return ' + offset_x + ' }').replace('for(); ', '')
        offset_js = re.sub('!0(.*?):', '', offset_js)
        offset_js = re.sub(r'\(new Image\)(.*?),', ' ', offset_js)
        ctx = execjs.compile(offset_js)
        return ctx.call(func_name, result)

    @staticmethod
    def parse(result, price_offset):
        flights = result['data']['flights']
        for flight in flights:
            binfo = flight['binfo'] if 'binfo' in set(flight.keys()) else flight['binfo1']
            item = {
                'arrAirport': binfo['arrAirport'],
                'depAirport': binfo['depAirport'],
                'arrDate': binfo['arrDate'],
                'arrTime': binfo['arrTime'],
                'depDate': binfo['depDate'],
                'depTime': binfo['depTime'],
                'distance': binfo['distance'],
                'flightTime': binfo['flightTime'],
                'lateTime': binfo['lateTime'],
                'fullName': binfo['fullName'],
                'name': binfo['name'],
                'shortName': binfo['shortName'],
                'mealDesc': binfo['mealDesc'],
                'code': flight['code'],
                'planeFullType': binfo['planeFullType'],
                'stopAirports': binfo['stopAirports'],
                'stopCitys': binfo['stopCitys'],
                'discountStr': flight['discountStr'],
                'minPrice': flight['minPrice'] + price_offset
            }
            print(item)

    def run(self):
        while True:
            url = self._make_url()
            pre, cookie = self._get_cookie_pre(url)
            self.headers.update({
                'pre': pre,
                'cookie': cookie,
                'referer': url
            })
            item = self._get__m__(cookie)
            result = self._req_api(item)
            if result['code'] == 0:
                print('请求成功! ')
                price_offset = self.get_price_offset(result)
                print('价格反爬偏移量: {}'.format(price_offset))
                self.parse(result, price_offset)
                return True
            else:
                print('请求失败, 请检查是否有该机场或者日期格式! ')


if __name__ == '__main__':
    QnrAirplanTicketSpider().run()
