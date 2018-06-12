'''
    a plugin in qqbot https://github.com/pandolia/qqbot
'''
# TODO: key-value, ml
import random, time, sys, requests, json, threading, os
from snownlp import SnowNLP
from googletrans import Translator, LANGUAGES
from qqbot.utf8logger import INFO


ip = '104.238.149.58'
nic = 'nicbh'
max_length = 719
translator = Translator(service_urls=['translate.google.cn'])
rand_generator = random.SystemRandom()
bt_buffer = {}


def in_bt_buffer(keyword):
    out_date_time = 5 * 60
    now_time = time.time()
    if keyword in bt_buffer:
        if now_time - bt_buffer[keyword] < out_date_time:
            return True
        else:
            bt_buffer[keyword] = now_time
            with open('bt_buffer.log', 'w+', encoding='utf-8') as file:
                file.write(json.dumps(bt_buffer, ensure_ascii=False, indent=4))
            return False
    else:
        bt_buffer[keyword] = now_time
        with open('bt_buffer.log', 'w+', encoding='utf-8') as file:
            file.write(json.dumps(bt_buffer, ensure_ascii=False, indent=4))
        return False


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
    timestamp = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())
    print('[deal@{}] {}'.format(timestamp, content))
    sys.stdout.flush()


def onExit(bot, code, reason, error):
    if code == 202:
        INFO('开始休眠...')
        time.sleep(random.randint(3, 10))
        INFO('休眠结束')


def onQQMessage(bot, contact, member, content):
    if bot.isMe(contact, member):
        return
    if content == '' or content == '/表情':
        return
    anic = '@{} '.format(nic)
    if anic in content:
        content = '[@ME] ' + content.replace(anic, '')

    # TODO config file
    if '@ME' in content or member is None:
        if member is not None:
            content = content[5:].strip()
        # look for
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
        if content.lower() == 'help':
            help_text = '指令：状态, help, 黄图, 黄文/黄段子, 黄网, av\n' + \
                        'src2dest sourceLanguage 源语言翻译到目标语言\n' + \
                        'detectlang text 语言检测\n' + \
                        'languages 语言缩写列表\n' + \
                        'bt keyword 磁力搜索\n' + \
                        '(0<len<9)-(all_len<15) 番号搜索'
            send(bot, contact, help_text)
            return

        # translate
        if '2' in content.split()[0]:
            shortLang = {'c': 'zh-cn', 'j': 'ja', 'e': 'en'}
            sourceLang, targetLang = content.split()[0].lower().split('2')
            transcode = '{}2{} '.format(sourceLang, targetLang)
            if content.lower().startswith(transcode):
                text = content[len(transcode):].strip()
                if sourceLang in shortLang:
                    sourceLang = shortLang[sourceLang]
                if targetLang in shortLang:
                    targetLang = shortLang[targetLang]
                if sourceLang in LANGUAGES and targetLang in LANGUAGES and len(text) > 0:
                    send(bot, contact, translator.translate(text, targetLang, sourceLang).text)
                    return
        if content.lower().startswith('detectlang '):
            text = content[11:].strip()
            if len(text) > 0:
                detected = translator.detect(text)
                send(bot, contact, '{}@{}'.format(LANGUAGES[detected.lang], detected.confidence))
                return
        if content.lower() == 'languages':
            langs = sorted([(short, long) for short, long in LANGUAGES.items()], key=lambda x: x[0])
            send(bot, contact, ', '.join(['{}:{}'.format(short, long) for short, long in langs]))
            return

        # bt
        keyword = None
        if content.lower().startswith('bt '):
            keyword = content[3:].strip()
        else:
            position = content.find('-')
            if 0 < position < 9 and len(content) < 15:
                keyword = content.replace(' ', '')
        print_flush('[btInfo]: "{}", "{}"'.format(content, keyword))
        if keyword is not None and len(keyword) > 0:
            def search2(bot, contact, keyword):
                try:
                    r = requests.post('http://{}:5000/search2'.format(ip), data={'keyword': keyword}, timeout=60*10)
                    print_flush('[btInfo]: "{}", {}'.format(keyword, r.ok))
                    if r.ok:
                        data = json.loads(r.text)
                        response = ['相关排序:'] + ['{}.{}\n时间:{} 大小:{} 人气:{}\n{}'.format(
                            x['num'], x['name'], x['time'], x['volume'], x['hot'], x['magnet'])
                            for x in data[0]]
                        send(bot, contact, response)
                        response = ['人气排序:'] + ['{}.{}\n时间:{} 大小:{} 人气:{}\n{}'.format(
                            x['num'], x['name'], x['time'], x['volume'], x['hot'], x['magnet'])
                            for x in data[1]]
                        send(bot, contact, response)
                    else:
                        send(bot, contact, '搜索"{}"网络错误了哦'.format(keyword))
                except:
                    send(bot, contact, '搜索"{}"网络错误了哦'.format(keyword))
            if in_bt_buffer(keyword.lower()):
                send(bot, contact, '刚刚才搜过"{}"了哦'.format(keyword.lower()))
                return
            netcom = threading.Thread(target=search2, args=(bot, contact, keyword))
            netcom.setDaemon(True)
            netcom.start()
        else:
            send(bot, contact, '嘤嘤嘤' if member is None else '@{} 嘤嘤嘤'.format(member.name))
    else:
        # repeat
        rand = rand_generator.random()
        prob = abs(SnowNLP(content).sentiments - 0.5) / 2
        print_flush(prob)
        if rand < prob or '二' in content:
            send(bot, contact, content + ' 嘤嘤嘤')
