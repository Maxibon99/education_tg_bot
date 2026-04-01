# Импортируем нужные модули
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes
import nest_asyncio
nest_asyncio.apply()

TOKEN = ""  

#для функции get_mathstat_fact()
matstat_topics = [
    "среднее", "медиана", "мода", "средневзвешенное",
    "дисперсия", "стандартное отклонение", "квартили", 
    "интерквартильный размах", "асимметрия", "эксцесс",
    "p-value", "гипотезы", "нулевая гипотеза", "альтернативная гипотеза",
    "уровень значимости", "критическая область", "ошибка I рода", 
    "ошибка II рода", "мощность теста",
    "доверительные интервалы", "доверительная вероятность",
    "корреляция", "коэффициент корреляции", "линейная регрессия",
    "множественная регрессия", "коэффициент детерминации R²",
    "Центральная предельная теорема", "нормальное распределение",
    "стандартное нормальное распределение", "биномиальное распределение",
    "пуассоновское распределение", "равномерное распределение",
    "экспоненциальное распределение", "распределение Стьюдента",
    "хи-квадрат распределение", "F-распределение",
    "выборки", "генеральная совокупность", "репрезентативность",
    "случайная выборка", "стратифицированная выборка", "кластерная выборка",
    "t-тест", "z-тест", "хи-квадрат тест", "F-тест",
    "ANOVA", "двухфакторный ANOVA", "MANOVA",
    "тест Вилкоксона", "тест Манна-Уитни", "тест Краскела-Уоллиса",
    "тест Шапиро-Уилка", "тест Левена", "тест Колмогорова-Смирнова",
    "перцентили", "квантили", "боксплот", "гистограмма",
    "QQ-plot", "матрица корреляций", "scatterplot",
    "остатки", "гомоскедастичность", "нормальность остатков",
    "автокорреляция", "мультиколлинеарность",
    "логистическая регрессия", "ROC-кривая", "AUC",
    "байесовская статистика", "априорное распределение",
    "апостериорное распределение", "байесовский фактор",
    "вероятностная выборка", "ненамеренная выборка",
    "метод моментов", "метод максимального правдоподобия",
    "дисперсионный анализ", "факторный анализ",
    "главные компоненты PCA", "кластерный анализ",
    "дискриминантный анализ", "time series", "тренд",
    "сезонность", "авторегрессия AR", "скользящее среднее MA"
]

ml_topics = [
    "переобучение", "недообучение", "смещение", "разброс",
    "train-test разбиение", "кросс-валидация", "k-fold CV",
    "точность", "полнота", "точность", "F1-мера", "ROC-AUC",
    "матрица ошибок", "нормализация признаков", "стандартизация",
    "one-hot кодирование", "ordinal encoding",
    "градиентный спуск", "скорость обучения", "размер батча",
    "эпохи", "раннее останавление", "регуляризация",
    "L1 регуляризация", "L2 регуляризация", "dropout",
    "подбор гиперпараметров", "сеточный поиск", "случайный поиск",
    "инженерия признаков", "отбор признаков", "проклятье размерности",
    "утечка данных", "дисбаланс классов", "SMOTE", "веса классов",
    "дерево решений", "случайный лес", "градиентный бустинг",
    "XGBoost", "LightGBM", "k-ближайших соседей",
    "метод опорных векторов", "линейная регрессия", "логистическая регрессия",
    "нейронная сеть", "функция активации", "ReLU", "softmax",
    "конвейер", "валидационная выборка", "тестовая выборка",
    "энтропия", "джини", "глубина дерева", "листья",
    "бэггинг", "буфинг", "стэкинг"
]

topics = matstat_topics + ml_topics

# Добавляем импорт и функцию для фактов
from gigachat import GigaChat 
import random
import asyncio
import re
from pylatexenc.latex2text import LatexNodes2Text
from latex2mathml.converter import convert

GIGACHAT_KEY = ""

# ГЛОБАЛЬНЫЙ список пользователей для автоотправки
subscribers = set()

async def get_mathstat_fact():
    """LLM сам выбирает тему + факт"""
    topic = random.choice(topics)
    prompt = f"""Ты эксперт по матстатистике. 

    Тема: {topic}

     Напиши ОДИН короткий факт по этой теме для новичка (3-4 предложения, макс 100 слов). 
    Простыми словами, формулы можно. 

        Правила ответа ОБЯЗАТЕЛЬНЫ:
        - ОДИН факт в 2-3 предложениях (максимум 100 слов)
        - Коротко
        - Сложные темы объясняешь простыми словами
        - Можешь использовать формулы
        - Объясняешь почему именно так обстоит дело, а не иначе
        - НИКОГДА не пиши сразу несколько тем
        - БЕЗ повторов и воды
        - В формулах ОБЯЗАТЕЛЬНО указываешь значенение букв и символом
        - Если возможно, то приводи живой пример для лучшего понимания 
        - Разделяй предложения по абзацам
    
Формат ответа: только факт. Никаких "тема: ..." """

    try:
        async def llm_call():
            with GigaChat(credentials=GIGACHAT_KEY, verify_ssl_certs=False,
                         model='GigaChat-Pro', temperature=0.7, max_new_tokens=120) as giga:
                response = giga.chat(prompt)
                latex_text = response.choices[0].message.content
                
                converter = LatexNodes2Text()
                clean_text = converter.latex_to_text(latex_text)
                clean_text = ' '.join(clean_text.split())
                
                return clean_text
        
        return await asyncio.wait_for(llm_call(), timeout=15.0)
        
    except Exception as e:
        return f"❌ Ошибка: {str(e)}"

# ИСПРАВЛЕННАЯ ФУНКЦИЯ автоотправки
async def auto_fact(context: ContextTypes.DEFAULT_TYPE) -> None:
    """Отправляет факт каждые 30 минут всем подписчикам"""
    global subscribers
    
    if not subscribers:  # Если нет подписчиков - выходим
        return
        
    fact = await get_mathstat_fact()
    keyboard = [[InlineKeyboardButton("📊 Новый факт", callback_data="fact")]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    # Отправляем всем подписчикам БЕЗ send_chat_action (была ошибка!)
    for chat_id in list(subscribers):
        try:
            await context.bot.send_message(
                chat_id=chat_id,
                text=f"📊 Факт:\n{fact}",
                reply_markup=reply_markup,
                parse_mode=None
            )
        except Exception as e:
            print(f"Ошибка отправки {chat_id}: {e}")
            subscribers.discard(chat_id)  # Удаляем неактивных

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    global subscribers
    chat_id = update.effective_chat.id
    subscribers.add(chat_id)
    
    welcome_text = f"✅ Подписка активирована! Факты каждые 30 мин.\nПодписчиков: {len(subscribers)}\n\nПриветствую! Повторенье - мать ученья. Этот бот помогает освоить базу матстатистики и ML."
    
    keyboard = [[InlineKeyboardButton("📊 Получить факт", callback_data="fact")]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(welcome_text, reply_markup=reply_markup)

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()
    
    if query.data == "fact":
        await query.message.chat.send_action("typing")  
        
        fact = await get_mathstat_fact()
        
        keyboard = [[InlineKeyboardButton("📊 Новый факт", callback_data="fact")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.message.reply_text(
            f"📊 Факт:\n{fact}",
            reply_markup=reply_markup,
            parse_mode=None
        )

# Создаем бота
application = Application.builder().token(TOKEN).build()

# Добавляем все хендлеры
application.add_handler(CommandHandler("start", start))
application.add_handler(CallbackQueryHandler(button_handler))

# АВТООТПРАВКА КАЖДЫЕ 30 МИНУТ
application.job_queue.run_repeating(
    auto_fact, 
    interval=60,  # 30 минут
    first=30        # первый через 30 сек
)

print("🚀 Бот запущен! Напиши /start для подписки")
application.run_polling(allowed_updates=Update.ALL_TYPES)
