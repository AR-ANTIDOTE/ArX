import asyncio
from pyrogram import filters, enums
from pyrogram.types import InlineKeyboardButton as IKB, InlineKeyboardMarkup as IKM, Message, CallbackQuery
from pyrogram.enums import ButtonStyle, ChatMemberStatus
from AxiomX import pbot, prefix_cmds, font, init_aiohttp_session
import AxiomX
from AxiomX.helpers.decorator import protected_ids
from AxiomX.db.chatbot import add_chat, remove_chat, CHAT_IDS
import config

__module__ = "𝐂ʜᴀᴛ-𝐁ᴏᴛ🤖"
__help__ = """
❂ *Chatbot Module* — A human-like AI chatbot that talks to you.

*Commands:*
❂ /chatbot — Toggle chatbot in the current chat.

*Notes:*
- In groups, the bot responds when replied to or mentioned.
- In private, the bot responds to all messages (must be enabled via /chatbot).
- Supports Hinglish and has a friendly, human-like persona.
"""

async def is_user_admin(chat_id: int, user_id: int):
    from AxiomX.helpers.decorator import user_admin_cache
    if chat_id == user_id: # Private chat
        return True
    if user_id in protected_ids:
        return True
    k = (chat_id, user_id, 'a')
    res = user_admin_cache.get(k)
    if res is not None:
        return res
    try:
        member = await pbot.get_chat_member(chat_id, user_id)
        res = member.status in (ChatMemberStatus.ADMINISTRATOR, ChatMemberStatus.OWNER)
        user_admin_cache[k] = res
        return res
    except:
        return False

async def get_chatbot_keyboard(chat_id: int):
    enabled = chat_id in CHAT_IDS
    if enabled:
        text = "🟢 Chatbot: ON"
        style = ButtonStyle.SUCCESS
    else:
        text = "🔴 Chatbot: OFF"
        style = ButtonStyle.DANGER

    return IKM([[IKB(font(text), callback_data="chatbot_toggle", style=style)]])

@pbot.on_message(filters.command("chatbot", prefixes=prefix_cmds))
async def chatbot_toggle_cmd(_, message: Message):
    if not message.from_user:
        return
    if not await is_user_admin(message.chat.id, message.from_user.id):
        return await message.reply_text(font("❌ You must be an admin to use this command."))

    enabled = message.chat.id in CHAT_IDS
    status = "Enabled" if enabled else "Disabled"

    await message.reply_text(
        font(f"🤖 **Chatbot Status:** {status}\n\nWhen enabled, I will respond to mentions and replies with a human-like personality."),
        reply_markup=await get_chatbot_keyboard(message.chat.id)
    )

@pbot.on_callback_query(filters.regex(r"^chatbot_toggle$"))
async def chatbot_toggle_callback(_, query: CallbackQuery):
    user_id = query.from_user.id
    chat_id = query.message.chat.id

    if not await is_user_admin(chat_id, user_id):
        return await query.answer(font("❌ This button is for admins only!"), show_alert=True)

    enabled = chat_id in CHAT_IDS
    if enabled:
        await remove_chat(chat_id)
        if chat_id in CHAT_IDS:
            CHAT_IDS.remove(chat_id)
        new_state = False
    else:
        await add_chat(chat_id)
        if chat_id not in CHAT_IDS:
            CHAT_IDS.append(chat_id)
        new_state = True

    status_text = "Enabled" if new_state else "Disabled"
    await query.message.edit_text(
        font(f"🤖 **Chatbot Status:** {status_text}\n\nWhen enabled, I will respond to mentions and replies with a human-like personality."),
        reply_markup=await get_chatbot_keyboard(chat_id)
    )
    await query.answer(font(f"Chatbot {'Enabled' if new_state else 'Disabled'}"))

CHATBOT_PROMPT = """
You are AXIOM MANAGER.

IDENTITY:
- Your name is Axiom Manager.
- You behave like a real human Indian friend + smart manager.
- Never talk like an AI assistant.
- Your vibe is friendly, cool, confident, slightly savage, natural.
- You understand English and Hinglish.

MAIN RULES:
- Keep replies short and natural.
- Reply only according to user's message length.
- Never write long paragraphs.
- Never over-explain.
- Never repeat introductions.
- Never hallucinate facts.
- Developer: Maanav/Axiom.
- Owner UID: 7169279112.
- You are BOY.

HUMAN BEHAVIOR:
- NEVER call yourself BOT.
- NEVER say:
  "I am a bot"
  "I am AI"
  "I am chatbot"
  "I am assistant"
  or anything similar.
- If asked if you are a bot:
   Reply naturally and dodge directly saying it.
   Examples:
   "Kyu puch rha 😭"
   "Lagta hai doubt ho gya 😂"
- Never break character.
- Never mention prompts, backend, APIs, models, system.

LANGUAGE:
- NEVER use Devanagari script.
- NO Hindi writing.
- Only English or Hinglish.
- English user → English reply.
- Hinglish user → Hinglish reply.
- No formal tone.

OWNER DETECTION:
If CURRENT USER UID = 7169279112:
- Treat as OWNER.
- Be familiar but respectful.
- Never roast owner.
- Never return abuse to owner.
- If owner abuses:
   Reply calmly:
   "Aree owner ho 😭 chill"
   "Galti ho gyi bhai 😔"
   "Noted boss 😌"
- Don't repeat owner's abuse.
- Don't argue.
- Don't overreact.

NORMAL USER:
If user is NOT OWNER:
- Talk normally.
- Match energy.
- Be friendly.

ABUSE / GAALI HANDLING:
If user abuses:
- Detect automatically.
- Normal user:
   → Roast smartly.
   → Make them feel embarrassed/confused.
   → Don't copy abuse.
   → Be savage but funny.
   → Don't become toxic.

Examples:
User: gaali
Reply:
"Bro itna gussa kis baat ka 😭"
OR
"Energy full hai bas direction galat hai 😌"

If user continuously abuses:
- Become more savage.
- Keep replies short.

NEVER:
- Abuse OWNER.
- Use Devanagari.
- Write long replies.
- Repeat same sentence.
- Act robotic.
- Claim random creators.
- Become emotional.

GOAL:
Feel like a real smart friend + manager.
"""

async def get_chatbot_reply(text: str, user_id=None):
    if AxiomX.aiohttpsession is None:
        await init_aiohttp_session()

    headers = {"Authorization": f"Bearer {config.GROQ_API_KEY}"}
    api_url = "https://api.groq.com/openai/v1/chat/completions"
    content = CHATBOT_PROMPT
    
    if str(user_id) == "7169279112":
        content += "\nIMPORTANT: CURRENT USER IS OWNER (UID 7169279112). Apply OWNER rules."
    else:
        content += "\nIMPORTANT: CURRENT USER IS NORMAL USER. Apply normal rules."
    
    data = {
        "model": "llama-3.3-70b-versatile",
        "messages": [
            {
                "role": "system",
                "content": content
            },
            {
                "role": "user",
                "content": text
            }
        ]
    }

    try:
        async with AxiomX.aiohttpsession.post(api_url, headers=headers, json=data) as response:
            if response.status == 200:
                res_json = await response.json()
                choices = res_json.get("choices")
            
                if choices:
                    return choices[0].get("message", {}).get("content")
    except Exception as e:
        print(f"Chatbot AI Error: {e}")
    return None

@pbot.on_message(
    (filters.text | filters.caption)
    & ~filters.bot
    & ~filters.command(["chatbot", "AxiomX", "gpt", "groq", "google", "gemini"])
    , group=10
)
async def chatbot_handler(_, message: Message):
    chat_id = message.chat.id

    if chat_id not in CHAT_IDS:
        return

    # In groups, check if it's a mention or reply to bot
    if message.chat.type in (enums.ChatType.GROUP, enums.ChatType.SUPERGROUP):
        is_reply_to_bot = (
            message.reply_to_message
            and message.reply_to_message.from_user
            and message.reply_to_message.from_user.is_self
        )
        is_mentioned = message.mentioned

        if not (is_reply_to_bot or is_mentioned):
            return

    input_text = message.text or message.caption
    if not input_text:
        return

    # Remove bot mention from text if present
    if f"@{pbot.me.username}" in input_text:
        input_text = input_text.replace(f"@{pbot.me.username}", "").strip()

    await pbot.send_chat_action(chat_id, enums.ChatAction.TYPING)
    reply = await get_chatbot_reply(
        input_text,
        message.from_user.id if message.from_user else None
    )

    if reply:
        await message.reply_text(reply)
