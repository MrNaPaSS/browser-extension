import sys
with open('telegram_bot_handler.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()
for i, line in enumerate(lines):
    if 'PO' in line or 'pocket' in line.lower() or 'ID' in line:
        if 'Получен ID' in line or 'Форматированный ID' in line or 'pocket_option_id' in line:
            print(f"{i+1}: {line.strip()}")
