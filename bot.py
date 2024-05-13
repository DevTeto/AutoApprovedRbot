import os, random, traceback
import config

from pyrogram import filters, Client
from pyrogram.types import Message, ChatJoinRequest, InlineKeyboardButton, InlineKeyboardMarkup 
from pyrogram.errors import FloodWait, InputUserDeactivated, UserIsBlocked, PeerIdInvalid, ChatAdminRequired, UserNotParticipant

from database import add_user, add_group, all_users, all_groups, users, remove_user

app = Client("Auto Approve Bot", api_id=config.API_ID, api_hash=config.API_HASH, bot_token=config.BOT_TOKEN)

welcome=[
    "https://telegra.ph/file/51d04427815840250d03a.mp4",
    "https://telegra.ph/file/f41fddb95dceca7b09cbc.mp4",
    "https://telegra.ph/file/a66716c98fa50b2edd63d.mp4",
    "https://telegra.ph/file/17a8ab5b8eeb0b898d575.mp4",
]

#approve 
@app.on_chat_join_request()
async def approval(app: Client, m: ChatJoinRequest):
    usr = m.from_user
    cht = m.chat
    try:
        add_group(cht.id)
        await app.approve_chat_join_request(cht.id, usr.id)
        gif = random.choice(welcome)
        await app.send_animation(chat_id=usr.id, animation=gif, caption=f"Hey There {usr.first_name}\nWelcome To {cht.title}\n\n{usr.first_name} Your Request To Join {cht.title} Has Been Accepted By {app.me.first_name}")
        add_user(usr.id)
    except (UserIsBlocked, PeerIdInvalid):
        pass
    except Exception as err:
        print(str(err))   

#pvtstart
@app.on_message(filters.command("start") & filters.private)
async def start(app: Client, msg: Message):
    if config.FSUB:
        try:
            await app.get_chat_member(chat_id=config.CHANNEL, user_id=msg.from_user.id)
            add_user(msg.from_user.id)
            await msg.reply_photo(photo="https://telegra.ph/file/f394c45e5f2f147a37090.jpg", caption=f"⎉︙أهـلاً عـزيزي : {msg.from_user.mention}\n\n⎉︙اسمـي {app.me.mention}\n⎉︙استطيع قبول اي طلب انضمام بسهوله\n⎉︙فقط ارفعني مشرف واستمتع",
                                 reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton(f"اضف البوت الي مجموعتك✅", url=f"https://t.me/{app.me.username}?startgroup=true")], [InlineKeyboardButton("‹ قناه المطور ›", url=f"https://t.me/{config.CHANNEL}")]]))
        except UserNotParticipant:
            await msg.reply_text(text=f"⎉︙يجـب اولاً الاشتـراك بالقناه لاستخدامي\n\n {(await app.get_chat(config.CHANNEL)).title}\n⎉︙انضـم ثم ارسل /start", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("‹ اطغط هنا ›", url=f"https://t.me/{config.CHANNEL}")], [InlineKeyboardButton ("أضف البوت لمجموعتـك✅", url=f"https://t.me/{app.me.username}?start=start")]]))
        except ChatAdminRequired:
            await app.send_message(text=f"هذا الخيار مطور السورس فقط هو من يعرفه", chat_id=config.OWNER_ID)
    else:
        await msg.reply_photo(
            photo="https://telegra.ph/file/f394c45e5f2f147a37090.jpg",
            caption=f"⎉︙أهـلاً عـزيزي : {msg.from_user.mention}\n\n⎉︙اسمـي {app.me.mention}\n⎉︙استطيع قبول اي طلب انضمام بسهوله\n⎉︙فقط ارفعني مشرف واستمتع",
            reply_markup=InlineKeyboardMarkup(
                [
                    [
                        InlineKeyboardButton(f"أضـف البوت لمجموعتـك✅")
                    ],
                    [
                        InlineKeyboardButton("‹ قناه المطور ›", url=f"https://t.me/WX_PM")
                    ],
                ]
            )
        )
        add_user(msg.from_user.id)
        

#Gcstart and id
@app.on_message(filters.command("start") & filters.group)
async def gc(app: Client, msg: Message):
    add_group(msg.chat.id)
    add_user(msg.from_user.id)
    await msg.reply_text(text=f"⎉︙ ي عـزيزي : {msg.from_user.mention}\n\n- أرسلي خاص للحصول علي معلومات اكثر...", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("‹ اطغط هنا للبدأ ›", url=f"https://t.me/{app.me.username}?start=start")]]))

#stats
@app.on_message(filters.command("stats") & filters.user(config.OWNER_ID))
async def dbtool(app: Client, m: Message):
    xx = all_users()
    x = all_groups()
    await m.reply_text(text=f"Stats for {app.me.mention}\n🙋‍♂️ Users : {xx}\n👥 Groups : {x}")

#Broadcast
@app.on_message(filters.command("fbroadcast") & filters.user(config.OWNER_ID))
async def fcast(_, m : Message):
    allusers = users
    lel = await m.reply_text("`⚡️ Processing...`")
    success = 0
    failed = 0
    deactivated = 0
    blocked = 0
    for usrs in allusers.find():
        try:
            userid = usrs["user_id"]
            #print(int(userid))
            if m.command[0] == "fbroadcast":
                await m.reply_to_message.forward(int(userid))
            success +=1
        except FloodWait as ex:
            await asyncio.sleep(ex.value)
            if m.command[0] == "fbroadcast":
                await m.reply_to_message.forward(int(userid))
        except InputUserDeactivated:
            deactivated +=1
            remove_user(userid)
        except UserIsBlocked:
            blocked +=1
        except Exception as e:
            print(e)
            failed +=1

    await lel.edit(f"✅Successful Broadcast to {success} users.\n❌ Failed to {failed} users.\n👾 Found {blocked} Blocked users \n👻 Found {deactivated} Deactivated users.")
    


#run
print(f"Starting {app.name}")
try:
    app.run()
except:
    traceback.print_exc()
    
