from bs4 import BeautifulSoup as bs
import requests
import re
import json
from database.messages.db_control import add_or_update_horoscope
from database.messages.db import init_db
from misc import SIGNS_EN_RU, SIGNS_RU_EN


def remove_tags(text):
    return re.compile(r'<[^>]+>').sub('', text)


# возвращает гороскоп для всех зз на сегодня
def get_horo():
    res = {}
    for k in SIGNS_EN_RU.keys():
        sub_res = {}
        headers = requests.utils.default_headers()
        headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows; U; Windows NT 5.0) AppleWebKit/532.1.0 (KHTML, like Gecko)'
                          ' Chrome/34.0.822.0 Safari/532.1.0', })
        url = requests.get('https://horo.mail.ru/prediction/' + k + '/' + 'today/', headers=headers)
        s = bs(url.text, 'html.parser')
        text = s.find("main", {"data-qa": "ArticleLayout"})
        text = re.sub(r'<a(.*?)</a>', '', str(text))
        text = remove_tags(text)
        sub_res[0] = text + "\n Источник: mail.ru"
        res[SIGNS_EN_RU[k]] = sub_res

    for k in SIGNS_RU_EN.keys():
        data = (bs(requests.get("https://74.ru/horoscope/daily/").text, 'html.parser').find('h3', text=v).findNext(
            'div').text + "\n Источник: 74.ru")
        res[k][1] = data
    return res


data = get_horo()
# Инициализируем бд в случае если еще не запускали бота
init_db()
for k, v in data.items():
    add_or_update_horoscope(k, json.dumps(v, ensure_ascii=False).encode("utf-8"))
