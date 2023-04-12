import csv
import time

import requests
from bs4 import BeautifulSoup
url = "https://api.bilibili.com/x/v1/dm/list.so?oid=373478551"

csv_headers = ['弹幕内容','发送位置','发送时间','弹幕类型','弹幕字体大小','发送者id']

headers = {
    'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:39.0) Gecko/20100101 Firefox/39.0',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
    'Accept-Language': 'en-US,en;q=0.5',
    'Accept-Encoding': 'gzip, deflate',
    'Connection': 'close'
}
def get_page(url):
    # threadLock.acquire()
    # start_request = True
    NETWORK_STATUS = True
    response = requests.get(url,headers=headers,verify=True,timeout=20)
    # threadLock.release()
    if response.status_code == 200:
        # start_request = False
        return response.content
    else:
        print('error')

def parse_page(html):
    soup = BeautifulSoup(html,'lxml')
    ds = soup.find_all('d')
    # print(len(ds))
    for d in ds:
        rows = []
        text = d.text
        p = str(d['p'])
        attrs = p.split(',')
        time_sec = int(attrs[0].split('.')[0])
        time_int = int(time_sec/60)
        time_float = time_sec%60
        mytime = str(time_int) + '分' + str(time_float) + '秒'
        # print(time)
        if int(attrs[1]) == 4:
            type = "底部弹幕"
        elif int(attrs[1]) == 5:
            type = "顶部弹幕"
        elif int(attrs[1]) == 6:
            type = "逆向弹幕"
        elif int(attrs[1]) == 7:
            type = "精准定位"
        elif int(attrs[1]) == 8:
            type = "高级弹幕"
        else:
            type = "普通弹幕"
        fint_size = attrs[2]
        timeArray = time.localtime(int(attrs[4]))
        date = time.strftime("%Y--%m--%d %H:%M:%S", timeArray)
        id = attrs[6]
        rows.append([text,mytime,date,type,fint_size,id])
        save_to_csv('b站弹幕（BV1Xb4y1k714）.csv',rows)
        print(text + ' ' + mytime + ' ' + date + ' ' + type + ' ' + fint_size + ' ' + id)


def save_to_csv(csv_name,rows):
    # is_exist = False
    # if os.path.exists(csv_name):
    #     is_exist = True
    with open(csv_name, 'a',encoding='utf-8',newline='')as f:
        # if is_exist is False:
        #     f_csv = csv.writer(f)
        #     f_csv.writerow(csv_headers)
        f_csv = csv.writer(f)
        f_csv.writerows(rows)

def main():
    html = get_page(url)
    # print(html)
    parse_page(html)

if __name__ == '__main__':
    with open('b站弹幕（BV1Xb4y1k714）.csv', 'a',encoding='utf-8-sig',newline='')as f:
        # if is_exist is False:
        #     f_csv = csv.writer(f)
        #     f_csv.writerow(csv_headers)
        f_csv = csv.writer(f)
        f_csv.writerow(csv_headers)
    main()