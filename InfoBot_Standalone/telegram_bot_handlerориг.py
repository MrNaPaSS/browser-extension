"""
TELEGRAM БОТ @info_xm_trust_bot
Система доступа к сигналам
"""

import asyncio
import logging
import json
import csv
import requests
import threading
import random
import urllib.parse
import http.server
import socketserver
from datetime import datetime, timedelta
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, WebAppInfo, ChatMemberUpdated
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, ChatMemberHandler, filters, ContextTypes
from telegram.error import TelegramError, BadRequest
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger

# Импорт системы мультиязычности
from i18n import t, get_user_language, set_user_language, get_language_keyboard, LANGUAGES, TEXTS

# Импорт реферальной системы
from referral_system import ReferralManager
from referral_config import REFERRAL_BONUS_LEVELS, get_next_bonus_level

# Настройка логирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

class InfoBot:
    """Бот для управления доступом к сигналам"""
    
    def __init__(self):
        self.bot_token = "8224525669:AAEr7omZHZ7LzDDAnpgx8VG-iM87ixYVGT4"
        self.referral_link = "https://u3.shortink.io/register?utm_campaign=827841&utm_source=affiliate&utm_medium=sr&a=CQQJpdvm2ya9dU&ac=tggg&code=50START"
        self.referral_code = "50START"
        self.min_deposit = 50
        self.admin_chat_id = "511442168"  # Ваш Telegram ID
        
        # Конфигурация канала для проверки подписки
        self.channel_username = "@NeKnopkaBabl0"  # Username канала для проверки подписки
        self.channel_url = "https://t.me/+avD8ncMHBp4zMzhi"  # Ссылка на канал для кнопки подписки
        
        # Путь к приветственному фото
        self.welcome_photo = "welcome.jpg"  # Файл должен быть в той же папке с ботом
        
        # База данных пользователей
        self.users_db_file = "info_bot_users.json"
        self.users_db = self._load_users_db()
        
        # Хранение ID последних сообщений бота для каждого пользователя (для удаления фото)
        self.user_last_messages = {}  # {user_id: [message_ids]}
        
        # Отслеживание повторных нажатий кнопки "Проверить доступ"
        self.access_check_history = {}  # {user_id: [timestamps]}
        self.max_repeated_checks = 3  # Максимум повторных проверок
        self.check_cooldown = 300  # 5 минут между проверками
        
        # Отслеживание рандомных сообщений
        self.random_message_history = {}  # {user_id: [timestamps]}
        self.random_message_cooldown = 300  # 5 минут между сообщениями
        
        # Система предупреждений о блокировке
        self.user_warnings = {}  # {user_id: warning_count}
        self.max_warnings = 2  # Максимум предупреждений перед блокировкой (1-е, 2-е)
        self.blocked_users = set()  # Заблокированные пользователи
        
        # История событий для администратора
        self.admin_events = []  # [{timestamp, event_type, user_id, description}]
        self.max_events = 50  # Максимум событий в истории
        
        # Данные рассылки
        self.broadcast_data = {}  # {admin_id: {content_type, content, audience, message_type}}
        self.failed_users_list = {}  # {admin_id: [user_ids]} - список неактивных пользователей для очистки
        
        # Защита от повторной отправки ID
        self.id_submission_count = {}  # {user_id: count}
        
        # Система мотивационных рассылок
        self.motivation_enabled = True  # Включить/выключить рассылки
        self.motivation_interval_hours = 48  # Интервал между рассылками (2 дня)
        self.motivation_min_interval_hours = 24  # Минимальный интервал (защита от спама)
        self.motivation_auto_enabled = False  # Автопланировщик выключен, только ручной запуск
        self.scheduler = None  # Планировщик задач
        self.application = None  # Ссылка на telegram Application
        
        # Реферальная система "Здравый Трейдер"
        self.referral_manager = ReferralManager(
            users_db=self.users_db,
            users_db_file=self.users_db_file,
            bot_username="moneyhoney7_bot"  # Основной бот
        )
        
        # Шаблоны мотивационных сообщений
        self.motivation_templates = [
            {
                "name": "bonus_reminder",
                "text": """
🎁 <b>ВЫ УПУСКАЕТЕ ДЕНЬГИ ПРЯМО СЕЙЧАС!</b>

Пока вы откладываете - другие уже зарабатывают по $500-1000 в день!

💰 <b>ВАШ ЭКСКЛЮЗИВНЫЙ БОНУС:</b>
• +50% БОНУС к депозиту (удвойте стартовый капитал!)
• Промокод: {promo_code}
• Всего от ${min_deposit} для старта

📊 <b>Профессиональные сигналы с точностью 80%+</b>
Более 500 успешных трейдеров уже с нами!

⏰ <b>НЕ ТЕРЯЙТЕ ВРЕМЯ - КАЖДАЯ МИНУТА НА СЧЕТУ!</b>

<a href="{referral_link}">💸 НАЧАТЬ ЗАРАБАТЫВАТЬ СЕЙЧАС →</a>

👨‍💻 Поддержка 24/7: @kaktotakxm
                """.strip()
            },
            {
                "name": "success_stories",
                "text": """
💰 <b>ПОКА ВЫ ДУМАЕТЕ - ДРУГИЕ ЗАРАБАТЫВАЮТ!</b>

Реальные результаты наших клиентов за последнюю неделю:

✅ dmitry_trade - +$2,450 за 5 дней
✅ maks_invest - +$1,920 за неделю  
✅ alexey_pro - +$3,200 за 4 дня

<b>ЭТО МОГЛИ БЫТЬ ВАШИ ДЕНЬГИ!</b>

🔥 <b>СКОЛЬКО ЕЩЁ ВЫ БУДЕТЕ ОТКЛАДЫВАТЬ?</b>
Каждый день промедления = упущенная прибыль!

🎁 <b>ЭКСКЛЮЗИВ:</b> +50% к депозиту | Промокод: {promo_code}

⚡ От ${min_deposit} - начните уже СЕГОДНЯ!

<a href="{referral_link}">💸 ЗАБРАТЬ СВОЮ ПРИБЫЛЬ →</a>

<b>Не дайте другим забрать ваши деньги!</b>
                """.strip()
            },
            {
                "name": "limited_offer",
                "text": """
🚨 <b>СРОЧНО! ПРЕДЛОЖЕНИЕ ИСТЕКАЕТ!</b>

⏰ <b>ОСТАЛОСЬ НЕСКОЛЬКО ЧАСОВ!</b>

🔥 <b>ПОСЛЕДНИЙ ШАНС ПОЛУЧИТЬ:</b>
• +50% БОНУС к депозиту (ТОЛЬКО СЕГОДНЯ!)
• Доступ к закрытому VIP-каналу
• Точные сигналы с прибылью 80%+
• Персонального менеджера 24/7

💰 Промокод: {promo_code}
📊 Минимум: всего ${min_deposit}

<b>⚠️ ЗАВТРА БУДЕТ ПОЗДНО!</b>
Упустите сейчас - потеряете навсегда!

<a href="{referral_link}">💸 АКТИВИРОВАТЬ БОНУС СЕЙЧАС →</a>

<b>🔥 ДЕЙСТВУЙТЕ, ПОКА НЕ ПОЗДНО!</b>
                """.strip()
            },
            {
                "name": "why_wait",
                "text": """
❓ <b>ПОЧЕМУ ВЫ ДО СИХ ПОР НЕ НАЧАЛИ?</b>

💸 <b>Каждый день без торговли = минус $300-500 прибыли!</b>

Пока вы сомневаетесь:
❌ Другие зарабатывают на ваших сомнениях
❌ Вы теряете реальные деньги
❌ Время работает ПРОТИВ вас

✅ <b>НО ВЫ ЕЩЁ МОЖЕТЕ ВСЁ ИЗМЕНИТЬ!</b>

📊 <b>НАШИ ПРЕИМУЩЕСТВА:</b>
• Точность сигналов 80%+ (проверено!)
• Минимальный риск, максимальная прибыль
• Профессиональная команда 24/7
• Ежедневная прибыль УЖЕ СЕГОДНЯ

🎁 +50% БОНУС | Промокод: {promo_code}

💰 От ${min_deposit} - НАЧНИТЕ ПРЯМО СЕЙЧАС!

<a href="{referral_link}">💸 ХВАТИТ ТЕРЯТЬ ДЕНЬГИ! →</a>

<b>⚡ Чем дольше ждёте - тем больше теряете!</b>
                """.strip()
            },
            {
                "name": "professional_approach",
                "text": """
🎯 <b>ХВАТИТ РАБОТАТЬ ЗА КОПЕЙКИ!</b>

💰 <b>Пока вы на работе зарабатываете $50/день...</b>
...наши клиенты делают $500-1000 ПАССИВНО!

<b>ВОПРОС: ВЫ ХОТИТЕ ПРОДОЛЖАТЬ РАБОТАТЬ, ИЛИ НАЧАТЬ ЗАРАБАТЫВАТЬ?</b>

🔥 <b>ЧТО ЖДЁТ ВАС:</b>
• Точные сигналы (просто копируй и зарабатывай!)
• Аналитика 24/7 в режиме реального времени
• Личный менеджер + VIP-поддержка
• Проверенные стратегии от профи

🎁 <b>ЭКСКЛЮЗИВНЫЙ БОНУС:</b>
+50% к депозиту | Промокод: {promo_code}

⚡ Всего ${min_deposit} - и вы в игре!

<a href="{referral_link}">💸 НАЧАТЬ ЗАРАБАТЫВАТЬ КАК ПРОФИ →</a>

<b>💎 Или продолжайте работать за копейки. Ваш выбор.</b>
                """.strip()
            },
            {
                "name": "freedom_challenge",
                "text": """
🛑 <b>СТОП! ХВАТИТ РАБОТАТЬ НА КОГО-ТО!</b>

Ваш БУДУЩИЙ БОСС - это ВЫ!

📈 <b>УЖЕ ЗАВТРА ВАША ЗАРПЛАТА МОЖЕТ БЫТЬ В 10 РАЗ БОЛЬШЕ!</b>
Мы даем инструменты, чтобы бросить надоевшую работу.

💸 <b>ЗАБУДЬТЕ О БЕДНОСТИ:</b>
• Проверенные стратегии, которые работают
• Мгновенный вывод прибыли 24/7
• Гарантированная точность сигналов (80%+)

🔥 <b>ВАШ БИЛЕТ К СВОБОДЕ:</b>
+50% БОНУС к депозиту | Промокод: {promo_code}
Старт: всего ${min_deposit}

<a href="{referral_link}">🚀 ВЫЙТИ НА НОВЫЙ УРОВЕНЬ ДОХОДА →</a>

<b>Не упустите шанс изменить свою жизнь ПРЯМО СЕЙЧАС!</b>
                """.strip()
            },
            {
                "name": "vip_spot_closing",
                "text": """
👑 <b>VIP-ДОСТУП ЗАКРЫВАЕТСЯ!</b>

🚨 <b>ПОСЛЕДНИЕ 5 МЕСТ В НАШЕМ ЗАКРЫТОМ КЛУБЕ!</b>
Это не шутка. Мы ограничиваем число, чтобы гарантировать прибыль каждому!

Что вы теряете, если не успеете?
❌ Доступ к сигналам 90%+ точности
❌ Персонального менеджера-аналитика
❌ Эксклюзивные отчеты по рынку

🔑 <b>ОТКРОЙТЕ ДВЕРЬ К ЭЛИТНОМУ ЗАРАБОТКУ:</b>
🎁 БОНУС +50% | Промокод: {promo_code}
Минимум: ${min_deposit}

<a href="{referral_link}">⏳ ЗАНЯТЬ ПОСЛЕДНЕЕ VIP-МЕСТО →</a>

<b>Ваше финансовое будущее зависит от 5 минут, которые у вас есть!</b>
                """.strip()
            },
            {
                "name": "one_day_profit_test",
                "text": """
📅 <b>ПРОВЕРЬТЕ НАС СЕГОДНЯ!</b>

🚫 <b>НИКАКОГО РИСКА!</b>
Просто попробуйте один день. Вы либо увидите реальную прибыль, либо... нет. Мы уверены в результате!

💡 <b>СЕГОДНЯШНИЙ ПЛАН:</b>
1. Пополнить счет (от ${min_deposit})
2. Получить БОНУС +50% (Промокод: {promo_code})
3. Скопировать 3 наших сигнала
4. Увидеть ПРИБЫЛЬ до конца дня!

💰 <b>ПОЧЕМУ БЫ НЕ ПОПРОБОВАТЬ?</b>
Это самый простой способ заработать сотни долларов.

<a href="{referral_link}">✅ ТЕСТ-ДРАЙВ ПРИБЫЛИ НАЧИНАЕТСЯ! →</a>

<b>Через 24 часа вы будете либо богаче, либо... нет. Выбирайте.</b>
                """.strip()
            },
            {
                "name": "live_signal_alert",
                "text": """
📈 <b>ВНИМАНИЕ! СИГНАЛ АКТИВЕН ПРЯМО СЕЙЧАС!</b>

💰 <b>СЕЙЧАС ВАША ВОЗМОЖНОСТЬ ЗАРАБОТАТЬ!</b>

Пока вы читаете это, наш активный сигнал уже приносит +15% прибыли!
⏰ Осталось **15 минут**, чтобы войти!

📊 <b>КАК ЗАРАБОТАТЬ СЕЙЧАС:</b>
1. Войти в аккаунт
2. Использовать Промокод: {promo_code} (+50% к капиталу!)
3. Скопировать сигнал (Мы покажем какой!)

💵 <b>ВЫ МОЖЕТЕ ЗАРАБОТАТЬ ПЕРВЫЕ $100 СЕГОДНЯ!</b>
Не упустите эту сделку!

<a href="{referral_link}">⚡️ СКОПИРОВАТЬ СИГНАЛ И ЗАРАБОТАТЬ! →</a>

<b>Счёт идёт на секунды! Не дайте сделке закрыться без вас.</b>
                """.strip()
            },
            {
                "name": "biggest_mistake_fomo",
                "text": """
❌ <b>ГЛАВНАЯ ОШИБКА, КОТОРУЮ ВЫ СОВЕРШАЕТЕ!</b>

Это не ошибка в стратегии. Это — **ПРОМЕДЛЕНИЕ!**

Пока вы ждете "идеального момента", рынок уходит, а вместе с ним:
📉 - $500 в неделю
📉 - Вся ваша потенциальная прибыль

✅ <b>ИСПРАВЬТЕ ЭТУ ОШИБКУ СЕЙЧАС:</b>
Начните с минимальных ${min_deposit}
Получите наш ГАРАНТИРОВАННЫЙ БОНУС +50% | {promo_code}
Прекратите терять деньги на сомнениях!

<a href="{referral_link}">🔥 ИСПРАВИТЬ ОШИБКУ И НАЧАТЬ ЗАРАБАТЫВАТЬ! →</a>

<b>Сделайте это сейчас, чтобы не жалеть завтра!</b>
                """.strip()
            },
            {
                "name": "goal_focus_vision",
                "text": """
🏝️ <b>О ЧЕМ ВЫ МЕЧТАЕТЕ?</b>

Новая машина? Путешествие? Свобода от кредитов?
❌ Это не произойдет, пока вы ничего не меняете.

✅ <b>МЫ ЗНАЕМ, КАК СДЕЛАТЬ ВАШУ МЕЧТУ РЕАЛЬНОСТЬЮ:</b>
Наши трейдеры используют прибыль, чтобы оплатить свою лучшую жизнь.

💰 <b>ВСТРОЕННЫЙ УСПЕХ:</b>
• Прогнозируемая ежедневная прибыль
• Полная поддержка
• БОНУС +50% для быстрого старта (Промокод: {promo_code})

📊 <b>${min_deposit} - это инвестиция в ВАШУ МЕЧТУ.</b>

<a href="{referral_link}">✨ НАЧАТЬ ПУТЬ К МЕЧТЕ →</a>

<b>Чем раньше начнете, тем быстрее купите билет на свой личный остров!</b>
                """.strip()
            },
            {
                "name": "24_hour_lockdown",
                "text": """
💥 <b>24 ЧАСА ДО БЛОКИРОВКИ ПРЕДЛОЖЕНИЯ!</b>

ЭТО ВАШЕ **ПОСЛЕДНЕЕ НАПОМИНАНИЕ!**
⏳ Ровно через 24 часа это предложение перестанет существовать.

⛔ <b>ВЫ ПОТЕРЯЕТЕ:</b>
• Бонус +50% (Вы потеряете половину своего стартового капитала!)
• Доступ к сигналам 80%+ точности
• Шанс начать с ${min_deposit}

<b>НЕ ДАЙТЕ СЕБЕ СТАТЬ АУТСАЙДЕРОМ!</b>

<a href="{referral_link}">🚨 АКТИВИРОВАТЬ ПРЕДЛОЖЕНИЕ ДО БЛОКИРОВКИ! →</a>

<b>Подумайте о том, сколько вы потеряете, если проспите!</b>
                """.strip()
            },
            {
                "name": "insider_secret_reveal",
                "text": """
🤫 <b>МЫ РАСКРОЕМ ВАМ СЕКРЕТ!</b>

Большие банки и фонды не хотят, чтобы вы знали, как легко можно зарабатывать на рынке. Мы нашли **"ЛАЗЕЙКУ"!**

🔥 <b>ВАША ЛАЗЕЙКА К БОЛЬШИМ ДЕНЬГАМ:</b>
• Уникальный алгоритм, который видит сделку до её начала
• Вы просто копируете результат
• ВСЕГО ${min_deposit} для старта!

🎁 <b>СЕКРЕТНЫЙ БОНУС:</b>
+50% к вашему первому депозиту | Промокод: {promo_code}

<a href="{referral_link}">🔑 ИСПОЛЬЗОВАТЬ СЕКРЕТНУЮ ЛАЗЕЙКУ →</a>

<b>Вступайте в клуб тех, кто знает больше, чем остальные!</b>
                """.strip()
            },
            {
                "name": "lost_profit_calculation",
                "text": """
🤯 <b>СКОЛЬКО ВЫ УЖЕ ПОТЕРЯЛИ?</b>

Если бы вы начали неделю назад, ваша прибыль могла бы составить:
✅ **+ $1,500 - $3,000** (Это реальные результаты наших трейдеров)

Это реальные деньги, которые вы **не заработали**. Хватит!

💰 <b>НАЧНИТЕ ВОЗВРАЩАТЬ УТЕРЯННОЕ!</b>
• Сегодня ваш шанс начать с УДВОЕННЫМ капиталом
• БОНУС +50% (Промокод: {promo_code})
• Ваш шанс от ${min_deposit} до $1,000 в день!

<a href="{referral_link}">💸 ВЕРНУТЬ УПУЩЕННУЮ ПРИБЫЛЬ СЕГОДНЯ ЖЕ! →</a>

<b>Посчитайте, сколько вам стоит ваше промедление.</b>
                """.strip()
            },
            {
                "name": "copy_paste_money",
                "text": """
🖍️ <b>САМЫЙ ЛЁГКИЙ СПОСОБ ЗАРАБОТКА В ИНТЕРНЕТЕ!</b>

Забудьте о сложных стратегиях, графиках и аналитике.
Ваша работа: **СКОПИРОВАТЬ - ВСТАВИТЬ - ЗАРАБОТАТЬ!**

👍 <b>НАСТОЛЬКО ПРОСТО, ЧТО СПРАВИТСЯ ДАЖЕ РЕБЁНОК:</b>
• Получите точный сигнал от наших экспертов
• Введите его в своем кабинете
• Наблюдайте за ростом баланса
• Старт всего от ${min_deposit}

🎁 <b>БОНУС ДЛЯ ЛЕНИВЫХ:</b>
+50% к депозиту, чтобы начать с комфортом | {promo_code}

<a href="{referral_link}">🖱️ СКОПИРОВАТЬ ПЕРВУЮ ПРИБЫЛЬ →</a>

<b>Не усложняйте. Просто делайте деньги!</b>
                """.strip()
            }
        ]
    
    def _add_admin_event(self, event_type: str, user_id: int, description: str):
        """Добавить событие в историю для администратора"""
        event = {
            'timestamp': datetime.now().isoformat(),
            'event_type': event_type,
            'user_id': user_id,
            'description': description
        }
        self.admin_events.insert(0, event)  # Добавляем в начало списка
        # Ограничиваем размер истории
        if len(self.admin_events) > self.max_events:
            self.admin_events = self.admin_events[:self.max_events]
    
    def _load_users_db(self):
        """Загрузка базы пользователей из JSON"""
        try:
            with open(self.users_db_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                logger.info(f"✅ Загружено {len(data)} пользователей из базы")
                return data
        except FileNotFoundError:
            logger.info("📝 Создается новая база пользователей")
            return {}
        except Exception as e:
            logger.error(f"❌ Ошибка загрузки базы пользователей: {e}")
            return {}
    
    def _save_users_db(self):
        """Сохранение базы пользователей в JSON"""
        try:
            with open(self.users_db_file, 'w', encoding='utf-8') as f:
                json.dump(self.users_db, f, ensure_ascii=False, indent=2)
            logger.info(f"💾 База пользователей сохранена ({len(self.users_db)} пользователей)")
        except Exception as e:
            logger.error(f"❌ Ошибка сохранения базы пользователей: {e}")
    
    # ============================================
    # РЕФЕРАЛЬНАЯ СИСТЕМА - УВЕДОМЛЕНИЯ
    # ============================================
    
    async def _notify_referrer_new_click(self, referrer_id: str, new_user_name: str):
        """Уведомление реферера о новом переходе по ссылке"""
        if not self.application:
            return
        
        try:
            referrer_lang = get_user_language(int(referrer_id), self.users_db)
            stats = self.referral_manager.get_referral_stats(referrer_id)
            
            # Форматируем имя: если это username (начинается с @), оставляем как есть, иначе используем имя как есть
            # В шаблоне уже есть @ перед {username}, поэтому передаем имя без @
            display_name = new_user_name.lstrip('@') if new_user_name.startswith('@') else new_user_name
            message = t('referral_new_click', referrer_lang, username=display_name)
            
            await self.application.bot.send_message(
                chat_id=int(referrer_id),
                text=message,
                parse_mode='Markdown'
            )
            logger.info(f"Уведомление о переходе отправлено рефереру {referrer_id}")
        except Exception as e:
            logger.error(f"Ошибка отправки уведомления рефереру: {e}")
    
    async def _notify_referrer_activation(self, referrer_id: str, activated_user_name: str):
        """Уведомление реферера об активации реферала"""
        if not self.application:
            return
        
        try:
            referrer_lang = get_user_language(int(referrer_id), self.users_db)
            stats = self.referral_manager.get_referral_stats(referrer_id)
            
            next_level, remaining = get_next_bonus_level(stats['activated_count'])
            progress = f"{stats['activated_count']}/{next_level['friends_required']}" if next_level else "🏆 MAX"
            
            message = t('referral_friend_activated', referrer_lang, 
                       username=activated_user_name, 
                       progress=progress)
            
            # Проверяем достигнут ли новый уровень
            available = stats.get('available_bonuses', [])
            if available:
                message += "\n\n" + t('referral_bonus_available', referrer_lang)
            
            keyboard = [[InlineKeyboardButton(
                t('btn_referral_menu', referrer_lang), 
                callback_data="referral_menu"
            )]]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await self.application.bot.send_message(
                chat_id=int(referrer_id),
                text=message,
                parse_mode='Markdown',
                reply_markup=reply_markup
            )
            logger.info(f"Уведомление об активации отправлено рефереру {referrer_id}")
        except Exception as e:
            logger.error(f"Ошибка отправки уведомления об активации: {e}")
    
    async def _notify_admin_bonus_request(self, user_id: str, bonus_id: str):
        """Уведомление админа о новой заявке на бонус"""
        if not self.application:
            return
        
        try:
            user_data = self.users_db.get(user_id, {})
            username = user_data.get('username', 'Пользователь')
            ref_data = user_data.get('referral', {})
            tv_username = ref_data.get('tradingview_username', 'Не указан')
            
            # Находим информацию о бонусе
            bonus_info = None
            for level in REFERRAL_BONUS_LEVELS:
                if level['id'] == bonus_id:
                    bonus_info = level
                    break
            
            message = f"""
🎁 *НОВАЯ ЗАЯВКА НА БОНУС*

👤 Пользователь: @{username}
🆔 ID: `{user_id}`
📊 TradingView: {tv_username}

🏆 Бонус: {bonus_info['bonus_name'] if bonus_info else bonus_id}
📅 Срок: {bonus_info['bonus_days'] if bonus_info else '?'} дней
            """.strip()
            
            keyboard = [
                [
                    InlineKeyboardButton("✅ Одобрить", callback_data=f"approve_bonus_{user_id}"),
                    InlineKeyboardButton("❌ Отклонить", callback_data=f"reject_bonus_{user_id}")
                ],
                [InlineKeyboardButton("📋 Все заявки", callback_data="admin_referral_requests")]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await self.application.bot.send_message(
                chat_id=int(self.admin_chat_id),
                text=message,
                parse_mode='Markdown',
                reply_markup=reply_markup
            )
            logger.info(f"Уведомление о заявке на бонус отправлено админу")
        except Exception as e:
            logger.error(f"Ошибка отправки уведомления админу: {e}")
    
    def _get_motivation_message(self):
        """Получить случайный шаблон мотивационного сообщения"""
        template = random.choice(self.motivation_templates)
        message = template['text'].format(
            promo_code=self.referral_code,
            min_deposit=self.min_deposit,
            referral_link=self.referral_link
        )
        return message
    
    def _can_send_motivation(self, user_id):
        """Проверить, можно ли отправить мотивационное сообщение пользователю"""
        user_data = self.users_db.get(str(user_id))
        if not user_data:
            return False
        
        # Не отправляем, если уже есть депозит
        if user_data.get('deposited', False):
            return False
        
        # Проверяем минимальный интервал
        last_sent = user_data.get('last_motivation_sent')
        if last_sent:
            try:
                last_sent_dt = datetime.fromisoformat(last_sent)
                time_since_last = datetime.now() - last_sent_dt
                if time_since_last < timedelta(hours=self.motivation_min_interval_hours):
                    return False
            except:
                pass
        
        return True
    
    async def _send_motivation_message(self, user_id):
        """Отправить мотивационное сообщение пользователю"""
        if not self.application or not self.motivation_enabled:
            return False
        
        if not self._can_send_motivation(user_id):
            return False
        
        try:
            message = self._get_motivation_message()
            
            # Добавляем кнопки
            keyboard = [
                [InlineKeyboardButton("🔗 Пополнить счет", url=self.referral_link)],
                [InlineKeyboardButton("📞 Поддержка", url="https://t.me/kaktotakxm")],
                [InlineKeyboardButton("✅ Проверить доступ", callback_data="check_access")]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await self.application.bot.send_message(
                chat_id=user_id,
                text=message,
                parse_mode='HTML',
                reply_markup=reply_markup,
                disable_web_page_preview=True
            )
            
            # Обновляем время последней отправки
            user_data = self.users_db.get(str(user_id), {})
            user_data['last_motivation_sent'] = datetime.now().isoformat()
            self.users_db[str(user_id)] = user_data
            self._save_users_db()
            
            logger.info(f"✅ Мотивационное сообщение отправлено пользователю {user_id}")
            self._add_admin_event('motivation_sent', user_id, 'Отправлено мотивационное сообщение')
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Ошибка отправки мотивационного сообщения пользователю {user_id}: {e}")
            return False
    
    def _motivation_job(self):
        """Фоновая задача для отправки мотивационных сообщений"""
        if not self.motivation_enabled or not self.application:
            return
        
        logger.info("🔔 Запуск задачи мотивационных рассылок...")
        sent_count = 0
        
        # Получаем пользователей без депозита
        users_without_deposit = [
            user_id for user_id, user_data in self.users_db.items()
            if not user_data.get('deposited', False) and not user_data.get('verified', False)
        ]
        
        logger.info(f"📊 Найдено пользователей без депозита: {len(users_without_deposit)}")
        
        # Создаем событийный цикл для асинхронных операций
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        for user_id in users_without_deposit:
            try:
                if self._can_send_motivation(user_id):
                    result = loop.run_until_complete(self._send_motivation_message(user_id))
                    if result:
                        sent_count += 1
                        # Небольшая пауза между отправками
                        asyncio.run(asyncio.sleep(1))
            except Exception as e:
                logger.error(f"❌ Ошибка при отправке мотивации пользователю {user_id}: {e}")
        
        loop.close()
        
        logger.info(f"✅ Мотивационные сообщения отправлены: {sent_count} из {len(users_without_deposit)}")
        
        # Уведомляем админа
        if sent_count > 0:
            try:
                requests.post(
                    f"https://api.telegram.org/bot{self.bot_token}/sendMessage",
                    data={
                        'chat_id': self.admin_chat_id,
                        'text': f"📊 Мотивационная рассылка завершена\n\n✅ Отправлено: {sent_count} сообщений\n👥 Всего без депозита: {len(users_without_deposit)}"
                    }
                )
            except Exception as e:
                logger.error(f"❌ Ошибка отправки отчета админу: {e}")
    
    def start_motivation_scheduler(self, application):
        """Запустить планировщик мотивационных рассылок"""
        self.application = application
        
        if not self.motivation_auto_enabled:
            logger.info("🔕 Автоматический планировщик мотивационных рассылок отключён. Доступна только ручная отправка через админ-панель.")
            try:
                requests.post(
                    f"https://api.telegram.org/bot{self.bot_token}/sendMessage",
                    data={
                        'chat_id': self.admin_chat_id,
                        'text': "🤖 Бот запущен!\n\n🔕 Мотивационные рассылки: ручной режим\n🛡️ Защита от спама: активна\n➡️ Используйте кнопку \"📧 Запустить рассылку\" в админ-панели."
                    }
                )
            except Exception as e:
                logger.error(f"❌ Ошибка отправки уведомления админу: {e}")
            return
        
        if self.scheduler is None:
            self.scheduler = BackgroundScheduler()
            
            # Добавляем задачу с интервалом
            self.scheduler.add_job(
                self._motivation_job,
                trigger=IntervalTrigger(hours=self.motivation_interval_hours),
                id='motivation_mailer',
                name='Мотивационные рассылки',
                replace_existing=True
            )
            
            self.scheduler.start()
            logger.info(f"🔔 Планировщик мотивационных рассылок запущен (интервал: {self.motivation_interval_hours} часов)")
            
            # Отправляем уведомление админу
            try:
                requests.post(
                    f"https://api.telegram.org/bot{self.bot_token}/sendMessage",
                    data={
                        'chat_id': self.admin_chat_id,
                        'text': f"🤖 Бот запущен!\n\n🔔 Мотивационные рассылки: активны\n⏰ Интервал: каждые {self.motivation_interval_hours} часов\n🛡️ Защита от спама: {self.motivation_min_interval_hours} часов"
                    }
                )
            except Exception as e:
                logger.error(f"❌ Ошибка отправки уведомления админу: {e}")
    
    def _export_users_csv(self):
        """Экспорт пользователей в CSV файл"""
        import csv
        csv_filename = f"users_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        
        try:
            with open(csv_filename, 'w', newline='', encoding='utf-8-sig') as csvfile:
                fieldnames = ['ID', 'Username', 'Telegram', 'Язык', 'Дата регистрации', 'PocketOption ID', 'Статус', 'Верифицирован', 'Депозит']
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                
                writer.writeheader()
                for user_id, user_data in self.users_db.items():
                    writer.writerow({
                        'ID': user_id,
                        'Username': user_data.get('username', 'N/A'),
                        'Telegram': f"@{user_data.get('username', 'N/A')}",
                        'Язык': user_data.get('language', 'N/A'),
                        'Дата регистрации': user_data.get('registered_at', 'N/A')[:19] if user_data.get('registered_at') else 'N/A',
                        'PocketOption ID': user_data.get('pocket_option_id', 'Не отправлен'),
                        'Статус': user_data.get('status', 'N/A'),
                        'Верифицирован': '✅ Да' if user_data.get('verified') else '❌ Нет',
                        'Депозит': '✅ Да' if user_data.get('deposited') else '❌ Нет'
                    })
            
            logger.info(f"📊 Экспортировано {len(self.users_db)} пользователей в {csv_filename}")
            return csv_filename
        except Exception as e:
            logger.error(f"❌ Ошибка экспорта пользователей: {e}")
            return None
    
    async def _delete_user_last_messages(self, user_id: int, context: ContextTypes.DEFAULT_TYPE, limit: int = 10):
        """
        Удаляет последние N сообщений бота пользователю (включая фото)
        
        Args:
            user_id: ID пользователя
            context: Контекст бота
            limit: Максимальное количество сообщений для удаления
        """
        user_id_str = str(user_id)
        if user_id_str in self.user_last_messages:
            message_ids = self.user_last_messages[user_id_str][-limit:]  # Берем последние N
            self.user_last_messages[user_id_str] = []
            
            for msg_id in message_ids:
                try:
                    await context.bot.delete_message(chat_id=user_id, message_id=msg_id)
                except Exception as e:
                    # Игнорируем ошибки удаления (сообщение уже удалено или недоступно)
                    logger.debug(f"Не удалось удалить сообщение {msg_id} для пользователя {user_id}: {e}")
    
    def _save_message_id(self, user_id: int, message_id: int):
        """
        Сохраняет ID сообщения для последующего удаления
        
        Args:
            user_id: ID пользователя
            message_id: ID сообщения
        """
        user_id_str = str(user_id)
        if user_id_str not in self.user_last_messages:
            self.user_last_messages[user_id_str] = []
        self.user_last_messages[user_id_str].append(message_id)
        # Оставляем только последние 10 сообщений для каждого пользователя
        if len(self.user_last_messages[user_id_str]) > 10:
            self.user_last_messages[user_id_str] = self.user_last_messages[user_id_str][-10:]
    
    async def check_channel_subscription(self, user_id: int, context: ContextTypes.DEFAULT_TYPE) -> bool:
        """
        Проверяет подписку пользователя на канал
        
        Args:
            user_id: ID пользователя
            context: Контекст бота
            
        Returns:
            True если пользователь подписан, False если нет
        """
        # Если канал не настроен, блокируем доступ
        if not self.channel_username:
            logger.error("❌ channel_username не настроен! Проверка подписки невозможна. Настройте self.channel_username в __init__")
            return False
        
        try:
            member = await context.bot.get_chat_member(chat_id=self.channel_username, user_id=user_id)
            # Проверяем статус подписки
            if member.status in ['member', 'administrator', 'creator']:
                logger.debug(f"✅ Пользователь {user_id} подписан на канал (статус: {member.status})")
                return True
            else:
                logger.debug(f"❌ Пользователь {user_id} не подписан на канал (статус: {member.status})")
                return False
        except BadRequest as e:
            # BadRequest обычно означает, что пользователь не подписан или бот не админ канала
            error_message = str(e)
            if "user not found" in error_message.lower() or "chat not found" in error_message.lower():
                logger.warning(f"⚠️ Пользователь {user_id} не подписан на канал {self.channel_username}: {e}")
            elif "not enough rights" in error_message.lower() or "can't get chat member" in error_message.lower() or "member list is inaccessible" in error_message.lower():
                logger.error(f"❌ БОТ НЕ ЯВЛЯЕТСЯ АДМИНИСТРАТОРОМ КАНАЛА {self.channel_username}! Добавьте бота в администраторы канала с правом 'Выбор администраторов' или просто дайте полные права админа. Ошибка: {e}")
            else:
                logger.warning(f"⚠️ Ошибка при проверке подписки пользователя {user_id}: {e}")
            return False
        except TelegramError as e:
            logger.error(f"❌ Telegram ошибка при проверке подписки пользователя {user_id}: {e}")
            return False
        except Exception as e:
            logger.error(f"❌ Неожиданная ошибка проверки подписки пользователя {user_id}: {e}", exc_info=True)
            return False
        
    async def start_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Команда /start"""
        user_id = update.effective_user.id
        logger.info(f"🚀 HANDLING /START: user_id={user_id}")
        
        try:
            # Используем имя пользователя, если нет username
            username = update.effective_user.username or (update.effective_user.first_name or "User")
            
            # Парсинг реферального кода из аргументов (/start ref_123456)
            referrer_id = None
            if context.args and len(context.args) > 0:
                start_param = context.args[0]
                referrer_id = self.referral_manager.parse_referral_code(start_param)
                logger.info(f"🔗 Referral param found: {start_param}, referrer_id={referrer_id}")
            
            # Проверяем, новый ли это пользователь
            is_new_user = str(user_id) not in self.users_db
            logger.info(f"👤 is_new_user={is_new_user}, user_in_db={str(user_id) in self.users_db}")
            
            # Для админа сразу ставим русский язык
            if str(user_id) == self.admin_chat_id:
                logger.info(f"🤴 Admin /start detected")
                if is_new_user or 'language' not in self.users_db.get(str(user_id), {}):
                    if str(user_id) not in self.users_db:
                        self.users_db[str(user_id)] = {
                            'username': username,
                            'registered_at': datetime.now().isoformat(),
                            'status': 'admin',
                            'pocket_option_id': None,
                            'verified': True,
                            'deposited': True,
                            'language': 'ru'
                        }
                    else:
                        self.users_db[str(user_id)]['language'] = 'ru'
                    self._save_users_db()
            # Если новый пользователь (не админ) - показываем выбор языка
            elif is_new_user or 'language' not in self.users_db.get(str(user_id), {}):
                logger.info(f"🌐 Redirecting to language selection (is_new={is_new_user})")
                # Создаем запись пользователя БЕЗ языка
                if str(user_id) not in self.users_db:
                    self.users_db[str(user_id)] = {
                        'username': username,
                        'registered_at': datetime.now().isoformat(),
                        'status': 'new',
                        'pocket_option_id': None,
                        'verified': False,
                        'deposited': False
                    }
                    self._save_users_db()
                    
                    # Регистрируем реферала если есть реферер
                    if referrer_id and referrer_id != str(user_id):
                        logger.info(f"🔗 Регистрация реферала: новый={user_id}, реферер={referrer_id}")
                        success, msg = self.referral_manager.register_referral_click(str(user_id), referrer_id)
                        logger.info(f"🔗 Результат регистрации: success={success}, msg={msg}")
                        if success:
                            # Уведомляем реферера о новом переходе
                            logger.info(f"📤 Отправляем уведомление рефереру {referrer_id}")
                            await self._notify_referrer_new_click(referrer_id, username)
                
                # Показываем выбор языка для новых пользователей
                keyboard = get_language_keyboard()
                reply_markup = InlineKeyboardMarkup(keyboard)
                
                await update.message.reply_text(
                    "🌐 *Welcome! Choose your language / Выберите язык*\n\n"
                    "Please select your preferred language:",
                    reply_markup=reply_markup,
                    parse_mode='Markdown'
                )
                logger.info(f"✅ Language keyboard sent to {user_id}")
                return
            
            # Если пользователь уже выбрал язык - показываем приветствие
            user_lang = get_user_language(
                user_id, 
                self.users_db, 
                update.effective_user.language_code
            )
            logger.info(f"📚 User language detected: {user_lang}")
            
            # Проверяем подписку на канал (для админа пропускаем проверку)
            if str(user_id) != self.admin_chat_id:
                is_subscribed = await self.check_channel_subscription(user_id, context)
                logger.info(f"📢 Subscription status: {is_subscribed}")
                if not is_subscribed:
                    # Показываем сообщение о необходимости подписки
                    subscription_text = f"""
{t('subscription_required_title', user_lang)}

{t('subscription_required_text', user_lang)}
                    """.strip()
                    
                    keyboard = [[InlineKeyboardButton(t('btn_subscribe', user_lang), url=self.channel_url)]]
                    reply_markup = InlineKeyboardMarkup(keyboard)
                    
                    msg = await update.message.reply_text(
                        subscription_text,
                        reply_markup=reply_markup,
                        parse_mode='Markdown'
                    )
                    self._save_message_id(user_id, msg.message_id)
                    logger.info(f"🛑 Subscription prompt sent to {user_id}")
                    return
            
            # Если подписан или админ - показываем главное меню
            logger.info(f"🏰 Showing main menu to {user_id}")
            await self._send_main_menu(user_id, context, user_lang)
            logger.info(f"✨ Start command sequence completed for {user_id}")
            
        except Exception as e:
            logger.error(f"❌ CRITICAL ERROR IN start_command: {e}", exc_info=True)
            # Пытаемся уведомить пользователя об ошибке
            try:
                await update.message.reply_text("❌ Произошла ошибка. Пожалуйста, попробуйте еще раз или обратитесь в поддержку.")
            except:
                pass
        
    async def instruction_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Кнопка Инструкция"""
        query = update.callback_query
        await query.answer()
        
        user_id = query.from_user.id
        user_lang = get_user_language(user_id, self.users_db)
        
        # Определяем откуда пришли (по умолчанию - из level_free)
        callback_data = query.data
        if callback_data.startswith("instruction_from_"):
            from_section = callback_data.replace("instruction_from_", "")
        else:
            from_section = "level_free"  # По умолчанию
        
        # Формируем ссылку для регистрации
        registration_link = "https://u3.shortink.io/register?utm_campaign=827841&utm_source=affiliate&utm_medium=sr&a=CQQJpdvm2ya9dU&ac=tggg&code=50START"
        
        instruction_text = f"""
{t('instruction_title', user_lang)}

1️⃣ {t('instruction_step1', user_lang, link=registration_link)}

2️⃣ {t('instruction_step2', user_lang)}

3️⃣ {t('instruction_step3', user_lang)}
        """.strip()
        
        # Определяем куда возвращаться в зависимости от источника
        if from_section == "faq":
            back_callback = "faq_menu"
        elif from_section == "level_free":
            back_callback = "level_free"
        else:
            back_callback = "trader_menu"
        
        keyboard = [
            [InlineKeyboardButton(t('btn_back', user_lang), callback_data=back_callback)],
            [InlineKeyboardButton(t('btn_main_menu', user_lang), callback_data="back_to_main")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(
            instruction_text,
            reply_markup=reply_markup,
            parse_mode='Markdown'
        )
    
    # ============================================
    # МЕНЮ ТРЕЙДЕРА
    # ============================================
    
    async def trader_menu_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Меню трейдера с уровнями доступа"""
        query = update.callback_query
        await query.answer()
        
        user_id = query.from_user.id
        user_lang = get_user_language(user_id, self.users_db)
        
        # Проверяем подписку на канал (для админа пропускаем проверку)
        if str(user_id) != self.admin_chat_id:
            is_subscribed = await self.check_channel_subscription(user_id, context)
            if not is_subscribed:
                # Показываем сообщение о необходимости подписки
                subscription_text = f"""
{t('subscription_required_title', user_lang)}

{t('subscription_required_text', user_lang)}
                """.strip()
                
                keyboard = [[InlineKeyboardButton(t('btn_subscribe', user_lang), url=self.channel_url)]]
                reply_markup = InlineKeyboardMarkup(keyboard)
                
                if query.message.photo:
                    await query.delete_message()
                    await context.bot.send_message(
                        chat_id=user_id,
                        text=subscription_text,
                        reply_markup=reply_markup,
                        parse_mode='Markdown'
                    )
                else:
                    await query.edit_message_text(
                        subscription_text,
                        reply_markup=reply_markup,
                        parse_mode='Markdown'
                    )
                return
        
        # Если подписан или админ - показываем меню трейдера
        menu_text = f"""
{t('trader_menu_title', user_lang)}

{t('trader_menu_description', user_lang)}
        """.strip()
        
        # Сетка 2x2 для уровней
        keyboard = [
            [InlineKeyboardButton(t('btn_promocodes', user_lang), callback_data="promocodes_menu")],
            [
                InlineKeyboardButton(t('btn_level_free', user_lang), callback_data="level_free"),
                InlineKeyboardButton(t('btn_level_pro', user_lang), callback_data="level_pro")
            ],
            [
                InlineKeyboardButton(t('btn_level_mentor', user_lang), callback_data="level_mentor"),
                InlineKeyboardButton(t('btn_level_elite', user_lang), callback_data="level_elite")
            ],
            [InlineKeyboardButton(t('btn_pocketoptions', user_lang), url="https://u3.shortink.io/main?utm_campaign=827841&utm_source=affiliate&utm_medium=sr&a=CQQJpdvm2ya9dU&ac=sait&code=VDN436")],
            [InlineKeyboardButton(t('btn_blackmirror_ultra', user_lang), url="https://ru.tradingview.com/script/3eVmzktt-black-mirror-predictor/")],
            [InlineKeyboardButton(t('btn_contact_manager', user_lang), url="https://t.me/kaktotakxm")],
            [InlineKeyboardButton(t('btn_invite_friend', user_lang), url="https://t.me/share/url?url=https%3A%2F%2Ft.me%2F%2BavD8ncMHBp4zMzhi&text=%D0%9F%D1%80%D0%B8%D1%81%D0%BE%D0%B5%D0%B4%D0%B8%D0%BD%D1%8F%D0%B9%D1%81%D1%8F%20%D0%BA%20%D0%BD%D0%B0%D1%88%D0%B5%D0%BC%D1%83%20%D1%81%D0%BE%D0%BE%D0%B1%D1%89%D0%B5%D1%81%D1%82%D0%B2%D1%83%20%D1%82%D1%80%D0%B5%D0%B9%D0%B4%D0%B5%D1%80%D0%BE%D0%B2%21%20%F0%9F%9A%80")],
            [InlineKeyboardButton(t('btn_faq', user_lang), callback_data="faq_menu")],
            [
                InlineKeyboardButton(t('btn_back', user_lang), callback_data="back_to_start"),
                InlineKeyboardButton(t('btn_main_menu', user_lang), callback_data="back_to_main")
            ]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        if query.message.photo:
            await query.delete_message()
            await context.bot.send_message(
                chat_id=user_id,
                text=menu_text,
                reply_markup=reply_markup,
                parse_mode='Markdown'
            )
        else:
            await query.edit_message_text(
                menu_text,
                reply_markup=reply_markup,
                parse_mode='Markdown'
            )
    
    async def level_free_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Описание уровня FREE"""
        query = update.callback_query
        await query.answer()
        
        user_id = query.from_user.id
        user_lang = get_user_language(user_id, self.users_db)
        
        level_text = f"""
{t('level_free_title', user_lang)}

{t('level_free_description', user_lang)}
        """.strip()
        
        keyboard = [
            [InlineKeyboardButton(t('btn_see_in_action', user_lang), url="https://t.me/NeKnopkaBabl0/a/6")],
            [InlineKeyboardButton(t('btn_get_access', user_lang), callback_data="instruction_from_level_free")],
            [
                InlineKeyboardButton(t('btn_back_to_trader', user_lang), callback_data="trader_menu"),
                InlineKeyboardButton(t('btn_main_menu', user_lang), callback_data="back_to_main")
            ]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(
            level_text,
            reply_markup=reply_markup,
            parse_mode='Markdown'
        )
    
    async def level_pro_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Описание уровня PRO"""
        query = update.callback_query
        await query.answer()
        
        user_id = query.from_user.id
        user_lang = get_user_language(user_id, self.users_db)
        
        level_text = f"""
{t('level_pro_title', user_lang)}

{t('level_pro_description', user_lang)}
        """.strip()
        
        keyboard = [
            [InlineKeyboardButton(t('btn_black_mirror_ultra', user_lang), url="https://ru.tradingview.com/script/3eVmzktt-black-mirror-predictor/")],
            [InlineKeyboardButton(t('btn_see_in_action', user_lang), url="https://t.me/NeKnopkaBabl0/a/5")],
            [InlineKeyboardButton(t('btn_learn_more', user_lang), url="https://t.me/kaktotakxm")],
            [
                InlineKeyboardButton(t('btn_back_to_trader', user_lang), callback_data="trader_menu"),
                InlineKeyboardButton(t('btn_main_menu', user_lang), callback_data="back_to_main")
            ]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(
            level_text,
            reply_markup=reply_markup,
            parse_mode='Markdown'
        )
    
    async def level_mentor_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Описание уровня MENTOR"""
        query = update.callback_query
        await query.answer()
        
        user_id = query.from_user.id
        user_lang = get_user_language(user_id, self.users_db)
        
        level_text = f"""
{t('level_mentor_title', user_lang)}

{t('level_mentor_description', user_lang)}
        """.strip()
        
        keyboard = [
            [InlineKeyboardButton(t('btn_learn_more', user_lang), url="https://t.me/kaktotakxm")],
            [
                InlineKeyboardButton(t('btn_back_to_trader', user_lang), callback_data="trader_menu"),
                InlineKeyboardButton(t('btn_main_menu', user_lang), callback_data="back_to_main")
            ]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(
            level_text,
            reply_markup=reply_markup,
            parse_mode='Markdown'
        )
    
    async def level_elite_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Описание уровня ELITE"""
        query = update.callback_query
        await query.answer()
        
        user_id = query.from_user.id
        user_lang = get_user_language(user_id, self.users_db)
        
        level_text = f"""
{t('level_elite_title', user_lang)}

{t('level_elite_description', user_lang)}
        """.strip()
        
        keyboard = [
            [InlineKeyboardButton(t('btn_learn_more', user_lang), url="https://t.me/kaktotakxm")],
            [
                InlineKeyboardButton(t('btn_back_to_trader', user_lang), callback_data="trader_menu"),
                InlineKeyboardButton(t('btn_main_menu', user_lang), callback_data="back_to_main")
            ]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(
            level_text,
            reply_markup=reply_markup,
            parse_mode='Markdown'
        )
    
    # ============================================
    # FAQ
    # ============================================
    
    async def faq_menu_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Меню FAQ"""
        query = update.callback_query
        await query.answer()
        
        user_id = query.from_user.id
        user_lang = get_user_language(user_id, self.users_db)
        
        faq_text = f"""
{t('faq_title', user_lang)}

{t('faq_select_question', user_lang)}
        """.strip()
        
        keyboard = [
            [InlineKeyboardButton(t('faq_btn_how_start', user_lang), callback_data="faq_how_start")],
            [InlineKeyboardButton(t('faq_btn_have_account', user_lang), callback_data="faq_have_account")],
            [InlineKeyboardButton(t('faq_btn_get_indicator', user_lang), callback_data="faq_get_indicator")],
            [
                InlineKeyboardButton(t('btn_back_to_trader', user_lang), callback_data="trader_menu"),
                InlineKeyboardButton(t('btn_main_menu', user_lang), callback_data="back_to_main")
            ]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(
            faq_text,
            reply_markup=reply_markup,
            parse_mode='Markdown'
        )
    
    async def faq_how_start_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Ответ на FAQ: Как начать?"""
        query = update.callback_query
        await query.answer()
        
        user_id = query.from_user.id
        user_lang = get_user_language(user_id, self.users_db)
        
        answer_text = t('faq_answer_how_start', user_lang)
        
        keyboard = [
            [InlineKeyboardButton(t('btn_get_free_access', user_lang), callback_data="instruction_from_faq")],
            [InlineKeyboardButton(t('btn_back_to_faq', user_lang), callback_data="faq_menu")],
            [
                InlineKeyboardButton(t('btn_back_to_trader', user_lang), callback_data="trader_menu"),
                InlineKeyboardButton(t('btn_main_menu', user_lang), callback_data="back_to_main")
            ]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(
            answer_text,
            reply_markup=reply_markup,
            parse_mode='Markdown'
        )
    
    async def faq_have_account_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Ответ на FAQ: У меня уже есть аккаунт"""
        query = update.callback_query
        await query.answer()
        
        user_id = query.from_user.id
        user_lang = get_user_language(user_id, self.users_db)
        
        answer_text = t('faq_answer_have_account', user_lang)
        
        keyboard = [
            [InlineKeyboardButton(t('btn_get_free_access', user_lang), callback_data="instruction_from_faq")],
            [InlineKeyboardButton(t('btn_back_to_faq', user_lang), callback_data="faq_menu")],
            [
                InlineKeyboardButton(t('btn_back_to_trader', user_lang), callback_data="trader_menu"),
                InlineKeyboardButton(t('btn_main_menu', user_lang), callback_data="back_to_main")
            ]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(
            answer_text,
            reply_markup=reply_markup,
            parse_mode='Markdown'
        )
    
    async def faq_get_indicator_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Ответ на FAQ: Как получить индикатор?"""
        query = update.callback_query
        await query.answer()
        
        user_id = query.from_user.id
        user_lang = get_user_language(user_id, self.users_db)
        
        answer_text = t('faq_answer_get_indicator', user_lang)
        
        keyboard = [
            [InlineKeyboardButton(t('btn_support', user_lang), url="https://t.me/kaktotakxm")],
            [InlineKeyboardButton(t('btn_back_to_faq', user_lang), callback_data="faq_menu")],
            [
                InlineKeyboardButton(t('btn_back_to_trader', user_lang), callback_data="trader_menu"),
                InlineKeyboardButton(t('btn_main_menu', user_lang), callback_data="back_to_main")
            ]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(
            answer_text,
            reply_markup=reply_markup,
            parse_mode='Markdown'
        )
    
    # ============================================
    # РЕФЕРАЛЬНАЯ СИСТЕМА "ЗДРАВЫЙ ТРЕЙДЕР"
    # ============================================
    
    async def referral_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Команда /referral - меню реферальной программы"""
        user_id = str(update.effective_user.id)
        user_lang = get_user_language(int(user_id), self.users_db)
        
        # Получаем статистику рефералов
        stats = self.referral_manager.get_referral_stats(user_id)
        ref_link = self.referral_manager.get_referral_link(user_id)
        
        # Формируем текст
        menu_text = t('referral_menu_title', user_lang) + "\n\n"
        menu_text += t('referral_menu_description', user_lang) + "\n\n"
        menu_text += f"🔗 *{t('referral_your_link', user_lang)}:*\n`{ref_link}`\n\n"
        menu_text += f"📊 *{t('referral_stats_title', user_lang)}:*\n"
        menu_text += f"👥 {t('referral_total_clicks', user_lang)}: {stats['total_clicks']}\n"
        menu_text += f"✅ {t('referral_activated', user_lang)}: {stats['activated_count']}\n\n"
        menu_text += f"🎯 *{t('referral_progress', user_lang)}:*\n{stats['progress_bar']}\n"
        
        if stats['next_level']:
            menu_text += f"\n📈 {t('referral_next_bonus', user_lang, days=stats['next_level']['bonus_days'], remaining=stats['remaining'])}"
        
        keyboard = [
            [InlineKeyboardButton(t('btn_referral_copy_link', user_lang), callback_data="referral_copy_link")],
            [InlineKeyboardButton(t('btn_referral_share', user_lang), url=f"https://t.me/share/url?url={urllib.parse.quote(ref_link, safe='')}")],
        ]
        
        # Добавляем кнопку получения бонуса если есть доступные
        if stats['available_bonuses']:
            keyboard.append([InlineKeyboardButton(
                f"🎁 {t('btn_referral_claim_bonus', user_lang)}", 
                callback_data="referral_claim_bonus"
            )])
        
        keyboard.append([InlineKeyboardButton(t('btn_referral_rules', user_lang), callback_data="referral_rules")])
        keyboard.append([InlineKeyboardButton(t('btn_main_menu', user_lang), callback_data="back_to_main")])
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(
            menu_text,
            reply_markup=reply_markup,
            parse_mode='Markdown'
        )
    
    # ============================================
    # ЗДРАВЫЙ ТРЕЙДЕР (РЕФЕРАЛЬНАЯ СИСТЕМА)
    # ============================================
    
    async def healthy_trader_menu_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Меню Здравый Трейдер с описанием и реферальной системой"""
        query = update.callback_query
        await query.answer()
        
        user_id = str(query.from_user.id)
        user_lang = get_user_language(int(user_id), self.users_db)
        
        # Получаем статистику рефералов
        stats = self.referral_manager.get_referral_stats(user_id)
        ref_link = self.referral_manager.get_referral_link(user_id)
        
        # Формируем сообщение
        menu_text = t('healthy_trader_title', user_lang) + "\n\n"
        menu_text += t('healthy_trader_description', user_lang) + "\n\n"
        menu_text += "━━━━━━━━━━━━━━━━━━━━━━\n\n"
        
        menu_text += f"*{t('referral_your_link', user_lang)}*\n`{ref_link}`\n\n"
        menu_text += f"*{t('referral_progress', user_lang)}*\n{stats['progress_bar']}\n"
        
        if stats['next_level']:
            if stats['next_level']['id'] == 'level_3' or stats['next_level']['bonus_days'] == 0:
                menu_text += f"\n{t('referral_until_mentorship', user_lang, remaining=stats['remaining'])}"
            else:
                menu_text += f"\n{t('referral_until_subscription', user_lang, days=stats['next_level']['bonus_days'], remaining=stats['remaining'])}"
        
        keyboard = [
            [InlineKeyboardButton(t('btn_referral_stats', user_lang), callback_data="referral_stats")],
            [InlineKeyboardButton(t('btn_referral_share', user_lang), url=f"https://t.me/share/url?url={urllib.parse.quote(ref_link, safe='')}")],
        ]
        
        if stats['available_bonuses']:
            keyboard.append([InlineKeyboardButton(
                t('btn_claim_bonus', user_lang), 
                callback_data="referral_claim_bonus"
            )])
        
        keyboard.append([InlineKeyboardButton(t('btn_referral_rules', user_lang), callback_data="referral_rules")])
        keyboard.append([InlineKeyboardButton(t('btn_main_menu', user_lang), callback_data="back_to_main")])
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        if query.message.photo:
            await query.delete_message()
            await context.bot.send_message(
                chat_id=int(user_id),
                text=menu_text,
                reply_markup=reply_markup,
                parse_mode='Markdown'
            )
        else:
            await query.edit_message_text(
            menu_text,
            reply_markup=reply_markup,
            parse_mode='Markdown'
        )
    
    async def referral_stats_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Статистика рефералов и подписка"""
        query = update.callback_query
        await query.answer()
        
        user_id = str(query.from_user.id)
        user_lang = get_user_language(int(user_id), self.users_db)
        
        # Получаем статистику
        stats = self.referral_manager.get_referral_stats(user_id)
        
        # Получаем информацию о активной подписке
        user_key = user_id if user_id in self.users_db else str(user_id)
        user_data = self.users_db.get(user_key, {})
        ref_data = user_data.get("referral", {})
        active_sub = ref_data.get("active_subscription")
        
        # Формируем сообщение (HTML для корректного отображения username с _)
        text = f"<b>{t('referral_stats_title', user_lang)}</b>\n\n"
        text += f"<b>{t('referral_stats_description', user_lang)}</b>\n\n"
        text += "━━━━━━━━━━━━━━━━━━━━━━\n\n"
        
        # Показываем активную подписку
        if active_sub:
            text += f"<b>{t('referral_stats_active_subscription', user_lang)}</b>\n"
            text += f"📦 {active_sub.get('bonus_name', 'Подписка')}\n"
            try:
                start = datetime.fromisoformat(active_sub['start_date'])
                text += f"{t('referral_subscription_start', user_lang)} {start.strftime('%d.%m.%Y')}\n"
                if active_sub.get('end_date'):
                    end = datetime.fromisoformat(active_sub['end_date'])
                    now = datetime.now()
                    if now > end:
                        text += f"<i>{t('referral_subscription_expired', user_lang)}</i>\n"
                    else:
                        days_left = (end - now).days
                        if days_left == 0:
                            hours_left = int((end - now).total_seconds() // 3600)
                            text += t('referral_subscription_remaining_hours', user_lang, hours=hours_left) + "\n"
                        else:
                            text += t('referral_subscription_remaining_days', user_lang, days=days_left) + "\n"
                else:
                    text += t('referral_subscription_unlimited', user_lang) + "\n"
            except:
                pass
            text += "\n"
        else:
            text += f"<b>{t('referral_stats_no_subscription', user_lang)}</b>\n\n"
        
        text += "━━━━━━━━━━━━━━━━━━━━━━\n\n"
        text += f"<b>{t('referral_stats_clicks', user_lang)}</b> {stats['total_clicks']}\n"
        text += f"<b>{t('referral_stats_activated', user_lang)}</b> {stats['activated_count']}\n\n"
        
        # Список рефералов
        referrals = ref_data.get("referrals", [])
        activated = ref_data.get("activated_referrals", [])
        
        if referrals:
            text += f"<b>{t('referral_stats_your_referrals', user_lang)}</b>\n"
            for ref_id in referrals[-10:]:  # Последние 10
                status = "✅" if ref_id in activated else "⏳"
                # Пытаемся получить username
                ref_user = self.users_db.get(ref_id, self.users_db.get(str(ref_id), {}))
                ref_name = ref_user.get("username", ref_id)
                text += f"{status} @{ref_name}\n"
            if len(referrals) > 10:
                text += f"<i>{t('referral_stats_and_more', user_lang, count=len(referrals) - 10)}</i>\n"
        
        keyboard = [
            [InlineKeyboardButton(t('btn_back', user_lang), callback_data="healthy_trader_menu")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(
            text,
            reply_markup=reply_markup,
            parse_mode='HTML'
        )
    
    async def referral_menu_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Callback для меню рефералов (редирект на healthy_trader_menu)"""
        # Редирект на новое меню
        await self.healthy_trader_menu_callback(update, context)
    
    async def referral_menu_callback_legacy(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Callback для меню рефералов (старый вариант)"""
        query = update.callback_query
        await query.answer()
        
        user_id = str(query.from_user.id)
        user_lang = get_user_language(int(user_id), self.users_db)
        
        stats = self.referral_manager.get_referral_stats(user_id)
        ref_link = self.referral_manager.get_referral_link(user_id)
        
        menu_text = t('referral_menu_title', user_lang) + "\n\n"
        menu_text += t('referral_menu_description', user_lang) + "\n\n"
        menu_text += f"🔗 *{t('referral_your_link', user_lang)}:*\n`{ref_link}`\n\n"
        menu_text += f"📊 *{t('referral_stats_title', user_lang)}:*\n"
        menu_text += f"👥 {t('referral_total_clicks', user_lang)}: {stats['total_clicks']}\n"
        menu_text += f"✅ {t('referral_activated', user_lang)}: {stats['activated_count']}\n\n"
        menu_text += f"🎯 *{t('referral_progress', user_lang)}:*\n{stats['progress_bar']}\n"
        
        if stats['next_level']:
            menu_text += f"\n📈 {t('referral_next_bonus', user_lang, days=stats['next_level']['bonus_days'], remaining=stats['remaining'])}"
        
        keyboard = [
            [InlineKeyboardButton(t('btn_referral_copy_link', user_lang), callback_data="referral_copy_link")],
            [InlineKeyboardButton(t('btn_referral_share', user_lang), url=f"https://t.me/share/url?url={urllib.parse.quote(ref_link, safe='')}")],
        ]
        
        if stats['available_bonuses']:
            keyboard.append([InlineKeyboardButton(
                f"🎁 {t('btn_referral_claim_bonus', user_lang)}", 
                callback_data="referral_claim_bonus"
            )])
        
        keyboard.append([InlineKeyboardButton(t('btn_referral_rules', user_lang), callback_data="referral_rules")])
        keyboard.append([InlineKeyboardButton(t('btn_main_menu', user_lang), callback_data="back_to_main")])
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(
            menu_text,
            reply_markup=reply_markup,
            parse_mode='Markdown'
        )
    
    async def referral_copy_link_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Показать ссылку для копирования"""
        query = update.callback_query
        user_id = str(query.from_user.id)
        user_lang = get_user_language(int(user_id), self.users_db)
        
        ref_link = self.referral_manager.get_referral_link(user_id)
        
        await query.answer(t('referral_link_copied', user_lang), show_alert=True)
        
        # Отправляем ссылку отдельным сообщением для удобства копирования
        await context.bot.send_message(
            chat_id=query.from_user.id,
            text=f"🔗 {t('referral_your_link', user_lang)}:\n\n`{ref_link}`",
            parse_mode='Markdown'
        )
    
    async def referral_share_message_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Отправить готовое сообщение для пересылки друзьям"""
        query = update.callback_query
        user_id = str(query.from_user.id)
        user_lang = get_user_language(int(user_id), self.users_db)
        
        ref_link = self.referral_manager.get_referral_link(user_id)
        
        await query.answer()
        
        # Формируем красивое сообщение с кликабельным текстом (HTML)
        share_message = f"""🚀 <b>Хочешь торговать с умом?</b>

Присоединяйся к нашей команде трейдеров!

✅ Бесплатные сигналы
✅ Обучение торговле  
✅ Поддержка 24/7

👇 <a href="{ref_link}">НАЖМИ СЮДА ЧТОБЫ НАЧАТЬ</a>

💰 Начни зарабатывать уже сегодня!"""
        
        await context.bot.send_message(
            chat_id=query.from_user.id,
            text=share_message,
            parse_mode='HTML',
            disable_web_page_preview=False
        )
        
        # Подсказка
        await context.bot.send_message(
            chat_id=query.from_user.id,
            text="👆 <b>Перешли это сообщение друзьям!</b>",
            parse_mode='HTML'
        )
    
    async def referral_rules_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Правила реферальной программы"""
        query = update.callback_query
        await query.answer()
        
        user_id = str(query.from_user.id)
        user_lang = get_user_language(int(user_id), self.users_db)
        
        rules_text = t('referral_rules_title', user_lang) + "\n\n"
        rules_text += t('referral_rules_text', user_lang)
        
        keyboard = [
            [InlineKeyboardButton(t('btn_back', user_lang), callback_data="referral_menu")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(
            rules_text,
            reply_markup=reply_markup,
            parse_mode='Markdown'
        )
    
    async def referral_claim_bonus_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Запрос на получение бонуса"""
        query = update.callback_query
        await query.answer()
        
        user_id = str(query.from_user.id)
        user_lang = get_user_language(int(user_id), self.users_db)
        
        stats = self.referral_manager.get_referral_stats(user_id)
        available = stats.get('available_bonuses', [])
        claimed = stats.get('claimed_bonuses', [])
        
        if not available:
            await query.edit_message_text(
                t('referral_no_bonus_available', user_lang),
                parse_mode='Markdown'
            )
            return
        
        # Проверяем есть ли активная (не истёкшая) подписка
        user_key = user_id if user_id in self.users_db else str(user_id)
        user_data = self.users_db.get(user_key, {})
        ref_data = user_data.get("referral", {})
        active_sub = ref_data.get("active_subscription")
        
        has_active_subscription = False
        if active_sub and active_sub.get('end_date'):
            try:
                end_date = datetime.fromisoformat(active_sub['end_date'])
                if datetime.now() < end_date:
                    has_active_subscription = True
            except:
                pass
        
        if has_active_subscription:
            # Есть активная подписка - показываем информацию но без возможности взять новый бонус
            end_date = datetime.fromisoformat(active_sub['end_date'])
            days_left = (end_date - datetime.now()).days
            
            text = f"*{t('referral_bonus_blocked_title', user_lang)}*\n\n"
            text += f"📦 {active_sub.get('bonus_name', 'Подписка')}\n"
            if days_left > 0:
                text += t('referral_subscription_remaining_days', user_lang, days=days_left) + "\n\n"
            else:
                hours_left = int((end_date - datetime.now()).total_seconds() // 3600)
                text += t('referral_subscription_remaining_hours', user_lang, hours=hours_left) + "\n\n"
            
            text += f"*{t('referral_bonus_blocked_available', user_lang)}*\n"
            for bonus in available:
                if bonus['id'] == 'level_3' or bonus['bonus_days'] == 0:
                    text += f"• {bonus['bonus_name']}\n"
                else:
                    text += f"• {bonus['bonus_name']} ({bonus['bonus_days']} {t('days', user_lang)})\n"
            
            keyboard = [[InlineKeyboardButton(t('btn_back', user_lang), callback_data="referral_menu")]]
            reply_markup = InlineKeyboardMarkup(keyboard)
        else:
            # Нет активной подписки - можно выбрать бонус
            text = t('referral_select_bonus', user_lang) + "\n\n"
            
            keyboard = []
            for bonus in available:
                # Для менторства не показываем дни
                if bonus['id'] == 'level_3' or bonus['bonus_days'] == 0:
                    btn_text = f"🎁 {bonus['bonus_name']}"
                else:
                    btn_text = f"🎁 {bonus['bonus_name']} ({bonus['bonus_days']} дней)"
                keyboard.append([InlineKeyboardButton(btn_text, callback_data=f"claim_bonus_{bonus['id']}")])
            
            keyboard.append([InlineKeyboardButton(t('btn_back', user_lang), callback_data="referral_menu")])
            reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(
            text,
            reply_markup=reply_markup,
            parse_mode='Markdown'
        )
    
    async def claim_bonus_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработка выбора конкретного бонуса - показываем подтверждение"""
        query = update.callback_query
        await query.answer()
        
        user_id = str(query.from_user.id)
        user_lang = get_user_language(int(user_id), self.users_db)
        
        # Получаем ID бонуса из callback_data
        bonus_id = query.data.replace("claim_bonus_", "")
        
        # Находим информацию о бонусе
        bonus_info = None
        for level in REFERRAL_BONUS_LEVELS:
            if level['id'] == bonus_id:
                bonus_info = level
                break
        
        if not bonus_info:
            await query.edit_message_text("❌ Бонус не найден", parse_mode='Markdown')
            return
        
        # Показываем подтверждение
        if bonus_id == "level_3":
            text = f"🎁 *Подтверждение запроса*\n\n"
            text += f"Вы запрашиваете: *{bonus_info['bonus_name']}*\n\n"
            text += f"📝 {bonus_info['description']}\n\n"
            text += "⚠️ После получения этого бонуса ваш счёт рефералов будет обнулён!\n\n"
            text += "Подтвердить запрос?"
        else:
            text = f"🎁 *Подтверждение запроса*\n\n"
            text += f"Вы запрашиваете: *{bonus_info['bonus_name']}*\n"
            text += f"📅 Срок: {bonus_info['bonus_days']} дней\n\n"
            text += f"📝 {bonus_info['description']}\n\n"
            text += "Подтвердить запрос?"
        
        keyboard = [
            [InlineKeyboardButton("✅ Подтвердить", callback_data=f"confirm_bonus_{bonus_id}")],
            [InlineKeyboardButton("❌ Отмена", callback_data="referral_menu")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(
            text,
            reply_markup=reply_markup,
            parse_mode='Markdown'
        )
    
    async def confirm_bonus_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Подтверждение запроса бонуса"""
        query = update.callback_query
        await query.answer()
        
        user_id = str(query.from_user.id)
        user_lang = get_user_language(int(user_id), self.users_db)
        
        # Получаем ID бонуса
        bonus_id = query.data.replace("confirm_bonus_", "")
        
        # Проверяем есть ли сохранённый TradingView username
        user_key = user_id if user_id in self.users_db else str(user_id)
        user_data = self.users_db.get(user_key, {})
        ref_data = user_data.get("referral", {})
        saved_tv_username = ref_data.get("tradingview_username")
        
        if saved_tv_username:
            # Username уже есть - сразу отправляем заявку
            success, message = self.referral_manager.request_bonus(user_id, bonus_id, saved_tv_username)
            
            if success:
                await self._notify_admin_bonus_request(user_id, bonus_id)
                await query.edit_message_text(
                    "✅ *Заявка отправлена!*\n\n"
                    f"📊 TradingView: {saved_tv_username}\n\n"
                    "Мы уведомим вас когда бонус будет одобрен.",
                    parse_mode='Markdown'
                )
            else:
                await query.edit_message_text(f"❌ Ошибка: {message}", parse_mode='Markdown')
        else:
            # Запрашиваем TradingView username
            text = t('referral_enter_tv_username', user_lang)
            
            # Сохраняем состояние ожидания ввода
            if user_id not in self.broadcast_data:
                self.broadcast_data[user_id] = {}
            self.broadcast_data[user_id]['awaiting_tv_username'] = bonus_id
            
            keyboard = [[InlineKeyboardButton(t('btn_cancel', user_lang), callback_data="referral_menu")]]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await query.edit_message_text(
                text,
                reply_markup=reply_markup,
                parse_mode='Markdown'
            )
    
    async def process_tv_username(self, user_id: str, tv_username: str) -> bool:
        """Обработка введённого TradingView username"""
        # Проверяем оба варианта ключей
        int_id = int(user_id) if user_id.isdigit() else None
        broadcast_key = user_id if user_id in self.broadcast_data else int_id if int_id and int_id in self.broadcast_data else None
        
        if broadcast_key is None:
            return False
        
        bonus_id = self.broadcast_data[broadcast_key].get('awaiting_tv_username')
        if not bonus_id:
            return False
        
        # Очищаем состояние
        del self.broadcast_data[broadcast_key]['awaiting_tv_username']
        
        # Создаём заявку на бонус
        success, message = self.referral_manager.request_bonus(user_id, bonus_id, tv_username)
        
        if success:
            # Уведомляем админа
            await self._notify_admin_bonus_request(user_id, bonus_id)
        
        return success
    
    # ============================================
    # АДМИН-ПАНЕЛЬ РЕФЕРАЛОВ
    # ============================================
    
    async def admin_referral_stats_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Статистика реферальной системы для админа"""
        query = update.callback_query
        await query.answer()
        
        user_id = str(query.from_user.id)
        if user_id != self.admin_chat_id:
            return
        
        global_stats = self.referral_manager.get_global_stats()
        top_referrers = self.referral_manager.get_top_referrers(5)
        
        text = "📊 *СТАТИСТИКА РЕФЕРАЛЬНОЙ СИСТЕМЫ*\n\n"
        text += f"👥 Всего переходов: {global_stats['total_referrals']}\n"
        text += f"✅ Активировано: {global_stats['total_activated']}\n"
        text += f"🎁 Бонусов выдано: {global_stats['total_bonuses_claimed']}\n"
        text += f"⏳ Заявок в ожидании: {global_stats['pending_requests']}\n"
        text += f"📈 Конверсия: {global_stats['conversion_rate']:.1f}%\n\n"
        
        if top_referrers:
            text += "*🏆 ТОП РЕФЕРЕРОВ:*\n"
            for i, ref in enumerate(top_referrers, 1):
                text += f"{i}. @{ref['username']} — {ref['activated_count']} друзей\n"
        
        keyboard = [
            [InlineKeyboardButton("📋 Заявки на бонус", callback_data="admin_referral_requests")],
            [InlineKeyboardButton("🔙 Назад", callback_data="admin_panel")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(
            text,
            reply_markup=reply_markup,
            parse_mode='Markdown'
        )
    
    async def admin_referral_requests_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Список заявок на бонус для админа"""
        query = update.callback_query
        await query.answer()
        
        user_id = str(query.from_user.id)
        if user_id != self.admin_chat_id:
            return
        
        pending = self.referral_manager.get_pending_bonus_requests()
        
        if not pending:
            text = "✅ *Нет ожидающих заявок на бонус*"
            keyboard = [[InlineKeyboardButton("🔙 Назад", callback_data="admin_referral_stats")]]
        else:
            text = f"📋 *ЗАЯВКИ НА БОНУС ({len(pending)})*\n\n"
            keyboard = []
            
            for req in pending[:10]:  # Ограничиваем до 10
                bonus_name = req['bonus_info']['bonus_name'] if req['bonus_info'] else req['bonus_id']
                text += f"👤 @{req['username']} (ID: {req['user_id']})\n"
                text += f"   🎁 {bonus_name}\n"
                text += f"   📊 TV: {req['tradingview_username'] or 'Не указан'}\n\n"
                
                keyboard.append([
                    InlineKeyboardButton(f"✅ {req['username'][:10]}", callback_data=f"approve_bonus_{req['user_id']}"),
                    InlineKeyboardButton(f"❌ {req['username'][:10]}", callback_data=f"reject_bonus_{req['user_id']}")
                ])
            
            keyboard.append([InlineKeyboardButton("🔙 Назад", callback_data="admin_referral_stats")])
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(
            text,
            reply_markup=reply_markup,
            parse_mode='Markdown'
        )
    
    async def approve_bonus_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Одобрение заявки на бонус"""
        query = update.callback_query
        
        admin_id = str(query.from_user.id)
        if admin_id != self.admin_chat_id:
            await query.answer("Нет прав", show_alert=True)
            return
        
        target_user_id = query.data.replace("approve_bonus_", "")
        
        # Получаем информацию о pending бонусе до одобрения
        user_key = target_user_id if target_user_id in self.users_db else str(target_user_id)
        user_data = self.users_db.get(user_key, {})
        ref_data = user_data.get("referral", {})
        pending_bonus = ref_data.get("pending_bonus_request")
        
        success, message = self.referral_manager.approve_bonus(target_user_id, admin_id)
        
        if success:
            await query.answer("✅ Бонус одобрен!", show_alert=True)
            
            # Уведомляем пользователя
            try:
                user_lang = get_user_language(int(target_user_id), self.users_db)
                
                if pending_bonus == "level_3":
                    # Специальное сообщение для менторства
                    mentorship_text = """🎉 *ПОЗДРАВЛЯЕМ!*

Вы получили доступ к *Менторству + Софту*!

✅ Вам будет предоставлен доступ к индикатору *Black Mirror Ultra*

📞 Для обсуждения деталей менторства и получения поддержки, пожалуйста, напишите нам:"""
                    
                    keyboard = [[InlineKeyboardButton("✍️ Написать", url="https://t.me/kaktotakxm")]]
                    reply_markup = InlineKeyboardMarkup(keyboard)
                    
                    await context.bot.send_message(
                        chat_id=int(target_user_id),
                        text=mentorship_text,
                        reply_markup=reply_markup,
                        parse_mode='Markdown'
                    )
                else:
                    # Стандартное сообщение для подписки на индикатор
                    await context.bot.send_message(
                        chat_id=int(target_user_id),
                        text=t('referral_bonus_approved', user_lang),
                        parse_mode='Markdown'
                    )
            except Exception as e:
                logger.error(f"Ошибка уведомления пользователя о бонусе: {e}")
        else:
            await query.answer(f"❌ Ошибка: {message}", show_alert=True)
        
        # Обновляем список заявок
        await self.admin_referral_requests_callback(update, context)
    
    async def reject_bonus_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Отклонение заявки на бонус"""
        query = update.callback_query
        
        admin_id = str(query.from_user.id)
        if admin_id != self.admin_chat_id:
            await query.answer("Нет прав", show_alert=True)
            return
        
        target_user_id = query.data.replace("reject_bonus_", "")
        
        success, message = self.referral_manager.reject_bonus(target_user_id, admin_id)
        
        if success:
            await query.answer("❌ Заявка отклонена", show_alert=True)
            
            # Уведомляем пользователя
            try:
                user_lang = get_user_language(int(target_user_id), self.users_db)
                await context.bot.send_message(
                    chat_id=int(target_user_id),
                    text=t('referral_bonus_rejected', user_lang),
                    parse_mode='Markdown'
                )
            except Exception as e:
                logger.error(f"Ошибка уведомления пользователя об отклонении: {e}")
        else:
            await query.answer(f"❌ Ошибка: {message}", show_alert=True)
        
        # Обновляем список заявок
        await self.admin_referral_requests_callback(update, context)
    
    # ============================================
    # НАВИГАЦИЯ
    # ============================================
    
    async def check_subscription_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработчик проверки подписки после возврата из канала"""
        query = update.callback_query
        await query.answer()
        
        user_id = query.from_user.id
        user_lang = get_user_language(user_id, self.users_db)
        
        # Проверяем подписку на канал (для админа пропускаем проверку)
        if str(user_id) != self.admin_chat_id:
            is_subscribed = await self.check_channel_subscription(user_id, context)
            if not is_subscribed:
                # Показываем сообщение о необходимости подписки
                subscription_text = f"""
{t('subscription_required_title', user_lang)}

{t('subscription_required_text', user_lang)}
                """.strip()
                
                keyboard = [[InlineKeyboardButton(t('btn_subscribe', user_lang), url=self.channel_url)]]
                reply_markup = InlineKeyboardMarkup(keyboard)
                
                try:
                    msg = await query.edit_message_text(
                        subscription_text,
                        reply_markup=reply_markup,
                        parse_mode='Markdown'
                    )
                    self._save_message_id(user_id, msg.message_id)
                except BadRequest as e:
                    if "message is not modified" in str(e).lower():
                        pass
                    else:
                        logger.error(f"Error editing subscription message: {e}")
                return
        
        # Если подписан или админ - показываем главное меню
        await self._send_main_menu(user_id, context, user_lang, query=query)

    async def _send_main_menu(self, user_id: int, context: ContextTypes.DEFAULT_TYPE, user_lang: str, query=None):
        """Отправка главного меню пользователю с приветственным фото"""
        welcome_message = f"""
{t('welcome_greeting', user_lang)}

{t('welcome_description', user_lang)}

{t('welcome_evolution_title', user_lang)}

{t('welcome_level_1', user_lang)}
{t('welcome_level_2', user_lang)}
{t('welcome_level_3', user_lang)}
{t('welcome_level_4', user_lang)}

{t('welcome_conclusion', user_lang)}
        """.strip()
        
        keyboard = [
            [InlineKeyboardButton("🎓 Академия Здравого Трейдера", web_app=WebAppInfo(url="https://tradeacademy.onrender.com"))],
            [InlineKeyboardButton(t('btn_healthy_trader', user_lang), callback_data="healthy_trader_menu")],
            [InlineKeyboardButton(t('btn_language', user_lang), callback_data="change_language")]
        ]
        if str(user_id) == self.admin_chat_id:
            keyboard.append([InlineKeyboardButton(t('btn_admin_panel', user_lang), callback_data="admin_panel")])
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        # Если вызвано из коллбэка - пытаемся удалить старое сообщение
        if query:
            try:
                await query.delete_message()
            except Exception as e:
                logger.debug(f"Не удалось удалить старое сообщение: {e}")
        
        # Очищаем старые сообщения бота перед отправкой нового меню
        await self._delete_user_last_messages(user_id, context, limit=5)

        # Отправляем фото с кнопками
        import os
        photo_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'welcome.jpg')
        
        try:
            if os.path.exists(photo_path):
                with open(photo_path, 'rb') as photo:
                    msg = await context.bot.send_photo(
                        chat_id=user_id,
                        photo=photo,
                        caption=welcome_message,
                        reply_markup=reply_markup,
                        parse_mode='Markdown'
                    )
                    self._save_message_id(user_id, msg.message_id)
            else:
                # Если фото нет, отправляем только текст
                msg = await context.bot.send_message(
                    chat_id=user_id,
                    text=welcome_message,
                    reply_markup=reply_markup,
                    parse_mode='Markdown'
                )
                self._save_message_id(user_id, msg.message_id)
        except Exception as e:
            logger.error(f"Ошибка при отправке главного меню: {e}")
            # Fallback на текстовое сообщение
            try:
                msg = await context.bot.send_message(
                    chat_id=user_id,
                    text=welcome_message,
                    reply_markup=reply_markup,
                    parse_mode='Markdown'
                )
                self._save_message_id(user_id, msg.message_id)
            except Exception as e2:
                logger.error(f"Критическая ошибка отправки меню: {e2}")

    async def handle_chat_member_update(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Автоматическая проверка подписки при событии в канале"""
        result = update.chat_member
        if not result or not result.chat or not result.chat.username:
            return
            
        if result.chat.username.replace("@", "").lower() != self.channel_username.replace("@", "").lower():
            return

        user_id = result.from_user.id
        status = result.new_chat_member.status
        
        # Если статус изменился на "участник" (был кикнут, вышел или новый)
        if status in ['member', 'administrator', 'creator']:
            # Проверяем, не отправляли ли мы уже приветствие недавно (чтобы избежать дублей)
            # Для простоты просто логгируем и отправляем
            logger.info(f"User {user_id} automatically joined channel {self.channel_username}")
            user_lang = get_user_language(user_id, self.users_db)
            # Удаляем старые сообщения (включая просьбу о подписке)
            await self._delete_user_last_messages(user_id, context, limit=5)
            await self._send_main_menu(user_id, context, user_lang)
    
    async def promocodes_menu_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработчик меню промокодов"""
        query = update.callback_query
        await query.answer()
        
        user_id = query.from_user.id
        user_lang = get_user_language(user_id, self.users_db)
        
        menu_text = f"""
{t('promocodes_menu_title', user_lang)}

{t('promocodes_menu_description', user_lang)}
        """.strip()
        
        keyboard = [
            [InlineKeyboardButton(t('promocode_1_title', user_lang), url="https://u3.shortink.io/register?utm_campaign=827841&utm_source=affiliate&utm_medium=sr&a=CQQJpdvm2ya9dU&ac=min&code=WELCOME50")],
            [InlineKeyboardButton(t('promocode_2_title', user_lang), url="https://u3.shortink.io/register?utm_campaign=827841&utm_source=affiliate&utm_medium=sr&a=CQQJpdvm2ya9dU&ac=tggg&code=50START")],
            [InlineKeyboardButton(t('promocode_3_title', user_lang), url="https://u3.shortink.io/register?utm_campaign=827841&utm_source=affiliate&utm_medium=sr&a=CQQJpdvm2ya9dU&ac=proba&code=OUJ012")],
            [InlineKeyboardButton(t('promocode_4_title', user_lang), url="https://u3.shortink.io/register?utm_campaign=827841&utm_source=affiliate&utm_medium=sr&a=CQQJpdvm2ya9dU&ac=test-indikator&code=DENCHIK60")],
            [InlineKeyboardButton(t('promocode_5_title', user_lang), url="https://u3.shortink.io/register?utm_campaign=827841&utm_source=affiliate&utm_medium=sr&a=CQQJpdvm2ya9dU&ac=test-indikator132&code=VDN436")],
            [InlineKeyboardButton(t('btn_back', user_lang), callback_data="trader_menu")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(
            menu_text,
            reply_markup=reply_markup,
            parse_mode='Markdown'
        )
    
    async def back_to_main_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Возврат в главное меню"""
        query = update.callback_query
        await query.answer()
        
        user_id = query.from_user.id
        user_lang = get_user_language(user_id, self.users_db)
        
        # Формируем приветственное сообщение
        await self._send_main_menu(user_id, context, user_lang, query=query)
    
    async def change_language_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Смена языка из главного меню"""
        query = update.callback_query
        await query.answer()
        
        user_id = query.from_user.id
        user_lang = get_user_language(user_id, self.users_db)
        
        keyboard = get_language_keyboard()
        # Добавляем кнопку назад
        keyboard.append([InlineKeyboardButton(t('btn_back', user_lang), callback_data="back_to_main")])
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        if query.message.photo:
            await query.delete_message()
            await context.bot.send_message(
                chat_id=user_id,
                text=t('language_select', user_lang),
                reply_markup=reply_markup,
                parse_mode='Markdown'
            )
        else:
            await query.edit_message_text(
            t('language_select', user_lang),
            reply_markup=reply_markup,
            parse_mode='Markdown'
        )
    
    async def admin_panel_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Кнопка Админ-панель из главного меню"""
        query = update.callback_query
        await query.answer()
        
        user_id = query.from_user.id
        
        # Проверяем, что это администратор
        if str(user_id) != self.admin_chat_id:
            await query.edit_message_text(
                "❌ У вас нет прав для доступа к этому разделу",
                parse_mode='Markdown'
            )
            return
        
        # Статистика пользователей
        total_users = len(self.users_db)
        verified_users = len([u for u in self.users_db.values() if u.get('verified')])
        with_id = len([u for u in self.users_db.values() if u.get('pocket_option_id')])
        with_deposit = len([u for u in self.users_db.values() if u.get('deposited')])
        motivation_status = (
            "🔕 Ручной режим (авто отключено)" if not self.motivation_auto_enabled
            else f"🔔 Авто каждые {self.motivation_interval_hours} ч."
        )
        
        # Статистика по датам
        today = datetime.now().strftime('%Y-%m-%d')
        new_today = len([u for u in self.users_db.values() if u.get('registered_at', '')[:10] == today])
        week_ago = (datetime.now() - timedelta(days=7)).strftime('%Y-%m-%d')
        new_week = len([u for u in self.users_db.values() if u.get('registered_at', '')[:10] >= week_ago])
        
        admin_text = f"""
⚙️ *АДМИН-ПАНЕЛЬ*

📊 *Статистика пользователей:*
• Всего: {total_users}
• Верифицированы: {verified_users}
• С ID PocketOption: {with_id}
• С депозитом: {with_deposit}

📈 *За период:*
• Сегодня: +{new_today}
• За неделю: +{new_week}

📧 *Рассылки:* {motivation_status}

🚫 *Заблокировано:* {len(self.blocked_users)}
        """.strip()
        
        # Статистика рефералов
        ref_stats = self.referral_manager.get_global_stats()
        pending_bonuses = ref_stats.get('pending_requests', 0)
        
        keyboard = [
            [InlineKeyboardButton("📊 Статистика", callback_data="admin_stats")],
            [InlineKeyboardButton(f"👥 Рефералы ({pending_bonuses} заявок)", callback_data="admin_referral_stats")],
            [InlineKeyboardButton("📤 Экспорт CSV", callback_data="admin_export_users")],
            [InlineKeyboardButton("📧 Новая рассылка", callback_data="admin_new_broadcast")],
            [InlineKeyboardButton("📋 События", callback_data="admin_events")],
            [InlineKeyboardButton("🗑 Очистка статистики", callback_data="admin_clear_stats")],
            [InlineKeyboardButton("🔄 Обновить", callback_data="admin_panel")],
            [InlineKeyboardButton(t('btn_main_menu', 'ru'), callback_data="back_to_main")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        if query.message.photo:
            await query.delete_message()
            await context.bot.send_message(
                chat_id=user_id,
                text=admin_text,
                reply_markup=reply_markup,
                parse_mode='Markdown'
            )
        else:
            await query.edit_message_text(
                admin_text,
                reply_markup=reply_markup,
                parse_mode='Markdown'
            )
        
        # Обновляем callback_data для обновления
        await query.answer()
        
    async def check_access_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Кнопка Проверить доступ"""
        query = update.callback_query
        await query.answer()
        
        user_id = query.from_user.id
        user_lang = get_user_language(user_id, self.users_db)
        current_time = datetime.now()
        
        # Проверяем, не заблокирован ли пользователь
        if user_id in self.blocked_users:
            blocked_text = f"""
{t('blocked_title', user_lang)}

{t('blocked_reason', user_lang)}

{t('blocked_permanent', user_lang)}

{t('blocked_contact', user_lang)}
{t('blocked_user_id', user_lang).format(user_id)}
            """.strip()
            
            await query.edit_message_text(
                blocked_text,
                parse_mode='Markdown'
            )
            return
        
        if user_id not in self.users_db:
            await query.edit_message_text(
                t('error_not_registered', user_lang),
                parse_mode='Markdown'
            )
            return
            
        user_data = self.users_db[user_id]
        
        # Проверяем историю нажатий кнопки
        if user_id not in self.access_check_history:
            self.access_check_history[user_id] = []
        
        # Добавляем текущее время
        self.access_check_history[user_id].append(current_time)
        
        # Очищаем старые записи (старше 1 часа)
        hour_ago = current_time.timestamp() - 3600
        self.access_check_history[user_id] = [
            ts for ts in self.access_check_history[user_id] 
            if ts.timestamp() > hour_ago
        ]
        
        # Проверяем количество повторных нажатий
        recent_checks = len(self.access_check_history[user_id])
        
        # Если пользователь НЕ выполнил необходимые действия и делает повторные проверки
        if not user_data.get('verified') and recent_checks > 1:
            # Проверяем, выполнил ли пользователь действия с последней проверки
            last_check = self.access_check_history[user_id][-2] if recent_checks > 1 else None
            
            if last_check:
                time_since_last = (current_time - last_check).total_seconds()
                
                # Если прошло мало времени и действия не выполнены
                if time_since_last < self.check_cooldown:
                    # Увеличиваем счетчик предупреждений
                    if user_id not in self.user_warnings:
                        self.user_warnings[user_id] = 0
                    self.user_warnings[user_id] += 1
                    
                    warning_count = self.user_warnings[user_id]
                    
                    # Проверяем, не превышен ли лимит предупреждений (блокировка после 2-го предупреждения)
                    if warning_count >= self.max_warnings:
                        # БЛОКИРУЕМ ПОЛЬЗОВАТЕЛЯ
                        self.blocked_users.add(user_id)
                        
                        # Уведомляем администратора о блокировке
                        username_safe = user_data['username'].replace('*', '').replace('_', '').replace('`', '')
                        telegram_username = update.effective_user.username or 'без username'
                        telegram_username_safe = telegram_username.replace('*', '').replace('_', '').replace('`', '')
                        
                        admin_message = f"""🚨 ПОЛЬЗОВАТЕЛЬ ЗАБЛОКИРОВАН!

👤 Пользователь: {username_safe}
🆔 ID: {user_id}
📧 Telegram: @{telegram_username_safe}

⚠️ Причина: Превышение лимита предупреждений (2/2 - после второго предупреждения)
🔄 Проверок: {recent_checks} раз подряд

⏰ Время блокировки: {current_time.strftime('%H:%M:%S %d.%m.%Y')}

💡 Для разблокировки используйте: /unblock_user {user_id}"""
                        
                        try:
                            requests.post(
                                f"https://api.telegram.org/bot{self.bot_token}/sendMessage",
                                data={
                                    'chat_id': self.admin_chat_id,
                                    'text': admin_message
                                }
                            )
                        except Exception as e:
                            logger.error(f"Ошибка уведомления админа о блокировке: {e}")
                        
                        # Логируем блокировку
                        logger.warning(f"🚨 ПОЛЬЗОВАТЕЛЬ ЗАБЛОКИРОВАН: {user_data['username']} (ID: {user_id}) - Превышение лимита предупреждений")
                        self._add_admin_event('blocked', user_id, f"⛔ @{user_data['username']} ЗАБЛОКИРОВАН за {recent_checks} проверок подряд")
                        
                        # Сообщение о блокировке пользователю НА ЕГО ЯЗЫКЕ
                        blocked_text = f"""
{t('blocked_title', user_lang)}

{t('blocked_reason', user_lang)}

{t('blocked_permanent', user_lang)}

{t('blocked_contact', user_lang)}
{t('blocked_user_id', user_lang).format(user_id)}
                        """.strip()
                        
                        await query.edit_message_text(
                            blocked_text,
                            parse_mode='Markdown'
                        )
                        return
                    
                    # Показываем предупреждение с эскалацией
                    if warning_count == 1:
                        warning_level = t('warning_first_title', user_lang)
                        warning_text = t('warning_block_threat', user_lang)
                    else:  # warning_count == 2 (последнее предупреждение)
                        warning_level = t('warning_last_title', user_lang)
                        warning_text = t('warning_block_threat', user_lang)
                    
                    # Базовое сообщение
                    warning_message = f"""
{warning_level}

{t('warning_checks_count', user_lang).format(recent_checks)}

{warning_text}

{t('warning_status_wont_change', user_lang)}

{t('warning_steps_required', user_lang).format(self.min_deposit)}

{t('warning_cooldown', user_lang).format(int((self.check_cooldown - time_since_last) / 60))}

{t('warning_advice', user_lang)}
                    """.strip()
                    
                    # Дополнительное предупреждение для второго предупреждения - убрано для упрощения
                    # Вся необходимая информация уже в warning_message выше
                    
                    keyboard = [
                        [InlineKeyboardButton(t('btn_registration', user_lang), url=self.referral_link)],
                        [InlineKeyboardButton(t('btn_support', user_lang), url="https://t.me/kaktotakxm")],
                        [InlineKeyboardButton(t('btn_back', user_lang), callback_data="back_to_start")]
                    ]
                    reply_markup = InlineKeyboardMarkup(keyboard)
                    
                    await query.edit_message_text(
                        warning_message,
                        reply_markup=reply_markup,
                        parse_mode='Markdown'
                    )
                    return
        
        # Обычное сообщение со статусом
        referral_status = t('access_referral_used', user_lang) if user_data.get('referral_used') else t('access_referral_not_used', user_lang)
        deposit_status = t('access_deposit_confirmed', user_lang) if user_data.get('deposited') else t('access_deposit_not_confirmed', user_lang)
        account_id = user_data.get('pocket_option_id', t('access_id_not_sent', user_lang))
        access_status = t('access_active', user_lang) if user_data.get('verified') else t('access_not_granted', user_lang)
        
        registration_date = (user_data.get('registered_at') or '')[:10] or '-'

        status_message = f"""
{t('access_status_title', user_lang)}

{t('access_user', user_lang).format(user_data['username'])}
{t('access_registration', user_lang).format(registration_date)}
{t('access_referral_link', user_lang).format(referral_status)}
{t('access_deposit', user_lang).format(deposit_status)}
{t('access_account_id', user_lang).format(account_id)}
{t('access_status', user_lang).format(access_status)}

        """.strip()
        
        if user_data.get('verified'):
            status_message += t('access_granted_message', user_lang)
            # Сбрасываем историю проверок при успешном доступе
            self.access_check_history[user_id] = []
        else:
            status_message += t('access_not_granted_message', user_lang).format(self.min_deposit)
            
            # Добавляем информацию о повторных проверках
            if recent_checks > 1:
                status_message += t('access_checks_info', user_lang).format(recent_checks)
        
        keyboard = [
            [InlineKeyboardButton(t('btn_registration', user_lang), url=self.referral_link)],
            [InlineKeyboardButton(t('btn_support', user_lang), url="https://t.me/kaktotakxm")],
            [InlineKeyboardButton(t('btn_back', user_lang), callback_data="back_to_start")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(
            status_message,
            reply_markup=reply_markup,
            parse_mode='Markdown'
        )
        
    async def back_to_start_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Кнопка Назад - возврат в главное меню"""
        query = update.callback_query
        await query.answer()
        
        user_id = query.from_user.id
        user_lang = get_user_language(user_id, self.users_db)
        
        # Формируем приветственное сообщение
        welcome_message = f"""
{t('welcome_greeting', user_lang)}

{t('welcome_description', user_lang)}

{t('welcome_evolution_title', user_lang)}

{t('welcome_level_1', user_lang)}
{t('welcome_level_2', user_lang)}
{t('welcome_level_3', user_lang)}
{t('welcome_level_4', user_lang)}

{t('welcome_conclusion', user_lang)}
        """.strip()
        
        # Новая структура главного меню
        keyboard = [
            [InlineKeyboardButton("🎓 Академия Здравого Трейдера", web_app=WebAppInfo(url="https://tradeacademy.onrender.com"))],
            [InlineKeyboardButton(t('btn_healthy_trader', user_lang), callback_data="healthy_trader_menu")],
            [InlineKeyboardButton(t('btn_language', user_lang), callback_data="change_language")]
        ]
        # Добавляем кнопку админ-панели только для администратора
        if str(user_id) == self.admin_chat_id:
            keyboard.append([InlineKeyboardButton(t('btn_admin_panel', user_lang), callback_data="admin_panel")])
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        # Удаляем текущее сообщение меню трейдера и предыдущие сообщения бота (включая фото)
        try:
            await query.delete_message()
        except Exception as e:
            logger.debug(f"Не удалось удалить текущее сообщение: {e}")
        
        # Удаляем предыдущие сообщения бота (включая фото)
        await self._delete_user_last_messages(user_id, context, limit=10)
        
        # Отправляем фото отдельно, потом текст с кнопками
        import os
        photo_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'welcome.jpg')
        try:
            # Сначала отправляем фото
            if os.path.exists(photo_path):
                with open(photo_path, 'rb') as photo:
                    photo_msg = await context.bot.send_photo(
                        chat_id=user_id,
                        photo=photo
                    )
                    self._save_message_id(user_id, photo_msg.message_id)
                    logger.info(f"✅ Отправлено фото welcome.jpg пользователю {user_id}")
            else:
                logger.error(f"❌ Файл welcome.jpg не найден по пути: {photo_path}")
            # Потом отправляем текст с кнопками
            text_msg = await context.bot.send_message(
                chat_id=user_id,
                text=welcome_message,
                reply_markup=reply_markup,
                parse_mode='Markdown'
            )
            self._save_message_id(user_id, text_msg.message_id)
        except FileNotFoundError:
            logger.error(f"❌ Файл welcome.jpg не найден по пути: {photo_path}")
            # Если фото нет, отправляем только текст
            text_msg = await context.bot.send_message(
                chat_id=user_id,
                text=welcome_message,
                reply_markup=reply_markup,
                parse_mode='Markdown'
            )
            self._save_message_id(user_id, text_msg.message_id)
        except Exception as e:
            logger.error(f"❌ Ошибка отправки приветствия: {e}", exc_info=True)
            text_msg = await context.bot.send_message(
                chat_id=user_id,
                text=welcome_message,
                reply_markup=reply_markup,
                parse_mode='Markdown'
            )
            self._save_message_id(user_id, text_msg.message_id)
        
    async def language_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Команда /language - выбор языка"""
        user_id = update.effective_user.id
        user_lang = get_user_language(user_id, self.users_db)
        
        keyboard = get_language_keyboard()
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(
            t('language_select', user_lang),
            reply_markup=reply_markup,
            parse_mode='Markdown'
        )
    
    async def language_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработчик выбора языка"""
        try:
            query = update.callback_query
            await query.answer()
            
            user_id = query.from_user.id
            # Используем имя пользователя, если нет username
            username = query.from_user.username or (query.from_user.first_name or "User")
            
            logger.info(f"🌐 LANGUAGE CALLBACK TRIGGERED - User: {username} (ID: {user_id}), callback_data: {query.data}")
            
            # Извлекаем код языка из callback_data (формат: "lang_ru", "lang_en" и т.д.)
            if query.data.startswith("lang_"):
                lang_code = query.data[5:]  # Убираем префикс "lang_"
                
                # Проверяем, был ли это первый выбор языка (новый пользователь)
                # Проверяем оба варианта ключей (int и str)
                user_id_str = str(user_id)
                user_data = self.users_db.get(user_id, self.users_db.get(user_id_str, {}))
                is_first_language_selection = not user_data or 'language' not in user_data
                
                # Устанавливаем язык пользователя
                if set_user_language(user_id, self.users_db, lang_code):
                    self._save_users_db()
                    # Отправляем подтверждение на новом языке
                    confirmation_text = t('language_changed', lang_code)
                    await query.edit_message_text(
                        confirmation_text,
                        parse_mode='Markdown'
                    )
                
                # Если это первый выбор языка - уведомляем администратора (но не для самого админа)
                if is_first_language_selection and str(user_id) != self.admin_chat_id:
                    logger.info(f"🆕 Новый пользователь выбрал язык: {username} (ID: {user_id}) - {lang_code}")
                    self._add_admin_event('new_user', user_id, f"Новый пользователь @{username} выбрал язык: {lang_code}")
                    await self.notify_admin_new_user(user_id, username, update)
                
                # Через 2 секунды проверяем подписку (кроме админа)
                await asyncio.sleep(2)
                
                # Проверяем подписку на канал (для админа пропускаем проверку)
                if str(user_id) != self.admin_chat_id:
                    is_subscribed = await self.check_channel_subscription(user_id, context)
                    if not is_subscribed:
                        # Показываем сообщение о необходимости подписки
                        subscription_text = f"""
{t('subscription_required_title', lang_code)}

{t('subscription_required_text', lang_code)}
                        """.strip()
                        
                        keyboard = [
                            [InlineKeyboardButton(t('btn_subscribe', lang_code), url=self.channel_url)],
                            [InlineKeyboardButton(t('btn_check_access', lang_code), callback_data="check_subscription")]
                        ]
                        reply_markup = InlineKeyboardMarkup(keyboard)
                        
                        await context.bot.send_message(
                            chat_id=query.from_user.id,
                            text=subscription_text,
                            reply_markup=reply_markup,
                            parse_mode='Markdown'
                        )
                        return
                
                # Если подписан или админ - показываем главное меню
                welcome_message = f"""
{t('welcome_greeting', lang_code)}

{t('welcome_description', lang_code)}

{t('welcome_evolution_title', lang_code)}

{t('welcome_level_1', lang_code)}
{t('welcome_level_2', lang_code)}
{t('welcome_level_3', lang_code)}
{t('welcome_level_4', lang_code)}

{t('welcome_conclusion', lang_code)}
                """.strip()
                
                # Новая структура главного меню
                keyboard = [
                    [InlineKeyboardButton("🎓 Академия Здравого Трейдера", web_app=WebAppInfo(url="https://tradeacademy.onrender.com"))],
                    [InlineKeyboardButton(t('btn_healthy_trader', lang_code), callback_data="healthy_trader_menu")],
                    [InlineKeyboardButton(t('btn_language', lang_code), callback_data="change_language")]
                ]
                # Добавляем кнопку админ-панели только для администратора
                if str(user_id) == self.admin_chat_id:
                    keyboard.append([InlineKeyboardButton(t('btn_admin_panel', lang_code), callback_data="admin_panel")])
                reply_markup = InlineKeyboardMarkup(keyboard)
                
                # Отправляем фото отдельно, потом текст с кнопками
                try:
                    # Сначала отправляем фото
                    with open('welcome.jpg', 'rb') as photo:
                        await context.bot.send_photo(
                            chat_id=query.from_user.id,
                            photo=photo
                        )
                    # Потом отправляем текст с кнопками
                    await context.bot.send_message(
                        chat_id=query.from_user.id,
                        text=welcome_message,
                        reply_markup=reply_markup,
                        parse_mode='Markdown'
                    )
                except FileNotFoundError:
                    logger.error("Файл welcome.jpg не найден")
                    # Если фото нет, отправляем только текст
                    await context.bot.send_message(
                        chat_id=query.from_user.id,
                        text=welcome_message,
                        reply_markup=reply_markup,
                        parse_mode='Markdown'
                    )
                except Exception as e:
                    logger.error(f"Ошибка отправки приветствия: {e}")
                    await context.bot.send_message(
                        chat_id=query.from_user.id,
                        text=welcome_message,
                        reply_markup=reply_markup,
                        parse_mode='Markdown'
                    )

        except Exception as e:
            logger.error(f"🚨 КРИТИЧЕСКАЯ ОШИБКА в language_callback: {e}", exc_info=True)
            try:
                await update.callback_query.answer("❌ Произошла ошибка при выборе языка", show_alert=True)
            except:
                pass
    
    async def choose_language_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработчик кнопки выбора языка из меню"""
        query = update.callback_query
        await query.answer()
        
        user_id = query.from_user.id
        user_lang = get_user_language(user_id, self.users_db)
        
        keyboard = get_language_keyboard()
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(
            t('language_select', user_lang),
            reply_markup=reply_markup,
            parse_mode='Markdown'
        )
    
    async def handle_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработка текстовых сообщений"""
        # Проверяем, что у нас есть пользователь
        if not update.effective_user:
            logger.error("Получено сообщение без информации о пользователе")
            return
            
        user_id = update.effective_user.id
        user_lang = get_user_language(user_id, self.users_db)
        
        logger.info(f"📨 Получено сообщение от пользователя {user_id}")
        
        # Проверяем, если админ в режиме создания рассылки
        logger.info(f"🔍 Проверяем режим рассылки: user_id={user_id}, admin_chat_id={self.admin_chat_id}, в режиме рассылки={user_id in self.broadcast_data}")
        if str(user_id) == self.admin_chat_id and user_id in self.broadcast_data:
            logger.info(f"🔔 Админ {user_id} в режиме рассылки, обрабатываем сообщение")
            await self.handle_broadcast_message(update, context)
            return
        
        # Проверяем, есть ли текст в сообщении (только для обычных пользователей)
        if not update.message.text:
            # Если нет текста, но есть фото/документ/другое - игнорируем
            if update.message.photo or update.message.document or update.message.video or update.message.audio:
                await update.message.reply_text(
                    t('error_unknown_message', user_lang),
                    parse_mode='Markdown'
                )
            return
        
        message_text = update.message.text.strip()
        
        # Проверяем ожидание TradingView username для реферального бонуса
        user_id_str = str(user_id)
        # Проверяем оба варианта ключей (int и str)
        broadcast_key = user_id if user_id in self.broadcast_data else user_id_str if user_id_str in self.broadcast_data else None
        if broadcast_key and self.broadcast_data[broadcast_key].get('awaiting_tv_username'):
            success = await self.process_tv_username(user_id_str, message_text)
            if success:
                await update.message.reply_text(
                    t('referral_bonus_request_sent', user_lang) if 'referral_bonus_request_sent' in TEXTS else 
                    "✅ *Заявка отправлена!*\n\nМы уведомим вас когда бонус будет одобрен.",
                    parse_mode='Markdown'
                )
            else:
                await update.message.reply_text(
                    "❌ Ошибка при отправке заявки. Попробуйте ещё раз.",
                    parse_mode='Markdown'
                )
            return
        
        # Проверяем если это ID аккаунта PocketOption (с PO или без)
        if (message_text.upper().startswith('PO') and len(message_text) >= 5) or \
           (message_text.isdigit() and len(message_text) >= 5):
            await self.handle_pocket_option_id(user_id, message_text, update)
        else:
            # Обычное сообщение - проверяем предупреждения
            await self.handle_random_message(user_id, update, user_lang)
            
    async def handle_random_message(self, user_id: int, update: Update, user_lang: str):
        """Обработка рандомных сообщений с системой предупреждений"""
        # Проверяем, не заблокирован ли пользователь
        if user_id in self.blocked_users:
            blocked_text = f"""
{t('blocked_title', user_lang)}

{t('blocked_reason', user_lang)}

{t('blocked_permanent', user_lang)}

{t('blocked_contact', user_lang)}
{t('blocked_user_id', user_lang).format(user_id)}
            """.strip()
            
            await update.message.reply_text(
                blocked_text,
                parse_mode='Markdown'
            )
            return
        
        if user_id not in self.users_db:
            await update.message.reply_text(
                t('error_not_registered', user_lang),
                parse_mode='Markdown'
            )
            return
        
        user_data = self.users_db[user_id]
        current_time = datetime.now()
        
        # Добавляем текущее сообщение в историю
        if user_id not in self.random_message_history:
            self.random_message_history[user_id] = []
        
        self.random_message_history[user_id].append(current_time)
        
        # Оставляем только последние 10 сообщений
        self.random_message_history[user_id] = self.random_message_history[user_id][-10:]
        
        # Проверяем последние сообщения
        recent_messages = [
            msg_time for msg_time in self.random_message_history[user_id]
            if (current_time - msg_time).total_seconds() < self.random_message_cooldown
        ]
        
        # Если есть несколько сообщений за короткое время
        if len(recent_messages) >= 2:
            # Увеличиваем счетчик предупреждений
            if user_id not in self.user_warnings:
                self.user_warnings[user_id] = 0
            self.user_warnings[user_id] += 1
            
            warning_count = self.user_warnings[user_id]
            
            # Проверяем, не превышен ли лимит предупреждений
            if warning_count >= self.max_warnings:
                # БЛОКИРУЕМ ПОЛЬЗОВАТЕЛЯ
                self.blocked_users.add(user_id)
                
                # Уведомляем администратора
                username_safe = user_data['username'].replace('*', '').replace('_', '').replace('`', '')
                telegram_username = update.effective_user.username or 'без username'
                telegram_username_safe = telegram_username.replace('*', '').replace('_', '').replace('`', '')
                
                admin_message = f"""🚨 ПОЛЬЗОВАТЕЛЬ ЗАБЛОКИРОВАН!

👤 Пользователь: {username_safe}
🆔 ID: {user_id}
📧 Telegram: @{telegram_username_safe}

⚠️ Причина: Превышение лимита предупреждений (2/2) - рандомные сообщения
🔄 Сообщений: {len(recent_messages)} раз подряд

⏰ Время блокировки: {current_time.strftime('%H:%M:%S %d.%m.%Y')}

💡 Для разблокировки используйте: /unblock_user {user_id}"""
                
                try:
                    requests.post(
                        f"https://api.telegram.org/bot{self.bot_token}/sendMessage",
                        data={
                            'chat_id': self.admin_chat_id,
                            'text': admin_message
                        }
                    )
                except Exception as e:
                    logger.error(f"Ошибка уведомления админа о блокировке: {e}")
                
                logger.warning(f"🚨 ПОЛЬЗОВАТЕЛЬ ЗАБЛОКИРОВАН: {user_data['username']} (ID: {user_id}) - Рандомные сообщения")
                self._add_admin_event('blocked', user_id, f"⛔ @{user_data['username']} ЗАБЛОКИРОВАН за {len(recent_messages)} рандомных сообщений")
                
                # Сообщение о блокировке
                blocked_text = f"""
{t('blocked_title', user_lang)}

{t('blocked_reason', user_lang)}

{t('blocked_permanent', user_lang)}

{t('blocked_contact', user_lang)}
{t('blocked_user_id', user_lang).format(user_id)}
                """.strip()
                
                await update.message.reply_text(
                    blocked_text,
                    parse_mode='Markdown'
                )
                return
            
            # Показываем предупреждение
            if warning_count == 1:
                warning_level = t('warning_first_title', user_lang)
                warning_text = t('warning_block_threat', user_lang)
            else:  # warning_count == 2
                warning_level = t('warning_last_title', user_lang)
                warning_text = t('warning_block_threat', user_lang)
            
            warning_message = f"""
{warning_level}

{t('warning_checks_count', user_lang).format(len(recent_messages))}

{warning_text}

{t('warning_status_wont_change', user_lang)}

{t('warning_steps_required', user_lang).format(self.min_deposit)}

{t('warning_cooldown', user_lang).format(self.random_message_cooldown // 60)}

{t('warning_advice', user_lang)}
            """.strip()
            
            await update.message.reply_text(
                warning_message,
                parse_mode='Markdown'
            )
            return
        
        # Обычное сообщение об ошибке
        await update.message.reply_text(
            t('error_unknown_message', user_lang),
            parse_mode='Markdown'
        )
    
    async def handle_pocket_option_id(self, user_id: int, po_id: str, update: Update):
        """Обработка ID аккаунта PocketOption"""
        
        logger.info(f"🆔 Получен ID аккаунта от пользователя {user_id}: {po_id}")
        user_lang = get_user_language(user_id, self.users_db)
        
        # Проверяем оба варианта ключей (int и str)
        user_key = user_id if user_id in self.users_db else str(user_id) if str(user_id) in self.users_db else None
        if user_key is None:
            logger.warning(f"⚠️ Пользователь {user_id} не найден в базе данных")
            await update.message.reply_text(
                t('error_use_start', user_lang),
                parse_mode='Markdown'
            )
            return
            
        # Форматируем ID (добавляем PO если нет)
        if po_id.upper().startswith('PO'):
            formatted_id = po_id.upper()
        else:
            formatted_id = f"PO{po_id}"
            
        logger.info(f"📝 Форматированный ID: {formatted_id}")
        
        # Проверяем, отправлял ли пользователь ID ранее
        if user_id in self.id_submission_count:
            self.id_submission_count[user_id] += 1
            
            if self.id_submission_count[user_id] == 2:
                # Второе предупреждение
                await update.message.reply_text(
                    "⚠️ ПРЕДУПРЕЖДЕНИЕ!\n\n"
                    "Вы уже отправили ID ранее. При следующей отправке вы будете ЗАБЛОКИРОВАНЫ!",
                    parse_mode='Markdown'
                )
                return
            elif self.id_submission_count[user_id] >= 3:
                # Блокировка
                self.blocked_users.add(user_id)
                await update.message.reply_text(
                    "🚫 ВЫ ЗАБЛОКИРОВАНЫ!\n\n"
                    "Вы отправили ID более 3 раз. Обратитесь в поддержку: @kaktotakxm",
                    parse_mode='Markdown'
                )
                logger.warning(f"🚨 Пользователь {user_id} заблокирован за повторную отправку ID")
                return
        else:
            self.id_submission_count[user_id] = 1
            
        # Сохраняем ID
        self.users_db[user_key]['pocket_option_id'] = formatted_id
        self._save_users_db()
        
        # Сбрасываем историю проверок доступа при отправке ID
        if user_id in self.access_check_history:
            self.access_check_history[user_id] = []
            logger.info(f"🔄 Сброшена история проверок для пользователя {user_id}")
        
        # Сбрасываем предупреждения и историю рандомных сообщений при отправке ID
        if user_id in self.user_warnings:
            self.user_warnings[user_id] = 0
            logger.info(f"🔄 Сброшены предупреждения для пользователя {user_id}")
        if user_id in self.random_message_history:
            self.random_message_history[user_id] = []
            logger.info(f"🔄 Сброшена история рандомных сообщений для пользователя {user_id}")
        
        # Уведомляем администратора об отправке ID
        logger.info(f"📤 Пользователь {user_id} отправил ID: {formatted_id}")
        username = self.users_db[user_key].get('username', 'Unknown')
        self._add_admin_event('id_sent', user_id, f"@{username} отправил PocketOption ID: {formatted_id}")
        await self.notify_admin_id_sent(user_id, formatted_id, update)
        
        # Ответ пользователю на его языке
        response_text = f"""
{t('id_received_title', user_lang).format(formatted_id)}

{t('id_checking', user_lang)}

{t('id_processing_time', user_lang)}

{t('id_what_checked', user_lang)}

{t('id_after_verification', user_lang)}

{t('id_questions', user_lang)}
        """.strip()
        
        await update.message.reply_text(
            response_text,
            parse_mode='Markdown'
        )
        
    async def help_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Команда /help"""
        user_id = update.effective_user.id
        user_lang = get_user_language(user_id, self.users_db)
        
        help_text = f"""
{t('help_title', user_lang)}

{t('help_commands', user_lang)}

{t('help_send_id', user_lang)}

🔗 *{t('btn_registration', user_lang)}:*
{self.referral_link}

{t('help_min_deposit', user_lang).format(self.min_deposit)}

📞 *{t('btn_support', user_lang)}:* @kaktotakxm

{t('help_response_time', user_lang)}
        """.strip()
        
        await update.message.reply_text(help_text, parse_mode='Markdown')
        
    async def status_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Команда /status"""
        user_id = update.effective_user.id
        user_lang = get_user_language(user_id, self.users_db)
        
        if user_id not in self.users_db:
            await update.message.reply_text(
                t('error_not_registered', user_lang),
                parse_mode='Markdown'
            )
            return
            
        user_data = self.users_db[user_id]
        
        registration_date = (user_data.get('registered_at') or '')[:10] or '-'

        status_text = f"""
{t('status_title', user_lang)}

{t('access_user', user_lang).format(user_data['username'])}
{t('access_registration', user_lang).format(registration_date)}
{t('access_account_id', user_lang).format(user_data.get('pocket_option_id', t('access_id_not_sent', user_lang)))}
{t('access_status', user_lang).format(t('access_active', user_lang) if user_data.get('verified') else t('access_not_granted', user_lang))}

        """.strip()
        
        if not user_data.get('verified'):
            status_text += t('status_not_verified', user_lang).format(self.min_deposit)
        
        await update.message.reply_text(status_text, parse_mode='Markdown')
    
    async def notify_admin_new_user(self, user_id: int, username: str, update: Update):
        """Уведомление администратора о новом пользователе"""
        # Получаем имя пользователя из Telegram
        user = update.effective_user
        user_name = user.first_name or "User"
        if user.last_name:
            user_name = f"{user.first_name} {user.last_name}"
        
        # Безопасное получение username
        telegram_username = "без username"
        if user and user.username:
            telegram_username = f"@{user.username}"
        elif user_name and user_name != "User":
            telegram_username = user_name
        
        # Безопасное создание сообщения без Markdown проблем
        admin_message = f"""🆕 НОВЫЙ ПОЛЬЗОВАТЕЛЬ ЗАРЕГИСТРИРОВАЛСЯ!

👤 Пользователь: {user_name}
🆔 ID: {user_id}
📧 Telegram: {telegram_username}
📅 Время регистрации: {datetime.now().strftime('%H:%M:%S %d.%m.%Y')}

📊 Статистика:
• Всего пользователей: {len(self.users_db)}
• Новых сегодня: {len([u for u in self.users_db.values() if u.get('registered_at', '')[:10] == datetime.now().strftime('%Y-%m-%d')])}

💡 Ожидайте отправки ID аккаунта для верификации"""
        
        try:
            # Используем синхронный requests.post в отдельном потоке
            
            def send_notification():
                try:
                    logger.info(f"📤 Отправляем уведомление администратору (ID: {self.admin_chat_id})")
                    logger.info(f"📝 Длина сообщения: {len(admin_message)} символов")
                    
                    response = requests.post(
                        f"https://api.telegram.org/bot{self.bot_token}/sendMessage",
                        data={
                            'chat_id': self.admin_chat_id,
                            'text': admin_message
                        },
                        timeout=10
                    )
                    
                    logger.info(f"📡 Ответ сервера: HTTP {response.status_code}")
                    
                    if response.status_code == 200:
                        logger.info(f"✅ Уведомление о новом пользователе отправлено администратору: {username} (ID: {user_id})")
                    else:
                        logger.error(f"❌ Ошибка отправки уведомления: HTTP {response.status_code}")
                        logger.error(f"❌ Ответ сервера: {response.text}")
                except Exception as e:
                    logger.error(f"❌ Ошибка отправки уведомления администратору: {e}")
            
            # Запускаем в отдельном потоке
            thread = threading.Thread(target=send_notification)
            thread.daemon = True
            thread.start()
            
        except Exception as e:
            logger.error(f"❌ Критическая ошибка при отправке уведомления: {e}")
    
    async def notify_admin_id_sent(self, user_id: int, formatted_id: str, update: Update):
        """Уведомление администратора об отправке ID аккаунта"""
        # Безопасное получение username
        telegram_username = "без username"
        if update.effective_user and update.effective_user.username:
            telegram_username = f"@{update.effective_user.username}"
        
        # Проверяем реферальную информацию
        user_data = self.users_db.get(str(user_id), {})
        ref_data = user_data.get('referral', {})
        invited_by = ref_data.get('invited_by', None)
        referrer_info = ""
        if invited_by:
            referrer_data = self.users_db.get(invited_by, {})
            referrer_info = f"\n👥 Приглашён: @{referrer_data.get('username', invited_by)}"
        
        # Безопасное создание сообщения без Markdown проблем
        admin_message = f"""🔔 НОВЫЙ ЗАПРОС ДОСТУПА

👤 Пользователь: {self.users_db.get(str(user_id), {}).get('username', 'Unknown')}
🆔 ID: {user_id}
📧 Telegram: {telegram_username}
🆔 PocketOption ID: {formatted_id}{referrer_info}

⏰ Время: {datetime.now().strftime('%H:%M:%S %d.%m.%Y')}

🔗 Реферальная ссылка: {self.referral_link}

✅ Проверьте:
1. Регистрация по реферальной ссылке
2. Пополнение минимум ${self.min_deposit}
3. Предоставьте доступ если все ОК"""
        
        try:
            # Отправляем с кнопками для быстрого подтверждения
            keyboard = [
                [
                    InlineKeyboardButton("✅ Подтвердить депозит", callback_data=f"confirm_deposit_{user_id}"),
                    InlineKeyboardButton("❌ Отклонить", callback_data=f"reject_user_{user_id}")
                ]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await self.application.bot.send_message(
                chat_id=int(self.admin_chat_id),
                text=admin_message,
                reply_markup=reply_markup
            )
            logger.info(f"✅ Уведомление об отправке ID отправлено администратору")
            
        except Exception as e:
            logger.error(f"❌ Критическая ошибка при отправке уведомления об ID: {e}")
    
    async def confirm_deposit_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Подтверждение депозита пользователя (для админа)"""
        query = update.callback_query
        
        admin_id = str(query.from_user.id)
        if admin_id != self.admin_chat_id:
            await query.answer("Нет прав", show_alert=True)
            return
        
        target_user_id = query.data.replace("confirm_deposit_", "")
        
        if target_user_id not in self.users_db:
            await query.answer("Пользователь не найден", show_alert=True)
            return
        
        # Подтверждаем депозит
        self.users_db[target_user_id]['deposited'] = True
        self.users_db[target_user_id]['verified'] = True
        self._save_users_db()
        
        # Проверяем и активируем реферала
        logger.info(f"🔍 Проверка активации реферала для {target_user_id}")
        activated, referrer_id = self.referral_manager.check_and_activate_referral(target_user_id)
        logger.info(f"🔍 Результат: activated={activated}, referrer_id={referrer_id}")
        
        referral_msg = ""
        if activated and referrer_id:
            # Уведомляем реферера
            username = self.users_db[target_user_id].get('username', 'Пользователь')
            logger.info(f"📤 Отправляем уведомление об активации рефереру {referrer_id}")
            await self._notify_referrer_activation(referrer_id, username)
            referral_msg = f"\n👥 Реферал активирован для @{self.users_db.get(referrer_id, {}).get('username', referrer_id)}"
        
        await query.answer(f"✅ Депозит подтверждён!{referral_msg}", show_alert=True)
        
        # Уведомляем пользователя о получении доступа
        try:
            user_lang = get_user_language(int(target_user_id), self.users_db)
            await context.bot.send_message(
                chat_id=int(target_user_id),
                text=t('access_granted_message', user_lang),
                parse_mode='Markdown'
            )
            
            # Второе сообщение с кнопкой на бот сигналов
            signal_bot_message = t('signal_bot_access_message', user_lang)
            signal_keyboard = [
                [InlineKeyboardButton("🚀 Devil SIGNAL — Бот сигналов", url="https://t.me/FOREX_SIGNAL_PRO1_bot")]
            ]
            signal_reply_markup = InlineKeyboardMarkup(signal_keyboard)
            
            await context.bot.send_message(
                chat_id=int(target_user_id),
                text=signal_bot_message,
                reply_markup=signal_reply_markup,
                parse_mode='Markdown'
            )
        except Exception as e:
            logger.error(f"Ошибка уведомления пользователя о доступе: {e}")
        
        # Обновляем сообщение
        await query.edit_message_text(
            query.message.text + f"\n\n✅ ДЕПОЗИТ ПОДТВЕРЖДЁН{referral_msg}"
        )
    
    async def admin_stats_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Команда /admin_stats - только для администратора"""
        user_id = update.effective_user.id
        
        # Проверяем, что это администратор
        if str(user_id) != self.admin_chat_id:
            await update.message.reply_text(
                "❌ У вас нет прав для выполнения этой команды",
                parse_mode='Markdown'
            )
            return
        
        # Статистика проверок доступа
        total_users = len(self.users_db)
        users_with_checks = len(self.access_check_history)
        total_checks = sum(len(checks) for checks in self.access_check_history.values())
        
        # Находим пользователей с наибольшим количеством проверок
        top_checkers = []
        for uid, checks in self.access_check_history.items():
            if len(checks) > 1:  # Только тех, кто проверял более 1 раза
                username = self.users_db.get(uid, {}).get('username', 'Unknown')
                top_checkers.append((username, len(checks)))
        
        top_checkers.sort(key=lambda x: x[1], reverse=True)
        
        # Статистика заблокированных пользователей
        blocked_count = len(self.blocked_users)
        warned_users = len([uid for uid, count in self.user_warnings.items() if count > 0])
        
        # Статистика новых пользователей
        today = datetime.now().strftime('%Y-%m-%d')
        new_today = len([u for u in self.users_db.values() if u.get('registered_at', '')[:10] == today])
        week_ago = (datetime.now().replace(hour=0, minute=0, second=0, microsecond=0) - timedelta(days=7)).strftime('%Y-%m-%d')
        new_week = len([u for u in self.users_db.values() if u.get('registered_at', '')[:10] >= week_ago])
        
        stats_text = f"""
📊 *СТАТИСТИКА ПРОВЕРОК ДОСТУПА*

👥 *Общая статистика:*
• Всего пользователей: {total_users}
• Новых сегодня: {new_today}
• Новых за неделю: {new_week}
• Пользователей с проверками: {users_with_checks}
• Всего проверок: {total_checks}
• Пользователей с предупреждениями: {warned_users}
• Заблокированных пользователей: {blocked_count}

🔄 *Топ повторных проверок:*
        """.strip()
        
        if top_checkers:
            for i, (username, count) in enumerate(top_checkers[:5], 1):
                stats_text += f"\n{i}. @{username}: {count} проверок"
        else:
            stats_text += "\n• Нет повторных проверок"
        
        stats_text += f"""

⚙️ *Настройки:*
• Максимум проверок: {self.max_repeated_checks}
• Кулдаун: {self.check_cooldown // 60} мин.
• Максимум предупреждений: {self.max_warnings} (1-е, 2-е = бан)

💡 *Управление:*
• /reset_checks - сбросить все проверки
• /blocked_users - список заблокированных
• /unblock_user <ID> - разблокировать пользователя
        """.strip()
        
        await update.message.reply_text(stats_text, parse_mode='Markdown')
    
    async def reset_checks_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Команда /reset_checks - сброс всех проверок (только для админа)"""
        user_id = update.effective_user.id
        
        # Проверяем, что это администратор
        if str(user_id) != self.admin_chat_id:
            await update.message.reply_text(
                "❌ У вас нет прав для выполнения этой команды",
                parse_mode='Markdown'
            )
            return
        
        # Сбрасываем все проверки
        self.access_check_history = {}
        self.random_message_history = {}
        self.user_warnings = {}
        
        await update.message.reply_text(
            "✅ История всех проверок доступа и предупреждений сброшена",
            parse_mode='Markdown'
        )
    
    async def unblock_user_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Команда /unblock_user <user_id> - разблокировка пользователя (только для админа)"""
        user_id = update.effective_user.id
        
        # Проверяем, что это администратор
        if str(user_id) != self.admin_chat_id:
            await update.message.reply_text(
                "❌ У вас нет прав для выполнения этой команды",
                parse_mode='Markdown'
            )
            return
        
        # Получаем ID пользователя для разблокировки
        if not context.args:
            await update.message.reply_text(
                "❌ Укажите ID пользователя для разблокировки\n"
                "Пример: /unblock_user 123456789",
                parse_mode='Markdown'
            )
            return
        
        try:
            target_user_id = int(context.args[0])
        except ValueError:
            await update.message.reply_text(
                "❌ Неверный формат ID пользователя",
                parse_mode='Markdown'
            )
            return
        
        # Разблокируем пользователя
        if target_user_id in self.blocked_users:
            self.blocked_users.remove(target_user_id)
            
            # Сбрасываем предупреждения
            if target_user_id in self.user_warnings:
                self.user_warnings[target_user_id] = 0
            
            # Сбрасываем историю проверок
            if target_user_id in self.access_check_history:
                self.access_check_history[target_user_id] = []
            
            # Сбрасываем историю рандомных сообщений
            if target_user_id in self.random_message_history:
                self.random_message_history[target_user_id] = []
            
            await update.message.reply_text(
                f"✅ Пользователь {target_user_id} разблокирован\n"
                f"• Предупреждения сброшены\n"
                f"• История проверок очищена\n"
                f"• История сообщений очищена\n\n"
                f"💡 Пользователь может продолжить использование бота",
                parse_mode='Markdown'
            )
            
            # Уведомление пользователю отключено
            logger.info(f"✅ Пользователь {target_user_id} разблокирован администратором")
        else:
            await update.message.reply_text(
                f"ℹ️ Пользователь {target_user_id} не заблокирован",
                parse_mode='Markdown'
            )
    
    async def blocked_users_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Команда /blocked_users - список заблокированных пользователей (только для админа)"""
        user_id = update.effective_user.id
        
        # Проверяем, что это администратор
        if str(user_id) != self.admin_chat_id:
            await update.message.reply_text(
                "❌ У вас нет прав для выполнения этой команды",
                parse_mode='Markdown'
            )
            return
        
        if not self.blocked_users:
            await update.message.reply_text(
                "✅ Заблокированных пользователей нет",
                parse_mode='Markdown'
            )
            return
        
        blocked_list = "🚫 *ЗАБЛОКИРОВАННЫЕ ПОЛЬЗОВАТЕЛИ:*\n\n"
        
        for blocked_id in self.blocked_users:
            username = self.users_db.get(blocked_id, {}).get('username', 'Unknown')
            warnings = self.user_warnings.get(blocked_id, 0)
            blocked_list += f"• ID: {blocked_id}\n"
            blocked_list += f"  Username: @{username}\n"
            blocked_list += f"  Предупреждений: {warnings}\n\n"
        
        blocked_list += f"💡 *Для разблокировки используйте:* /unblock_user <ID>"
        
        await update.message.reply_text(blocked_list, parse_mode='Markdown')
    
    async def admin_panel_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Команда /admin_panel - панель администратора"""
        user_id = update.effective_user.id
        
        # Проверяем, что это администратор
        if str(user_id) != self.admin_chat_id:
            await update.message.reply_text(
                "❌ У вас нет прав для выполнения этой команды",
                parse_mode='Markdown'
            )
            return
        
        # Статистика пользователей
        total_users = len(self.users_db)
        verified_users = len([u for u in self.users_db.values() if u.get('verified')])
        with_id = len([u for u in self.users_db.values() if u.get('pocket_option_id')])
        with_deposit = len([u for u in self.users_db.values() if u.get('deposited')])
        motivation_status = (
            f"🔕 Ручной режим (авто отключено)" if not self.motivation_auto_enabled
            else f"🔔 Авто каждые {self.motivation_interval_hours} ч."
        )
        
        motivation_status = (
            "🔕 Ручной режим (авто отключено)" if not self.motivation_auto_enabled
            else f"🔔 Авто каждые {self.motivation_interval_hours} ч."
        )
        
        # Статистика по датам
        today = datetime.now().strftime('%Y-%m-%d')
        new_today = len([u for u in self.users_db.values() if u.get('registered_at', '')[:10] == today])
        week_ago = (datetime.now() - timedelta(days=7)).strftime('%Y-%m-%d')
        new_week = len([u for u in self.users_db.values() if u.get('registered_at', '')[:10] >= week_ago])
        
        # Статистика по языкам
        languages = {}
        for user_data in self.users_db.values():
            lang = user_data.get('language', 'Не выбран')
            languages[lang] = languages.get(lang, 0) + 1
        
        lang_stats = '\n'.join([f"  • {lang}: {count}" for lang, count in sorted(languages.items(), key=lambda x: x[1], reverse=True)])
        
        panel_text = f"""
👑 *ПАНЕЛЬ АДМИНИСТРАТОРА*

📊 *СТАТИСТИКА ПОЛЬЗОВАТЕЛЕЙ:*

👥 *Общая информация:*
• Всего пользователей: {total_users}
• Верифицированных: {verified_users}
• Отправили ID: {with_id}
• С депозитом: {with_deposit}
• Мотивационные рассылки: {motivation_status}

📅 *Новые пользователи:*
• Сегодня: {new_today}
• За неделю: {new_week}

🌐 *Распределение по языкам:*
{lang_stats}

⚠️ *Система безопасности:*
• С предупреждениями: {len([uid for uid, count in self.user_warnings.items() if count > 0])}
• Заблокированных: {len(self.blocked_users)}

💾 *Файл базы данных:* `{self.users_db_file}`
        """.strip()
        
        keyboard = [
            [InlineKeyboardButton("📥 Скачать таблицу пользователей", callback_data="admin_export_users")],
            [InlineKeyboardButton("📋 Последние события", callback_data="admin_events")],
            [InlineKeyboardButton("🔄 Обновить статистику", callback_data="admin_refresh")],
            [InlineKeyboardButton("📊 Детальная статистика", callback_data="admin_stats")],
            [InlineKeyboardButton("📧 Новая рассылка", callback_data="admin_new_broadcast")],
            [InlineKeyboardButton("📧 Запустить рассылку", callback_data="admin_send_motivation")],
            [InlineKeyboardButton("🗑️ Очистить статистику", callback_data="admin_clear_stats")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(
            panel_text,
            reply_markup=reply_markup,
            parse_mode='Markdown'
        )
    
    async def admin_export_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработчик экспорта пользователей"""
        query = update.callback_query
        await query.answer()
        
        user_id = query.from_user.id
        
        # Проверяем, что это администратор
        if str(user_id) != self.admin_chat_id:
            await query.edit_message_text(
                "❌ У вас нет прав для выполнения этой команды",
                parse_mode='Markdown'
            )
            return
        
        await query.edit_message_text(
            "⏳ Генерирую таблицу пользователей...",
            parse_mode='Markdown'
        )
        
        # Экспортируем пользователей
        csv_file = self._export_users_csv()
        
        if csv_file:
            try:
                # Отправляем файл
                with open(csv_file, 'rb') as f:
                    await context.bot.send_document(
                        chat_id=self.admin_chat_id,
                        document=f,
                        filename=csv_file,
                        caption=f"📊 *Таблица пользователей*\n\nВсего записей: {len(self.users_db)}\nДата экспорта: {datetime.now().strftime('%d.%m.%Y %H:%M:%S')}",
                        parse_mode='Markdown'
                    )
                
                # Удаляем временный файл
                import os
                os.remove(csv_file)
                
                await query.edit_message_text(
                    "✅ Таблица пользователей отправлена!",
                    parse_mode='Markdown'
                )
            except Exception as e:
                logger.error(f"❌ Ошибка отправки файла: {e}")
                await query.edit_message_text(
                    f"❌ Ошибка отправки файла: {e}",
                    parse_mode='Markdown'
                )
        else:
            await query.edit_message_text(
                "❌ Ошибка создания файла экспорта",
                parse_mode='Markdown'
            )
    
    async def admin_refresh_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработчик обновления статистики"""
        query = update.callback_query
        await query.answer("🔄 Обновляю статистику...")
        
        user_id = query.from_user.id
        
        # Проверяем, что это администратор
        if str(user_id) != self.admin_chat_id:
            await query.edit_message_text(
                "❌ У вас нет прав для выполнения этой команды",
                parse_mode='Markdown'
            )
            return
        
        # Статистика пользователей
        total_users = len(self.users_db)
        verified_users = len([u for u in self.users_db.values() if u.get('verified')])
        with_id = len([u for u in self.users_db.values() if u.get('pocket_option_id')])
        with_deposit = len([u for u in self.users_db.values() if u.get('deposited')])
        
        # Статистика по датам
        today = datetime.now().strftime('%Y-%m-%d')
        new_today = len([u for u in self.users_db.values() if u.get('registered_at', '')[:10] == today])
        week_ago = (datetime.now() - timedelta(days=7)).strftime('%Y-%m-%d')
        new_week = len([u for u in self.users_db.values() if u.get('registered_at', '')[:10] >= week_ago])
        
        # Статистика по языкам
        languages = {}
        for user_data in self.users_db.values():
            lang = user_data.get('language', 'Не выбран')
            languages[lang] = languages.get(lang, 0) + 1
        
        lang_stats = '\n'.join([f"  • {lang}: {count}" for lang, count in sorted(languages.items(), key=lambda x: x[1], reverse=True)])
        
        # Добавляем время обновления для различия контента (с микросекундами)
        update_time = datetime.now().strftime('%H:%M:%S.%f')[:-3]  # миллисекунды
        
        panel_text = f"""👑 ПАНЕЛЬ АДМИНИСТРАТОРА

📊 СТАТИСТИКА ПОЛЬЗОВАТЕЛЕЙ:

👥 Общая информация:
• Всего пользователей: {total_users}
• Верифицированных: {verified_users}
• Отправили ID: {with_id}
• С депозитом: {with_deposit}
• Мотивационные рассылки: {motivation_status}

📅 Новые пользователи:
• Сегодня: {new_today}
• За неделю: {new_week}

🌐 Распределение по языкам:
{lang_stats}

⚠️ Система безопасности:
• С предупреждениями: {len([uid for uid, count in self.user_warnings.items() if count > 0])}
• Заблокированных: {len(self.blocked_users)}

💾 Файл базы данных: {self.users_db_file}

🕐 Обновлено: {update_time}"""
        
        keyboard = [
            [InlineKeyboardButton("📥 Скачать таблицу пользователей", callback_data="admin_export_users")],
            [InlineKeyboardButton("📋 Последние события", callback_data="admin_events")],
            [InlineKeyboardButton("🔄 Обновить статистику", callback_data="admin_refresh")],
            [InlineKeyboardButton("📊 Детальная статистика", callback_data="admin_stats")],
            [InlineKeyboardButton("📧 Новая рассылка", callback_data="admin_new_broadcast")],
            [InlineKeyboardButton("📧 Запустить рассылку", callback_data="admin_send_motivation")],
            [InlineKeyboardButton("🗑️ Очистить статистику", callback_data="admin_clear_stats")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(
            panel_text,
            reply_markup=reply_markup
        )
    
    async def admin_stats_detailed_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработчик детальной статистики"""
        query = update.callback_query
        await query.answer()
        
        user_id = query.from_user.id
        
        # Проверяем, что это администратор
        if str(user_id) != self.admin_chat_id:
            await query.edit_message_text(
                "❌ У вас нет прав для выполнения этой команды",
                parse_mode='Markdown'
            )
            return
        
        # Статистика проверок доступа
        total_users = len(self.users_db)
        users_with_checks = len(self.access_check_history)
        total_checks = sum(len(checks) for checks in self.access_check_history.values())
        
        # Находим пользователей с наибольшим количеством проверок
        top_checkers = []
        for uid, checks in self.access_check_history.items():
            if len(checks) > 1:  # Только тех, кто проверял более 1 раза
                username = self.users_db.get(uid, {}).get('username', 'Unknown')
                top_checkers.append((username, len(checks)))
        
        top_checkers.sort(key=lambda x: x[1], reverse=True)
        
        # Статистика заблокированных пользователей
        blocked_count = len(self.blocked_users)
        warned_users = len([uid for uid, count in self.user_warnings.items() if count > 0])
        
        # Статистика новых пользователей
        today = datetime.now().strftime('%Y-%m-%d')
        new_today = len([u for u in self.users_db.values() if u.get('registered_at', '')[:10] == today])
        week_ago = (datetime.now().replace(hour=0, minute=0, second=0, microsecond=0) - timedelta(days=7)).strftime('%Y-%m-%d')
        new_week = len([u for u in self.users_db.values() if u.get('registered_at', '')[:10] >= week_ago])
        
        stats_text = f"""📊 СТАТИСТИКА ПРОВЕРОК ДОСТУПА

👥 Общая статистика:
• Всего пользователей: {total_users}
• Новых сегодня: {new_today}
• Новых за неделю: {new_week}
• Пользователей с проверками: {users_with_checks}
• Всего проверок: {total_checks}
• Пользователей с предупреждениями: {warned_users}
• Заблокированных пользователей: {blocked_count}

🔄 Топ повторных проверок:"""
        
        if top_checkers:
            for i, (username, count) in enumerate(top_checkers[:5], 1):
                # Безопасное имя пользователя
                safe_username = username.replace('*', '').replace('_', '').replace('`', '') if username else 'Unknown'
                stats_text += f"\n{i}. @{safe_username}: {count} проверок"
        else:
            stats_text += "\n• Нет повторных проверок"
        
        stats_text += f"""

⚙️ Настройки:
• Максимум проверок: {self.max_repeated_checks}
• Кулдаун: {self.check_cooldown // 60} мин.
• Максимум предупреждений: {self.max_warnings} (1-е, 2-е = бан)

💡 Управление:
• /reset_checks - сбросить все проверки
• /blocked_users - список заблокированных
• /unblock_user <ID> - разблокировать пользователя"""
        
        keyboard = [
            [InlineKeyboardButton("◀️ Назад к панели", callback_data="back_to_admin_panel")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(
            stats_text,
            reply_markup=reply_markup
        )
    
    async def admin_events_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработчик просмотра последних событий"""
        query = update.callback_query
        await query.answer("🔄 Обновляю события...")
        
        user_id = query.from_user.id
        
        # Проверяем, что это администратор
        if str(user_id) != self.admin_chat_id:
            await query.edit_message_text(
                "❌ У вас нет прав для выполнения этой команды",
                parse_mode='Markdown'
            )
            return
        
        # Добавляем время обновления для различия контента
        update_time = datetime.now().strftime('%H:%M:%S.%f')[:-3]  # миллисекунды
        
        if not self.admin_events:
            events_text = f"""📋 ПОСЛЕДНИЕ СОБЫТИЯ

ℹ️ Пока нет событий для отображения.

События появятся когда:
• Зарегистрируются новые пользователи
• Пользователи отправят PocketOption ID
• Произойдут блокировки

🕐 Обновлено: {update_time}"""
        else:
            events_text = f"📋 ПОСЛЕДНИЕ СОБЫТИЯ\n\n"
            
            # Показываем последние 20 событий
            for i, event in enumerate(self.admin_events[:20], 1):
                timestamp = datetime.fromisoformat(event['timestamp'])
                time_str = timestamp.strftime('%H:%M:%S %d.%m')
                
                # Иконки для разных типов событий
                icons = {
                    'new_user': '🆕',
                    'id_sent': '🆔',
                    'blocked': '⛔',
                    'unblocked': '✅',
                    'verified': '✅'
                }
                icon = icons.get(event['event_type'], '📌')
                
                events_text += f"{i}. {icon} {time_str} - {event['description']}\n"
            
            if len(self.admin_events) > 20:
                events_text += f"\n...и еще {len(self.admin_events) - 20} событий"
            
            events_text += f"\n\n🕐 Обновлено: {update_time}"
        
        keyboard = [
            [InlineKeyboardButton("🔄 Обновить", callback_data="admin_events")],
            [InlineKeyboardButton("◀️ Назад к панели", callback_data="back_to_admin_panel")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(
            events_text,
            reply_markup=reply_markup
        )
    
    async def back_to_admin_panel_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработчик кнопки 'Назад к панели'"""
        query = update.callback_query
        await query.answer()
        
        user_id = query.from_user.id
        
        # Проверяем, что это администратор
        if str(user_id) != self.admin_chat_id:
            await query.edit_message_text(
                "❌ У вас нет прав для выполнения этой команды",
                parse_mode='Markdown'
            )
            return
        
        # Статистика пользователей
        total_users = len(self.users_db)
        verified_users = len([u for u in self.users_db.values() if u.get('verified')])
        with_id = len([u for u in self.users_db.values() if u.get('pocket_option_id')])
        with_deposit = len([u for u in self.users_db.values() if u.get('deposited')])
        
        # Статистика по датам
        today = datetime.now().strftime('%Y-%m-%d')
        new_today = len([u for u in self.users_db.values() if u.get('registered_at', '')[:10] == today])
        week_ago = (datetime.now() - timedelta(days=7)).strftime('%Y-%m-%d')
        new_week = len([u for u in self.users_db.values() if u.get('registered_at', '')[:10] >= week_ago])
        
        # Статистика по языкам
        languages = {}
        for user_data in self.users_db.values():
            lang = user_data.get('language', 'Не выбран')
            languages[lang] = languages.get(lang, 0) + 1
        
        lang_stats = '\n'.join([f"  • {lang}: {count}" for lang, count in sorted(languages.items(), key=lambda x: x[1], reverse=True)])
        
        panel_text = f"""
👑 *ПАНЕЛЬ АДМИНИСТРАТОРА*

📊 *СТАТИСТИКА ПОЛЬЗОВАТЕЛЕЙ:*

👥 *Общая информация:*
• Всего пользователей: {total_users}
• Верифицированных: {verified_users}
• Отправили ID: {with_id}
• С депозитом: {with_deposit}

📅 *Новые пользователи:*
• Сегодня: {new_today}
• За неделю: {new_week}

🌐 *Распределение по языкам:*
{lang_stats}

⚠️ *Система безопасности:*
• С предупреждениями: {len([uid for uid, count in self.user_warnings.items() if count > 0])}
• Заблокированных: {len(self.blocked_users)}

💾 *Файл базы данных:* `{self.users_db_file}`
        """.strip()
        
        keyboard = [
            [InlineKeyboardButton("📥 Скачать таблицу пользователей", callback_data="admin_export_users")],
            [InlineKeyboardButton("📋 Последние события", callback_data="admin_events")],
            [InlineKeyboardButton("🔄 Обновить статистику", callback_data="admin_refresh")],
            [InlineKeyboardButton("📊 Детальная статистика", callback_data="admin_stats")],
            [InlineKeyboardButton("📧 Новая рассылка", callback_data="admin_new_broadcast")],
            [InlineKeyboardButton("📧 Запустить рассылку", callback_data="admin_send_motivation")],
            [InlineKeyboardButton("🗑️ Очистить статистику", callback_data="admin_clear_stats")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(
            panel_text,
            reply_markup=reply_markup,
            parse_mode='Markdown'
        )
    
    async def admin_send_motivation_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработчик ручного запуска мотивационной рассылки"""
        query = update.callback_query
        await query.answer("📧 Запускаю рассылку...")
        
        user_id = query.from_user.id
        
        # Проверяем, что это администратор
        if str(user_id) != self.admin_chat_id:
            await query.edit_message_text(
                "❌ У вас нет прав для выполнения этой команды",
                parse_mode='Markdown'
            )
            return
        
        # Запускаем рассылку в отдельном потоке
        await query.edit_message_text(
            "🔄 Мотивационная рассылка запущена!\n\nОтчет будет отправлен после завершения.",
            parse_mode='Markdown'
        )
        
        # Запускаем задачу в фоне
        threading.Thread(target=self._motivation_job, daemon=True).start()
    
    async def admin_clear_stats_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработчик очистки статистики"""
        query = update.callback_query
        await query.answer()
        
        user_id = query.from_user.id
        
        # Проверяем, что это администратор
        if str(user_id) != self.admin_chat_id:
            await query.edit_message_text(
                "❌ У вас нет прав для выполнения этой команды",
                parse_mode='Markdown'
            )
            return
        
        # Показываем предупреждение с подтверждением
        confirm_text = """⚠️ ВНИМАНИЕ! ОЧИСТКА СТАТИСТИКИ
    
    Выберите тип очистки:
    
    🔄 СБРОС СТАТУСОВ:
    • Сбросить верификацию и депозиты
    • Очистить историю проверок
    • Очистить предупреждения и блокировки
    
    🗑️ ПОЛНАЯ ОЧИСТКА:
    • Удалить ВСЕХ пользователей
    • Очистить всю статистику
    • Начать с чистого листа"""
        
        keyboard = [
            [InlineKeyboardButton("🔄 Сбросить статусы", callback_data="admin_clear_confirm")],
            [InlineKeyboardButton("🗑️ Удалить всех пользователей", callback_data="admin_clear_full")],
            [InlineKeyboardButton("❌ Отмена", callback_data="back_to_admin_panel")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(
            confirm_text,
            reply_markup=reply_markup
        )
    
    async def admin_clear_confirm_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработчик подтверждения очистки статистики"""
        query = update.callback_query
        await query.answer("🗑️ Очищаю статистику...")
        
        user_id = query.from_user.id
        
        # Проверяем, что это администратор
        if str(user_id) != self.admin_chat_id:
            await query.edit_message_text(
                "❌ У вас нет прав для выполнения этой команды"
            )
            return
        
        # Очищаем статистику
        cleared_items = []
        
        # Очищаем историю проверок доступа
        checks_count = len(self.access_check_history)
        self.access_check_history = {}
        if checks_count > 0:
            cleared_items.append(f"• История проверок: {checks_count} пользователей")
        
        # Очищаем предупреждения
        warnings_count = len(self.user_warnings)
        self.user_warnings = {}
        if warnings_count > 0:
            cleared_items.append(f"• Предупреждения: {warnings_count} пользователей")
        
        # Очищаем список заблокированных
        blocked_count = len(self.blocked_users)
        self.blocked_users = set()
        if blocked_count > 0:
            cleared_items.append(f"• Заблокированные: {blocked_count} пользователей")
        
        # Очищаем события
        events_count = len(self.admin_events)
        self.admin_events = []
        if events_count > 0:
            cleared_items.append(f"• События администратора: {events_count} событий")
        
        # Очищаем статистику в базе пользователей (сбрасываем флаги)
        users_reset = 0
        for user_id_key, user_data in self.users_db.items():
            if user_data.get('verified') or user_data.get('deposited'):
                user_data['verified'] = False
                user_data['deposited'] = False
                user_data['pocket_option_id'] = None
                users_reset += 1
        
        if users_reset > 0:
            cleared_items.append(f"• Сброшены статусы: {users_reset} пользователей")
            # Сохраняем изменения в файл
            self._save_users_db()
        
        # Формируем сообщение о результате
        if cleared_items:
            result_text = f"""✅ СТАТИСТИКА ОЧИЩЕНА

Очищено:
{chr(10).join(cleared_items)}

⏰ Время очистки: {datetime.now().strftime('%H:%M:%S %d.%m.%Y')}

💾 База пользователей обновлена
Всего пользователей: {len(self.users_db)}
Статусы сброшены: {users_reset}"""
        else:
            result_text = """ℹ️ СТАТИСТИКА УЖЕ ПУСТА

Нет данных для очистки."""
        
        logger.info(f"🗑️ Администратор очистил статистику: {len(cleared_items)} категорий, сброшено {users_reset} пользователей")
        
        keyboard = [
            [InlineKeyboardButton("◀️ Назад к панели", callback_data="back_to_admin_panel")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(
            result_text,
            reply_markup=reply_markup
        )

    async def admin_clear_full_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработчик полной очистки всех пользователей"""
        query = update.callback_query
        await query.answer("🗑️ Выполняю полную очистку...")
        
        user_id = query.from_user.id
        
        # Проверяем, что это администратор
        if str(user_id) != self.admin_chat_id:
            await query.edit_message_text(
                "❌ У вас нет прав для выполнения этой команды"
            )
            return
        
        # Очищаем ВСЕ данные
        users_count = len(self.users_db)
        checks_count = len(self.access_check_history)
        warnings_count = len(self.user_warnings)
        blocked_count = len(self.blocked_users)
        events_count = len(self.admin_events)
        
        # Полная очистка
        self.users_db = {}
        self.access_check_history = {}
        self.user_warnings = {}
        self.blocked_users = set()
        self.admin_events = []
        
        # Сохраняем пустую базу
        self._save_users_db()
        
        result_text = f"""✅ ПОЛНАЯ ОЧИСТКА ЗАВЕРШЕНА

Удалено:
• Пользователей: {users_count}
• История проверок: {checks_count}
• Предупреждения: {warnings_count}
• Заблокированные: {blocked_count}
• События: {events_count}

⏰ Время очистки: {datetime.now().strftime('%H:%M:%S %d.%m.%Y')}

🎯 База данных полностью очищена
Начинаем с чистого листа!"""
        
        logger.info(f"🗑️ Администратор выполнил полную очистку: {users_count} пользователей удалено")
        
        keyboard = [
            [InlineKeyboardButton("◀️ Назад к панели", callback_data="back_to_admin_panel")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(
            result_text,
            reply_markup=reply_markup
        )

    async def admin_new_broadcast_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработчик кнопки 'Новая рассылка'"""
        query = update.callback_query
        await query.answer()
        
        user_id = query.from_user.id
        
        # Проверяем, что это администратор
        if str(user_id) != self.admin_chat_id:
            await query.edit_message_text(
                "❌ У вас нет прав для выполнения этой команды",
                parse_mode='Markdown'
            )
            return
        
        # Показываем выбор аудитории
        audience_text = """📧 НОВАЯ РАССЫЛКА

Выберите аудиторию для рассылки:

👥 **Все пользователи** - отправить всем
💰 **Без депозита** - только тем, кто не пополнил счет
✅ **Верифицированные** - только с подтвержденным доступом

Выберите тип аудитории:"""
        
        keyboard = [
            [InlineKeyboardButton("👥 Все пользователи", callback_data="broadcast_audience_all")],
            [InlineKeyboardButton("💰 Без депозита", callback_data="broadcast_audience_no_deposit")],
            [InlineKeyboardButton("✅ Верифицированные", callback_data="broadcast_audience_verified")],
            [InlineKeyboardButton("❌ Отмена", callback_data="back_to_admin_panel")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(
            audience_text,
            reply_markup=reply_markup,
            parse_mode='Markdown'
        )
    
    async def admin_select_audience_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработчик выбора аудитории для рассылки"""
        query = update.callback_query
        await query.answer()
        
        user_id = query.from_user.id
        
        # Проверяем, что это администратор
        if str(user_id) != self.admin_chat_id:
            await query.edit_message_text(
                "❌ У вас нет прав для выполнения этой команды",
                parse_mode='Markdown'
            )
            return
        
        # Извлекаем тип аудитории из callback_data
        audience_type = query.data.split("_")[-1]  # all, no_deposit, verified
        
        # Сохраняем выбор аудитории
        if user_id not in self.broadcast_data:
            self.broadcast_data[user_id] = {}
        
        self.broadcast_data[user_id]['audience'] = audience_type
        
        # Показываем выбор типа рассылки
        type_text = f"""📧 НОВАЯ РАССЫЛКА

Аудитория: {self._get_audience_name(audience_type)}

Выберите тип рассылки:

📝 **Одно сообщение** - одинаковое для всех языков
🌐 **Мультиязычная** - разные версии для каждого языка

Выберите тип:"""
        
        keyboard = [
            [InlineKeyboardButton("📝 Одно сообщение", callback_data="broadcast_type_single")],
            [InlineKeyboardButton("🌐 Мультиязычная", callback_data="broadcast_type_multi")],
            [InlineKeyboardButton("◀️ Назад", callback_data="admin_new_broadcast")],
            [InlineKeyboardButton("❌ Отмена", callback_data="back_to_admin_panel")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(
            type_text,
            reply_markup=reply_markup,
            parse_mode='Markdown'
        )
    
    async def admin_broadcast_type_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработчик выбора типа рассылки"""
        query = update.callback_query
        await query.answer()
        
        user_id = query.from_user.id
        
        # Проверяем, что это администратор
        if str(user_id) != self.admin_chat_id:
            await query.edit_message_text(
                "❌ У вас нет прав для выполнения этой команды",
                parse_mode='Markdown'
            )
            return
        
        # Извлекаем тип рассылки из callback_data
        broadcast_type = query.data.split("_")[-1]  # single, multi
        
        # Сохраняем тип рассылки
        self.broadcast_data[user_id]['type'] = broadcast_type
        
        # Показываем инструкции для отправки контента
        if broadcast_type == 'single':
            content_text = f"""📧 НОВАЯ РАССЫЛКА

Аудитория: {self._get_audience_name(self.broadcast_data[user_id]['audience'])}
Тип: Одно сообщение

📤 **Отправьте контент для рассылки:**

Поддерживаемые типы:
• 📝 Текстовое сообщение
• 🖼️ Фото с подписью
• 🎥 Видео с подписью
• 📄 Документ с подписью
• 🎵 Аудио с подписью

Просто отправьте нужный контент в этот чат."""
        else:
            content_text = f"""📧 НОВАЯ РАССЫЛКА

Аудитория: {self._get_audience_name(self.broadcast_data[user_id]['audience'])}
Тип: Мультиязычная

📤 **Отправьте контент для рассылки:**

Поддерживаемые типы:
• 📝 Текстовое сообщение
• 🖼️ Фото с подписью
• 🎥 Видео с подписью
• 📄 Документ с подписью
• 🎵 Аудио с подписью

Просто отправьте нужный контент в этот чат.
Бот автоматически определит язык и создаст версии для всех поддерживаемых языков."""
        
        keyboard = [
            [InlineKeyboardButton("◀️ Назад", callback_data=f"broadcast_audience_{self.broadcast_data[user_id]['audience']}")],
            [InlineKeyboardButton("❌ Отмена", callback_data="back_to_admin_panel")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(
            content_text,
            reply_markup=reply_markup,
            parse_mode='Markdown'
        )
    
    async def handle_broadcast_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработка сообщений от админа для рассылки"""
        user_id = update.effective_user.id
        
        logger.info(f"📨 Получено сообщение для рассылки от админа {user_id}")
        
        if user_id not in self.broadcast_data:
            logger.warning(f"⚠️ Админ {user_id} не в режиме рассылки")
            return
        
        broadcast_data = self.broadcast_data[user_id]
        
        # Проверяем наличие обязательных ключей
        if 'audience' not in broadcast_data:
            await update.message.reply_text(
                "❌ Ошибка: не выбрана аудитория. Начните рассылку заново через /admin.",
                parse_mode='Markdown'
            )
            # Очищаем данные рассылки
            del self.broadcast_data[user_id]
            return
        
        if 'type' not in broadcast_data:
            # Устанавливаем значение по умолчанию
            broadcast_data['type'] = 'single'
            logger.warning(f"⚠️ Тип рассылки не был установлен, используем 'single' по умолчанию")
        
        # Определяем тип контента
        content_type = None
        content = None
        
        if update.message.text:
            content_type = 'text'
            content = update.message.text
            logger.info(f"📝 Определен тип контента: текст")
        elif update.message.photo:
            content_type = 'photo'
            content = {
                'photo': update.message.photo[-1].file_id,
                'caption': update.message.caption or ''
            }
            logger.info(f"📷 Определен тип контента: фото с подписью '{update.message.caption or 'без подписи'}'")
        elif update.message.video:
            content_type = 'video'
            content = {
                'video': update.message.video.file_id,
                'caption': update.message.caption or ''
            }
        elif update.message.document:
            content_type = 'document'
            content = {
                'document': update.message.document.file_id,
                'caption': update.message.caption or ''
            }
        elif update.message.audio:
            content_type = 'audio'
            content = {
                'audio': update.message.audio.file_id,
                'caption': update.message.caption or ''
            }
        else:
            await update.message.reply_text(
                "❌ Неподдерживаемый тип контента. Поддерживаются: текст, фото, видео, документы, аудио.",
                parse_mode='Markdown'
            )
            return
        
        # Сохраняем контент
        broadcast_data['content_type'] = content_type
        broadcast_data['content'] = content
        
        # Показываем превью
        await self._show_broadcast_preview(update, context, broadcast_data)
    
    async def _show_broadcast_preview(self, update: Update, context: ContextTypes.DEFAULT_TYPE, broadcast_data: dict):
        """Показать превью рассылки"""
        user_id = update.effective_user.id
        
        # Проверяем наличие обязательных ключей
        if 'audience' not in broadcast_data:
            await update.message.reply_text(
                "❌ Ошибка: не выбрана аудитория. Начните рассылку заново.",
                parse_mode='Markdown'
            )
            return
        
        if 'type' not in broadcast_data:
            # Устанавливаем значение по умолчанию
            broadcast_data['type'] = 'single'
            logger.warning(f"⚠️ Тип рассылки не был установлен, используем 'single' по умолчанию")
        
        # Получаем список пользователей для рассылки
        target_users = self._get_target_users(broadcast_data['audience'])
        
        preview_text = f"""📧 ПРЕВЬЮ РАССЫЛКИ

Аудитория: {self._get_audience_name(broadcast_data['audience'])}
Тип: {'Одно сообщение' if broadcast_data.get('type', 'single') == 'single' else 'Мультиязычная'}
Получателей: {len(target_users)}

📤 Контент: {self._get_content_preview(broadcast_data['content_type'], broadcast_data['content'])}

⚠️ **ВНИМАНИЕ:** Рассылка будет отправлена всем получателям!
Убедитесь, что контент корректен."""
        
        keyboard = [
            [InlineKeyboardButton("✅ Отправить рассылку", callback_data="broadcast_confirm")],
            [InlineKeyboardButton("◀️ Изменить", callback_data="admin_new_broadcast")],
            [InlineKeyboardButton("❌ Отмена", callback_data="broadcast_cancel")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(
            preview_text,
            reply_markup=reply_markup,
            parse_mode='Markdown'
        )
    
    async def confirm_broadcast_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработчик подтверждения рассылки"""
        query = update.callback_query
        await query.answer("📧 Запускаю рассылку...")
        
        user_id = query.from_user.id
        
        # Проверяем, что это администратор
        if str(user_id) != self.admin_chat_id:
            await query.edit_message_text(
                "❌ У вас нет прав для выполнения этой команды",
                parse_mode='Markdown'
            )
            return
        
        if user_id not in self.broadcast_data:
            await query.edit_message_text(
                "❌ Данные рассылки не найдены",
                parse_mode='Markdown'
            )
            return
        
        broadcast_data = self.broadcast_data[user_id]
        
        # Проверяем длину подписи для медиа-контента
        if broadcast_data['content_type'] in ['photo', 'video', 'document', 'audio']:
            caption = broadcast_data['content'].get('caption', '')
            if len(caption) > 1024:
                await query.edit_message_text(
                    f"⚠️ **ПРЕДУПРЕЖДЕНИЕ О ДЛИНЕ ПОДПИСИ**\n\n"
                    f"Подпись к {broadcast_data['content_type']} слишком длинная:\n"
                    f"📏 Текущая длина: **{len(caption)}** символов\n"
                    f"📏 Максимальная длина: **1024** символа\n\n"
                    f"Подпись будет автоматически обрезана до 1024 символов с добавлением \"...\"\n\n"
                    f"**Продолжить рассылку?**",
                    reply_markup=InlineKeyboardMarkup([
                        [InlineKeyboardButton("✅ Да, продолжить", callback_data="broadcast_confirm_long")],
                        [InlineKeyboardButton("❌ Отмена", callback_data="broadcast_cancel")]
                    ]),
                    parse_mode='Markdown'
                )
                return
        
        # Запускаем рассылку
        await self._execute_broadcast(query, context, broadcast_data)
        
        # Очищаем данные рассылки
        del self.broadcast_data[user_id]
    
    async def confirm_long_caption_broadcast_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработчик подтверждения рассылки с длинной подписью"""
        query = update.callback_query
        await query.answer("📧 Запускаю рассылку с обрезанной подписью...")
        
        user_id = query.from_user.id
        
        # Проверяем, что это администратор
        if str(user_id) != self.admin_chat_id:
            await query.edit_message_text(
                "❌ У вас нет прав для выполнения этой команды",
                parse_mode='Markdown'
            )
            return
        
        if user_id not in self.broadcast_data:
            await query.edit_message_text(
                "❌ Данные рассылки не найдены",
                parse_mode='Markdown'
            )
            return
        
        # Запускаем рассылку
        await self._execute_broadcast(query, context, self.broadcast_data[user_id])
        
        # Очищаем данные рассылки
        del self.broadcast_data[user_id]
    
    async def cancel_broadcast_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработчик отмены рассылки"""
        query = update.callback_query
        await query.answer("❌ Рассылка отменена")
        
        user_id = query.from_user.id
        
        # Проверяем, что это администратор
        if str(user_id) != self.admin_chat_id:
            await query.edit_message_text(
                "❌ У вас нет прав для выполнения этой команды",
                parse_mode='Markdown'
            )
            return
        
        # Очищаем данные рассылки
        if user_id in self.broadcast_data:
            del self.broadcast_data[user_id]
        
        await query.edit_message_text(
            "❌ Рассылка отменена",
            parse_mode='Markdown'
        )
    
    async def _execute_broadcast(self, query, context: ContextTypes.DEFAULT_TYPE, broadcast_data: dict):
        """Выполнение рассылки"""
        user_id = query.from_user.id
        
        # Проверяем наличие обязательных ключей
        if 'audience' not in broadcast_data:
            await query.edit_message_text(
                "❌ Ошибка: не выбрана аудитория. Начните рассылку заново.",
                parse_mode='Markdown'
            )
            return
        
        if 'type' not in broadcast_data:
            broadcast_data['type'] = 'single'
            logger.warning(f"⚠️ Тип рассылки не был установлен, используем 'single' по умолчанию")
        
        # Получаем список пользователей для рассылки
        target_users = self._get_target_users(broadcast_data['audience'])
        
        if not target_users:
            await query.edit_message_text(
                "❌ Нет пользователей для рассылки",
                parse_mode='Markdown'
            )
            return
        
        # ВАЖНО: Убираем дубликаты и конвертируем в правильный тип
        target_users = list(set([int(uid) if isinstance(uid, str) else uid for uid in target_users]))
        
        logger.info(f"📧 Рассылка: получено {len(target_users)} уникальных пользователей")
        
        # Обновляем сообщение
        await query.edit_message_text(
            f"📧 Рассылка запущена...\n\nОтправка {len(target_users)} сообщений...",
            parse_mode='Markdown'
        )
        
        # Статистика отправки
        sent_count = 0
        failed_count = 0
        failed_users = []
        sent_to_users = set()  # Защита от дубликатов
        
        # Отправляем сообщения
        for user_id_target in target_users:
            # КРИТИЧНО: Проверяем что пользователю ещё не отправляли
            if user_id_target in sent_to_users:
                logger.warning(f"⚠️ Пропуск дубликата пользователя {user_id_target}")
                continue
            
            sent_to_users.add(user_id_target)
            try:
                success = await self._send_broadcast_message(
                    context, user_id_target, broadcast_data
                )
                
                if success:
                    sent_count += 1
                else:
                    failed_count += 1
                    # КРИТИЧНО: Сохраняем ID как строку, так как в базе ключи - строки
                    failed_users.append(str(user_id_target))
                
                # Пауза между отправками
                await asyncio.sleep(1)
                
            except Exception as e:
                logger.error(f"Ошибка отправки рассылки пользователю {user_id_target}: {e}")
                failed_count += 1
                # КРИТИЧНО: Сохраняем ID как строку, так как в базе ключи - строки
                failed_users.append(str(user_id_target))
        
        # Отправляем отчет админу
        report_text = f"""📊 ОТЧЕТ О РАССЫЛКЕ

✅ Успешно отправлено: {sent_count}
❌ Ошибок: {failed_count}
👥 Всего получателей: {len(target_users)}

Аудитория: {self._get_audience_name(broadcast_data['audience'])}
Тип: {'Одно сообщение' if broadcast_data['type'] == 'single' else 'Мультиязычная'}

⏰ Время завершения: {datetime.now().strftime('%H:%M:%S %d.%m.%Y')}"""
        
        keyboard = []
        if failed_users:
            report_text += f"\n\n❌ Ошибки у пользователей: {len(failed_users)}"
            # Сохраняем список неактивных пользователей для очистки
            if not hasattr(self, 'failed_users_list'):
                self.failed_users_list = {}
            self.failed_users_list[user_id] = failed_users
            keyboard.append([InlineKeyboardButton(f"🗑️ Очистить неактивных ({len(failed_users)})", callback_data="clean_inactive_users")])
        
        reply_markup = InlineKeyboardMarkup(keyboard) if keyboard else None
        
        await query.edit_message_text(
            report_text,
            reply_markup=reply_markup,
            parse_mode='Markdown'
        )
        
        # Логируем событие
        self._add_admin_event(
            'broadcast_sent', 
            user_id, 
            f"Рассылка: {sent_count}/{len(target_users)} отправлено"
        )
    
    async def clean_inactive_users_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Очистка неактивных пользователей из базы"""
        query = update.callback_query
        await query.answer()
        
        user_id = query.from_user.id
        
        # Проверяем, что это администратор
        if str(user_id) != self.admin_chat_id:
            await query.edit_message_text(
                "❌ У вас нет прав для выполнения этой команды",
                parse_mode='Markdown'
            )
            return
        
        # Проверяем наличие списка неактивных пользователей
        if not hasattr(self, 'failed_users_list') or user_id not in self.failed_users_list:
            await query.edit_message_text(
                "❌ Список неактивных пользователей не найден",
                parse_mode='Markdown'
            )
            return
        
        failed_users = self.failed_users_list[user_id]
        
        if not failed_users:
            await query.edit_message_text(
                "✅ Неактивных пользователей нет",
                parse_mode='Markdown'
            )
            return
        
        # Обновляем сообщение
        await query.edit_message_text(
            f"🗑️ Удаляю {len(failed_users)} неактивных пользователей...",
            parse_mode='Markdown'
        )
        
        removed_count = 0
        
        # Логируем для отладки
        logger.info(f"🔍 Начало удаления: список failed_users содержит {len(failed_users)} пользователей")
        if failed_users:
            logger.info(f"🔍 Типы ID в failed_users: {[type(uid).__name__ for uid in failed_users[:5]]}")
            logger.info(f"🔍 Первые 5 ID: {failed_users[:5]}")
        logger.info(f"🔍 Ключи в базе (первые 5): {list(self.users_db.keys())[:5]}")
        
        # Удаляем всех пользователей из списка ошибок
        for target_user_id in failed_users:
            try:
                # КРИТИЧНО: Конвертируем ID в строку, так как в базе ключи - строки
                target_user_id_str = str(target_user_id)
                
                logger.info(f"🔍 Удаляю пользователя: ID={target_user_id_str} (тип исходного: {type(target_user_id).__name__})")
                
                # Удаляем из базы данных
                if target_user_id_str in self.users_db:
                    username = self.users_db[target_user_id_str].get('username', 'Unknown')
                    del self.users_db[target_user_id_str]
                    removed_count += 1
                    logger.info(f"✅ Удалён неактивный пользователь {target_user_id_str} (@{username})")
                else:
                    logger.warning(f"⚠️ Пользователь {target_user_id_str} не найден в базе данных!")
                    # Пробуем найти вручную на случай если формат ключа отличается
                    found = False
                    for key in list(self.users_db.keys()):
                        if str(key) == target_user_id_str:
                            username = self.users_db[key].get('username', 'Unknown')
                            del self.users_db[key]
                            removed_count += 1
                            found = True
                            logger.info(f"✅ Удалён неактивный пользователь {key} (@{username}) после поиска")
                            break
                    if not found:
                        logger.error(f"❌ Пользователь {target_user_id_str} не найден в базе!")
                
                # Также удаляем из всех других структур (там могут быть и int и str)
                try:
                    target_user_id_int = int(target_user_id_str)
                    if target_user_id_int in self.access_check_history:
                        del self.access_check_history[target_user_id_int]
                    if target_user_id_int in self.random_message_history:
                        del self.random_message_history[target_user_id_int]
                    if target_user_id_int in self.user_warnings:
                        del self.user_warnings[target_user_id_int]
                    if target_user_id_int in self.blocked_users:
                        self.blocked_users.remove(target_user_id_int)
                except (ValueError, TypeError):
                    pass  # Если не удалось конвертировать в int, пропускаем
                    
            except Exception as e:
                logger.error(f"❌ Ошибка удаления пользователя {target_user_id}: {e}", exc_info=True)
        
        # Сохраняем базу
        self._save_users_db()
        
        # Формируем отчёт
        report_text = f"""✅ ОЧИСТКА ЗАВЕРШЕНА

📊 Статистика:
• Удалено пользователей: {removed_count}
• Осталось в базе: {len(self.users_db)}

⏰ Время: {datetime.now().strftime('%H:%M:%S %d.%m.%Y')}"""
        
        keyboard = [
            [InlineKeyboardButton("🔙 В админ-панель", callback_data="back_to_admin_panel")]
        ]
        
        await query.edit_message_text(
            report_text,
            reply_markup=InlineKeyboardMarkup(keyboard),
            parse_mode='Markdown'
        )
        
        # Очищаем список неактивных
        if hasattr(self, 'failed_users_list'):
            self.failed_users_list.pop(user_id, None)
        
        # Логируем событие
        self._add_admin_event(
            'clean_inactive',
            user_id,
            f"Очищено {removed_count} неактивных пользователей"
        )
    
    async def _send_broadcast_message(self, context: ContextTypes.DEFAULT_TYPE, user_id: int, broadcast_data: dict):
        """Отправить сообщение рассылки конкретному пользователю"""
        try:
            content_type = broadcast_data['content_type']
            content = broadcast_data['content']
            
            if content_type == 'text':
                await context.bot.send_message(
                    chat_id=user_id,
                    text=content,
                    parse_mode='HTML'
                )
            elif content_type == 'photo':
                # Обрезаем подпись до 1024 символов (лимит Telegram)
                caption = content['caption']
                if len(caption) > 1024:
                    logger.warning(f"⚠️ Подпись к фото слишком длинная ({len(caption)} символов), обрезаем до 1024")
                    caption = caption[:1021] + "..."
                
                await context.bot.send_photo(
                    chat_id=user_id,
                    photo=content['photo'],
                    caption=caption,
                    parse_mode='HTML'
                )
            elif content_type == 'video':
                # Обрезаем подпись до 1024 символов (лимит Telegram)
                caption = content['caption']
                if len(caption) > 1024:
                    caption = caption[:1021] + "..."
                
                await context.bot.send_video(
                    chat_id=user_id,
                    video=content['video'],
                    caption=caption,
                    parse_mode='HTML'
                )
            elif content_type == 'document':
                # Обрезаем подпись до 1024 символов (лимит Telegram)
                caption = content['caption']
                if len(caption) > 1024:
                    caption = caption[:1021] + "..."
                
                await context.bot.send_document(
                    chat_id=user_id,
                    document=content['document'],
                    caption=caption,
                    parse_mode='HTML'
                )
            elif content_type == 'audio':
                # Обрезаем подпись до 1024 символов (лимит Telegram)
                caption = content['caption']
                if len(caption) > 1024:
                    caption = caption[:1021] + "..."
                
                await context.bot.send_audio(
                    chat_id=user_id,
                    audio=content['audio'],
                    caption=caption,
                    parse_mode='HTML'
                )
            
            return True
            
        except Exception as e:
            logger.error(f"Ошибка отправки рассылки пользователю {user_id}: {e}")
            return False
    
    def _get_target_users(self, audience_type: str) -> list:
        """Получить список пользователей для рассылки"""
        # Убираем дубликаты используя set
        if audience_type == 'all':
            return list(set(self.users_db.keys()))
        elif audience_type == 'no_deposit':
            return list(set([
                user_id for user_id, user_data in self.users_db.items()
                if not user_data.get('deposited', False)
            ]))
        elif audience_type == 'verified':
            return list(set([
                user_id for user_id, user_data in self.users_db.items()
                if user_data.get('verified', False)
            ]))
        return []
    
    def _get_audience_name(self, audience_type: str) -> str:
        """Получить название аудитории"""
        names = {
            'all': 'Все пользователи',
            'no_deposit': 'Без депозита',
            'verified': 'Верифицированные'
        }
        return names.get(audience_type, 'Неизвестно')
    
    def _get_content_preview(self, content_type: str, content) -> str:
        """Получить превью контента"""
        if content_type == 'text':
            return f"📝 Текст: {content[:50]}{'...' if len(content) > 50 else ''}"
        elif content_type == 'photo':
            return f"🖼️ Фото: {content['caption'][:50]}{'...' if len(content['caption']) > 50 else ''}"
        elif content_type == 'video':
            return f"🎥 Видео: {content['caption'][:50]}{'...' if len(content['caption']) > 50 else ''}"
        elif content_type == 'document':
            return f"📄 Документ: {content['caption'][:50]}{'...' if len(content['caption']) > 50 else ''}"
        elif content_type == 'audio':
            return f"🎵 Аудио: {content['caption'][:50]}{'...' if len(content['caption']) > 50 else ''}"
        return "Неизвестный тип"

# Функции для админа
async def grant_access_to_user(bot_token: str, user_id: int, admin_chat_id: str, bot_instance=None):
    """Предоставить доступ пользователю (вызывается админом)"""
    
    success_message = """
🎉 *ДОСТУП ПРЕДОСТАВЛЕН!*

✅ *Ваша заявка одобрена!*

📊 *Теперь вы получаете:*
• Все торговые сигналы
• Точные точки входа
• Профессиональную аналитику
• Поддержку 24/7

🚀 *Начните зарабатывать прямо сейчас!*

💎 *Добро пожаловать в команду профи!*

👨‍💻 *Поддержка:* @kaktotakxm
    """.strip()
    
    try:
        response = requests.post(
            f"https://api.telegram.org/bot{bot_token}/sendMessage",
            data={
                'chat_id': user_id,
                'text': success_message,
                'parse_mode': 'Markdown'
            }
        )
        
        if response.status_code == 200:
            # Сбрасываем историю проверок доступа и предупреждения
            if bot_instance:
                if hasattr(bot_instance, 'access_check_history') and user_id in bot_instance.access_check_history:
                    bot_instance.access_check_history[user_id] = []
                if hasattr(bot_instance, 'user_warnings') and user_id in bot_instance.user_warnings:
                    bot_instance.user_warnings[user_id] = 0
                if hasattr(bot_instance, '_save_users_db'):
                    bot_instance._save_users_db()
            
            # Уведомляем админа
            requests.post(
                f"https://api.telegram.org/bot{bot_token}/sendMessage",
                data={
                    'chat_id': admin_chat_id,
                    'text': f"✅ Доступ предоставлен пользователю {user_id}"
                }
            )
            logger.info(f"✅ Доступ предоставлен пользователю {user_id}")
            return True
    except Exception as e:
        logger.error(f"Ошибка предоставления доступа: {e}")
        
    return False

    
async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик ошибок"""
    logger.error(f"Ошибка при обработке обновления: {context.error}")
    
    # Если есть пользователь, отправляем сообщение об ошибке
    if update and update.effective_user:
        try:
            await context.bot.send_message(
                chat_id=update.effective_user.id,
                text="❌ Произошла ошибка. Попробуйте позже."
            )
        except Exception as e:
            logger.error(f"Не удалось отправить сообщение об ошибке: {e}")

class DataRequestHandler(http.server.BaseHTTPRequestHandler):
    """Обработчик запросов к API данных"""
    
    def do_GET(self):
        """Обработка GET запросов"""
        if self.path == '/users':
            try:
                # Читаем файл базы данных
                with open("info_bot_users.json", 'r', encoding='utf-8') as f:
                    data = f.read()
                
                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', '*') # Разрешаем запросы с любых доменов
                self.send_header('Access-Control-Allow-Headers', 'ngrok-skip-browser-warning, Content-Type') # Разрешаем наши заголовки
                self.end_headers()
                self.wfile.write(data.encode('utf-8'))
                return
            except Exception as e:
                logger.error(f"API Error: {e}")
                self.send_response(500)
                self.end_headers()
                return
        
        # Если путь не найден
        self.send_response(404)
        self.end_headers()

    def do_OPTIONS(self):
        """Обработка OPTIONS запросов (CORS)"""
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'ngrok-skip-browser-warning, Content-Type')
        self.end_headers()

def run_api_server(port=8081):
    """Запуск API сервера в отдельном потоке"""
    try:
        handler = DataRequestHandler
        with socketserver.TCPServer(("", port), handler) as httpd:
            logger.info(f"🚀 API Server running on port {port}")
            httpd.serve_forever()
    except Exception as e:
        logger.error(f"❌ Ошибка API сервера: {e}")
def main():
    """Main function"""
    # Запускаем API сервер в отдельном потоке
    try:
        api_thread = threading.Thread(target=run_api_server, kwargs={'port': 8081}, daemon=True)
        api_thread.start()
    except Exception as e:
        logger.error(f"❌ Ошибка запуска API сервера: {e}")

    bot = InfoBot()
    
    # Создаем Application и передаем токен
    application = Application.builder().token(bot.bot_token).build()
    
    # Регистрация обработчика ошибок
    application.add_error_handler(error_handler)
    
    # Регистрация обработчиков команд

    application.add_handler(CommandHandler("start", bot.start_command))
    application.add_handler(CommandHandler("help", bot.help_command))
    application.add_handler(CommandHandler("status", bot.status_command))
    application.add_handler(CommandHandler("language", bot.language_command))
    application.add_handler(CommandHandler("admin_stats", bot.admin_stats_command))
    application.add_handler(CommandHandler("reset_checks", bot.reset_checks_command))
    application.add_handler(CommandHandler("unblock_user", bot.unblock_user_command))
    application.add_handler(CommandHandler("blocked_users", bot.blocked_users_command))
    application.add_handler(CommandHandler("admin_panel", bot.admin_panel_command))
    application.add_handler(CommandHandler("referral", bot.referral_command))
    
    # Обработчики кнопок
    application.add_handler(CallbackQueryHandler(bot.back_to_start_callback, pattern="back_to_start"))
    application.add_handler(CallbackQueryHandler(bot.instruction_callback, pattern="instruction"))
    application.add_handler(CallbackQueryHandler(bot.language_callback, pattern="^lang_"))
    
    # Обработчики меню трейдера
    application.add_handler(CallbackQueryHandler(bot.trader_menu_callback, pattern="trader_menu"))
    application.add_handler(CallbackQueryHandler(bot.level_free_callback, pattern="level_free"))
    application.add_handler(CallbackQueryHandler(bot.level_pro_callback, pattern="level_pro"))
    application.add_handler(CallbackQueryHandler(bot.level_mentor_callback, pattern="level_mentor"))
    application.add_handler(CallbackQueryHandler(bot.level_elite_callback, pattern="level_elite"))
    
    # Обработчики промокодов и проверки подписки
    application.add_handler(CallbackQueryHandler(bot.promocodes_menu_callback, pattern="promocodes_menu"))
    application.add_handler(CallbackQueryHandler(bot.check_subscription_callback, pattern="check_subscription"))
    application.add_handler(ChatMemberHandler(bot.handle_chat_member_update, ChatMemberHandler.CHAT_MEMBER))
    
    # Обработчики FAQ
    application.add_handler(CallbackQueryHandler(bot.faq_menu_callback, pattern="faq_menu"))
    application.add_handler(CallbackQueryHandler(bot.faq_how_start_callback, pattern="faq_how_start"))
    application.add_handler(CallbackQueryHandler(bot.faq_have_account_callback, pattern="faq_have_account"))
    application.add_handler(CallbackQueryHandler(bot.faq_get_indicator_callback, pattern="faq_get_indicator"))
    
    # Обработчики навигации
    application.add_handler(CallbackQueryHandler(bot.back_to_main_callback, pattern="back_to_main"))
    application.add_handler(CallbackQueryHandler(bot.change_language_callback, pattern="change_language"))
    application.add_handler(CallbackQueryHandler(bot.admin_panel_callback, pattern="^admin_panel$"))
    
    # Обработчики админ-панели
    application.add_handler(CallbackQueryHandler(bot.admin_export_callback, pattern="admin_export_users"))
    application.add_handler(CallbackQueryHandler(bot.admin_refresh_callback, pattern="admin_refresh"))
    application.add_handler(CallbackQueryHandler(bot.admin_stats_detailed_callback, pattern="admin_stats"))
    application.add_handler(CallbackQueryHandler(bot.admin_events_callback, pattern="admin_events"))
    application.add_handler(CallbackQueryHandler(bot.admin_send_motivation_callback, pattern="admin_send_motivation"))
    application.add_handler(CallbackQueryHandler(bot.admin_clear_stats_callback, pattern="admin_clear_stats"))
    application.add_handler(CallbackQueryHandler(bot.admin_clear_confirm_callback, pattern="admin_clear_confirm"))
    application.add_handler(CallbackQueryHandler(bot.admin_clear_full_callback, pattern="admin_clear_full"))
    application.add_handler(CallbackQueryHandler(bot.back_to_admin_panel_callback, pattern="back_to_admin_panel"))
    
    # Обработчики рассылки
    application.add_handler(CallbackQueryHandler(bot.admin_new_broadcast_callback, pattern="^admin_new_broadcast$"))
    application.add_handler(CallbackQueryHandler(bot.admin_select_audience_callback, pattern="^broadcast_audience_"))
    application.add_handler(CallbackQueryHandler(bot.admin_broadcast_type_callback, pattern="^broadcast_type_"))
    application.add_handler(CallbackQueryHandler(bot.confirm_broadcast_callback, pattern="^broadcast_confirm$"))
    application.add_handler(CallbackQueryHandler(bot.confirm_long_caption_broadcast_callback, pattern="^broadcast_confirm_long$"))
    application.add_handler(CallbackQueryHandler(bot.cancel_broadcast_callback, pattern="^broadcast_cancel$"))
    application.add_handler(CallbackQueryHandler(bot.clean_inactive_users_callback, pattern="^clean_inactive_users$"))
    
    # Обработчики реферальной системы (Здравый Трейдер)
    application.add_handler(CallbackQueryHandler(bot.healthy_trader_menu_callback, pattern="^healthy_trader_menu$"))
    application.add_handler(CallbackQueryHandler(bot.referral_stats_callback, pattern="^referral_stats$"))
    application.add_handler(CallbackQueryHandler(bot.referral_menu_callback, pattern="^referral_menu$"))
    application.add_handler(CallbackQueryHandler(bot.referral_copy_link_callback, pattern="^referral_copy_link$"))
    application.add_handler(CallbackQueryHandler(bot.referral_share_message_callback, pattern="^referral_share_message$"))
    application.add_handler(CallbackQueryHandler(bot.referral_rules_callback, pattern="^referral_rules$"))
    application.add_handler(CallbackQueryHandler(bot.referral_claim_bonus_callback, pattern="^referral_claim_bonus$"))
    application.add_handler(CallbackQueryHandler(bot.claim_bonus_callback, pattern="^claim_bonus_"))
    application.add_handler(CallbackQueryHandler(bot.confirm_bonus_callback, pattern="^confirm_bonus_"))
    application.add_handler(CallbackQueryHandler(bot.admin_referral_stats_callback, pattern="^admin_referral_stats$"))
    application.add_handler(CallbackQueryHandler(bot.admin_referral_requests_callback, pattern="^admin_referral_requests$"))
    application.add_handler(CallbackQueryHandler(bot.approve_bonus_callback, pattern="^approve_bonus_"))
    application.add_handler(CallbackQueryHandler(bot.reject_bonus_callback, pattern="^reject_bonus_"))
    application.add_handler(CallbackQueryHandler(bot.confirm_deposit_callback, pattern="^confirm_deposit_"))

    # Обработчики сообщений
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, bot.handle_message))
    application.add_handler(MessageHandler(filters.PHOTO, bot.handle_message))
    application.add_handler(MessageHandler(filters.VIDEO, bot.handle_message))
    application.add_handler(MessageHandler(filters.Document.ALL, bot.handle_message))
    application.add_handler(MessageHandler(filters.AUDIO, bot.handle_message))
    
    # Запускаем планировщик мотивационных рассылок
    bot.start_motivation_scheduler(application)
    
    # Запускаем бота
    logger.info("🤖 Бот @info_xm_trust_bot запущен с поддержкой мультиязычности!")
    logger.info("🌐 Поддерживаемые языки: Русский, English, ไทย, Español, العربية, Українська")
    if bot.motivation_auto_enabled:
        logger.info(f"🔔 Мотивационные рассылки: активны (интервал {bot.motivation_interval_hours} часов)")
    else:
        logger.info("🔕 Мотивационные рассылки: ручной режим (автопланировщик отключён)")
    
    logger.info("⏳ Ожидание обновлений (polling)...")
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()