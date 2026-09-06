# -*- coding: utf-8 -*-
import requests
import json
import time
import re
import threading
from datetime import datetime

# ======== الإعدادات ========
TOKEN = "8984794385:AAFaE0m1Rs_ztzC_a0Sg7TNbHcJeWcHPwmU"
ADMIN_CHAT_ID = 6458400064  # آيدي المشرف
BINANCE_ID = "743427300"

# ======== ملفات التخزين ========
USERS_FILE = "users.json"
BLACKLIST_FILE = "blacklist.json"
CHAT_REQUESTS_FILE = "chat_requests.json"

# ======== الإعدادات العامة ========
chat_enabled = True

# ======== تخزين مؤقت ========
user_state = {}
active_chats = {}
admin_reply_mode = {}
broadcast_mode = {}

# ======== دوال مساعدة ========
def send_message(chat_id, text, keyboard=None):
    try:
        url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
        payload = {"chat_id": chat_id, "text": text, "parse_mode": "Markdown"}
        if keyboard:
            payload["reply_markup"] = json.dumps(keyboard)
        response = requests.post(url, json=payload, timeout=10)
        return response.status_code == 200
    except:
        return False

def send_photo(chat_id, photo_url, caption=""):
    try:
        url = f"https://api.telegram.org/bot{TOKEN}/sendPhoto"
        payload = {"chat_id": chat_id, "photo": photo_url, "caption": caption, "parse_mode": "Markdown"}
        response = requests.post(url, json=payload, timeout=10)
        return response.status_code == 200
    except:
        return False

# ======== إدارة المستخدمين ========
def save_user(user_id):
    try:
        with open(USERS_FILE, "r") as f:
            users = json.load(f)
    except:
        users = []
    if user_id not in users:
        users.append(user_id)
        with open(USERS_FILE, "w") as f:
            json.dump(users, f, indent=2)
        return True
    return False

def get_all_users():
    try:
        with open(USERS_FILE, "r") as f:
            return json.load(f)
    except:
        return []

# ======== القائمة السوداء ========
def load_blacklist():
    try:
        with open(BLACKLIST_FILE, "r") as f:
            return json.load(f)
    except:
        return []

def save_blacklist(blacklist):
    with open(BLACKLIST_FILE, "w") as f:
        json.dump(blacklist, f, indent=2)

def is_blacklisted(user_id):
    return user_id in load_blacklist()

def add_to_blacklist(user_id):
    blacklist = load_blacklist()
    if user_id not in blacklist:
        blacklist.append(user_id)
        save_blacklist(blacklist)
        return True
    return False

def remove_from_blacklist(user_id):
    blacklist = load_blacklist()
    if user_id in blacklist:
        blacklist.remove(user_id)
        save_blacklist(blacklist)
        return True
    return False

# ======== إدارة طلبات المحادثة ========
def load_chat_requests():
    try:
        with open(CHAT_REQUESTS_FILE, "r") as f:
            return json.load(f)
    except:
        return {}

def save_chat_requests(requests):
    with open(CHAT_REQUESTS_FILE, "w") as f:
        json.dump(requests, f, indent=2)

def add_chat_request(user_id, chat_id):
    requests = load_chat_requests()
    requests[str(user_id)] = {
        "user_id": user_id,
        "chat_id": chat_id,
        "status": "pending",
        "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    save_chat_requests(requests)

def update_chat_request(user_id, status):
    requests = load_chat_requests()
    if str(user_id) in requests:
        requests[str(user_id)]["status"] = status
        save_chat_requests(requests)

def delete_chat_request(user_id):
    requests = load_chat_requests()
    if str(user_id) in requests:
        del requests[str(user_id)]
        save_chat_requests(requests)

def get_pending_requests():
    requests = load_chat_requests()
    return {k: v for k, v in requests.items() if v["status"] == "pending"}

# ======== سعر الصرف ========
def get_exchange_rate():
    try:
        url = "https://api.exchangerate-api.com/v4/latest/USD"
        response = requests.get(url, timeout=10)
        data = response.json()
        if data.get("rates") and data["rates"].get("EGP"):
            return data["rates"]["EGP"]
    except:
        pass
    return None

# ======== أذكار ========
MORNING_DHKIR = "🌅 أذكار الصباح... (نص طويل تم اختصاره)"
EVENING_DHKIR = "🌇 أذكار المساء... (نص طويل تم اختصاره)"

def send_morning_dhkir():
    while True:
        now = datetime.now()
        if now.hour == 5 and now.minute == 0:
            send_message(ADMIN_CHAT_ID, MORNING_DHKIR)
            time.sleep(60)
        time.sleep(30)

def send_evening_dhkir():
    while True:
        now = datetime.now()
        if now.hour == 18 and now.minute == 0:
            send_message(ADMIN_CHAT_ID, EVENING_DHKIR)
            time.sleep(60)
        time.sleep(30)

def send_prayer_reminder():
    while True:
        time.sleep(300)
        send_message(ADMIN_CHAT_ID, "🕌 تذكير بالصلاة على النبي ﷺ...")

# ======== لوحات المفاتيح ========
def main_keyboard():
    return {
        "keyboard": [
            ["🎯 عرض اليوم المميز", "🐋 باقات الاستثمار"],
            ["🌍 تحويل Binance", "💱 سعر الدولار اليوم"],
            ["📤 إرسال إيصال", "📞 طلب التواصل مع المدير"],
            ["📊 حالة استثماري", "❓ المساعدة"]
        ],
        "resize_keyboard": True
    }

def admin_keyboard():
    return {
        "keyboard": [
            ["📢 بث رسالة (نص)", "🖼️ بث رسالة (صورة)"],
            ["👥 عدد المستخدمين", "📞 طلبات التواصل"],
            ["🚫 طرد مستخدم", "🔓 إلغاء طرد"],
            ["⏸️ إيقاف المحادثات", "▶️ تشغيل المحادثات"],
            ["📊 الإحصائيات", "🔙 العودة للقائمة"]
        ],
        "resize_keyboard": True
    }

def packages_keyboard():
    return {
        "keyboard": [
            ["🎯 عرض اليوم (125 → 1350)"],
            ["🐋 الحوت الصغير (150 → 2500)"],
            ["🐋 الحوت الكبير (250 → 3790)"],
            ["🔙 العودة للقائمة"]
        ],
        "resize_keyboard": True
    }

def chat_request_keyboard(user_id):
    return {
        "inline_keyboard": [
            [{"text": "✅ قبول المحادثة", "callback_data": f"accept_chat_{user_id}"}],
            [{"text": "❌ رفض المحادثة", "callback_data": f"reject_chat_{user_id}"}]
        ]
    }

def end_chat_keyboard():
    return {
        "keyboard": [
            ["🔚 إنهاء المحادثة"]
        ],
        "resize_keyboard": True
    }

def admin_reply_keyboard(user_id):
    return {
        "inline_keyboard": [
            [{"text": "✉️ الرد على العميل", "callback_data": f"reply_to_{user_id}"}],
            [{"text": "🔚 إنهاء المحادثة مع العميل", "callback_data": f"end_chat_{user_id}"}]
        ]
    }

# ======== معالجة الأوامر ========
def handle_updates():
    global chat_enabled, user_state, active_chats, admin_reply_mode, broadcast_mode
    last_update_id = 0
    
    while True:
        try:
            url = f"https://api.telegram.org/bot{TOKEN}/getUpdates"
            response = requests.get(url, params={"offset": last_update_id + 1, "timeout": 30})
            updates = response.json()
            
            if updates.get("ok"):
                for update in updates.get("result", []):
                    last_update_id = update["update_id"]
                    
                    if "message" in update:
                        message = update["message"]
                        chat_id = message["chat"]["id"]
                        user_id = message["from"]["id"]
                        text = message.get("text", "")
                        
                        # التحقق من الحظر
                        if is_blacklisted(user_id) and chat_id != ADMIN_CHAT_ID:
                            send_message(chat_id, "🚫 أنت محظور.")
                            continue
                        
                        # تسجيل المستخدم الجديد
                        if save_user(user_id):
                            username = message["from"].get("username", "لا يوجد")
                            first_name = message["from"].get("first_name", "لا يوجد")
                            send_message(ADMIN_CHAT_ID, 
                                f"👤 *مستخدم جديد*\n🆔 `{user_id}`\n📛 @{username}\n👤 {first_name}")
                        
                        # ======== أوامر البوت ========
                        if text == "/start":
                            send_message(chat_id,
                                "🐋 *مرحبًا بك في بوت استثمار الحيتان!*\n\n"
                                "🎯 عرض اليوم: 125 ج.م ← 1350 ج.م\n"
                                "🌍 تحويل Binance متاح\n\n"
                                "اختر من القائمة:",
                                main_keyboard()
                            )
                        
                        elif text == "💱 سعر الدولار اليوم":
                            rate = get_exchange_rate()
                            if rate:
                                send_message(chat_id, f"💱 1 دولار = *{rate:.2f}* ج.م")
                            else:
                                send_message(chat_id, "❌ لم نتمكن من جلب السعر.")
                        
                        elif text == "🎯 عرض اليوم المميز":
                            send_message(chat_id,
                                "🎯 *عرض اليوم*\n💰 125 ج.م ← 1350 ج.م\n📋 `01214764047`\n🌍 Binance ID: `743427300`",
                                main_keyboard()
                            )
                            user_state[user_id] = {"state": "package_selected", "package": "125"}
                        
                        elif text == "🐋 باقات الاستثمار":
                            send_message(chat_id, "🐋 اختر الباقة:", packages_keyboard())
                        
                        elif text == "🎯 عرض اليوم (125 → 1350)":
                            send_message(chat_id, "🎯 125 ج.م ← 1350 ج.م\n📋 `01214764047`")
                            user_state[user_id] = {"state": "package_selected", "package": "125"}
                        
                        elif text == "🐋 الحوت الصغير (150 → 2500)":
                            send_message(chat_id, "🐋 150 ج.م ← 2500 ج.م\n📋 `01214764047`")
                            user_state[user_id] = {"state": "package_selected", "package": "150"}
                        
                        elif text == "🐋 الحوت الكبير (250 → 3790)":
                            send_message(chat_id, "🐋 250 ج.م ← 3790 ج.م\n📋 `01214764047`")
                            user_state[user_id] = {"state": "package_selected", "package": "250"}
                        
                        elif text == "🌍 تحويل Binance":
                            send_message(chat_id, "🌍 Binance ID: `743427300`")
                        
                        elif text == "📤 إرسال إيصال":
                            send_message(chat_id, "📸 أرسل صورة الإيصال.")
                            user_state[user_id] = {"state": "waiting_receipt"}
                        
                        # ======== طلب التواصل مع المدير ========
                        elif text == "📞 طلب التواصل مع المدير":
                            if not chat_enabled:
                                send_message(chat_id, "⏸️ خدمة العملاء متوقفة حاليًا.")
                                continue
                            
                            # التحقق من وجود طلب سابق
                            requests_data = load_chat_requests()
                            if str(user_id) in requests_data and requests_data[str(user_id)]["status"] == "pending":
                                send_message(chat_id, "⏳ طلبك قيد الانتظار...")
                                continue
                            
                            # إرسال الطلب للمشرف
                            add_chat_request(user_id, chat_id)
                            
                            admin_msg = (
                                f"📞 *طلب تواصل جديد*\n\n"
                                f"👤 المستخدم: `{user_id}`\n"
                                f"🕒 الوقت: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
                            )
                            send_message(ADMIN_CHAT_ID, admin_msg, chat_request_keyboard(user_id))
                            
                            send_message(chat_id, "✅ تم إرسال طلبك، سيتم الرد عليك قريبًا.")
                        
                        # ======== حالة الاستثمار ========
                        elif text == "📊 حالة استثماري":
                            send_message(chat_id, "📊 لا توجد استثمارات نشطة.")
                        
                        elif text == "❓ المساعدة":
                            send_message(chat_id, "❓ للمساعدة تواصل مع المدير.")
                        
                        # ======== أوامر المشرف ========
                        elif chat_id == ADMIN_CHAT_ID:
                            if text == "/admin":
                                send_message(ADMIN_CHAT_ID, "👑 *لوحة التحكم*", admin_keyboard())
                            
                            elif text == "📞 طلبات التواصل":
                                pending = get_pending_requests()
                                if not pending:
                                    send_message(ADMIN_CHAT_ID, "📭 لا توجد طلبات معلقة.")
                                else:
                                    msg = "📋 *طلبات التواصل المعلقة:*\n\n"
                                    for uid, data in pending.items():
                                        msg += f"• `{uid}` - {data['time']}\n"
                                    send_message(ADMIN_CHAT_ID, msg)
                            
                            elif text == "📢 بث رسالة (نص)":
                                send_message(ADMIN_CHAT_ID, "✍️ اكتب الرسالة:")
                                broadcast_mode[user_id] = {"active": True, "type": "text"}
                            
                            elif text == "🖼️ بث رسالة (صورة)":
                                send_message(ADMIN_CHAT_ID, "🖼️ أرسل الصورة مع النص (اختياري):")
                                broadcast_mode[user_id] = {"active": True, "type": "photo"}
                            
                            elif text == "👥 عدد المستخدمين":
                                users = get_all_users()
                                send_message(ADMIN_CHAT_ID, f"👥 عدد المستخدمين: {len(users)}")
                            
                            elif text == "🚫 طرد مستخدم":
                                send_message(ADMIN_CHAT_ID, "✍️ أرسل ID المستخدم:")
                                broadcast_mode[user_id] = {"active": True, "type": "ban"}
                            
                            elif text == "🔓 إلغاء طرد":
                                send_message(ADMIN_CHAT_ID, "✍️ أرسل ID المستخدم:")
                                broadcast_mode[user_id] = {"active": True, "type": "unban"}
                            
                            elif text == "⏸️ إيقاف المحادثات":
                                chat_enabled = False
                                send_message(ADMIN_CHAT_ID, "⏸️ تم إيقاف المحادثات.")
                            
                            elif text == "▶️ تشغيل المحادثات":
                                chat_enabled = True
                                send_message(ADMIN_CHAT_ID, "▶️ تم تشغيل المحادثات.")
                            
                            elif text == "📊 الإحصائيات":
                                users = get_all_users()
                                blacklist = load_blacklist()
                                pending = get_pending_requests()
                                send_message(ADMIN_CHAT_ID,
                                    f"📊 *الإحصائيات*\n\n"
                                    f"👥 المستخدمين: {len(users)}\n"
                                    f"🚫 المحظورين: {len(blacklist)}\n"
                                    f"📞 طلبات معلقة: {len(pending)}\n"
                                    f"💬 محادثات نشطة: {len(active_chats)}"
                                )
                            
                            elif text == "🔙 العودة للقائمة":
                                send_message(ADMIN_CHAT_ID, "🔙 تم العودة.", main_keyboard())
                            
                            elif text == "/cancel_broadcast":
                                if user_id in broadcast_mode:
                                    del broadcast_mode[user_id]
                                send_message(ADMIN_CHAT_ID, "❌ تم إلغاء البث.")
                            
                            # ======== معالجة البث النصي ========
                            elif user_id in broadcast_mode and broadcast_mode[user_id]["type"] == "text":
                                users = get_all_users()
                                if not users:
                                    send_message(ADMIN_CHAT_ID, "❌ لا يوجد مستخدمين.")
                                    del broadcast_mode[user_id]
                                    return
                                
                                send_message(ADMIN_CHAT_ID, f"📤 جاري الإرسال لـ {len(users)} مستخدم...")
                                success = 0
                                for user in users:
                                    if send_message(user, text):
                                        success += 1
                                    time.sleep(0.05)
                                send_message(ADMIN_CHAT_ID, f"✅ تم الإرسال: {success}/{len(users)}")
                                del broadcast_mode[user_id]
                            
                            # ======== معالجة الطرد ========
                            elif user_id in broadcast_mode and broadcast_mode[user_id]["type"] == "ban":
                                try:
                                    target_id = int(text.strip())
                                    if add_to_blacklist(target_id):
                                        send_message(ADMIN_CHAT_ID, f"✅ تم طرد `{target_id}`")
                                        send_message(target_id, "🚫 تم حظرك.")
                                    else:
                                        send_message(ADMIN_CHAT_ID, f"⚠️ `{target_id}` محظور بالفعل.")
                                except:
                                    send_message(ADMIN_CHAT_ID, "❌ ID غير صحيح.")
                                del broadcast_mode[user_id]
                            
                            elif user_id in broadcast_mode and broadcast_mode[user_id]["type"] == "unban":
                                try:
                                    target_id = int(text.strip())
                                    if remove_from_blacklist(target_id):
                                        send_message(ADMIN_CHAT_ID, f"✅ تم إلغاء طرد `{target_id}`")
                                    else:
                                        send_message(ADMIN_CHAT_ID, f"⚠️ `{target_id}` غير محظور.")
                                except:
                                    send_message(ADMIN_CHAT_ID, "❌ ID غير صحيح.")
                                del broadcast_mode[user_id]
                        
                        # ======== إنهاء المحادثة ========
                        elif text == "🔚 إنهاء المحادثة":
                            if user_id in active_chats:
                                del active_chats[user_id]
                                if user_id in admin_reply_mode:
                                    del admin_reply_mode[user_id]
                                send_message(chat_id, "🔚 تم إنهاء المحادثة.", main_keyboard())
                                send_message(ADMIN_CHAT_ID, f"🔚 المستخدم `{user_id}` أنهى المحادثة.")
                            else:
                                send_message(chat_id, "لا توجد محادثة نشطة.", main_keyboard())
                        
                        elif text == "🔙 العودة للقائمة":
                            send_message(chat_id, "🔙 تم العودة.", main_keyboard())
                        
                        # ======== رسالة من المستخدم في المحادثة ========
                        elif user_id in active_chats:
                            admin_msg = f"💬 *من العميل* `{user_id}`:\n\n{text}"
                            send_message(ADMIN_CHAT_ID, admin_msg, admin_reply_keyboard(user_id))
                            send_message(chat_id, "✅ تم الإرسال.")
                        
                        # ======== رسالة من المشرف ========
                        elif chat_id == ADMIN_CHAT_ID and user_id in admin_reply_mode:
                            target_user = admin_reply_mode[user_id]
                            send_message(target_user, f"📩 *من المدير:*\n\n{text}")
                            send_message(ADMIN_CHAT_ID, f"✅ تم الإرسال للعميل `{target_user}`")
                        
                        else:
                            send_message(chat_id, "❓ استخدم الأزرار.", main_keyboard())
                    
                    # ======== الصور ========
                    if "photo" in update.get("message", {}):
                        message = update["message"]
                        chat_id = message["chat"]["id"]
                        user_id = message["from"]["id"]
                        photo = message["photo"][-1]
                        file_id = photo["file_id"]
                        caption = message.get("caption", "")
                        
                        # البث بالصورة
                        if chat_id == ADMIN_CHAT_ID and user_id in broadcast_mode and broadcast_mode[user_id]["type"] == "photo":
                            users = get_all_users()
                            success = 0
                            for user in users:
                                if send_photo(user, file_id, caption):
                                    success += 1
                                time.sleep(0.05)
                            send_message(ADMIN_CHAT_ID, f"✅ تم الإرسال: {success}/{len(users)}")
                            del broadcast_mode[user_id]
                            continue
                        
                        # استلام إيصال
                        send_photo(ADMIN_CHAT_ID, file_id, f"📸 *إيصال جديد*\n👤 المستخدم: `{user_id}`")
                        send_message(chat_id, "✅ تم استلام إيصالك، سيتم مراجعته خلال 15 دقيقة.", main_keyboard())
                    
                    # ======== الأزرار ========
                    if "callback_query" in update:
                        callback = update["callback_query"]
                        callback_id = callback["id"]
                        data = callback["data"]
                        user_id = callback["from"]["id"]
                        
                        if data.startswith("accept_chat_"):
                            target_user_id = int(data.split("_")[2])
                            requests_data = load_chat_requests()
                            if str(target_user_id) in requests_data:
                                # قبول الطلب
                                active_chats[target_user_id] = True
                                admin_reply_mode[user_id] = target_user_id
                                update_chat_request(target_user_id, "accepted")
                                
                                send_message(ADMIN_CHAT_ID, f"✅ تم قبول محادثة `{target_user_id}`")
                                send_message(target_user_id, 
                                    "✅ *تم قبول طلب التواصل*\nيمكنك الآن مراسلة المدير.",
                                    end_chat_keyboard()
                                )
                                delete_chat_request(target_user_id)
                                
                                requests.post(f"https://api.telegram.org/bot{TOKEN}/answerCallbackQuery",
                                             json={"callback_query_id": callback_id, "text": "✅ تم القبول"})
                        
                        elif data.startswith("reject_chat_"):
                            target_user_id = int(data.split("_")[2])
                            if str(target_user_id) in load_chat_requests():
                                send_message(ADMIN_CHAT_ID, f"❌ تم رفض محادثة `{target_user_id}`")
                                send_message(target_user_id, "❌ تم رفض طلب التواصل.")
                                delete_chat_request(target_user_id)
                                
                                requests.post(f"https://api.telegram.org/bot{TOKEN}/answerCallbackQuery",
                                             json={"callback_query_id": callback_id, "text": "❌ تم الرفض"})
                        
                        elif data.startswith("reply_to_"):
                            target_user_id = int(data.split("_")[2])
                            if target_user_id in active_chats:
                                admin_reply_mode[user_id] = target_user_id
                                send_message(ADMIN_CHAT_ID, f"✉️ يمكنك الرد على العميل `{target_user_id}`")
                                requests.post(f"https://api.telegram.org/bot{TOKEN}/answerCallbackQuery",
                                             json={"callback_query_id": callback_id, "text": "✉️ اكتب رسالتك"})
                        
                        elif data.startswith("end_chat_"):
                            target_user_id = int(data.split("_")[2])
                            if target_user_id in active_chats:
                                del active_chats[target_user_id]
                            if target_user_id in admin_reply_mode:
                                del admin_reply_mode[target_user_id]
                            send_message(target_user_id, "🔚 تم إنهاء المحادثة من قبل المدير.", main_keyboard())
                            send_message(ADMIN_CHAT_ID, f"🔚 تم إنهاء المحادثة مع `{target_user_id}`")
                            requests.post(f"https://api.telegram.org/bot{TOKEN}/answerCallbackQuery",
                                         json={"callback_query_id": callback_id, "text": "🔚 تم الإنهاء"})
        
        except Exception as e:
            print(f"خطأ: {e}")
        time.sleep(1)

# ======== التشغيل ========
if __name__ == "__main__":
    print("="*50)
    print("🐋 بوت استثمار الحيتان - النسخة النهائية")
    print("="*50)
    
    # تشغيل التذكيرات
    threading.Thread(target=send_prayer_reminder, daemon=True).start()
    threading.Thread(target=send_morning_dhkir, daemon=True).start()
    threading.Thread(target=send_evening_dhkir, daemon=True).start()
    
    send_message(ADMIN_CHAT_ID, 
        "✅ *تم تشغيل البوت بنجاح!*\n\n"
        "📞 ميزة طلب التواصل مفعلة.\n"
        "🔄 يمكنك قبول أو رفض الطلبات.\n"
        "💬 المحادثات تعمل بشكل مباشر.\n\n"
        "📌 استخدم `/admin` للوحة التحكم."
    )
    
    print("✅ جاهز لاستقبال الأوامر...")
    handle_updates()