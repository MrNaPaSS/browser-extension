#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Реферальная система "Здравый Трейдер"
Модуль управления рефералами, бонусами и уведомлениями
"""

import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Any

from referral_config import (
    REFERRAL_SETTINGS,
    REFERRAL_BONUS_LEVELS,
    get_bonus_for_referrals,
    get_next_bonus_level,
    get_available_bonuses,
    get_progress_bar
)

logger = logging.getLogger(__name__)


class ReferralManager:
    """Менеджер реферальной системы"""
    
    def __init__(self, users_db: Dict, users_db_file: str, bot_username: str = "moneyhoney7_bot"):
        """
        Инициализация менеджера рефералов
        
        Args:
            users_db: Словарь с данными пользователей
            users_db_file: Путь к файлу БД пользователей
            bot_username: Username бота для генерации ссылок
        """
        self.users_db = users_db
        self.users_db_file = users_db_file
        self.bot_username = bot_username
        self.settings = REFERRAL_SETTINGS
        
        # Инициализируем реферальные данные для существующих пользователей
        self._init_referral_data()
    
    def _init_referral_data(self):
        """Инициализирует реферальные данные для всех пользователей"""
        for user_id, user_data in self.users_db.items():
            if "referral" not in user_data:
                user_data["referral"] = self._create_default_referral_data(user_id)
    
    def _create_default_referral_data(self, user_id: str) -> Dict:
        """Создаёт структуру реферальных данных по умолчанию"""
        return {
            "code": f"ref_{user_id}",
            "invited_by": None,
            "referrals": [],              # Все перешедшие по ссылке
            "activated_referrals": [],    # Засчитанные (с депозитом)
            "bonuses_claimed": [],        # ID забранных бонусов
            "tradingview_username": None,
            "pending_bonus_request": None,  # ID ожидающего бонуса или None
            "bonus_requests_history": []  # История заявок на бонусы
        }
    
    def _save_users_db(self):
        """Сохраняет БД пользователей в файл"""
        try:
            with open(self.users_db_file, 'w', encoding='utf-8') as f:
                json.dump(self.users_db, f, ensure_ascii=False, indent=2)
            return True
        except Exception as e:
            logger.error(f"Ошибка сохранения БД: {e}")
            return False
    
    def get_referral_link(self, user_id: str) -> str:
        """
        Получает реферальную ссылку пользователя
        
        Args:
            user_id: ID пользователя
            
        Returns:
            Реферальная ссылка
        """
        code = f"ref_{user_id}"
        return f"https://t.me/{self.bot_username}?start={code}"
    
    def get_referral_code(self, user_id: str) -> str:
        """Получает реферальный код пользователя"""
        return f"ref_{user_id}"
    
    def parse_referral_code(self, start_param: str) -> Optional[str]:
        """
        Парсит реферальный код из параметра start
        
        Args:
            start_param: Параметр из /start ref_123456
            
        Returns:
            ID реферера или None
        """
        if not start_param:
            return None
        
        if start_param.startswith("ref_"):
            referrer_id = start_param[4:]  # Убираем "ref_"
            # Проверяем что это число
            if referrer_id.isdigit():
                return referrer_id
        
        return None
    
    def register_referral_click(self, new_user_id: str, referrer_id: str) -> Tuple[bool, str]:
        """
        Регистрирует переход по реферальной ссылке
        
        Args:
            new_user_id: ID нового пользователя
            referrer_id: ID реферера
            
        Returns:
            Tuple (успех, сообщение)
        """
        # Проверка на самореферал
        if self.settings["anti_fraud"]["prevent_self_referral"]:
            if new_user_id == referrer_id:
                return False, "Нельзя использовать собственную ссылку"
        
        # Проверяем существует ли реферер
        if referrer_id not in self.users_db:
            return False, "Реферер не найден"
        
        # Инициализируем данные нового пользователя если нужно
        if new_user_id not in self.users_db:
            return False, "Пользователь не зарегистрирован"
        
        user_data = self.users_db[new_user_id]
        if "referral" not in user_data:
            user_data["referral"] = self._create_default_referral_data(new_user_id)
        
        # Проверяем не был ли уже приглашён
        if self.settings["anti_fraud"]["one_referrer_only"]:
            if user_data["referral"]["invited_by"] is not None:
                return False, "Пользователь уже был приглашён"
        
        # Регистрируем реферала
        user_data["referral"]["invited_by"] = referrer_id
        
        # Добавляем в список рефералов у реферера
        referrer_data = self.users_db[referrer_id]
        if "referral" not in referrer_data:
            referrer_data["referral"] = self._create_default_referral_data(referrer_id)
        
        if new_user_id not in referrer_data["referral"]["referrals"]:
            referrer_data["referral"]["referrals"].append(new_user_id)
        
        self._save_users_db()
        
        return True, "Реферал зарегистрирован"
    
    def check_and_activate_referral(self, user_id: str) -> Tuple[bool, Optional[str]]:
        """
        Проверяет и активирует реферала (когда выполнены условия)
        
        Args:
            user_id: ID пользователя для проверки
            
        Returns:
            Tuple (был ли активирован, ID реферера для уведомления)
        """
        if user_id not in self.users_db:
            return False, None
        
        user_data = self.users_db[user_id]
        
        # Проверяем условия активации
        conditions = self.settings["activation_conditions"]
        
        if conditions["require_po_id"]:
            if not user_data.get("pocket_option_id"):
                return False, None
        
        if conditions["require_deposit"]:
            if not user_data.get("deposited", False):
                return False, None
        
        # Проверяем есть ли реферер
        if "referral" not in user_data:
            return False, None
        
        referrer_id = user_data["referral"].get("invited_by")
        if not referrer_id:
            return False, None
        
        # Проверяем не был ли уже активирован
        if referrer_id not in self.users_db:
            return False, None
        
        referrer_data = self.users_db[referrer_id]
        if "referral" not in referrer_data:
            referrer_data["referral"] = self._create_default_referral_data(referrer_id)
        
        if user_id in referrer_data["referral"]["activated_referrals"]:
            return False, None  # Уже активирован
        
        # Проверка уникальности PO ID
        if self.settings["anti_fraud"]["check_unique_po_id"]:
            po_id = user_data.get("pocket_option_id")
            if po_id:
                for uid, udata in self.users_db.items():
                    if uid != user_id and udata.get("pocket_option_id") == po_id:
                        logger.warning(f"Дубликат PO ID: {po_id} у пользователей {user_id} и {uid}")
                        return False, None
        
        # Активируем реферала
        referrer_data["referral"]["activated_referrals"].append(user_id)
        self._save_users_db()
        
        logger.info(f"Реферал {user_id} активирован для {referrer_id}")
        return True, referrer_id
    
    def get_referral_stats(self, user_id: str) -> Dict:
        """
        Получает статистику рефералов пользователя
        
        Args:
            user_id: ID пользователя
            
        Returns:
            Словарь со статистикой
        """
        if user_id not in self.users_db:
            return {
                "total_clicks": 0,
                "activated_count": 0,
                "current_bonus": None,
                "next_level": None,
                "remaining": 0,
                "progress_bar": "",
                "available_bonuses": [],
                "claimed_bonuses": []
            }
        
        user_data = self.users_db[user_id]
        if "referral" not in user_data:
            user_data["referral"] = self._create_default_referral_data(user_id)
            self._save_users_db()
        
        ref_data = user_data["referral"]
        activated_count = len(ref_data.get("activated_referrals", []))
        claimed = ref_data.get("bonuses_claimed", [])
        
        current_bonus = get_bonus_for_referrals(activated_count)
        next_level, remaining = get_next_bonus_level(activated_count)
        available_bonuses = get_available_bonuses(activated_count, claimed)
        
        return {
            "total_clicks": len(ref_data.get("referrals", [])),
            "activated_count": activated_count,
            "current_bonus": current_bonus,
            "next_level": next_level,
            "remaining": remaining,
            "progress_bar": get_progress_bar(activated_count, next_level),
            "available_bonuses": available_bonuses,
            "claimed_bonuses": claimed,
            "pending_bonus_request": ref_data.get("pending_bonus_request"),
            "tradingview_username": ref_data.get("tradingview_username")
        }
    
    def get_referral_list(self, user_id: str) -> List[Dict]:
        """
        Получает список рефералов пользователя с их статусами
        
        Args:
            user_id: ID пользователя
            
        Returns:
            Список рефералов с информацией
        """
        if user_id not in self.users_db:
            return []
        
        user_data = self.users_db[user_id]
        if "referral" not in user_data:
            return []
        
        ref_data = user_data["referral"]
        referrals = ref_data.get("referrals", [])
        activated = set(ref_data.get("activated_referrals", []))
        
        result = []
        for ref_id in referrals:
            if ref_id in self.users_db:
                ref_user = self.users_db[ref_id]
                result.append({
                    "user_id": ref_id,
                    "username": ref_user.get("username", "Пользователь"),
                    "registered_at": ref_user.get("registered_at"),
                    "is_activated": ref_id in activated,
                    "has_po_id": bool(ref_user.get("pocket_option_id")),
                    "has_deposit": ref_user.get("deposited", False)
                })
        
        return result
    
    def request_bonus(self, user_id: str, bonus_id: str, tradingview_username: str = None) -> Tuple[bool, str]:
        """
        Создаёт заявку на получение бонуса
        
        Args:
            user_id: ID пользователя
            bonus_id: ID бонуса (level_1, level_2, level_3)
            tradingview_username: Username в TradingView (опционально)
            
        Returns:
            Tuple (успех, сообщение)
        """
        if user_id not in self.users_db:
            return False, "Пользователь не найден"
        
        user_data = self.users_db[user_id]
        if "referral" not in user_data:
            return False, "Нет данных о рефералах"
        
        ref_data = user_data["referral"]
        stats = self.get_referral_stats(user_id)
        
        # Проверяем что бонус доступен
        available_ids = [b["id"] for b in stats["available_bonuses"]]
        if bonus_id not in available_ids:
            return False, "Бонус недоступен или уже получен"
        
        # Проверяем нет ли уже активной заявки
        if ref_data.get("pending_bonus_request"):
            return False, "У вас уже есть активная заявка на бонус"
        
        # Создаём заявку
        ref_data["pending_bonus_request"] = bonus_id
        if tradingview_username:
            ref_data["tradingview_username"] = tradingview_username
        
        # Добавляем в историю
        request_record = {
            "bonus_id": bonus_id,
            "requested_at": datetime.now().isoformat(),
            "status": "pending",
            "tradingview_username": tradingview_username
        }
        if "bonus_requests_history" not in ref_data:
            ref_data["bonus_requests_history"] = []
        ref_data["bonus_requests_history"].append(request_record)
        
        self._save_users_db()
        
        # Находим информацию о бонусе
        bonus_info = None
        for level in REFERRAL_BONUS_LEVELS:
            if level["id"] == bonus_id:
                bonus_info = level
                break
        
        return True, f"Заявка на {bonus_info['bonus_name'] if bonus_info else bonus_id} создана"
    
    def approve_bonus(self, user_id: str, admin_id: str) -> Tuple[bool, str]:
        """
        Одобряет заявку на бонус (для админа)
        
        Args:
            user_id: ID пользователя
            admin_id: ID админа
            
        Returns:
            Tuple (успех, сообщение)
        """
        if user_id not in self.users_db:
            return False, "Пользователь не найден"
        
        user_data = self.users_db[user_id]
        if "referral" not in user_data:
            return False, "Нет данных о рефералах"
        
        ref_data = user_data["referral"]
        pending = ref_data.get("pending_bonus_request")
        
        if not pending:
            return False, "Нет активной заявки"
        
        # Одобряем бонус
        if pending not in ref_data.get("bonuses_claimed", []):
            if "bonuses_claimed" not in ref_data:
                ref_data["bonuses_claimed"] = []
            ref_data["bonuses_claimed"].append(pending)
        
        # Находим информацию о бонусе для установки срока подписки
        bonus_info = None
        for level in REFERRAL_BONUS_LEVELS:
            if level["id"] == pending:
                bonus_info = level
                break
        
        # Сохраняем информацию о активной подписке
        now = datetime.now()
        ref_data["active_subscription"] = {
            "bonus_id": pending,
            "bonus_name": bonus_info["bonus_name"] if bonus_info else pending,
            "start_date": now.isoformat(),
            "end_date": (now + timedelta(days=bonus_info["bonus_days"])).isoformat() if bonus_info and bonus_info["bonus_days"] > 0 else None,
            "days": bonus_info["bonus_days"] if bonus_info else 0
        }
        
        # Обновляем историю
        for request in reversed(ref_data.get("bonus_requests_history", [])):
            if request.get("bonus_id") == pending and request.get("status") == "pending":
                request["status"] = "approved"
                request["approved_at"] = now.isoformat()
                request["approved_by"] = admin_id
                break
        
        ref_data["pending_bonus_request"] = None
        
        # Снимаем рефералов - для всех бонусов одинаково
        # Находим сколько рефералов требует этот бонус
        for level in REFERRAL_BONUS_LEVELS:
            if level["id"] == pending:
                bonus_info = level
                break
        
        if bonus_info:
            # Снимаем нужное количество рефералов
            required = bonus_info["friends_required"]
            current_referrals = ref_data.get("activated_referrals", [])
            if len(current_referrals) >= required:
                ref_data["activated_referrals"] = current_referrals[required:]
                logger.info(f"Снято {required} рефералов для {user_id}, осталось {len(ref_data['activated_referrals'])}")
        
        self._save_users_db()
        
        return True, f"Бонус {pending} одобрен"
    
    def reject_bonus(self, user_id: str, admin_id: str, reason: str = "") -> Tuple[bool, str]:
        """
        Отклоняет заявку на бонус (для админа)
        
        Args:
            user_id: ID пользователя
            admin_id: ID админа
            reason: Причина отклонения
            
        Returns:
            Tuple (успех, сообщение)
        """
        if user_id not in self.users_db:
            return False, "Пользователь не найден"
        
        user_data = self.users_db[user_id]
        if "referral" not in user_data:
            return False, "Нет данных о рефералах"
        
        ref_data = user_data["referral"]
        pending = ref_data.get("pending_bonus_request")
        
        if not pending:
            return False, "Нет активной заявки"
        
        # Обновляем историю
        for request in reversed(ref_data.get("bonus_requests_history", [])):
            if request.get("bonus_id") == pending and request.get("status") == "pending":
                request["status"] = "rejected"
                request["rejected_at"] = datetime.now().isoformat()
                request["rejected_by"] = admin_id
                request["rejection_reason"] = reason
                break
        
        ref_data["pending_bonus_request"] = None
        self._save_users_db()
        
        return True, f"Заявка на {pending} отклонена"
    
    def get_pending_bonus_requests(self) -> List[Dict]:
        """
        Получает список всех ожидающих заявок на бонусы (для админа)
        
        Returns:
            Список заявок с информацией о пользователях
        """
        pending = []
        
        for user_id, user_data in self.users_db.items():
            if "referral" not in user_data:
                continue
            
            ref_data = user_data["referral"]
            bonus_id = ref_data.get("pending_bonus_request")
            
            if bonus_id:
                # Находим информацию о бонусе
                bonus_info = None
                for level in REFERRAL_BONUS_LEVELS:
                    if level["id"] == bonus_id:
                        bonus_info = level
                        break
                
                pending.append({
                    "user_id": user_id,
                    "username": user_data.get("username", "Пользователь"),
                    "bonus_id": bonus_id,
                    "bonus_info": bonus_info,
                    "tradingview_username": ref_data.get("tradingview_username"),
                    "activated_referrals": len(ref_data.get("activated_referrals", []))
                })
        
        return pending
    
    def get_top_referrers(self, limit: int = 10) -> List[Dict]:
        """
        Получает топ рефереров по количеству активированных рефералов
        
        Args:
            limit: Максимальное количество в списке
            
        Returns:
            Список топ рефереров
        """
        referrers = []
        
        for user_id, user_data in self.users_db.items():
            if "referral" not in user_data:
                continue
            
            ref_data = user_data["referral"]
            activated = len(ref_data.get("activated_referrals", []))
            
            if activated > 0:
                referrers.append({
                    "user_id": user_id,
                    "username": user_data.get("username", "Пользователь"),
                    "activated_count": activated,
                    "total_clicks": len(ref_data.get("referrals", []))
                })
        
        # Сортируем по количеству активированных рефералов
        referrers.sort(key=lambda x: x["activated_count"], reverse=True)
        
        return referrers[:limit]
    
    def get_global_stats(self) -> Dict:
        """
        Получает глобальную статистику реферальной системы
        
        Returns:
            Словарь с общей статистикой
        """
        total_referrals = 0
        total_activated = 0
        total_bonuses_claimed = 0
        pending_requests = 0
        
        for user_data in self.users_db.values():
            if "referral" not in user_data:
                continue
            
            ref_data = user_data["referral"]
            total_referrals += len(ref_data.get("referrals", []))
            total_activated += len(ref_data.get("activated_referrals", []))
            total_bonuses_claimed += len(ref_data.get("bonuses_claimed", []))
            
            if ref_data.get("pending_bonus_request"):
                pending_requests += 1
        
        return {
            "total_referrals": total_referrals,
            "total_activated": total_activated,
            "total_bonuses_claimed": total_bonuses_claimed,
            "pending_requests": pending_requests,
            "conversion_rate": (total_activated / total_referrals * 100) if total_referrals > 0 else 0
        }

