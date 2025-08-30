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
    reply_messages = []
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
            reply_messages.append(
                TextSendMessage(text="請輸入正確格式：\n【姓名/系所/公司名稱+群組編號】\n例如：\n【艾依古/資工系/Google1】")
            )
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
                reply_messages.append(
                    TextSendMessage(text="群組不存在，請聯絡管理員")
                )
                line_bot_api.reply_message(
                    event.reply_token,
                    reply_messages
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
            reply_messages.append(
                TextSendMessage(text="註冊成功")
            )
    else:
        user_info = user_info.first()
        
        # 【企業博覽會規則說明】
        if event.message.text == "【企業博覽會規則說明】":
            reply_messages.append(
                TextSendMessage(text=f"🌟哈囉 {user_info.user_name}！，您的序號是：{user_info.user_id}\n我是可松！一個懷抱夢想的魔物訓練師！\n\n我的圖鑑上，已經登錄了無數珍奇魔物📖\n但每當夜深人靜，我總會想：\n「我真正想獲得的，是魔物？還是…更好的未來？」\n\n直到某天，我收到了一封神祕來信✉️——\n「傳說中有五大能量石，\n集齊它們，就能讓訓練師與魔物一同進化！」\n\n這一次，我想邀請你，一起踏上這場旅程！💥\n{user_info.user_name}，這不只是尋寶🌟，\n是讓我們進化的旅程，準備好一起冒險了嗎？✨")
            )
            reply_messages.append(
                TextSendMessage(text="走訪各個企業攤位就像與不同的訓練家交流，能更認識各種職業，同時更深入了解自己擅長的東西，慢慢找到想投身的領域。在逐步探索的過程中，對各個企業與自己有更深入的想法，找到未來的方向！\n\n1️⃣ 參加者需完成企博攤位任務或指定娛樂交流活動\n2️⃣ 掃描 QRcode 隨機得到一種寶石\n3️⃣ 依據不同數量和種類的寶石對應三種等級的抽獎券\n4️⃣ 點擊【兌換抽獎券】進行不同等級之抽獎券兌換")
            )
            reply_messages.append(
                TextSendMessage(text="✨抽獎方法✨\n\n1️⃣ 在 LINE Bot 上點擊【兌換抽獎券】\n2️⃣ 選擇欲兌換的等級抽獎券\n3️⃣ 9/21（日）由工作人員统一抽獎\n4️⃣ LINE Bot 會在【中獎通知】通知中獎名單\n\n🎟️ 抽獎時間：9/21（日）10:30 - 11:00\n🎟️ 領獎時間：9/21（日）11:00 - 13:30\n\n註：逾期未兌換獎品者，視同放棄兌換\n\n📍 一個人可以兌換無上限數量之抽獎券\n📍 兌換任一 Level 的抽獎券即視為參與該 Level 之抽獎")
            )
        # 【娛樂交流活動報名】
        elif event.message.text == "【娛樂交流活動報名】":
            reply_messages.append(
                TextSendMessage(text="活動尚未開始報名，敬請期待！")
            )
        # 【我的寶石】
        elif event.message.text == "【我的寶石】":
            reply_messages.append(
                TextSendMessage(text="請輸入：【能量寶石掃描】或【能量寶石查詢】")
            )
        # 【兌換抽獎券】

        # 【中獎通知】
    line_bot_api.reply_message(
        event.reply_token,
        reply_messages
    )