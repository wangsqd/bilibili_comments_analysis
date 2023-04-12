
import requests
from lxml import etree
import pandas as pd
from wordcloud import WordCloud
import jieba
import datetime


class BarrageSpider:
    def __init__(self, bv):
        # 需要一个bv号，在接下来的代码中进行替换操作
        self.bv = bv
        self.video_name = None
        # 不需要登录的弹幕接口地址 只能爬取部分弹幕
        self.barrage_url = 'https://comment.bilibili.com/{}.xml'
        # 需要登陆的弹幕接口地址 根据日期进行分类 需要循环爬取 最后归总数据
        self.date_url = 'https://api.bilibili.com/x/v2/dm/history?type=1&oid={}&date={}'  # 2021-01-01
        # 点击按钮弹出日历的数据接口，这里我们用来作索引
        self.index_url = 'https://api.bilibili.com/x/v2/dm/history/index?type=1&oid={}&month={}'  # 2021-01
        # 在抓包工具中找的一个简洁的请求，里面有我们需要的oid或者是cid
        self.bv_url = 'https://api.bilibili.com/x/player/pagelist?bvid=' + bv + '&jsonp=jsonp'
        # 视频时间获取
        self.video_url = 'https://www.bilibili.com/video/{}'.format(bv)
        # 不需要登录接口的伪装头
        self.comment = {
            'referer': 'https://www.bilibili.com/',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                          'Chrome/87.0.4280.88 Safari/537.36 Edg/87.0.664.66 '
        }
        # 需要登录的伪装头 因为需要登录 ip代理已经没有意义了 这里就不再使用IP代理
        self.date_headers = {
            "referer": "https://www.bilibili.com/",
            "origin": "https://www.bilibili.com",
            'cookie' : "buvid3=C25DB3D3-141A-F85E-BE6E-69269408A21799096infoc; i-wanna-go-back=-1; _uuid=1584D14D-41FC-1B68-E3910-9CFBBD5BC32498792infoc; buvid4=E18DEA1A-684D-248D-1A7D-BCDC5E4C936700135-022080420-E0glGruAoXIRHfzWp6auIA==; buvid_fp_plain=undefined; DedeUserID=28870342; DedeUserID__ckMd5=2256c64cabcd6865; nostalgia_conf=-1; CURRENT_BLACKGAP=0; b_ut=5; LIVE_BUVID=AUTO8716596935621816; b_nut=100; hit-dyn-v2=1; blackside_state=1; hit-new-style-dyn=0; CURRENT_FNVAL=4048; rpdid=0zbfAI3c3p|15cJspUfp|1R|3w1OVauO; header_theme_version=CLOSE; home_feed_column=5; CURRENT_PID=6430d4f0-cd6b-11ed-a583-895e24eff4ec; CURRENT_QUALITY=80; fingerprint=754eb3f786187f0e1acd7fd4921820c1; buvid_fp=754eb3f786187f0e1acd7fd4921820c1; bp_video_offset_28870342=783546491953217800; SESSDATA=889e8b40,1696830834,c9a05*41; bili_jct=930f1c778a1fd702d87a427c7f91215a; sid=80xvx150; FEED_LIVE_VERSION=V8; PVID=5; b_lsid=D93CAC2E_1877493123B; bsource=search_bing; innersign=1",
            "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
                          "Chrome/87.0.4280.88 Safari/537.36 Edg/87.0.664.66 "
        }

    # 从接口返回的json中获取到我们的cid 注： cid = oid
    def get_cid(self):
        # 定位到数据data中下面的cid
        return requests.get(url=self.bv_url, headers=self.comment).json()['data'][0]['cid']

    def get_video_time(self):
        time_data = requests.get(url=self.video_url, headers=self.comment).text
        video_page = etree.HTML(time_data)
        v_time = video_page.xpath('//div[@class="video-data"]/span[3]/text()')[0].split(' ')[0]
        self.video_name = video_page.xpath('//h1[@class="video-title"]/span/text()')[0]
        return v_time

    # 解析不需要登录的接口 返回类型是xml文件
    def parse_url(self):
        # 获取指定视频的cid/oid
        cid = self.get_cid()
        # 对页面进行伪装请求，这里注意不要转换成text，使用二进制
        response = requests.get(url=self.barrage_url.format(cid), headers=self.comment).content
        # etree解析
        data = etree.HTML(response)
        # 定位到所有的d元素
        barrage_list = data.xpath('//d')
        for barrage in barrage_list:
            # 获取d元素的p属性值
            info = barrage.xpath('./@p')[0].split(',')
            # 获取弹幕内容
            content = barrage.xpath('./text()')[0]
            item = {'出现时间': info[0], '弹幕模式': info[1], '字体大小': info[2], '颜色': info[3], '发送时间': info[4], '弹幕池': info[5],
                    '用户ID': info[6], 'rowID': info[7], '内容': content}
            # 因为这只是一部分弹幕 所以就没有进行持久化存储 没有必要
            print(item)

    # 循环爬取所有弹幕 需要传入month的数据 根据视频发布的日期到现在的所有月份
    def parse_date_url(self, month):
        print('正在爬取{}月份的数据'.format(month))
        # 存放爬到的数据
        result = []
        # 获取视频的oid
        oid = self.get_cid()
        # 获取日期索引
        date_by_month = requests.get(url=self.index_url.format(oid, month), headers=self.date_headers).json().get(
            'data')
        # 根据日期索引循环请求
        if date_by_month:
            for day in date_by_month:
                print('{}月份数据下的{}'.format(month, day))
                # 注意还是二进制文件
                date_page = requests.get(url=self.date_url.format(oid, day), headers=self.date_headers).content
                date_data = etree.HTML(date_page)
                # 解析到到所有的d元素
                barrage_list = date_data.xpath('//d')
                # 循环解析数据
                for barrage in barrage_list:
                    # 获取d元素的p属性值
                    things = barrage.xpath('./@p')[0].split(',')
                    # 获取弹幕内容 并去掉所有空格
                    content = barrage.xpath('./text()')[0].replace(" ", "")
                    item = {'出现时间': things[0], '弹幕模式': things[1], '字体大小': things[2], '颜色': things[3], '发送时间': things[4],
                            '弹幕池': things[5],
                            '用户ID': things[6], 'rowID': things[7], '内容': content}
                    result.append(item)
        # 返回封装好的数据
        return result

    # 根据现在的时间遍历所有的月份信息
    def parse_month(self):
        start_day = datetime.datetime.strptime(self.get_video_time(), '%Y-%m-%d')
        end_day = datetime.date.today()
        months = (end_day.year - start_day.year) * 12 + end_day.month - start_day.month
        m_list = []
        for mon in range(start_day.month - 1, start_day.month + months):
            if (mon % 12 + 1) < 10:
                m_list.append('{}-0{}'.format(start_day.year + mon // 12, mon % 12 + 1))
            else:
                m_list.append('{}-{}'.format(start_day.year + mon // 12, mon % 12 + 1))
        return m_list

    # 舍友指导下的一行代码生成词云 编译器自动格式化了 本质还是一行代码
    def wordCloud(self):
        WordCloud(font_path="C:/Windows/Fonts/simfang.ttf", background_color='white', scale=16).generate(" ".join(
            [c for c in jieba.cut("".join(str((pd.read_csv('{}弹幕池数据集.csv'.format(self.video_name))['内容']).tolist()))) if
             len(c) > 1])).to_file(
            "{}词云.png".format(self.video_name))


if __name__ == '__main__':
    # 输入指定的视频bv号
    bv_id = input('输入视频对应的bv号:')
    # new一个对象
    spider = BarrageSpider(bv_id)
    spider.parse_month()
    # 请求今年1月和去年12月的数据 并合并数据
    word_data = []
    months = spider.parse_month()
    # 循环遍历爬取
    for month in months:
        word = spider.parse_date_url(month)
        word_data.extend(word)
    # 数据格式化处理 并输出csv格式文件
    data = pd.DataFrame(word_data)
    data.drop_duplicates(subset=['rowID'], keep='first')
    # 字符集编码需要为utf-8-sig 不然会乱码
    data.to_csv('{}弹幕池数据集.csv'.format(spider.video_name), index=False, encoding='utf-8-sig')
    # # 生成词云
    spider.wordCloud()

