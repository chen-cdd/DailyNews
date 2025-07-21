from wechatpy import WeChatClient

APPID = ""
APPSECRET = ""

cli = WeChatClient(APPID, APPSECRET)

followers = cli.user.get_followers()  # {'total':..,'count':..,'data':{'openid':[...]} ...}
openids = followers["data"]["openid"]
print("粉丝 OpenID 列表：", openids)

# 如果粉丝不多，你能直接猜哪个是自己；否则继续遍历昵称
for oid in openids:
    info = cli.user.get(oid)   
    print(oid, info.get("nickname"), info.get("subscribe_time"))
