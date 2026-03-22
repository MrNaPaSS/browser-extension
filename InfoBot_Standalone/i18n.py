#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Модуль мультиязычности для Telegram бота
Поддерживаемые языки: русский, английский, тайский, испанский, арабский, украинский
"""

from typing import Dict, Any

# Конфигурация языков
LANGUAGES = {
    "ru": {"name": "Русский", "flag": "🇷🇺"},
    "en": {"name": "English", "flag": "🇬🇧"},
    "th": {"name": "ไทย", "flag": "🇹🇭"},
    "es": {"name": "Español", "flag": "🇪🇸"},
    "ar": {"name": "العربية", "flag": "🇸🇦"},
    "uk": {"name": "Українська", "flag": "🇺🇦"}
}

DEFAULT_LANGUAGE = "en"

# Словарь переводов
TEXTS = {
    # Команда /start
    "welcome_title": {
        "ru": "**🔥 СТАРТ БЕСПЛАТНО**",
        "en": "**🔥 START FOR FREE**",
        "th": "**🔥 เริ่มต้นฟรี**",
        "es": "**🔥 EMPEZAR GRATIS**",
        "ar": "**🔥 ابدأ مجانًا**",
        "uk": "**🔥 ПОЧАТОК БЕЗКОШТОВНО**"
    },
    
    "welcome_greeting": {
        "ru": "**👋 Привет в Академии Здравого Трейдера! Ты сделал шаг**",
        "en": "**👋 Welcome trader, if you're already here, you're on the right path!**",
        "th": "**👋 ยินดีต้อนรับเทรดเดอร์ หากคุณอยู่ที่นี่แล้ว คุณมาถูกทางแล้ว!**",
        "es": "**👋 Bienvenido trader, si ya estás aquí, estás en el camino correcto!**",
        "ar": "**👋 مرحباً أيها المتداول، إذا كنت هنا بالفعل، فأنت على الطريق الصحيح!**",
        "uk": "**👋 Вітаю трейдер, якщо ти вже тут, ти на правильному шляху!**"
    },
    
    "welcome_description": {
        "ru": "**Трейдинг - это не лотерея, а точная стратегия: мы убираем хаос эмоций, ставим на ML, статистику и дисциплину. Здесь каждый день - система, которая работает на дистанции, без иллюзий.**",
        "en": "**Trading is not a casino, it's mathematics. We removed emotions and replaced them with ML models and dry statistics.**",
        "th": "**การซื้อขายไม่ใช่คาสิโน มันคือคณิตศาสตร์ เราเอาอารมณ์ออกและแทนที่ด้วยโมเดล ML และสถิติแห้ง**",
        "es": "**El trading no es un casino, es matemáticas. Eliminamos las emociones y las reemplazamos con modelos ML y estadísticas secas.**",
        "ar": "**التداول ليس كازينو، بل رياضيات. أزلنا المشاعر واستبدلناها بنماذج ML والإحصائيات الجافة.**",
        "uk": "**Трейдинг - це не казино, це математика. Ми прибрали емоції та замінили їх на ML-моделі та суху статистику.**"
    },
    
    "welcome_evolution_title": {
        "ru": "**Что ждёт тебя в Академии:**",
        "en": "**Your evolution here:**",
        "th": "**การพัฒนาของคุณที่นี่:**",
        "es": "**Tu evolución aquí:**",
        "ar": "**تطورك هنا:**",
        "uk": "**Твоя еволюція тут:**"
    },
    
    "welcome_level_1": {
        "ru": "**🔹 Лайв-торговля: Сессии в реальном времени - рубим рынок вместе, шаг за шагом.**",
        "en": "**🔹 Level 1 (FREE): Get ready signals for free and start earning without investing in software.**",
        "th": "**🔹 ระดับ 1 (ฟรี): รับสัญญาณสำเร็จรูปฟรีและเริ่มรับรายได้โดยไม่ต้องลงทุนในซอฟต์แวร์**",
        "es": "**🔹 Nivel 1 (GRATIS): Obtén señales listas gratis y comienza a ganar sin invertir en software.**",
        "ar": "**🔹 المستوى 1 (مجاني): احصل على إشارات جاهزة مجاناً وابدأ في الكسب دون الاستثمار في البرامج.**",
        "uk": "**🔹 Level 1 (FREE): Отримай безкоштовно готові сигнали та почни заробляти без вкладень у софт.**"
    },
    
    "welcome_level_2": {
        "ru": "**🔹 Разбор рынка live: Мгновенный анализ - тренды, сигналы, риски**",
        "en": "**🔹 Level 2 (PRO): Take our software - Deep analytics and proprietary indicators.**",
        "th": "**🔹 ระดับ 2 (PRO): รับซอฟต์แวร์ของเรา - การวิเคราะห์เชิงลึกและตัวบ่งชี้ที่เป็นกรรมสิทธิ์**",
        "es": "**🔹 Nivel 2 (PRO): Toma nuestro software - Análisis profundo e indicadores propietarios.**",
        "ar": "**🔹 المستوى 2 (PRO): خذ برنامجنا - تحليلات عميقة ومؤشرات حصرية.**",
        "uk": "**🔹 Level 2 (PRO): Забери наш софт - Глибока аналітика та авторські індикатори.**"
    },
    
    "welcome_level_3": {
        "ru": "**🔹 Здравое комьюнити форум: Обмен реальными опытами - без фейка, только рост и поддержка**",
        "en": "**🔹 Level 3 (MENTOR): Mentorship, full trading breakdown and personal support.**",
        "th": "**🔹 ระดับ 3 (MENTOR): การให้คำปรึกษา การวิเคราะห์การซื้อขายแบบเต็มรูปแบบและการสนับสนุนส่วนบุคคล**",
        "es": "**🔹 Nivel 3 (MENTOR): Mentoría, análisis completo de trading y apoyo personal.**",
        "ar": "**🔹 المستوى 3 (MENTOR): الإرشاد، تحليل تداول كامل والدعم الشخصي.**",
        "uk": "**🔹 Level 3 (MENTOR): Менторство, повний розбір торгівлі та особистий супровід.**"
    },
    
    "welcome_level_4": {
        "ru": "**🔹 Авторские софты: Наши инструменты, автоматизация, трекинг, индикаторы**",
        "en": "**👑 Level 4 (ELITE): Private channel and Live trading with fund.**",
        "th": "**👑 ระดับ 4 (ELITE): ช่องส่วนตัวและการซื้อขายสดกับกองทุน**",
        "es": "**👑 Nivel 4 (ELITE): Canal privado y trading en vivo con fondo.**",
        "ar": "**👑 المستوى 4 (ELITE): قناة خاصة والتداول المباشر مع الصندوق.**",
        "uk": "**👑 Level 4 (ELITE): Закритий канал та Live-торгівля з фондом.**"
    },
    
    "welcome_conclusion": {
        "ru": "**От выбора до профита - один клик. Добро пожаловать 👇**",
        "en": "**You either play or earn systematically. The choice is yours. All the tools are already below 👇**",
        "th": "**คุณสามารถเล่นหรือหารายได้อย่างเป็นระบบ ตัวเลือกอยู่ที่คุณ เครื่องมือทั้งหมดอยู่ด้านล่างแล้ว 👇**",
        "es": "**O juegas o ganas sistemáticamente. La elección es tuya. Todas las herramientas ya están abajo 👇**",
        "ar": "**إما أن تلعب أو تربح بشكل منهجي. الاختيار لك. جميع الأدوات موجودة بالفعل أدناه 👇**",
        "uk": "**Ти або граєш, або заробляєш системно. Вибір за тобою. Весь інструментарій вже внизу 👇**"
    },
    
    "welcome_intro": {
        "ru": "**Сразу после регистрации и пополнения вы получаете доступ к фундаменту нашей системы:**",
        "en": "**Immediately after registration and deposit, you get access to the foundation of our system:**",
        "th": "**ทันทีหลังจากลงทะเบียนและฝากเงิน คุณจะได้รับสิทธิ์เข้าถึงรากฐานของระบบของเรา:**",
        "es": "**Inmediatamente después del registro y depósito, obtienes acceso a la base de nuestro sistema:**",
        "ar": "**مباشرة بعد التسجيل والإيداع، ستحصل على حق الوصول إلى أساس نظامنا:**",
        "uk": "**Відразу після реєстрації та поповнення ви отримуєте доступ до фундаменту нашої системи:**"
    },
    
    "welcome_features_title": {
        "ru": "**🤖 Телеграм Бот & Приложение (FREE)**",
        "en": "**🤖 Telegram Bot & App (FREE)**",
        "th": "**🤖 เทเลแกรมบอท & แอปพลิเคชัน (ฟรี)**",
        "es": "**🤖 Bot de Telegram y App (GRATIS)**",
        "ar": "**🤖 بوت تيليجرام والتطبيق (مجاني)**",
        "uk": "**🤖 Телеграм Бот & Додаток (FREE)**"
    },
    
    "welcome_feature_1": {
        "ru": "**Твои первые шаги в алгоритмическом трейдинге. Получай чистые, отфильтрованные данные и сигналы, чтобы увидеть, как работает наша логика.**",
        "en": "**Your first steps in algorithmic trading. Get clean, filtered data and signals to see how our logic works.**",
        "th": "**ก้าวแรกของคุณในการซื้อขายด้วยอัลกอริทึม รับข้อมูลและสัญญาณที่ผ่านการกรองและสะอาดเพื่อดูว่าตรรกะของเราทำงานอย่างไร**",
        "es": "**Tus primeros pasos en el trading algorítmico. Obtén datos y señales limpios y filtrados para ver cómo funciona nuestra lógica.**",
        "ar": "**خطواتك الأولى في التداول الخوارزمي. احصل على بيانات وإشارات نظيفة ومصفاة لترى كيف يعمل منطقنا.**",
        "uk": "**Твої перші кроки в алгоритмічному трейдингу. Отримуй чисті, відфільтровані дані та сигнали, щоб побачити, як працює наша логіка.**"
    },
    
    "welcome_feature_2": {
        "ru": "",
        "en": "",
        "th": "",
        "es": "",
        "ar": "",
        "uk": ""
    },
    
    "welcome_feature_3": {
        "ru": "**🪧 Твоя Первая Дисциплина: Начни работать с рынком, опираясь на факты, а не на страх или жадность. Сделай первые осознанные сделки.**",
        "en": "**🪧 Your First Discipline: Start working with the market based on facts, not fear or greed. Make your first conscious trades.**",
        "th": "**🪧 วินัยแรกของคุณ: เริ่มทำงานกับตลาดโดยอิงจากข้อเท็จจริง ไม่ใช่ความกลัวหรือความโลภ ทำการซื้อขายอย่างมีสติครั้งแรกของคุณ**",
        "es": "**🪧 Tu Primera Disciplina: Comienza a trabajar con el mercado basándote en hechos, no en miedo o codicia. Realiza tus primeras operaciones conscientes.**",
        "ar": "**🪧 انضباطك الأول: ابدأ العمل مع السوق بناءً على الحقائق، وليس الخوف أو الطمع. قم بصفقاتك الواعية الأولى.**",
        "uk": "**🪧 Твоя Перша Дисципліна: Почни працювати з ринком, спираючись на факти, а не на страх або жадібність. Зроби перші усвідомлені угоди.**",
    },
    
    "welcome_feature_4": {
        "ru": "",
        "en": "",
        "th": "",
        "es": "",
        "ar": ""
    },
    
    "welcome_how_title": {
        "ru": "**🚀 СИСТЕМА, КОТОРАЯ РАСТЕТ ВМЕСТЕ С ТОБОЙ**",
        "en": "**🚀 A SYSTEM THAT GROWS WITH YOU**",
        "th": "**🚀 ระบบที่เติบโตไปพร้อมกับคุณ**",
        "es": "**🚀 UN SISTEMA QUE CRECE CONTIGO**",
        "ar": "**🚀 نظام ينمو معك**",
        "uk": "**🚀 СИСТЕМА, ЯКА РОСТЕ РАЗОМ З ТОБОЮ**",
    },
    
    "welcome_step_1": {
        "ru": "**🍸 Бесплатный доступ - это только вход в экосистему. Внутри тебя ждет глубина, которая позволяет выбрать свой путь развития:**",
        "en": "**🍸 Free access is just the entry into the ecosystem. Inside, depth awaits you, allowing you to choose your development path:**",
        "th": "**🍸 การเข้าถึงฟรีเป็นเพียงทางเข้าสู่ระบบนิเวศ ภายในมีความลึกซึ้งรอคุณอยู่ ซึ่งช่วยให้คุณเลือกเส้นทางการพัฒนาของตนเอง:**",
        "es": "**🍸 El acceso gratuito es solo la entrada al ecosistema. Adentro te espera profundidad, permitiéndote elegir tu camino de desarrollo:**",
        "ar": "**🍸 الوصول المجاني هو مجرد الدخول إلى النظام البيئي. في الداخل، ينتظرك عمق يسمح لك باختيار مسار تطورك:**",
        "uk": "**🍸 Безкоштовний доступ - це тільки вхід в екосистему. Всередині тебе чекає глибина, яка дозволить вибрати свій шлях розвитку:**"
    },
    
    "welcome_step_2": {
        "ru": "**🎯 ПРОФИ Инструменты и Индикаторы: Для тех, кто хочет самостоятельно принимать решения, используя наши проверенные ML-модели и авторский индикатор.**",
        "en": "**🎯 PRO Tools and Indicators: For those who want to make decisions independently using our proven ML models and proprietary indicator.**",
        "th": "**🎯 เครื่องมือและตัวบ่งชี้ PRO: สำหรับผู้ที่ต้องการตัดสินใจด้วยตนเองโดยใช้โมเดล ML ที่พิสูจน์แล้วและตัวบ่งชี้ที่เป็นกรรมสิทธิ์ของเรา**",
        "es": "**🎯 Herramientas e Indicadores PRO: Para quienes desean tomar decisiones de forma independiente utilizando nuestros modelos ML probados y nuestro indicador exclusivo.**",
        "ar": "**🎯 أدوات ومؤشرات PRO: لأولئك الذين يرغبون في اتخاذ القرارات بشكل مستقل باستخدام نماذج ML المثبتة لدينا ومؤشرنا الخاص.**",
        "uk": "**🎯 ПРОФІ Інструменти та Індикатори: Для тих, хто хочесамостійно приймати рішення, використовуючи наші перевірені ML-моделі і авторські індикатори.**",
    },
    
    "welcome_step_2_bonus": {
        "ru": "**⚡️ АЛГО Глубокий Анализ: Подключай передовые, специализированные ML-модели в веб-приложении для хирургической точности.**",
        "en": "**⚡️ ALGO Deep Analysis: Connect advanced, specialized ML models in the web app for surgical precision.**",
        "th": "**⚡️ ALGO การวิเคราะห์เชิงลึก: เชื่อมต่อโมเดล ML ขั้นสูงและเฉพาะทางในเว็บแอปเพื่อความแม่นยำระดับศัลยกรรม**",
        "es": "**⚡️ ALGO Análisis Profundo: Conecta modelos ML avanzados y especializados en la aplicación web para una precisión quirúrgica.**",
        "ar": "**⚡️ ALGO تحليل عميق: قم بتوصيل نماذج ML المتقدمة والمتخصصة في تطبيق الويب للحصول على دقة جراحية.**",
        "uk": "**⚡️ АЛГО Глибокий Аналіз: Підключай передові, спеціалізовані ML-моделі в веб-застосунку для хірургічної точності.**"
    },
    
    "welcome_step_2_promo": {
        "ru": "**👑 ЭЛИТА Прямой Доход: Самый высокий уровень - закрытый Discord с Live-торговлей. Здесь мы работаем с крупным капиталом, торгуем в прямом эфире и максимизируем прибыль, работая как единый фонд.**",
        "en": "**👑 ELITE Direct Income: The highest level - a closed Discord with Live trading. Here we work with large capital, trade live, and maximize profits working as a unified fund.**",
        "th": "**👑 ELITE รายได้โดยตรง: ระดับสูงสุด - Discord ปิดที่มีการเทรดสด ที่นี่เราทำงานกับเงินทุนขนาดใหญ่ เทรดสด และเพิ่มผลกำไรสูงสุดโดยทำงานเป็นกองทุนเดียว**",
        "es": "**👑 ELITE Ingreso Directo: El nivel más alto: un Discord cerrado con trading en vivo. Aquí trabajamos con gran capital, operamos en vivo y maximizamos las ganancias trabajando como un fondo unificado.**",
        "ar": "**👑 ELITE الدخل المباشر: أعلى مستوى - Discord مغلق مع تداول مباشر. هنا نعمل برأس مال كبير، نتداول مباشرة، ونعظم الأرباح بالعمل كصندوق موحد.**",
        "uk": "**👑 ЕЛІТА Прямий Дохід: Самий висодоий рівень - закритий Discord с Live-торгівлею. Тут ми працюємо с великим капіталом, торгуємо в прямому ефірі і максимізуємо прибуток, пряцюючи як єдиний фонд.**",
    },
    
    "registration_link_text": {
        "ru": "**РЕГИСТРАЦИЯ НА ПЛАТФОРМЕ**",
        "en": "**PLATFORM REGISTRATION**",
        "th": "**การลงทะเบียนบนแพลตฟอร์ม**",
        "es": "**REGISTRO EN LA PLATAFORMA**",
        "ar": "**التسجيل في المنصة**",
        "uk": "**РЕГИСТРАЦИЯ НА ПЛАТФОРМЕ**",
    },
    
    "welcome_step_3": {
        "ru": "",
        "en": "",
        "th": "",
        "es": "",
        "ar": "",
        "uk": "",
    },
    
    "welcome_step_4": {
        "ru": "**Мы не обещаем \"грааль\". Мы даем инструменты и комьюнити, чтобы ты стал профессионалом, чья прибыль растет со временем и дисциплиной.**",
        "en": "**We don't promise a 'grail'. We provide tools and community so you can become a professional whose profit grows with time and discipline.**",
        "th": "**เราไม่สัญญาว่าจะมี 'จอกศักดิ์สิทธิ์' เรามอบเครื่องมือและชุมชนเพื่อให้คุณกลายเป็นมืออาชีพที่มีผลกำไรเติบโตตามเวลาและวินัย**",
        "es": "**No prometemos un 'santo grial'. Brindamos herramientas y comunidad para que te conviertas en un profesional cuyas ganancias crecen con el tiempo y la disciplina.**",
        "ar": "**نحن لا نعد بـ 'الكأس المقدسة'. نحن نقدم الأدوات والمجتمع لتصبح محترفًا تنمو أرباحه بمرور الوقت والانضباط.**",
        "uk": "**Ми не обіцяємо \"грааль\". Ми даємо інструменти та ком'юніті, щоб ти став професіоналом, чия прибуток росте з часом та дисципліною.**"
    },
    
    "welcome_traders_only": {
        "ru": "**Готов сделать первый шаг к системному трейдингу?**",
        "en": "**Ready to take the first step towards systematic trading?**",
        "th": "**พร้อมที่จะก้าวแรกสู่การเทรดอย่างเป็นระบบหรือยัง?**",
        "es": "**¿Listo para dar el primer paso hacia el trading sistemático?**",
        "ar": "**هل أنت مستعد لاتخاذ الخطوة الأولى نحو التداول المنهجي؟**",
        "uk": "**Готовий зробити перший крок до системному трейдингу?**",
    },
    
    "welcome_support": {
        "ru": "**ЗАРЕГИСТРИРУЙСЯ СЕЙЧАС И НАЧНИ С БЕСПЛАТНОГО БОТА И ПРИЛОЖЕНИЯ. 👇**",
        "en": "**REGISTER NOW AND START WITH THE FREE BOT AND APP. 👇**",
        "th": "**ลงทะเบียนตอนนี้และเริ่มต้นด้วยบอทและแอปฟรี 👇**",
        "es": "**REGÍSTRATE AHORA Y COMIENZA CON EL BOT Y LA APP GRATUITOS. 👇**",
        "ar": "**سجل الآن وابدأ مع البوت والتطبيق المجانيين. 👇**",
        "uk": "**ЗАРЕЄСТРУЙТЕСЬ СЕЙЧАС ТА НАЧНІТЬ З БЕЗКОШТОВНОГО БОТУ ТА ЗАСТОСУНКУ. 👇**",
    },
    
    # Кнопки главного меню
    "btn_instruction": {
        "ru": "📝 Инструкция",
        "en": "📝 Instructions",
        "th": "📝 คำแนะนำ",
        "es": "📝 Instrucciones",
        "ar": "📝 التعليمات",
        "uk": "📝 Інструкція",
    },
    
    "btn_registration": {
        "ru": "🔗 Регистрация",
        "en": "🔗 Registration",
        "th": "🔗 ลงทะเบียน",
        "es": "🔗 Registro",
        "ar": "🔗 التسجيل",
        "uk": "🔗 Реєстрація",
    },
    
    "btn_check_access": {
        "ru": "✅ Проверить доступ",
        "en": "✅ Check access",
        "th": "✅ ตรวจสอบการเข้าถึง",
        "es": "✅ Verificar acceso",
        "ar": "✅ التحقق من الوصول",
        "uk": "✅ Перевірити доступ",
    },
    
    "btn_support": {
        "ru": "📞 Поддержка",
        "en": "📞 Support",
        "th": "📞 การสนับสนุน",
        "es": "📞 Soporte",
        "ar": "📞 الدعم",
        "uk": "📞 Підтримка",
    },
    
    "btn_channel": {
        "ru": "📢 Главный канал",
        "en": "📢 Main Channel",
        "th": "📢 ช่องหลัก",
        "es": "📢 Canal Principal",
        "ar": "📢 القناة الرئيسية",
        "uk": "📢 Головний канал",
    },
    
    "btn_indicator": {
        "ru": "📊 Индикатор",
        "en": "📊 Indicator",
        "th": "📊 ตัวบ่งชี้",
        "es": "📊 Indicador",
        "ar": "📊 المؤشر",
        "uk": "📊 Індикатор",
    },
    
    "btn_language": {
        "ru": "🌐 Язык / Language",
        "en": "🌐 Language / Язык",
        "th": "🌐 ภาษา / Language",
        "es": "🌐 Idioma / Language",
        "ar": "🌐 اللغة / Language",
        "uk": "🌐 Язик / Language",
    },
    
    "btn_back": {
        "ru": "🔙 Назад",
        "en": "🔙 Back",
        "th": "🔙 กลับ",
        "es": "🔙 Atrás",
        "ar": "🔙 رجوع",
        "uk": "🔙 Назад",
    },
    
    # Инструкция
    "instruction_title": {
        "ru": "📋 *ИНСТРУКЦИЯ*",
        "en": "📋 *INSTRUCTIONS*",
        "th": "📋 *คำแนะนำ*",
        "es": "📋 *INSTRUCCIONES*",
        "ar": "📋 *التعليمات*",
        "uk": "📋 *ІНСТРУКЦІЯ*",
    },
    
    "instruction_step1": {
        "ru": "Начните сейчас! Нажмите на кнопку ниже и пройдите быструю регистрацию на платформе:\n\n[РЕГИСТРАЦИЯ НА ПЛАТФОРМЕ]({link})",
        "en": "Start now! Click the button below and complete quick registration on the platform:\n\n[REGISTRATION ON PLATFORM]({link})",
        "th": "เริ่มเลย! คลิกปุ่มด้านล่างและลงทะเบียนบนแพลตฟอร์ม:\n\n[ลงทะเบียนบนแพลตฟอร์ม]({link})",
        "es": "¡Comienza ahora! Haz clic en el botón de abajo y completa el registro rápido en la plataforma:\n\n[REGISTRO EN LA PLATAFORMA]({link})",
        "ar": "ابدأ الآن! انقر على الزر أدناه وأكمل التسجيل السريع على المنصة:\n\n[التسجيل على المنصة]({link})",
        "uk": "Почніть зараз! Натисніть на кнопку нижче та пройдіть швидку реєстрацію на платформі:\n\n[РЕГИСТРАЦИЯ НА ПЛАТФОРМЕ]({link})",
    },
    
    "instruction_step2": {
        "ru": "Активируйте бонус! Пополните счет минимум на $50.",
        "en": "Activate the bonus! Deposit at least $50 to your account.",
        "th": "เปิดใช้งานโบนัส! ฝากเงินอย่างน้อย $50",
        "es": "¡Activa el bono! Deposita al menos $50 en tu cuenta.",
        "ar": "قم بتنشيط المكافأة! أودع ما لا يقل عن $50 في حسابك.",
        "uk": "Активуйте бонус! Поповніть рахунок мінимум на $50.",
    },
    
    "instruction_step3": {
        "ru": "Получите доступ! Отправьте мне ваш ID аккаунта PocketOption.",
        "en": "Get access! Send me your PocketOption account ID.",
        "th": "รับการเข้าถึง! ส่ง ID บัญชี PocketOption ของคุณมาให้ฉัน",
        "es": "¡Obtén acceso! Envíame tu ID de cuenta de PocketOption.",
        "ar": "احصل على الوصول! أرسل لي معرف حساب PocketOption الخاص بك.",
        "uk": "Отримайте доступ! Відправте мені ваш ID акаунта PocketOption.",
    },
    
    "instruction_step1_title": {
        "ru": "*ШАГ 1: Регистрация*",
        "en": "*STEP 1: Registration*",
        "th": "*ขั้นตอนที่ 1: การลงทะเบียน*",
        "es": "*PASO 1: Registro*",
        "ar": "*الخطوة 1: التسجيل*",
        "uk": "*ШАГ 1: Реєстрація*",
    },
    
    "instruction_step1_1": {
        "ru": "• Нажмите кнопку \"🔗 Регистрация\"",
        "en": "• Click the \"🔗 Registration\" button",
        "th": "• คลิกปุ่ม \"🔗 ลงทะเบียน\"",
        "es": "• Haga clic en el botón \"🔗 Registro\"",
        "ar": "• انقر على زر \"🔗 التسجيل\"",
        "uk": "• Натисніть кнопку \"🔗 Реєстрація\"",
    },
    
    "instruction_step1_2": {
        "ru": "• Зарегистрируйтесь на PocketOption",
        "en": "• Register on PocketOption",
        "th": "• ลงทะเบียนบน PocketOption",
        "es": "• Regístrese en PocketOption",
        "ar": "• سجل على PocketOption",
        "uk": "• Зареєструйтесь на PocketOption",
    },
    
    "instruction_step1_3": {
        "ru": "• Обязательно используйте нашу ссылку!",
        "en": "• Be sure to use our link!",
        "th": "• ตรวจสอบให้แน่ใจว่าใช้ลิงก์ของเรา!",
        "es": "• ¡Asegúrese de usar nuestro enlace!",
        "ar": "• تأكد من استخدام رابطنا!",
        "uk": "• Обовязково використовуйте нашу ссилку!",
    },
    
    "instruction_step2_title": {
        "ru": "*ШАГ 2: Пополнение*",
        "en": "*STEP 2: Deposit*",
        "th": "*ขั้นตอนที่ 2: การฝากเงิน*",
        "es": "*PASO 2: Depósito*",
        "ar": "*الخطوة 2: الإيداع*",
        "uk": "*ШАГ 2: Поповнення*",
    },
    
    "instruction_step2_1": {
        "ru": "• Пополните баланс минимум на $50",
        "en": "• Deposit at least $50",
        "th": "• ฝากเงินอย่างน้อย $50",
        "es": "• Deposite al menos $50",
        "ar": "• أودع ما لا يقل عن $50",
        "uk": "• Поповніть баланс мінимум на $50",
    },
    
    "instruction_step2_2": {
        "ru": "• Получите +50% бонус к депозиту",
        "en": "• Get +50% bonus on deposit",
        "th": "• รับโบนัส +50% จากการฝาก",
        "es": "• Obtenga +50% de bonificación",
        "ar": "• احصل على +50% مكافأة",
        "uk": "• Отримайте +50% бонус до депозиту",
    },
    
    "instruction_step2_3": {
        "ru": "• Промокод: 50START",
        "en": "• Promo code: 50START",
        "th": "• รหัสโปรโมชั่น: 50START",
        "es": "• Código promocional: 50START",
        "ar": "• رمز الترويج: 50START",
        "uk": "• Промокод: 50START",
    },
    
    "instruction_step3_title": {
        "ru": "*ШАГ 3: Отправка ID*",
        "en": "*STEP 3: Send ID*",
        "th": "*ขั้นตอนที่ 3: ส่ง ID*",
        "es": "*PASO 3: Enviar ID*",
        "ar": "*الخطوة 3: إرسال المعرف*",
        "uk": "*ШАГ 3: Відправка ID*",
    },
    
    "instruction_step3_1": {
        "ru": "• Скопируйте ваш ID аккаунта",
        "en": "• Copy your account ID",
        "th": "• คัดลอก ID บัญชีของคุณ",
        "es": "• Copie su ID de cuenta",
        "ar": "• انسخ معرف حسابك",
        "uk": "• Скопіюйте ваш ID акаунта",
    },
    
    "instruction_step3_2": {
        "ru": "• Отправьте его боту в сообщении",
        "en": "• Send it to the bot in a message",
        "th": "• ส่งไปยังบอทในข้อความ",
        "es": "• Envíelo al bot en un mensaje",
        "ar": "• أرسله للبوت في رسالة",
        "uk": "• Відправте його боту в повідомленні",
    },
    
    "instruction_step3_3": {
        "ru": "• Формат: 37525432 (только цифры)",
        "en": "• Format: 37525432 (numbers only)",
        "th": "• รูปแบบ: 37525432 (ตัวเลขเท่านั้น)",
        "es": "• Formato: 37525432 (solo números)",
        "ar": "• التنسيق: 37525432 (أرقام فقط)",
        "uk": "• Формат: 37525432 (тільки цифри)",
    },
    
    "instruction_step4_title": {
        "ru": "*ШАГ 4: Проверка*",
        "en": "*STEP 4: Verification*",
        "th": "*ขั้นตอนที่ 4: การตรวจสอบ*",
        "es": "*PASO 4: Verificación*",
        "ar": "*الخطوة 4: التحقق*",
        "uk": "ШАГ 4: Перевірка*",
    },
    
    "instruction_step4_1": {
        "ru": "• Мы проверим вашу регистрацию",
        "en": "• We'll verify your registration",
        "th": "• เราจะตรวจสอบการลงทะเบียนของคุณ",
        "es": "• Verificaremos su registro",
        "ar": "• سنتحقق من تسجيلك",
        "uk": "• Ми перевіримо вашу реєстрацію",
    },
    
    "instruction_step4_2": {
        "ru": "• Подтвердим пополнение",
        "en": "• Confirm deposit",
        "th": "• ยืนยันการฝากเงิน",
        "es": "• Confirmar depósito",
        "ar": "• تأكيد الإيداع",
        "uk": "• Підтвердимо поповнення",
    },
    
    "instruction_step4_3": {
        "ru": "• Предоставим доступ к сигналам",
        "en": "• Grant access to signals",
        "th": "• ให้สิทธิ์เข้าถึงสัญญาณ",
        "es": "• Otorgar acceso a señales",
        "ar": "• منح الوصول إلى الإشارات",
        "uk": "• Надаємо доступ до сигналів",
    },
    
    "instruction_time": {
        "ru": "⏰ *Время обработки:* до 24 часов",
        "en": "⏰ *Processing time:* up to 24 hours",
        "th": "⏰ *เวลาในการประมวลผล:* สูงสุด 24 ชั่วโมง",
        "es": "⏰ *Tiempo de procesamiento:* hasta 24 horas",
        "ar": "⏰ *وقت المعالجة:* حتى 24 ساعة",
        "uk": "⏰ *Время опряцювання:* до 24 годин",
    },
    
    "instruction_questions": {
        "ru": "❓ *Вопросы?* Пишите @kaktotakxm",
        "en": "❓ *Questions?* Write @kaktotakxm",
        "th": "❓ *คำถาม?* เขียน @kaktotakxm",
        "es": "❓ *¿Preguntas?* Escriba @kaktotakxm",
        "ar": "❓ *أسئلة؟* اكتب @kaktotakxm",
        "uk": "❓ *Питання?* Пишіть @kaktotakxm",
    },
    
    # Проверка доступа
    "access_status_title": {
        "ru": "📊 *ВАШ СТАТУС:*",
        "en": "📊 *YOUR STATUS:*",
        "th": "📊 *สถานะของคุณ:*",
        "es": "📊 *SU ESTADO:*",
        "ar": "📊 *حالتك:*",
        "uk": "📊 *ВАШ СТАТУС:*",
    },
    
    "access_user": {
        "ru": "👤 *Пользователь:* {}",
        "en": "👤 *User:* {}",
        "th": "👤 *ผู้ใช้:* {}",
        "es": "👤 *Usuario:* {}",
        "ar": "👤 *المستخدم:* {}",
        "uk": "👤 *Пользователь:* {}",
    },
    
    "access_registration": {
        "ru": "📅 *Регистрация:* {}",
        "en": "📅 *Registration:* {}",
        "th": "📅 *การลงทะเบียน:* {}",
        "es": "📅 *Registro:* {}",
        "ar": "📅 *التسجيل:* {}",
        "uk": "📅 *Реєстрація:* {}",
    },
    
    "access_referral_link": {
        "ru": "🔗 *Реферальная ссылка:* {}",
        "en": "🔗 *Referral link:* {}",
        "th": "🔗 *ลิงก์อ้างอิง:* {}",
        "es": "🔗 *Enlace de referencia:* {}",
        "ar": "🔗 *رابط الإحالة:* {}",
        "uk": "🔗 *Реферальна посилання:* {}",
    },
    
    "access_referral_used": {
        "ru": "✅ Использована",
        "en": "✅ Used",
        "th": "✅ ใช้แล้ว",
        "es": "✅ Usado",
        "ar": "✅ مستخدم",
        "uk": "✅ Використана",
    },
    
    "access_referral_not_used": {
        "ru": "❌ Не использована",
        "en": "❌ Not used",
        "th": "❌ ยังไม่ได้ใช้",
        "es": "❌ No usado",
        "ar": "❌ غير مستخدم",
        "uk": "❌ Не використана",
    },
    
    "access_deposit": {
        "ru": "💰 *Пополнение:* {}",
        "en": "💰 *Deposit:* {}",
        "th": "💰 *การฝากเงิน:* {}",
        "es": "💰 *Depósito:* {}",
        "ar": "💰 *الإيداع:* {}",
        "uk": "💰 *Поповнення:* {}",
    },
    
    "access_deposit_confirmed": {
        "ru": "✅ Подтверждено",
        "en": "✅ Confirmed",
        "th": "✅ ยืนยันแล้ว",
        "es": "✅ Confirmado",
        "ar": "✅ مؤكد",
        "uk": "✅ Підтверджено",
    },
    
    "access_deposit_not_confirmed": {
        "ru": "❌ Не подтверждено",
        "en": "❌ Not confirmed",
        "th": "❌ ยังไม่ได้ยืนยัน",
        "es": "❌ No confirmado",
        "ar": "❌ غير مؤكد",
        "uk": "❌ Не підтверджено",
    },
    
    "access_account_id": {
        "ru": "🆔 *ID аккаунта:* {}",
        "en": "🆔 *Account ID:* {}",
        "th": "🆔 *ID บัญชี:* {}",
        "es": "🆔 *ID de cuenta:* {}",
        "ar": "🆔 *معرف الحساب:* {}",
        "uk": "🆔 *ID акаунта:* {}",
    },
    
    "access_id_not_sent": {
        "ru": "Не отправлен",
        "en": "Not sent",
        "th": "ยังไม่ได้ส่ง",
        "es": "No enviado",
        "ar": "لم يتم الإرسال",
        "uk": "Не відправлений",
    },
    
    "access_status": {
        "ru": "✅ *Доступ:* {}",
        "en": "✅ *Access:* {}",
        "th": "✅ *การเข้าถึง:* {}",
        "es": "✅ *Acceso:* {}",
        "ar": "✅ *الوصول:* {}",
        "uk": "✅ *Доступ:* {}",
    },
    
    "access_active": {
        "ru": "Активен",
        "en": "Active",
        "th": "ใช้งานอยู่",
        "es": "Activo",
        "ar": "نشط",
        "uk": "Активний",
    },
    
    "access_not_granted": {
        "ru": "Не предоставлен",
        "en": "Not granted",
        "th": "ไม่ได้รับอนุญาต",
        "es": "No otorgado",
        "ar": "غير ممنوح",
        "uk": "Не наданний",
    },
    
    "access_granted_message": {
        "ru": "\n\n🎉 *ДОСТУП ПРЕДОСТАВЛЕН!*\nВы получаете все торговые сигналы!",
        "en": "\n\n🎉 *ACCESS GRANTED!*\nYou're receiving all trading signals!",
        "th": "\n\n🎉 *ได้รับอนุญาต!*\nคุณกำลังได้รับสัญญาณการซื้อขายทั้งหมด!",
        "es": "\n\n🎉 *¡ACCESO OTORGADO!*\n¡Está recibiendo todas las señales de trading!",
        "ar": "\n\n🎉 *تم منح الوصول!*\nأنت تتلقى جميع إشارات التداول!",
        "uk": "\n\n🎉 *ДОСТУП НАДАНО!*\nВи отримуєте всі торгові сигнали!",
    },
    
    "signal_bot_access_message": {
        "ru": "🤖 *Ваш персональный бот сигналов готов!*\n\nНажмите кнопку ниже, чтобы получить доступ к боту с торговыми сигналами и веб-приложением:",
        "en": "🤖 *Your personal signal bot is ready!*\n\nClick the button below to access the trading signals bot and web app:",
        "th": "🤖 *บอทสัญญาณส่วนตัวของคุณพร้อมแล้ว!*\n\nคลิกปุ่มด้านล่างเพื่อเข้าถึงบอทสัญญาณการซื้อขายและเว็บแอป:",
        "es": "🤖 *¡Tu bot de señales personal está listo!*\n\nHaz clic en el botón de abajo para acceder al bot de señales y la aplicación web:",
        "ar": "🤖 *بوت الإشارات الشخصي جاهز!*\n\nانقر على الزر أدناه للوصول إلى بوت إشارات التداول وتطبيق الويب:",
        "uk": "🤖 *Ваш персональний бот сигналів готовий!*\n\nНатисніть кнопку ниже, щобы отримати доступ к боту с торговыми сигналами и веб-приложением:",
    },
    
    "access_not_granted_message": {
        "ru": "\n\n⚠️ *ДОСТУП НЕ ПРЕДОСТАВЛЕН*\n\nВыполните все шаги:\n1. Регистрация по ссылке\n2. Пополнение $50+\n3. Отправка ID аккаунта",
        "en": "\n\n⚠️ *ACCESS NOT GRANTED*\n\nComplete all steps:\n1. Register via link\n2. Deposit $50+\n3. Send account ID",
        "th": "\n\n⚠️ *ไม่ได้รับอนุญาต*\n\nทำตามขั้นตอนทั้งหมด:\n1. ลงทะเบียนผ่านลิงก์\n2. ฝากเงิน $50+\n3. ส่ง ID บัญชี",
        "es": "\n\n⚠️ *ACCESO NO OTORGADO*\n\nComplete todos los pasos:\n1. Registrarse vía enlace\n2. Depositar $50+\n3. Enviar ID de cuenta",
        "ar": "\n\n⚠️ *لم يتم منح الوصول*\n\nأكمل جميع الخطوات:\n1. التسجيل عبر الرابط\n2. إيداع $50+\n3. إرسال معرف الحساب",
        "uk": "\n\n⚠️ *ДОСТУП НЕ НАДАНО*\n\nВиконайте всі кроки:\n1. Реєстрація за посиланням\n2. Поповнення $50+\n3. Відправка ID акаунта",
    },
    
    "access_checks_info": {
        "ru": "\n\n🔄 *Проверок сегодня:* {}\n💡 Выполните действия вместо повторных проверок!",
        "en": "\n\n🔄 *Checks today:* {}\n💡 Take action instead of repeated checks!",
        "th": "\n\n🔄 *การตรวจสอบวันนี้:* {}\n💡 ดำเนินการแทนการตรวจสอบซ้ำ!",
        "es": "\n\n🔄 *Verificaciones hoy:* {}\n💡 ¡Actúe en lugar de verificaciones repetidas!",
        "ar": "\n\n🔄 *عمليات التحقق اليوم:* {}\n💡 اتخذ إجراء بدلاً من الفحوصات المتكررة!",
        "uk": "\n\n🔄 *Перевірок сьогодні:* {}\n💡 Виконайте дії замість повторних перевірок!",
    },
    
    # Предупреждения
    "warning_first_title": {
        "ru": "⚠️ *ПЕРВОЕ ПРЕДУПРЕЖДЕНИЕ!*",
        "en": "⚠️ *FIRST WARNING!*",
        "th": "⚠️ *คำเตือนครั้งแรก!*",
        "es": "⚠️ *¡PRIMERA ADVERTENCIA!*",
        "ar": "⚠️ *تحذير أول!*",
        "uk": "⚠️ *ПЕРВОЕ ПРЕДУПРЕЖДЕНИЕ!*",
    },
    
    "warning_last_title": {
        "ru": "🚨 *ПОСЛЕДНЕЕ ПРЕДУПРЕЖДЕНИЕ!*",
        "en": "🚨 *FINAL WARNING!*",
        "th": "🚨 *คำเตือนสุดท้าย!*",
        "es": "🚨 *¡ADVERTENCIA FINAL!*",
        "ar": "🚨 *تحذير نهائي!*",
        "uk": "🚨 *ПОСЛЕДНЕЕ ПРЕДУПРЕЖДЕНИЕ!*",
    },
    
    "warning_checks_count": {
        "ru": "Вы проверяете доступ уже {} раз подряд!",
        "en": "You've checked access {} times in a row!",
        "th": "คุณตรวจสอบการเข้าถึงแล้ว {} ครั้งติดต่อกัน!",
        "es": "¡Ha verificado el acceso {} veces seguidas!",
        "ar": "لقد تحققت من الوصول {} مرة متتالية!",
        "uk": "Ви перевіряєте доступ вже {} раз підряд!",
    },
    
    "warning_block_threat": {
        "ru": "Следующее нарушение приведет к **ПОСТОЯННОЙ БЛОКИРОВКЕ НАВСЕГДА**!",
        "en": "Next violation will result in **PERMANENT BAN FOREVER**!",
        "th": "การละเมิดครั้งต่อไปจะทำให้ **ถูกแบนถาวรตลอดไป**!",
        "es": "¡La próxima violación resultará en **PROHIBICIÓN PERMANENTE PARA SIEMPRE**!",
        "ar": "الانتهاك التالي سيؤدي إلى **حظر دائم للأبد**!",
        "uk": "Следующее нарушение приведет к **ПОСТОЯННОЙ БЛОКИРОВКЕ НАВСЕГДА**!",
    },
    
    "warning_status_wont_change": {
        "ru": "🚫 *Статус не изменится автоматически!*",
        "en": "🚫 *Status won't change automatically!*",
        "th": "🚫 *สถานะจะไม่เปลี่ยนแปลงโดยอัตโนมัติ!*",
        "es": "🚫 *¡El estado no cambiará automáticamente!*",
        "ar": "🚫 *لن تتغير الحالة تلقائيًا!*",
        "uk": "🚫 *Статус не изменится автоматически!*",
    },
    
    "warning_steps_required": {
        "ru": "📋 *Для получения доступа выполните:*\n1️⃣ Регистрация по нашей ссылке\n2️⃣ Пополнение баланса ${}+\n3️⃣ Отправка ID аккаунта",
        "en": "📋 *To get access, complete:*\n1️⃣ Register via our link\n2️⃣ Deposit ${}+\n3️⃣ Send account ID",
        "th": "📋 *เพื่อเข้าถึง ให้ทำให้เสร็จ:*\n1️⃣ ลงทะเบียนผ่านลิงก์ของเรา\n2️⃣ ฝากเงิน ${}+\n3️⃣ ส่ง ID บัญชี",
        "es": "📋 *Para obtener acceso, complete:*\n1️⃣ Regístrese vía nuestro enlace\n2️⃣ Deposite ${}+\n3️⃣ Envíe ID de cuenta",
        "ar": "📋 *للحصول على الوصول، أكمل:*\n1️⃣ سجل عبر رابطنا\n2️⃣ أودع ${}+\n3️⃣ أرسل معرف الحساب",
        "uk": "📋 *Для отримання доступа виконайте:*\n1️⃣ Реєстрація по нашей ссылке\n2️⃣ Поповнення балансу ${}+\n3️⃣ Отправка ID акаунта",
    },
    
    "warning_cooldown": {
        "ru": "⏰ *Следующая проверка доступна через:* {} мин.",
        "en": "⏰ *Next check available in:* {} min.",
        "th": "⏰ *การตรวจสอบครั้งต่อไปพร้อมใช้งานใน:* {} นาที",
        "es": "⏰ *Próxima verificación disponible en:* {} min.",
        "ar": "⏰ *الفحص التالي متاح في:* {} دقيقة.",
        "uk": "⏰ *Следующая перевірка доступна через:* {} хв.",
    },
    
    "warning_advice": {
        "ru": "💡 *Совет:* Вместо повторных проверок выполните необходимые действия!",
        "en": "💡 *Advice:* Instead of repeated checks, complete the required actions!",
        "th": "💡 *คำแนะนำ:* แทนที่จะตรวจสอบซ้ำ ให้ทำการกระทำที่จำเป็น!",
        "es": "💡 *Consejo:* ¡En lugar de verificaciones repetidas, complete las acciones requeridas!",
        "ar": "💡 *نصيحة:* بدلاً من الفحوصات المتكررة، أكمل الإجراءات المطلوبة!",
        "uk": "💡 *Порада:* Замість повторних перевірок виконайте необхідні дії!",
    },
    
    # Блокировка
    "blocked_title": {
        "ru": "🚫 *ВАША УЧЕТНАЯ ЗАПИСЬ ЗАБЛОКИРОВАНА*",
        "en": "🚫 *YOUR ACCOUNT IS BLOCKED*",
        "th": "🚫 *บัญชีของคุณถูกบล็อก*",
        "es": "🚫 *SU CUENTA ESTÁ BLOQUEADA*",
        "ar": "🚫 *حسابك محظور*",
        "uk": "🚫 *ВАША УЧЕТНАЯ ЗАПИСЬ ЗАБЛОКИРОВАНА*",
    },
    
    "blocked_reason": {
        "ru": "❌ *Причина:* Многократные нарушения правил использования",
        "en": "❌ *Reason:* Multiple violations of usage rules",
        "th": "❌ *เหตุผล:* การละเมิดกฎการใช้งานหลายครั้ง",
        "es": "❌ *Razón:* Múltiples violaciones de las reglas de uso",
        "ar": "❌ *السبب:* انتهاكات متعددة لقواعد الاستخدام",
        "uk": "❌ *Причина:* Многократные нарушения правил использования",
    },
    
    "blocked_permanent": {
        "ru": "⚠️ *Блокировка действует навсегда*",
        "en": "⚠️ *Ban is permanent*",
        "th": "⚠️ *การแบนเป็นการถาวร*",
        "es": "⚠️ *La prohibición es permanente*",
        "ar": "⚠️ *الحظر دائم*",
        "uk": "⚠️ *Блокування действует навсігда*",
    },
    
    "blocked_contact": {
        "ru": "📞 *Для разблокировки обратитесь:* @kaktotakxm",
        "en": "📞 *To unblock, contact:* @kaktotakxm",
        "th": "📞 *เพื่อปลดบล็อก ติดต่อ:* @kaktotakxm",
        "es": "📞 *Para desbloquear, contacte:* @kaktotakxm",
        "ar": "📞 *لإلغاء الحظر، اتصل بـ:* @kaktotakxm",
        "uk": "📞 *Для разблокировки обратитесь:* @kaktotakxm",
    },
    
    "blocked_user_id": {
        "ru": "💬 *Укажите ваш ID:* {}",
        "en": "💬 *Provide your ID:* {}",
        "th": "💬 *ระบุ ID ของคุณ:* {}",
        "es": "💬 *Proporcione su ID:* {}",
        "ar": "💬 *قدم معرفك:* {}",
        "uk": "💬 *Вкажіть ваш ID:* {}",
    },
    
    # ID аккаунта
    "id_received_title": {
        "ru": "✅ *ID получен:* {}",
        "en": "✅ *ID received:* {}",
        "th": "✅ *ได้รับ ID แล้ว:* {}",
        "es": "✅ *ID recibido:* {}",
        "ar": "✅ *تم استلام المعرف:* {}",
        "uk": "✅ *ID получен:* {}",
    },
    
    "id_checking": {
        "ru": "🔍 *Проверяем ваши данные...*",
        "en": "🔍 *Checking your data...*",
        "th": "🔍 *กำลังตรวจสอบข้อมูลของคุณ...*",
        "es": "🔍 *Verificando sus datos...*",
        "ar": "🔍 *جاري التحقق من بياناتك...*",
        "uk": "🔍 *Перевіряємо ваши дані...*",
    },
    
    "id_processing_time": {
        "ru": "⏰ *Время обработки:* до 24 часов",
        "en": "⏰ *Processing time:* up to 24 hours",
        "th": "⏰ *เวลาในการประมวลผล:* สูงสุด 24 ชั่วโมง",
        "es": "⏰ *Tiempo de procesamiento:* hasta 24 horas",
        "ar": "⏰ *وقت المعالجة:* حتى 24 ساعة",
        "uk": "⏰ *Время обработки:* до 24 годин",
    },
    
    "id_what_checked": {
        "ru": "📋 *Что проверяется:*\n• Регистрация по нашей ссылке\n• Пополнение баланса\n• Активность аккаунта",
        "en": "📋 *What's being checked:*\n• Registration via our link\n• Balance deposit\n• Account activity",
        "th": "📋 *สิ่งที่กำลังตรวจสอบ:*\n• การลงทะเบียนผ่านลิงก์ของเรา\n• การฝากเงิน\n• กิจกรรมบัญชี",
        "es": "📋 *Lo que se está verificando:*\n• Registro vía nuestro enlace\n• Depósito de saldo\n• Actividad de cuenta",
        "ar": "📋 *ما يتم التحقق منه:*\n• التسجيل عبر رابطنا\n• إيداع الرصيد\n• نشاط الحساب",
        "uk": "📋 *Що перевіряється:*\n• Реєстрація за нашою посиланням\n• Поповнення балансу\n• Активність акаунта",
    },
    
    "id_after_verification": {
        "ru": "✅ *После проверки вы получите доступ к сигналам!*",
        "en": "✅ *After verification you'll get access to signals!*",
        "th": "✅ *หลังจากการตรวจสอบคุณจะได้รับการเข้าถึงสัญญาณ!*",
        "es": "✅ *¡Después de la verificación obtendrá acceso a las señales!*",
        "ar": "✅ *بعد التحقق ستحصل على الوصول إلى الإشارات!*",
        "uk": "✅ *Після перевірки ви отримайте доступ до сигналів!*",
    },
    
    "id_questions": {
        "ru": "📞 *Вопросы?* @kaktotakxm",
        "en": "📞 *Questions?* @kaktotakxm",
        "th": "📞 *คำถาม?* @kaktotakxm",
        "es": "📞 *¿Preguntas?* @kaktotakxm",
        "ar": "📞 *أسئلة؟* @kaktotakxm",
        "uk": "📞 *Питання?* @kaktotakxm",
    },
    
    # Ошибки
    "error_not_registered": {
        "ru": "❌ Вы не зарегистрированы в системе!\n\nИспользуйте /start для начала.",
        "en": "❌ You're not registered in the system!\n\nUse /start to begin.",
        "th": "❌ คุณไม่ได้ลงทะเบียนในระบบ!\n\nใช้ /start เพื่อเริ่มต้น",
        "es": "❌ ¡No está registrado en el sistema!\n\nUse /start para comenzar.",
        "ar": "❌ أنت غير مسجل في النظام!\n\nاستخدم /start للبدء.",
        "uk": "❌ Вы не зарегистрированы в системе!\n\nВикористовуйте /start для начала.",
    },
    
    "error_use_start": {
        "ru": "❌ Сначала используйте команду /start",
        "en": "❌ First use the /start command",
        "th": "❌ ใช้คำสั่ง /start ก่อน",
        "es": "❌ Primero use el comando /start",
        "ar": "❌ استخدم أمر /start أولاً",
        "uk": "❌ Спочатку використовуйте команду /start",
    },
    
    "error_unknown_message": {
        "ru": "❓ *Не понимаю ваше сообщение*\n\n📋 *Доступные команды:*\n• /start - Начать работу с ботом\n• /help - Помощь\n• /status - Проверить статус\n• /language - Выбор языка\n\n🆔 *Для отправки ID:* напишите ваш ID аккаунта\nПримеры: 37525432 или PO37525432\n\n📞 *Поддержка:* @kaktotakxm",
        "en": "❓ *I don't understand your message*\n\n📋 *Available commands:*\n• /start - Start working with the bot\n• /help - Help\n• /status - Check status\n• /language - Choose language\n\n🆔 *To send ID:* write your account ID\nExamples: 37525432 or PO37525432\n\n📞 *Support:* @kaktotakxm",
        "th": "❓ *ฉันไม่เข้าใจข้อความของคุณ*\n\n📋 *คำสั่งที่พร้อมใช้งาน:*\n• /start - เริ่มทำงานกับบอท\n• /help - ความช่วยเหลือ\n• /status - ตรวจสอบสถานะ\n• /language - เลือกภาษา\n\n🆔 *เพื่อส่ง ID:* เขียน ID บัญชีของคุณ\nตัวอย่าง: 37525432 หรือ PO37525432\n\n📞 *การสนับสนุน:* @kaktotakxm",
        "es": "❓ *No entiendo su mensaje*\n\n📋 *Comandos disponibles:*\n• /start - Comenzar a trabajar con el bot\n• /help - Ayuda\n• /status - Verificar estado\n• /language - Elegir idioma\n\n🆔 *Para enviar ID:* escriba su ID de cuenta\nEjemplos: 37525432 o PO37525432\n\n📞 *Soporte:* @kaktotakxm",
        "ar": "❓ *لا أفهم رسالتك*\n\n📋 *الأوامر المتاحة:*\n• /start - ابدأ العمل مع البوت\n• /help - المساعدة\n• /status - التحقق من الحالة\n• /language - اختر اللغة\n\n🆔 *لإرسال المعرف:* اكتب معرف حسابك\nأمثلة: 37525432 أو PO37525432\n\n📞 *الدعم:* @kaktotakxm",
        "uk": "❓ *Не розумію ваше повідомлення*\n\n📋 *Доступные команды:*\n• /start - Начать работу с ботом\n• /help - Допомога\n• /status - Перевірити статус\n• /language - Выбор языка\n\n🆔 *Для отправки ID:* напишіть ваш ID акаунта\nПримеры: 37525432 або PO37525432\n\n📞 *Поддержка:* @kaktotakxm",
    },
    
    # Команда /help
    "help_title": {
        "ru": "🆘 *ПОМОЩЬ*",
        "en": "🆘 *HELP*",
        "th": "🆘 *ความช่วยเหลือ*",
        "es": "🆘 *AYUDA*",
        "ar": "🆘 *المساعدة*",
        "uk": "🆘 *ДОПОМОГА*",
    },
    
    "help_commands": {
        "ru": "📋 *Доступные команды:*\n• /start - Начать работу с ботом\n• /help - Эта справка\n• /status - Проверить ваш статус\n• /language - Выбрать язык",
        "en": "📋 *Available commands:*\n• /start - Start working with bot\n• /help - This help\n• /status - Check your status\n• /language - Choose language",
        "th": "📋 *คำสั่งที่พร้อมใช้งาน:*\n• /start - เริ่มทำงานกับบอท\n• /help - ความช่วยเหลือนี้\n• /status - ตรวจสอบสถานะของคุณ\n• /language - เลือกภาษา",
        "es": "📋 *Comandos disponibles:*\n• /start - Comenzar a trabajar con bot\n• /help - Esta ayuda\n• /status - Verificar su estado\n• /language - Elegir idioma",
        "ar": "📋 *الأوامر المتاحة:*\n• /start - ابدأ العمل مع البوت\n• /help - هذه المساعدة\n• /status - تحقق من حالتك\n• /language - اختر اللغة",
        "uk": "📋 *Доступные команды:*\n• /start - Начать работу с ботом\n• /help - Эта справка\n• /status - Перевірити ваш статус\n• /language - Выбрать язык",
    },
    
    "help_send_id": {
        "ru": "🆔 *Как отправить ID аккаунта:*\nНапишите: PO + ваш ID\nПример: PO123456789",
        "en": "🆔 *How to send account ID:*\nWrite: PO + your ID\nExample: PO123456789",
        "th": "🆔 *วิธีส่ง ID บัญชี:*\nเขียน: PO + ID ของคุณ\nตัวอย่าง: PO123456789",
        "es": "🆔 *Cómo enviar ID de cuenta:*\nEscriba: PO + su ID\nEjemplo: PO123456789",
        "ar": "🆔 *كيفية إرسال معرف الحساب:*\nاكتب: PO + معرفك\nمثال: PO123456789",
        "uk": "🆔 *Як відправити ID акаунта:*\nНапишіть: PO + ваш ID\nПриклад: PO123456789",
    },
    
    "help_min_deposit": {
        "ru": "💰 *Минимальный депозит:* ${}",
        "en": "💰 *Minimum deposit:* ${}",
        "th": "💰 *การฝากเงินขั้นต่ำ:* ${}",
        "es": "💰 *Depósito mínimo:* ${}",
        "ar": "💰 *الحد الأدنى للإيداع:* ${}",
        "uk": "💰 *Хвимальный депозит:* ${}",
    },
    
    "help_response_time": {
        "ru": "⏰ *Время ответа:* до 24 часов",
        "en": "⏰ *Response time:* up to 24 hours",
        "th": "⏰ *เวลาตอบกลับ:* สูงสุด 24 ชั่วโมง",
        "es": "⏰ *Tiempo de respuesta:* hasta 24 horas",
        "ar": "⏰ *وقت الاستجابة:* حتى 24 ساعة",
        "uk": "⏰ *Часм відповіді:* до 24 годин",
    },
    
    # Команда /status
    "status_title": {
        "ru": "📊 *ВАШ СТАТУС:*",
        "en": "📊 *YOUR STATUS:*",
        "th": "📊 *สถานะของคุณ:*",
        "es": "📊 *SU ESTADO:*",
        "ar": "📊 *حالتك:*",
        "uk": "📊 *ВАШ СТАТУС:*",
    },
    
    "status_not_verified": {
        "ru": "\n\n⚠️ *Для получения доступа:*\n1. Регистрация по ссылке\n2. Пополнение ${}+\n3. Отправка ID аккаунта",
        "en": "\n\n⚠️ *To get access:*\n1. Register via link\n2. Deposit ${}+\n3. Send account ID",
        "th": "\n\n⚠️ *เพื่อเข้าถึง:*\n1. ลงทะเบียนผ่านลิงก์\n2. ฝากเงิน ${}+\n3. ส่ง ID บัญชี",
        "es": "\n\n⚠️ *Para obtener acceso:*\n1. Registrarse vía enlace\n2. Depositar ${}+\n3. Enviar ID de cuenta",
        "ar": "\n\n⚠️ *للحصول على الوصول:*\n1. التسجيل عبر الرابط\n2. إيداع ${}+\n3. إرسال معرف الحساب",
        "uk": "\n\n⚠️ *Для отримання доступу:*\n1. Реєстрація за посиланням\n2. Поповнення ${}+\n3. Відправка ID акаунта",
    },
    
    # Команда /language
    "language_select": {
        "ru": "🌐 *Выберите язык / Choose language*\n\nВыберите предпочитаемый язык интерфейса:",
        "en": "🌐 *Choose language / Выберите язык*\n\nSelect your preferred interface language:",
        "th": "🌐 *เลือกภาษา / Choose language*\n\nเลือกภาษาที่คุณต้องการ:",
        "es": "🌐 *Elegir idioma / Choose language*\n\nSeleccione su idioma preferido:",
        "ar": "🌐 *اختر اللغة / Choose language*\n\nحدد لغتك المفضلة:",
        "uk": "🌐 *Оберіть язык / Choose language*\n\nОберіть предпочитаемый язык интерфейса:",
    },
    
    "language_changed": {
        "ru": "✅ Язык изменен на Русский",
        "en": "✅ Language changed to English",
        "th": "✅ เปลี่ยนภาษาเป็น ไทย แล้ว",
        "es": "✅ Idioma cambiado a Español",
        "ar": "✅ تم تغيير اللغة إلى العربية",
        "uk": "✅ Язик змінено на Український",
    },
    
    # ============================================
    # НОВЫЕ ТЕКСТЫ: Главное меню
    # ============================================
    
    "btn_trader_menu": {
        "ru": "📼 Меню трейдера",
        "en": "📼 Trader Menu",
        "th": "📼 เมนูเทรดเดอร์",
        "es": "📼 Menú del Trader",
        "ar": "📼 قائمة المتداول",
        "uk": "📼 Меню трейдера",
    },
    
    "btn_get_free_access": {
        "ru": "🆓 Получить бесплатный доступ",
        "en": "🆓 Get Free Access",
        "th": "🆓 รับการเข้าถึงฟรี",
        "es": "🆓 Obtener Acceso Gratis",
        "ar": "🆓 احصل على وصول مجاني",
        "uk": "🆓 Отримати безкоштовний доступ",
    },
    
    "btn_invite_friend": {
        "ru": "👥 Пригласить друга",
        "en": "👥 Invite a Friend",
        "th": "👥 เชิญเพื่อน",
        "es": "👥 Invitar a un Amigo",
        "ar": "👥 دعوة صديق",
        "uk": "👥 Пригласити друга",
    },
    
    "btn_healthy_trader": {
        "ru": "🌿 Здравое Движение (Бонусы)",
        "en": "🌿 Healthy Movement (Bonuses)",
        "th": "🌿 การเคลื่อนไหวที่ดีต่อสุขภาพ (โบนัส)",
        "es": "🌿 Movimiento Saludable (Bonos)",
        "ar": "🌿 الحركة الصحية (مكافآت)",
        "uk": "🌿 Здоровий Рух (Бонуси)",
    },
    
    "healthy_trader_title": {
        "ru": "🌿 *ЗДРАВОЕ ДВИЖЕНИЕ (БОНУСЫ)*",
        "en": "🌿 *HEALTHY MOVEMENT (BONUSES)*",
        "th": "🌿 *การเคลื่อนไหวที่ดีต่อสุขภาพ (โบนัส)*",
        "es": "🌿 *MOVIMIENTO SALUDABLE (BONOS)*",
        "ar": "🌿 *الحركة الصحية (مكافآت)*",
        "uk": "🌿 *ЗДОРОВИЙ РУХ (БОНУСИ)*",
    },
    
    "healthy_trader_description": {
        "ru": """**🎯 Пригласи друга — развивайтесь и обучайтесь вместе!**

**Приводи друзей в нашу команду и получай за это реальные бонусы!**

**Вместе учиться трейдингу интереснее и эффективнее. А мы поощряем тех, кто помогает расти нашему сообществу честных трейдеров.**

**✅ Условия участия:**
**• Для участия в программе достаточно быть подписанным на канал**

**🏆 Твои бонусы:**
**• 2 друга → Неделя подписки на индикатор**
**• 5 друзей → Месяц подписки**
**• 10 друзей → 🔥 Софт + Менторство!**

**💡 Важно:**
**Раздел с активным бонусом появится автоматически при достижении определённого прогресса. Просто приглашай друзей и следи за своим прогрессом!**

**💡 Развивайтесь вместе — зарабатывайте вместе!**""",
        "en": """**🎯 Invite a friend — learn and grow together!**

**Bring friends to our team and get real bonuses!**

**Learning trading together is more fun and effective. We reward those who help grow our community of honest traders.**

**✅ Participation conditions:**
**• To participate in the program, just subscribe to the channel**

**🏆 Your bonuses:**
**• 2 friends → 1 week subscription**
**• 5 friends → 1 month subscription**
**• 10 friends → 🔥 Software + Mentorship!**

**💡 Important:**
**The active bonus section will appear automatically when you reach certain progress. Just invite friends and track your progress!**

**💡 Grow together — earn together!**""",
        "th": """**🎯 เชิญเพื่อน — เรียนรู้และเติบโตด้วยกัน!**

**พาเพื่อนมาร่วมทีมและรับโบนัสจริง!**

**เรียนรู้การเทรดด้วยกันสนุกและมีประสิทธิภาพมากขึ้น**

**✅ เงื่อนไขการเข้าร่วม:**
**• สำหรับการเข้าร่วมโปรแกรม เพียงสมัครสมาชิกช่อง**

**🏆 โบนัสของคุณ:**
**• 2 เพื่อน → 1 สัปดาห์**
**• 5 เพื่อน → 1 เดือน**
**• 10 เพื่อน → 🔥 ซอฟต์แวร์ + เมนเทอร์!**

**💡 สิ่งสำคัญ:**
**ส่วนโบนัสที่ใช้งานจะปรากฏโดยอัตโนมัติเมื่อคุณถึงความคืบหน้าบางอย่าง เพียงเชิญเพื่อนและติดตามความคืบหน้าของคุณ!**

**💡 เติบโตด้วยกัน — หารายได้ด้วยกัน!**""",
        "es": """**🎯 Invita amigo — ¡aprendan y crezcan juntos!**

**Trae amigos a nuestro equipo y obtén bonos reales!**

**Aprender trading juntos es más divertido y efectivo.**

**✅ Condiciones de participación:**
**• Para participar en el programa, solo suscríbete al canal**

**🏆 Tus bonos:**
**• 2 amigos → 1 semana de suscripción**
**• 5 amigos → 1 mes de suscripción**
**• 10 amigos → 🔥 ¡Software + Mentoría!**

**💡 Importante:**
**La sección de bono activo aparecerá automáticamente cuando alcances cierto progreso. ¡Solo invita amigos y rastrea tu progreso!**

**💡 ¡Crezcan juntos — ganen juntos!**""",
        "ar": """**🎯 ادعُ صديقاً — تعلموا وانموا معاً!**

**أحضر أصدقاء لفريقنا واحصل على مكافآت حقيقية!**

**التعلم معاً أكثر متعة وفعالية.**

**✅ شروط المشاركة:**
**• للمشاركة في البرنامج، فقط اشترك في القناة**

**🏆 مكافآتك:**
**• 2 أصدقاء → أسبوع اشتراك**
**• 5 أصدقاء → شهر اشتراك**
**• 10 أصدقاء → 🔥 برنامج + إرشاد!**

**💡 مهم:**
**ستظهر قسم المكافأة النشط تلقائياً عند وصولك إلى تقدم معين. فقط ادعو الأصدقاء وتابع تقدمك!**

**💡 انموا معاً — اكسبوا معاً!**""",
        "uk": """**🎯 Запроси друга — розвивайся та навчайся разом!**

**Приводь друзів до нашої команди та отримуй за це реальні бонуси!**

**Разом навчатися трейдингу цікавіше та ефективніше. А ми заохочуємо тих, хто допомагає рости нашій спільноті чесних трейдерів.**

**✅ Умови участі:**
**• Для участі в програмі достатньо бути підписаним на канал**

**🏆 Твої бонуси:**
**• 2 друга → Тиждень підписки на індикатор**
**• 5 друзів → Місяць підписки**
**• 10 друзів → 🔥 Софт + Менторство!**

**💡 Важливо:**
**Розділ з активним бонусом з'явиться автоматично при досягненні певного прогресу. Просто запрошуй друзів та стеж за своїм прогресом!**

**💡 Розвивайся разом — заробляй разом!**"""
    },
    
    "btn_my_referral_link": {
        "ru": "🔗 Моя реферальная ссылка",
        "en": "🔗 My Referral Link",
        "th": "🔗 ลิงก์แนะนำของฉัน",
        "es": "🔗 Mi Enlace de Referido",
        "ar": "🔗 رابط الإحالة الخاص بي",
        "uk": "🔗 Моє реферальне посилання",
    },
    
    "btn_my_progress": {
        "ru": "📊 Мой прогресс",
        "en": "📊 My Progress",
        "th": "📊 ความคืบหน้าของฉัน",
        "es": "📊 Mi Progreso",
        "ar": "📊 تقدمي",
        "uk": "📊 Мій прогрес",
    },
    
    "btn_claim_bonus": {
        "ru": "🎁 Получить бонус",
        "en": "🎁 Claim Bonus",
        "th": "🎁 รับโบนัส",
        "es": "🎁 Reclamar Bono",
        "ar": "🎁 المطالبة بالمكافأة",
        "uk": "🎁 Отримати бонус",
    },
    
    "btn_contact_manager": {
        "ru": "👨‍💼 Связаться с менеджером",
        "en": "👨‍💼 Contact Manager",
        "th": "👨‍💼 ติดต่อผู้จัดการ",
        "es": "👨‍💼 Contactar Manager",
        "ar": "👨‍💼 اتصل بالمدير",
        "uk": "👨‍💼 Звязатися з менеджером",
    },
    
    "btn_main_menu": {
        "ru": "🏠 Главное меню",
        "en": "🏠 Main Menu",
        "th": "🏠 เมนูหลัก",
        "es": "🏠 Menú Principal",
        "ar": "🏠 القائمة الرئيسية",
        "uk": "🏠 Головне меню",
    },
    
    "btn_faq": {
        "ru": "❓ FAQ (Вопросы/Ответы)",
        "en": "❓ FAQ (Questions/Answers)",
        "th": "❓ FAQ (คำถาม/คำตอบ)",
        "es": "❓ FAQ (Preguntas/Respuestas)",
        "ar": "❓ FAQ (أسئلة/إجابات)",
        "uk": "❓ FAQ (Питання/Відповіді)",
    },
    
    # ============================================
    # МЕНЮ ТРЕЙДЕРА
    # ============================================
    
    "trader_menu_title": {
        "ru": "*📼 МЕНЮ ТРЕЙДЕРА*",
        "en": "*📼 TRADER MENU*",
        "th": "*📼 เมนูเทรดเดอร์*",
        "es": "*📼 MENÚ DEL TRADER*",
        "ar": "*📼 قائمة المتداول*",
        "uk": "*📼 МЕНЮ ТРЕЙДЕРА*",
    },
    
    "trader_menu_description": {
        "ru": "*Выберите свой уровень развития в трейдинге.*\n\n*Каждый уровень открывает новые возможности и инструменты для заработка на рынке.*",
        "en": "*Choose your trading development level.*\n\n*Each level unlocks new opportunities and tools for earning in the market.*",
        "th": "*เลือกระดับการพัฒนาการเทรดของคุณ*\n\n*แต่ละระดับจะปลดล็อกโอกาสและเครื่องมือใหม่สำหรับการทำกำไรในตลาด*",
        "es": "*Elige tu nivel de desarrollo en trading.*\n\n*Cada nivel desbloquea nuevas oportunidades y herramientas para ganar en el mercado.*",
        "ar": "*اختر مستوى تطورك في التداول.*\n\n*كل مستوى يفتح فرصًا وأدوات جديدة للكسب في السوق.*",
        "uk": "*Оберіть свій рівень розвитку в трейдингу.*\n\n*Кожен рівень відкриває нові можливості та інструменти для заробітку на ринку.*",
    },
    
    # ============================================
    # УРОВНИ
    # ============================================
    
    "btn_level_free": {
        "ru": "🆓 FREE",
        "en": "🆓 FREE",
        "th": "🆓 ฟรี",
        "es": "🆓 GRATIS",
        "ar": "🆓 مجاني",
        "uk": "🆓 FREE",
    },
    
    "btn_level_pro": {
        "ru": "💰 PRO",
        "en": "💰 PRO",
        "th": "💰 โปร",
        "es": "💰 PRO",
        "ar": "💰 احترافي",
        "uk": "💰 PRO",
    },
    
    "btn_level_mentor": {
        "ru": "🎓 MENTOR",
        "en": "🎓 MENTOR",
        "th": "🎓 เมนเทอร์",
        "es": "🎓 MENTOR",
        "ar": "🎓 مرشد",
        "uk": "🎓 MENTOR",
    },
    
    "btn_level_elite": {
        "ru": "👑 ELITE",
        "en": "👑 ELITE",
        "th": "👑 อีลิท",
        "es": "👑 ELITE",
        "ar": "👑 نخبة",
        "uk": "👑 ELITE",
    },
    
    "btn_get_access": {
        "ru": "✅ Получить",
        "en": "✅ Get Access",
        "th": "✅ รับการเข้าถึง",
        "es": "✅ Obtener",
        "ar": "✅ احصل عليه",
        "uk": "✅ Отримати",
    },
    
    "btn_learn_more": {
        "ru": "💬 Узнать подробнее",
        "en": "💬 Learn More",
        "th": "💬 เรียนรู้เพิ่มเติม",
        "es": "💬 Saber Más",
        "ar": "💬 اعرف المزيد",
        "uk": "💬 Узнати подробніше",
    },
    
    "btn_back_to_trader": {
        "ru": "🔙 Назад к меню",
        "en": "🔙 Back to Menu",
        "th": "🔙 กลับไปที่เมนู",
        "es": "🔙 Volver al Menú",
        "ar": "🔙 العودة للقائمة",
        "uk": "🔙 Назад до меню",
    },
    
    # ============================================
    # УРОВЕНЬ FREE
    # ============================================
    
    "level_free_title": {
        "ru": "🆓 *УРОВЕНЬ FREE*",
        "en": "🆓 *FREE LEVEL*",
        "th": "🆓 *ระดับฟรี*",
        "es": "🆓 *NIVEL GRATIS*",
        "ar": "🆓 *المستوى المجاني*",
        "uk": "🆓 *РІВЕНЬ FREE*",
    },
    
    "level_free_description": {
        "ru": """*Твой старт в алгоритмическом трейдинге!*

*📱 Что входит:*
*• Telegram бот Forex Signals Pro*
*• Веб-приложение с сигналами*
*• Базовые торговые сигналы*
*• Доступ к каналу*

*🎯 Для кого:*
*Для тех, кто хочет начать зарабатывать на рынке без вложений в софт.*

*💡 Преимущества:*
*• Полностью бесплатно*
*• Готовые сигналы*
*• Простой старт*""",
        "en": """*Your start in algorithmic trading!*

*📱 What's included:*
*• Telegram bot Forex Signals Pro*
*• Web app with signals*
*• Basic trading signals*
*• Channel access*

*🎯 Who is it for:*
*For those who want to start earning in the market without investing in software.*

*💡 Benefits:*
*• Completely free*
*• Ready-made signals*
*• Easy start*""",
        "th": """*จุดเริ่มต้นของคุณในการเทรดอัลกอริทึม!*

*📱 สิ่งที่รวมอยู่:*
*• บอทเทเลแกรม Forex Signals Pro*
*• เว็บแอปพร้อมสัญญาณ*
*• สัญญาณการเทรดพื้นฐาน*
*• การเข้าถึงช่อง*

*🎯 เหมาะสำหรับ:*
*สำหรับผู้ที่ต้องการเริ่มหารายได้ในตลาดโดยไม่ต้องลงทุนในซอฟต์แวร์*

*💡 ประโยชน์:*
*• ฟรีทั้งหมด*
*• สัญญาณสำเร็จรูป*
*• เริ่มต้นง่าย*""",
        "es": """*¡Tu inicio en el trading algorítmico!*

*📱 Qué incluye:*
*• Bot de Telegram Forex Signals Pro*
*• App web con señales*
*• Señales básicas de trading*
*• Acceso al canal*

*🎯 Para quién es:*
*Para quienes quieren empezar a ganar en el mercado sin invertir en software.*

*💡 Beneficios:*
*• Completamente gratis*
*• Señales listas*
*• Inicio fácil*""",
        "ar": """*بدايتك في التداول الخوارزمي!*

*📱 ما يتضمن:*
*• بوت تيليجرام Forex Signals Pro*
*• تطبيق ويب مع إشارات*
*• إشارات تداول أساسية*
*• الوصول إلى القناة*

*🎯 لمن هذا:*
*لمن يريد البدء في الكسب من السوق دون الاستثمار في البرامج.*

*💡 الفوائد:*
*• مجاني تمامًا*
*• إشارات جاهزة*
*• بداية سهلة*""",
        "uk": """*Твій старт в алгоритмічному трейдингу!*

*📱 Що входить:*
*• Telegram бот Forex Signals Pro*
*• Веб-застосунок з сигналами*
*• Базові торгові сигнали*
*• Доступ до каналу*

*🎯 Для кого:*
*Для тих, хто хоче почати заробляти на ринку без вкладень у софт.*

*💡 Переваги:*
*• Повністю безкоштовно*
*• Готові сигнали*
*• Простий старт*"""
    },
    
    # ============================================
    # УРОВЕНЬ PRO
    # ============================================
    
    "level_pro_title": {
        "ru": "💰 *УРОВЕНЬ PRO*",
        "en": "💰 *PRO LEVEL*",
        "th": "💰 *ระดับโปร*",
        "es": "💰 *NIVEL PRO*",
        "ar": "💰 *المستوى الاحترافي*",
        "uk": "💰 *РІВЕНЬ PRO*",
    },
    
    "level_pro_description": {
        "ru": """*Профессиональные инструменты для серьезного заработка!*

*🔧 Что входит:*
*• Авторский индикатор (TradingView)*
*• Торговая стратегия*
*• Всё из уровня FREE*

*🎯 Для кого:*
*Для тех, кто хочет самостоятельно принимать решения с помощью проверенных инструментов.*

*💡 Преимущества:*
*• Глубокая аналитика*
*• Авторские разработки*
*• Повышенная точность сигналов*""",
        "en": """*Professional tools for serious earnings!*

*🔧 What's included:*
*• Proprietary indicator (TradingView)*
*• Trading strategy*
*• Everything from FREE level*

*🎯 Who is it for:*
*For those who want to make decisions independently using proven tools.*

*💡 Benefits:*
*• Deep analytics*
*• Proprietary developments*
*• Increased signal accuracy*""",
        "th": """*เครื่องมือระดับมืออาชีพสำหรับการทำกำไรจริงจัง!*

*🔧 สิ่งที่รวมอยู่:*
*• ตัวบ่งชี้พิเศษ (TradingView)*
*• กลยุทธ์การเทรด*
*• ทุกอย่างจากระดับ FREE*

*🎯 เหมาะสำหรับ:*
*สำหรับผู้ที่ต้องการตัดสินใจด้วยตนเองโดยใช้เครื่องมือที่พิสูจน์แล้ว*

*💡 ประโยชน์:*
*• การวิเคราะห์เชิงลึก*
*• การพัฒนาพิเศษ*
*• ความแม่นยำของสัญญาณที่เพิ่มขึ้น*""",
        "es": """*¡Herramientas profesionales para ganancias serias!*

*🔧 Qué incluye:*
*• Indicador propietario (TradingView)*
*• Estrategia de trading*
*• Todo del nivel FREE*

*🎯 Para quién es:*
*Para quienes quieren tomar decisiones independientemente usando herramientas probadas.*

*💡 Beneficios:*
*• Análisis profundo*
*• Desarrollos propietarios*
*• Mayor precisión de señales*""",
        "ar": """*أدوات احترافية للكسب الجاد!*

*🔧 ما يتضمن:*
*• مؤشر حصري (TradingView)*
*• استراتيجية تداول*
*• كل شيء من المستوى المجاني*

*🎯 لمن هذا:*
*لمن يريد اتخاذ قرارات مستقلة باستخدام أدوات مثبتة.*

*💡 الفوائد:*
*• تحليلات عميقة*
*• تطويرات حصرية*
*• دقة إشارات متزايدة*""",
        "uk": """*Професійні інструменти для серйозного заробітку!*

*🔧 Що входить:*
*• Авторський індикатор (TradingView)*
*• Торгова стратегія*
*• Все з рівня FREE*

*🎯 Для кого:*
*Для тих, хто хоче самостійно приймати рішення за допомогою перевірених інструментів.*

*💡 Переваги:*
*• Глибока аналітика*
*• Авторські розробки*
*• Підвищена точність сигналів*"""
    },
    
    # ============================================
    # УРОВЕНЬ MENTOR
    # ============================================
    
    "level_mentor_title": {
        "ru": "🎓 *УРОВЕНЬ MENTOR*",
        "en": "🎓 *MENTOR LEVEL*",
        "th": "🎓 *ระดับเมนเทอร์*",
        "es": "🎓 *NIVEL MENTOR*",
        "ar": "🎓 *مستوى المرشد*",
        "uk": "🎓 *РІВЕНЬ MENTOR*",
    },
    
    "level_mentor_description": {
        "ru": """*Персональное обучение и сопровождение!*

*📚 Что входит:*
*• Индикатор + весь софт*
*• Личный разбор сделок*
*• Сопровождение в формате обучения*
*• Разбор рынка*
*• Всё из уровня PRO*

*🎯 Для кого:*
*Для тех, кто хочет глубоко погрузиться в трейдинг под руководством опытного ментора.*

*💡 Преимущества:*
*• Индивидуальный подход*
*• Разбор ваших ошибок*
*• Ускоренное обучение*""",
        "en": """*Personal training and support!*

*📚 What's included:*
*• Indicator + all software*
*• Personal trade analysis*
*• Training-style support*
*• Market breakdown*
*• Everything from PRO level*

*🎯 Who is it for:*
*For those who want to deeply immerse in trading under experienced mentor guidance.*

*💡 Benefits:*
*• Individual approach*
*• Analysis of your mistakes*
*• Accelerated learning*""",
        "th": """*การฝึกอบรมและการสนับสนุนส่วนบุคคล!*

*📚 สิ่งที่รวมอยู่:*
*• ตัวบ่งชี้ + ซอฟต์แวร์ทั้งหมด*
*• การวิเคราะห์การเทรดส่วนตัว*
*• การสนับสนุนแบบฝึกอบรม*
*• การวิเคราะห์ตลาด*
*• ทุกอย่างจากระดับ PRO*

*🎯 เหมาะสำหรับ:*
*สำหรับผู้ที่ต้องการดำดิ่งลึกในการเทรดภายใต้การแนะนำของเมนเทอร์ที่มีประสบการณ์*

*💡 ประโยชน์:*
*• แนวทางส่วนบุคคล*
*• การวิเคราะห์ข้อผิดพลาดของคุณ*
*• การเรียนรู้แบบเร่งด่วน*""",
        "es": """*¡Entrenamiento y apoyo personal!*

*📚 Qué incluye:*
*• Indicador + todo el software*
*• Análisis personal de trades*
*• Soporte en formato de entrenamiento*
*• Análisis del mercado*
*• Todo del nivel PRO*

*🎯 Para quién es:*
*Para quienes quieren sumergirse profundamente en el trading bajo la guía de un mentor experimentado.*

*💡 Beneficios:*
*• Enfoque individual*
*• Análisis de tus errores*
*• Aprendizaje acelerado*""",
        "ar": """*تدريب ودعم شخصي!*

*📚 ما يتضمن:*
*• المؤشر + كل البرامج*
*• تحليل صفقات شخصي*
*• دعم بأسلوب التدريب*
*• تحليل السوق*
*• كل شيء من المستوى الاحترافي*

*🎯 لمن هذا:*
*لمن يريد الغوص عميقًا في التداول تحت إشراف مرشد خبير.*

*💡 الفوائد:*
*• نهج فردي*
*• تحليل أخطائك*
*• تعلم مُسرَّع*""",
        "uk": """*Персональне навчання та супровід!*

*📚 Що входить:*
*• Індикатор + весь софт*
*• Особистий розбір угод*
*• Супровід у форматі навчання*
*• Розбір ринку*
*• Все з рівня PRO*

*🎯 Для кого:*
*Для тих, хто хоче глибоко зануритися в трейдинг під керівництвом досвідченого ментора.*

*💡 Переваги:*
*• Індивідуальний підхід*
*• Розбір ваших помилок*
*• Прискорене навчання*"""
    },
    
    # ============================================
    # УРОВЕНЬ ELITE
    # ============================================
    
    "level_elite_title": {
        "ru": "👑 *УРОВЕНЬ ELITE*",
        "en": "👑 *ELITE LEVEL*",
        "th": "👑 *ระดับอีลิท*",
        "es": "👑 *NIVEL ELITE*",
        "ar": "👑 *مستوى النخبة*",
        "uk": "👑 *РІВЕНЬ ELITE*",
    },
    
    "level_elite_description": {
        "ru": """*Максимальный уровень - работа с фондом!*

*👑 Что входит:*
*• Закрытый Discord*
*• Live-торговля в прямом эфире*
*• Работа с фондом*
*• Все преимущества уровня MENTOR*

*🎯 Для кого:*
*Для серьезных трейдеров, готовых работать с крупным капиталом и максимизировать прибыль.*

*💡 Преимущества:*
*• Торговля вместе с профессионалами*
*• Доступ к эксклюзивным сделкам*
*• Максимальная прибыль*""",
        "en": """*Maximum level - working with the fund!*

*👑 What's included:*
*• Closed Discord*
*• Live trading in real-time*
*• Working with the fund*
*• All MENTOR level benefits*

*🎯 Who is it for:*
*For serious traders ready to work with large capital and maximize profits.*

*💡 Benefits:*
*• Trading alongside professionals*
*• Access to exclusive deals*
*• Maximum profit*""",
        "th": """*ระดับสูงสุด - ทำงานกับกองทุน!*

*👑 สิ่งที่รวมอยู่:*
*• Discord ปิด*
*• การเทรดสดแบบเรียลไทม์*
*• การทำงานกับกองทุน*
*• สิทธิประโยชน์ทั้งหมดของระดับ MENTOR*

*🎯 เหมาะสำหรับ:*
*สำหรับเทรดเดอร์จริงจังที่พร้อมทำงานกับทุนขนาดใหญ่และเพิ่มผลกำไรสูงสุด*

*💡 ประโยชน์:*
*• เทรดร่วมกับมืออาชีพ*
*• เข้าถึงดีลพิเศษ*
*• กำไรสูงสุด*""",
        "es": """*¡Nivel máximo - trabajando con el fondo!*

*👑 Qué incluye:*
*• Discord cerrado*
*• Trading en vivo en tiempo real*
*• Trabajo con el fondo*
*• Todos los beneficios del nivel MENTOR*

*🎯 Para quién es:*
*Para traders serios listos para trabajar con gran capital y maximizar ganancias.*

*💡 Beneficios:*
*• Trading junto a profesionales*
*• Acceso a deals exclusivos*
*• Máxima ganancia*""",
        "ar": """*أعلى مستوى - العمل مع الصندوق!*

*👑 ما يتضمن:*
*• Discord مغلق*
*• تداول مباشر في الوقت الحقيقي*
*• العمل مع الصندوق*
*• جميع مزايا مستوى المرشد*

*🎯 لمن هذا:*
*للمتداولين الجادين المستعدين للعمل برأس مال كبير وتعظيم الأرباح.*

*💡 الفوائد:*
*• التداول جنبًا إلى جنب مع المحترفين*
*• الوصول إلى صفقات حصرية*
*• أقصى ربح*""",
        "uk": """*Максимальний рівень - робота з фондом!*

*👑 Що входить:*
*• Закритий Discord*
*• Live-торгівля в прямому ефірі*
*• Робота з фондом*
*• Всі переваги рівня MENTOR*

*🎯 Для кого:*
*Для серйозних трейдерів, готових працювати з великим капіталом та максимізувати прибуток.*

*💡 Переваги:*
*• Торгівля разом з професіоналами*
*• Доступ до ексклюзивних угод*
*• Максимальний прибуток*"""
    },
    
    # ============================================
    # FAQ
    # ============================================
    
    "faq_title": {
        "ru": "*❓ FAQ - Частые вопросы*",
        "en": "*❓ FAQ - Frequently Asked Questions*",
        "th": "*❓ คำถามที่พบบ่อย*",
        "es": "*❓ FAQ - Preguntas Frecuentes*",
        "ar": "*❓ الأسئلة الشائعة*",
        "uk": "*❓ FAQ - Часті запитання*",
    },
    
    "faq_select_question": {
        "ru": """Выберите вопрос, чтобы получить подробный ответ.

📚 *В этом разделе вы найдете ответы на самые частые вопросы:*
• Как начать работу с ботом
• Что делать, если уже есть аккаунт
• Как получить доступ к индикаторам
• Все о регистрации и верификации

💡 *Не нашли ответ?*
Свяжитесь с нашей поддержкой через кнопку в меню - мы всегда готовы помочь!

Выберите вопрос ниже для получения подробной информации:""",
        "en": """Select a question to get a detailed answer.

📚 *In this section you will find answers to the most common questions:*
• How to start working with the bot
• What to do if you already have an account
• How to get access to indicators
• Everything about registration and verification

💡 *Didn't find an answer?*
Contact our support via the menu button - we're always ready to help!

Select a question below for detailed information:""",
        "th": """เลือกคำถามเพื่อรับคำตอบโดยละเอียด

📚 *ในส่วนนี้คุณจะพบคำตอบสำหรับคำถามที่พบบ่อยที่สุด:*
• วิธีเริ่มทำงานกับบอท
• ควรทำอย่างไรหากมีบัญชีอยู่แล้ว
• วิธีการเข้าถึงตัวบ่งชี้
• ทุกอย่างเกี่ยวกับการลงทะเบียนและการยืนยัน

💡 *ไม่พบคำตอบ?*
ติดต่อฝ่ายสนับสนุนของเราผ่านปุ่มในเมนู - เราพร้อมให้ความช่วยเหลือเสมอ!

เลือกคำถามด้านล่างเพื่อรับข้อมูลโดยละเอียด:""",
        "es": """Seleccione una pregunta para obtener una respuesta detallada.

📚 *En esta sección encontrará respuestas a las preguntas más frecuentes:*
• Cómo empezar a trabajar con el bot
• Qué hacer si ya tiene una cuenta
• Cómo obtener acceso a los indicadores
• Todo sobre registro y verificación

💡 *¿No encontró una respuesta?*
¡Contáctenos a través del botón del menú - siempre estamos listos para ayudar!

Seleccione una pregunta a continuación para obtener información detallada:""",
        "ar": """اختر سؤالاً للحصول على إجابة مفصلة.

📚 *في هذا القسم ستجد إجابات على الأسئلة الأكثر شيوعًا:*
• كيفية البدء في العمل مع البوت
• ماذا تفعل إذا كان لديك حساب بالفعل
• كيفية الحصول على الوصول إلى المؤشرات
• كل شيء عن التسجيل والتحقق

💡 *لم تجد إجابة?*
اتصل بدعمنا عبر زر القائمة - نحن دائماً مستعدون للمساعدة!

اختر سؤالاً أدناه للحصول على معلومات مفصلة:""",
        "uk": """Оберіть питання, щоб отримати детальну відповідь.

📚 *У цьому розділі ви знайдете відповіді на найчастіші питання:*
• Як почати роботу з ботом
• Що робити, якщо вже є акаунт
• Як отримати доступ до індикаторів
• Все про реєстрацію та верифікацію

💡 *Не знайшли відповідь?*
Зв'яжіться з нашою підтримкою через кнопку в меню - ми завжди готові допомогти!

Виберіть питання нижче для отримання детальної інформації:""",
    },
    
    "faq_btn_how_start": {
        "ru": "🚀 Как начать?",
        "en": "🚀 How to start?",
        "th": "🚀 เริ่มต้นอย่างไร?",
        "es": "🚀 ¿Cómo empezar?",
        "ar": "🚀 كيف أبدأ؟",
        "uk": "🚀 Як почати?",
    },
    
    "faq_answer_how_start": {
        "ru": """*🚀 Как начать?*

*Шаг 1:* *Зарегистрируйтесь на платформе PocketOption по нашей ссылке*

*Шаг 2:* *Пополните баланс минимум на $50 (используйте промокод 50START для бонуса +50%)*

*Шаг 3:* *Отправьте ваш ID аккаунта боту*

*Шаг 4:* *Получите доступ к сигналам и начните зарабатывать!*

*⏰ Время обработки: до 24 часов*""",
        "en": """*🚀 How to start?*

*Step 1:* *Register on PocketOption platform via our link*

*Step 2:* *Deposit at least $50 (use promo code 50START for +50% bonus)*

*Step 3:* *Send your account ID to the bot*

*Step 4:* *Get access to signals and start earning!*

*⏰ Processing time: up to 24 hours*""",
        "th": """*🚀 เริ่มต้นอย่างไร?*

*ขั้นตอนที่ 1:* *ลงทะเบียนบนแพลตฟอร์ม PocketOption ผ่านลิงก์ของเรา*

*ขั้นตอนที่ 2:* *ฝากเงินอย่างน้อย $50 (ใช้โค้ดโปรโมชั่น 50START สำหรับโบนัส +50%)*

*ขั้นตอนที่ 3:* *ส่ง ID บัญชีของคุณไปยังบอท*

*ขั้นตอนที่ 4:* *รับการเข้าถึงสัญญาณและเริ่มหารายได้!*

*⏰ เวลาในการประมวลผล: สูงสุด 24 ชั่วโมง*""",
        "es": """*🚀 ¿Cómo empezar?*

*Paso 1:* *Regístrate en la plataforma PocketOption a través de nuestro enlace*

*Paso 2:* *Deposita al menos $50 (usa el código promocional 50START para +50% de bonificación)*

*Paso 3:* *Envía tu ID de cuenta al bot*

*Paso 4:* *¡Obtén acceso a las señales y comienza a ganar!*

*⏰ Tiempo de procesamiento: hasta 24 horas*""",
        "ar": """*🚀 كيف أبدأ؟*

*الخطوة 1:* *سجل على منصة PocketOption عبر رابطنا*

*الخطوة 2:* *أودع ما لا يقل عن $50 (استخدم الرمز الترويجي 50START للحصول على مكافأة +50%)*

*الخطوة 3:* *أرسل معرف حسابك إلى البوت*

*الخطوة 4:* *احصل على الوصول إلى الإشارات وابدأ في الكسب!*

*⏰ وقت المعالجة: حتى 24 ساعة*""",
        "uk": """*🚀 Як почати?*

*Крок 1:* *Зареєструйтеся на платформі PocketOption за нашим посиланням*

*Крок 2:* *Поповніть баланс мінімум на $50 (використайте промокод 50START для бонусу +50%)*

*Крок 3:* *Відправте ваш ID акаунта боту*

*Крок 4:* *Отримайте доступ до сигналів та почніть заробляти!*

*⏰ Час обробки: до 24 годин*"""
    },
    
    "btn_back_to_faq": {
        "ru": "🔙 Назад к FAQ",
        "en": "🔙 Back to FAQ",
        "th": "🔙 กลับไปที่ FAQ",
        "es": "🔙 Volver a FAQ",
        "ar": "🔙 العودة للأسئلة الشائعة",
        "uk": "🔙 Назад до FAQ",
    },
    
    "faq_btn_have_account": {
        "ru": "🔄 У меня уже есть аккаунт",
        "en": "🔄 I already have an account",
        "th": "🔄 ฉันมีบัญชีอยู่แล้ว",
        "es": "🔄 Ya tengo una cuenta",
        "ar": "🔄 لدي حساب بالفعل",
        "uk": "🔄 У меня вже є акаунт",
    },
    
    "faq_answer_have_account": {
        "ru": """*🔄 У меня уже есть аккаунт*

*Если у вас уже есть аккаунт на PocketOption, вам необходимо:*

*Шаг 1:* *Закрыть старый аккаунт*

*Шаг 2:* *Пройти регистрацию заново по нашей реферальной ссылке*

*Шаг 3:* *Пополнить баланс минимум $50*

*Шаг 4:* *Отправить новый ID аккаунта боту*

*⚠️ Это необходимо для получения бонусов и доступа к сигналам.*""",
        "en": """*🔄 I already have an account*

*If you already have a PocketOption account, you need to:*

*Step 1:* *Close your old account*

*Step 2:* *Register again using our referral link*

*Step 3:* *Deposit at least $50*

*Step 4:* *Send your new account ID to the bot*

*⚠️ This is required to receive bonuses and access to signals.*""",
        "th": """*🔄 ฉันมีบัญชีอยู่แล้ว*

*หากคุณมีบัญชี PocketOption อยู่แล้ว คุณต้อง:*

*ขั้นตอนที่ 1:* *ปิดบัญชีเก่า*

*ขั้นตอนที่ 2:* *ลงทะเบียนใหม่โดยใช้ลิงก์แนะนำของเรา*

*ขั้นตอนที่ 3:* *ฝากเงินอย่างน้อย $50*

*ขั้นตอนที่ 4:* *ส่ง ID บัญชีใหม่ไปยังบอท*

*⚠️ จำเป็นสำหรับการรับโบนัสและการเข้าถึงสัญญาณ*""",
        "es": """*🔄 Ya tengo una cuenta*

*Si ya tienes una cuenta en PocketOption, necesitas:*

*Paso 1:* *Cerrar tu cuenta antigua*

*Paso 2:* *Registrarte de nuevo usando nuestro enlace de referencia*

*Paso 3:* *Depositar al menos $50*

*Paso 4:* *Enviar tu nuevo ID de cuenta al bot*

*⚠️ Esto es necesario para recibir bonos y acceso a señales.*""",
        "ar": """*🔄 لدي حساب بالفعل*

*إذا كان لديك حساب PocketOption بالفعل، تحتاج إلى:*

*الخطوة 1:* *إغلاق حسابك القديم*

*الخطوة 2:* *التسجيل مرة أخرى باستخدام رابط الإحالة الخاص بنا*

*الخطوة 3:* *إيداع ما لا يقل عن $50*

*الخطوة 4:* *إرسال معرف حسابك الجديد إلى البوت*

*⚠️ هذا ضروري للحصول على المكافآت والوصول إلى الإشارات.*""",
        "uk": """*🔄 У мене вже є акаунт*

*Якщо у вас вже є акаунт на PocketOption, вам необхідно:*

*Крок 1:* *Закрити старий акаунт*

*Крок 2:* *Пройти реєстрацію заново за нашою реферальною ссилкою*

*Крок 3:* *Поповнити баланс мінімум $50*

*Крок 4:* *Відправити новий ID акаунта боту*

*⚠️ Це необхідно для отримання бонусів та доступу до сигналів.*"""
    },
    
    "faq_btn_get_indicator": {
        "ru": "📊 Как получить индикатор?",
        "en": "📊 How to get the indicator?",
        "th": "📊 จะรับตัวบ่งชี้ได้อย่างไร?",
        "es": "📊 ¿Cómo obtener el indicador?",
        "ar": "📊 كيف أحصل على المؤشر؟",
        "uk": "📊 Як отримати індикатор?",
    },
    
    "faq_answer_get_indicator": {
        "ru": """*📊 Как получить индикатор?*

*Для получения доступа к индикатору Black Mirror Ultra свяжитесь с нашей поддержкой.*

*Менеджер расскажет о условиях и поможет с подключением.*

*👨‍💼 Поддержка:* *@kaktotakxm*""",
        "en": """*📊 How to get the indicator?*

*To get access to the Black Mirror Ultra indicator, contact our support.*

*The manager will explain the conditions and help with connection.*

*👨‍💼 Support:* *@kaktotakxm*""",
        "th": """*📊 จะรับตัวบ่งชี้ได้อย่างไร?*

*เพื่อรับสิทธิ์เข้าถึงตัวบ่งชี้ Black Mirror Ultra ติดต่อฝ่ายสนับสนุนของเรา*

*ผู้จัดการจะอธิบายเงื่อนไขและช่วยเหลือในการเชื่อมต่อ*

*👨‍💼 การสนับสนุน:* *@kaktotakxm*""",
        "es": """*📊 ¿Cómo obtener el indicador?*

*Para obtener acceso al indicador Black Mirror Ultra, contacta con nuestro soporte.*

*El gerente explicará las condiciones y ayudará con la conexión.*

*👨‍💼 Soporte:* *@kaktotakxm*""",
        "ar": """*📊 كيف أحصل على المؤشر؟*

*للحصول على الوصول إلى مؤشر Black Mirror Ultra، اتصل بدعمنا.*

*سيشرح المدير الشروط ويساعد في التوصيل.*

*👨‍💼 الدعم:* *@kaktotakxm*""",
        "uk": """*📊 Як отримати індикатор?*

*Для отримання доступу до індикатора Black Mirror Ultra зв'яжіться з нашою підтримкою.*

*Менеджер розповість про умови та допоможе з підключенням.*

*👨‍💼 Підтримка:* *@kaktotakxm*"""
    },
    
    "btn_admin_panel": {
        "ru": "⚙️ Админ-панель",
        "en": "⚙️ Admin Panel",
        "th": "⚙️ แผงผู้ดูแล",
        "es": "⚙️ Panel de Admin",
        "ar": "⚙️ لوحة الإدارة",
        "uk": "⚙️ Адмін-панель",
    },
    
    "btn_forex_signals_pro": {
        "ru": "📊 Forex Signals Pro",
        "en": "📊 Forex Signals Pro",
        "th": "📊 Forex Signals Pro",
        "es": "📊 Forex Signals Pro",
        "ar": "📊 Forex Signals Pro",
        "uk": "📊 Forex Signals Pro",
    },
    
    "btn_black_mirror_ultra": {
        "ru": "🔮 Black Mirror Ultra",
        "en": "🔮 Black Mirror Ultra",
        "th": "🔮 Black Mirror Ultra",
        "es": "🔮 Black Mirror Ultra",
        "ar": "🔮 Black Mirror Ultra",
        "uk": "🔮 Black Mirror Ultra",
    },
    
    "btn_see_in_action": {
        "ru": "▶️ Посмотреть в работе",
        "en": "▶️ See in Action",
        "th": "▶️ ดูการทำงาน",
        "es": "▶️ Ver en Acción",
        "ar": "▶️ شاهد أثناء العمل",
        "uk": "▶️ Подивитися в роботі",
    },
    
    # ============================================
    # РЕФЕРАЛЬНАЯ СИСТЕМА "ЗДРАВЫЙ ТРЕЙДЕР"
    # ============================================
    
    "referral_menu_title": {
        "ru": "👥 *РЕФЕРАЛЬНАЯ ПРОГРАММА*",
        "en": "👥 *REFERRAL PROGRAM*",
        "th": "👥 *โปรแกรมแนะนำ*",
        "es": "👥 *PROGRAMA DE REFERIDOS*",
        "ar": "👥 *برنامج الإحالة*",
        "uk": "👥 *РЕФЕРАЛЬНАЯ ПРОГРАММА*",
    },
    
    "referral_menu_description": {
        "ru": "*Приглашай друзей — развивайтесь вместе и получай бонусы!*\n\n🎁 *Уровни наград:*\n• *2 друга* = Неделя подписки на индикатор\n• *5 друзей* = Месяц подписки на индикатор\n• *10 друзей* = 🔥 Софт + Менторство!",
        "en": "*Invite friends — learn together and get bonuses!*\n\n🎁 *Reward levels:*\n• *2 friends* = 1 week indicator subscription\n• *5 friends* = 1 month indicator subscription\n• *10 friends* = 🔥 Software + Mentorship!",
        "th": "*ชวนเพื่อน — เรียนรู้ด้วยกันและรับโบนัส!*\n\n🎁 *ระดับรางวัล:*\n• *2 เพื่อน* = สมัคร 1 สัปดาห์\n• *5 เพื่อน* = สมัคร 1 เดือน\n• *10 เพื่อน* = 🔥 ซอฟต์แวร์ + เมนเทอร์!",
        "es": "*¡Invita amigos — aprendan juntos y obtén bonos!*\n\n🎁 *Niveles de recompensa:*\n• *2 amigos* = 1 semana de suscripción\n• *5 amigos* = 1 mes de suscripción\n• *10 amigos* = 🔥 Software + Mentoría!",
        "ar": "*ادعو أصدقاء — تعلموا معاً واحصل على مكافآت!*\n\n🎁 *مستويات المكافآت:*\n• *2 أصدقاء* = أسبوع اشتراك\n• *5 أصدقاء* = شهر اشتراك\n• *10 أصدقاء* = 🔥 برنامج + إرشاد!",
        "uk": "*Запрошуй друзів — розвивайся разом та отримуй бонуси!*\n\n🎁 *Рівні нагород:*\n• *2 друга* = Тиждень підписки на індикатор\n• *5 друзів* = Місяць підписки на індикатор\n• *10 друзів* = 🔥 Софт + Менторство!",
    },
    
    "referral_your_link": {
        "ru": "Твоя ссылка",
        "en": "Your link",
        "th": "ลิงก์ของคุณ",
        "es": "Tu enlace",
        "ar": "رابطك",
        "uk": "Твоя силка",
    },
    
    "referral_stats_title": {
        "ru": "Статистика",
        "en": "Statistics",
        "th": "สถิติ",
        "es": "Estadísticas",
        "ar": "الإحصائيات",
        "uk": "Статистика",
    },
    
    "referral_total_clicks": {
        "ru": "Перешли по ссылке",
        "en": "Clicked link",
        "th": "คลิกลิงก์",
        "es": "Clics en enlace",
        "ar": "نقرات الرابط",
        "uk": "Перешли по силці",
    },
    
    "referral_activated": {
        "ru": "Активировано",
        "en": "Activated",
        "th": "เปิดใช้งานแล้ว",
        "es": "Activados",
        "ar": "مفعل",
        "uk": "Активовано",
    },
    
    "referral_progress": {
        "ru": "Прогресс до бонуса",
        "en": "Progress to bonus",
        "th": "ความคืบหน้าสู่โบนัส",
        "es": "Progreso al bono",
        "ar": "التقدم نحو المكافأة",
        "uk": "Прогресс до бонусу",
    },
    
    "referral_next_bonus": {
        "ru": "До бонуса осталось: {remaining} друзей",
        "en": "{remaining} friends left to bonus",
        "th": "เหลืออีก {remaining} เพื่อนสำหรับตัวบ่งชี้ {days} วัน",
        "es": "Faltan {remaining} amigos para {days} días de indicador",
        "ar": "تبقى {remaining} صديق للحصول على المؤشر لمدة {days} يوم",
        "uk": "До бонусу залишилося: {remaining} друзів",
    },
    
    "btn_referral_copy_link": {
        "ru": "📋 Скопировать ссылку",
        "en": "📋 Copy link",
        "th": "📋 คัดลอกลิงก์",
        "es": "📋 Copiar enlace",
        "ar": "📋 نسخ الرابط",
        "uk": "📋 Скопіювати посилання",
    },
    
    "btn_referral_share": {
        "ru": "📤 Поделиться ссылкой",
        "en": "📤 Share link",
        "th": "📤 แชร์ลิงก์",
        "es": "📤 Compartir enlace",
        "ar": "📤 مشاركة الرابط",
        "uk": "📤 Поділитися посиланням",
    },
    
    "btn_referral_claim_bonus": {
        "ru": "Забрать бонус",
        "en": "Claim bonus",
        "th": "รับโบนัส",
        "es": "Reclamar bono",
        "ar": "استلام المكافأة",
        "uk": "Отримати бонус",
    },
    
    "btn_referral_stats": {
        "ru": "📊 Статистика / Рефералы",
        "en": "📊 Statistics / Referrals",
        "th": "📊 สถิติ / การแนะนำ",
        "es": "📊 Estadísticas / Referidos",
        "ar": "📊 الإحصائيات / الإحالات",
        "uk": "📊 Статистика / Реферали",
    },
    
    "referral_stats_title": {
        "ru": "📊 Статистика и рефералы",
        "en": "📊 Statistics and referrals",
        "th": "📊 สถิติและการแนะนำ",
        "es": "📊 Estadísticas y referidos",
        "ar": "📊 الإحصائيات والإحالات",
        "uk": "📊 Статистика і реферали",
    },
    
    "referral_stats_description": {
        "ru": """Здесь вы можете отслеживать свой прогресс в реферальной программе.

📈 *Что показывает статистика:*
• Количество переходов по вашей ссылке
• Количество активированных рефералов
• Текущий прогресс до следующего бонуса
• Список ваших рефералов и их статус

💡 *Полезная информация:*
• Реферал считается активированным после регистрации, ввода ID и депозита
• Прогресс обновляется автоматически
• Бонусы можно получить в разделе "Забрать бонус"

🎯 *Совет:* Поделитесь своей ссылкой в социальных сетях для привлечения большего количества рефералов!""",
        "en": """Here you can track your progress in the referral program.

📈 *What the statistics show:*
• Number of clicks on your link
• Number of activated referrals
• Current progress to the next bonus
• List of your referrals and their status

💡 *Useful information:*
• A referral is considered activated after registration, ID entry and deposit
• Progress updates automatically
• Bonuses can be claimed in the "Claim Bonus" section

🎯 *Tip:* Share your link on social media to attract more referrals!""",
        "th": """ที่นี่คุณสามารถติดตามความคืบหน้าในโปรแกรมแนะนำ

📈 *สถิติแสดงอะไร:*
• จำนวนคลิกบนลิงก์ของคุณ
• จำนวนการแนะนำที่เปิดใช้งาน
• ความคืบหน้าปัจจุบันสู่โบนัสถัดไป
• รายการการแนะนำของคุณและสถานะ

💡 *ข้อมูลที่เป็นประโยชน์:*
• การแนะนำจะถือว่าเปิดใช้งานหลังจากลงทะเบียน ป้อน ID และฝากเงิน
• ความคืบหน้าอัปเดตโดยอัตโนมัติ
• โบนัสสามารถรับได้ในส่วน "รับโบนัส"

🎯 *เคล็ดลับ:* แชร์ลิงก์ของคุณบนโซเชียลมีเดียเพื่อดึงดูดการแนะนำมากขึ้น!""",
        "es": """Aquí puedes rastrear tu progreso en el programa de referidos.

📈 *Qué muestran las estadísticas:*
• Número de clics en tu enlace
• Número de referidos activados
• Progreso actual hacia el siguiente bono
• Lista de tus referidos y su estado

💡 *Información útil:*
• Un referido se considera activado después del registro, ingreso de ID y depósito
• El progreso se actualiza automáticamente
• Los bonos se pueden reclamar en la sección "Reclamar Bono"

🎯 *Consejo:* ¡Comparte tu enlace en redes sociales para atraer más referidos!""",
        "ar": """هنا يمكنك تتبع تقدمك في برنامج الإحالة.

📈 *ما تظهره الإحصائيات:*
• عدد النقرات على رابطك
• عدد الإحالات المفعلة
• التقدم الحالي نحو المكافأة التالية
• قائمة إحالاتك وحالتها

💡 *معلومات مفيدة:*
• تعتبر الإحالة مفعلة بعد التسجيل وإدخال المعرف والإيداع
• يتم تحديث التقدم تلقائياً
• يمكن المطالبة بالمكافآت في قسم "المطالبة بالمكافأة"

🎯 *نصيحة:* شارك رابطك على وسائل التواصل الاجتماعي لجذب المزيد من الإحالات!""",
        "uk": """Тут ви можете відстежувати свій прогрес у реферальній програмі.

📈 *Що показує статистика:*
• Кількість переходів за вашим посиланням
• Кількість активованих рефералів
• Поточний прогрес до наступного бонусу
• Список ваших рефералів та їх статус

💡 *Корисна інформація:*
• Реферал вважається активованим після реєстрації, введення ID та депозиту
• Прогрес оновлюється автоматично
• Бонуси можна отримати в розділі "Забрати бонус"

🎯 *Порада:* Поділіться своїм посиланням у соціальних мережах для залучення більшої кількості рефералів!""",
    },
    
    "referral_stats_active_subscription": {
        "ru": "🎫 Активная подписка:",
        "en": "🎫 Active subscription:",
        "th": "🎫 การสมัครสมาชิกที่ใช้งานอยู่:",
        "es": "🎫 Suscripción activa:",
        "ar": "🎫 الاشتراك النشط:",
        "uk": "🎫 Активна підписка:",
    },
    
    "referral_stats_no_subscription": {
        "ru": "🎫 Подписка: нет активной",
        "en": "🎫 Subscription: none active",
        "th": "🎫 การสมัครสมาชิก: ไม่มีที่ใช้งานอยู่",
        "es": "🎫 Suscripción: ninguna activa",
        "ar": "🎫 الاشتراك: لا يوجد نشط",
        "uk": "🎫 Підписка: немає активної",
    },
    
    "referral_stats_clicks": {
        "ru": "👥 Переходов по ссылке:",
        "en": "👥 Link clicks:",
        "th": "👥 คลิกลิงก์:",
        "es": "👥 Clics en enlace:",
        "ar": "👥 نقرات الرابط:",
        "uk": "👥 Переходів по силці:",
    },
    
    "referral_stats_activated": {
        "ru": "✅ Активировано рефералов:",
        "en": "✅ Activated referrals:",
        "th": "✅ การแนะนำที่เปิดใช้งาน:",
        "es": "✅ Referidos activados:",
        "ar": "✅ الإحالات المفعلة:",
        "uk": "✅ Активовано рефералів:",
    },
    
    "referral_stats_your_referrals": {
        "ru": "👤 Твои рефералы:",
        "en": "👤 Your referrals:",
        "th": "👤 การแนะนำของคุณ:",
        "es": "👤 Tus referidos:",
        "ar": "👤 إحالاتك:",
        "uk": "👤 Твої реферали:",
    },
    
    "referral_stats_and_more": {
        "ru": "...и ещё {count}",
        "en": "...and {count} more",
        "th": "...และอีก {count}",
        "es": "...y {count} más",
        "ar": "...و {count} آخرين",
        "uk": "...и ещё {count}",
    },
    
    "referral_subscription_start": {
        "ru": "📅 Начало:",
        "en": "📅 Start:",
        "th": "📅 เริ่มต้น:",
        "es": "📅 Inicio:",
        "ar": "📅 البداية:",
        "uk": "📅 Начало:",
    },
    
    "referral_subscription_expired": {
        "ru": "⚠️ Подписка истекла",
        "en": "⚠️ Subscription expired",
        "th": "⚠️ การสมัครสมาชิกหมดอายุ",
        "es": "⚠️ Suscripción expirada",
        "ar": "⚠️ انتهى الاشتراك",
        "uk": "⚠️ Підписка закінчилася",
    },
    
    "referral_subscription_remaining_days": {
        "ru": "⏰ Осталось: {days} дн.",
        "en": "⏰ Remaining: {days} days",
        "th": "⏰ เหลือ: {days} วัน",
        "es": "⏰ Restante: {days} días",
        "ar": "⏰ المتبقي: {days} أيام",
        "uk": "⏰ Залишилося: {days} дн.",
    },
    
    "referral_subscription_remaining_hours": {
        "ru": "⏰ Осталось: {hours} ч.",
        "en": "⏰ Remaining: {hours} h.",
        "th": "⏰ เหลือ: {hours} ชม.",
        "es": "⏰ Restante: {hours} h.",
        "ar": "⏰ المتبقي: {hours} س.",
        "uk": "⏰ Залишилося: {hours} год.",
    },
    
    "referral_subscription_unlimited": {
        "ru": "⏰ Бессрочно",
        "en": "⏰ Unlimited",
        "th": "⏰ ไม่จำกัด",
        "es": "⏰ Ilimitado",
        "ar": "⏰ غير محدود",
        "uk": "⏰ Бессрочно",
    },
    
    "referral_bonus_blocked_title": {
        "ru": "⚠️ У вас уже есть активная подписка!",
        "en": "⚠️ You already have an active subscription!",
        "th": "⚠️ คุณมีการสมัครสมาชิกที่ใช้งานอยู่แล้ว!",
        "es": "⚠️ ¡Ya tienes una suscripción activa!",
        "ar": "⚠️ لديك اشتراك نشط بالفعل!",
        "uk": "⚠️ У вас вже є активна підписка!",
    },
    
    "referral_bonus_blocked_available": {
        "ru": "📋 Доступные бонусы после окончания:",
        "en": "📋 Available bonuses after expiration:",
        "th": "📋 โบนัสที่สามารถใช้ได้หลังหมดอายุ:",
        "es": "📋 Bonos disponibles después del vencimiento:",
        "ar": "📋 المكافآت المتاحة بعد انتهاء الصلاحية:",
        "uk": "📋 Доступные бонусы после окончания:",
    },
    
    "days": {
        "ru": "дней",
        "en": "days",
        "th": "วัน",
        "es": "días",
        "ar": "أيام",
        "uk": "днів",
    },
    
    "referral_your_link": {
        "ru": "🔗 Твоя реферальная ссылка:",
        "en": "🔗 Your referral link:",
        "th": "🔗 ลิงก์แนะนำของคุณ:",
        "es": "🔗 Tu enlace de referido:",
        "ar": "🔗 رابط الإحالة الخاص بك:",
        "uk": "🔗 Твоя реферальна посилання:",
    },
    
    "referral_progress": {
        "ru": "🎯 Прогресс:",
        "en": "🎯 Progress:",
        "th": "🎯 ความคืบหน้า:",
        "es": "🎯 Progreso:",
        "ar": "🎯 التقدم:",
        "uk": "🎯 Прогресс:",
    },
    
    "referral_until_mentorship": {
        "ru": "📈 До Менторства осталось: {remaining} друзей",
        "en": "📈 Until Mentorship: {remaining} friends left",
        "th": "📈 จนถึงการให้คำปรึกษา: เหลืออีก {remaining} เพื่อน",
        "es": "📈 Hasta Mentoría: faltan {remaining} amigos",
        "ar": "📈 حتى الإرشاد: متبقي {remaining} أصدقاء",
        "uk": "📈 До Менторства залишилося: {remaining} друзів",
    },
    
    "referral_until_subscription": {
        "ru": "📈 До {days} дней подписки осталось: {remaining} друзей",
        "en": "📈 Until {days} days subscription: {remaining} friends left",
        "th": "📈 จนถึงการสมัครสมาชิก {days} วัน: เหลืออีก {remaining} เพื่อน",
        "es": "📈 Hasta suscripción de {days} días: faltan {remaining} amigos",
        "ar": "📈 حتى اشتراك {days} أيام: متبقي {remaining} أصدقاء",
        "uk": "📈 До {days} днів підписки залишилося: {remaining} друзів",
    },
    
    "btn_referral_rules": {
        "ru": "📜 Правила программы",
        "en": "📜 Program rules",
        "th": "📜 กฎโปรแกรม",
        "es": "📜 Reglas del programa",
        "ar": "📜 قواعد البرنامج",
        "uk": "📜 Правила програми",
    },
    
    "btn_referral_menu": {
        "ru": "👥 Мои рефералы",
        "en": "👥 My referrals",
        "th": "👥 การแนะนำของฉัน",
        "es": "👥 Mis referidos",
        "ar": "👥 إحالاتي",
        "uk": "👥 Мои реферали",
    },
    
    "referral_share_text": {
        "ru": "🔥 Присоединяйся к нашей команде трейдеров! Регистрируйся по ссылке выше 👆",
        "en": "🔥 Join our trading team! Register via link above 👆",
        "th": "🔥 เข้าร่วมทีมเทรดเดอร์ของเรา! ลงทะเบียนผ่านลิงก์ด้านบน 👆",
        "es": "🔥 ¡Únete a nuestro equipo de trading! Regístrate por el enlace arriba 👆",
        "ar": "🔥 انضم لفريق التداول! سجل عبر الرابط أعلاه 👆",
        "uk": "🔥 Присоединяйся к нашей команде трейдеров! Регистрируйся по ссылке выше 👆",
    },
    
    "referral_link_copied": {
        "ru": "✅ Ссылка скопирована! Отправьте её друзьям",
        "en": "✅ Link copied! Send it to friends",
        "th": "✅ คัดลอกลิงก์แล้ว! ส่งให้เพื่อน",
        "es": "✅ ¡Enlace copiado! Envíalo a amigos",
        "ar": "✅ تم نسخ الرابط! أرسله للأصدقاء",
        "uk": "✅ Посилання скопійовано! Відправте її друзям",
    },
    
    "referral_rules_title": {
        "ru": "📜 *ПРАВИЛА РЕФЕРАЛЬНОЙ ПРОГРАММЫ*",
        "en": "📜 *REFERRAL PROGRAM RULES*",
        "th": "📜 *กฎโปรแกรมแนะนำ*",
        "es": "📜 *REGLAS DEL PROGRAMA DE REFERIDOS*",
        "ar": "📜 *قواعد برنامج الإحالة*",
        "uk": "📜 *ПРАВИЛА РЕФЕРАЛЬНОЇ ПРОГРАМИ*",
    },
    
    "referral_rules_text": {
        "ru": "*Как это работает:*\n\n1️⃣ Поделись своей уникальной ссылкой с друзьями\n2️⃣ Друг регистрируется по твоей ссылке и начинает торговать\n3️⃣ Друг засчитывается в твою статистику\n4️⃣ Достигни уровня и забери бонус — подписку на индикатор Black Mirror Ultra!\n\n*Условия участия в программе:*\n• Для участия достаточно быть подписанным на канал\n• Приглашай друзей по своей реферальной ссылке\n\n*Условия засчитывания друга:*\n• Регистрация по твоей ссылке\n• Ввод Pocket Option ID в боте\n• Пополнение счёта от $50\n\n*🏆 Система бонусов:*\n• 2 друга → Неделя подписки на индикатор\n• 5 друзей → Месяц подписки\n• 10 друзей → 🔥 Софт + Менторство!\n\n*💡 Развивайтесь вместе — зарабатывайте вместе!*",
        "en": "*How it works:*\n\n1️⃣ Share your unique link with friends\n2️⃣ Friend registers via your link and starts trading\n3️⃣ Friend is counted in your stats\n4️⃣ Reach the level and claim bonus — Black Mirror Ultra indicator subscription!\n\n*Program participation conditions:*\n• To participate, just subscribe to the channel\n• Invite friends using your referral link\n\n*Friend activation conditions:*\n• Registration via your link\n• Enter Pocket Option ID in the bot\n• Account deposit from $50\n\n*🏆 Bonus system:*\n• 2 friends → 1 week subscription\n• 5 friends → 1 month subscription\n• 10 friends → 🔥 Software + Mentorship!\n\n*💡 Grow together — earn together!*",
        "th": "*มันทำงานอย่างไร:*\n\n1️⃣ แชร์ลิงก์เฉพาะของคุณกับเพื่อน\n2️⃣ เพื่อนลงทะเบียนผ่านลิงก์ของคุณและเริ่มเทรด\n3️⃣ เพื่อนถูกนับในสถิติของคุณ\n4️⃣ ถึงระดับและรับโบนัส — การสมัครสมาชิก Black Mirror Ultra!\n\n*เงื่อนไขการเข้าร่วมโปรแกรม:*\n• สำหรับการเข้าร่วม เพียงสมัครสมาชิกช่อง\n• เชิญเพื่อนโดยใช้ลิงก์แนะนำของคุณ\n\n*เงื่อนไขการเปิดใช้งานเพื่อน:*\n• ลงทะเบียนผ่านลิงก์ของคุณ\n• ป้อน Pocket Option ID ในบอท\n• ฝากเงินในบัญชีตั้งแต่ $50\n\n*🏆 ระบบโบนัส:*\n• 2 เพื่อน → 1 สัปดาห์\n• 5 เพื่อน → 1 เดือน\n• 10 เพื่อน → 🔥 ซอฟต์แวร์ + เมนเทอร์!\n\n*💡 เติบโตด้วยกัน — หารายได้ด้วยกัน!*",
        "es": "*Cómo funciona:*\n\n1️⃣ Comparte tu enlace único con amigos\n2️⃣ El amigo se registra por tu enlace y empieza a operar\n3️⃣ El amigo cuenta en tus estadísticas\n4️⃣ ¡Alcanza el nivel y reclama el bono — suscripción al indicador Black Mirror Ultra!\n\n*Condiciones de participación en el programa:*\n• Para participar, solo suscríbete al canal\n• Invita amigos usando tu enlace de referido\n\n*Condiciones de activación del amigo:*\n• Registro vía tu enlace\n• Ingresar Pocket Option ID en el bot\n• Depósito en cuenta desde $50\n\n*🏆 Sistema de bonos:*\n• 2 amigos → 1 semana de suscripción\n• 5 amigos → 1 mes de suscripción\n• 10 amigos → 🔥 ¡Software + Mentoría!\n\n*💡 ¡Crezcan juntos — ganen juntos!*",
        "ar": "*كيف يعمل:*\n\n1️⃣ شارك رابطك الفريد مع الأصدقاء\n2️⃣ الصديق يسجل عبر رابطك ويبدأ التداول\n3️⃣ يتم حساب الصديق في إحصائياتك\n4️⃣ اصل للمستوى واستلم المكافأة — اشتراك مؤشر Black Mirror Ultra!\n\n*شروط المشاركة في البرنامج:*\n• للمشاركة، فقط اشترك في القناة\n• ادعو الأصدقاء باستخدام رابط الإحالة الخاص بك\n\n*شروط تفعيل الصديق:*\n• التسجيل عبر رابطك\n• إدخال Pocket Option ID في البوت\n• إيداع في الحساب من 50$\n\n*🏆 نظام المكافآت:*\n• 2 أصدقاء → أسبوع اشتراك\n• 5 أصدقاء → شهر اشتراك\n• 10 أصدقاء → 🔥 برنامج + إرشاد!\n\n*💡 انموا معاً — اكسبوا معاً!*",
        "uk": "*Як це працює:*\n\n1️⃣ Поділися своєю унікальною посиланням з друзями\n2️⃣ Друг реєструється за твоєю посиланням та починає торгувати\n3️⃣ Друг зараховується до твоєї статистики\n4️⃣ Досягни рівня та забери бонус — підписку на індикатор Black Mirror Ultra!\n\n*Умови участі в програмі:*\n• Для участі достатньо бути підписаним на канал\n• Запрошуй друзів за своєю реферальною посиланням\n\n*Умови зарахування друга:*\n• Реєстрація за твоєю посиланням\n• Введення Pocket Option ID в боті\n• Поповнення рахунка від $50\n\n*🏆 Система бонусів:*\n• 2 друга → Тиждень підписки на індикатор\n• 5 друзів → Місяць підписки\n• 10 друзів → 🔥 Софт + Менторство!\n\n*💡 Розвивайтесь разом — заробляйте разом!*",
    },
    
    "referral_no_bonus_available": {
        "ru": "❌ *Нет доступных бонусов*\n\nПригласите больше друзей чтобы разблокировать награды!",
        "en": "❌ *No bonuses available*\n\nInvite more friends to unlock rewards!",
        "th": "❌ *ไม่มีโบนัสที่สามารถใช้ได้*\n\nเชิญเพื่อนเพิ่มเติมเพื่อปลดล็อกรางวัล!",
        "es": "❌ *No hay bonos disponibles*\n\n¡Invita más amigos para desbloquear recompensas!",
        "ar": "❌ *لا توجد مكافآت متاحة*\n\nادعو المزيد من الأصدقاء لفتح المكافآت!",
        "uk": "❌ *Немає доступных бонусів*\n\nПригласите больше друзів щобы разблокировать награды!",
    },
    
    "referral_select_bonus": {
        "ru": "🎁 *Выберите бонус для получения:*",
        "en": "🎁 *Select bonus to claim:*",
        "th": "🎁 *เลือกโบนัสที่จะรับ:*",
        "es": "🎁 *Selecciona el bono a reclamar:*",
        "ar": "🎁 *اختر المكافأة للاستلام:*",
        "uk": "🎁 *Оберіть бонус для отримання:*",
    },
    
    "referral_enter_tv_username": {
        "ru": "📊 *Введите ваш username в TradingView:*\n\nЭто нужно для выдачи доступа к индикатору.\n\nПример: `your_username`",
        "en": "📊 *Enter your TradingView username:*\n\nThis is needed to grant indicator access.\n\nExample: `your_username`",
        "th": "📊 *ป้อนชื่อผู้ใช้ TradingView ของคุณ:*\n\nจำเป็นสำหรับการให้สิทธิ์เข้าถึงตัวบ่งชี้\n\nตัวอย่าง: `your_username`",
        "es": "📊 *Ingresa tu nombre de usuario de TradingView:*\n\nEsto es necesario para otorgar acceso al indicador.\n\nEjemplo: `your_username`",
        "ar": "📊 *أدخل اسم المستخدم الخاص بك في TradingView:*\n\nهذا ضروري لمنح الوصول إلى المؤشر.\n\nمثال: `your_username`",
        "uk": "📊 *Введите ваш username в TradingView:*\n\nЭто нужно для выдачи доступа к индикатору.\n\nПример: `your_username`",
    },
    
    "btn_cancel": {
        "ru": "❌ Отмена",
        "en": "❌ Cancel",
        "th": "❌ ยกเลิก",
        "es": "❌ Cancelar",
        "ar": "❌ إلغاء",
        "uk": "❌ Скасування",
    },
    
    "referral_bonus_approved": {
        "ru": "🎉 *ПОЗДРАВЛЯЕМ!*\n\n✅ Ваша заявка на бонус одобрена!\n\n📊 Доступ к индикатору TradingView будет предоставлен в ближайшее время.\n\n👨‍💼 По вопросам: @kaktotakxm",
        "en": "🎉 *CONGRATULATIONS!*\n\n✅ Your bonus request is approved!\n\n📊 TradingView indicator access will be granted soon.\n\n👨‍💼 Questions: @kaktotakxm",
        "th": "🎉 *ยินดีด้วย!*\n\n✅ คำขอโบนัสของคุณได้รับการอนุมัติแล้ว!\n\n📊 การเข้าถึงตัวบ่งชี้ TradingView จะได้รับในเร็วๆ นี้\n\n👨‍💼 คำถาม: @kaktotakxm",
        "es": "🎉 *¡FELICITACIONES!*\n\n✅ ¡Tu solicitud de bono está aprobada!\n\n📊 El acceso al indicador TradingView se otorgará pronto.\n\n👨‍💼 Preguntas: @kaktotakxm",
        "ar": "🎉 *تهانينا!*\n\n✅ تمت الموافقة على طلب المكافأة الخاص بك!\n\n📊 سيتم منح الوصول إلى مؤشر TradingView قريبًا.\n\n👨‍💼 أسئلة: @kaktotakxm",
        "uk": "🎉 *ПОЗДРАВЛЯЕМ!*\n\n✅ Ваша заявка на бонус одобрена!\n\n📊 Доступ к индикатору TradingView будет предоставлен в ближайшее время.\n\n👨‍💼 По питанняам: @kaktotakxm",
    },
    
    "referral_bonus_rejected": {
        "ru": "❌ *Заявка отклонена*\n\nВаша заявка на бонус была отклонена.\n\nЕсли у вас есть вопросы, свяжитесь с: @kaktotakxm",
        "en": "❌ *Request rejected*\n\nYour bonus request was rejected.\n\nIf you have questions, contact: @kaktotakxm",
        "th": "❌ *คำขอถูกปฏิเสธ*\n\nคำขอโบนัสของคุณถูกปฏิเสธ\n\nหากมีคำถาม ติดต่อ: @kaktotakxm",
        "es": "❌ *Solicitud rechazada*\n\nTu solicitud de bono fue rechazada.\n\nSi tienes preguntas, contacta: @kaktotakxm",
        "ar": "❌ *تم رفض الطلب*\n\nتم رفض طلب المكافأة الخاص بك.\n\nإذا كانت لديك أسئلة، اتصل بـ: @kaktotakxm",
        "uk": "❌ *Заявка відхилена*\n\nВаша заявка на бонус була відхилена.\n\nЯкщо у вас є питання, зв'яжіться з: @kaktotakxm",
    },
    
    "referral_new_click": {
        "ru": "👋 *Новый переход по вашей ссылке!*\n\nПользователь @{username} перешёл по вашей реферальной ссылке.\n\nКогда он зарегистрируется и пополнит счёт, он будет засчитан!",
        "en": "👋 *New click on your link!*\n\nUser @{username} clicked your referral link.\n\nWhen they register and deposit, they will be counted!",
        "th": "👋 *มีคนคลิกลิงก์ของคุณ!*\n\nผู้ใช้ @{username} คลิกลิงก์แนะนำของคุณ\n\nเมื่อพวกเขาลงทะเบียนและฝากเงิน พวกเขาจะถูกนับ!",
        "es": "👋 *¡Nuevo clic en tu enlace!*\n\nEl usuario @{username} hizo clic en tu enlace de referido.\n\n¡Cuando se registre y deposite, será contado!",
        "ar": "👋 *نقرة جديدة على رابطك!*\n\nالمستخدم @{username} نقر على رابط الإحالة الخاص بك.\n\nعندما يسجل ويودع، سيتم حسابه!",
        "uk": "👋 *Новый переход по вашей ссылке!*\n\nПользователь @{username} перешёл по вашей реферальной ссылке.\n\nКогда он зареєструється и пополнит счёт, он будет засчитан!",
    },
    
    "referral_bonus_available": {
        "ru": "🎁 *У вас есть доступный бонус!* Нажмите 'Забрать бонус' в меню рефералов.",
        "en": "🎁 *You have an available bonus!* Click 'Claim bonus' in referral menu.",
        "th": "🎁 *คุณมีโบนัสที่สามารถใช้ได้!* คลิก 'รับโบนัส' ในเมนูแนะนำ",
        "es": "🎁 *¡Tienes un bono disponible!* Haz clic en 'Reclamar bono' en el menú de referidos.",
        "ar": "🎁 *لديك مكافأة متاحة!* انقر على 'استلام المكافأة' في قائمة الإحالة.",
        "uk": "🎁 *У вас є доступний бонус!* Натисніть 'Забрати бонус' в меню рефералів.",
    },
    
    "referral_friend_activated": {
        "ru": "🎉 *Отличные новости!*\n\nВаш друг @{username} выполнил все условия и засчитан как реферал!\n\n📊 Ваш прогресс: {progress}\n\nПродолжайте приглашать друзей!",
        "en": "🎉 *Great news!*\n\nYour friend @{username} completed all conditions and counted as referral!\n\n📊 Your progress: {progress}\n\nKeep inviting friends!",
        "th": "🎉 *ข่าวดี!*\n\nเพื่อนของคุณ @{username} ทำตามเงื่อนไขครบแล้วและนับเป็นผู้แนะนำ!\n\n📊 ความคืบหน้าของคุณ: {progress}\n\nเชิญเพื่อนต่อไป!",
        "es": "🎉 *¡Grandes noticias!*\n\nTu amigo @{username} cumplió todas las condiciones y fue contado como referido!\n\n📊 Tu progreso: {progress}\n\n¡Sigue invitando amigos!",
        "ar": "🎉 *أخبار رائعة!*\n\nصديقك @{username} أكمل جميع الشروط وتم احتسابه كإحالة!\n\n📊 تقدمك: {progress}\n\nواصل دعوة الأصدقاء!",
        "uk": "🎉 *Отличные новости!*\n\nВаш друг @{username} выполнил всі умови и засчитан як реферал!\n\n📊 Ваш прогресс: {progress}\n\nПродолжайте приглашать друзів!",
    },
    
    "referral_bonus_request_sent": {
        "ru": "✅ *Заявка отправлена!*\n\nВаша заявка на бонус отправлена администратору на рассмотрение.\n\nОжидайте уведомления!",
        "en": "✅ *Request sent!*\n\nYour bonus request has been sent to admin for review.\n\nWait for notification!",
        "th": "✅ *ส่งคำขอแล้ว!*\n\nคำขอโบนัสของคุณถูกส่งไปยังผู้ดูแลระบบเพื่อตรวจสอบ\n\nรอการแจ้งเตือน!",
        "es": "✅ *¡Solicitud enviada!*\n\nTu solicitud de bono ha sido enviada al administrador para revisión.\n\n¡Espera la notificación!",
        "ar": "✅ *تم إرسال الطلب!*\n\nتم إرسال طلب المكافأة الخاص بك إلى المسؤول للمراجعة.\n\nانتظر الإشعار!",
        "uk": "✅ *Заявка відправлена!*\n\nВаша заявка на бонус відправлена адміністратору на розгляд.\n\nОчікуйте сповіщення!",
    },
    
    "referral_bonus_approved_mentorship": {
        "ru": "🎉 *ПОЗДРАВЛЯЕМ!*\n\nВы получили доступ к *Менторству + Софту*!\n\n✅ Вам будет предоставлен доступ к индикатору Black Mirror Ultra\n\n📞 Для обсуждения деталей менторства и получения поддержки, пожалуйста, напишите:",
        "en": "🎉 *CONGRATULATIONS!*\n\nYou have received access to *Mentorship + Software*!\n\n✅ You will be granted access to Black Mirror Ultra indicator\n\n📞 To discuss mentorship details and get support, please contact:",
        "th": "🎉 *ยินดีด้วย!*\n\nคุณได้รับสิทธิ์เข้าถึง *การให้คำปรึกษา + ซอฟต์แวร์*!\n\n✅ คุณจะได้รับสิทธิ์เข้าถึงตัวบ่งชี้ Black Mirror Ultra\n\n📞 เพื่อหารือรายละเอียดการให้คำปรึกษาและรับการสนับสนุน โปรดติดต่อ:",
        "es": "🎉 *¡FELICITACIONES!*\n\n¡Has recibido acceso a *Mentoría + Software*!\n\n✅ Se te otorgará acceso al indicador Black Mirror Ultra\n\n📞 Para discutir los detalles de la mentoría y obtener soporte, por favor contacta:",
        "ar": "🎉 *تهانينا!*\n\nلقد حصلت على وصول إلى *الإرشاد + البرنامج*!\n\n✅ سيتم منحك وصولاً إلى مؤشر Black Mirror Ultra\n\n📞 لمناقشة تفاصيل الإرشاد والحصول على الدعم، يرجى التواصل:",
        "uk": "🎉 *ПОЗДРАВЛЯЕМ!*\n\nВы отримайли доступ к *Менторству + Софту*!\n\n✅ Вам будет предоставлен доступ к индикатору Black Mirror Ultra\n\n📞 Для обсуждения деталей менторства и отримання поддержки, пожалуйста, напишіть:",
    },
    
    "btn_contact_admin": {
        "ru": "✍️ Написать",
        "en": "✍️ Contact",
        "th": "✍️ ติดต่อ",
        "es": "✍️ Contactar",
        "ar": "✍️ تواصل",
        "uk": "✍️ Написать",
    },
    
    # Проверка подписки на канал
    "subscription_required_title": {
        "ru": "**Упс...**",
        "en": "**Oops...**",
        "th": "**อ๊ะ...**",
        "es": "**Ups...**",
        "ar": "**عذراً...**",
        "uk": "**Упс...**",
    },
    
    "subscription_required_text": {
        "ru": "**Для получения доступа к академии и форуму подпишитесь на главный канал:**",
        "en": "**To gain access to the academy and forum, please subscribe to the main channel:**",
        "th": "**หากต้องการเข้าถึงสถาบันและฟอรัม โปรดสมัครรับข้อมูลช่องหลัก:**",
        "es": "**Para obtener acceso a la academia y al foro, por favor suscríbete al canal principal:**",
        "ar": "**للوصول إلى الأكاديمية والمنتدى، يرجى الاشتراك في القناة الرئيسية:**",
        "uk": "**Для отримання доступу до академії та форуму підпишіться на головний канал:**",
    },
    
    "btn_subscribe": {
        "ru": "📢 Подписаться на канал",
        "en": "📢 Subscribe to Channel",
        "th": "📢 สมัครรับข้อมูลช่อง",
        "es": "📢 Suscribirse al Canal",
        "ar": "📢 الاشتراك في القناة",
        "uk": "📢 Підписатися на канал",
    },
    
    # Меню промокодов
    "promocodes_menu_title": {
        "ru": "🎁 *Промокоды*",
        "en": "🎁 *Promo Codes*",
        "th": "🎁 *รหัสโปรโมชั่น*",
        "es": "🎁 *Códigos Promocionales*",
        "ar": "🎁 *رموز ترويجية*",
        "uk": "🎁 *Промокоди*",
    },
    
    "promocodes_menu_description": {
        "ru": """Выберите промокод для получения бонуса при регистрации и пополнении счета.

💎 *Преимущества промокодов:*
• Дополнительный бонус к вашему депозиту
• Быстрый старт с увеличенным балансом
• Максимальная выгода от первого пополнения

🚀 *Как использовать:*
1. Выберите подходящий промокод
2. Перейдите по ссылке для регистрации
3. Введите промокод при пополнении счета
4. Получите бонус на свой баланс

✨ Используйте промокод при первом депозите для максимальной выгоды!""",
        "en": """Choose a promo code to get a bonus when registering and depositing.

💎 *Promo code benefits:*
• Additional bonus to your deposit
• Quick start with increased balance
• Maximum benefit from first deposit

🚀 *How to use:*
1. Choose a suitable promo code
2. Follow the link to register
3. Enter the promo code when depositing
4. Get bonus to your balance

✨ Use the promo code on your first deposit for maximum benefit!""",
        "th": """เลือกรหัสโปรโมชั่นเพื่อรับโบนัสเมื่อลงทะเบียนและฝากเงิน

💎 *ข้อดีของรหัสโปรโมชั่น:*
• โบนัสเพิ่มเติมสำหรับการฝากเงินของคุณ
• เริ่มต้นอย่างรวดเร็วด้วยยอดเงินที่เพิ่มขึ้น
• ประโยชน์สูงสุดจากการฝากเงินครั้งแรก

🚀 *วิธีใช้:*
1. เลือกรหัสโปรโมชั่นที่เหมาะสม
2. ไปที่ลิงก์เพื่อลงทะเบียน
3. ป้อนรหัสโปรโมชั่นเมื่อฝากเงิน
4. รับโบนัสในยอดเงินของคุณ

✨ ใช้รหัสโปรโมชั่นในการฝากเงินครั้งแรกเพื่อประโยชน์สูงสุด!""",
        "es": """Elige un código promocional para obtener un bono al registrarte y depositar.

💎 *Beneficios del código promocional:*
• Bono adicional a tu depósito
• Inicio rápido con saldo aumentado
• Máximo beneficio del primer depósito

🚀 *Cómo usar:*
1. Elige un código promocional adecuado
2. Sigue el enlace para registrarte
3. Ingresa el código al depositar
4. Recibe el bono en tu saldo

✨ ¡Usa el código promocional en tu primer depósito para máximo beneficio!""",
        "ar": """اختر رمزًا ترويجيًا للحصول على مكافأة عند التسجيل والإيداع.

💎 *فوائد الرمز الترويجي:*
• مكافأة إضافية لإيداعك
• بداية سريعة برصيد متزايد
• أقصى استفادة من الإيداع الأول

🚀 *كيفية الاستخدام:*
1. اختر رمزًا ترويجيًا مناسبًا
2. اتبع الرابط للتسجيل
3. أدخل الرمز عند الإيداع
4. احصل على المكافأة في رصيدك

✨ استخدم الرمز الترويجي في إيداعك الأول للحصول على أقصى فائدة!""",
        "uk": """Виберіть промокод для отримання бонусу при реєстрації та поповненні рахунку.

💎 *Переваги промокодів:*
• Додатковий бонус до вашого депозиту
• Швидкий старт зі збільшеним балансом
• Максимальна вигода від першого поповнення

🚀 *Як використовувати:*
1. Виберіть підходящий промокод
2. Перейдіть за посиланням для реєстрації
3. Введіть промокод при поповненні рахунку
4. Отримайте бонус на свій баланс

✨ Використовуйте промокод при першому депозиті для максимальної вигоди!""",
    },
    
    "btn_promocodes": {
        "ru": "🎁 Промокоды",
        "en": "🎁 Promo Codes",
        "th": "🎁 รหัสโปรโมชั่น",
        "es": "🎁 Códigos Promocionales",
        "ar": "🎁 رموز ترويجية",
        "uk": "🎁 Промокоди",
    },
    
    "btn_pocketoptions": {
        "ru": "🌐 PocketOptions (Торгуем Здесь)",
        "en": "🌐 PocketOptions (Trade Here)",
        "th": "🌐 PocketOptions (เทรดที่นี่)",
        "es": "🌐 PocketOptions (Opera Aquí)",
        "ar": "🌐 PocketOptions (تداول هنا)",
        "uk": "🌐 PocketOptions (Торгуємо Тут)",
    },
    
    "btn_blackmirror_ultra": {
        "ru": "📊 BlackMirror ULTRA (TradingView)",
        "en": "📊 BlackMirror ULTRA (TradingView)",
        "th": "📊 BlackMirror ULTRA (TradingView)",
        "es": "📊 BlackMirror ULTRA (TradingView)",
        "ar": "📊 BlackMirror ULTRA (TradingView)",
        "uk": "📊 BlackMirror ULTRA (TradingView)",
    },
    
    "promocode_1_title": {
        "ru": "+50% мин. депозит 20$",
        "en": "+50% min. deposit $20",
        "th": "+50% ฝากขั้นต่ำ $20",
        "es": "+50% depósito mín. $20",
        "ar": "+50% الحد الأدنى للإيداع 20$",
        "uk": "+50% мін. депозит 20$",
    },
    
    "promocode_1_description": {
        "ru": "Бонус +50% к первому депозиту от 20$",
        "en": "Bonus +50% to first deposit from $20",
        "th": "โบนัส +50% สำหรับการฝากครั้งแรกตั้งแต่ $20",
        "es": "Bono +50% al primer depósito desde $20",
        "ar": "مكافأة +50% للإيداع الأول من 20$",
        "uk": "Бонус +50% до першого депозиту від 20$",
    },
    
    "promocode_2_title": {
        "ru": "+50% мин. депозит 50$",
        "en": "+50% min. deposit $50",
        "th": "+50% ฝากขั้นต่ำ $50",
        "es": "+50% depósito mín. $50",
        "ar": "+50% الحد الأدنى للإيداع 50$",
        "uk": "+50% мін. депозит 50$",
    },
    
    "promocode_2_description": {
        "ru": "Бонус +50% к первому депозиту от 50$",
        "en": "Bonus +50% to first deposit from $50",
        "th": "โบนัส +50% สำหรับการฝากครั้งแรกตั้งแต่ $50",
        "es": "Bono +50% al primer depósito desde $50",
        "ar": "مكافأة +50% للإيداع الأول من 50$",
        "uk": "Бонус +50% до першого депозиту від 50$",
    },
    
    "promocode_3_title": {
        "ru": "+60% мин. депозит 50$",
        "en": "+60% min. deposit $50",
        "th": "+60% ฝากขั้นต่ำ $50",
        "es": "+60% depósito mín. $50",
        "ar": "+60% الحد الأدنى للإيداع 50$",
        "uk": "+60% мін. депозит 50$",
    },
    
    "promocode_3_description": {
        "ru": "Бонус +60% к первому депозиту от 50$",
        "en": "Bonus +60% to first deposit from $50",
        "th": "โบนัส +60% สำหรับการฝากครั้งแรกตั้งแต่ $50",
        "es": "Bono +60% al primer depósito desde $50",
        "ar": "مكافأة +60% للإيداع الأول من 50$",
        "uk": "Бонус +60% до першого депозиту від 50$",
    },
    
    "promocode_4_title": {
        "ru": "Промо от Дэнчика DENCHIK60",
        "en": "Promo from Denchik DENCHIK60",
        "th": "โปรโมชั่นจาก Denchik DENCHIK60",
        "es": "Promo de Denchik DENCHIK60",
        "ar": "عرض ترويجي من Denchik DENCHIK60",
        "uk": "Промо від Денчика DENCHIK60",
    },
    
    "promocode_4_description": {
        "ru": "Эксклюзивный промокод DENCHIK60",
        "en": "Exclusive promo code DENCHIK60",
        "th": "รหัสโปรโมชั่นพิเศษ DENCHIK60",
        "es": "Código promocional exclusivo DENCHIK60",
        "ar": "رمز ترويجي حصري DENCHIK60",
        "uk": "Ексклюзивний промокод DENCHIK60",
    },
    
    "promocode_5_title": {
        "ru": "Промо BlackMirror Ultra TEST",
        "en": "Promo BlackMirror Ultra TEST",
        "th": "โปรโมชั่น BlackMirror Ultra TEST",
        "es": "Promo BlackMirror Ultra TEST",
        "ar": "عرض ترويجي BlackMirror Ultra TEST",
        "uk": "Промо BlackMirror Ultra TEST",
    },
    
    "promocode_5_description": {
        "ru": "Тестовый промокод BlackMirror Ultra",
        "en": "Test promo code BlackMirror Ultra",
        "th": "รหัสโปรโมชั่นทดสอบ BlackMirror Ultra",
        "es": "Código promocional de prueba BlackMirror Ultra",
        "ar": "رمز ترويجي تجريبي BlackMirror Ultra",
        "uk": "Тестовий промокод BlackMirror Ultra",
    }
}


def t(key: str, lang: str = DEFAULT_LANGUAGE, **kwargs) -> str:
    """
    Получает перевод для указанного ключа и языка
    
    Args:
        key: Ключ перевода
        lang: Код языка (ru, en, th, es, ar)
        **kwargs: Параметры для форматирования строки
    
    Returns:
        Переведенная строка
    """
    # Проверяем валидность языка
    if lang not in LANGUAGES:
        lang = DEFAULT_LANGUAGE
    
    # Получаем перевод
    translation = TEXTS.get(key, {}).get(lang)
    
    # Если перевод не найден, используем английский как fallback
    if translation is None:
        translation = TEXTS.get(key, {}).get(DEFAULT_LANGUAGE, f"[{key}]")
    
    # Форматируем строку если есть параметры
    if kwargs:
        try:
            translation = translation.format(**kwargs)
        except (KeyError, ValueError):
            pass
    
    return translation


def get_user_language(user_id: int, users_db: Dict, telegram_lang: str = None) -> str:
    """
    Получает язык пользователя
    
    Args:
        user_id: ID пользователя
        users_db: База данных пользователей
        telegram_lang: Язык из Telegram профиля (опционально)
    
    Returns:
        Код языка
    """
    # Проверяем сохраненный язык пользователя (ключи могут быть int или str)
    if user_id in users_db and 'language' in users_db[user_id]:
        return users_db[user_id]['language']
    if str(user_id) in users_db and 'language' in users_db[str(user_id)]:
        return users_db[str(user_id)]['language']
    
    # Пытаемся использовать язык из Telegram профиля
    if telegram_lang:
        # Telegram возвращает языки в формате 'ru', 'en', 'th', 'es', 'ar' и т.д.
        if telegram_lang in LANGUAGES:
            return telegram_lang
    
    # Возвращаем язык по умолчанию
    return DEFAULT_LANGUAGE


def set_user_language(user_id: int, users_db: Dict, language: str) -> bool:
    """
    Устанавливает язык пользователя
    
    Args:
        user_id: ID пользователя
        users_db: База данных пользователей
        language: Код языка
    
    Returns:
        True если успешно, False если язык не поддерживается
    """
    if language not in LANGUAGES:
        return False
    
    # Проверяем оба варианта ключей (int и str)
    if user_id in users_db:
        users_db[user_id]['language'] = language
    elif str(user_id) in users_db:
        users_db[str(user_id)]['language'] = language
    else:
        users_db[user_id] = {'language': language}
    
    return True


def get_language_keyboard():
    """
    Создает клавиатуру выбора языка
    
    Returns:
        List[List[str]]: Список кнопок для InlineKeyboardMarkup
    """
    from telegram import InlineKeyboardButton
    
    buttons = []
    for lang_code, lang_info in LANGUAGES.items():
        button_text = f"{lang_info['flag']} {lang_info['name']}"
        buttons.append([InlineKeyboardButton(button_text, callback_data=f"lang_{lang_code}")])
    
    return buttons



