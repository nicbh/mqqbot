'''
debian:
    google-chrome chromedriver
    pip3 install beautifulsoup4 flask requests
'''

from bs4 import BeautifulSoup
from urllib.parse import unquote, quote
from flask import Flask, request
import requests, json, time, random


def sleep(down, up):
    time.sleep(random.random() * (up - down) + up)


def getResouce(html):
    resource = []
    soup = BeautifulSoup(html, 'html.parser')
    list = soup.find_all('dl')
    num = 3
    if len(list) < num:
        num = len(list)
    for item in list[0:num]:
        href = item.dt.a.attrs['href']
        spans = item.find(class_='option').find_all('span')
        magnet = spans[0].a.attrs['href']
        name = unquote(magnet[magnet.rfind('=') + 1:])
        time_ = spans[1].b.string
        volume = spans[2].b.string
        # files = spans[3].b.string
        hots = spans[5].b.string
        resource.append({
            'name': name,
            'href': href,
            'magnet': magnet,
            'time': time_,
            'volume': volume,
            # 'file': files,
            'hot': hots
        })
    return resource


from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys

chrome_options = Options()
chrome_options.add_argument('--headless')
chrome_options.add_argument('--disable-gpu')
chrome_options.add_argument('--no-sandbox')
chrome_options.binary_location = '/opt/google/chrome/chrome'

app = Flask(__name__)


@app.route('/search2', methods=['POST'])
def search_v2():
    response = None
    browser = webdriver.Chrome(chrome_options=chrome_options)
    try:
        browser.set_window_size(1080, 720)
        browser.implicitly_wait(20)
        url = 'http://cnbtkitty.net/'
        keyword = quote(request.form['keyword'])
        sleep(0.5, 1.5)
        browser.get(url)
        sleep(0.5, 1.5)
        browser.find_element_by_id('kwd').send_keys(keyword)
        sleep(0.5, 1)
        browser.find_element_by_id('kwd').send_keys(Keys.ENTER)
        url = browser.current_url
        print(url)
        subclass = ['4']
        resources = [getResouce(browser.page_source)]
        for sub in subclass:
            url = url[0:url.find('/', url.find('search/') + 7)]
            url = '{}/1/{}/0.html'.format(url, sub)
            sleep(0.5, 1.5)
            browser.get(url)
            resouce = getResouce(browser.page_source)
            resources.append(resouce)
        response = json.dumps(resources, ensure_ascii=False)
        return response
    finally:
        browser.quit()


@app.route('/search', methods=['POST'])
def search():
    keyword = quote(request.form['keyword'])
    print(keyword)
    url = 'http://cnbtkitty.net/'
    data = {
        'keyword': keyword,
        'hidden': True
    }
    headers = {
        'Host': 'cnbtkitty.net',
        'Proxy-Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1',
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/65.0.3325.181 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
        'Origin': 'http://cnbtkitty.net/',
        'Accept-Encoding': 'gzip, deflate',
        'Accept-Language': 'zh-CN,zh;q=0.9',
        'Cache-Control': 'no-cache',
        'Content-Type': 'application/x-www-form-urlencoded,'
    }
    headers['Content-Length'] = str(len(keyword) + 20)
    r = requests.post(url, headers=headers, data=data)

    if r.ok:
        url = r.url
        print(url)
        num = 3
        subclass = ['1', '4']
        resources = []
        for sub in subclass:
            time.sleep(random.randint(1, 2))
            url = url[0:url.find('/', url.find('search/') + 7)]
            url = '{}/1/{}/0.html'.format(url, sub)
            r = requests.get(url)
            resources.append(getResouce(r.text))
        response = json.dumps(resources, ensure_ascii=False)
        return response
    else:
        print(r.text)
        raise ConnectionError


if __name__ == '__main__':
    app.run(debug=False, host='0.0.0.0')
