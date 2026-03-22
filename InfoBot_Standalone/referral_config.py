#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Конфигурация реферальной системы "Здравый Трейдер"
Система приглашений друзей с бонусами — подписка на индикатор TradingView
"""

from typing import Dict, List, Tuple

# ============================================
# УРОВНИ БОНУСОВ
# ============================================

REFERRAL_BONUS_LEVELS: List[Dict] = [
    {
        "id": "level_1",
        "friends_required": 2,
        "bonus_days": 7,
        "bonus_name": "Неделя подписки",
        "bonus_name_en": "1 week subscription",
        "description": "Подписка на индикатор Black Mirror Ultra на 7 дней",
        "description_en": "Black Mirror Ultra indicator subscription for 7 days"
    },
    {
        "id": "level_2", 
        "friends_required": 5,
        "bonus_days": 30,
        "bonus_name": "Месяц подписки",
        "bonus_name_en": "1 month subscription",
        "description": "Подписка на индикатор Black Mirror Ultra на 30 дней",
        "description_en": "Black Mirror Ultra indicator subscription for 30 days"
    },
    {
        "id": "level_3",
        "friends_required": 10,
        "bonus_days": 7,
        "bonus_name": "Софт + Менторство",
        "bonus_name_en": "Software + Mentorship",
        "description": "Полный доступ к софту и персональное менторство",
        "description_en": "Full software access and personal mentorship",
        "special": "mentorship"
    }
]

# ============================================
# НАСТРОЙКИ РЕФЕРАЛЬНОЙ СИСТЕМЫ
# ============================================

REFERRAL_SETTINGS = {
    # Условия засчитывания реферала
    "activation_conditions": {
        "require_po_id": True,          # Требуется ввод Pocket Option ID
        "require_deposit": True,         # Требуется подтверждение депозита (deposited=true)
    },
    
    # Защита от накруток
    "anti_fraud": {
        "check_unique_po_id": True,      # Проверка уникальности PO ID
        "prevent_self_referral": True,   # Запрет реферить самого себя
        "one_referrer_only": True,       # Один реферер на пользователя (первая ссылка)
    },
    
    # Формат реферальной ссылки
    "link_format": "ref_{user_id}",      # t.me/bot?start=ref_123456
    
    # Уведомления
    "notifications": {
        "notify_on_click": True,         # Уведомлять когда кто-то перешёл по ссылке
        "notify_on_activation": True,    # Уведомлять когда реферал засчитан
        "notify_on_level_up": True,      # Уведомлять о достижении уровня
        "notify_admin_on_bonus_claim": True,  # Уведомлять админа о заявках на бонус
    },
    
    # Администратор
    "admin_chat_id": "511442168",
    
    # Контакт для связи по бонусам
    "support_contact": "@kaktotakxm",
}


def get_bonus_for_referrals(count: int) -> Dict | None:
    """
    Получает бонус для количества рефералов
    
    Args:
        count: Количество активированных рефералов
        
    Returns:
        Dict с информацией о бонусе или None
    """
    for level in reversed(REFERRAL_BONUS_LEVELS):
        if count >= level["friends_required"]:
            return level
    return None


def get_next_bonus_level(count: int) -> Tuple[Dict | None, int]:
    """
    Получает следующий уровень бонуса и сколько рефералов осталось
    
    Args:
        count: Текущее количество активированных рефералов
        
    Returns:
        Tuple (следующий уровень или None, сколько осталось до него)
    """
    for level in REFERRAL_BONUS_LEVELS:
        if count < level["friends_required"]:
            remaining = level["friends_required"] - count
            return level, remaining
    return None, 0


def get_available_bonuses(count: int, claimed_bonuses: List[str]) -> List[Dict]:
    """
    Получает список доступных (незабранных) бонусов
    При получении высшего бонуса - нижние недоступны
    
    Args:
        count: Количество активированных рефералов
        claimed_bonuses: Список уже забранных бонусов (id)
        
    Returns:
        Список доступных бонусов
    """
    # Находим максимальный полученный уровень
    max_claimed_level = 0
    for level in REFERRAL_BONUS_LEVELS:
        if level["id"] in claimed_bonuses:
            level_num = int(level["id"].split("_")[1])  # level_1 -> 1
            if level_num > max_claimed_level:
                max_claimed_level = level_num
    
    available = []
    for level in REFERRAL_BONUS_LEVELS:
        level_num = int(level["id"].split("_")[1])
        # Бонус доступен если: достаточно рефералов, не забран, и выше максимального забранного
        if count >= level["friends_required"] and level["id"] not in claimed_bonuses and level_num > max_claimed_level:
            available.append(level)
    return available


def get_progress_bar(count: int, next_level: Dict) -> str:
    """
    Генерирует прогресс-бар до следующего уровня
    
    Args:
        count: Текущее количество рефералов
        next_level: Следующий уровень
        
    Returns:
        Строка с прогресс-баром
    """
    if not next_level:
        # Все уровни достигнуты - показываем полную шкалу и общий счёт
        max_target = REFERRAL_BONUS_LEVELS[-1]["friends_required"] if REFERRAL_BONUS_LEVELS else 10
        bar = "▓" * max_target
        return f"🏆 [{bar}] {count} друзей"
    
    target = next_level["friends_required"]
    filled = min(count, target)
    empty = target - filled
    
    bar = "▓" * filled + "░" * empty
    return f"[{bar}] {filled}/{target}"

