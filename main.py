import json
import requests
import HtmlFilter
import sqlite3
import random
import threading
import time


def filter_input():  # 过滤输入
    number = input("页数")
    commodity_name = input("商品名称")
    if number.isnumeric():
        return number, commodity_name
    else:
        raise ValueError


# 先从京东上面整点博弈论的阳间数据 放java stream里去试一下水


def getMessage(page, commodity="博弈论"):
    global primary_key
    url = "https://search.jd.com/Search?keyword=" + commodity + "&enc=utf-8&suggest=2.his.0.0&wq=&pvid" \
                                                                "=4b818fdec33f49daa16be827cdd37ead&page=" + str(page)
    # 英文商品无法爬取 很奇怪 但是不知道为什么 好吧 其实是没有换代理（User-agent) ip已经炸了
    # 越来越奇怪了？ 有的能爬有的不能爬就真滴很离谱 还得看运气 反正User-Agent设置为Mozilla会被拒
    headers = {
        'user-agent': "Chrome/10"
    }

    res = requests.get(url, headers=headers)
    content = HtmlFilter.HtmlFilter(res.text)
    for i in content:
        cursor.execute("INSERT INTO DATAMODEL (ID,PRICE,NAME,SALER) VALUES (?,?,?,?)",
                       (primary_key, i["price"], i["book"], i["saler"]))
        conn.commit()
        primary_key += 1
    # print(content)


def main():
    # conn = sqlite3.connect(commodity + "CommodityData.db")

    try:
        cursor.execute('''CREATE TABLE DATAMODEL 
        ( ID    INT PRIMARY KEY ,
          PRICE DOUBLE NOT NULL,
          NAME  CHAR(77) NOT NULL,
          SALER CHAR(77) NOT NULL);''')
    except:
        pass
    global contents
    for i in range(int(page)):  # 爬多少页 从1开始
        # temp = threading.Thread(target=getMessage, args=[i + 1, commodity])
        # temp.start()
        # temp.join()
        # print(contents)
        getMessage(i + 1, commodity)
    conn.close()


if __name__ == "__main__":
    page, commodity = filter_input()
    conn = sqlite3.connect(commodity + "CommodityData.db")
    cursor = conn.cursor()
    primary_key = 1
    main()
