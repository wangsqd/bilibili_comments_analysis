import requests
import re


def get_response(html_url):
    headers = {
        'cookie' : "buvid3=C25DB3D3-141A-F85E-BE6E-69269408A21799096infoc; i-wanna-go-back=-1; _uuid=1584D14D-41FC-1B68-E3910-9CFBBD5BC32498792infoc; buvid4=E18DEA1A-684D-248D-1A7D-BCDC5E4C936700135-022080420-E0glGruAoXIRHfzWp6auIA==; buvid_fp_plain=undefined; DedeUserID=28870342; DedeUserID__ckMd5=2256c64cabcd6865; nostalgia_conf=-1; CURRENT_BLACKGAP=0; b_ut=5; LIVE_BUVID=AUTO8716596935621816; b_nut=100; hit-dyn-v2=1; blackside_state=1; hit-new-style-dyn=0; CURRENT_FNVAL=4048; rpdid=0zbfAI3c3p|15cJspUfp|1R|3w1OVauO; header_theme_version=CLOSE; home_feed_column=5; CURRENT_PID=6430d4f0-cd6b-11ed-a583-895e24eff4ec; CURRENT_QUALITY=80; fingerprint=754eb3f786187f0e1acd7fd4921820c1; buvid_fp=754eb3f786187f0e1acd7fd4921820c1; bp_video_offset_28870342=783546491953217800; SESSDATA=889e8b40,1696830834,c9a05*41; bili_jct=930f1c778a1fd702d87a427c7f91215a; sid=80xvx150; FEED_LIVE_VERSION=V8; PVID=5; b_lsid=D93CAC2E_1877493123B; bsource=search_bing; innersign=1",
        'origin':'https://www.bilibili.com',
        'referer': 'https://www.bilibili.com/video/BV19E41197Kc',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.138 Safari/537.36',
    }
    response = requests.get(url=html_url, headers=headers)
    return response


def get_date(html_url):
    response = get_response(html_url)
    json_data = response.json()
    date = json_data['data']
    print(date)
    return date


def save(content):
    for i in content:
        with open('B站弹幕.xlsx', mode='a', encoding='utf-8') as f:
            f.write(i)
            f.write('\n')
            print(i)


def main(html_url):
    data = get_date(html_url)
    for date in data:
        url = f'https://api.bilibili.com/x/v2/dm/web/history/seg.so?type=1&oid=1047253529&date={date}' #改oid后面的
        html_data = get_response(url).text
        result = re.findall(".*?([\u4E00-\u9FA5]+).*?", html_data)
        save(result)


if __name__ == '__main__':
    one_url = 'https://api.bilibili.com/x/v2/dm/history/index?type=1&oid=1047253529&month=2023-03' #改oid还有month
    main(one_url)
