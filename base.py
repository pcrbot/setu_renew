import os
import json
import traceback
import asyncio
import aiohttp
import random
import string
import base64
import re
from hoshino import R
from .config import get_config, get_group_config
from .acggov import acggov_init, acggov_fetch_process, acggov_get_setu, acggov_search_setu, acggov_get_ranking_setu, acggov_get_ranking, get_setu_native
from .lolicon import lolicon_init, lolicon_get_setu,lolicon_fetch_process, lolicon_search_setu
from .lolicon import get_setu_native as lolicon_get_setu_native


def check_path():
    state = {}
    sub_dirs = ['acggov', 'lolicon', 'lolicon_r18']
    for item in sub_dirs:
        res = R.img('setu_mix/' + item)
        if not os.path.exists(res.path):
            os.makedirs(res.path)
        state[item] = len(os.listdir(res.path)) // 2
    return state
check_path()

def get_spec_image(id):
    image = lolicon_get_setu_native(0,id)
    if not image["data"]:
        imageurl = f'没有在本地找到这张图片呢~\n原图地址:https://pixiv.lancercmd.cc/{id}'
        return imageurl
    image = format_setu_msg(image,1)
    return image


def add_salt(data):
    salt = ''.join(random.sample(string.ascii_letters + string.digits, 6))
    return data + bytes(salt, encoding="utf8")

def format_setu_msg(image,method=0):
    rule = re.compile('^([A-Za-z0-9+/]{4})*([A-Za-z0-9+/]{4}|[A-Za-z0-9+/]{3}=|[A-Za-z0-9+/]{2}==)$')
    data = (rule.search(str(image['data'])))
    if data:
        base64_str = f"base64://{base64.b64encode(add_salt(image['data'])).decode()}"
        msg = f'「{image["title"]}」/「{image["author"]}」\nPID:{image["id"]}\n[CQ:image,file={base64_str}]'
    else:
        msg = f'「{image["title"]}」/「{image["author"]}」\nPID:{image["id"]}[CQ:image,file=file:///{image["data"]}]'
    if method == 1:
        msg = f'「{image["title"]}」/「{image["author"]}」\n[CQ:image,file=file:///{image["data"]}]'
        msg2 = f'如果看不到原图的话,在这里查看哦~\n{image["url"]}'
        return msg, msg2
    return msg

async def get_setu(group_id):
    source_list = []
    if get_group_config(group_id, 'lolicon'):
        source_list.append(1)
    if get_group_config(group_id, 'lolicon_r18'):
        source_list.append(2)
    if get_group_config(group_id, 'acggov'):
        source_list.append(3)
    source = 0
    if len(source_list) > 0:
        source = random.choice(source_list)
    
    image = None
    if source == 1:
        image = await lolicon_get_setu(0)
    elif source == 2:
        image = await lolicon_get_setu(1)
    elif source == 3:
        image = await acggov_get_setu()
    else:
        return None
    if not image:
        return '获取失败'
    elif image['id'] != 0:
        return format_setu_msg(image)
    else:
        return image['title']

async def search_setu(group_id, keyword, num):
    source_list = []
    if get_group_config(group_id, 'lolicon') and get_group_config(group_id, 'lolicon_r18'):
        source_list.append(2)
    elif get_group_config(group_id, 'lolicon'):
        source_list.append(0)
    elif get_group_config(group_id, 'lolicon_r18'):
        source_list.append(1)
    if get_group_config(group_id, 'acggov'):
        source_list.append(3)

    if len(source_list) == 0:
        return None
    
    image_list = None
    msg_list = []
    while len(source_list) > 0 and len(msg_list) == 0:
        source = source_list.pop(random.randint(0, len(source_list) - 1))
        if source == 0:
            image_list = await lolicon_search_setu(keyword, 0, num)
        elif source == 1:
            image_list = await lolicon_search_setu(keyword, 1, num)
        elif source == 2:
            image_list = await lolicon_search_setu(keyword, 2, num)
        elif source == 3:
            image_list = await acggov_search_setu(keyword, num)
        if image_list and len(image_list) > 0:
            for image in image_list:
                msg_list.append(format_setu_msg(image))
    return msg_list

async def get_ranking(group_id, page: int = 0):
    if not get_group_config(group_id, 'acggov'):
        return None
    return await acggov_get_ranking(page)


async def get_ranking_setu(group_id, number: int) -> (int, str):
    if not get_group_config(group_id, 'acggov'):
        return None
    image = await acggov_get_ranking_setu(number)
    if not image:
        return '获取失败'
    elif image['id'] != 0:
        return format_setu_msg(image)
    else:
        return image['title']

async def fetch_process():
    tasks = []
    #tasks.append(asyncio.ensure_future(acggov_fetch_process()))
    tasks.append(asyncio.ensure_future(lolicon_fetch_process()))
    for task in asyncio.as_completed(tasks):
        await task

acggov_init()
lolicon_init()
