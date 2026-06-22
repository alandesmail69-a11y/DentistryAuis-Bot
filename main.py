import os, io, threading
from flask import Flask
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes
import PyPDF2
from openai import OpenAI

# ---------- FLASK WEB SERVER ----------
flask_app = Flask(__name__)

@flask_app.route('/')
def index():
    return "🦷 Dentistry Bot is running!", 200

def run_web_server():
    port = int(os.environ.get('PORT', 8000))
    flask_app.run(host='0.0.0.0', port=port)

# ---------- GROQ AI SETUP ----------
GROQ_API_KEY = os.environ.get("GROQ_API_KEY")
if not GROQ_API_KEY:
    print("❌ Missing GROQ_API_KEY!")
    exit(1)

client = OpenAI(
    api_key=GROQ_API_KEY,
    base_url="https://api.groq.com/openai/v1"
)

def ask_groq(prompt):
    response = client.chat.completions.create(
        model="mixtral-8x7b-32768",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.7
    )
    return response.choices[0].message.content

# ---------- COURSES AND LECTURES ----------
LECTURES = {
    "1": {
        "name": "Semester 1",
        "courses": {
            "ethics": {
                "name": "Ethics",
                "files": [
                    f"telegram-bot/pdfs/1/ethics/ethics{i}.pdf" for i in range(1, 14)
                ],
                "desc": "Ethics in dentistry (13 files)"
            },
            "terminology": {
                "name": "Terminology",
                "files": [
                    f"telegram-bot/pdfs/1/terminology/term{i}.pdf" for i in range(1, 21)
                ],
                "desc": "Dental terminology (20 files)"
            },
            "biology": {
                "name": "Biology",
                "files": [
                    f"telegram-bot/pdfs/1/biology/bio{i}.pdf" for i in range(1, 16)
                ],
                "desc": "Oral biology (15 files)"
            }
        }
    },
    "2": {"name": "Semester 2", "courses": {}},
    "3": {"name": "Semester 3", "courses": {}},
    "4": {"name": "Semester 4", "courses": {}},
    "5": {"name": "Semester 5", "courses": {}},
    "6": {"name": "Semester 6", "courses": {}},
    "7": {"name": "Semester 7", "courses": {}},
    "8": {"name": "Semester 8", "courses": {}},
    "9": {"name": "Semester 9", "courses": {}},
    "10": {"name": "Semester 10", "courses": {}},
    "11": {"name": "Semester 11", "courses": {}}
}

course_contents = {}

def load_pdfs():
    for sem_id, sem_data in LECTURES.items():
        for course_id, course_data in sem_data.get("courses", {}).items():
            files = course_data.get("files", [])
            combined_text = ""
            all_exist = True
            for file_name in files:
                if os.path.exists(file_name):
                    try:
                        with open(file_name, "rb") as f:
                            reader = PyPDF2.PdfReader(f)
                            for page in reader.pages:
                                combined_text += page.extract_text()
                        print(f"✅ Loaded {file_name}")
                    except Exception as e:
                        print(f"⚠️ Error reading {file_name}: {e}")
                else:
                    print(f"⚠️ File {file_name} not found!")
                    all_exist = False
            if all_exist and combined_text.strip():
                key = f"{sem_id}_{course_id}"
                course_contents[key] = combined_text
                print(f"📚 Combined {len(files)} files → {len(combined_text)} chars")
            else:
                print(f"⚠️ Could not load {course_id} – check file paths")

load_pdfs()

# ---------- GET TELEGRAM TOKEN ----------
TOKEN = os.environ.get("TELEGRAM_TOKEN")
if not TOKEN:
    print("❌ Missing TELEGRAM_TOKEN!")
    exit(1)

# ---------- BOT FUNCTIONS ----------
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [[InlineKeyboardButton(f"📚 {LECTURES[s]['name']}", callback_data=f"sem_{s}")] for s in LECTURES]
    await update.message.reply_text("🦷 Welcome! Choose a semester:", reply_markup=InlineKeyboardMarkup(keyboard))

async def button_click(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data

    if data.startswith("sem_"):
        sem_id = data[4:]  # everything after "sem_"
        context.user_data["sem"] = sem_id
        courses = LECTURES.get(sem_id, {}).get("courses", {})
        if not courses:
            await query.edit_message_text(f"📂 {LECTURES[sem_id]['name']}\n\n⚠️ No courses added yet.")
            return
        keyboard = []
        for course_id, course_data in courses.items():
            name = course_data.get("name", course_id)
            key = f"{sem_id}_{course_id}"
            status = "✅" if key in course_contents else "📤"
            keyboard.append([InlineKeyboardButton(f"{status} {name}", callback_data=f"course_{key}")])
        keyboard.append([InlineKeyboardButton("🔙 Back", callback_data="back")])
        await query.edit_message_text(f"📂 {LECTURES[sem_id]['name']} - Choose a course:", reply_markup=InlineKeyboardMarkup(keyboard))

    elif data.startswith("course_"):
        key = data[7:]  # everything after "course_"
        # key is like "1_ethics"
        parts = key.split("_", 1)
        if len(parts) != 2:
            await query.edit_message_text("⚠️ Invalid course selection.")
            return
        sem_id, course_id = parts
        if sem_id not in LECTURES or course_id not in LECTURES[sem_id].get("courses", {}):
            await query.edit_message_text("⚠️ Course not found.")
            return
        course_data = LECTURES[sem_id]["courses"][course_id]
        course_name = course_data.get("name", course_id)
        context.user_data['current_course'] = key
        files = course_data.get("files", [])
        if not files:
            await query.edit_message_text("⚠️ No PDF files defined.")
            return
        keyboard = []
        for idx, file_name in enumerate(files, 1):
            keyboard.append([InlineKeyboardButton(f"📄 Lecture {idx}", callback_data=f"lecture_{key}_{idx-1}")])
        keyboard.append([InlineKeyboardButton("🔙 Back to Courses", callback_data=f"sem_{sem_id}")])
        await query.edit_message_text(
            f"📚 *{course_name}*\n{len(files)} lectures available.\n\nClick a lecture to view it.",
            parse_mode="Markdown",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )

    elif data.startswith("lecture_"):
        # format: lecture_{sem}_{course}_{idx}
        # e.g. lecture_1_ethics_0
        remainder = data[8:]  # after "lecture_"
        # split off the last part (index)
        last_underscore = remainder.rfind("_")
        if last_underscore == -1:
            await query.edit_message_text("⚠️ Invalid lecture selection.")
            return
        key = remainder[:last_underscore]   # "1_ethics"
        idx = int(remainder[last_underscore + 1:])
        parts = key.split("_", 1)
        if len(parts) != 2:
            await query.edit_message_text("⚠️ Invalid lecture selection.")
            return
        sem_id, course_id = parts
        if sem_id not in LECTURES or course_id not in LECTURES[sem_id].get("courses", {}):
            await query.edit_message_text("⚠️ Course not found.")
            return
        course_data = LECTURES[sem_id]["courses"][course_id]
        files = course_data.get("files", [])
        if idx >= len(files):
            await query.edit_message_text("⚠️ Lecture not found.")
            return
        file_name = files[idx]
        if not os.path.exists(file_name):
            await query.edit_message_text(f"⚠️ File not found on server: {file_name}")
            return
        await context.bot.send_document(
            chat_id=update.effective_chat.id,
            document=open(file_name, 'rb'),
            caption=f"📄 {course_data['name']} - Lecture {idx+1}"
        )
        if key in course_contents:
            keyboard = [
                [InlineKeyboardButton("❓ Ask Question", callback_data=f"ask_{key}")],
                [InlineKeyboardButton("📝 Generate Quiz", callback_data=f"quiz_{key}")],
                [InlineKeyboardButton("🔙 Back to Lectures", callback_data=f"course_{key}")]
            ]
            await query.edit_message_text(
                f"✅ *{course_data['name']}* - Lecture {idx+1} sent.\n\n💡 Ask questions based on ALL lectures in this course!",
                parse_mode="Markdown",
                reply_markup=InlineKeyboardMarkup(keyboard)
            )
        else:
            await query.edit_message_text("⚠️ Course content not loaded — AI questions unavailable.")

    elif data.startswith("ask_") or data.startswith("quiz_"):
        key = data[4:]  # everything after "ask_" or "quiz_"
        context.user_data['current_course'] = key
        context.user_data['action'] = "ask" if data.startswith("ask_") else "quiz"
        if data.startswith("ask_"):
            await query.edit_message_text("✍️ Type your question below.")
        else:
            await query.edit_message_text("✍️ Type 'yes' to get a 5-question quiz on this course.")

    elif data == "back":
        keyboard = [[InlineKeyboardButton(f"📚 {LECTURES[s]['name']}", callback_data=f"sem_{s}")] for s in LECTURES]
        await query.edit_message_text("🦷 Welcome! Choose a semester:", reply_markup=InlineKeyboardMarkup(keyboard))

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_text = update.message.text
    key = context.user_data.get('current_course')
    action = context.user_data.get('action', 'ask')
    if not key or key not in course_contents:
        await update.message.reply_text("⚠️ Please select a course first via /start.")
        return
    lecture_text = course_contents[key]
    parts = key.split("_", 1)
    sem_id, course_id = parts
    course_name = LECTURES[sem_id]["courses"][course_id].get("name", course_id)
    try:
        if action == "quiz":
            prompt = f"""You are a dentistry professor. Based ONLY on this lecture text, generate a 5-question multiple-choice quiz.
Lecture text: {lecture_text}
Student request: {user_text}
Format: List 5 questions with 4 options each (A, B, C, D) and provide the correct answers at the end."""
        else:
            prompt = f"""You are a dentistry professor. Based ONLY on this lecture text, answer the student's question clearly.
Lecture text: {lecture_text}
Student question: {user_text}"""

        response = ask_groq(prompt)
        await update.message.reply_text(f"🧑‍🏫 *{course_name}*\n\n{response}", parse_mode="Markdown")
        context.user_data['action'] = 'ask'
    except Exception as e:
        await update.message.reply_text(f"⚠️ AI error: {str(e)}")

def main():
    threading.Thread(target=run_web_server, daemon=True).start()
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button_click))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    print("🤖 Bot is running...")
    app.run_polling()

if __name__ == "__main__":
    main()
