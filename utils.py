from vkpymusic import TokenReceiver, Service
import requests
import os


def convert_song_duration(seconds: int) -> str:
    """
    Convert song duration(in seconds) to duration('xx:xx')
    :param seconds:
    :return:
    """
    mins = seconds // 60
    secs = seconds % 60
    return f'{mins:0>2}:{secs:0>2}'


def vk_search(query: str, count=100) -> dict[int: dict]:
    # Для ручного получения токена
    # https://oauth.vk.com/authorize?client_id=2685278&scope=audio&redirect_uri=https://oauth.vk.com/blank.html&display=page&response_type=token
    service = Service(os.getenv('VK_USER_AGENT'), os.getenv('VK_TOKEN'))
    try:
        songs = service.search_songs_by_text(text=query, count=count)

        result = {}
        counter = 0
        try:
            for song in songs:
                result[f"v{counter}"] = {'name': song.title,
                                         'author': song.artist,
                                         'album': None,
                                         'bitrate': None,
                                         'duration_text': convert_song_duration(song.duration),
                                         'duration': song.duration,
                                         'album_cover_url': None,
                                         'url': song.url
                                         }
                counter += 1
        except Exception:
            pass

        return result
    except Exception as e:
        print(e)
        return {}


def mail_ru_search(query, count=100) -> dict:
    headers = {
        'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64; rv:109.0) Gecko/20100101 Firefox/115.0',
        'Accept': 'application/json, text/javascript, */*; q=0.01',
        'Accept-Language': 'ru-RU,ru;q=0.8,en-US;q=0.5,en;q=0.3',
        'X-Secret-Key': '%E5%97%D1%D9%E1%D3%CE%A0%9B%DF%D1%AE%D4%9D%DA%D6%D2%D7%9D%A7%99',
        'X-Requested-With': 'XMLHttpRequest',
        'Connection': 'keep-alive',
        'Referer': 'https://my.mail.ru/music/search/Five',
        'Sec-Fetch-Dest': 'empty',
        'Sec-Fetch-Mode': 'cors',
        'Sec-Fetch-Site': 'same-origin',
    }

    params = {
        'xemail': '',
        'ajax_call': '1',
        'func_name': 'music.search',
        'mna': '',
        'mnb': '',
        'arg_query': query,
        'arg_extended': '1',
        'arg_search_params': f'{{"music":{{"limit":{count}}},"playlist":{{"limit":50}},"album":{{"limit":10}},"artist":{{"limit":10}}}}',
        # '{"music":{"limit":400},"playlist":{"limit":50},"album":{"limit":10},"artist":{"limit":10}}'
        'arg_offset': '0',
        'arg_limit': '200',
        '_': '1688932574418',
    }

    resp = requests.get('https://my.mail.ru/cgi-bin/my/ajax', params=params, headers=headers)
    resp_data = resp.json()

    result = {}
    counter = 0
    try:
        for md in resp_data[3]['MusicData']:
            result[f"m{counter}"] = {'name': md['Name_Text_HTML'],
                                     'author': md['Author'],
                                     'album': md['Album'],
                                     'bitrate': md['BitRate'],
                                     'duration_text': md['Duration'],
                                     'duration': md['DurationInSeconds'],
                                     'album_cover_url': md['AlbumCoverURL'],
                                     'url': 'https:' + md['URL']
                                     }
            counter += 1
    except Exception as e:
        print(e)

    return result
