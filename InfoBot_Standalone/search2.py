import sys
try:
    with open('telegram_bot_handler.py', 'r', encoding='utf-8') as f:
        lines = f.readlines()
    for i, line in enumerate(lines):
        if 'confirm_deposit' in line:
            print(f"{i+1}: {line.strip()}")
except Exception as e:
    print(str(e))
