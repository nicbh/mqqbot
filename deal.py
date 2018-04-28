'''
    a plugin in qqbot https://github.com/pandolia/qqbot
'''
# TODO: asynchronous, default response
import random, time, sys, requests, json
from snownlp import SnowNLP

ip = '144.202.120.176'
nic = 'nicbh'
max_length = 719


def send(bot, contact, massage):
    if type(massage) == list:
        content = '\n'.join(massage)
        while len(content) > max_length:
            for i in range(1, len(massage) + 1):
                content = '\n'.join(massage[0:i])
                if len(content) > max_length:
                    if i == 1:
                        bot.SendTo(contact, content)
                        massage = massage[1:]
                    else:
                        content = '\n'.join(massage[0:i - 1])
                        bot.SendTo(contact, content)
                        massage = massage[i - 1:]
                    break
            content = '\n'.join(massage)
        else:
            bot.SendTo(contact, content)
    else:
        bot.SendTo(contact, massage)


def print_flush(content):
    sys.stdout.flush()
    print(content)
    sys.stdout.flush()


def onQQMessage(bot, contact, member, content):
    if bot.isMe(contact, member):
        return
    if content == '' or content == '/表情':
        return
    anic = '@{} '.format(nic)
    if anic in content:
        content = '[@ME] ' + content.replace(anic, '')

    # TODO config file
    if '@ME' in content:
        content = content[5:].strip()
        if content == '状态':
            send(bot, contact, '我在哦')
            return
        if content == '黄漫' or content.lower() == 'hentai':
            hhentai = ['https://hanime.tv', 'http://hentaiplay.net', 'https://e-hentai.org']
            send(bot, contact, random.choice(hhentai))
            return
        if content == '黄图':
            hpic = ['https://www.pixiv.net', 'http://konachan.com', 'https://www.tumblr.com', 'https://www.lofter.com']
            send(bot, contact, random.choice(hpic))
            return
        if content == '黄文' or content == '黄段子':
            hessay = ['https://www.zhihu.com', 'https://weibo.com']
            send(bot, contact, random.choice(hessay))
            return
        if content == '黄网':
            hsite = ['https://www.baidu.com', 'https://pan.baidu.com']
            send(bot, contact, random.choice(hsite))
            return
        if content.lower() == 'av':
            av = ['https://javmoo.net', 'https://hpjav.com', 'https://www.youav.com', 'https://www.pornhub.com',
                  'https://www.xvideos.com']
            send(bot, contact, random.choice(av))
            return
        keyword = None
        if content.startswith('bt '):
            keyword = content[3:].strip()
        else:
            position = content.find('-')
            if 0 < position < 6 and len(content) < 15:
                keyword = content.replace(' ', '')
        print_flush('[btInfo]: "{}", "{}"'.format(content, keyword))
        if keyword is not None and len(keyword) > 0:
            r = requests.post('http://{}:5000/search2'.format(ip), data={'keyword': keyword})
            if r.ok:
                data = json.loads(r.text)
                response = ['{}.{}\n时间:{} 大小:{} 人气:{}\n{}'.format(
                    x['num'], x['name'], x['time'], x['volume'], x['hot'], x['magnet'])
                    for x in data[0]]
                send(bot, contact, response)
                response = ['{}.{}\n时间:{} 大小:{} 人气:{}\n{}'.format(
                    x['num'], x['name'], x['time'], x['volume'], x['hot'], x['magnet'])
                    for x in data[1]]
                send(bot, contact, response)
        else:
            send(bot, contact, '@{} 嘤嘤嘤'.format(member))

    else:
        rand = random.randint(0, 100)
        prob = abs(SnowNLP(content).sentiments - 0.5) * 100 / 2
        print_flush(prob)
        if rand < prob or '二' in content:
            send(bot, contact, content + ' 嘤嘤嘤')
