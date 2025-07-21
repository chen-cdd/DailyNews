# publisher.py
from typing import Tuple
from wechatpy.client import WeChatClient
from wechatpy.exceptions import WeChatClientException
from loguru import logger
import os
import json

# 微信接口 URL
DRAFT_ADD_URL    = "https://api.weixin.qq.com/cgi-bin/draft/add?access_token={token}"
MASS_PREVIEW_URL = "https://api.weixin.qq.com/cgi-bin/message/mass/preview?access_token={token}"
MASS_SENDALL_URL = "https://api.weixin.qq.com/cgi-bin/message/mass/sendall?access_token={token}"

def publish(
    markdown: str,
    html: str,
    app_id: str,
    app_secret: str,
    preview_openid: str = "",
    publish_mode: str = "draft_only",
    title: str = "每日AI精选资讯",
    author: str = "GSCC",
    digest: str = "AI 自动改写资讯摘要",
    thumb_path: str = "config/thumb.jpg",  # 默认封面路径
) -> Tuple[str, str]:
    """
    publish_mode:
      - none       : 不调用微信 API
      - draft_only : 只创建草稿
      - preview    : 创建草稿 + 发送预览
      - sendall    : 创建草稿 + 群发
    返回 (status, media_id)
    """
    # 验证凭证
    if not app_id or not app_secret:
        logger.warning("未配置公众号凭证，跳过微信发布。")
        return ("skipped", "")

    # 初始化客户端 & 拿 token
    client = WeChatClient(app_id, app_secret)
    token = client.access_token

    # 上传封面图
    try:
        if not os.path.exists(thumb_path):
            logger.error(f"未找到封面图文件: {thumb_path}")
            return ("thumb_missing", "")
        with open(thumb_path, 'rb') as f:
            upload_resp = client.material.add("image", f)
            thumb_media_id = upload_resp["media_id"]
            logger.info(f"封面图上传成功，thumb_media_id={thumb_media_id}")
    except WeChatClientException as e:
        logger.exception("封面图上传失败")
        return (f"thumb_upload_error:{e.errcode}", "")

    # 构造草稿文章结构
    article = {
        "title": title,
        "author": author,
        "content": html,
        "digest": digest,
        "thumb_media_id": thumb_media_id,
        "need_open_comment": 0,
        "only_fans_can_comment": 0,
    }
    body = {"articles": [article]}

    # 创建草稿
    try:
        resp = client._http.post(
            DRAFT_ADD_URL.format(token=token),
            data=json.dumps(body, ensure_ascii=False).encode("utf-8"),
        )
        data = resp.json()
        if data.get("errcode", 0) != 0:
            raise WeChatClientException(data["errcode"], data.get("errmsg", "未知错误"))
        media_id = data.get("media_id", "")
        logger.info(f"草稿创建成功 media_id={media_id}")
    except WeChatClientException as e:
        logger.exception("草稿创建失败")
        return (f"draft_error:{e.errcode}", "")

    # 根据模式决定后续操作
    if publish_mode in ("none", "draft_only"):
        return ("draft", media_id)

    if publish_mode == "preview":
        if not preview_openid:
            logger.error("preview 模式需提供 preview_openid，回退 draft_only")
            return ("draft", media_id)
        try:
            preview_body = {
                "touser": preview_openid,
                "mpnews": {"media_id": media_id},
                "msgtype": "mpnews"
            }
            resp = client._http.post(
                MASS_PREVIEW_URL.format(token=token),
                data=json.dumps(preview_body, ensure_ascii=False).encode("utf-8"),
            )
            data = resp.json()
            if data.get("errcode") == 0:
                logger.info(f"预览已发送至 {preview_openid}")
                return ("preview", media_id)
            else:
                raise WeChatClientException(data["errcode"], data.get("errmsg"))
        except WeChatClientException as e:
            logger.exception("预览失败")
            return (f"preview_error:{e.errcode}", media_id)

    if publish_mode == "sendall":
        try:
            send_body = {
                "filter": {"is_to_all": True},
                "mpnews": {"media_id": media_id},
                "msgtype": "mpnews"
            }
            resp = client._http.post(
                MASS_SENDALL_URL.format(token=token),
                data=json.dumps(send_body, ensure_ascii=False).encode("utf-8"),
            )
            data = resp.json()
            if data.get("errcode") == 0:
                logger.warning("⚠ 群发已执行，请确认无误！")
                return ("sent", media_id)
            else:
                raise WeChatClientException(data["errcode"], data.get("errmsg"))
        except WeChatClientException as e:
            logger.exception("群发失败")
            return (f"send_error:{e.errcode}", media_id)

    # 兜底
    logger.error(f"未知 publish_mode={publish_mode}，回退 draft_only")
    return ("draft", media_id)
