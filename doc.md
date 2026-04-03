
# 1、机器人简介

## 典型使用场景
- 发消息，例如：发送报警、业务统计数据、事件通知等
- 收消息，例如用来做人机互动
- 打电话，目前只用于业务监控报警（如夜间）


本文档的最新版本在web上更新，[关注最新版本请点击查看](https://easydoc.qihoo.net/doc?project=1d414e4d0ce730bec9b805b12ca28509&doc=3596913a227ae858de8e1dcca7dae3d6&config=toc)


## 申请开通

**360集团内**

**申请个人机器人** 无需审批快速完成。个人机器人是你个人专属机器人，私聊权限只能与你私聊，你把它拉到群里也能发群。建议报警类业务发群，这样你能自助管理报警接收成员。

> 推推搜索 推推机器人助手，和它私聊。使用 /创建 可自助创建一个机器人，得到appid和secret后用。另外你也可以对它使用 /改头像 指令。

**申请标准机器人**，需要审批，仅当你需要发送多个私聊时使用。

> - 第一步：在qlink系统( https://qlink.qihoo.net/apps/home )提交申请
    - 新建事项 -> 搜索推推
    - 选择【申请推推机器人】
    - 消息发送范围：是指机器人单聊可以发送的范围，对群聊没有限制。建议选择所在的一级事业部。
    - 推推公众号文章接收范围：选自己部门，不要选全员（因为不用发公众号文章）
- 第二步：申请通过后，管理员会将appid和secret回填到申请单中
    - appid：开发者的账号
    - secret：开发者的密钥


**不属于360集团的组织**

> 联系你的组织管理员开通。


## 开源SDK(golang)

使用这个go包，写几行代码就能发消息，公司内部开源，大家也可以一起维护

https://v.src.corp.qihoo.net/pubcode/notice


# 2、机器人发消息

报警类需求建议先参考[QAlarm](http://qalarm.qihoo.net/m/index/index)，QAlarm 已对接推推，可以消息发送到推推app上。如果需求不满足，再考虑直接对接本API

## 接口与鉴权
url传入appid和secret参数鉴权

| 请求  |   说明
| :---  | :-----
| 域名  | https://alarm.im.qihoo.net
| 协议  | HTTPS/HTTP都支持。原则上必须走https，不推荐http。因为http可能会被网络中间人记录引起密钥泄露
| 方法  | POST
| 接口  | /message/custom/send?appid={APPID}&secret={SECRET}
| appid | URL参数，开发者账号
| secret| URL参数，开发者密钥
| Content-Type | application/json
| Body         | json格式，见第3章不同消息类型定义

> 备注：目前仍支持token参数鉴权，仅用于历史兼容，文档已移除


## 发送范围

支持发给人或者群，在发消息请求body中json字段指定。以下 tousers/touids/togroups 至少填其一，不支持人和群混发。

| 范围  |   参数  | 说明
| :---  | :-----  | ---
| 发给人| tousers | 接收人域账号列表，格式为数组。**数量限制：100**
| 发给人| touids | 接收人uid列表，格式为数组。**数量限制：100**
| 发给群| togroups | 群id列表，格式为数组。无需申请权限，只要机器人在群里就能发。**数量限制：10**

**tousers补充说明**
- 发给360集团用户，tousers为域账号列表
- 发给其他组织如外包/金融/花椒，tousers为手机号列表；其他租户具体咨询租户管理员
- 申请机器人权限时，必须包含发送目标权限
- 如果存在跨组织发送（比如申请的机器人隶属于集团，想发给外包），需要先申请权限


**togroups补充说明**
- 群ID如何获取？见常见FAQ
- 如何把机器人拉到群里？见常见FAQ
- 发到群里的方案好处是
    - 无需管理接收人列表的增删
    - 可邀请其他组织/外包人员进群查看

## 外网如何访问

为了安全起见，默认 alarm.im.qihoo.net 只能在内网访问，在外网无法访问。如有外网发消息需求，可以见【联系我们】发邮件到申请开通外网发送权限，提供如下信息
```
appid: （必填）
机器人名字：（必填）
用途&必要性：（必填）
```
原则上不允许拥有大范围私聊权限特别是allstaff的机器人申请外网权限。如果需要申请，需要私聊权限范围变小。建议业务机器人尽量不发私聊，而是发到群里，一方面安全性好（机器人在群里才能发），另一方面能自助管理接收人员列表。


开通后，可以用外网url前缀来访问接口，例如：
```
原来 https://alarm.im.qihoo.net/message/custom/send?appid=123456&secret=***
改为 https://im.live.360.cn:8282/robot/message/custom/send?appid=123456&secret=***
```

## 接口对接开发规范
通过api开发对接机器人接口时，拿到http响应后，应按以下顺序处理：
1. 判断http status code是否为200
2. 判断响应json中errcode是否为0
3. 解析响应json结果

如不按上述顺序判断，跳过步骤1和2，直接执行3解析响应结果，是错误对接行为，机器人接口不保证业务可拿到预期结果。

# 3、发送消息类型

## 文本消息

- 消息体对象:

| JSON字段          | 描述
| ----------------- | --------------------------
| msgtype           | text |
| tousers           | 见《发送范围》章节 |
| touids           | 见《发送范围》章节 |
| togroups          | 见《发送范围》章节 |
| at                    | （可选）要@提醒的人。域账号列表，定义与`tousers`相同。仅群消息有效，如果要at的人不在群内，将被忽略。**数量限制：100人**，如果要@所有人，将“@all”填入该列表。支持消息格式：text(文本), image(图片), mixed(图文混排) |
| text.content           | 文字内容，**长度限制：50000** （一个中文字符长度为1），超出限制将被截断！ |

- 群消息@xxx自定义出现位置

在`content`字段中以"@user "的形式出现（注意最后有一个空格），机器人在发消息时会将该字符串替换为"@user_name "的形式。

示例：

```
{
    "togroups": ["76526696480*****"],
    "at": ["zhangsan"],
    "msgtype": "text",
    "text": {
        "content": "Hello @zhangsan World"
    }
}
```

最终发的消息内容是："Hello @张三 World"。

- 返回结果

| 字段    | 描述                                         |
| ------- | -------------------------------------------- |
| errcode | 错误码，0代表成功                            |
| errmsg  | 错误信息                                     |
| msgids | 发送成功的消息id，结构为`[{"user":"zhangsan","msgid":"123***"}]`或`[{"group":"111***","msgid":"123***"}]` |
| fails   | 发送失败列表，结构同`tousers`或`togroups`。**仅在指定`tousers`或`togroups`时，且有发送失败的用户有效** |
| explains | 解释`fails`失败列表为什么会失败。**该字段仅用于排查问题，业务方不要解析！！！**  |

- 示例: 发给人


```
POST /message/custom/send?appid=123&secret=* HTTP/1.1
Host: alarm.im.qihoo.net
Content-Type: application/json

{
    "tousers": ["zhangsan", "zhangsi"],
    "msgtype": "text",
    "text": {
        "content": "Hello World"
    }
}
```


示例：也可以用 linux curl 命令行做测试发送，或者POSTMAN一类（略）
```
curl -k -X POST -H "Content-Type:application/json" "https://alarm.im.qihoo.net/message/custom/send?appid=***&secret=***" -d "{\"tousers\":[\"zhangsan\",\"zhangsi\"],\"msgtype\":\"text\",\"text\":{\"content\":\"Hello World\"}}"

示例响应：
{
    "trans_id": "2d15a86cd48d898dfbeb8d7c691ea6a6",
    "appid": "******",
    "robot_uid": "765*****",
    "robot_name": "*****",
    "errcode": 0,
    "errmsg": "请求成功",
    "msgids": [{
        "user": "zhangsan",
        "msgid": "7103784****"
        }, {
        "user": "zhangsi",
        "msgid": "7103786****"
    }]
}
```
> 其中，响应的**trans_id**用来排查问题，对接口有疑问可以提供此id供排查

- 示例: 发给群

```
POST /message/custom/send?appid=123&secret=** HTTP/1.1
Host: alarm.im.qihoo.net
Content-Type: application/json

{
    "togroups": ["76526696480*****"],
    "at": ["zhangsan"],
    "msgtype": "text",
    "text": {
        "content": "Hello World"
    }
}
```

## 引用消息

引用消息只支持发文本，因此这是“文本消息”的一种特殊情况。被引用的消息不限制格式例如可以引用一个图片，回复收到。引用消息可用于机器人问答等场景（见《5、机器人收消息》章节），明确机器人回答是哪条消息。

- 消息体对象变动:

| JSON字段          | 描述
| ----------------- | --------------------------
| msgtype           | text |
| tousers           | **数量限制：1人** |
| togroups          | **数量限制：1个群** |
| text.reference_msgid | 引用的消息id，从收消息回调的msgid字段获得 |


- 示例: 发给人

```
POST /message/custom/send?appid=123&secret=* HTTP/1.1
Host: alarm.im.qihoo.net
Content-Type: application/json

{
    "tousers": ["zhangsan"],
    "msgtype": "text",
    "text": {
        "content": "Hello World",
        "reference_msgid": "123456789****"
    }
}
```


- 示例: 发给群

```
POST /message/custom/send?appid=123&secret=** HTTP/1.1
Host: alarm.im.qihoo.net
Content-Type: application/json

{
    "togroups": ["76526696480*****"],
    "at": ["zhangsan"],
    "msgtype": "text",
    "text": {
        "content": "Hello World",
        "reference_msgid": "123456789****"
    }
}
```


## 链接消息

链接消息是发过来一个卡片，带有可选的图/文，点击后可以跳转到指定url

- 消息体对象:

| JSON字段          | 描述                              |
| ----------------- | ----------------------------------|
| msgtype           | link
| tousers           | 见《发送范围》章节|
| togroups          | 见《发送范围》章节|
| link.url               | 必填。点击消息跳转链接。默认点击走客户端内置浏览器打开。在url后面追加 ?target=new&open_window=local ，可以让PC端走外部浏览器打开。注意推推内置浏览器可能存在兼容性问题，如果打开白屏就试试用外部浏览器打开的模式。 |
| link.title             | 标题。会加粗显示。**长度限制：100** ，超出限制将被截断！ |
| link.content           | 摘要（可选）。支持多行。**长度限制：600** ，超出限制将被截断！ |
| link.image             | 配图（可选）。支持jpeg和png格式的外部URL，或者mediaId详见上传文件。|

- 返回结果

同发送文本消息

- 示例数据

```
POST /message/custom/send?appid=123&secret=** HTTP/1.1
Host: alarm.im.qihoo.net
Content-Type: application/json

{
    "tousers": ["zhangsan", "lisi"],
    "msgtype": "link",
    "link": {
        "url": "http://www.test.cn?target=new&open_window=local",
        "title": "测试标题",
        "content": "可选的摘要信息",
        "image": "http://abc.com/image.jpeg"
    }
}
```

示例效果

![](http://p0.qhimg.com/t11098f6bcd5b276296b7527145.png)


## 图片消息

- 接口URL：同发送文本消息
- 消息体对象：

| 字段     | 描述                              |
| -------- | --------------------------------- |
| msgtype  | image                   |
| tousers   | 见《发送范围》章节|
| togroups  | 见《发送范围》章节|
| at | 见《文本消息》章节 |
| image.media_id | 文件ID 见《上传文件》章节 |

- POST示例数据

```
{
    "tousers": ["zhangsan"],
    "msgtype": "image",
    "image": {
        "media_id": "****a6"
    }
}
```


## 图文混排消息

- 接口URL：同发送文本消息
- 消息体对象：

| 字段     | 描述                              |
| -------- | --------------------------------- |
| msgtype  | mixed                   |
| tousers   | 见《发送范围》章节 |
| togroups  | 见《发送范围》章节 |
| at | 见《文本消息》章节 |
| mixed | object数组，支持多条图文混排 **数组长度限制：10** |

mixed数组中每个object格式：

| 字段     | 描述                              |
| -------- | --------------------------------- |
| type  | text(文本) 或 image(图片) |
| value   | 如果type为text，则value为文本内容，**文本总长度限制：50000**；如果type为image，则value为media_id(文件ID 见《上传文件》章节) |

- POST示例数据

```
{
    "tousers": ["zhangsan"],
    "msgtype": "mixed",
    "mixed": [
        {"type":"text","value":"Hello World"},
        {"type":"image", "value": "****a6"}
    ]
}
```

示例效果

![](http://p0.qhimg.com/t01dd57c6bc1a367825.png)



## 附件消息

表现形式就是发一个文件过来。支持office文件、pdf、txt、html等各种文件格式，**但不能是图片**，图片必须用图片接口发送。

文件上传时注意
- **需要用 type=file 参数上传**
- **带有合适的文件名**，因为文件名在消息内会显示。


- 消息体对象：

| 字段     | 描述                              |
| -------- | --------------------------------- |
| msgtype  | attachment              |
| tousers   | 见《发送范围》章节|
| togroups  | 见《发送范围》章节|
| attachment.media_id | 文件ID 见《上传文件》章节 |


- POST示例数据

```
{
    "tousers": ["zhangsan"],
    "msgtype": "attachment",
    "attachment": {
        "media_id": "**ac"
    }
}
```


## 可交互式消息

- 消息体对象：

| 字段     | 描述                              |
| -------- | --------------------------------- |
| msgtype  | interactive              |
| tousers   | 见《发送范围》章节|
| togroups  | 见《发送范围》章节|
| interactive | 详细字段可参考：[可交互式消息](https://easydoc.soft.360.cn/doc?project=38ed795130e25371ef319aeb60d5b4fa&doc=da9c112a95070e5221257dd1d3c93296&config=title_menu_toc#h1-5%E5%8F%AF%E4%BA%A4%E4%BA%92%E5%BC%8F%E6%B6%88%E6%81%AF%28%E5%BE%85%E5%AE%8C%E5%96%84%29) ，总json长度限制：4KB|



- POST示例数据

```
{
  "tousers": [
    "zhangsan"
  ], 
  "msgtype": "interactive", 
  "interactive": {
    "id": "594ccc6d20e01c077b5c9013", 
    "mobileurl": "https://umapp-qr.lap.360.cn", 
    "url": "https://www.360.com", 
    "head": {
      "text": "这是头部显示文本", 
      "bgcolor": "#fefefe", 
      "tcolor": "#332233"
    }, 
    "body": {
      "content": "这是正文显示内容", 
      "image": "5fa93c96ee9eac5fac6f3d77"
    }, 
    "footer": [
      {
        "text": "底部字段", 
        "rtext": "底部字段的内容"
      }
    ]
  }
}
```


## 页面消息
用户使用角度看，表现形式和链接消息(link)相似。

与链接消息(link)的区别：链接消息你需要有个网站提供url，如果你对安全性要求比较高，发布到外网&鉴权就会有困扰。针对这个问题，推推实现了页面缓存消息(page)，你可以直接发一段html，不需要提供url服务。

另外page消息，推推内置实现了移动端字体适配、暗黑模式适配，业务完全不用操心移动端的效果。APP暗黑模式下字体颜色会自动调整。为了兼容深色模式，建议业务的不要给字体加背景色，也不要使用黑色、白色的字体色，可以使用红色，蓝色等颜色。不然深色模式可能看不清楚。

- 消息体对象:

| JSON字段      | 描述                                                         |
| ------------- | ------------------------------------------------------------ |
| msgtype       | page                                                         |
| tousers       | 见《发送范围》章节                                           |
| togroups      | 见《发送范围》章节                                           |
| page.title         | 标题，必填。会加粗显示。**长度限制：100** ，超出限制将被截断！ |
| page.summary       | （可选）简介。支持多行。**长度限制：600** ，超出限制将被截断！ |
| page.content       | 正文，必填。格式需为html。**长度限制：100KB** ，超出限制将报错！ |
| page.image         | （可选）配图。支持jpeg和png格式的外部URL，或者mediaId详见上传文件。 |
| page.format        | （可选）content格式，默认html。目前只支持html                        |
| page.privilege     | （可选）权限控制，可选项有：specific、scope、corp、any。<br/>- specific: 默认值。给指定的人或群成员看，即参数中的tousers或togroups(群成员)；<br/>- scope: 给机器人配置的可见范围的人看，如果机器人可见范围只有一个部门，则只有该部门的成员可查看该消息；<br/>- corp: 给机器人所在组织（公司）的所有成员看，不给其他组织的人看；<br/>- any: 给任意推推用户看，没有权限认证（需单独联系我们申请） |
| page.delims_left   | （可选）默认空代表不进行指令渲染。如果想做指令渲染，则必须和delims_right都填写了，才能让渲染指令生效。比如你想显示访问者名字，可以将delims_left传"{{"，将delims_right传"}}"，假设张三访问该页面时，会将页面html中的{{tuitui_visitor_name}}替换为“张三”。具体见后面渲染指令的解释 |
| page.delims_right  | （可选）需要和delims_left配对使用，比如可以设置为'{{}}'、'<<>>'、'[[]]'、'(())'等等，如果delims_left和delims_right字段为空，指令渲染不会生效。 |
| page.kv            | （可选）json object，用户请求时，推推渲染页面用{{tuitui_page_kv "key"}}指令替换此处文本。 |
| page.default_value | （可选）如果kv没有命中，{{tuitui_page_kv "key"}}指令用该值替换文本。 |
| page.debug         | （可选）true/false，是否开始调试模式。当网页渲染失败，debug标志决定是否显示错误详情，**仅用于开发阶段调试，正式发布请关闭debug模式**  |

- 推推页面渲染指令清单，假设delims为{{ 与 }}

| 指令名                    | 参数     | 示例                                                         | 指令含义                                                 |
| ------------------------- | -------- | ------------------------------------------------------------ | -------------------------------------------------------- |
| tuitui_visitor_name       | 无       | {{tuitui_visitor_name}}                                      | 页面访问者姓名，当privilege为any时无效                   |
| tuitui_visitor_account    | 无       | {{tuitui_visitor_account}}                                   | 页面访问者域账号，当privilege为any时无效                 |
| tuitui_visitor_avatar     | 无       | <image src='{{tuitui_visitor_avatar}}'>                   | 页面访问者头像，当privilege为any时无效                   |
| tuitui_visitor_email      | 无       | <a href='mailto:{{tuitui_visitor_email}}'>发邮件给我</a> | 页面访问者邮箱，当privilege为any时无效                   |
| tuitui_visitor_mobile     | 无       | {{tuitui_visitor_mobile}}                                    | 页面访问者手机号，当privilege为any时无效                 |
| tuitui_visitor_gender     | 无       | {{tuitui_visitor_gender}}                                    | 页面访问者性别，当privilege为any时无效                   |
| tuitui_visitor_department | 无       | {{tuitui_visitor_department}}                                | 页面访问者部门，当privilege为any时无效                   |
| tuitui_visitor_vpn_user   | 无       | {{tuitui_visitor_vpn_user}}                                  | 页面访问者VPN账号，当privilege为any时无效                |
| tuitui_visitor_ip         | 无       | {{tuitui_visitor_ip}}                                        | 页面访问者来源IP，当privilege为any时无效                 |
| tuitui_user_name          | 域账号   | {{tuitui_user_name "zhangsan"}}                              | 获取用户姓名                                             |
| tuitui_user_avatar        | 域账号   | <image src='{{tuitui_user_avatar "zhangsan"}}'>           | 获取用户头像                                             |
| tuitui_user_email         | 域账号   | <a href='mailto:{{tuitui_user_email "zhangsan"}}'>发邮件给张三</a> | 获取用户邮箱                                             |
| tuitui_user_department    | 域账号   | {{tuitui_user_department "zhangsan"}}                        | 获取用户部门（此处只显示用户所在部门，不显示整体部门树） |
| tuitui_robot_name         | 无       | {{tuitui_robot_name}}                                        | 该消息发送机器人名字                                     |
| tuitui_robot_desc         | 无       | {{tuitui_robot_desc}}                                        | 该消息发送机器人描述                                     |
| tuitui_contact            | 域账号   | <a href='{{tuitui_contact "zhangsan"}}'>在推推中联系张三</a> | 在推推中联系张三，点击该链接会跳转到与张三的推推聊天页   |
| tuitui_image              | media_id | <image src='{{tuitui_image "5e8727b4ee9eac7315175833"}}'> | 获取图片URL                                              |
| tuitui_file               | media_id | <a href='{{tuitui_file "5e8727b4ee9eac7315175833"}}'>下载</a> | 获取文件下载URL                                          |
| tuitui_page_kv            | key      | {{tuitui_page_kv "key"}}                                     | 获取发消息时预定义的value of key                         |



- 示例请求

```
POST /message/custom/send?appid=123&secret=*** HTTP/1.1
Host: alarm.im.qihoo.net
Content-Type: application/json

{
    "tousers": ["zhangsan"],
    "msgtype": "page",
    "page": {
        "title": "卡片标题，50个字符限制",
        "summary": "卡片摘要",
        "image": "卡片配图，见文件上传，此处为media_id",
        "content": "点击后显示的正文，html格式",
    }
}
```


- 示例返回

```json
{
  "trans_id": "006ab7b7f2a0019daee4e4df850b6237", 
  "appid": "1", 
  "robot_uid": "123456", 
  "robot_name": "机器人名字", 
  "robot_desc": "机器人描述", 
  "errcode": 0, 
  "errmsg": "请求成功", 
  "msgids": [
    {
      "user": "zhangsan", 
      "msgid": "7135289229751353391"
    }
  ], 
  "page_id": "DHvh2rZXZCQ8" // 修改消息时可用该page_id修改页面
}
```


示例效果

![](http://p0.qhimg.com/t11098f6bcd5b276296b7527145.png)



**大批量推送page消息**

因为有`tousers`100个的限制，不能一次性发给大量的用户。这种情况下，可以将页面权限设置为`scope`或`corp`，在第一批发送成功后，用返回的`page_id`继续推送剩下的人，可提高推送速度

- 请求示例：

```json
POST /message/custom/send?appid=123&secret=*** HTTP/1.1
Host: alarm.im.qihoo.net
Content-Type: application/json

{
    "tousers": ["zhangsan", "lisi"],
    "msgtype": "page",
    "page": {
        "page_id": "DHvh2rZXZCQ8"
    }
}
```

当然，用`page_id`继续推送时，不能修改该页面的任何信息。


## 强通知消息

**注1：该接口需要申请权限使用，如有业务需要，请联系我们。**

**注2：该接口开通后默认允许发出100条强通知/天，如业务需要调整上限，请联系我们。**

- 接口：`POST /strongNotice/single/send`
- Content-Type: `application/json`
- 消息体对象:

| JSON字段      | 描述                                                         |
| ------------- | ------------------------------------------------------------ |
| account       | 见《发送范围》章节 |
| content         | 强通知内容。**长度限制：50000** （一个中文字符长度为1），超出限制将被截断！ |
| sms_notice       | 值：true/false，如果超过1分钟未接收强通知，将发短信提醒 |
| call_notice       | 值：true/false，如果超过1分钟未接收强通知，将打电话提醒 |


- 返回结果

```json
{
  "trans_id": "006ab7b7f2a0019daee4e4df850b6237", 
  "appid": "1", 
  "robot_uid": "123456", 
  "robot_name": "机器人名字", 
  "robot_desc": "机器人描述", 
  "errcode": 0, 
  "errmsg": "请求成功"
}
```

- 示例数据

```
POST /strongNotice/single/send?appid=123&secret=** HTTP/1.1
Host: alarm.im.qihoo.net
Content-Type: application/json

{
    "account": "zhangsan",
    "content": "您好，我有急事找您",
    "sms_notice": false,
    "call_notice": false
}
```


## 团队帖子(HTML)

- 消息体对象:

| JSON字段 | 描述                                                         |
| -------- | ------------------------------------------------------------ |
| msgtype  | richtext/html                                                |
| toteams  | 数组，如：[{"team_id":"139437582835515396","channel_id":"139437582835515397","parent_id":"150465353749626947","tags":["334894487845455592"]}]<br/>参数解释：team_id团队ID，可在推推团队管理页面获取；channel_id频道ID，可在推推频道管理页面获取；parent_id父帖ID，可选字段，有该字段时表示回复该帖子，没有该字段时表示发新帖子；tags帖子关联标签组，可选字段。 |
| richtext | {"html":"你的富文本","delims_left":"","delims_right":""}<br/>参数解释：html帖子内容，html由业务方生成；delims_left和delims_right是可选字段，必须成对出现，如"{{"和"}}"，用于调用推推html页面渲染指令（具体指令见下文）。 |

- 帖子渲染指令

| 指令名        | 参数     | 示例                                                         | 指令含义        |
| ------------- | -------- | ------------------------------------------------------------ | --------------- |
| tuitui_image  | media_id | <image src='{{tuitui_image "5e8727b4ee9eac7315175833"}}'>  | 获取图片URL     |
| tuitui_file   | media_id | <a href='{{tuitui_file "5e8727b4ee9eac7315175833"}}'>下载</a> | 获取文件下载URL |
| tuitui_at     | account  | {{tuitui_at "域账号"}}                                       | 帖子@功能       |
| tuitui_at_tag | tag_id  | {{tuitui_at_tag "1234567"}}                                       | 帖子@标签功能       |
| tuitui_at_all | 无       | {{tuitui_at_all}}                                            | 帖子@所有人功能 |

**tag_id来源：**见接口[/teams/tags/list](https://easydoc.soft.360.cn/doc?project=38ed795130e25371ef319aeb60d5b4fa&doc=b0421279764cea6a7ac2f300afd09ce9&config=title_menu_toc)

- 返回结果

| 字段    | 描述              |
| ------- | ----------------- |
| errcode | 错误码，0代表成功 |
| errmsg  | 错误信息          |
| fails   | 发送失败团队列表，结构同参数`toteams`  |
| explains | 解释`fails`失败列表为什么会失败。**该字段仅用于排查问题，业务方不要解析！！！**  |

- 请求示例

```
POST /message/custom/send?appid=***&secret=****** HTTP/1.1
Host: alarm.im.qihoo.net
Content-Type: application/json

{
    "toteams": [{
        "team_id": "139437582835515396",
        "channel_id": "139437582835515397"
    }],
    "msgtype": "richtext/html",
    "richtext": {
        "html": "请 {{tuitui_at \"zhangsan\"}} 看一下这个图: <br><span class=tt-editor-image><img src={{tuitui_image \"6743b832e2338c3c79edec32\"}} /></span>",
        "delims_left": "{{",
        "delims_right": "}}"
    }
}
```

- 返回结果

```
{
    "trans_id": "006ab7b7f2a0019daee4e4df850b6237",
    "appid": "1",
    "robot_uid": "123456",
    "robot_name": "机器人名字",
    "robot_desc": "机器人描述",
    "errcode": 0,
    "errmsg": "请求成功",
    "post_ids": [
        {
            "team_id": "437582835515396",
            "channel_id": "437582835515397",
            "post_id": "355528030454219"
        }
    ]
}
```

- xss检测规则
    - 不允许的标签：<!DOCTYPE>, html, head, title, meta, body, script, noscript, style, iframe, link；
    - 不允许的标签属性：action和以on开头的，比如onclick等；
    - 不允许的标签属性值：类似`javascript:xxx`和`hidden`；
    - 当使用标签内style属性时，属性值不允许使用以下值和函数：expression(), regex(), display:none。


**html中，可引用推推CSS，使得页面风格与推推一致，并且支持推推的原生能力**
推推的css以tt-editor开头
- 引用推推链接样式 ```<a href=... target=_blank class=tt-editor-link>```
- 引用推推图片样式，这样才能支持图片查看器、发大图必备：```<span class=tt-editor-image><img src="{{tuitui_image "6743b832e2338c3c79edec32"}}"></span>```
- 等其他样式


## 团队帖子(Markdown)

在团队中，支持发送markdown帖子。并且支持带有部分html标签，比如颜色、表格等。

- 消息体对象:

| JSON字段 | 描述                                                         |
| -------- | ------------------------------------------------------------ |
| msgtype  | richtext/markdown                                                |
| toteams  | 参考html消息 |
| richtext | {"markdown":"你的富文本"}，支持可选的delims_left和delims_right相关指令，见html帖子 |

- 请求示例

```
POST /message/custom/send?appid=***&secret=****** HTTP/1.1
Host: alarm.im.qihoo.net
Content-Type: application/json

{
    "toteams": [
        {
            "team_id": "139437582835515396",
            "channel_id": "139437582835515397"
        }
    ],
    "msgtype": "richtext/markdown",
    "richtext": {
        "markdown": "# 计划\n- 步骤1\n- <font color=red>步骤2</font>"
    }
}
```

## 上传文件

上传文件。类型包括：图片、音/视频、office文件等格式，获得media_id用于发送图文消息、附件消息。


|       |   说明
| :---  | :-----
| 域名  | https://alarm.im.qihoo.net
| 协议  | HTTPS/HTTP都支持。建议走https
| 方法  | POST 
| 接口  | /media/upload?appid=xx&secret=xx&type={TYPE}
| Content-Type | multipart/form-data


| 字段 | 必填 |  说明
| :---  | :----- | :-----
| appid、secret | 是| URL参数，必选字段，具体见鉴权
| type         | 否       | URL参数，文件类型。默认值为图片（image）、其他格式文件（file）   |
| media        | 是       | 按multipart/form-data规范的字段名，参考示例。【大小限制：10MB】|


- response对象：

| 字段     | 描述                                                |
| -------- | --------------------------------------------------- |
| errcode  | 错误码，0代表成功                                   |
| filename | 文件名，没什么意义                                  |
| media_id | 资源文件ID，可用于发其他消息 |

- 请求示例

```
用CURL命令行上传当前目录下 123.png 文件例子

curl -v "https://alarm.im.qihoo.net/media/upload?appid=123&secret=**&type=image" -F "media=@123.png"

```
请求协议
```
POST /media/upload?appid=123&secret=**&type=image HTTP/1.1
Host: alarm.im.qihoo.net
User-Agent: curl/7.55.1
Accept: */*
Content-Length: 44093
Expect: 100-continue
Content-Type: multipart/form-data; boundary=------------------------3e60d5e8697fd004

HTTP/1.1 100 Continue

--------------------------3e60d5e8697fd004
Content-Disposition: form-data; name="media"; filename="123.png"
Content-Type: application/octet-stream

（略）
```


成功返回：
```
{
    "errcode": 0,
    "errmsg": "",
    "filename": "123.png",
    "media_id": "********a4"
}
```



### 查询文件

查询文件。用上传文件返回的media_id，获取 **临时** 下载URL。


|       |   说明
| :---  | :-----
| 域名  | https://alarm.im.qihoo.net
| 协议  | HTTPS/HTTP都支持。建议走https
| 方法  | POST 
| 接口  | /media/fetch?appid=xx&secret=xx
| Content-Type | application/json


| 字段 | 必填 |  说明
| :---  | :----- | :-----
| appid、secret | 是| URL参数，必选字段，具体见鉴权
| media_ids        | 是       | 要查询的文件id列表，限制100个 |

- response对象：

| 字段     | 描述                                                |
| -------- | --------------------------------------------------- |
| errcode  | 错误码，0代表成功                                   |
| media_url | 资源文件 **临时** 下载URL，临时使用，不可长期使用！ |

- 请求示例

```
curl -v "https://alarm.im.qihoo.net/media/fetch?appid=123&secret=**" -d '{"media_ids": ["84965011b8798baa03252437"]}'
```

成功返回：
```
{
    "errcode": 0,
    "errmsg": "",
    "media_url": {"84965011b8798baa03252437": "https://xxx"}
}
```






## 电话报警

电话报警表现形式就是用公共号码给被叫人打电话，电话接通后，有机器播报的语音。

主要用作业务夜间故障报警用途。

目前语音播报模板：`服务端报警，报警资源名${message}，详情请查看相关信息`。

模板不可修改，业务方只可以修改其中${message}部分。注意${message}尽量不要用原始的详细报错内容，因为可能会命中电话供应商的关键词黑名单导致发不出去。建议填一个固定的业务名就可以了。同时建议用推推/邮件发送一份文字版本的报警，电话只是起到一个提醒去看的作用。

### 计费
每呼叫5分钱。为集团业务方便，目前优惠政策为每个业务每月 2000 次免费呼叫（即月费用低于百元免收费）；量大会进行业务结算。

### 发送电话报警

- 接口URL：同发送文本消息
- 消息体：JSON对象(**结构见示例**)：

| 字段    | 描述               |
| ------- | ------------------ |
| msgtype | voice              |
| tousers | 见《发送范围》章节 |
| voice.mobiles | 电话号码列表，数组格式，**数量限制：20** |
| voice.message | 报警内容           |

说明：
> - 常见用法发送目标是推推用户，直接传 tousers 就可以了，不需要传voice.mobiles手机号，也不需要知道用户手机号
> - 有些特殊情况不是发给推推用户，而是直接发给例如外部用户外部租户，这种情况不传tousers，只传voice.mobiles电话号码列表。

常见问题说明：
> - 手机收不到报警电话：手机可能带有来电拦截功能，建议将以下2个报警号码加白：021-22797274、0575-89593887；
> - 被叫号触发被叫流控：每个被叫号码被叫限制为1次/分钟、10次/小时、100次/天，业务可自查是否呼叫频繁，触发流控。

- 返回结果

| 字段    | 描述         |
| ------- | ------------ |
| errcode | 错误码       |
| errmsg  | 错误信息     |
| voice   | 语音呼叫结果 |

- 示例数据

```
{
    "msgtype": "voice",
    "voice": {
        "mobiles": ["136xxxxxxxx"],
        "message": "报警内容"
    }
}
```

- 返回数据

```
{
    "errcode":0,
    "errmsg":"请求成功",
    "voice":[
        {
            "mobile":"136xxxxxxxx",
            "success":true,
            "call_id":"119211000050^10331221050"
        }
    ]
}
```



### 查询电话报警

查询电话接听状态

|       |   说明
| :---  | :-----
| 域名  | https://alarm.im.qihoo.net
| 协议  | HTTPS/HTTP都支持。建议走https
| 方法  | GET
| 接口  | /message/voice/detail?appid=123&secret=**&call_id=xxx
| call_id | 呼叫id 


**接口限制：100次/min**

- 示例请求

```
curl http://alarm.im.qihoo.net/message/voice/detail?appid=123&secret=**&call_id=119211000050^10331221050
```

- 返回结果

```
{
    "errcode":0,
    "errmsg":"请求成功",
    "detail":{
        "call_id":"119515645682^106311895682",
        "callee":"136xxxxxxxx", // 被叫号码
        "callee_show_number":"051068514987", // 被叫显号
        "state":"200000", // 通话状态
        "state_desc":"用户接听", // 通话状态描述
        "gmt_create":"2020-05-07 10:27:52", // 通话请求的接收时间
        "start_date":"2020-05-07 10:28:04", // 呼叫开始时间
        "end_date":"2020-05-07 10:28:11", // 呼叫结束时间
        "duration":7 // 通话时长，单位：秒
    }
}
```

- state描述：

| state  | state_desc       |
| ------ | ---------------- |
| 200    | 外呼任务提交成功 |
| 200000 | 用户接听         |
| 200005 | 用户无法接通     |


# 4、修改消息

## 修改消息接口

| 请求         | 说明                                                         |
| :----------- | :----------------------------------------------------------- |
| 域名         | https://alarm.im.qihoo.net                                   |
| 协议         | HTTPS/HTTP都支持。建议走https                                |
| 方法         | POST                                                         |
| 接口         | /message/custom/modify?appid=123&secret=** |
| appid、secret | URL参数，必选字段，见鉴权|
| Content-Type | application/json                                             |
| Body         | json格式，见下文                                             |

- 返回结果

| 字段    | 描述                                         |
| ------- | -------------------------------------------- |
| errcode | 错误码，0代表成功                            |
| errmsg  | 错误信息                                     |
| fails   | 修改失败列表，结构同`tousers`或`togroups`。 |
| explains | 解释`fails`失败列表为什么会失败。**该字段仅用于排查问题，业务方不要解析！！！**  |

修改消息请求Body格式示例：


```bash
curl -H 'Content-Type: application/json' 'https://alarm.im.qihoo.net/message/custom/modify?appid=123&secret=**' -d '{
  "togroups": [{"group":"7723****1966","msgid":"5678****1234"}],
  "msgtype": "text",
  "text":{"content":"hollow knight"}
}'
# 返回结果如下：
{
  "trans_id": "ae45****e872", 
  "appid": "***", 
  "robot_uid": "****", 
  "robot_name": "******", 
  "robot_desc": "******", 
  "errcode": 0, 
  "errmsg": "请求成功", 
  "success": [
    {
      "group": "7723****1966", 
      "msgid": "5678****1234"
    }
  ]
}
```

## 修改范围

支持修改机器人发送的单人或者群消息，在修改消息请求body中json字段指定。以下tousers/togroups必填其一，且只能填一种，不只持人群混改。

| 范围         | 参数     | 说明                                                |
| ------------ | -------- | --------------------------------------------------- |
| 修改单聊消息 | tousers  | 格式为数组`[{"user":"account","msgid":"消息ID"}]`   |
| 修改群聊消息 | togroups | 格式为数组`[{"group":"group_id","msgid":"消息ID"}]` |

#### 关于`msgid`的来源：

发送单聊消息返回结果

```bash
curl -H 'Content-Type: application/json' 'https://alarm.im.qihoo.net/message/custom/send?appid=123&secret=**' -d '{
  "tousers": ["account_1", "account_2"],
  "msgtype": "text",
  "text":{"content":"hello world"}
}'
# 返回结果如下：
{
  "trans_id": "13fd****04fe", 
  "appid": "***", 
  "robot_uid": "***", 
  "robot_name": "***", 
  "robot_desc": "***", 
  "errcode": 0, 
  "errmsg": "请求成功", 
  "msgids": [{
      "user": "account_1", 
      "msgid": "1234****5678" // 单聊消息ID
  }, {
      "user": "account_2", 
      "msgid": "4321****8765" // 单聊消息ID
  }]
}
```

发送群聊消息返回结果


```bash
curl -H 'Content-Type: application/json' 'https://alarm.im.qihoo.net/message/custom/send?appid=123&secret=**' -d '{
  "togroups": ["7723****1966"],
  "msgtype": "text",
  "text":{"content":"hello world"}
}'
# 返回结果如下：
{
  "trans_id": "13fd****04fe", 
  "appid": "***", 
  "robot_uid": "***", 
  "robot_name": "***", 
  "robot_desc": "***", 
  "errcode": 0, 
  "errmsg": "请求成功", 
  "msgids": [{
      "group": "7723****1966", 
      "msgid": "5678****1234" // 群聊消息ID
  }]
}
```

**注：**本接口和`发送消息接口`，只有`tousers`和`togroups`字段不同，其余字段完全相同（参考上述示例和第3章《发送消息类型》）。

消息类型支持：

- 文本消息
- 链接消息
- 图片消息
- 图文混排消息
- 附件消息


## 撤回消息

| JSON字段 | 描述               |
| -------- | ------------------ |
| msgtype  | recall             |
| tousers  | 见《修改范围》章节 |
| togroups | 见《修改范围》章节 |

示例：

```bash
curl -H 'Content-Type: application/json' 'https://alarm.im.qihoo.net/message/custom/modify?appid=123&secret=**' -d '{
  "tousers": [
    {"user": "account_1", "msgid": "1234****5678"},
    {"user": "account_2", "msgid": "4321****8765"}
  ],
  "msgtype": "recall"
}'
# 返回结果如下：
{
  "trans_id": "ae45****e872", 
  "appid": "***", 
  "robot_uid": "****", 
  "robot_name": "******", 
  "robot_desc": "******", 
  "errcode": 0, 
  "errmsg": "请求成功", 
  "success": [
    {"user": "account_1", "msgid": "1234****5678"},
    {"user": "account_2", "msgid": "4321****8765"}
  ]
}
```

## 修改消息不发厂商推送

在某些业务场景下，修改消息后，不需要修改移动端的厂商推送消息。比如在PC端审批消息后，可以选择不给移动端推送消息，避免手机响铃。

使用方式：在请求的json中加入`"without_push": true`，如下：

| JSON字段 | 描述               |
| -------- | ------------------ |
| without_push  | true/false 是否需要推送厂商推送  |

```bash
curl -H 'Content-Type: application/json' 'https://alarm.im.qihoo.net/message/custom/modify?appid=123&secret=**' -d '{
  "togroups": [{"group":"7723****1966","msgid":"5678****1234"}],
  "msgtype": "text",
  "text":{"content":"hollow knight"},
  "without_push": true
}'
```




## 修改推推页面消息

### 修改卡片展示信息

仅修改推推消息卡片展示样式，不修改页面内容：

| JSON字段 | 描述                                                         |
| -------- | ------------------------------------------------------------ |
| msgtype  | page                                                         |
| tousers  | 见《发送范围》章节                                           |
| togroups | 见《发送范围》章节                                           |
| page.page_id  | 必填，发消息时返回的页面唯一id                               |
| page.title    | 标题。会加粗显示。**长度限制：100** ，超出限制将被截断！ |
| page.summary  | 简介（可选）。支持多行。**长度限制：600** ，超出限制将被截断！ |
| page.image    | 配图（可选）。支持jpeg和png格式的外部URL，或者mediaId详见上传文件。 |

- 请求示例：

```json
POST /message/custom/modify?appid=123&secret=** HTTP/1.1
Host: alarm.im.qihoo.net
Content-Type: application/json

{
    "tousers": [{"user":"zhangsan","msgid":"12345"}, {"user":"lisi","msgid":"67890"}],
    "msgtype": "page",
    "page": {
        "page_id": "DHvh2rZXZCQ8",
        "title": "50个字符限制",
        "summary": "卡片上显示的正文",
        "image": "见文件上传，此处为media_id"
    }
}
```





### 修改页面内容

反过来，如果仅需修改页面内容，不修改消息卡片展示样式，可以用这个：

| JSON字段      | 描述                                                         |
| ------------- | ------------------------------------------------------------ |
| msgtype       | page                                                         |
| page.page_id       | 必填，发消息时返回的页面唯一id                               |
| page.content       | 正文，必填。格式需为html。**长度限制：100KB** ，超出限制将报错！ |
| page.format        | content格式，默认html。目前只支持html                        |
| page.delims_left   | 和delims_right一起生效。如果需要渲染content的内容，需要将渲染的内容用delims包围起来，比如需要根据访问者渲染页面，可以将delims_left设为'{{'，将delims_right设为'}}'，访问者用{{tuitui_visitor_name}}表示。假设张三访问该页面时，会将页面中的{{tuitui_visitor_name}}替换为“张三”。 |
| page.delims_right  | 需要和delims_left配对使用，比如可以设置为'{{}}'、'<<>>'、'[[]]'、'(())'等等，如果delims_left和delims_right字段为空，推推将不进行渲染。 |
| page.kv            | json object，用户请求时，推推渲染页面用{{tuitui_page_kv "key"}}指令替换此处文本。 |
| page.default_value | 如果kv没有命中，{{tuitui_page_kv "key"}}指令用该值替换文本。 |
| page.debug         | true/false，是否开始调试模式。当打开调试模式后，如果推推渲染网页失败，会将渲染错误信息显示出来。**正式发布信息时请一定关闭调试模式！** |

以上，除`msgtype`和`page_id`以外，均为非必填参数，不填的参数将保持原样不变。**注：**不需要填`tousers`和`togroups`，且不支持权限修改。

- 请求示例：

```json
POST /message/custom/modify?appid=123&secret=** HTTP/1.1
Host: alarm.im.qihoo.net
Content-Type: application/json

{
    "msgtype": "page",
    "page": {
        "page_id": "DHvh2rZXZCQ8",
        "content": "HTML内容"
    }
}
```



### 同时修改

接口`/message/custom/modify`支持同时修改卡片展示信息和链接页面内容。



### 删除页面

如果页面内容发布错误，需要删除该页面，可以调`/message/custom/modify`接口删除该页面：

| JSON字段 | 描述                           |
| -------- | ------------------------------ |
| msgtype  | page                           |
| page.page_id  | 必填，发消息时返回的页面唯一id |
| page.delete   | true，表示需要删除该页面       |

- 请求示例：

```json
POST /message/custom/modify?appid=123&secret=** HTTP/1.1
Host: alarm.im.qihoo.net
Content-Type: application/json

{
    "msgtype": "page",
    "page": {
        "page_id": "DHvh2rZXZCQ8",
        "delete": true
    }
}
```

页面删除后，客户端点击链接卡片进来，将看到`HTTP 404 Not Found`错误。



### 撤回并删除

如果需要撤回推推上的卡片消息，可查看《撤回消息》章节。

由于消息撤回后，页面还在，如果用户留有页面链接，客户端仍然可以通过链接进入查看页面内容。

因此，如果在撤回`page`消息时，一并删除页面（客户端访问页面将返回`HTTP 404 Not Found`错误），可以在撤回时，带上`page_id`参数：

| JSON字段 | 描述                           |
| -------- | ------------------------------ |
| msgtype  | recall                         |
| tousers  | 见《修改范围》章节             |
| togroups | 见《修改范围》章节             |
| page.page_id  | 必填，发消息时返回的页面唯一id |

- 请求示例：

```bash
curl -H 'Content-Type: application/json' 'https://alarm.im.qihoo.net/message/custom/modify?appid=123&secret=**' -d '{
  "tousers": [
    {"user": "account_1", "msgid": "1234****5678"},
    {"user": "account_2", "msgid": "4321****8765"}
  ],
  "msgtype": "recall",
  "page": {
    "page_id": "DHvh2rZXZCQ8"
  }
}'
```


## 修改团队帖子

api变为`/message/custom/modify`，将上节“发送团队帖子”的返回结果，放在`toteams`参数中，其它不变。

**注：**如果帖子关联标签，需要在`toteams`参数中，带上`tags`参数，详见《3、发消息类型/团队帖子(HTML)》章节。

- 请求示例：

```
POST /message/custom/modify?appid=***&secret=****** HTTP/1.1
Host: alarm.im.qihoo.net
Content-Type: application/json

{
    "toteams": [
        {
            "team_id": "139437582835515396",
            "channel_id": "139437582835515397",
            "post_id": "159355528030454219"
        }
    ],
    "msgtype": "richtext/html",
    "richtext": {
        "html": "{{tuitui_at \"zhangsan\"}} 已恢复",
        "delims_left": "{{",
        "delims_right": "}}"
    }
}
```



# 5、机器人收消息

收消息，是指机器人可以接收单聊、群聊消息，并可以回复，用于人机对话。

## 收消息回调url

收消息回调url，又叫Outgoing webhook。如果机器人收到了消息，推推后台会把消息通过http post给这个url。这个url由业务方提供开发并维护，能用ip或域名访问都可以。


## 如何开通

- 首先，你需要先开通机器人权限，拿到appid/secret
- 见【机器人自助修改接口】中的文档，自助修改回调url
- 开通后建议先拉个小群测试，等测试通过后，再把机器人拉到正式服务的群中。以免测试过程中对其他人打扰

## 安全身份验证

为了防止你的webhook被恶意调用，一般可以用https 且 webhook url中增加密钥串参数的方式来简单实现。

如果需要更严格的安全验证，可以进一步做如下工作：
- 通过 checksum 能验证webhook内容是推推发起的
- 通过 nonce + Timestamp能解决重放安全问题（如果你有需求的话）

推推在回调url时，会在http请求头中增加以下鉴权字段：
```
X-Tuitui-Robot-Appid: 机器人的appid
X-Tuitui-Robot-Timestamp: 毫秒级时间戳
X-Tuitui-Robot-Nonce: 回调唯一标识
X-Tuitui-Robot-Checksum: 鉴权字段=sha1(app_secret + timestamp + nonce + post的json_body)
```

示例：
假设机器人appid="1234567"，secret="0123456789abcdef0123456789abcdef01234567"，某次回调的json为"{}"，完整回调HTTP为：

```
POST /your/outgoing/webhook/api HTTP/1.1
Host: your.hostname:port
Content-Type: application/json; charset=utf8
X-Tuitui-Robot-Appid: 1234567
X-Tuitui-Robot-Timestamp: 1688378302682
X-Tuitui-Robot-Nonce: e455b35b-62cf-4c5c-a720-0bcefc950120
X-Tuitui-Robot-Checksum: 0b84c156042fd154ab18ef7686864debc1d1ad0c

{}
```

鉴权计算：

```
X-Tuitui-Robot-Checksum = sha1(
  "0123456789abcdef0123456789abcdef01234567"
  + "1688378302682"
  + "e455b35b-62cf-4c5c-a720-0bcefc950120"
  + "{}"
)
```

## 长连接方式收消息

这个方案与webhook区别是，业务方不需要有固定的ip端口，通过主动发起长连接连接至推推服务器来收取消息。

整体流程：

websocket连接至`wss://alarm.im.qihoo.net/callback?auth=<appid>.<secret>`（外网`wss://im.live.360.cn:8282/robot/callback?auth=<appid>.<secret>`）。

连接成功后，推推主动下发机器人收到的消息内容。格式：

```json
{
  "event_id": "唯一id，可用做幂等判断",
  "header": { // 上一章节中“X-Tuitui-Robot-”开头的头部字段
    "X-Tuitui-Robot-Appid": "1234567",
    "X-Tuitui-Robot-Timestamp": "1688378302682",
    "X-Tuitui-Robot-Nonce": "e455b35b-62cf-4c5c-a720-0bcefc950120",
    "X-Tuitui-Robot-Checksum": "0b84c156042fd154ab18ef7686864debc1d1ad0c"
  },
  "body": {} // 见下面《收消息格式》章节
}
```

业务方通过websocket接收到事件后，需要按以下格式回复确认收到消息：

```json
{
  "ack": "下发的event_id值"
}
```

**注意：**当且仅当业务方回复ack后，推推才会下发下一个事件。如果业务方没有回复ack，推推将不断重复下发同一事件。

### 心跳-保持长连在线

推推在websocket空闲时，会下发心跳事件保持websocket长连接在线。心跳事件没有`header`信息，完整格式如下：

```json
{
  "event_id": "e455b35b62cf4c5ca7200bcefc950120",
  "header": {},
  "body": {
    "event": "keepalive"
  }
}
```

业务方收到心跳后，直接回复ack即可：

```json
{
  "ack": "e455b35b62cf4c5ca7200bcefc950120"
}
```

### ack超时

推推主动下发事件后，需要在3秒内收到业务方回复的`ack`消息，如果没有在3秒内收到（业务处理时间过长或网络抖动等原因），推推会将该消息再次下发，直到业务方回复ack为止。重复下发的事件，`event_id`、`header`、`body`均保持一致，业务方可以根据`event_id`字段去重做幂等操作。

### 多个长连接

如果业务方有多个websocket以相同的`auth`参数连接上来：

- 事件下发：随机挑选一个连接下发事件；
- 消息确认：只要任何一个连接ack了当前事件，推推就会开始下发下一事件。

### 消息队列长度限制

推推最多会保存1000条待下发的消息，超过1000条时，删除最早的消息，总保持最多存储1000条限制。

如果机器人超过7天没有收到新消息，推推将销毁该机器人的收消息队列，如果队列中还有业务方没有处理的消息事件，这些事件也将被销毁。

## 收消息格式

机器人收消息格式分为三部分：
- 事件发出者，包括三个主要字段：uid, user_account, user_name；
- 事件：打开与机器人的单聊会话（single_chat_open），单聊（single_chat），群聊（group_chat），建群（group_create），入群（group_invite），踢群成员（group_kick），发/回贴（teams_post_create），改帖（teams_post_modify），频道创建（teams_channel_create）
- 事件内容：根据事件不同，内容结构不同，具体见下面示例

### 打开与机器人的单聊会话


```json
{
    "cid": "7652886633113456",
    "uid": "7652669334456778",
    "user_account": "zhangsan",
    "user_name": "张三",
    "timestamp": "1591337058",
    "event": "single_chat_open" // 打开单聊会话事件
}
```

以上json可以理解为：“张三”打开了与“xxx机器人”的单聊会话。



### 单聊文本：

```json
{
    "cid": "7652886633113456",
    "uid": "7652669334456778",
    "user_account": "zhangsan",
    "user_name": "张三",
    "timestamp": "1591337058",
    "event": "single_chat", // 单聊事件
    "data": {
        "msgid": "123****", // 本条消息的消息id
        "msg_type": "text", // 文本消息类型
        "text": "这条是消息正文"
    }
}
```

以上json可以理解为：“张三”给“xxx机器人”发了一条单聊文本消息。


### 单聊图片：

```json
{
    "cid": "7652886633113456",
    "uid": "7652669334456778",
    "user_account": "zhangsan",
    "user_name": "张三",
    "timestamp": "1591337058",
    "event": "single_chat", // 单聊事件
    "data": {
        "msgid": "123****", // 本条消息的消息id
        "msg_type": "image", // 图片消息类型
        "images": ["https://xxx/file.png"], // 推推支持一次发多张图，所以图片是个下载地址的数组
        "image_ids": ["03f454e08797149c640448ea "] // 图片media_id，可直接拿来用
    }
}
```



### 单聊语音：

```json
{
    "cid": "7652886633113456",
    "uid": "7652669334456778",
    "user_account": "zhangsan",
    "user_name": "张三",
    "timestamp": "1591337058",
    "event": "single_chat", // 单聊事件
    "data": {
        "msgid": "123****", // 本条消息的消息id
        "msg_type": "voice", // 语音消息类型
        "voice": "https://xxx/file.amr", // 语音是一个url，格式是AMR
        "voice_id": "03f454e08797149c640448ea" // 语音文件media_id，可拿来用
    }
}
```


### 单聊文件：

```json
{
    "cid": "7652886633113456",
    "uid": "7652669334456778",
    "user_account": "zhangsan",
    "user_name": "张三",
    "timestamp": "1591337058",
    "event": "single_chat", // 单聊事件
    "data": {
        "msgid": "123****", // 本条消息的消息id
        "msg_type": "file", // 文件消息类型
        "file": {"name":"abc.txt", "url":"https://xxx.txt", "file_id": "03f454e08797149c640448ea"}
    }
}
```


### 单聊引用消息

引用消息在原单群聊消息回调`data`结构中添加`ref`字段，`ref`结构含义保持和`data`内容一致，见以下示例。

**注意：**当且仅当是引用消息时，才有`ref`字段出现。

引用消息支持消息类型有：文本(text)，图片(image)，图文混排(mixed)，文件(file)，语音(voice)。


张三引用机器人的文本消息：

```json
{
    "cid": "7652886633113456",
    "uid": "7652669334456778",
    "user_account": "zhangsan",
    "user_name": "张三",
    "timestamp": "1591337058",
    "event": "single_chat", // 单聊事件
    "data": {
        "msgid": "123****", // 本条消息的消息id
        "msg_type": "text", // 文本消息类型
        "text": "这条是消息正文",
        "ref": {
            "cid": "7652886633113456",
            "uid": "7651234567890123", // 机器人uid
            "user_account": "", // 机器人没有域账号
            "user_name": "机器人名称",
            "is_me": true, // 优先使用该字段判断是否引用的本机器人发的消息，如果被引用消息不是机器人发的，该值为false
            "msgid": "7454***",
            "msg_type": "text",
            "text": "被引用的消息内容"
        }
    }
}
```


张三引用机器人的图片消息：

```json
{
    "cid": "7652886633113456",
    "uid": "7652669334456778",
    "user_account": "zhangsan",
    "user_name": "张三",
    "timestamp": "1591337058",
    "event": "single_chat", // 单聊事件
    "data": {
        "msgid": "123****", // 本条消息的消息id
        "msg_type": "text", // 文本消息类型
        "text": "这条是消息正文",
        "ref": {
            "cid": "7652886633113456",
            "uid": "7651234567890123", // 机器人uid
            "user_account": "", // 机器人没有域账号
            "user_name": "机器人名称",
            "is_me": true, // 是否引用的本机器人发的消息
            "msgid": "7454***",
            "msg_type": "image",
            "images": [
                "https://im.qihoo.net:8989/uploads/wCFG2gGQYXieE01Q0MmpyMmPGEM.jpeg?e=20250111T124715&s=x95rFRj9NNHm-oozWwiIODlDcqd-7nxk_dLRkAwZNrM"
            ],
            "image_ids": [
                "18e5e1f5dd79f414d80d0e59"
            ]
        }
    }
}
```



张三引用**自己**发的文件消息：

```json
{
    "cid": "7652886633113456",
    "uid": "7652669334456778",
    "user_account": "zhangsan",
    "user_name": "张三",
    "timestamp": "1591337058",
    "event": "single_chat", // 单聊事件
    "data": {
        "msgid": "123****", // 本条消息的消息id
        "msg_type": "text", // 文本消息类型
        "text": "这条是消息正文",
        "ref": {
            "cid": "7652886633113456",
            "uid": "7652669334456778", // 张三的uid
            "user_account": "zhangsan",
            "user_name": "张三",
            "is_me": false, // 不是引用的本机器人发的消息
            "msgid": "7454***",
            "msg_type": "file",
            "file": {
                "name": "文件名称",
                "url": "https://xxx", // 临时下载链接
                "file_id": "3ce125*********c643334" // 文件media_id
            }
        }
    }
}
```





### 群聊文本消息：

```json
{
    "cid": "7652886633113456",
    "uid": "7652669334456778",
    "user_account": "zhangsan",
    "user_name": "张三",
    "timestamp": "1679454800",
    "event": "group_chat",
    "data": {
        "group_id": "765261111123456",
        "group_name": "xxx机器人对接测试",
        "at_me": true, // ATTENTION: 优先使用该字段判断有无@机器人。当且仅当该群消息明确有“@xxx机器人”行为时，该字段为true，否则false，也即：@所有人时，不计入“@xxx机器人”行为。如需处理“@所有人”行为，参考"at"字段内容。
        "at": [
            {
                "is_at_all": true,
                "name": "所有人"
            },
            {
                "is_at_all": false, // 仅当该字段为false时，cid, uid, account有效。注：机器人无account
                "cid": "7723038392975868",
                "uid": "7723038392983222",
                "name": "xxx机器人"
            }
        ],
        "msgid": "123****", // 本条消息的消息id
        "msg_type": "text",
        "text": "@所有人 @xxx机器人 "
    }
}
```

以上json可以理解为：“张三”在“xxx机器人对接测试”群里“@了xxx机器人”。

### 群聊图片、语音

参考单聊的data格式。

### 群聊引用消息

- 新增`ref`字段中不含重复的`group_id`、`group_name`信息；
- 新增`ref`字段中不含`at`、`at_me`字段；
- 其余规则和单聊保持一致。

示例：

```json
{
    "cid": "7652886633113456",
    "uid": "7652669334456778",
    "user_account": "zhangsan",
    "user_name": "张三",
    "timestamp": "1679454800",
    "event": "group_chat",
    "data": {
        "group_id": "765261111123456",
        "group_name": "xxx机器人对接测试",
        "at_me": true,
        "at": [
            {
                "is_at_all": true,
                "name": "所有人"
            },
            {
                "is_at_all": false,
                "cid": "7723038392975868",
                "uid": "7723038392983222",
                "name": "xxx机器人"
            }
        ],
        "msgid": "123****",
        "msg_type": "text",
        "text": "@所有人 @xxx机器人 ",
        "ref": {
            "cid": "7723038392975868",
            "uid": "7723038392983222",
            "user_account": "",
            "user_name": "xxx机器人",
            "is_me": true,
            "msgid": "7454440992318908991",
            "msg_type": "text",
            "text": "@张三 机器人at张三的消息"
        }
    }
}
```

### 建群通知

```json
{
    "cid": "7652886633113456",
    "uid": "7652669334456778",
    "user_account": "zhangsan",
    "user_name": "张三",
    "timestamp": "1679454322",
    "event": "group_create",
    "data": {
        "group_id": "765261111123456",
        "group_name": "xxx机器人对接测试",
        "members_contains_me": true, // ATTENTION: 优先使用该字段判断本次群成员变动中，是否包含xxx机器人
        "members": [ // members中不包括群创建人，即“张三”
            {
                "uid": "7723038392983222",
                "name": "xxx机器人" // 机器人没有account
            },
            {
                "uid": "7723038392984678",
                "account": "lisi",
                "name": "李四"
            }
        ]
    }
}
```

以上json可以理解为：“张三”创建了“xxx机器人对接测试”群，群成员有“xxx机器人”和“李四”。

### 群成员加入通知

```json
{
    "cid": "7652886633113456",
    "uid": "7652669334456778",
    "user_account": "zhangsan",
    "user_name": "张三",
    "timestamp": "1679454373",
    "event": "group_invite",
    "data": {
        "group_id": "765261111123456",
        "group_name": "xxx机器人对接测试",
        "members_contains_me": true, // ATTENTION: 优先使用该字段判断本次群成员变动中，是否包含xxx机器人
        "members": [
            {
                "uid": "7723038392983222",
                "name": "xxx机器人"
            }
        ]
    }
}
```

以上json可以理解为：“张三”邀请“xxx机器人”加入了“xxx机器人对接测试”群。

### 踢群成员通知

```json
{
    "cid": "7652886633113456",
    "uid": "7652669334456778",
    "user_account": "zhangsan",
    "user_name": "张三",
    "timestamp": "1679454349",
    "event": "group_kick",
    "data": {
        "group_id": "765261111123456",
        "group_name": "xxx机器人对接测试",
        "members_contains_me": true, // ATTENTION: 优先使用该字段判断本次群成员变动中，是否包含xxx机器人
        "members": [
            {
                "uid": "7723038392983222",
                "name": "xxx机器人"
            }
        ]
    }
}
```

以上json可以理解为：“张三”将“xxx机器人”移出了“xxx机器人对接测试”群。（以后xxx机器人将不再能收到该群消息）

### 团队发帖子、修改帖子、回复帖子事件通知

```json
{
    "cid": "7652886633113456",
    "uid": "7652669334456778",
    "user_account": "zhangsan",
    "user_name": "张三",
    "timestamp": "1679454969",
    "event": "teams_post_create", // 当修改帖子时，event为"teams_post_modify"
    "data": {
        "team_id": "139437582835515396",
        "team_name": "团队名称",
        "channel_id": "139437582835515397",
        "channel_name": "频道名称",
        "is_reply": true, // 是否是回复帖子
        "parent_id": "165044530041585675", // 父帖id，当is_reply为true时，该字段有效
        "post_id": "165307145816899655", // 帖子id
        "content": "帖子简要内容",
        "rich_text_type": "json/v1", // 富文本格式
        "rich_text": "{\"root\":{\"children\":[{\"children\":[{\"detail\":0,\"format\":0,\"mode\":\"normal\",\"style\":\"\",\"text\":\"帖子简要内容\",\"type\":\"text\",\"version\":1}],\"direction\":\"ltr\",\"format\":\"\",\"indent\":0,\"type\":\"paragraph\",\"version\":1}],\"direction\":\"ltr\",\"format\":\"\",\"indent\":0,\"type\":\"root\",\"version\":1}}", // 富文本内容
        "at": [
            {
                "type": "all" // @所有人的情况
            },
            {
                "type": "tag", // @团队标签的情况
                "tag": {
                    "id": "173126443016914493",
                    "name": "标签名",
                    "desc": "标签描述",
                    "members": [
                        {
                            "uid": "7652669648886827",
                            "name": "yyy机器人"
                        }
                    ]
                }
            },
            {
                "type": "user", // @团队成员的情况
                "user": {
                    "uid": "7652807087760056",
                    "name": "xxx机器人" // 机器人没有account字段
                }
            }
        ]
        "at_me": true, // ATTENTION: 优先使用该字段判断有无@机器人。当且仅当该帖子有明确“@xxx机器人”行为时，该字段为true，否则false，也即：“@所有人”或“@团队标签”不计入“@机器人”行为。如果需要处理“@所有人”或者“@团队标签”，参见"at"字段。
    }
}
```

以上json可以理解为：“张三”在“团队名称”的“频道名称”回复了id为“165044530041585675”的帖子，回复内容为“帖子简要内容”。

### 创建团队频道通知

```json
{
    "cid": "7652886633113456",
    "uid": "7652669334456778",
    "user_account": "zhangsan",
    "user_name": "张三",
    "timestamp": "1679457224",
    "event": "teams_channel_create",
    "data": {
        "team_id": "139437582835515396",
        "team_name": "团队名称",
        "channel_id": "165316830968152214",
        "channel_name": "新建频道名称"
    }
}
```

以上json可以理解为：“张三”在“团队名称”创建了“频道名称”。



### 团队信息变更通知

```json
{
    "cid": "7652886633113456",
    "uid": "7652669334456778",
    "user_account": "zhangsan",
    "user_name": "张三",
    "timestamp": "1679457224",
    "event": "teams_team_update",
    "data": {
        "team_id": "139437582835515396",
        "name": "团队名称",
        "desc": "团队描述",
        "logo": "团队头像media_id",
        "logo_url": "团队头像临时下载链接",
        "is_public": false, // 是否是公开团队
        "settings": {
                "create_channel": false, // 仅管理员可以创建频道
                "add_member": true, // 仅管理员可以添加成员
                "add_tab": false, // 仅管理员可配置选项卡
                "share_post": false, // 仅管理员可分享帖子
        },
        "channels_order": {
                "channel_id_0": 0, // 频道id -> 排序序号，序号按从小到大序
                "channel_id_1": 1
        } // 频道排序
    }
}
```



### 删除团队通知

```json
{
    "cid": "7652886633113456",
    "uid": "7652669334456778",
    "user_account": "zhangsan",
    "user_name": "张三",
    "timestamp": "1679457224",
    "event": "teams_team_delete",
    "data": {
        "team_id": "139437582835515396"
    }
}
```




### 团队成员变动通知

```json
{
    "cid": "7652886633113456",
    "uid": "7652669334456778",
    "user_account": "zhangsan",
    "user_name": "张三",
    "timestamp": "1679457224",
    "event": "teams_member_add", // 或 teams_member_remove 表示添加新成员或踢除成员，teams_member_set表示团队成员角色变更
    "data": {
        "team_id": "139437582835515396",
        "team_name": "团队名称",
        "members": [{
            "uid": "7723038392984678",
            "account": "lisi",
            "name": "李四"
        }]
    }
}
```

以上json可以理解为：“张三”将“李四”拉进（或踢出）“团队”。



## 收消息格式（旧格式）

为保持和原有收消息格式兼容（不保证完全兼容），以上新收消息格式中会有以下冗余字段：

消息是json格式。文本例子
```
{
    "cid":"7652886633113456",
    "uid":"7652669334456778",
    "user_account":"zhangsan",
    "user_name":"张三",
    "group_id":"765261111123456",
    "group_name":"xxx机器人对接测试",
    "msgtype":"text",
    "text":"这条是消息正文",
    "origin_text":"这条是引用消息",
    "trigger_word":"",
    "timestamp":"1591337058"
}
```

图片例子：
```json
{
  "cid": "7652886633113456", 
  "uid": "7652669334456778", 
  "user_account": "zhangsan", 
  "user_name": "张三", 
  "group_id": "", 
  "group_name": "", 
  "msgtype": "image", 
  "text": "", 
  "origin_text": "", 
  "trigger_word": "", 
  "images": [
    "https://www.file.com/xxx"
  ], 
  "timestamp": "1639388207"
}
```

文件例子：
```json
{
  "cid": "7652886633113456", 
  "uid": "7652669334456778", 
  "user_account": "zhangsan", 
  "user_name": "张三", 
  "group_id": "", 
  "group_name": "", 
  "msgtype": "file", 
  "text": "", 
  "origin_text": "", 
  "trigger_word": "", 
  "file": {
    "name": "file.txt", 
    "url": "https://www.file.com/xxx"
  }, 
  "timestamp": "1639388189"
}
```

| 字段   | 描述 |
| ------ | ---------------- |
| cid    | 组织id |
| uid    | 用户id |
| user_account   | 账号名，一般指域账号 |
| user_name      | 用户显示名称，一般指姓名 |
| group_id/group_name   | 群聊才有的字段，单聊不带 |
| msgtype | 消息类型：text(文本), reference(引用), file(文件), image(图片), mixed(图文混排) |
| text           | 消息正文 |
| origin_text  | 引用消息 |
| trigger_word   | 忽略这个字段 |
| file | 文件消息才有的字段，格式为：{"name": "filename.ext", "url": "https://file/download/url"} |
| images | 数组，图片、图文混排消息才有的字段，数组中的每个元素为图片下载地址：["https://image/download/url"] |
| timestamp      | 消息 utc 时间 |


**机器人收消息规则**

和正常思维一样
- 单聊：能收到
- 群：必须机器人在群里，才能收到群消息。不想让机器人收可以踢它出去。

**避免误插嘴**

考虑群里人其他人也在说话，不是每句都需要机器人回答，为防止群里机器人误插嘴，一般业务可以约定机器人只回答 @机器人的，或者以特殊字符命令开始的消息，或者含有特殊关键词。例如
```
今天天气怎么样 @问答机器人
/天气
/查询 xxx
```

**避免两个机器人打架**

如果把两个机器人拉到同一个群里，代码逻辑不当可能会引起打架，死循环刷屏。所以一般机器人只回复@自己的消息，可以避免这个问题。

## sse流式消息

业务方如果需要用到sse流式消息，可以在webhook（机器人收消息）中，按以下格式响应：

- http响应头`Content-Type: text/event-stream; charset=utf-8`；
- 以`data: {"v": "文本片段"}`流式输出sse内容；
- 以`data: [DONE]`结束sse过程；
- 如果sse过程较长，业务服务端和推推服务端需要发送心跳信息，来维持长连接，心跳内容不做限制。


示例：

```
Content-Type: text/event-stream; charset=utf-8

data: {"v": "你"}

data: {"v": "好"}

: keepalive

data: {"v": "推"}

data: {"v": "推！"}

data: [DONE]
```


**限制**

- 仅支持纯文本（markdown格式不会被渲染）；
- 仅支持单、群聊；
- 文本长度限制：5000。sse消息文本最大长度，（一个中文字符长度为1），超出限制将被截断；
- http header响应超时：10秒。如果超时将丢弃该响应。
- sse事件超时：30秒。如果在30秒内没有收到下个sse事件，推推将断开sse连接（可通过心跳机制维持连接）；
- sse过程总限时：3600秒。整个sse过程总时间限制，超时后推推主动断开连接。



# 6、群管理功能

## 建群

- 接口: `POST /group/create`
- Content-Type: `application/json`

- 消息体对象:

| JSON字段          | 描述
| ----------------- | --------------------------
| name              | 群名称，必填 |
| owner              | 群主域账号，必填 |
| members           | 群成员域账号，必填，限制：100人，见《发送范围》章节 |

**备注：**群主(owner)可以包含在群成员(members)中，群主及成员和发消息接口《发送范围》保持一致。

**频率限制：**每个机器人，每天可调用该接口10次，如果有特殊需求，调整频率限制，请联系我们申请。

- 返回结果

| 字段    | 描述                                         |
| ------- | -------------------------------------------- |
| errcode | 错误码，0代表成功                            |
| errmsg  | 错误信息                                     |
| group_id | 群ID，可用于发群消息接口 |
| fails   | 拉群失败用户列表 |
| explains | 解释`fails`失败列表为什么会失败。**该字段仅用于排查问题，业务方不要解析！！！**  |

- 示例：

```json
POST /group/create?appid=*****&secret=****** HTTP/1.1
Host: alarm.im.qihoo.net
Content-Type: application/json

{
  "name": "群名称", 
  "owner": "zhanger", 
  "members": [
    "zhangsan", 
    "zhangsi"
  ]
}
```


## 拉人进群

- 接口: `POST /group/member/add`
- Content-Type: `application/json`

- 消息体对象:

| JSON字段          | 描述
| ----------------- | --------------------------
| group_id              | 群ID，必填 |
| members           | 群成员域账号，必填，见《发送范围》章节 |

- 返回结果

| 字段    | 描述                                         |
| ------- | -------------------------------------------- |
| errcode | 错误码，0代表成功                            |
| errmsg  | 错误信息                                     |
| fails   | 失败用户列表 |
| explains | 解释`fails`失败列表为什么会失败。**该字段仅用于排查问题，业务方不要解析！！！**  |

- 示例：

```json
POST /group/member/add?appid=***&secret=*** HTTP/1.1
Host: alarm.im.qihoo.net
Content-Type: application/json

{
  "group_id": "12345", 
  "members": [
    "zhangsan", 
    "zhangsi"
  ]
}
```



## 踢人

- 接口: `POST /group/member/remove`
- Content-Type: `application/json`

- 消息体对象:

| JSON字段          | 描述
| ----------------- | --------------------------
| group_id              | 群ID，必填 |
| members           | 群成员域账号，必填，见《发送范围》章节 |

- 返回结果

| 字段    | 描述                                         |
| ------- | -------------------------------------------- |
| errcode | 错误码，0代表成功                            |
| errmsg  | 错误信息                                     |
| fails   | 踢失败用户列表 |
| explains | 解释`fails`失败列表为什么会失败。**该字段仅用于排查问题，业务方不要解析！！！**  |

- 示例：

```json
POST /group/member/remove?appid=***&secret=*** HTTP/1.1
Host: alarm.im.qihoo.net
Content-Type: application/json

{
  "group_id": "12345", 
  "members": [
    "zhangsan", 
    "zhangsi"
  ]
}
```



## 机器人所在群列表

- 接口: `GET /group/robot/in`
- 消息体对象:
  - 无

- 返回结果

| 字段    | 描述              |
| ------- | ----------------- |
| errcode | 错误码，0代表成功 |
| errmsg  | 错误信息          |
| groups  | 机器人所在群列表  |

- 请求示例：

```json
GET /group/robot/in?appid=***&secret=*** HTTP/1.1
Host: alarm.im.qihoo.net
Content-Type: application/json
```

- 返回结果示例

  ```json
  {
    "trans_id": "de45d7aed20e51df1269e5fdfb9dcfaf", 
    "appid": "xxx", 
    "robot_uid": "78392241", 
    "robot_name": "robot name", 
    "robot_desc": "robot desc", 
    "errcode": 0, 
    "errmsg": "请求成功", 
    "groups": [
      {
        "group_id": "1234567890", 
        "name": "群名称"
      }
    ]
  }
  ```

  

## 用户是否在群内

- 接口: `POST /group/user/isin`

- 请求body

| JSON字段 | 描述             |
| -------- | ---------------- |
| user     | 用户域账号，必填 |
| groups   | 群id列表，必填   |

- 返回结果

| 字段    | 描述                       |
| ------- | -------------------------- |
| errcode | 错误码，0代表成功          |
| errmsg  | 错误信息                   |
| groups  | 用户和机器人共同所在群列表 |

<details> <summary>点击展开示例</summary>
<pre>
请求：
POST /group/user/isin?appid=***&secret=*** HTTP/1.1
Host: alarm.im.qihoo.net
Content-Type: application/json

{
  "groups": [
    "1234567890", // 用户在该群中
    "6473824128"  // 用户不在该群中
  ],
  "user": "域账号"
}

响应：
{
    "trans_id": "de45d7aed20e51df1269e5fdfb9dcfaf", 
    "appid": "xxx", 
    "robot_uid": "78392241", 
    "robot_name": "robot name", 
    "robot_desc": "robot desc", 
    "errcode": 0, 
    "errmsg": "请求成功", 
    "groups": [
      {
        "group_id": "1234567890",
        "name": "群名称"
      }
    ]
}
</pre>
</details>


# 7、自助改回调等属性

## 改名

- 接口: `POST /robot/name/modify`

**注意**: 接口限速每分钟1次，遇到频控错误请1分钟后再操作；修改5分钟后生效。

- 消息体对象

| JSON字段 | 描述             |
| -------- | ---------------- |
| name     | 机器人名字，必填 |


- 返回结果

| 字段    | 描述                       |
| ------- | -------------------------- |
| errcode | 错误码，0代表成功          |
| errmsg  | 错误信息                   |

- 请求示例：

```json
POST /robot/name/modify?appid=***&secret=*** HTTP/1.1
Host: alarm.im.qihoo.net
Content-Type: application/json

{
  "name": "机器人新名字"
}
```


## 改头像

- 接口: `POST /robot/avatar/modify`

**注意**: 接口限速每分钟1次，遇到频控错误请1分钟后再操作；修改5分钟后生效。


- 消息体对象

| JSON字段 | 描述             |
| -------- | ---------------- |
| avatar      | 机器人头像文件ID，必填，限制图片尺寸：100×100、200×200或400×400 |

头像`avatar` 获取方法：见《上传文件》章节。

- 返回结果

| 字段    | 描述                       |
| ------- | -------------------------- |
| errcode | 错误码，0代表成功          |
| errmsg  | 错误信息                   |

- 请求示例：

```json
POST /robot/avatar/modify?appid=***&secret=*** HTTP/1.1
Host: alarm.im.qihoo.net
Content-Type: application/json

{
  "avatar": "机器人新头像id通过上传图片获得"
}
```


## 改收消息回调url

- 接口: `POST /robot/webhook/modify`

**注意**: 接口限速每分钟1次，遇到频控错误请1分钟后再操作；修改5分钟后生效。


- 消息体对象

| JSON字段 | 描述             |
| -------- | ---------------- |
| url      | 机器人收消息回调url |



- 返回结果

| 字段    | 描述                       |
| ------- | -------------------------- |
| errcode | 错误码，0代表成功          |
| errmsg  | 错误信息                   |

- 请求示例：

```json
POST /robot/webhook/modify?appid=***&secret=*** HTTP/1.1
Host: alarm.im.qihoo.net
Content-Type: application/json

{
  "url": "https://xxx"
}
```

curl 示例：(linux shell)
```
curl -X POST  'https://alarm.im.qihoo.net/robot/webhook/modify?appid=123456&secret=***' -H 'Content-Type:application/json' -d '{"url": "https://your_url"}'
```

注意：10.16网段的CORP机/开发机不建议用来接回调。因默认CORP与IDC机房不互通，需要去信息安全平台申请服务端ACL(TCP协议0.0.0.0到你的端口)，建议使用IDC机房作为回调地址。

## 改可交互式消息回调url

- 接口: `POST /robot/interactive_url/modify`

**注意**: 接口限速每分钟1次，遇到频控错误请1分钟后再操作；修改5分钟后生效。


- 消息体对象

| JSON字段 | 描述             |
| -------- | ---------------- |
| url      | 机器人可交互式消息回调url |



- 返回结果

| 字段    | 描述                       |
| ------- | -------------------------- |
| errcode | 错误码，0代表成功          |
| errmsg  | 错误信息                   |

- 请求示例：

```json
POST /robot/interactive_url/modify?appid=***&secret=*** HTTP/1.1
Host: alarm.im.qihoo.net
Content-Type: application/json

{
  "url": "https://xxx"
}
```



## 查询自身属性

- 接口: `GET /robot/prop/get`

- 消息体对象

- 返回结果

| 字段    | 描述                       |
| ------- | -------------------------- |
| errcode | 错误码，0代表成功          |
| errmsg  | 错误信息                   |
| properties  | 机器人属性 |

- 请求示例：

```json
GET /robot/prop/get?appid=***&secret=*** HTTP/1.1
Host: alarm.im.qihoo.net
```

- 返回结果示例

  ```json
  {
    "trans_id": "de45d7aed20e51df1269e5fdfb9dcfaf", 
    "appid": "xxx", 
    "robot_uid": "78392241", 
    "robot_name": "robot name", 
    "robot_desc": "robot desc", 
    "errcode": 0, 
    "errmsg": "请求成功",
    "properties":{
        "name": "robot name",
        "avatar": "robot avatar",
        "webhook": "https://xxx",
        "interactive_url": "https://yyy"
    }
  }
  ```

# 8、机器人快捷指令

（**目前仅支持团队**）机器人快捷指令是指，在输入框中输入"/"的方式，唤起机器人支持的快捷指令。旨在帮助用户了解及键入机器人支持的功能及用法。示例效果如下：

![机器人快捷指令](https://p0.ssl.qhimg.com/t019c4087512b579a6a.png)



## 设置机器人快捷指令

- 接口：`POST /shortcutCommand/set`

- 消息体对象

| JSON字段      | 描述                                                         |
| ------------- | ------------------------------------------------------------ |
| shortcut_cmds | 数组，每个数组项是个object结构。所有的快捷指令，注意：每次设置均是**全量覆盖**设置 |

每个快捷指令字段：

| JSON字段            | 描述                                                 |
| ------------------- | ---------------------------------------------------- |
| command_name        | 指令名称，用于匹配和展示机器人功能，长度限制：20字符 |
| command_description | 指令描述，机器人功能详细描述，长度限制：50字符       |

- 示例

    ```
    POST /shortcutCommand/set?appid=***&secret=*** HTTP/1.1
    Host: alarm.im.qihoo.net
    Content-Type: application/json
    
    {
        "shortcut_cmds": [
            {
                "command_name": "基础模型_国风",
                "command_description": "2.5D华丽国风风格，擅长人物画"
            }
        ]
    }
    ```

    

## 查询机器人支持的所有快捷指令

- 接口：`GET /shortcutCommand/get`

- 示例：

    ```
    GET /shortcutCommand/get?appid=***&secret=*** HTTP/1.1
    Host: alarm.im.qihoo.net
    Content-Type: application/json
    
    {
        "trans_id": "b8c1d4a2ae1927c014f8815a0b45bf17",
        "appid": "123",
        "robot_uid": "456",
        "robot_name": "robot name",
        "robot_desc": "robot desc",
        "errcode": 0,
        "errmsg": "请求成功",
        "datas": {
            "shortcut_cmds": [
                {
                    "command_scope": [
                        "teams"
                    ],
                    "command_type": "input",
                    "command_description": "2.5D华丽国风风格，擅长人物画",
                    "command_name": "基础模型_国风",
                    "command_content": "基础模型_国风"
                }
            ]
        }
    }
    ```




# 9、FAQ

**机器人和公众号的关系**

> - 公众号是人工发文章用的，有web管理后台来人工编写文章，一般是发文章给allstaff或者指定部门范围的推送文章
- 机器人隶属于公众号，是公众号的消息服务。不是给人发的，而是给API接口调用。机器人和普通用户类似，都可以收、发消息，以及群管理，等人能进行的操作。
- 一个公众号可以有多个机器人

**改机器人名字、头像**

> 机器人头像名字可单独配置，和公众号可以不同。见《7、机器人自助修改属性》。


**把机器人拉到群里？**

> - 第一步：用发消息API，给自己发一条单聊消息，自己收到
- 第二步：客户端添加群成员，最近聊天列表有你的机器人，把它拉到群里

**群ID怎么拿到**
> PC端，群的右上角...详情->群聊ID，点击右侧图标复制。

**消息发送失败: 机器人无权发送给目标，请检查权限申请**
> 一般是发送目标人员换部门了，而当初申请机器人的时候不包含这个范围。所以需要提供机器人名字，新的部门范围，联系我们重新调整下权限。

# 10、官方机器人-Gitlab&Grafana

- Gitlab机器人：无需开发，在推推上订阅git事件通知；支持发送到单聊、群聊、团队频道；
- Grafana机器人：无需开发，在推推上收到grafana报警通知。支持发送到群聊、团队频道；

在推推->群->聊天设置->群机器人可以找到。



# 11、联系我们

邮箱联系 g-tuitui-fankui@360.cn
