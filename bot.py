from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, FSInputFile
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.client.session.aiohttp import AiohttpSession
import asyncio
from pathlib import Path
import time
import json
import traceback

# Tarjima funksiyasini import qilish
from slaydtranslate import slaydt

BOT_TOKEN = "8508767861:AAGvTqzevWzCIicsIGJkzHeBQqFxNLK6Bk4"

# Bot va Dispatcher yaratish
session = AiohttpSession(timeout=900)
bot = Bot(token=BOT_TOKEN,session=session)
storage = MemoryStorage()
dp = Dispatcher(storage=storage)

# Files papkasini yaratish
FILES_DIR = Path("files")
FILES_DIR.mkdir(exist_ok=True)

# FSM States
class TranslateStates(StatesGroup):
    waiting_for_file = State()
    waiting_for_source_language = State()
    waiting_for_target_language = State()

# Til kodlari lug'ati
LANGUAGE_CODES = {
    "Qaraqalpaqsha": "kaa_Latn",
    "Қорақалпоқча": "kaa_Cyrl",
    "O‘zbekcha": "eng_Latn",
    "Ўзбекча": "uzn_Cyrl",
    "Qozoqcha": "kaz_Cyrl",
    "Ruscha": "rus_Cyrl",
    "Inglizcha": "eng_Latn",
    "Turkcha": "rus_Cyrl",
    "Koreyscha": "kor_Hang",
    "Xitoycha": "zho_Hans",
}

# Faylni xavfsiz o'chirish funksiyasi
def safe_delete(file_path, max_retries=5, delay=0.5):
    """Faylni xavfsiz o'chirish, agar ishlatilayotgan bo'lsa kutadi"""
    for attempt in range(max_retries):
        try:
            if file_path.exists():
                file_path.unlink()
            return True
        except PermissionError:
            if attempt < max_retries - 1:
                time.sleep(delay)
            else:
                print(f"⚠️ Faylni o'chirib bo'lmadi: {file_path}")
                return False
        except Exception as e:
            print(f"❌ Xato: {e}")
            return False
    return False

# Start komandasi handleri
@dp.message(Command("start"))
async def cmd_start(message: types.Message, state: FSMContext):
    """Start komandasi"""
    await state.clear()

    welcome_text = (
        "🎉 Xosh keldin'iz!\n\n"
        "Men sizge fayllarin'izdi awdarmalap beremen.\n"
        "Faylarin'izdi awdarmalaw ushin /translate."
    )

    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Awdarmalaw", callback_data="translate_slide")],
        [InlineKeyboardButton(text="👤 Profil", callback_data="profile")],
        [InlineKeyboardButton(text="📊 Statistika", callback_data="statistics")],
        [InlineKeyboardButton(text="ℹ️ Jardem", callback_data="help")]
    ])

    await message.answer(welcome_text, reply_markup=keyboard)

# Inline button handleri
@dp.callback_query(F.data == "profile")
async def callback_profile(callback: types.CallbackQuery):
    """Profil buttoni"""
    await callback.answer()
    user = callback.from_user
    profile_text = (
        "╭━━━━━━━━━━━━━━━━━━━━━━━╮\n"
        "✧ 👤 Profil infoi\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━\n"
        f"✧ Ati: {user.first_name}\n"
        f"✧ Username: @{user.username if user.username else 'Joq'}\n"
        f"✧ ID: {user.id}\n"
        "╰━━━━━━━━━━━━━━━━━━━━━━━╯"
    )

    back_keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="◀️ Artqa", callback_data="back_to_menu")]
    ])

    await callback.message.edit_text(profile_text, reply_markup=back_keyboard)

@dp.callback_query(F.data == "help")
async def callback_help(callback: types.CallbackQuery):
    """Yordam buttoni"""
    await callback.answer()
    help_text = (
        "╭━━━━━━━━━━━━━━━━━━━━━━━╮\n"
        "✧ ℹ️ Jardem\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━\n"
        "1️⃣ /translate komandasin basin'\n"
        "2️⃣ PPTX formatdag'i faylinizdi jiberin'\n"
        "3️⃣ Awele slayd tilin tan'lan'\n"
        "4️⃣ Kiyin qaysi tilge awdarmalaysiz\n"
        "5️⃣ Awdarmalaw baslanadi\n"
        "⚠️ Diqqat:\n"
        "• hazirshe tekg'ana .pptx fayllar qabullanadi\n"
        "╰━━━━━━━━━━━━━━━━━━━━━━━╯"
    )

    back_keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="◀️ Artqa", callback_data="back_to_menu")]
    ])

    await callback.message.edit_text(help_text, reply_markup=back_keyboard)

@dp.callback_query(F.data == "statistics")
async def callback_statistics(callback: types.CallbackQuery):
    """Statistika buttoni"""
    await callback.answer()
    statistics_text = (
        "╭━━━━━━━━━━━━━━━━━━━━━━━╮\n"
        "✧ 📊 Statistika\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━\n"
        "ele islep shigilmadi.\n"
        "╰━━━━━━━━━━━━━━━━━━━━━━━╯"
    )

    back_keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="◀️ Arta", callback_data="back_to_menu")]
    ])

    await callback.message.edit_text(statistics_text, reply_markup=back_keyboard)

@dp.callback_query(F.data == "back_to_menu")
async def callback_back_to_menu(callback: types.CallbackQuery, state: FSMContext):
    """Asosiy menyuga qaytish"""
    await callback.answer()
    await state.clear()

    welcome_text = (
        "🎉 Xosh keldin'iz!\n\n"
        "Men sizge fayllarin'izdi awdarmalap beremen.\n"
        "Faylarin'izdi awdarmalaw ushin /translate."
    )

    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Awdarmalaw", callback_data="translate_slide")],
        [InlineKeyboardButton(text="👤 Profil", callback_data="profile")],
        [InlineKeyboardButton(text="📊 Statistika", callback_data="statistics")],
        [InlineKeyboardButton(text="ℹ️ Jardem", callback_data="help")]
    ])

    await callback.message.edit_text(welcome_text, reply_markup=keyboard)

@dp.callback_query(F.data == "translate_slide")
async def callback_translate_slide(callback: types.CallbackQuery, state: FSMContext):
    """Tarjima buttoni"""
    await callback.answer()
    await cmd_translate(callback.message, state)

# Tarjima komandasi
@dp.message(Command("translate"))
async def cmd_translate(message: types.Message, state: FSMContext):
    """Tarjima qilish komandasi"""
    await message.answer("Iltimos, PPTX faylini yuboring:")
    await state.set_state(TranslateStates.waiting_for_file)

# Fayl yuborish handleri
@dp.message(TranslateStates.waiting_for_file, F.document)
async def handle_file(message: types.Message, state: FSMContext):
    """Faylni qabul qilish va tilni so'rash"""
    document = message.document

    if not document.file_name.lower().endswith('.pptx'):
        await message.answer(
            "❌ Faqat PPTX formatdagi fayllarni yuklang!\n"
            "Qaytadan urinib ko'ring."
        )
        return

    await state.update_data(file_id=document.file_id, file_name=document.file_name)
    await state.set_state(TranslateStates.waiting_for_source_language)

    # Tilni tanlash buttonlari
    keyboard = []
    row = []
    count = 0
    for language, code in LANGUAGE_CODES.items():
        btn_text = f"Slayd tili: {language}"
        btn_data = f"src_lang:{code}"
        row.append(InlineKeyboardButton(text=btn_text, callback_data=btn_data))
        count += 1
        if count % 2 == 0:  # Har 2 ta buttondan keyin yangi qator
            keyboard.append(row)
            row = []
    if row:  # Agar oxirgi qatorda buttonlar bo'lsa
        keyboard.append(row)

    reply_markup = InlineKeyboardMarkup(inline_keyboard=keyboard)

    await message.answer(
        "Iltimos, slayd tilini tanlang:",
        reply_markup=reply_markup
    )

# Asl tilni tanlash handleri
@dp.callback_query(TranslateStates.waiting_for_source_language, F.data.startswith("src_lang:"))
async def source_language_callback(callback: types.CallbackQuery, state: FSMContext):
    """Asl tilni tanlanganda, tarjima tilini so'rash"""
    source_lang = callback.data.split(":")[1]  # Masalan: "eng_Latn"
    if source_lang not in ("rus_Cyrl", "eng_Latn", "uzn_Latn", "uzn_Cyrl", "kaa_Latn", "kaa_Cyrl"):
        await callback.answer("❌Noto'g'ri til kodi!", show_alert=True)
        return
    await state.update_data(source_lang=source_lang)
    await state.set_state(TranslateStates.waiting_for_target_language)

    # Tarjima tilini tanlash buttonlari
    keyboard = []
    row = []
    count = 0
    for language, code in LANGUAGE_CODES.items():
        btn_text = f"Tarjima: {language}"
        btn_data = f"tgt_lang:{code}"
        row.append(InlineKeyboardButton(text=btn_text, callback_data=btn_data))
        count += 1
        if count % 2 == 0:  # Har 2 ta buttondan keyin yangi qator
            keyboard.append(row)
            row = []
    if row:  # Agar oxirgi qatorda buttonlar bo'lsa
        keyboard.append(row)

    reply_markup = InlineKeyboardMarkup(inline_keyboard=keyboard)

    await callback.message.edit_text(
        "Iltimos, tarjima tilini tanlang:",
        reply_markup=reply_markup
    )

# Tarjima tilini tanlash handleri
@dp.callback_query(TranslateStates.waiting_for_target_language, F.data.startswith("tgt_lang:"))
async def target_language_callback(callback: types.CallbackQuery, state: FSMContext):
    """Tarjima tilini tanlanganda, faylni tarjima qilish"""
    target_lang = callback.data.split(":")[1]  # Masalan: "uzn_Latn"
    if target_lang not in ("rus_Cyrl", "eng_Latn", "uzn_Latn", "uzn_Cyrl", "kaa_Latn", "kaa_Cyrl"):
        await callback.answer("❌Noto'g'ri til kodi!", show_alert=True)
        return

    user_data = await state.get_data()
    file_id = user_data.get('file_id')
    file_name = user_data.get('file_name')
    source_lang = user_data.get('source_lang')

    if not file_id or not source_lang:
        await callback.message.answer("❌ Fayl yoki til topilmadi. Iltimos, qaytadan urinib ko'ring.")
        await state.clear()
        return

    status_message = await callback.message.edit_text("⏳ Fayl yuklanmoqda...")

    user_id = callback.from_user.id
    input_file_path = FILES_DIR / f"{user_id}_input.pptx"
    output_file_path = FILES_DIR / f"{user_id}_output.pptx"
    log_file_path = FILES_DIR / f"{user_id}_log.txt"

    try:
        # Eski fayllarni tozalash
        safe_delete(input_file_path)
        safe_delete(output_file_path)
        safe_delete(log_file_path)

        # Faylni saqlash
        file = await bot.get_file(file_id)
        await bot.download_file(file.file_path, destination=input_file_path)

        # Tarjima boshlandi
        await status_message.edit_text(
            "🔄 Tarjima qilinmoqda...\n\n"
            "⏳ Bu jarayon bir necha daqiqa davom etishi mumkin.\n"
            f"Asl til: {source_lang}\n"
            f"Tarjima tili: {target_lang}\n\n"
            "Iltimos kuting, men sizga xabar beraman!"
        )

        # Progress updater - har 30 sekundda xabar yangilash
        async def update_progress():
            messages = [
                "🔄 Tarjima davom etmoqda...\n⏳ Iltimos sabr qiling...",
                "🔄 Hali ham ishlayapman...\n⏳ Tez orada tugaydi...",
                "🔄 Deyarli tayyor...\n⏳ Yana bir oz...",
            ]
            counter = 0
            while True:
                await asyncio.sleep(30)
                try:
                    await status_message.edit_text(messages[counter % len(messages)])
                    counter += 1
                except:
                    break

        # Progress updater ni background'da ishga tushirish
        progress_task = asyncio.create_task(update_progress())

        # Tarjima qilish
        loop = asyncio.get_event_loop()
        result = await loop.run_in_executor(
            None,
            slaydt,
            str(input_file_path),
            str(output_file_path),
            source_lang,
            target_lang
        )

        # Progress task'ni to'xtatish
        progress_task.cancel()

        await status_message.edit_text("✅ Tarjima tugadi! Fayllar yuborilmoqda...")

        # Tarjima qilingan faylni yuborish
        if output_file_path.exists():
            await callback.message.answer_document(
                FSInputFile(output_file_path),
                caption=f"✅ Tarjima muvaffaqiyatli yakunlandi!\n\n"
                        f"📄 Asl fayl: {file_name}\n"
                        f"Asl til: {source_lang}\n"
                        f"Tarjima tili: {target_lang}"
            )

        # Log faylni yuborish
        if log_file_path.exists():
            await callback.message.answer_document(
                FSInputFile(log_file_path),
                caption="📜 Tarjima logi"
            )

        await status_message.delete()

        # Asosiy menyu
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="🔄 Yana tarjima qilish", callback_data="translate_slide")],
            [InlineKeyboardButton(text="🏠 Asosiy menyu", callback_data="back_to_menu")]
        ])

        await callback.message.answer("✅ Tayyor! Yana tarjima qilasizmi?", reply_markup=keyboard)

    except asyncio.CancelledError:
        # Progress task bekor qilinganda
        pass
    except Exception as e:
        await status_message.edit_text(
            f"❌ Xatolik yuz berdi!\n\n"
            f"Xato: {str(e)}\n\n"
            f"Iltimos, qaytadan urinib ko'ring."
        )
        print(f"Error details: {e}")
        traceback.print_exc()

    finally:
        # Fayllarni tozalash
        await asyncio.sleep(2)
        await asyncio.get_event_loop().run_in_executor(None, safe_delete, input_file_path)
        await asyncio.get_event_loop().run_in_executor(None, safe_delete, output_file_path)
        await asyncio.get_event_loop().run_in_executor(None, safe_delete, log_file_path)

        await state.clear()

@dp.message(TranslateStates.waiting_for_file)
async def handle_wrong_format(message: types.Message):
    """Fayl o'rniga boshqa narsa yuborilganda"""
    await message.answer(
        "❌ Iltimos, faqat PPTX formatdagi FAYL yuboring!\n\n"
        "Hozir siz fayl yuborishingiz kerak."
    )
async def main():
    """Botni ishga tushirish"""
    if not BOT_TOKEN:
        print("❌ Xato: BOT_TOKEN topilmadi!")
        return

    print("✅ Bot ishga tushdi...")
    print(f"📁 Fayllar saqlanadigan papka: {FILES_DIR.absolute()}")
    await dp.start_polling(bot)

if __name__ == '__main__':
    asyncio.run(main())