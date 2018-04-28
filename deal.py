'''
    a plugin in qqbot https://github.com/pandolia/qqbot
'''

import random, time, sys, requests, json
from snownlp import SnowNLP

ip = '144.202.120.176'
nic = 'nicbh'


def onQQMessage(bot, contact, member, content):
    if bot.isMe(contact, member):
        return
    if contact.name != '正经学习群' or content == '' or content == '/表情':
        return
    anic = '@{} '.format(nic)
    iif anic in content:
        content = '[@ME] ' + content.replace(anic, '')
    if '@ME' in content:
        content = content[5:].strip()
        if content == '状态':
            bot.SendTo(contact, '我在哦')
            return
        if content == '黄漫' or content.lower() == 'hentai':
            hhentai = ['https://hanime.tv', 'http://hentaiplay.net', 'https://e-hentai.org']
            bot.SendTo(contact, random.choice(hhentai))
            return
        if content == '黄图':
            hpic = ['https://www.pixiv.net', 'http://konachan.com', 'https://www.tumblr.com', 'https://www.lofter.com']
            bot.SendTo(contact, random.choice(hpic))
            return
        if content == '黄文' or content == '黄段子':
            hessay = ['https://www.zhihu.com', 'https://weibo.com']
            bot.SendTo(contact, random.choice(hessay))
            return
        if content == '黄网':
            hsite = ['https://www.baidu.com', 'https://pan.baidu.com']bot.SendTo(contact, random.choice(hsite))
            return
        if content.lower() == 'av':
            av = ['https://javmoo.net', 'https://hpjav.com', 'https://www.youav.com', 'https://www.pornhub.com', 'https://www.xvideos.com']
            bot.SendTo(contact, random.choice(av))
            return
        keyword = None
        if content.startswith('bt '):
            keyword = content[3:]
        else:
            position = content.find('-')
            if 0 < position < 6 and len(content) < 15:
                keyword = content.replace(' ', '')
        sys.stdout.flush()
        print('[btInfo]', content, '||', keyword)
        sys.stdout.flush()
        if keyword is not None:
            r = requests.post('http://{}:5000/search2'.format(ip), data={'keyword': keyword})
            if r.ok:
                data = json.loads(r.text)
                response = '\n'.join(
                    ['{} {} {} {}\n{}'.format(x['name'], x['time'], x['volume'], x['hot'], x['magnet']) for x in data[0]])
                bot.SendTo(contact, response)
                response = '\n'.join(
                    ['{} {} {} {}\n{}'.format(x['name'], x['time'], x['volume'], x['hot'], x['magnet']) for x in
                     data[1]])
                bot.SendTo(contact, response)

    else:
        rand = random.randint(0, 100)
        prob = abs(SnowNLP(content).sentiments - 0.5) * 100 / 2
        print(prob)
        if rand < prob or '二' in content:
            bot.SendTo(contact, content + ' 嘤嘤嘤')
