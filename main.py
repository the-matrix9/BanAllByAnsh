import random
import os
import logging
import asyncio
from pyrogram import enums
from pyrogram.enums import ChatMembersFilter, ChatMemberStatus, ChatType
from pyrogram.types import ChatPermissions
from flask import Flask
from threading import Thread
from pymongo import MongoClient, errors
from pyrogram import Client, filters, idle
from pyrogram.errors import FloodWait, UserNotParticipant, RPCError
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton,CallbackQuery
from time import time
import sys

# Logging setup
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logging.getLogger("pyrogram").setLevel(logging.WARNING)

# Flask app
app_web = Flask(__name__)

@app_web.route('/')
def home():
    return "Shivi Bot is Running!"

def run_flask():
    app_web.run(host="0.0.0.0", port=8080)

# Config vars
API_ID = int(os.getenv("API_ID","14050586"))
API_HASH = os.getenv("API_HASH","42a60d9c657b106370c79bb0a8ac560c")
BOT_TOKEN = os.getenv("BOT_TOKEN","7590282379:AAFtKL-N0sCYGuvjvL0ZxppTiSIk2xa1kcQ")
BOT_USERNAME = os.getenv("BOT_USERNAME","AnshControler_Bot")
MONGO_URI = os.getenv("MONGO_URI","mongodb+srv://Krishna:pss968048@cluster0.4rfuzro.mongodb.net/?retryWrites=true&w=majority")
OWNER_ID = int(os.getenv("OWNER_ID","6258915779"))
FORCE_JOIN1 = os.getenv("FORCE_JOIN1","UR_RISHU_143")
FORCE_JOIN2 = os.getenv("FORCE_JOIN2","SparkCodez")

# MongoDB setup
try:
    client = MongoClient(MONGO_URI)
    db = client["banall_bot"]
    users_col = db["users"]
except errors.ConnectionFailure as e:
    logging.error(f"Failed to connect to MongoDB: {e}")
    sys.exit(1)

# Pyrogram bot
bot = Client(
    "banall",
    api_id=API_ID,
    api_hash=API_HASH,
    bot_token=BOT_TOKEN,
)
app = Client("my_bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

async def check_force_join(user_id):
    """Check if the user is a member of both required channels."""
    try:
        await bot.get_chat_member(FORCE_JOIN1, user_id)
        await bot.get_chat_member(FORCE_JOIN2, user_id)
        return True
    except UserNotParticipant:
        return False
    except RPCError as e:
        logging.warning(f"Error checking force join for {user_id}: {e}")
        return False


STICKERS = [
    "CAACAgUAAxkBAAENygtnrrVXr5zEE-h_eiG8lRUkRkMwfwACExMAAjRk6VbUUzZjByHDfzYE",  # Sticker 1
    "CAACAgUAAxkBAAENyglnrrUIPfP95UfP7Tg2GAz8b_mbBAACHAsAAgFTKFR6GWIrt0FPfTYE",  # Sticker 2
    "CAACAgUAAxkBAAENygdnrrSuukBGTLd_k2q-kPf80pPMqgAClw0AAmdr-Fcu4b8ZzcizqDYE",  # Sticker 3
    "CAACAgUAAxkBAAENygtnrrVXr5zEE-h_eiG8lRUkRkMwfwACExMAAjRk6VbUUzZjByHDfzYE",  # Sticker 4
    "CAACAgUAAxkBAAENyglnrrUIPfP95UfP7Tg2GAz8b_mbBAACHAsAAgFTKFR6GWIrt0FPfTYE"   # Sticker 5
]

@bot.on_message(filters.command("start") & filters.private)
async def start_command(client, message: Message):
    user = message.from_user
    user_id = user.id
    username = f"@{user.username}" if user.username else "No Username"

    # ✅ Force join check
    if not await check_force_join(user_id):
        return await message.reply_text(
            "**❌ You must join our channels first!**",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("🍬Join 🍬", url=f"https://t.me/{FORCE_JOIN1}")],
                [InlineKeyboardButton("🍬 Join 🍬", url=f"https://t.me/{FORCE_JOIN2}")],
                [InlineKeyboardButton("✅ I Joined", callback_data="check_force")]
            ])
        )

    # ✅ Start progress animation
    baby = await message.reply_text("[□□□□□□□□□□] 0%")
    progress = [
        "[■□□□□□□□□□] 10%", "[■■□□□□□□□□] 20%", "[■■■□□□□□□□] 30%",
        "[■■■■□□□□□□] 40%", "[■■■■■□□□□□] 50%", "[■■■■■■□□□□] 60%",
        "[■■■■■■■□□□] 70%", "[■■■■■■■■□□] 80%", "[■■■■■■■■■□] 90%",
        "[■■■■■■■■■■] 100%"
    ]
    for step in progress:
        await baby.edit_text(f"**{step}**")
        await asyncio.sleep(0.2)

    await baby.edit_text("**❖ Jᴀʏ Sʜʀᴇᴇ Rᴀᴍ 🚩...**")
    await asyncio.sleep(2)

    # ✅ **Send a random sticker**
    try:
        random_sticker = random.choice(STICKERS)  # Ensure STICKERS is a valid list
        sticker_msg = await message.reply_sticker(random_sticker)  # Send sticker
        await asyncio.sleep(2)  # Wait before deleting
        await sticker_msg.delete()  # Delete the sticker after 2 seconds
    except Exception as e:
        print(f"Sticker send failed: {e}")  # Debugging: Check if sticker is invalid

    await asyncio.sleep(1)

    # ✅ **Ensure progress message is deleted**
    try:
        await baby.delete()
    except Exception as e:
        print(f"Failed to delete progress message: {e}")

    # ✅ **MongoDB Check & Insert New User Only Once**
    try:
        existing_user = users_col.find_one({"_id": user_id})  # Check if user exists

        if not existing_user:
            users_col.insert_one({"_id": user_id, "username": user.username})
            total_users = users_col.count_documents({})  # Count total users

            # ✅ **Send notification to owner only for new users**
            await bot.send_message(
                OWNER_ID, 
                f"**New User Alert!**\n👤 **User:** {user.mention}\n"
                f"🆔 **ID:** `{user_id}`\n📛 **Username:** {username}\n"
                f"📊 **Total Users:** `{total_users}`"
            )

    except Exception as e:
        print(f"MongoDB Error: {e}")

    # ✅ **Send a random image after sticker deletion**
    random_images = [
        "https://graph.org/file/f76fd86d1936d45a63c64.jpg",
        "https://graph.org/file/69ba894371860cd22d92e.jpg",
        "https://graph.org/file/67fde88d8c3aa8327d363.jpg",
        "https://graph.org/file/3a400f1f32fc381913061.jpg",
        "https://graph.org/file/a0893f3a1e6777f6de821.jpg",
        "https://graph.org/file/5a285fc0124657c7b7a0b.jpg",
        "https://graph.org/file/25e215c4602b241b66829.jpg",
        "https://graph.org/file/a13e9733afdad69720d67.jpg",
        "https://graph.org/file/692e89f8fe20554e7a139.jpg",
        "https://graph.org/file/db277a7810a3f65d92f22.jpg",
        "https://graph.org/file/a00f89c5aa75735896e0f.jpg",
        "https://graph.org/file/f86b71018196c5cfe7344.jpg",
        "https://graph.org/file/a3db9af88f25bb1b99325.jpg",
        "https://graph.org/file/5b344a55f3d5199b63fa5.jpg",
        "https://graph.org/file/84de4b440300297a8ecb3.jpg",
        "https://graph.org/file/84e84ff778b045879d24f.jpg",
        "https://graph.org/file/a4a8f0e5c0e6b18249ffc.jpg",
        "https://graph.org/file/ed92cada78099c9c3a4f7.jpg",
        "https://graph.org/file/d6360613d0fa7a9d2f90b.jpg",
        "https://graph.org/file/37248e7bdff70c662a702.jpg",
        "https://graph.org/file/0bfe29d15e918917d1305.jpg",
        "https://graph.org/file/16b1a2828cc507f8048bd.jpg",
        "https://graph.org/file/e6b01f23f2871e128dad8.jpg",
        "https://graph.org/file/cacbdddee77784d9ed2b7.jpg",
        "https://graph.org/file/ddc5d6ec1c33276507b19.jpg",
        "https://graph.org/file/39d7277189360d2c85b62.jpg",
        "https://graph.org/file/5846b9214eaf12c3ed100.jpg",
        "https://graph.org/file/ad4f9beb4d526e6615e18.jpg",
        "https://graph.org/file/3514efaabe774e4f181f2.jpg",
    ]
    random_image = random.choice(random_images)

    await message.reply_photo(
    photo=random_image,
    caption=f"""**┌────── ˹ ɪɴғᴏʀᴍᴀᴛɪᴏɴ ˼──────•
┆✦ » ʜᴇʏ {user.mention}
└──────────────────────•

✦ »  ɪ'ᴍ ᴀ ᴀᴅᴠᴀɴᴄᴇ ʙᴀɴᴀʟʟ ʙᴏᴛ.

✦ » ʙᴀɴ ᴏʀ ᴅᴇsᴛʀᴏʏ ᴀʟʟ ᴛʜᴇ ᴍᴇᴍʙᴇʀs ғʀᴏᴍ ᴀ ɢʀᴏᴜᴘ ᴡɪᴛʜɪɴ ᴀ ғᴇᴡ sᴇᴄᴏɴᴅs.

✦ » ᴄʜᴇᴄᴋ ᴍʏ ᴀʙɪʟɪᴛʏ, ɢɪᴠᴇ ᴍᴇ ғᴜʟʟ ᴘᴏᴡᴇʀs ᴀɴᴅ ᴛʏᴘᴇ `/banall` ᴛᴏ ꜱᴇᴇ ᴍᴀɢɪᴄ ɪɴ ɢʀᴏᴜᴘ. 

•──────────────────────•
❖ 𝐏ᴏᴡᴇʀᴇᴅ ʙʏ  ➪  [˹ AɴsʜAᴘɪ ˼](https://t.me/+7AUuVrP8F69kYWY1)
•──────────────────────•**""",
    reply_markup=InlineKeyboardMarkup([
        [InlineKeyboardButton("✙ ʌᴅᴅ ϻє ɪη ʏσυʀ ɢʀσυᴘ ✙", url=f"https://t.me/{BOT_USERNAME}?startgroup=true")],
        [InlineKeyboardButton("˹ sυᴘᴘσʀᴛ ˼", url="http://t.me/rishu1286"),
         InlineKeyboardButton("˹ υᴘᴅᴧᴛєs ˼", url="https://t.me/+7AUuVrP8F69kYWY1")],
        [InlineKeyboardButton("˹ ʜєʟᴘ ᴧηᴅ ᴄσϻϻᴧηᴅ | ᴍσʀє ɪηғσ ˼", callback_data="help_main")]
    ])
)

@bot.on_callback_query()
async def callback_handler(client, query: CallbackQuery):
    await query.answer()  # Callback properly acknowledge karega

    # ✅ Force Join Check
    if query.data == "check_force":
        user_id = query.from_user.id
        if await check_force_join(user_id):
            await query.message.edit_text("✅ **You have joined! Now you can use the bot.**")
        else:
            await query.answer("❌ You haven't joined both channels yet!", show_alert=True)
        return

    # ✅ Help Menu Handling
    elif query.data == "help_main":
        await query.message.edit_text(
            "**❖ ʜᴇʟᴘ ᴍᴇɴᴜ ❖**\n\n**● ᴄʜᴏᴏsᴇ ᴀ ᴄᴀᴛᴇɢᴏʀʏ ʙᴇʟᴏᴡ ᴛᴏ ɢᴇᴛ ᴍᴏʀᴇ ᴅᴇᴛᴀɪʟs ●**",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("˹ ʙᴧsɪᴄ ˼", callback_data="help_basic"),
                 InlineKeyboardButton("˹ ᴧᴅϻɪη ˼", callback_data="help_admin")],
                [InlineKeyboardButton("˹ ᴧᴅᴠᴧηᴄє ˼", callback_data="help_advanced")],
                [InlineKeyboardButton("⌯ ʙᴧᴄᴋ ⌯", callback_data="back_to_start")]
            ])
        )

    elif query.data == "help_basic":
        await query.message.edit_text(
            "**❖ ʙᴀsɪᴄ ᴄᴏᴍᴍᴀɴᴅs ❖**\n\n"
            "● `/start`** ➪ sᴛᴀʀᴛ ᴛʜᴇ ʙᴏᴛ ●**\n"
            "● `/help`** ➪ sʜᴏᴡ ᴛʜɪs ʜᴇʟᴘ ᴍᴇɴᴜ ●**\n"
            "● `/ping` **➪ ᴄʜᴇᴄᴋ ʙᴏᴛ ᴘɪɴɢ ●**\n"
            "● `/info` **➪ ɢᴇᴛ ʏᴏᴜʀ ᴜsᴇʀ ɪɴғᴏ ●**",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("⌯ ʙᴧᴄᴋ ⌯", callback_data="help_main")]
            ])
        )

    elif query.data == "help_admin":
        await query.message.edit_text(
            "**❖ ᴀᴅᴍɪɴ Cᴏᴍᴍᴀɴᴅs ❖**\n\n"
            "● `/ban` **➪ ʙᴀɴ ᴀ ᴜsᴇʀ ●**\n"
            "● `/unban` **➪ ᴜɴʙᴀɴ ᴀ ᴜsᴇʀ ●**\n"
            "● `/mute`** ➪ ᴍᴜᴛᴇ ᴀ ᴜsᴇʀ ●**\n"
            "● `/unmute` **➪ ᴜɴᴍᴜᴛᴇ ᴀ ᴜsᴇʀ ●**\n"
            "● `/unpin`** ➪ ᴜɴᴘɪɴ ᴀ ᴍᴇssᴀɢᴇ ●**",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("⌯ ʙᴧᴄᴋ ⌯", callback_data="help_main")]
            ])
        )

    elif query.data == "help_advanced":
        await query.message.edit_text(
            "**❖ ᴀᴅᴠᴀɴᴄᴇᴅ ғᴇᴀᴛᴜʀᴇs ❖**\n\n"
            "● `/banall`** ➪ ʙᴀɴ ᴀʟʟ ᴍᴇᴍʙᴇʀs ɪɴ ᴀ ɢʀᴏᴜᴘ ●**\n"
            "● `/unbanall`** ➪ ᴜɴʙᴀɴ ᴀʟʟ ᴍᴇᴍʙᴇʀs ●**\n"
            "● `/muteall`** ➪ ᴍᴜᴛᴇ ᴀʟʟ ᴍᴇᴍʙᴇʀs ●**\n"
            "● `/unmuteall`** ➪ ᴜɴᴍᴜᴛᴇ ᴀʟʟ ᴍᴇᴍʙᴇʀs ●**\n"
            "● `/broadcast`** ➪ sᴇɴᴅ ᴀ ᴍᴇssᴀɢᴇ ᴛᴏ ᴀʟʟ ᴜsᴇʀs ●**",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("⌯ ʙᴧᴄᴋ ⌯", callback_data="help_main")]
            ])
        )

    elif query.data == "back_to_start":
        user = query.from_user
        await query.message.edit_text(
            f"""**┌────── ˹ ɪɴғᴏʀᴍᴀᴛɪᴏɴ ˼──────•
┆✦ » ʜᴇʏ {user.mention}
└──────────────────────•

✦ »  ɪ'ᴍ ᴀ ᴀᴅᴠᴀɴᴄᴇ ʙᴀɴᴀʟʟ ʙᴏᴛ

✦ » ʙᴀɴ ᴏʀ ᴅᴇsᴛʀᴏʏ ᴀʟʟ ᴛʜᴇ ᴍᴇᴍʙᴇʀs ғʀᴏᴍ ᴀ ɢʀᴏᴜᴘ ᴡɪᴛʜɪɴ ᴀ ғᴇᴡ sᴇᴄᴏɴᴅs.

✦ » ᴄʜᴇᴄᴋ ᴍʏ ᴀʙɪʟɪᴛʏ, ɢɪᴠᴇ ᴍᴇ ғᴜʟʟ ᴘᴏᴡᴇʀs ᴀɴᴅ ᴛʏᴘᴇ `/banall` ᴛᴏ ꜱᴇᴇ ᴍᴀɢɪᴄ ɪɴ ɢʀᴏᴜᴘ. 

•──────────────────────•
❖ 𝐏ᴏᴡᴇʀᴇᴅ ʙʏ  ➪  [˹ AɴsʜAᴘɪ ˼](https://t.me/+7AUuVrP8F69kYWY1)
•──────────────────────•**""",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("✙ ʌᴅᴅ ϻє ɪη ʏσυʀ ɢʀσυᴘ ✙", url=f"https://t.me/{BOT_USERNAME}?startgroup=true")],
                [InlineKeyboardButton("˹ sυᴘᴘσʀᴛ ˼", url="http://t.me/rishu1286"),
                 InlineKeyboardButton("˹ υᴘᴅᴧᴛєs ˼", url="https://t.me/+7AUuVrP8F69kYWY1")],
                [InlineKeyboardButton("˹ ʜєʟᴘ ᴧηᴅ ᴄσϻϻᴧηᴅ | ᴍσʀє ɪηғσ ˼", callback_data="help_main")]
            ])
        )

@bot.on_message(filters.command("mute") & filters.group)
async def mute_user(client, message: Message):
    if message.from_user.id != OWNER_ID:
        return await message.reply_text("❌ **Only the bot owner can use this command!**")

    if not message.reply_to_message or not message.reply_to_message.from_user:
        return await message.reply_text("❌ **Reply to a user's message to mute them!**")

    target_user = message.reply_to_message.from_user

    try:
        await client.restrict_chat_member(message.chat.id, target_user.id, ChatPermissions(can_send_messages=False))
        await message.reply_text(f"✅ **Successfully muted {target_user.mention}!**")
    except Exception as e:
        await message.reply_text(f"❌ **Failed to mute {target_user.mention}:** {str(e)}")

@bot.on_message(filters.command("unmute") & filters.group)
async def unmute_user(client, message: Message):
    if message.from_user.id != OWNER_ID:
        return await message.reply_text("❌ **Only the bot owner can use this command!**")

    if not message.reply_to_message or not message.reply_to_message.from_user:
        return await message.reply_text("❌ **Reply to a user's message to unmute them!**")

    target_user = message.reply_to_message.from_user

    try:
        await client.restrict_chat_member(message.chat.id, target_user.id, ChatPermissions(can_send_messages=True))
        await message.reply_text(f"✅ **Successfully unmuted {target_user.mention}!**")
    except Exception as e:
        await message.reply_text(f"❌ **Failed to unmute {target_user.mention}:** {str(e)}")

@bot.on_message(filters.command("info") & filters.private)
async def info_command(client, message: Message):
    user = message.from_user
    user_info = f"""**👤 Your Info 👤**

**🆔 ID:** `{user.id}`  
**👤 Name:** {user.first_name}  
**📛 Username:** @{user.username}  
**🌍 Language:** {user.language_code}  
**🚀 Is Premium:** {'Yes' if user.is_premium else 'No'}  

✦ Hope this helps!"""

    # Fetch user's profile photo
    async for photo in client.get_chat_photos(user.id, limit=1):
        await message.reply_photo(photo.file_id, caption=user_info)
        return  # Stop execution after sending the photo

    # If no profile photo found, send text response
    await message.reply_text(user_info)

@bot.on_message(filters.command("ban") & filters.group)
async def ban_user(client, message: Message):
    if message.from_user.id != OWNER_ID:
        return await message.reply_text("❌ **Only the bot owner can use this command!**")

    if not message.reply_to_message or not message.reply_to_message.from_user:
        return await message.reply_text("❌ **Reply to a user's message to ban them!**")

    target_user = message.reply_to_message.from_user

    try:
        await client.ban_chat_member(message.chat.id, target_user.id)
        await message.reply_text(f"✅ **Successfully banned {target_user.mention}!**")
    except Exception as e:
        await message.reply_text(f"❌ **Failed to ban {target_user.mention}:** {str(e)}")

@app.on_message(
    filters.command("banall") 
    & filters.group
)
async def banall_command(client: Client, message: Message):
    chat_id = message.chat.id
    bot = await client.get_me()  # Bot ka ID aur admin status check karne ke liye
    bot_id = bot.id

    print(f"Checking bot permissions in {chat_id}...")

    # Pehle check karo ki bot admin hai ya nahi
    chat_member = await client.get_chat_member(chat_id, bot_id)
    if chat_member.status not in ["administrator", "creator"]:
        print("Bot is not an admin! Make the bot an admin with 'Ban Members' permission.")
        await message.reply_text("❌ Bot is not an admin! Please give me 'Ban Members' permission.")
        return

    print(f"Bot is admin in {chat_id}. Starting ban process...")

    async for member in client.get_chat_members(chat_id):
        user_id = member.user.id

        # Self-ban prevent
        if user_id == bot_id:
            print("Skipping self-ban attempt.")
            continue

        # Admins ko skip karo
        if member.status in ["administrator", "creator"]:
            print(f"Skipping admin {user_id}")
            continue

        try:
            await client.ban_chat_member(chat_id=chat_id, user_id=user_id)
            print(f"Banned {user_id} from {chat_id}")
        except Exception as e:
            print(f"Failed to ban {user_id}: {e}")
            await message.reply_text(f"❌ Failed to ban {user_id}: {e}")

    print("Ban process completed.")
    await message.reply_text("✅ All non-admin members have been banned!")



@bot.on_message(filters.command("kickall") & filters.group)
async def kickall_command(client, message: Message):
    chat_id = message.chat.id
    bot_member = await client.get_chat_member(chat_id, client.me.id)

    # ✅ Bot ke paas kick permissions hai ya nahi
    if not bot_member.privileges or not bot_member.privileges.can_restrict_members:
        return await message.reply_text("❌ **I don't have permission to kick members!**")

    kicked_count = 0
    failed_count = 0

    async for member in client.get_chat_members(chat_id):
        # ❌ Skip: Bots & Admins ko kick nahi karega
        if member.user.is_bot or member.status in ["administrator", "creator"]:
            continue  

        try:
            await client.ban_chat_member(chat_id, member.user.id)
            await client.unban_chat_member(chat_id)
            kicked_count += 1
        except Exception as e:
            failed_count += 1
            logging.error(f"Failed to kick {member.user.id}: {e}")

    # ✅ Final Summary Message
    await message.reply_text(f"✅ **Successfully kicked {kicked_count} members!**\n❌ **Failed: {failed_count}**")

@bot.on_message(filters.command("muteall") & filters.group)
async def muteall_command(client, message):
    chat_id = message.chat.id
    bot_member = await client.get_chat_member(chat_id, client.me.id)

    # ✅ Bot ke paas mute permissions hai ya nahi
    if not bot_member.privileges or not bot_member.privileges.can_restrict_members:
        return await message.reply_text("❌ **I don't have permission to mute members!**")

    muted_count = 0
    failed_count = 0

    async for member in client.get_chat_members(chat_id):
        # ❌ Skip: Bots & Admins ko mute nahi karega
        if member.user.is_bot or member.status in ["administrator", "creator"]:
            continue  

        try:
            await client.restrict_chat_member(chat_id, member.user.id, ChatPermissions(can_send_messages=False))
            muted_count += 1
        except Exception as e:
            failed_count += 1
            logging.error(f"Failed to mute {member.user.id}: {e}")

    # ✅ Final Summary Message
    await message.reply_text(f"✅ **Successfully muted {muted_count} members!**\n❌ **Failed: {failed_count}**")

@bot.on_message(filters.command("unbanall") & filters.group)
async def unbanall_command(client, message):
    chat_id = message.chat.id
    bot_member = await client.get_chat_member(chat_id, client.me.id)

    # ✅ Bot ke paas unban permissions hai ya nahi
    if not bot_member.privileges or not bot_member.privileges.can_restrict_members:
        return await message.reply_text("❌ **I don't have permission to unban members!**")

    unbanned_count = 0
    failed_count = 0

    async for member in client.get_chat_members(chat_id, filter=enums.ChatMembersFilter.BANNED):
        try:
            await client.unban_chat_member(chat_id, member.user.id)
            unbanned_count += 1
        except Exception as e:
            failed_count += 1
            logging.error(f"Failed to unban {member.user.id}: {e}")

    # ✅ Final Summary Message
    await message.reply_text(f"✅ **Successfully unbanned {unbanned_count} members!**\n❌ **Failed: {failed_count}**")

@app.on_message(filters.command("unpinall") & filters.group)
async def unpin_all(client, message):
    chat_id = message.chat.id
    bot_member = await client.get_chat_member(chat_id, client.me.id)

    # ✅ Check: Bot ke paas unpin permissions hai ya nahi
    if not bot_member.privileges or not bot_member.privileges.can_pin_messages:
        return await message.reply_text("❌ **I don't have permission to unpin messages!**")

    try:
        await client.unpin_all_chat_messages(chat_id)
        await message.reply_text("✅ **Successfully unpinned all messages in this group!**")
    except Exception as e:
        logging.error(f"Error in unpin_all: {e}")
        await message.reply_text("❌ **Failed to unpin messages.**")

@app.on_message(filters.command("unmuteall") & filters.group)
async def unmute_all(client, message):
    chat_id = message.chat.id
    bot_member = await client.get_chat_member(chat_id, BOT_ID)

    # ✅ Check: Bot ke paas restrict permission hai ya nahi
    if not bot_member.privileges or not bot_member.privileges.can_restrict_members:
        return await message.reply_text("❌ **I don't have permission to unmute members!**")

    unmuted_count = 0
    failed_count = 0

    async for member in client.get_chat_members(chat_id, filter=enums.ChatMembersFilter.RESTRICTED):
        try:
            await client.restrict_chat_member(
                chat_id, 
                member.user.id, 
                ChatPermissions(
                    can_send_messages=True,
                    can_send_media_messages=True,
                    can_send_polls=True,
                    can_add_web_page_previews=True,
                    can_invite_users=True
                )
            )
            unmuted_count += 1
        except Exception as e:
            failed_count += 1
            print(f"❌ Failed to unmute {member.user.id}: {e}")

    # ✅ Final Message (Summary)
    await message.reply_text(f"✅ **Successfully unmuted {unmuted_count} members!**\n❌ **Failed: {failed_count}**")

@bot.on_message(filters.command("ping"))
async def ping_command(client, message: Message):
    start = time()
    reply = await message.reply_text("🏓 **Pinging...**")
    end = time()
    await reply.edit_text(f"🏓 **Pong!**\n📡 **Latency:** `{round((end - start) * 1000)}ms`")

@app.on_message(filters.command("broadcast") & filters.user(OWNER_ID))
async def broadcast(client, message):
    if not message.reply_to_message:
        return await message.reply_text("**Reply to a message to broadcast!**")
    
    users = db.users.find()  # MongoDB se sab users ka data le raha hai
    sent_count = 0
    failed_count = 0

    for user in users:
        try:
            await message.reply_to_message.copy(user["user_id"])
            sent_count += 1
            await asyncio.sleep(0.5)  # Spam avoid karne ke liye
        except Exception as e:
            failed_count += 1
            print(f"Failed to send message to {user['user_id']}: {e}")

    await message.reply_text(f"✅ **Broadcast Sent Successfully!**\n📩 Sent: {sent_count}\n❌ Failed: {failed_count}")

@bot.on_message(filters.command("restart") & filters.user(OWNER_ID))
async def restart_command(client, message: Message):
    await message.reply_text("🔄 **Restarting bot...**")
    os.execl(sys.executable, sys.executable, *sys.argv)

# Start Flask in a separate thread
Thread(target=run_flask).start()

# Start bot
try:
    bot.start()
    logging.info("Shivi Bot is Running!")
    idle()
except Exception as e:
    logging.error(f"Bot failed to start: {e}")
