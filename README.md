# setu_renew

基于HoshinoBot v2的涩图插件, 从 [acg-gov.com](https://acg-gov.com) 和 [lolicon.app](https://lolicon.app/) 获取图片.

**本项目基于@zyujs的[setu_mix](https://github.com/zyujs/setu_mix)改进而来。**

## 主要改进

- [x] 加入了群黑白名单功能
- [x] 加入了群人数限制功能
- [x] 代理全覆盖，从查询到获取到下载
- [x] 负载均衡，并可以智能选择仍有额度的key(需要多个lolicon key)
- [x] 搜索/发送/下载失败时均会发送提示，防止出现指令无响应或无下文的假象
- [x] 搜索无结果时可以随机发送一份涩图
- [x] 优化发送消息结构
- [x] 优化发图流程，本地图片使用file协议发送
- [x] 可根据图片pid提取图片，若本地有则会直接发送，否则会给出原图链接
- [x] 优化触发指令，将随机涩图的指令与指定关键词的指令合并
- [x] 支持自定义一人一次最多要的涩图数量
- [x] 中文化管理指令
- [x] 增加配置文件热重载的指令
- [ ] 成员黑名单
- [ ] 自动反和谐
- [ ] 使用转发消息的形式发送（规避检测，降低被举报的风险）

## 注意事项

本插件图片存放位置为 `RES_DIR/setu_mix` , 使用前请保证HoshinoBot的 `RES_DIR` 已经正确配置.

刚开始使用插件时本地仓库为空, 会导致无法发送随机图片, 可以在安装配置完毕后使用 `setu 缓存` 命令手动抓取一批图片.

## 安装方法

1. 在HoshinoBot的插件目录modules下clone本项目 `git clone https://github.com/pcrbot/setu_renew.git`
1. 将本插件目录下的配置文件模板 `config.template.json` 复制并重命名为 `config.json` , 修改该配置文件设置自己的apikey和其他选项, 除apikey以外都可保持默认值.
1. 在 `config/__bot__.py`的模块列表里加入 `setu_renew`
1. 重启HoshinoBot

## 配置文件详细说明

- `base`分组:  
  - `daily_max` : 每日每人要涩图的上限
  - `freq_limit` : 两次之间的冷却时间
  - `whitelistmode` : 白名单模式, 仅允许位于白名单中的群要涩图
  - `blacklistmode` : 黑名单模式, 不允许黑名单中的群要涩图
  - `ban_if_group_num_over` : 自动黑名单设置, 将群人数超过此处设置的自动加入黑名单, 设置为3000表示不启用
  - `max_pic_once_send` : 每人一次最多要涩图的张数  
- `default`分组 : 此处的配置为每个群的默认配置
  - `withdraw` : 撤回时间, 0为不撤回
  - `lolicon`、`lolicon_r18`、`acggov` : 是否启用各图源
- `lolicon`分组(acggov分组同):
  - `mode` : 模块模式, 0=关闭, 1=在线(不使用本地仓库), 2=在线(使用本地仓库), 3=离线(仅使用本地仓库), 默认模式为2.
  - `apikey` : apikey, 数组格式, 可配置多个 **(必须配置)**.
  - `r18` : 是否启用r18
  - `use_thumb` : 是否发送大小更小的图
  - `pixiv_direct` : 是否通过代理访问pixiv, 请在下方配置代理
  - `pixiv_proxy` : 访问pixiv的代理 **(推荐使用`https://i.pixiv.cat`)**
  - `lolicon_proxy` : 访问lolicon&上方代理的代理, 不需要请留空.

## 指令说明

- 来 [num] 张 [keyword] 涩/色/瑟图 : 来num张keyword的涩图 
(不指定数量与关键字发送一张随机涩图)
- 涩/色/瑟图 : 发送一张随机涩图
- 本日涩图排行榜 [page] : 获取[第page页]p站排行榜(需开启acggov模块)
- 看涩图 [n] 或 [start end] : 获取p站排行榜[第n名/从start名到end名]色图(需开启acggov模块)
- 提取图片 pid : 获取指定pid的图片,若本地有则会直接发送,否则将给出原图链接.

### 以下指令仅限超级用户使用

- `setu 设置 模块 设置值 [群号]` : 修改本群或指定群的设置  
设置项 - 取值 - 说明:
  - `acggov` : `开 / 关` 是否开启acggov模块
  - `lolicon` : `开 / 关` 是否开启lolicon模块
  - `lolicon_r18` : `开 / 关` 是否开启lolicon_r18模块
  - `撤回` : `n` 发出的图片在n秒后撤回, 设置为0表示不撤回
- `setu 状态 [群号]` : 查看本群或指定群的模块开启状态
- `setu 缓存` :  手动从api拉取一批图片存入本地仓库(插件每10分钟会自动拉取一次)
- `setu 仓库` : 查询本地仓库图片数量
- `setu 重载` : 热重载配置文件
- `setu 黑/白名单 新增/删除 群号` : 修改黑白名单

## 已知问题

- 使用纯在线模式时，采用的是base64方式发送，而此方法无法发送过大的图片，故有较大概率无法发送

## 开源协议

本插件以AGPL-v3协议开源
