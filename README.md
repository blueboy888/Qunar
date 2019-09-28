# 去哪儿爬虫

该爬虫仅为 js 逆向练手项目, 仅进行到数据获取阶段, 未实现数据存储等后续功能。

文件说明
--------

考虑到对去哪儿网站不好, 将关键 js 代码删除了, 如有需要, 且是正当用途, 可发邮件给我。
* encrypt.js: __m__ 参数加密js
* decrypter.js: 酒店评论解密js
* hotel_list: 酒店列表 API
* hotel_comment: 酒店评论 API
* air_ticket_demo: 机票查询 API

反爬
--------

* 请求头参数加密: cookie 校验
* 表单参数加密: feature 参数: 对请求的浏览器参数进行校验, __m__: cookie 校验
* 返回数据混淆: 接口返回的机票价格是随机偏移的, json数据中有一段js：t1000, 处理一下这段 js 传入获取到的数据, 即返回价格偏移量
* 返回数据加密: json数据经过AES加密

结果展示
--------

* 机票
![image](https://github.com/Esbiya/Qunar/blob/master/view/1.png)
![image](https://github.com/Esbiya/Qunar/blob/master/view/2.png)

* 酒店列表
![image](https://github.com/Esbiya/Qunar/blob/master/view/3.png)

* 酒店评论
![image](https://github.com/Esbiya/Qunar/blob/master/view/4.png)

公告
--------

该项目仅供学习参考, 请勿用作非法用途! 如若涉及侵权, 请联系2995438815@qq.com/18829040039@163.com, 收到必删除! 