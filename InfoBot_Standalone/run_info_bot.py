#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Запуск инфо бота
"""

import logging
import sys
import io

# Устанавливаем кодировку UTF-8 для вывода в консоль
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

from telegram_bot_handler import main

if __name__ == "__main__":
    
    print("Zapusk info bota...")  # ASCII-совместимый вывод
    main()
