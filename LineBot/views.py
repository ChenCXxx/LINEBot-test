from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse, HttpResponseBadRequest, HttpResponseForbidden, JsonResponse
from django.conf import settings
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, TextSendMessage
from .models import User, Group

import logging
logger = logging.getLogger(__name__)

# Create your views here.
line_bot_api = LineBotApi(settings.LINEBOT_CHANNEL_ACCESS_TOKEN)
handler = WebhookHandler(settings.LINEBOT_CHANNEL_SECRET)


@csrf_exempt
def callback(request):
    if request.method == 'POST':
        body = request.body.decode('utf-8')
        signature = request.headers['x-line-signature']
        try:
            handler.handle(body, signature)
        except InvalidSignatureError:
            return HttpResponseForbidden()
        return HttpResponse('OK')
    return HttpResponseBadRequest()


# 處理收到 MessageEvent 且內容為 TextMessage
@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    user_id = event.source.user_id
    

    user_info = User.objects.filter(user_id=user_id)

    if not user_info.exists():
        text_info = event.message.text
        if text_info != None:
            # replace "【" into "" and "】" into ""
            text_info = text_info.replace("【", "").replace("】", "")
        
        # text_info format: "NAME/DEPARTMENT/GROUP"
        part = [p.strip() for p in text_info.split("/")]
        if text_info == None or len(part) != 3:
            MessageReply = "格式錯誤"
        else:
            # 處理註冊
            profile = line_bot_api.get_profile(user_id)
            pic_url = profile.picture_url if profile.picture_url else ""
            line_name = profile.display_name if profile.display_name else ""
            user_name = part[0]
            department = part[1]
            # print user_name and department in logger
            logger.info(f"user_name: {user_name}, department: {department}")
            # 正規式
            import re
            match = re.match(r"([^\d]+)(\d+)", part[2])
            if match:
                company = match.group(1).strip()
                group_number = int(match.group(2))
            try:
                print(f"company: '{company}', group_number: '{group_number}'")
                group_obj = Group.objects.get(company=company, number=group_number)
            except Group.DoesNotExist:
                MessageReply = "群組不存在，請聯絡管理員"
                line_bot_api.reply_message(
                    event.reply_token,
                    TextSendMessage(text=MessageReply)
                )
                return
            User.objects.create(
                user_id=user_id,
                user_name=user_name,
                line_name=line_name,
                pic_url=pic_url,
                department=department,
                group=group_obj
            )
            MessageReply = "註冊成功"
    else:
        MessageReply = "您已註冊"

    line_bot_api.reply_message(
        event.reply_token,
        TextSendMessage(text=MessageReply)
    )