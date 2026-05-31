from telegram import Update
from telegram import InlineKeyboardButton as PTBButton
from telegram import InlineKeyboardMarkup as PTBMarkup
from telegram.ext import ContextTypes
from pyrogram import Client, filters, enums
from pyrogram.enums import ButtonStyle
from pyrogram.types import CallbackQuery
from pyrogram.types import InlineKeyboardButton as PyroButton
from pyrogram.types import InlineKeyboardMarkup as PyroMarkup
from AxiomX.helpers.decorator import Command, only_groups, admin_check
from AxiomX import BOT_USERNAME, pbot, font
from AxiomX.db import (
    locks_db, mod, reaction, disable, greetings, cleancommand_db, cleanservice_db,
    chatbot, antiraid, antinsfw_db, approval_db, antiflood, join_request,
    blocklistwords, translate, riddle, notes, rules, couple, autodelete,
    joinmute_db, antiforward_db, antitag_db, mediadelete_db
)
import math
from typing import Optional

CATEGORIES = [
    "ɢʀᴇᴇᴛɪɴɢs", "ʟᴏᴄᴋs", "ʀᴇᴀᴄᴛɪᴏɴs", "ᴀɴᴛɪ ɴsғᴡ", "ᴀɴᴛɪғʟᴏᴏᴅ", "ᴀɴᴛɪʀᴀɪᴅ",
    "ᴀᴅᴍɪɴ", "ᴄʜᴀᴛʙᴏᴛ", "ᴄᴍᴅ ᴅɪsᴀʙʟᴇ", "ᴊᴏɪɴ ʀᴇǫᴜᴇsᴛ", "ʙʟᴀᴄᴋʟɪsᴛ", "ᴛʀᴀɴsʟᴀᴛᴏʀ",
    "ʀɪᴅᴅʟᴇ", "ɴᴏᴛᴇs", "ᴄʟᴇᴀɴ ᴄᴍᴅ", "ᴄʟᴇᴀɴ sᴇʀᴠɪᴄᴇ", "ᴀᴘᴘʀᴏᴠᴀʟs", "ʀᴜʟᴇs",
    "ᴄᴏᴜᴘʟᴇ", "ᴊᴏɪɴ ᴍᴜᴛᴇ", "ᴀɴᴛɪ ғᴏʀᴡᴀʀᴅ", "ᴀɴᴛɪ ᴛᴀɢ", "ᴍᴇᴅɪᴀ ᴅᴇʟᴇᴛᴇ"
]
ITEMS_PER_PAGE = 12

async def fetch_settings(chat_id: int) -> dict:
    try:
        translator_data = await translate.get_chat(chat_id)
        couple_data = await couple.get_couple(chat_id)
        
        return {
            'locks': await locks_db.get_locks(chat_id),
            'welcome_status': await greetings.get_welcome_status(chat_id),
            'welcome_exists': await greetings.check_welcome(chat_id),
            'goodbye_status': await greetings.get_goodbye_status(chat_id),
            'goodbye_exists': await greetings.check_goodbye(chat_id),
            'reactions': await reaction.get_reaction_status(chat_id),
            'disabled': await disable.get_disabled(chat_id),
            'clean_command': await cleancommand_db.get_clean_type(chat_id),
            'clean_service': await cleanservice_db.get_clean_settings(chat_id),
            'chatbot': chat_id in chatbot.CHAT_IDS,
            'antiraid': await antiraid.get_antiraid_config(chat_id),
            'antinsfw': await antinsfw_db.get_antinsfw(chat_id),
            'antinsfw_admin': await antinsfw_db.get_antinsfw_admin(chat_id),
            'approved_users': await approval_db.get_all_approved_users(chat_id),
            'flood': await antiflood.get_flood_config(chat_id),
            'mods': await mod.get_all_mods(chat_id),
            'join_request': await join_request.is_request_enabled(chat_id),
            'blacklist_words': await blocklistwords.get_words(chat_id),
            'blacklist_mode': await blocklistwords.get_mode(chat_id),
            'translator': translator_data.get('lang') if translator_data else None,
            'riddle': chat_id in riddle.CHAT_IDS,
            'riddle_count': await riddle.get_chat_riddle_count(chat_id),
            'notes': await notes.get_notes_by_chat(chat_id),
            'rules': await rules.get_rules(chat_id),
            'rules_private': await rules.get_private_rules(chat_id),
            'couple': couple_data,
            'autodelete': await autodelete.get_autodelete(chat_id),
            'joinmute': await joinmute_db.get_joinmute_duration(chat_id),
            'antiforward': await antiforward_db.is_antiforward_enabled(chat_id),
            'antitag': await antitag_db.get_antitag_limit(chat_id),
            'mediadelete': await mediadelete_db.get_media_delete_settings(chat_id)
        }
    except Exception as e:
        print(f"[FETCH_SETTINGS ERROR] {e}")
        return {}

def fmt_header(title: str) -> str:
    return f"<b>⚙️ sᴇᴛᴛɪɴɢs ғᴏʀ {title}</b>\n\n"

def fmt_footer(chat_id: int) -> str:
    return f"\n<code>ᴄʜᴀᴛ ɪᴅ: {chat_id}</code>"

def fmt_greetings(chat_id: int, data: dict, title: str) -> str:
    text = fmt_header(title) + "👋 <b>ɢʀᴇᴇᴛɪɴɢs sᴇᴛᴛɪɴɢs</b>\n\n🎉 <b>ᴡᴇʟᴄᴏᴍᴇ:</b>\n"
    if data.get('welcome_exists'):
        status = "✅ ᴇɴᴀʙʟᴇᴅ" if data.get('welcome_status') else "⚠️ ᴅɪsᴀʙʟᴇᴅ"
        text += f"   └ sᴛᴀᴛᴜs: {status}\n   └ ᴍᴇssᴀɢᴇ: ✅ sᴇᴛ\n"
    else:
        text += "   └ sᴛᴀᴛᴜs: ❌ ɴᴏᴛ ᴄᴏɴғɪɢᴜʀᴇᴅ\n"
    
    text += "\n👋 <b>ɢᴏᴏᴅʙʏᴇ:</b>\n"
    if data.get('goodbye_exists'):
        status = "✅ ᴇɴᴀʙʟᴇᴅ" if data.get('goodbye_status') else "⚠️ ᴅɪsᴀʙʟᴇᴅ"
        text += f"   └ sᴛᴀᴛᴜs: {status}\n   └ ᴍᴇssᴀɢᴇ: ✅ sᴇᴛ\n"
    else:
        text += "   └ sᴛᴀᴛᴜs: ❌ ɴᴏᴛ ᴄᴏɴғɪɢᴜʀᴇᴅ\n"
    return text + fmt_footer(chat_id)

def fmt_locks(chat_id: int, data: dict, title: str) -> str:
    text = fmt_header(title) + "🔒 <b>ʟᴏᴄᴋs sᴇᴛᴛɪɴɢs</b>\n\n"
    if locks := data.get('locks', []):
        text += f"🔐 <b>ʟᴏᴄᴋᴇᴅ ɪᴛᴇᴍs ({len(locks)}):</b>\n"
        text += "\n".join(f"   └ <code>{lock}</code>" for lock in locks)
    else:
        text += "   ✅ ɴᴏ ʟᴏᴄᴋs ᴇɴᴀʙʟᴇᴅ"
    return text + fmt_footer(chat_id)

def fmt_antiflood(chat_id: int, data: dict, title: str) -> str:
    text = fmt_header(title) + "💧 <b>ᴀɴᴛɪғʟᴏᴏᴅ sᴇᴛᴛɪɴɢs</b>\n\n"
    flood = data.get('flood', {})
    if flood.get('limit', 0) > 0:
        text += f"⚠️ <b>sᴛᴀᴛᴜs:</b> ᴇɴᴀʙʟᴇᴅ\n\n📊 <b>ʟɪᴍɪᴛ:</b> {flood['limit']} ᴍᴇssᴀɢᴇs\n"
        text += f"⚡ <b>ᴀᴄᴛɪᴏɴ:</b> {flood.get('action', {}).get('type', 'N/A')}"
        if duration := flood.get('action', {}).get('duration'):
            text += f" ({duration})"
        text += f"\n🗑️ <b>ᴄʟᴇᴀʀ ᴍᴇssᴀɢᴇs:</b> {'✅ ʏᴇs' if flood.get('clear') else '❌ ɴᴏ'}\n"
        if flood.get('timer', {}).get('count', 0) > 0:
            text += f"⏱️ <b>ᴛɪᴍᴇʀ:</b> {flood['timer']['count']} ᴍᴇssᴀɢᴇs ɪɴ {flood['timer']['seconds']}s\n"
    else:
        text += "   ✅ ᴀɴᴛɪғʟᴏᴏᴅ ɪs ᴅɪsᴀʙʟᴇᴅ"
    return text + fmt_footer(chat_id)

def fmt_antiraid(chat_id: int, data: dict, title: str) -> str:
    text = fmt_header(title) + "🛡️ <b>ᴀɴᴛɪʀᴀɪᴅ sᴇᴛᴛɪɴɢs</b>\n\n"
    raid = data.get('antiraid', {})
    if raid.get('enabled_until'):
        text += f"⚠️ <b>sᴛᴀᴛᴜs:</b> ᴇɴᴀʙʟᴇᴅ\n⏰ <b>ᴜɴᴛɪʟ:</b> {raid['enabled_until']}\n"
    else:
        text += "   ✅ ᴀɴᴛɪʀᴀɪᴅ ɪs ᴅɪsᴀʙʟᴇᴅ\n"
    text += f"⏱️ <b>ʀᴀɪᴅ ᴛɪᴍᴇ:</b> {raid.get('raid_time', 21600)}s\n"
    text += f"⛔ <b>ʙᴀɴ ᴛɪᴍᴇ:</b> {raid.get('ban_time', 3600)}s\n"
    text += f"🔢 <b>ᴀᴜᴛᴏ ᴛʀɪɢɢᴇʀ:</b> {raid.get('auto_trigger', 0)}"
    return text + fmt_footer(chat_id)

def fmt_antinsfw(chat_id: int, data: dict, title: str) -> str:
    text = fmt_header(title) + "🔞 <b>ᴀɴᴛɪ-ɴsғᴡ sᴇᴛᴛɪɴɢs</b>\n\n"
    text += f"🛡️ <b>ᴀɴᴛɪ-ᴘᴏʀɴ:</b> {'✅ ᴇɴᴀʙʟᴇᴅ' if data.get('antinsfw') else '❌ ᴅɪsᴀʙʟᴇᴅ'}\n"
    text += f"👮 <b>ᴄʜᴇᴄᴋ ᴀᴅᴍɪɴs:</b> {'✅ ʏᴇs' if data.get('antinsfw_admin') else '❌ ɴᴏ'}"
    return text + fmt_footer(chat_id)

def fmt_reactions(chat_id: int, data: dict, title: str) -> str:
    text = fmt_header(title) + "😊 <b>ʀᴇᴀᴄᴛɪᴏɴs sᴇᴛᴛɪɴɢs</b>\n\n"
    text += f"🎭 <b>sᴛᴀᴛᴜs:</b> {'✅ ᴇɴᴀʙʟᴇᴅ' if data.get('reactions') else '❌ ᴅɪsᴀʙʟᴇᴅ'}"
    return text + fmt_footer(chat_id)

def fmt_chatbot(chat_id: int, data: dict, title: str) -> str:
    text = fmt_header(title) + "🤖 <b>ᴄʜᴀᴛʙᴏᴛ sᴇᴛᴛɪɴɢs</b>\n\n"
    text += f"💬 <b>sᴛᴀᴛᴜs:</b> {'✅ ᴇɴᴀʙʟᴇᴅ' if data.get('chatbot') else '❌ ᴅɪsᴀʙʟᴇᴅ'}"
    return text + fmt_footer(chat_id)

def fmt_cmd_disable(chat_id: int, data: dict, title: str) -> str:
    text = fmt_header(title) + "🚫 <b>ᴅɪsᴀʙʟᴇᴅ ᴄᴏᴍᴍᴀɴᴅs</b>\n\n"
    if disabled := data.get('disabled', []):
        text += f"❌ <b>ᴅɪsᴀʙʟᴇᴅ ({len(disabled)}):</b>\n"
        text += "\n".join(f"   └ <code>{cmd}</code>" for cmd in disabled[:10])
        if len(disabled) > 10:
            text += f"\n   └ ... ᴀɴᴅ {len(disabled) - 10} ᴍᴏʀᴇ"
    else:
        text += "   ✅ ɴᴏ ᴄᴏᴍᴍᴀɴᴅs ᴅɪsᴀʙʟᴇᴅ"
    return text + fmt_footer(chat_id)

async def fmt_admin(chat_id: int, data: dict, title: str) -> str:
    text = fmt_header(title) + "👑 <b>ᴀᴅᴍɪɴ & ᴍᴏᴅs</b>\n\n"
    if mods := data.get('mods', []):
        text += f"🛡️ <b>ᴍᴏᴅs ({len(mods)}):</b>\n"
        for m in mods[:5]:
            try:
                user = await pbot.get_users(m['user_id'])
                name = user.mention if user else f"<code>{m['user_id']}</code>"
            except:
                name = f"<code>{m['user_id']}</code>"
            text += f"   └ {name} - {m.get('role', 'mod')}\n"
        if len(mods) > 5:
            text += f"   └ ... ᴀɴᴅ {len(mods) - 5} ᴍᴏʀᴇ"
    else:
        text += "   ɴᴏ ᴍᴏᴅs ᴀssɪɢɴᴇᴅ"
    return text + fmt_footer(chat_id)

def fmt_approvals(chat_id: int, data: dict, title: str) -> str:
    text = fmt_header(title) + "✅ <b>ᴀᴘᴘʀᴏᴠᴇᴅ ᴜsᴇʀs</b>\n\n"
    approved = data.get('approved_users', [])
    text += f"👥 <b>ᴛᴏᴛᴀʟ ᴀᴘᴘʀᴏᴠᴇᴅ:</b> {len(approved)}"
    if approved:
        text += "\n\n<b>ᴜsᴇʀ ɪᴅs:</b>\n"
        text += "\n".join(f"   └ <code>{uid}</code>" for uid in approved[:10])
        if len(approved) > 10:
            text += f"\n   └ ... ᴀɴᴅ {len(approved) - 10} ᴍᴏʀᴇ"
    return text + fmt_footer(chat_id)

def fmt_join_request(chat_id: int, data: dict, title: str) -> str:
    text = fmt_header(title) + "👥 <b>ᴊᴏɪɴ ʀᴇǫᴜᴇsᴛ</b>\n\n"
    text += f"📢 <b>sᴛᴀᴛᴜs:</b> {'✅ ᴇɴᴀʙʟᴇᴅ' if data.get('join_request') else '❌ ᴅɪsᴀʙʟᴇᴅ'}"
    return text + fmt_footer(chat_id)

def fmt_blacklist(chat_id: int, data: dict, title: str) -> str:
    text = fmt_header(title) + "⛔ <b>ʙʟᴀᴄᴋʟɪsᴛ ᴡᴏʀᴅs</b>\n\n"
    if words := data.get('blacklist_words', []):
        text += f"🚫 <b>ʙʟᴀᴄᴋʟɪsᴛᴇᴅ ({len(words)}):</b>\n"
        text += "   " + ", ".join(f"<code>{w}</code>" for w in words[:8])
        if len(words) > 8:
            text += f" ... +{len(words) - 8} ᴍᴏʀᴇ"
        text += f"\n\n🔧 <b>ᴍᴏᴅᴇ:</b> {'✅ sᴛʀɪᴄᴛ' if data.get('blacklist_mode') else '❌ sᴏғᴛ'}"
    else:
        text += "   ✅ ɴᴏ ʙʟᴀᴄᴋʟɪsᴛᴇᴅ ᴡᴏʀᴅs"
    return text + fmt_footer(chat_id)

def fmt_translator(chat_id: int, data: dict, title: str) -> str:
    text = fmt_header(title) + "🌐 <b>ᴛʀᴀɴsʟᴀᴛᴏʀ sᴇᴛᴛɪɴɢs</b>\n\n"
    if data.get('translator'):
        text += f"🔤 <b>ʟᴀɴɢᴜᴀɢᴇ:</b> {data['translator']}\n📊 <b>sᴛᴀᴛᴜs:</b> ✅ ᴇɴᴀʙʟᴇᴅ"
    else:
        text += "   ❌ ᴛʀᴀɴsʟᴀᴛᴏʀ ɴᴏᴛ ᴄᴏɴғɪɢᴜʀᴇᴅ"
    return text + fmt_footer(chat_id)

def fmt_riddle(chat_id: int, data: dict, title: str) -> str:
    text = fmt_header(title) + "🎲 <b>ʀɪᴅᴅʟᴇ sᴇᴛᴛɪɴɢs</b>\n\n"
    if data.get('riddle'):
        text += "📊 <b>sᴛᴀᴛᴜs:</b> ✅ ᴇɴᴀʙʟᴇᴅ"
        if data.get('riddle_count'):
            text += f"\n🔢 <b>ᴄᴏᴜɴᴛ:</b> {data['riddle_count']}"
    else:
        text += "   ❌ ʀɪᴅᴅʟᴇ ɪs ᴅɪsᴀʙʟᴇᴅ"
    return text + fmt_footer(chat_id)

def fmt_notes(chat_id: int, data: dict, title: str) -> str:
    text = fmt_header(title) + "📝 <b>ɴᴏᴛᴇs</b>\n\n"
    if notes_list := data.get('notes', []):
        text += f"📋 <b>ᴛᴏᴛᴀʟ ɴᴏᴛᴇs: {len(notes_list)}</b>\n\n"
        for note in notes_list[:5]:
            text += f"   └ <code>#{note.get('tag', 'N/A')}</code> - {note.get('type', 'text')}\n"
        if len(notes_list) > 5:
            text += f"   └ ... ᴀɴᴅ {len(notes_list) - 5} ᴍᴏʀᴇ"
    else:
        text += "   ✅ ɴᴏ ɴᴏᴛᴇs sᴀᴠᴇᴅ"
    return text + fmt_footer(chat_id)

def fmt_clean_cmd(chat_id: int, data: dict, title: str) -> str:
    text = fmt_header(title) + "🧹 <b>ᴄʟᴇᴀɴ ᴄᴏᴍᴍᴀɴᴅ</b>\n\n"
    if data.get('clean_command'):
        text += f"🔧 <b>ᴛʏᴘᴇ:</b> {data['clean_command']}\n📊 <b>sᴛᴀᴛᴜs:</b> ✅ ᴇɴᴀʙʟᴇᴅ"
    else:
        text += "   ❌ ᴄʟᴇᴀɴ ᴄᴏᴍᴍᴀɴᴅ ᴅɪsᴀʙʟᴇᴅ"
    return text + fmt_footer(chat_id)

def fmt_clean_service(chat_id: int, data: dict, title: str) -> str:
    text = fmt_header(title) + "🧼 <b>ᴄʟᴇᴀɴ sᴇʀᴠɪᴄᴇ</b>\n\n"
    if services := data.get('clean_service', []):
        text += f"🗑️ <b>ᴄʟᴇᴀɴɪɴɢ ({len(services)}):</b>\n"
        text += "\n".join(f"   └ {svc}" for svc in services)
    else:
        text += "   ✅ ɴᴏ sᴇʀᴠɪᴄᴇ ᴄʟᴇᴀɴɪɴɢ ᴇɴᴀʙʟᴇᴅ"
    return text + fmt_footer(chat_id)

def fmt_rules(chat_id: int, data: dict, title: str) -> str:
    text = fmt_header(title) + "📜 <b>ʀᴜʟᴇs</b>\n\n"
    if data.get('rules'):
        text += f"📋 <b>sᴛᴀᴛᴜs:</b> ✅ sᴇᴛ\n"
        text += f"🔒 <b>ᴘʀɪᴠᴀᴛᴇ:</b> {'✅ ʏᴇs' if data.get('rules_private') else '❌ ɴᴏ'}"
    else:
        text += "   ❌ ɴᴏ ʀᴜʟᴇs sᴇᴛ"
    return text + fmt_footer(chat_id)

def fmt_couple(chat_id: int, data: dict, title: str) -> str:
    text = fmt_header(title) + "💑 <b>ᴄᴏᴜᴘʟᴇ sᴇᴛᴛɪɴɢs</b>\n\n"
    if couple_data := data.get('couple'):
        if couple_data.get('couples'):
            text += f"👫 <b>ᴛᴏᴛᴀʟ ᴄᴏᴜᴘʟᴇs:</b> {len(couple_data['couples'])}\n"
            text += f"📅 <b>ʟᴀsᴛ ᴜᴘᴅᴀᴛᴇ:</b> ᴅᴀʏ {couple_data.get('day', 0)}"
        else:
            text += "   ❌ ɴᴏ ᴄᴏᴜᴘʟᴇs sᴇᴛ"
    else:
        text += "   ❌ ɴᴏ ᴄᴏᴜᴘʟᴇs sᴇᴛ"
    return text + fmt_footer(chat_id)

def fmt_autodelete(chat_id: int, data: dict, title: str) -> str:
    text = fmt_header(title) + "🗑️ <b>ᴀᴜᴛᴏ ᴅᴇʟᴇᴛᴇ sᴇᴛᴛɪɴɢs</b>\n\n"

    # Check if it's the new mediadelete feature first
    if mdata := data.get('mediadelete'):
        if mdata.get('enabled'):
            text += f"⏱️ <b>ᴅᴇʟᴀʏ:</b> {mdata['delay']} sᴇᴄᴏɴᴅs\n📊 <b>sᴛᴀᴛᴜs:</b> ✅ ᴇɴᴀʙʟᴇᴅ (ᴍᴇᴅɪᴀ)"
            return text + fmt_footer(chat_id)

    if delay := data.get('autodelete'):
        text += f"⏱️ <b>ᴅᴇʟᴀʏ:</b> {delay} sᴇᴄᴏɴᴅs\n📊 <b>sᴛᴀᴛᴜs:</b> ✅ ᴇɴᴀʙʟᴇᴅ"
    else:
        text += "   ❌ ᴀᴜᴛᴏ ᴅᴇʟᴇᴛᴇ ᴅɪsᴀʙʟᴇᴅ"
    return text + fmt_footer(chat_id)

def fmt_antitag(chat_id: int, data: dict, title: str) -> str:
    text = fmt_header(title) + "🏷️ <b>ᴀɴᴛɪ ᴛᴀɢ sᴇᴛᴛɪɴɢs</b>\n\n"
    if limit := data.get('antitag'):
        text += f"📊 <b>ʟɪᴍɪᴛ:</b> {limit} ᴍᴇɴᴛɪᴏɴs\n📊 <b>sᴛᴀᴛᴜs:</b> ✅ ᴇɴᴀʙʟᴇᴅ"
    else:
        text += "   ❌ ᴀɴᴛɪ ᴛᴀɢ ᴅɪsᴀʙʟᴇᴅ"
    return text + fmt_footer(chat_id)

def fmt_joinmute(chat_id: int, data: dict, title: str) -> str:
    text = fmt_header(title) + "🤐 <b>ᴊᴏɪɴ ᴍᴜᴛᴇ sᴇᴛᴛɪɴɢs</b>\n\n"
    if duration := data.get('joinmute'):
        from .joinmute import format_time
        text += f"⏱️ <b>ᴅᴜʀᴀᴛɪᴏɴ:</b> {format_time(duration)}\n📊 <b>sᴛᴀᴛᴜs:</b> ✅ ᴇɴᴀʙʟᴇᴅ"
    else:
        text += "   ❌ ᴊᴏɪɴ ᴍᴜᴛᴇ ᴅɪsᴀʙʟᴇᴅ"
    return text + fmt_footer(chat_id)

def fmt_antiforward(chat_id: int, data: dict, title: str) -> str:
    text = fmt_header(title) + "⏩ <b>ᴀɴᴛɪ ғᴏʀᴡᴀʀᴅ sᴇᴛᴛɪɴɢs</b>\n\n"
    text += f"📊 <b>sᴛᴀᴛᴜs:</b> {'✅ ᴇɴᴀʙʟᴇᴅ' if data.get('antiforward') else '❌ ᴅɪsᴀʙʟᴇᴅ'}"
    return text + fmt_footer(chat_id)

FORMATTERS = {
    'ɢʀᴇᴇᴛɪɴɢs': fmt_greetings,
    'ʟᴏᴄᴋs': fmt_locks,
    'ʀᴇᴀᴄᴛɪᴏɴs': fmt_reactions,
    'ᴀɴᴛɪ_ɴsғᴡ': fmt_antinsfw,
    'ᴀɴᴛɪғʟᴏᴏᴅ': fmt_antiflood,
    'ᴀɴᴛɪʀᴀɪᴅ': fmt_antiraid,
    'ᴀᴅᴍɪɴ': fmt_admin,
    'ᴄʜᴀᴛʙᴏᴛ': fmt_chatbot,
    'ᴄᴍᴅ_ᴅɪsᴀʙʟᴇ': fmt_cmd_disable,
    'ᴊᴏɪɴ_ʀᴇǫᴜᴇsᴛ': fmt_join_request,
    'ʙʟᴀᴄᴋʟɪsᴛ': fmt_blacklist,
    'ᴛʀᴀɴsʟᴀᴛᴏʀ': fmt_translator,
    'ʀɪᴅᴅʟᴇ': fmt_riddle,
    'ɴᴏᴛᴇs': fmt_notes,
    'ᴄʟᴇᴀɴ_ᴄᴍᴅ': fmt_clean_cmd,
    'ᴄʟᴇᴀɴ_sᴇʀᴠɪᴄᴇ': fmt_clean_service,
    'ᴀᴘᴘʀᴏᴠᴀʟs': fmt_approvals,
    'ʀᴜʟᴇs': fmt_rules,
    'ᴄᴏᴜᴘʟᴇ': fmt_couple,
    'ᴀɴᴛɪ_ᴛᴀɢ': fmt_antitag,
    'ᴊᴏɪɴ_ᴍᴜᴛᴇ': fmt_joinmute,
    'ᴀɴᴛɪ_ғᴏʀᴡᴀʀᴅ': fmt_antiforward,
    'ᴍᴇᴅɪᴀ_ᴅᴇʟᴇᴛᴇ': fmt_autodelete
}

async def get_chat_title(chat_id: int) -> str:
    try:
        chat = await pbot.get_chat(chat_id)
        return chat.title
    except Exception as e:
        print(f"[GET_CHAT_TITLE ERROR] {e}")
        return "ᴜɴᴋɴᴏᴡɴ ᴄʜᴀᴛ"

def normalize_category(category: str) -> str:
    return category.lower().replace(' ', '_')

def build_category_keyboard(page: int, chat_id: int) -> PyroMarkup:
    total_pages = math.ceil(len(CATEGORIES) / ITEMS_PER_PAGE)
    start = page * ITEMS_PER_PAGE
    end = min((page + 1) * ITEMS_PER_PAGE, len(CATEGORIES))
    
    keyboard = []
    row = []
    
    for cat in CATEGORIES[start:end]:
        row.append(PyroButton(font(cat), callback_data=f"sett:{normalize_category(cat)}:{chat_id}", style=ButtonStyle.SUCCESS))
        if len(row) == 2:
            keyboard.append(row)
            row = []
    
    if row:
        keyboard.append(row)
    
    nav_buttons = []
    if page > 0:
        nav_buttons.append(PyroButton(font("‹ Back"), callback_data=f"sett:page:{page-1}:{chat_id}", style=ButtonStyle.PRIMARY))
    if page < total_pages - 1:
        nav_buttons.append(PyroButton(font("Next ›"), callback_data=f"sett:page:{page+1}:{chat_id}", style=ButtonStyle.PRIMARY))
    
    if nav_buttons:
        keyboard.append(nav_buttons)
    
    keyboard.append([PyroButton(font("✖️ Close"), callback_data=f"sett:close:{chat_id}", style=ButtonStyle.DANGER)])
    
    return PyroMarkup(keyboard)

def build_detail_keyboard(chat_id: int) -> PyroMarkup:
    return PyroMarkup([
        [PyroButton(font("« Menu"), callback_data=f"sett:back:{chat_id}", style=ButtonStyle.PRIMARY)],
        [PyroButton(font("✖️ Close"), callback_data=f"sett:close:{chat_id}", style=ButtonStyle.DANGER)]
    ])

async def handle_settings_deeplink(message, token: str):
    try:
        parts = token.split('_')
        if len(parts) < 3:
            await message.reply_text(font("❌ ɪɴᴠᴀʟɪᴅ sᴇᴛᴛɪɴɢs ʟɪɴᴋ!"))
            return False
        
        chat_id = int(parts[2])
        chat_title = await get_chat_title(chat_id)
        
        if parts[1] == 'main':
            text = f"<b>⚙️ ᴀᴠᴀɪʟᴀʙʟᴇ sᴇᴛᴛɪɴɢs ғᴏʀ {chat_title}</b>\n\n💫 sᴡɪᴘᴇ ᴀɴᴅ ᴄʜᴇᴄᴋ sᴇᴛᴛɪɴɢs.."
            await message.reply_text(
                text,
                reply_markup=build_category_keyboard(0, chat_id),
                parse_mode=enums.ParseMode.HTML
            )
            return True
        
        settings_data = await fetch_settings(chat_id)
        category = parts[1]
        
        formatter = FORMATTERS.get(category)
        if formatter:
            if category == 'ᴀᴅᴍɪɴ':
                text = await formatter(chat_id, settings_data, chat_title)
            else:
                text = formatter(chat_id, settings_data, chat_title)
        else:
            text = f"{fmt_header(chat_title)}⚠️ <b>{category.upper()}</b>\n\n⚠️ ғᴇᴀᴛᴜʀᴇ ɴᴏᴛ ʏᴇᴛ ɪᴍᴘʟᴇᴍᴇɴᴛᴇᴅ{fmt_footer(chat_id)}"
        
        await message.reply_text(
            text,
            reply_markup=build_detail_keyboard(chat_id),
            parse_mode=enums.ParseMode.HTML
        )
        return True
        
    except ValueError:
        await message.reply_text(font("❌ ɪɴᴠᴀʟɪᴅ ᴄʜᴀᴛ ɪᴅ!"))
        return False
    except Exception as e:
        print(f"[SETTINGS_DEEPLINK ERROR] {e}")
        await message.reply_text(font("❌ ᴇʀʀᴏʀ ʟᴏᴀᴅɪɴɢ sᴇᴛᴛɪɴɢs!"))
        return False

@pbot.on_callback_query(filters.regex(r"^sett:"))
async def handle_settings_callback(client: Client, query: CallbackQuery):
    try:
        parts = query.data.split(":")
        
        if len(parts) < 3:
            await query.answer(font("❌ ɪɴᴠᴀʟɪᴅ ᴅᴀᴛᴀ"), show_alert=True)
            return
        
        action = parts[1]
        
        if action == "close":
            await query.answer()
            try:
                await query.message.delete()
            except:
                pass
            return
        
        if action == "back":
            await query.answer(font("🔄 ʟᴏᴀᴅɪɴɢ ᴍᴇɴᴜ..."))
            chat_id = int(parts[2])
            chat_title = await get_chat_title(chat_id)
            
            text = f"<b>⚙️ ᴀᴠᴀɪʟᴀʙʟᴇ sᴇᴛᴛɪɴɢs ғᴏʀ {chat_title}</b>\n\n💫 sᴡɪᴘᴇ ᴀɴᴅ ᴄʜᴇᴄᴋ sᴇᴛᴛɪɴɢs.."
            
            try:
                await query.edit_message_text(
                    text,
                    reply_markup=build_category_keyboard(0, chat_id),
                    parse_mode=enums.ParseMode.HTML
                )
            except Exception as e:
                print(f"[CALLBACK_BACK ERROR] {e}")
            return
        
        if action == "page":
            await query.answer()
            page = int(parts[2])
            chat_id = int(parts[3])
            chat_title = await get_chat_title(chat_id)
            
            text = f"<b>⚙️ ᴀᴠᴀɪʟᴀʙʟᴇ sᴇᴛᴛɪɴɢs ғᴏʀ {chat_title}</b>\n\n💫 sᴡɪᴘᴇ ᴀɴᴅ ᴄʜᴇᴄᴋ sᴇᴛᴛɪɴɢs.."
            
            try:
                await query.edit_message_text(
                    text,
                    reply_markup=build_category_keyboard(page, chat_id),
                    parse_mode=enums.ParseMode.HTML
                )
            except Exception as e:
                print(f"[CALLBACK_PAGE ERROR] {e}")
            return
        
        await query.answer(font("🔄 ʟᴏᴀᴅɪɴɢ..."))
        category = action
        chat_id = int(parts[2])
        chat_title = await get_chat_title(chat_id)
        settings_data = await fetch_settings(chat_id)
        
        formatter = FORMATTERS.get(category)
        if formatter:
            if category == 'ᴀᴅᴍɪɴ':
                text = await formatter(chat_id, settings_data, chat_title)
            else:
                text = formatter(chat_id, settings_data, chat_title)
        else:
            text = f"{fmt_header(chat_title)}⚠️ <b>{category.upper()}</b>\n\n⚠️ ғᴇᴀᴛᴜʀᴇ ɴᴏᴛ ʏᴇᴛ ɪᴍᴘʟᴇᴍᴇɴᴛᴇᴅ{fmt_footer(chat_id)}"
        
        try:
            await query.edit_message_text(
                text,
                reply_markup=build_detail_keyboard(chat_id),
                parse_mode=enums.ParseMode.HTML
            )
        except Exception as e:
            print(f"[CALLBACK_CATEGORY ERROR] {e}")
            
    except ValueError as e:
        await query.answer(font("❌ ɪɴᴠᴀʟɪᴅ ᴅᴀᴛᴀ ғᴏʀᴍᴀᴛ"), show_alert=True)
        print(f"[CALLBACK_VALUE ERROR] {e}")
    except Exception as e:
        await query.answer(font("❌ ᴇʀʀᴏʀ ᴏᴄᴄᴜʀʀᴇᴅ"), show_alert=True)
        print(f"[CALLBACK ERROR] {e}")

@Command(["settings", "setting"], block=False)
@only_groups
@admin_check()
async def show_settings(update: Update, context: ContextTypes.DEFAULT_TYPE):
    import html
    
    chat_id = update.effective_chat.id
    chat_title = update.effective_chat.title
    
    # Escape HTML special characters in chat title
    safe_title = html.escape(chat_title)
    
    text = f"<b>⚙️ ᴀᴠᴀɪʟᴀʙʟᴇ sᴇᴛᴛɪɴɢs ғᴏʀ {safe_title}</b>\n\n💫 ᴄʟɪᴄᴋ ʜᴇʀᴇ ɢᴇᴛ sᴇᴛᴛɪɴɢs ɪɴ ᴘʀɪᴠᴀᴛᴇ..\n\n🎶 ғᴏʀ ᴄʜᴀɴɢᴇ ᴍᴜsɪᴄ ᴘʟᴀʏᴍᴏᴅᴇ\n\n🤖 ᴄʟɪᴄᴋ ʜᴇʀᴇ : /msettings"
    
    bot_username = BOT_USERNAME.lstrip('@')
    keyboard = PTBMarkup([[
        PTBButton(
            "⚙️ sᴇᴛᴛɪɴɢs",
            url=f"t.me/{bot_username}?start=settings_main_{chat_id}"
        )
    ]])
    
    try:
        await update.effective_message.reply_text(text, reply_markup=keyboard, parse_mode="HTML")
    except Exception as e:
        print(f"[SHOW_SETTINGS ERROR] {e}")
