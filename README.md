# 去哪儿爬虫

该爬虫仅为 js 逆向练手项目, 仅进行到数据获取阶段, 未实现数据存储等后续功能。

文件说明
--------

* encrypt.js: __m__ 参数加密js
* decrypter.js: 酒店评论解密js
* hotel_list: 酒店列表 API
* hotel_comment: 酒店评论 API
* air_ticket_demo: 机票查询 API

反爬
--------

* 请求头参数加密: cookie校验, 破解 js : encrypt.js
* 表单参数加密: feature 参数(破解 js : decrypter.js): 对请求的浏览器参数进行校验, __m__(破解 js : encrypt.js): cookie 校验
* 返回数据混淆: 接口返回的机票价格是随机偏移的, json数据中有一段js：t1000, 处理一下这段 js 传入获取到的数据, 即返回价格偏移量
* 返回数据加密: json数据经过AES加密, 解密 js : decrypter.js

公告
--------

该项目仅供学习参考, 请勿用作非法用途! 如若涉及侵权, 请联系2995438815@qq.com/18829040039@163.com, 收到必删除! 