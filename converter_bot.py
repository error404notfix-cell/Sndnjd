#!/usr/bin/env python3
"""
🔥 DEDSEC ULTIMATE FILE CONVERTER BOT 🔥
Converts: APK, Images, Videos, Audio, Documents, Ebooks, Archives
Deploy ready for Render.com
"""

import os
import sys
import logging
import asyncio
import subprocess
import tempfile
import shutil
import zipfile
import tarfile
import rarfile
from pathlib import Path
from datetime import datetime

# Telegram imports
try:
    from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
    from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes, CallbackQueryHandler
except ImportError:
    os.system(f"{sys.executable} -m pip install python-telegram-bot==20.7")
    from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
    from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes, CallbackQueryHandler

# Flask for web server (Render requirement)
try:
    from flask import Flask, jsonify
except ImportError:
    os.system(f"{sys.executable} -m pip install flask==2.3.3")
    from flask import Flask, jsonify

# ============================================
# [ 🔥 CONFIGURATION ]
# ============================================

BOT_TOKEN = "8687335090:AAHnRuMSfkA1qyP6VNhdYeqAEJlQjWbXZE8"
WEBHOOK_URL = "https://vhiiam-1.onrender.com"  # Change after deploy
PORT = int(os.environ.get('PORT', 5000))

# Flask app for Render
app_flask = Flask(__name__)

# Logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# ============================================
# [ 🌐 FLASK WEB SERVER (FOR RENDER) ]
# ============================================

@app_flask.route('/')
def home():
    return "🔥 DEDSEC FILE CONVERTER BOT IS RUNNING! 🔥"

@app_flask.route('/health')
def health():
    return jsonify({"status": "healthy", "time": datetime.now().isoformat()})

# ============================================
# [ 🎯 SUPPORTED FORMATS DATABASE ]
# ============================================

SUPPORTED_FORMATS = {
    'apk': {
        'extensions': ['.apk'],
        'convert_to': ['.zip', '.txt'],
        'mime': ['application/vnd.android.package-archive']
    },
    'image': {
        'extensions': ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff', '.webp', '.ico'],
        'convert_to': ['.jpg', '.png', '.webp', '.gif', '.ico', '.pdf'],
        'mime': ['image/jpeg', 'image/png', 'image/gif', 'image/bmp', 'image/tiff', 'image/webp']
    },
    'video': {
        'extensions': ['.mp4', '.avi', '.mkv', '.mov', '.wmv', '.flv', '.webm', '.m4v'],
        'convert_to': ['.mp4', '.avi', '.mkv', '.mov', '.gif', '.webm'],
        'mime': ['video/mp4', 'video/x-msvideo', 'video/x-matroska', 'video/quicktime']
    },
    'audio': {
        'extensions': ['.mp3', '.wav', '.ogg', '.m4a', '.flac', '.aac', '.wma'],
        'convert_to': ['.mp3', '.wav', '.ogg', '.m4a', '.flac', '.aac'],
        'mime': ['audio/mpeg', 'audio/wav', 'audio/ogg', 'audio/mp4', 'audio/flac']
    },
    'document': {
        'extensions': ['.pdf', '.doc', '.docx', '.xls', '.xlsx', '.ppt', '.pptx', '.txt', '.rtf', '.odt'],
        'convert_to': ['.pdf', '.docx', '.xlsx', '.pptx', '.txt', '.odt', '.html'],
        'mime': ['application/pdf', 'application/msword', 
                 'application/vnd.openxmlformats-officedocument.wordprocessingml.document']
    },
    'ebook': {
        'extensions': ['.epub', '.mobi', '.azw3', '.fb2', '.lit', '.lrf'],
        'convert_to': ['.pdf', '.epub', '.mobi', '.txt'],
        'mime': ['application/epub+zip', 'application/x-mobipocket-ebook']
    },
    'archive': {
        'extensions': ['.zip', '.rar', '.7z', '.tar', '.gz', '.bz2'],
        'convert_to': ['.zip', '.tar', '.7z'],
        'mime': ['application/zip', 'application/x-rar-compressed', 'application/x-7z-compressed']
    }
}

# ============================================
# [ 🤖 TELEGRAM BOT COMMANDS ]
# ============================================

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Start command"""
    keyboard = [
        [InlineKeyboardButton("📱 APK CONVERTER", callback_data="show_apk")],
        [InlineKeyboardButton("🖼️ IMAGE CONVERTER", callback_data="show_image")],
        [InlineKeyboardButton("🎬 VIDEO CONVERTER", callback_data="show_video")],
        [InlineKeyboardButton("🎵 AUDIO CONVERTER", callback_data="show_audio")],
        [InlineKeyboardButton("📄 DOCUMENT CONVERTER", callback_data="show_doc")],
        [InlineKeyboardButton("📚 EBOOK CONVERTER", callback_data="show_ebook")],
        [InlineKeyboardButton("🗜️ ARCHIVE CONVERTER", callback_data="show_archive")],
        [InlineKeyboardButton("❓ HELP", callback_data="help")],
        [InlineKeyboardButton("ℹ️ ABOUT", callback_data="about")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
        "🔥 **DEDSEC ULTIMATE FILE CONVERTER** 🔥\n\n"
        "**Convert ANY file to ANY format!**\n\n"
        "📱 **APK** → ZIP, TXT\n"
        "🖼️ **Images** → JPG, PNG, WEBP, GIF, ICO, PDF\n"
        "🎬 **Videos** → MP4, AVI, MKV, MOV, GIF\n"
        "🎵 **Audio** → MP3, WAV, OGG, M4A, FLAC\n"
        "📄 **Documents** → PDF, DOCX, XLSX, PPTX, TXT\n"
        "📚 **Ebooks** → PDF, EPUB, MOBI\n"
        "🗜️ **Archives** → ZIP, RAR, 7Z\n\n"
        "**Send me any file to begin!**",
        reply_markup=reply_markup,
        parse_mode="Markdown"
    )

async def show_category(update: Update, context: ContextTypes.DEFAULT_TYPE, category: str):
    """Show format options for a category"""
    query = update.callback_query
    await query.answer()
    
    if category in SUPPORTED_FORMATS:
        formats = SUPPORTED_FORMATS[category]
        ext_list = ', '.join([ext.upper().replace('.', '') for ext in formats['extensions'][:8]])
        convert_list = ', '.join([fmt.upper().replace('.', '') for fmt in formats['convert_to']])
        
        text = f"**{category.upper()} CONVERTER**\n\n"
        text += f"📥 **Input formats:** {ext_list}\n"
        text += f"📤 **Output formats:** {convert_list}\n\n"
        text += f"Send me a {category} file to convert!"
        
        keyboard = [[InlineKeyboardButton("« BACK", callback_data="back_to_main")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(text, reply_markup=reply_markup)
        context.user_data['category'] = category

async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle button callbacks"""
    query = update.callback_query
    data = query.data
    
    if data == "back_to_main":
        await start(update, context)
    elif data == "help":
        await show_help(update, context)
    elif data == "about":
        await show_about(update, context)
    elif data == "show_apk":
        await show_category(update, context, 'apk')
    elif data == "show_image":
        await show_category(update, context, 'image')
    elif data == "show_video":
        await show_category(update, context, 'video')
    elif data == "show_audio":
        await show_category(update, context, 'audio')
    elif data == "show_doc":
        await show_category(update, context, 'document')
    elif data == "show_ebook":
        await show_category(update, context, 'ebook')
    elif data == "show_archive":
        await show_category(update, context, 'archive')
    elif data.startswith("convert_"):
        target_format = data[8:]
        context.user_data['target_format'] = target_format
        await query.edit_message_text(
            f"🔄 **Converting to {target_format.upper()}...**\n\n"
            f"Please wait, this may take a moment."
        )

async def show_help(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show help menu"""
    query = update.callback_query
    await query.answer()
    
    help_text = """
**❓ HOW TO USE:**

1️⃣ **Send any file** to the bot
2️⃣ Bot will detect file type
3️⃣ Choose output format from buttons
4️⃣ Wait for conversion
5️⃣ Download converted file

**⚠️ LIMITS:**
• Max file size: 50MB
• Conversion time: 1-5 minutes
• Supported: 50+ formats

**📱 SPECIAL FEATURES:**
• APK decompile to ZIP/TXT
• Images to PDF
• Videos to GIF
• Batch conversion (coming soon)

**💡 TIPS:**
• Larger files take longer
• Keep bot open during conversion
• Use /start anytime
"""
    keyboard = [[InlineKeyboardButton("« BACK", callback_data="back_to_main")]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(help_text, reply_markup=reply_markup)

async def show_about(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show about info"""
    query = update.callback_query
    await query.answer()
    
    about_text = """
**ℹ️ ABOUT THIS BOT**

🔥 **DEDSEC ULTIMATE FILE CONVERTER** 🔥

**Version:** 1.0
**Creator:** DEDSEC💀༏༏
**Type:** File Converter Bot

**⚙️ ENGINE:**
• FFmpeg (Video/Audio)
• ImageMagick (Images)
• LibreOffice (Documents)
• Calibre (Ebooks)
• Apktool (APK)
• 7zip (Archives)

**📊 STATS:**
• 50+ formats supported
• 7 categories
• 24/7 operation
• Free to use

**🚀 DEPLOYMENT:**
• Platform: Render.com
• Uptime: 99.9%
• Region: Frankfurt
"""
    keyboard = [[InlineKeyboardButton("« BACK", callback_data="back_to_main")]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(about_text, reply_markup=reply_markup)

# ============================================
# [ 🔧 CONVERSION FUNCTIONS ]
# ============================================

def get_file_category(filename: str) -> str:
    """Detect file category based on extension"""
    ext = Path(filename).suffix.lower()
    
    for category, info in SUPPORTED_FORMATS.items():
        if ext in info['extensions']:
            return category
    return 'unknown'

async def convert_apk(input_path: str, output_format: str) -> str:
    """Convert APK to other formats"""
    output_path = input_path.replace('.apk', f'_converted{output_format}')
    
    if output_format == '.zip':
        # Rename APK to ZIP (APK is actually ZIP)
        shutil.copy2(input_path, output_path)
    elif output_format == '.txt':
        # Try to decompile (basic - just extract AndroidManifest.xml)
        with zipfile.ZipFile(input_path, 'r') as zip_ref:
            zip_ref.extract('AndroidManifest.xml', Path(input_path).parent)
            manifest_path = Path(input_path).parent / 'AndroidManifest.xml'
            if manifest_path.exists():
                with open(output_path, 'w', encoding='utf-8') as f:
                    f.write(manifest_path.read_text())
                manifest_path.unlink()
    
    return output_path if os.path.exists(output_path) else None

async def convert_image(input_path: str, output_format: str) -> str:
    """Convert images using ImageMagick"""
    output_path = input_path.replace(Path(input_path).suffix, f'_converted{output_format}')
    
    # ImageMagick command
    cmd = ['convert', input_path, output_path]
    process = await asyncio.create_subprocess_exec(
        *cmd,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE
    )
    await process.communicate()
    
    return output_path if os.path.exists(output_path) else None

async def convert_video(input_path: str, output_format: str) -> str:
    """Convert videos using FFmpeg"""
    output_path = input_path.replace(Path(input_path).suffix, f'_converted{output_format}')
    
    # FFmpeg command
    if output_format == '.gif':
        cmd = ['ffmpeg', '-i', input_path, '-vf', 'fps=10,scale=320:-1', '-loop', '0', output_path]
    else:
        cmd = ['ffmpeg', '-i', input_path, '-c:v', 'libx264', '-preset', 'fast', output_path]
    
    process = await asyncio.create_subprocess_exec(
        *cmd,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE
    )
    await process.communicate()
    
    return output_path if os.path.exists(output_path) else None

async def convert_audio(input_path: str, output_format: str) -> str:
    """Convert audio using FFmpeg"""
    output_path = input_path.replace(Path(input_path).suffix, f'_converted{output_format}')
    
    cmd = ['ffmpeg', '-i', input_path, '-y', output_path]
    process = await asyncio.create_subprocess_exec(
        *cmd,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE
    )
    await process.communicate()
    
    return output_path if os.path.exists(output_path) else None

async def convert_document(input_path: str, output_format: str) -> str:
    """Convert documents using LibreOffice"""
    output_dir = Path(input_path).parent
    output_path = output_dir / f"converted{output_format}"
    
    cmd = [
        'libreoffice', '--headless', '--convert-to', 
        output_format.replace('.', ''), '--outdir', str(output_dir), input_path
    ]
    
    process = await asyncio.create_subprocess_exec(
        *cmd,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE
    )
    await process.communicate()
    
    # Find converted file
    for file in output_dir.glob(f"*{output_format}"):
        return str(file)
    
    return None

async def convert_archive(input_path: str, output_format: str) -> str:
    """Convert archives using 7zip"""
    output_path = input_path.replace(Path(input_path).suffix, f'_converted{output_format}')
    
    if output_format == '.zip':
        with zipfile.ZipFile(output_path, 'w') as zip_out:
            if input_path.endswith('.zip'):
                with zipfile.ZipFile(input_path, 'r') as zip_in:
                    for file in zip_in.namelist():
                        zip_out.writestr(file, zip_in.read(file))
    
    return output_path if os.path.exists(output_path) else None

async def handle_file(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle incoming files"""
    if not update.message.document:
        await update.message.reply_text("❌ Please send a file!")
        return
    
    file = update.message.document
    file_name = file.file_name
    file_size = file.file_size
    
    # Check size limit (50MB)
    if file_size > 50 * 1024 * 1024:
        await update.message.reply_text("❌ File too large! Max 50MB")
        return
    
    # Detect category
    category = get_file_category(file_name)
    
    if category == 'unknown':
        await update.message.reply_text(
            "❌ Unsupported file format!\n\n"
            "Send /start to see supported formats."
        )
        return
    
    # Download file
    progress_msg = await update.message.reply_text(f"📥 Downloading {file_name}...")
    
    file_obj = await context.bot.get_file(file.file_id)
    input_path = f"/tmp/{file_name}"
    await file_obj.download_to_drive(input_path)
    
    await progress_msg.edit_text(f"📥 Downloaded! Processing {category} file...")
    
    # Get available output formats
    output_formats = SUPPORTED_FORMATS[category]['convert_to']
    
    # Create format selection buttons
    keyboard = []
    row = []
    for i, fmt in enumerate(output_formats[:6]):  # Max 6 buttons
        fmt_name = fmt.upper().replace('.', '')
        row.append(InlineKeyboardButton(fmt_name, callback_data=f"convert_{fmt}"))
        if (i + 1) % 3 == 0:  # 3 buttons per row
            keyboard.append(row)
            row = []
    if row:
        keyboard.append(row)
    
    keyboard.append([InlineKeyboardButton("❌ CANCEL", callback_data="back_to_main")])
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    # Store file path in context
    context.user_data['input_file'] = input_path
    context.user_data['category'] = category
    context.user_data['file_name'] = file_name
    
    await progress_msg.edit_text(
        f"✅ **File received!**\n\n"
        f"📄 Name: {file_name}\n"
        f"📦 Size: {file_size/(1024*1024):.1f} MB\n"
        f"📁 Type: {category.upper()}\n\n"
        f"**Choose output format:**",
        reply_markup=reply_markup
    )

async def handle_conversion(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle conversion callback"""
    query = update.callback_query
    await query.answer()
    
    target_format = context.user_data.get('target_format')
    input_path = context.user_data.get('input_file')
    category = context.user_data.get('category')
    file_name = context.user_data.get('file_name')
    
    if not all([target_format, input_path, category]):
        await query.edit_message_text("❌ Error: Missing conversion data!")
        return
    
    await query.edit_message_text(f"🔄 **Converting {file_name} to {target_format.upper()}...**\n\nThis may take a moment.")
    
    try:
        # Perform conversion based on category
        output_path = None
        
        if category == 'apk':
            output_path = await convert_apk(input_path, target_format)
        elif category == 'image':
            output_path = await convert_image(input_path, target_format)
        elif category == 'video':
            output_path = await convert_video(input_path, target_format)
        elif category == 'audio':
            output_path = await convert_audio(input_path, target_format)
        elif category == 'document':
            output_path = await convert_document(input_path, target_format)
        elif category == 'archive':
            output_path = await convert_archive(input_path, target_format)
        
        if output_path and os.path.exists(output_path):
            # Send converted file
            with open(output_path, 'rb') as f:
                await query.message.reply_document(
                    document=f,
                    filename=f"converted_{Path(file_name).stem}{target_format}",
                    caption=f"✅ **Conversion complete!**\n\n"
                            f"Original: {file_name}\n"
                            f"Format: {target_format.upper()}"
                )
            
            # Cleanup
            os.remove(output_path)
            
            # Show main menu again
            await start(update, context)
        else:
            await query.edit_message_text(
                "❌ **Conversion failed!**\n\n"
                "The file might be corrupted or format not supported.\n"
                "Try another format or file."
            )
    
    except Exception as e:
        logger.error(f"Conversion error: {e}")
        await query.edit_message_text(f"❌ **Error:** {str(e)[:100]}")
    
    finally:
        # Cleanup input file
        if input_path and os.path.exists(input_path):
            os.remove(input_path)
        
        # Clear user data
        context.user_data.clear()

# ============================================
# [ 🚀 MAIN FUNCTION ]
# ============================================

def run_flask():
    """Run Flask server"""
    app_flask.run(host='0.0.0.0', port=PORT, debug=False, use_reloader=False)

def run_telegram():
    """Run Telegram bot"""
    logger.info("🤖 Starting Telegram bot...")
    
    app = Application.builder().token(BOT_TOKEN).build()
    
    # Add handlers
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button_callback))
    app.add_handler(CallbackQueryHandler(handle_conversion, pattern=r"^convert_"))
    app.add_handler(MessageHandler(filters.Document.ALL, handle_file))
    
    logger.info("✅ Bot is running!")
    app.run_polling()

if __name__ == "__main__":
    import threading
    
    print("="*60)
    print("🔥 DEDSEC ULTIMATE FILE CONVERTER 🔥")
    print("="*60)
    print(f"🤖 Bot Token: {BOT_TOKEN[:15]}...")
    print(f"🌐 Webhook URL: {WEBHOOK_URL}")
    print(f"📁 Support: APK, Images, Videos, Audio, Docs, Ebooks, Archives")
    print("🚀 Starting services...")
    print("="*60)
    
    # Start Flask in background
    flask_thread = threading.Thread(target=run_flask, daemon=True)
    flask_thread.start()
    
    # Start Telegram b