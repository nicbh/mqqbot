'''
debian:
    google-chrome chromedriver xvfb xauth
    pip3 install beautifulsoup4 flask requests selenium
'''

import requests
import json
import time
import random
import sys
import os
import time
from bs4 import BeautifulSoup
from urllib.parse import unquote, quote
from flask import Flask, request
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import TimeoutException

timeout_start = 20
timeout_max = 60


def sleep(down, up):
    time.sleep(random.random() * (up - down) + up)


def open_site(browser, func):
    url = ''
    if type(func) is str:
        url = func
        func = lambda b: b.get(url)
    success = False
    timeout = timeout_start
    while success is False and timeout <= timeout_max:
        try:
            print('[INFO {}] start to loading {} in {}s'.format(
                time.ctime(), url, timeout))
            sys.stdout.flush()
            if timeout == timeout_start:
                func(browser)
            else:
                browser.refresh()
            success = True
        except TimeoutException:
            print('[INFO {}] time out after {} seconds when loading'.format(
                time.ctime(), timeout))
            sys.stdout.flush()
            try:
                browser.execute_script('window.stop()')
                success = True
            except TimeoutException:
                sleep(0.5, 1 + timeout / 10)
                timeout += 10
                url = browser.current_url
                browser.set_page_load_timeout(timeout)
                browser.set_script_timeout(timeout)
    browser.set_page_load_timeout(timeout_start)
    browser.set_script_timeout(timeout_start)


def url2hash(url):
    return url.split('/')[-1]


def url2magnet(url):
    return 'magnet:?xt=urn:btih:' + url2hash(url)


def getOptions(headless=True):
    chrome_options = Options()
    chrome_options.add_argument('--no-sandbox')
    if headless is True:  # if not, with xvfb
        chrome_options.add_argument('--headless')
    chrome_options.add_argument('--disable-gpu')
    chrome_options.add_argument('--ignore-certificate-errors')  # https certi
    # chrome_options.binary_location = '/opt/google/chrome/chrome'
    extension_path = os.getcwd() + '/stopper.crx'
    chrome_options.add_extension(extension_path)
    prefs = {
        'profile.default_content_setting_values': {
            'images': 2,
            'javascript': 2
        }
    }
    chrome_options.add_experimental_option('prefs', prefs)
    return chrome_options

app = Flask(__name__)


@app.route('/search_btso', methods=['POST'])
def search_btso(keyword=None):
    response = None
    browser = webdriver.Chrome(chrome_options=getOptions(False))
    try:
        length = 5
        if keyword is None:
            keyword = request.form['keyword']
            if 'length' in request.form:
                length = request.form['length']
        url = 'https://btso.pw/search/{}'.format(keyword)
        resources = []
        sleep(0.5, 1.5)
        open_site(browser, url)
        soup = BeautifulSoup(browser.page_source, 'html.parser')
        data_list = soup.find(class_='data_list')
        if data_list is not None:
            data_list = data_list.find_all('div')[1:]
            index = 0
            for item in data_list[0:length]:
                name = item.a.attrs['title']
                href = item.a.attrs['href']
                magnet = url2magnet(href)
                time_ = item.find(class_='date')
                volume = item.find(class_='size')
                index += 1
                resources.append({
                    'name': name,
                    'num': index,
                    'href': href,
                    'magnet': magnet,
                    'time': time_,
                    'volume': volume
                })
        resources = [x for x in resources if x is not None]
        response = json.dumps(resources, ensure_ascii=False)
        return response
    finally:
        browser.close()


@app.route('/search_bt2', methods=['POST'])
def search_btrabbit(keyword=None):
    response = None
    browser = webdriver.Chrome(chrome_options=getOptions())
    try:
        length = 5
        if keyword is None:
            keyword = request.form['keyword']
            if 'length' in request.form:
                length = request.form['length']
                if length > 30:
                    length = 30
        url = 'https://btso.pw/search/{}'.format(keyword)
        resources = []
        sleep(0.5, 1.5)
        open_site(browser, url)
        soup = BeautifulSoup(browser.page_source, 'html.parser')
        data_list = soup.find(class_='data_list')
        if data_list is not None:
            data_list = data_list.find_all('div')[1:]
            index = 0
            for item in data_list[0:length]:
                name = item.a.attrs['title']
                href = item.a.attrs['href']
                magnet = url2magnet(href)
                time_ = item.find(class_='date')
                volume = item.find(class_='size')
                index += 1
                resources.append({
                    'name': name,
                    'num': index,
                    'href': href,
                    'magnet': magnet,
                    'time': time_,
                    'volume': volume
                })
        resources = [x for x in resources if x is not None]
        response = json.dumps(resources, ensure_ascii=False)
        return response
    finally:
        browser.close()


@app.route('/search_bt', methods=['POST'])
def search_cnbtkitty(keyword=None):
    def getMagnet(contentUrl, browser):
        sleep(0.3, 0.7)
        open_site(browser, contentUrl)
        soup = BeautifulSoup(browser.page_source, 'html.parser')
        magnet = soup.find(class_='magnet')
        return magnet.a.attrs['href']

    def getResouce(html, browser):
        resource = []
        soup = BeautifulSoup(html, 'html.parser')
        list = soup.find_all('dl')
        num = 3
        index = 0
        if len(list) < num:
            num = len(list)
        for item in list[0:num]:
            href = item.dt.a
            if href is None:
                return None
            href = item.dt.a.attrs['href']
            spans = item.find(class_='option').find_all('span')
            magnet = getMagnet(spans[1].a.attrs['href'], browser)
            name = unquote(magnet[magnet.rfind('=') + 1:])
            magnet = magnet[0:magnet.rfind('&dn=')]
            time_ = spans[2].b.string
            volume = spans[3].b.string
            files = spans[4].b.string
            hots = spans[6].b.string
            index += 1
            resource.append({
                'name': name,
                'num': index,
                'href': href,
                'magnet': magnet,
                'time': time_,
                'volume': volume,
                # 'file': files,
                'hot': hots
            })
        return resource

    response = None
    browser = webdriver.Chrome(chrome_options=getOptions())
    try:
        browser.set_page_load_timeout(timeout_start)
        browser.set_script_timeout(timeout_start)
        url = 'http://cnbtkitty.org/'
        if keyword is None:
            keyword = request.form['keyword']
        keyword = quote(keyword)
        sleep(0.5, 1.5)
        open_site(browser, url)
        # sleep(0.5, 1.5)
        browser.find_element_by_id('kwd').send_keys(keyword)
        sleep(0.5, 1)
        open_site(browser, lambda b: b.find_element_by_id(
            'kwd').send_keys(Keys.ENTER))
        url = browser.current_url
        print(url)
        subclass = ['4']
        resources = [getResouce(browser.page_source, browser)]
        for sub in subclass:
            url = url[0:url.find('/', url.find('search/') + 7)]
            url = '{}/1/{}/0.html'.format(url, sub)
            sleep(0.5, 1.5)
            open_site(browser, url)
            resouce = getResouce(browser.page_source, browser)
            resources.append(resouce)
        resources = [x for x in resources if x is not None]
        response = json.dumps(resources, ensure_ascii=False)
        return response
    finally:
        browser.close()


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
    argv = sys.argv
    if len(argv) > 0 and argv[0].endswith('.py'):
        argv.pop(0)
    if len(argv) > 0:
        if argv[0].lower() == 'stop':
            os.system(
                "kill $(ps aux | grep 'chrom[e]' | awk '{print $2}')")
            os.system("kill $(ps aux | grep 'bt.p[y]' | awk '{print $2}')")
        elif argv[0].lower() == 'kw':
            mode = 'bt'
            if argv[1].lower() == 'btso':
                keyword = argv[2]
                mode = 'btso'
            elif argv[1].lower() == 'bt2':
                keyword = argv[2]
                mode = 'bt2'
            else:
                keyword = argv[1]
            print('start to search keyword "{}"...'.format(keyword))
            if mode == 'bt':
                response = search_cnbtkitty(keyword)
            elif mode == 'btso':
                response = search_btso(keyword)
            elif mode == 'bt2':
                response = search_btrabbit(keyword)
            print(quote(response))
    else:
        app.run(debug=False, host='0.0.0.0')