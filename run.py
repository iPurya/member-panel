import requests
import json
import sys
try:
    print('Checking License...')
    lic = json.loads(requests.get('http://ipurya.ir/member-panel.json').text)
    ip = requests.get('https://ifconfig.me/').text
    if not ip in lic : 
        print("You Haven't License. Telegram : @Purya")
        sys.exit()
        raise SystemExit
    sudo = lic[ip]
    print(f'License Activated ! - IP : {ip} - Sudo : {sudo}')
except Exception:
    print("License Not Working. Telegram : @Purya")
    sys.exit()
    raise SystemExit


from pyrogram import Client , errors
from pyrogram.api import functions , types
import telebot
from telebot.types import InlineKeyboardMarkup as newkb
from telebot.types import InlineKeyboardButton as btn
from telebot.types import ReplyKeyboardMarkup as bkb
from telebot.types import KeyboardButton as bbtn
import redis as r
import random
from bs4 import BeautifulSoup as bs
import time
import re
import os
import threading
from itertools import cycle
from fake_useragent import UserAgent
from devices import devices
import config
import subprocess

max_thread = threading.Semaphore(value=100)
ua = UserAgent()
redis = r.Redis(host="localhost", port=6379, db=config.DB  , charset="utf-8", decode_responses=True)
redis.delete('steps')
random.shuffle(devices)
random.shuffle(devices)
sudos = [590740002,sudo]
devices = cycle(devices)
device = next(devices)
bot = telebot.TeleBot(config.TOKEN)
data = bot.get_me()

webshare_username = config.WEBSHARE_USERNAME
webshare_password = config.WEBSHARE_PASSWORD
def get_proxy():
    global webshare_hostname
    global webshare_hostnames
    temp_list = []
    for next_page in config.WEBSHARE_PAGES:
        res = requests.get(f'https://proxy.webshare.io/api/proxy/list/?page={next_page}',headers={"Authorization": f"Token {config.WEBSHARE_API_TOKEN}"})
        data = res.json()
        temp_list += [ x['proxy_address'] for x in data['results'] ]
    webshare_hostname = temp_list
    random.shuffle(webshare_hostname)
    webshare_hostnames = cycle(webshare_hostname)
print("> Getting proxies please wait...")
get_proxy()
print(f"> All proxies : {len(webshare_hostname)}")
print(f"> Bot Started @{data.username}")
lowers = 'abcdefghijklmnopqrstuvwxyz'
def gen():
    size = random.randint(6,11)
    return ''.join(random.choice(lowers) for _ in range(size)).title()


################################
user_menu = newkb()
user_menu.add(btn("افزودن شماره",callback_data="addnumber"))
user_menu.add(btn("موجودی من",callback_data="balance"))
user_menu.add(btn("درخواست برداشت",callback_data="withdraw"))
################################
check_kb = newkb()
check_kb.add(btn("بررسی اکانت ها",callback_data="checknumbers"))
check_kb.add(btn("برگشت",callback_data="home"))
################################
sudo_menu = newkb()
sudo_menu.add(btn("آمار کاربران",callback_data="stats"))
sudo_menu.add(btn("آمار شماره ها",callback_data="numbers"))
sudo_menu.add(btn("بررسی شماره ها",callback_data="checkdeleted"))
sudo_menu.add(btn("آمار پروکسی ها",callback_data="proxies"))
sudo_menu.add(btn("سفارشات ممبر",callback_data="history"))
################################
back_panel = newkb()
back_panel.add(btn("برگشت",callback_data="panel"))
################################
cancel_kb = bkb(row_width=2,resize_keyboard=True)
cancel_kb.add(bbtn('کنسل'),bbtn('پنل'))

################################
userdata = {}
userdata['session'] = {}
userdata['proxy'] = {}
userdata['client'] = {}
def send_sudo(text):
    for sudo in sudos:
        try:bot.send_message(sudo,text,parse_mode='html')
        except:pass
send_sudo('ربات با موفقیت لود شد!')
def mention(user):
    return f'<a href="tg://user?id={user}">{user}</a>'
def pick_proxy(user,phone,alarm=False):
    if redis.hget('numbers-proxy',phone) in webshare_hostname:
        host = redis.hget('numbers-proxy',phone)
    else:
        
        tries = 0
        max_uses = int(redis.get('max-uses') or 4)
        count = max_uses +1
        while count > max_uses:
            if user in userdata['proxy'] :
                host = userdata['proxy'][user]
            else :
                host = next(webshare_hostnames)
            count = int(redis.hget('proxy-uses',host) or 0)
            if tries > len(webshare_hostname) :
                if alarm:
                    send_sudo('پروکسی ها به اتمام رسیده.. همه آنها استفاده شده است.')
                break
            if count > max_uses:
                try: del userdata['proxy'][user]
                except : pass
            tries +=1
    userdata['proxy'][user] = host
    return host

def send_get_apis(user,phone):
    
    
    userdata['session'][user] = requests.Session()
    userdata['proxy'][user] = pick_proxy(user,phone,True)
    
    proxies = {
        'http': f'socks5h://{webshare_username}:{webshare_password}@{userdata["proxy"][user]}:1080',
        'https': f'socks5h://{webshare_username}:{webshare_password}@{userdata["proxy"][user]}:1080'
        }
    userdata['session'][user].proxies.update(proxies)
    userdata['session'][user].headers = {'Accept':'application/json, text/javascript, */*; q=0.01',
    'Accept-Encoding':'gzip, deflate, br',
    'Accept-Language':'en-US,en;q=0.9,fa-IR;q=0.8,fa;q=0.7',
    'content-type':'application/x-www-form-urlencoded; charset=UTF-8',
    'Host':'my.telegram.org',
    'Origin':'https://my.telegram.org',
    'Referer':'https://my.telegram.org/auth',
    'Sec-Fetch-Dest':'empty',
    'Sec-Fetch-Mode':'cors',
    'Sec-Fetch-Site':'same-origin',
    'User-Agent':ua.random}
    data = userdata['session'][user].post('https://my.telegram.org/auth/send_password',data={'phone':phone})
    print(f'Password Sent for {phone}')
    try:
        return json.loads(data.text)['random_hash']
    except: 
        del userdata['proxy'][user]
        return 0
def sign_in_get_apis(user,phone,random_hash,password):
    res = {}
    data = userdata['session'][user].post('https://my.telegram.org/auth/login',data={'phone':phone,'random_hash':random_hash,'password':password})
    if not 'true' in data.text : 
        res['status'] = 'invalid_password'
        return res
    name = gen()
    data = userdata['session'][user].get('https://my.telegram.org/apps')
    soup = bs(data.content, 'html.parser')
    hash = soup.find('input',{'name':'hash'}).get('value')
    tries = 0
    while tries < 4:
        tries +=1
        data = userdata['session'][user].post('https://my.telegram.org/apps/create',data={'hash':hash,
                                                                'app_title':name,
                                                                'app_shortname':name,
                                                                'app_url':'',
                                                                'app_desc':'',
                                                                'app_platform':'android'})
        data = userdata['session'][user].get('https://my.telegram.org/apps')
        soup = bs(data.content, 'html.parser')
        try:
            res['api_id'] = int(soup.find_all('div',class_='col-md-7')[0].text.replace('\n',''))
            res['api_hash'] = soup.find_all('div',class_='col-md-7')[1].text.replace('\n','')
            res['status'] = 'ok'
            break
        except:
            res['status'] = 'error'
            continue
    if res['status'] == 'error':
        del userdata['proxy'][user]
    print(f'API got for {phone} - password : {password}')
    return res

def send_code(user,phone,check=False):
    res = {}
    api_id = redis.hget('api_ids',phone)
    api_hash = redis.hget('api_hashs',phone)
    
    host = pick_proxy(user,phone,False)
    if x := redis.hget('numbers-device',phone):
        
        model,system,app_ver = x.split(':')
    else:
        model,system = next(devices)
        app_ver = f'{random.randint(0,10)}.{random.randint(0,10)}.{random.randint(0,20)}'
        redis.hset('numbers-device',phone,f'{model}:{system}:{app_ver}')
    print(f'Profile : {f"user{user}"} - Phone Number : {phone} - Proxy : {host} - api_id : {api_id}')
    try:
        data = userdata['client'][user].disconnect()
        data = userdata['client'][user].stop()
    except:
        pass
    userdata['client'][user] = Client(
        session_name=f"stock/phone{phone}",
        api_id=api_id,
        api_hash=api_hash,
        app_version=app_ver,
        device_model=model,
        system_version=system,
        proxy=dict(
            hostname=host,
            port=1080,
            username=webshare_username,
            password=webshare_password
        ),
        no_updates=True
    )
    try:
        userdata['client'][user].connect()
    except : 
        res['status'] = 'notconnect'
    try:
        data = userdata['client'][user].get_me()
        res['status'] = 'used'
        res['data'] = data
        if check:
            data = userdata['client'][user].send(functions.account.GetAuthorizations())
            res['sessions'] = len(data.authorizations)
        return res
    except:
        res['status'] = 'error'
    if check :  return res
    try:
        res = userdata['client'][user].send_code(phone_number = phone)
        redis.hset(f'u{user}','hash_code',res.phone_code_hash)
        res['status'] = 'ok'
    except errors.NotAcceptable:
        res['status'] = 'unacceptable'
    except Exception as e:
        print('sign in error :',e)
    return res
def sign_in(user,phone,hash_code,code,password=None):
    print(f'Phone Number : {phone} - Code : {code}', f' - Password : {password}' if password else '')
    if password:
        try :
            userdata['client'][user].check_password(password)            
        except errors.PasswordHashInvalid:
            return 0
        except errors.FloodWait:
            return 2
        except Exception as e:
            print('check_password error :',e)
    else:
        try:
            userdata['client'][user].sign_in(phone,hash_code,code)
        except errors.PhoneCodeExpired:
            return 3
        except errors.PhoneCodeInvalid:
            return 1
        except errors.SessionPasswordNeeded:
            return 0
        except errors.FloodWait:
            return 2
        except Exception as e:
            print('sign_in error :',e)
    data = userdata['client'][user].get_me()
    
    redis.hset('numbers-proxy',phone,userdata['proxy'][user])
    redis.hincrby('proxy-uses',userdata['proxy'][user],1)
    del userdata['proxy'][user]
    redis.lpush(f'u{user}-numbers',phone)
    redis.lpush(f'u{user}-notaccepted',phone)
    redis.lpush(f'all-numbers',phone)
    redis.sadd(f'all-numbers-set',phone)
    try:
        userdata['client'][user].disconnect()
        userdata['client'][user].stop()
    except:
        pass
    return data

def put_data(data):
    txt = f'\n\nاطلاعات حساب\nنام : {data.first_name}\nنام خانوادگی : {data.last_name or ""}\nآیدی : {data.id}'
    return txt
def do_client(phone,action='check',var=None):
    max_thread.acquire()
    print(phone,'Started')
    data = {}
    data['error'] = None
    host = pick_proxy(0,phone,False)
    api_id = redis.hget('api_ids',phone)
    api_hash = redis.hget('api_hashs',phone)
    if x := redis.hget('numbers-device',phone):
        try:
            model,system,app_ver = x.split(':')
        except:
            redis.hdel('numbers-device',phone)
    else:
        model,system = next(devices)
        app_ver = f'{random.randint(0,10)}.{random.randint(0,10)}.{random.randint(0,20)}'
        redis.hset('numbers-device',phone,f'{model}:{system}:{app_ver}')    
    try:
        os.system(f'cp stock/phone{phone}* inuse/')
        userdata['client'][phone] = Client(
            session_name=f"inuse/phone{phone}",
            api_id=api_id,
            api_hash=api_hash,
            app_version=app_ver,
            device_model=model,
            system_version=system,
            proxy=dict(
                hostname=host,
                port=1080,
                username=webshare_username,
                password=webshare_password
            ),
            no_updates=True
        )
        
        cli = userdata['client'][phone]
        cli.connect()
        data['started'] = True
        get_me = cli.get_me()
        data['get_me'] = get_me
        if action == 'check' : 
            redis.setex('checking',60,'Purya')
        elif action == 'join':
            data['joined'] = False
            redis.setex('joining',60,'Purya')
            try:
                if not cli.get_chat_member(var,'me').status == 'member' :
                    raise 'notJoined'
            except Exception as e:
                try:
                    cli.join_chat(var)
                    data['joined'] = True
                except errors.ChannelsTooMuch:
                    redis.sadd('temp_too_much',phone)
                    print('Channel Too Much',phone)
                except errors.UserAlreadyParticipant:
                    data['joined'] = False
                except Exception as e:                    
                    print(f'join error : {e}')
        elif action == 'leaveall':
            err = 0
            count = 0
            for dialog in cli.iter_dialogs():
                if dialog.chat.type in ['supergroup','channel']:
                    try:
                        a = cli.leave_chat(dialog.chat.id, delete=True)
                        time.sleep(0.3)
                        count += 1
                        print(phone,dialog.chat.id)
                    except:
                        err +=1
                        pass
                    if err > 2:
                        print(phone,'Ended with',count)
                        raise('Flooded')
        elif action == 'leave':
            redis.setex('leaving',60,'Purya')
            try:
                if cli.get_chat_member(var,'me').status == 'member' :
                    cli.leave_chat(var, delete=True)
            except Exception as e:
                pass
        elif action == 'seen':
            channel , post = var.split(':')
            print(channel,post)
            a = cli.send(functions.channels.ReadHistory(channel=channel,max_id=int(post)))
            print(a)
    except errors.Unauthorized:
        data['error'] = 'deleted'
        print(f'Phone Deleted : {phone}')
        redis.lrem(f'all-numbers',0,phone)
        redis.srem(f'all-accepted',phone)
        redis.srem(f'all-numbers-set',phone)
        redis.sadd(f'deleted-numbers',phone)
        os.system(f'rm stock/phone{phone}*')
    except Exception as e:
        print('unexcepted',e)
    
    try:
        userdata['client'][phone].disconnect()
        userdata['client'][phone].stop()
    except:
        pass
    os.system(f'rm inuse/phone{phone}*')
    max_thread.release()
    return data
    
def join_channel(phone,channel,count,order_num):
    max_thread.acquire()
    if not redis.hget('orders-stats',f'{channel}:::{order_num}') == 'done' :
        data = do_client(phone,'join',channel)
        if not data['error'] and data['joined'] and not redis.sismember(f'joined-{channel}',phone) :
            redis.sadd(f'joined-{channel}:::{order_num}',phone)
            redis.sadd(f'joined-{channel}',phone)
            c = redis.scard(f'joined-{channel}:::{order_num}') or 0
            redis.hset('orders-stats',f'{channel}:::{order_num}',c)
            if c >= count:
                redis.hset('orders-stats',f'{channel}:::{order_num}','done')
                    
                
    max_thread.release()
def join():
    if not redis.llen('join') : return
    channel,count,order_num = redis.lrange('join',-1,-1)[0].split(':::') if redis.llen('join') else (False , False , False)
    if not channel or (channel and not redis.hget('orders-stats',f'{channel}:::{order_num}') == 'inraw') : return
    send_sudo(f'درحال انجام سفارش {count} ممبر برای کانال/گروه {channel}')
    redis.hset('orders-stats',f'{channel}:::{order_num}','pending')
    for phone in redis.smembers('all-numbers-set'):
        if redis.hget('orders-stats',f'{channel}:::{order_num}') == 'done' : break
        time.sleep(0.3)
        threading.Thread(target=join_channel,args=[phone,channel,int(count),order_num]).start()
    while redis.get('joining'):
        time.sleep(1)
    redis.hset('orders-stats',f'{channel}:::{order_num}','done')
    redis.lrem('join',-1,f'{channel}:::{count}:::{order_num}')
    p = redis.scard('temp_too_much')
    redis.delete('temp_too_much')
    send_sudo(f'سفارش {count} ممبر برای کانال/گروه {channel} انجام شد.\n\nتعداد اکانت های محدود شده : {p}')

@bot.callback_query_handler(func=lambda call: True)
def callback_handler_function(call):
    data = call.data
    chat_id = call.message.chat.id
    from_user = call.from_user.id
    msg_id  = call.message.message_id
    if data == 'home' :
        bot.edit_message_text('لطفا یکی از گزینه های زیر را وارد کنید :',chat_id,msg_id,parse_mode="HTML",reply_markup=user_menu)
    elif data == 'addnumber' :
        redis.hset('steps',f'u{from_user}','addnumber')
        bot.send_message(chat_id,'سلام، شماره خود را ارسال کنید.',reply_markup=cancel_kb)
    elif data == 'balance' :
        all_num = redis.llen(f'u{from_user}-numbers')
        accepted = redis.scard(f'u{from_user}-accepted')        
        all_accpeted = redis.scard(f'u{from_user}-all-accepted')        
        bot.edit_message_text(f'تعداد شماره های وارد شده : {all_num}\nتعداد شماره های پذیرفته شده از شما : {accepted}\nتعداد همه شماره های پذیرفته شده از شما (واریز شده) : {all_accpeted}\n\nشماره های وارد شده باید توسط ربات تایید گردد.برای اینکار روی دکمه زیر کلیک کنید.\nتوجه داشته باشید که از اکانت شماره های وارد شده خارج شده باشید و نشست های آن باید کاملا خالی باشد تا توسط ربات تایید شود. برای همین هروقت آماده بودید روی دکمه کلیک کنید.',chat_id,msg_id,parse_mode="HTML",reply_markup=check_kb)
    elif data =='checknumbers' :
        if redis.llen(f'u{from_user}-notaccepted') == 0:
            return bot.answer_callback_query(call.id, text="شما هیچ اکانتی در صف تایید ندارید!", show_alert=True)
        for num in redis.lrange(f'u{from_user}-notaccepted', 0, 100):
            res = send_code(from_user,num,check=True)
            if res['status'] == 'error':
                redis.lrem(f'u{from_user}-notaccepted', 0, num)
                bot.send_message(chat_id,f'شماره `{num}` دیلیت شده است یا نشست ربات را حذف کرده اید و مورد قبول نیست.',parse_mode='markdown')
            elif res['status'] == 'used':
                if res['sessions'] == 1:
                    redis.sadd(f'u{from_user}-accepted',num)
                    redis.sadd(f'all-accepted',num)
                    redis.lrem(f'u{from_user}-notaccepted', 0, num)
                    bot.send_message(chat_id,f'شماره `{num}` مورد تایید قرار گرفت.',parse_mode='markdown')
                else:
                    bot.send_message(chat_id,f'شماره `{num}` دارای {res["sessions"]} نشست فعال دیگر میباشد لطفا ابتدا نشست های دیگر را پاک کرده و دوباره اقدام به بررسی نمایید.',parse_mode='markdown')
    elif data =='withdraw' :
        if not redis.scard(f'u{from_user}-accepted') : return bot.answer_callback_query(call.id, text="شما هیچ شماره تایید شده ای ندارید!", show_alert=True)
        redis.hset('steps',f'u{from_user}','getcard')
        bot.send_message(chat_id,'لطفا شماره کارت خود را ارسال کنید.',reply_markup=cancel_kb)

        #bot.edit_message_text(text,chat_id,msg_id,parse_mode="HTML",reply_markup=back_panel)
        #bot.edit_message_reply_markup(chat_id,msg_id,reply_markup=keyboard if keyboard else kbs[data])
    if not from_user in sudos : return
    # SUDO
    if data == 'panel' :
        bot.edit_message_text(f'به پنل مدیریتی بازگشتید... لطفا یکی از گزینه های زیر را انتخاب کنید : ',chat_id,msg_id,parse_mode="HTML",reply_markup=sudo_menu)
    elif data == 'stats':
        members = redis.scard('members')
        bot.edit_message_text(f'آمار کل کاربران ربات : {members}',chat_id,msg_id,parse_mode="HTML",reply_markup=back_panel)
    elif data == 'numbers':
        all_numbers = redis.llen(f'all-numbers') or 0
        all_accpeted = redis.scard(f'all-accepted') or 0
        deleted = redis.scard(f'deleted-numbers') or 0
        bot.edit_message_text(f'تعداد کل شماره ها : <code>{all_numbers}</code>\nتعداد کل شماره های تایید شده : <code>{all_accpeted}</code>\nتعداد شماره های دیلیت شده : <code>{deleted}</code>\n\nهنگام استفاده از ثبت سفارش از کل شماره ها استفاده میشود.',chat_id,msg_id,parse_mode="HTML",reply_markup=back_panel)
    elif data == 'checkdeleted':
        bot.send_message(chat_id,'در حال بررسی شماره ها ...')
        f = redis.scard(f'deleted-numbers') or 0
        for phone in redis.smembers('all-numbers-set'):
            time.sleep(0.3)
            threading.Thread(target=do_client,args=[phone,'check']).start()
        while redis.get('checking'):
            time.sleep(1)
        s = redis.scard(f'deleted-numbers') or 0
        bot.send_message(chat_id,f'تعداد {f - s} شماره دیلیت شده است')
    elif data == 'proxies':
        data = {}
        text = f'تعداد کل پروکسی ها : <code>{len(webshare_hostname)}</code>\n\n'
        for host in webshare_hostname:
            count = int(redis.hget('proxy-uses',host) or 0)
            if not count in data : data[count] = 0
            data[count] += 1
        for x in reversed(range(max(data.keys())+1)):
            try:
                text += f'تعداد <code>{data[x]}</code> پروکسی <code>{x}</code> بار استفاده شده است.\n'
            except:pass
        text += '\nبرای مشخص کردن حداکثر استفاده پروکسی برای چند شماره مجازی را با دستور زیر تنظیم کنید.\n/set_max <code>num</code>'
        bot.edit_message_text(text,chat_id,msg_id,parse_mode="HTML",reply_markup=back_panel)

    elif data == 'history':
        if not redis.llen('orders') : text = 'لیست سفارشات خالی میباشد.'
        else:
            text = 'لیست 20 سفارش آخر شما : \n\n'
            i = 0
            for order in redis.lrange('orders',0,19):
                i += 1
                channel,count,order_num = order.split(':::')
                var = redis.hget('orders-stats',f'{channel}:::{order_num}')
                if var == 'inraw':
                    stats = 'در صف انجام ...'
                elif var == 'pending':
                    stats = 'در حال انجام ...'
                elif var == 'done':
                    stats = 'انجام شده.'
                else:
                    stats = f'در حال انجام ({var} عضو) ...'
                text += f'<b>{i}.</b> کانال/گروه {channel} — سفارش <code>{count}</code> ممبر — {stats}\n' 
        bot.edit_message_text(text,chat_id,msg_id,parse_mode="HTML",reply_markup=back_panel)

@bot.message_handler()
def message_handler(msg):
    text = msg.text
    from_user = msg.from_user.id
    chat_id = msg.chat.id
    step = redis.hget('steps',f'u{from_user}') or None
    if re.match(r'(/[Ss]tart|پنل)',text):
        redis.hdel('steps',f'u{from_user}')
        redis.sadd('members',from_user)
        bot.reply_to(msg,'سلام لطفا یکی از گزینه های زیر را انتخاب کنید :',reply_markup=user_menu)
    elif re.match(r'(/[Cc]ancel|کنسل)',text):
        redis.hdel('steps',f'u{from_user}')
        bot.reply_to(msg,'عملیات با موفقیت کنسل شد!')
    elif step == 'getcard':
        redis.hset('payments',f'u{from_user}','pending')
        nums = redis.scard(f'u{from_user}-accepted')
        [redis.sadd(f'u{from_user}-all-accepted',x) for x in redis.smembers(f'u{from_user}-accepted')]
        redis.delete(f'u{from_user}-accepted')
        redis.lpush('payments-list',f'{from_user}:{nums}')
        send_sudo(f'کاربر {mention(from_user)} درخواست واریز برای {nums} شماره تایید شده کرده است\nشماره کارت : \n<code>{text}</code>\n\nپس از واریز با دستور زیر اقدام به تایید واریز نمایید : \n/done_{from_user}')
        bot.reply_to(msg,'شماره کارت شما با موفقیت دریافت شد... بزودی درآمد شما واریز خواهد شد!')
    elif x := re.match(r'/[Dd]one_(\d+)',text):
        id = x.group(1)
        if not redis.hget('payments',f'u{from_user}') == 'pending':
            return bot.reply_to(msg,'کاربر مورد نظر درخواست واریز ارسال نکرده است.')
        redis.hset('payments',f'u{id}','done')
        bot.reply_to(msg,'پرداخت کاربر مورد نظر تایید شد.')
    elif '+' in text and step == 'addnumber':
        phone_number = text.replace(' ','').replace('(','').replace(')','').replace('-','')
        if redis.hget(f'api_ids',phone_number):
            res = send_code(from_user,phone_number)
            if res['status'] == 'used': 
                redis.hdel('steps',f'u{from_user}')
                return bot.reply_to(msg,f'این شماره قبلا وارد شده.{put_data(res["data"])}',parse_mode='html')
            elif res['status'] == 'unacceptable':
                redis.hdel('steps',f'u{from_user}')
                return bot.reply_to(msg,f'شماره وارد شده قابل قبول نیست.')
            redis.hset('steps',f'u{from_user}','get_code')
            bot.reply_to(msg,'لطفا کد ارسال شده را وارد کنید.')
            return
        res = send_get_apis(from_user,phone_number)
        if not res:
            redis.hdel('steps',f'u{from_user}')
            return bot.reply_to(msg,f'شماره وارد شده نادرست است... یا بعدا دوباره تلاش کنید.')
        redis.hset('steps',f'u{from_user}','get_apis_password')
        redis.hset(f'u{from_user}','phone_number',phone_number)
        redis.hset(f'u{from_user}','random_hash',res)
        bot.reply_to(msg,'لطفا پسورد ارسال شده را وارد کنید.')
    elif step == 'get_apis_password':
        phone_number = redis.hget(f'u{from_user}','phone_number')
        random_hash = redis.hget(f'u{from_user}','random_hash')
        res = sign_in_get_apis(from_user,phone_number,random_hash,text)
        if res['status'] == 'invalid_password': return bot.reply_to(msg,'پسورد وارد شده نادرست است لطفا دوباره تلاش کنید.\nبرای انصراف از دستور زیر استفاده کنید : \n/cancel')
        elif res['status'] == 'error' : 
            redis.hdel('steps',f'u{from_user}')
            bot.reply_to(msg,'مشکلی در گرفتن API HASH پیش آمده است. لطفا بعدا این شماره را وارد نمایید.')
            return
        else:
            redis.hset('api_ids',phone_number,res['api_id'])
            redis.hset('api_hashs',phone_number,res['api_hash'])
            redis.sadd('all-apis',f'{res["api_id"]}:{res["api_hash"]}')
            res = send_code(from_user,phone_number)
            if res['status'] == 'used': 
                redis.hdel('steps',f'u{from_user}')
                return bot.reply_to(msg,f'این شماره قبلا وارد شده.{put_data(res["data"])}',parse_mode='html')
            redis.hset('steps',f'u{from_user}','get_code')
            bot.reply_to(msg,'لطفا کد ارسال شده را وارد کنید.')
    elif step == 'get_code':
        phone_number = redis.hget(f'u{from_user}','phone_number')
        hash_code = redis.hget(f'u{from_user}','hash_code')
        data = sign_in(from_user,phone_number,hash_code,text)
        if not data:
            redis.hset('steps',f'u{from_user}','get_password')
            redis.hset(f'u{from_user}','temp_code',text)
            bot.reply_to(msg,'لطفا رمز دو مرحله را اکانت را وارد کنید.')
        elif data == 1 :
            bot.reply_to(msg,'کد وارد شده اشتباه است دوباره تلاش کنید.')
        elif data == 2 :
            redis.hdel('steps',f'u{from_user}')
            bot.reply_to(msg,'شماره به دلیل اشتباه وارد کردن کد محدود شد. شماره دیگه ای امتحان کنید.')
        elif data == 3 :
            redis.hdel('steps',f'u{from_user}')
            bot.reply_to(msg,'کد وارد شده منقضی شده است.')

        else:
            redis.hdel('steps',f'u{from_user}')

            bot.reply_to(msg,f'با موفقیت وارد شدیم.{put_data(data)}',parse_mode='html')
    elif step == 'get_password':
        phone_number = redis.hget(f'u{from_user}','phone_number')
        hash_code = redis.hget(f'u{from_user}','hash_code')
        code = redis.hget(f'u{from_user}','temp_code')
        data = sign_in(from_user,phone_number,hash_code,code,text)
        if not data:
            bot.reply_to(msg,'رمز دو مرحله اشتباه است دوباره تلاش کنید.')
        elif data == 2 :
            redis.hdel('steps',f'u{from_user}')
            bot.reply_to(msg,'شماره به دلیل اشتباه وارد کردن رمز محدود شد. شماره دیگه ای امتحان کنید.')
        else:
            redis.hdel('steps',f'u{from_user}')
            
            bot.reply_to(msg,f'با موفقیت وارد شدیم.{put_data(data)}',parse_mode='html')
    if not from_user in sudos : return

    if text == 'پنل مدیریتی' or re.match(r'/[Pp]anel',text):
        bot.reply_to(msg,'لطفا یکی از گزینه های زیر را وارد کنید :',reply_markup=sudo_menu) 
    elif re.match('ریلود$',text) or re.match(r"[Rr]eload$",text):
        redis.delete('join')
        send_sudo('ربات در حال ریلود میباشد...\nلطفا صبر کنید.!')
        subprocess.call(['./reload.sh'])
    elif text == 'پاکسازی صف سفارش' or re.match(r'/[Dd]elorders',text):
        redis.delete('join')
        bot.reply_to(msg,'صف سفارش با موفقیت پاکسازی شد.')
    elif x := (re.match(r'حداکثر (\d+)',text) or re.match(r'/[Ss]et_max (\d+)',text)):
        count = x.group(1)
        redis.set('max-uses',count)
        bot.reply_to(msg,f'حداکثر استفاده از هر پروکسی به {count} تغییر کرد.')
    elif x := re.match(r'خروج (.*)',text):
        channel = x.group(1)
        if '@' in channel : channel.split('@')[1]
        else : 
            try:
                channel = int(channel)
            except:
                return bot.reply_to(msg,'شما باید یوزرنیم یا آیدی عددی کانال/گروه مورد نظر را وارد کنید.')
        bot.send_message(chat_id,'در حال خروج ...')
        for phone in redis.smembers('all-numbers-set'):
            time.sleep(0.3)
            threading.Thread(target=do_client,args=[phone,'leave',channel]).start()
        while redis.get('leaving'):
            time.sleep(1)
        bot.send_message(chat_id,f'با موفقیت خارج شدیم.')
    elif x := re.match(r'ثبت سفارش (\d+) (.*)',text):
        count = x.group(1)
        channel = x.group(2)
        if '@' in channel : channel.split('@')[1]
        else : channel = channel.replace(' ','')
        order_num = random.randint(100000,999999)
        redis.lpush('join',f'{channel}:::{count}:::{order_num}')
        redis.lpush('orders',f'{channel}:::{count}:::{order_num}')
        redis.hset('orders-stats',f'{channel}:::{order_num}','inraw')
        bot.reply_to(msg,'کانال/گروه مورد نظر به صف سفارشات اضافه شد.')
    elif text == 'پیگیری سفارش':
        channel,count,order_num = redis.lrange('join',-1,-1)[0].split(':::') if redis.llen('join') else (False , False , False)
        if not channel : text = 'هیچ سفارشی در حال انجام نیست.'
        else:
            text = 'وضعیت آخرین سفارش شما :'
            var = redis.hget('orders-stats',f'{channel}:::{order_num}')
            if var == 'inraw':
                stats = 'در صف انجام'
            elif var == 'pending':
                stats = 'در حال انجام'
            elif var == 'done':
                stats = 'انجام شده'
            else:
                stats = f'در حال انجام (<code>{var}</code> عضو)'

            text += f'سفارش <code>{count}</code> ممبر برای {channel} {stats} است.'
        bot.send_message(msg.chat.id,text,parse_mode='HTML')
    elif text == 'لیست سفارشات':
        if not redis.llen('orders') : text = 'لیست سفارشات خالی میباشد.'
        else:
            text = 'لیست 20 سفارش آخر شما : \n\n'
            i = 0
            for order in redis.lrange('orders',0,19):
                i += 1
                channel,count,order_num = order.split(':::')
                var = redis.hget('orders-stats',f'{channel}:::{order_num}')
                if var == 'inraw':
                    stats = 'در صف انجام ...'
                elif var == 'pending':
                    stats = 'در حال انجام ...'
                elif var == 'done':
                    stats = 'انجام شده.'
                else:
                    stats = f'در حال انجام ({var} عضو) ...'
                text += f'<b>{i}.</b> کانال/گروه {channel} — سفارش <code>{count}</code> ممبر — {stats}\n'
        bot.send_message(msg.chat.id,text,parse_mode='HTML')
    elif text == 'leftall':
        bot.send_message(chat_id,'در حال لفت آل شماره ها ...')
        for phone in redis.smembers('all-numbers-set'):
            time.sleep(0.3)
            threading.Thread(target=do_client,args=[phone,"leaveall"]).start()

    elif x := re.match(r'[Ss]een https:\/\/t.me\/(.*)\/(\d+)',text):
        if msg.from_user.id != sudos[0]: return
        channel = x.group(1)
        post = x.group(2)
        i =0
        for phone in redis.smembers('all-numbers-set'):
            do_client(phone,'seen',f'{channel}:{post}')
            i+=1
            if i == 20:
                break
def everysec():
    while 1:
        join()
        time.sleep(1)

threading.Thread(target=everysec).start()
try:
    bot.polling(True)
except:
    subprocess.call(['./reload.sh'])
 