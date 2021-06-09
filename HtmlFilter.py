from bs4 import BeautifulSoup


def HtmlFilter(res):
    global commodities_list
    final_data_list = []
    price_list = []
    name_list = []
    saler_list = []
    soup = BeautifulSoup(res, 'html.parser')
    commodities_list_div = soup.find(id='J_goodsList')
    try:
        commodities_list = commodities_list_div.find_all(class_="gl-i-wrap")
    except:
        pass
    try:
        for i in commodities_list:
            price_list.append(i.find(class_="p-price").strong.i.string)
            name_list.append(i.find(class_="p-name").a.em.text)
            saler_list.append(i.find(class_='p-shopnum').a.text)
        for i in range(len(price_list)):
            final_data_list.append({"price": price_list[i], "book": name_list[i], "saler": saler_list[i]})
    except:
        pass
    return final_data_list

# print(i,"\n-------------------------------------------------------------\n")
# for i in commodities_list:
#     InitData = i.text.split()
#     print(InitData)
#     if(InitData[0][0]=='￥'):   # 不是广告
#         # InitData.pop(2)
#         # index = InitData.index("|")
#         final_data_list.append([InitData[0],InitData[1],InitData[3],])
#         # print(InitData)

# print(commodities_list_div.find_all(_class='gl-i-wrap'))
# J_goodsList > ul > li:nth-child(1) > div
