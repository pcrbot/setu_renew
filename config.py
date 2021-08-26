import datetime
import json
import os
import random
import traceback

import nonebot

import hoshino

cfgpath = os.path.join(os.path.dirname(__file__), 'config.json')
grouplistpath = os.path.join(os.path.dirname(__file__), 'grouplist.json')
groupconfigpath = os.path.join(os.path.dirname(__file__), 'groupconfig.json')
group_config = {}
config = {}
invaild_key_dict = {}
group_list = {}
config = json.load(open(cfgpath, 'r', encoding='utf8'))
group_list = json.load(open(grouplistpath, 'r', encoding='utf8'))
group_config = json.load(open(groupconfigpath, 'r', encoding='utf8'))



def get_config(key, sub_key):
	if key in config and sub_key in config[key]:
		return config[key][sub_key]
	return None


def group_list_check(gid):
	"""
    响应值:\n
    0 : ok\n
    1 : 启用白名单模式且不在白名单内\n
    2 : 启用黑名单模式且在黑名单内\n
    白名单优先级高于黑名单
    """
	gid = str(gid)
	if get_config('base', 'whitelistmode') is True:
		if gid in group_list["white_list"]:
			return 0
		else:
			return 1
	elif get_config('base', 'blacklistmode') is True:
		if gid in group_list["black_list"]:
			return 2
		else:
			return 0
	else:
		return 0


def set_group_list(gid, _list, mode):
	"""
    gid(int,str/list) : group id \n
    _list(int/str)    : 0 whitelist / 1 blacklist\n
    mode(int/str)     : 0 add / 1 remove\n
    返回值(第一字段 / int) : \n
    0   ok\n
    401 黑名单模式未开启\n
    402 白名单模式未开启\n
    403 无法访问黑白名单\n
    404 gid不在指定的列表中\n
    500 传入数据格式无效\n
    返回值(第二字段 / list/str) :\n
    空字符串 ok\n
    gid     未完成操作的gid
    """
	failed_gids = []
	try:
		_list = int(_list)
	except:
		return 500, ''
	try:
		mode = int(mode)
	except:
		return 500, ''
	if type(gid) == int or type(gid) == str:
		gid = [str(gid)]
	elif type(gid) == list:
		gid = [str(i) for i in gid]
	else:
		return 500, ''
	if _list == 0:
		if mode == 0:
			for i in gid:
				group_list["white_list"].append(i)
		if mode == 1:
			for i in gid:
				if i in group_list["white_list"]:
					group_list["white_list"].remove(i)
				else:
					hoshino.logger.error(f'[ERROR]gid {i} 不在指定列表中')
					failed_gids.append(i)
					continue
		group_list["white_list"] = list(set(group_list["white_list"]))
	else:
		if mode == 0:
			for i in gid:
				group_list["black_list"].append(i)
		if mode == 1:
			for i in gid:
				if i in group_list["black_list"]:
					group_list["black_list"].remove(i)
				else:
					hoshino.logger.error(f'[ERROR]gid {i} 不在指定列表中')
					failed_gids.append(i)
					continue
		group_list["black_list"] = list(set(group_list["black_list"]))
	try:
		with open(grouplistpath, 'w') as f:
			json.dump(group_list, f, ensure_ascii=False, indent=2)
			if get_config('base', 'blacklistmode') is False:
				return 401, failed_gids
			if get_config('base', 'whitelistmode') is False:
				return 402, failed_gids
			return 0, failed_gids
	except:
		return 403, failed_gids


def get_api_num():
	return int(len(config["lolicon"]["apikey"]))


def get_group_config(group_id, key):
	group_id = str(group_id)
	if group_id not in group_config:
		return config['default'][key]
	if key in group_config[group_id]:
		return group_config[group_id][key]
	else:
		return None


def set_group_config(group_id, key, value):
	group_id = str(group_id)
	if group_id not in group_config:
		group_config[group_id] = {}
		for k, v in config['default'].items():
			group_config[group_id][k] = v
	group_config[group_id][key] = value
	try:
		with open(groupconfigpath, 'w', encoding='utf8') as f:
			json.dump(group_config, f, ensure_ascii=False, indent=2)
	except:
		traceback.print_exc()


async def get_group_info(group_ids=0, info_type='member_count'):
	"""
    1. 传入一个整型数字, 返回单个群指定信息, 格式为字典
    2. 传入一个list, 内含多个群号(int), 返回一个字典, 键为群号, 值为指定信息
    3. 不填入参数, 返回一个包含所有群号与指定信息的字典
    无论获取多少群信息, 均只有一次API的开销, 传入未加入的群时, 将自动忽略
    info_type支持group_id, group_name, max_member_count, member_count
    """
	group_info_all = await get_group_list_all()
	_gids = []
	_gnames = []
	# 获得的已加入群为列表形式, 处理为需要的字典形式
	for it in group_info_all:
		_gids.append(it['group_id'])
		_gnames.append(it[info_type])
	group_info_dir = dict(zip(_gids, _gnames))
	
	if group_ids == 0:
		return group_info_dir
	if type(group_ids) == int:
		# 转为列表
		group_ids = [group_ids]
		hoshino.logger.error(group_ids)
	
	for key in list(group_info_dir.keys()):
		if key not in group_ids:
			del group_info_dir[key]
		else:
			# TODO: group not joined
			pass
	return group_info_dir


async def get_group_list_all():
	"""
    获取所有群, 无论授权与否, 返回为原始类型(列表)
    """
	bot = nonebot.get_bot()
	self_ids = bot._wsr_api_clients.keys()
	for sid in self_ids:
		group_list = await bot.get_group_list(self_id=sid)
	return group_list
