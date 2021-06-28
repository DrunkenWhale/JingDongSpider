import json
import requests
import HtmlFilter
import sqlite3
import random
import threading
import time

# 超进化！ 从当当书单上面拉热点图书再爬京东相关商品信息 (免费代理该嫖还得嫖)
# 当当网好像是静态页面 也没什么对爬虫的限制 但是我真的懒得再写了诶 干脆直接手动复制 可不敢看到这种操作就😅奥
saler_list = ['烟与镜',
              '蛤蟆先生去看心理医生',
              '虫洞书简：给青少年的74封信',
              '少年读史记',
              '文城',
              '乌合之众 : 大众心理研究',
              '你当像鸟飞往你的山',
              '活着',
              '三体：全三册 刘慈欣代表作，亚洲首部“雨果奖”获奖作品！',
              '心安即是归处',
              '云边有个小卖部',
              '非自然死亡：我的法医笔记',
              '别想太多啦：在复杂的世界里，做一个简单的人',
              '趣说中国史：如果把中国422位皇帝放在一个群里，他们会聊些什么？...',
              '消失的13级台阶',
              '人间失格',
              '东野圭吾：白夜行',
              '【樊登推荐】考试脑科学 脑科学中的高效记忆法',
              '人生没什么不可放下：弘一法师的人生智慧',
              '钝感力',
              '狂人日记：鲁迅小说全集',
              '马尔克斯：百年孤独',
              '被讨厌的勇气：“自我启发之父”阿德勒的哲学课',
              '走遍中国 图说天下 寻梦之旅',
              '非暴力沟通',
              '白色橄榄树',
              '小王子',
              '毛泽东选集',
              '人生海海',
              '东野圭吾：解忧杂货店',
              '半小时漫画历史系列',
              '愿你慢慢长大',
              '杀死一只知更鸟',
              '宫西达也超级绘本',
              '尼尔斯骑鹅旅行记',
              '四季时光',
              '万物由来科学绘本 写给孩子的科普绘本',
              '致我独一无二的宝贝',
              '平凡的世界：全三册',
              '那个不为人知的故事',
              '正面管教(修订版)',
              '人生海海',
              '愿你慢慢长大',
              '银火箭少年科幻系列・第1辑',
              '学会管自己幼儿版-歪歪兔自控力教育系列绘本',
              '偷偷藏不住',
              '纯粹理性批判',
              '平凡的世界：全三册',
              '刘擎西方现代思想讲义',
              '马尔克斯：百年孤独',
              '钱穆谈中国历史文化：中国历史精神',
              '边城',
              '万物由来科学绘本 写给孩子的科普绘本',
              '宫西达也“你肯定能行”绘本',
              '月亮与六便士',
              '谈判：如何在博弈中获得更多(第四版)Everything is Negotiable',
              '被讨厌的勇气：“自我启发之父”阿德勒的哲学课',
              '四五快读 第一册 全彩图 升级版',
              '沉默的病人',
              '毛泽东选集']
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

# 代理好贵..不开ip被秒封 妈耶
proxies_list = [{"http": i["ip"] + ":" + i["port"]} for i in requests.get(
    "http://piping.mogumiao.com/proxy/api/get_ip_bs?appKey=ed262816b4914c9fa8c960aa298bc21c&count=10&expiryDate=0&format=1&newLine=2").json()[
    "msg"]]


# 用户代理 蘑菇代理  给的api 处理一下成为一个字典元素的列表 扔到proxies中混一下代理就ok了 多线程爬虫大成功！

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

    res = requests.get(url, headers=headers, proxies=proxies_list[random.randint(0, len(proxies_list) - 1)])
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
    for commodity in saler_list:
        page = 30
        # page, commodity = filter_input()
        conn = sqlite3.connect("db/"+getDatabaseName(commodity) + "CommodityData.db")
        cursor = conn.cursor()
        main()
        write_to_sqlite(conn, cursor)
        contents.clear()  # 不清会一直累加
