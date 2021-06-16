import json
import requests
import HtmlFilter
import sqlite3
import random
import threading
import time

contents = []
# 最终结果 因为sqlite的connection和cursor必须在同一个线程内 所以必须统一写入
user_agent = [
    "Mozilla/5.0 (compatible; MSIE 9.0; Windows NT 6.1; Win64; x64; Trident/5.0; .NET CLR 3.5.30729; .NET CLR 3.0.30729; .NET CLR 2.0.50727; Media Center PC 6.0)",

    "Mozilla/5.0 (compatible; MSIE 8.0; Windows NT 6.0; Trident/4.0; WOW64; Trident/4.0; SLCC2; .NET CLR 2.0.50727; .NET CLR 3.5.30729; .NET CLR 3.0.30729; .NET CLR 1.0.3705; .NET CLR 1.1.4322)",

    "Mozilla/4.0 (compatible; MSIE 7.0b; Windows NT 5.2; .NET CLR 1.1.4322; .NET CLR 2.0.50727; InfoPath.2; .NET CLR 3.0.04506.30)",

    "Mozilla/5.0 (Windows; U; Windows NT 5.1; zh-CN) AppleWebKit/523.15 (KHTML, like Gecko, Safari/419.3) Arora/0.3 (Change: 287 c9dfb30)",

    "Mozilla/5.0 (X11; U; Linux; en-US) AppleWebKit/527+ (KHTML, like Gecko, Safari/419.3) Arora/0.6",

    "Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US; rv:1.8.1.2pre) Gecko/20070215 K-Ninja/2.1.1",

    "Mozilla/5.0 (Windows; U; Windows NT 5.1; zh-CN; rv:1.9) Gecko/20080705 Firefox/3.0 Kapiko/3.0",

    "Mozilla/5.0 (X11; Linux i686; U;) Gecko/20070322 Kazehakase/0.4.5"
]
# 这玩意不用多说了吧
proxies_list = [{"http": i["ip"] + ":" + i["port"]} for i in requests.get(
    "http://piping.mogumiao.com/proxy/api/get_ip_bs?appKey=ed262816b4914c9fa8c960aa298bc21c&count=10&expiryDate=0&format=1&newLine=2").json()[
    "msg"]]
# 用户代理 蘑菇代理给的api 处理一下成为一个字典元素的列表 扔到proxies中混一下代理就ok了 多线程爬虫大成功！

def filter_input():  # 过滤输入
    number = input("页数")
    commodity_name = input("商品名称")
    if number.isnumeric():
        return number, commodity_name
    else:
        raise ValueError


# 先从京东上面整点博弈论的阳间数据 放java stream里去试一下水


def getMessage(page, commodity="博弈论"):
    global contents
    url = "https://search.jd.com/Search?keyword=" + commodity + "&enc=utf-8&suggest=2.his.0.0&wq=&pvid" \
                                                                "=4b818fdec33f49daa16be827cdd37ead&page=" + str(page)
    # 英文商品无法爬取 很奇怪 但是不知道为什么 好吧 其实是没有换代理（User-agent) ip已经炸了
    # 越来越奇怪了？ 有的能爬有的不能爬就真滴很离谱 还得看运气 反正User-Agent设置为Mozilla会被拒
    headers = {
        'user-agent': user_agent[random.randint(0, len(user_agent) - 1)]
    }

    res = requests.get(url, headers=headers, proxies=proxies_list[random.randint(0, len(proxies_list)-1)])
    content = HtmlFilter.HtmlFilter(res.text)
    contents += content
    # for i in content:
    #     cursor.execute("INSERT INTO DATAMODEL (ID,PRICE,NAME,SALER) VALUES (?,?,?,?)",
    #                    (primary_key, i["price"], i["book"], i["saler"]))
    #     conn.commit()
    #     primary_key += 1
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
    thread_list = []
    for i in range(int(page)):  # 爬多少页 从1开始
        temp = threading.Thread(target=getMessage, args=[i + 1, commodity])
        temp.start()
        thread_list.append(temp)
        # print(contents)
        # getMessage(i + 1, commodity)
    for i in thread_list:
        i.join()


def write_to_sqlite(conn, cursor):
    primary_key = 1
    for i in contents:
        cursor.execute("INSERT INTO DATAMODEL (ID,PRICE,NAME,SALER) VALUES (?,?,?,?)",
                       (primary_key, i["price"], i["book"], i["saler"]))
        conn.commit()
        primary_key += 1
    conn.close()


def getDatabaseName(name):
    string = requests.get("http://fanyi.youdao.com/translate?&doctype=json&type=AUTO&i=%" + name).text.strip()
    word_after_change = json.loads(string)["translateResult"][0][0]["tgt"].strip().title().replace(" ", "")
    for i in word_after_change:
        if not i.isalpha():
            word_after_change = word_after_change.replace(i, "")
    return word_after_change


if __name__ == "__main__":
    page, commodity = filter_input()
    conn = sqlite3.connect(getDatabaseName(commodity) + "CommodityData.db")
    cursor = conn.cursor()
    main()
    write_to_sqlite(conn, cursor)
