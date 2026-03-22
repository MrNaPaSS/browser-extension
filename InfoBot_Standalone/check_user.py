import json
with open('info_bot_users.json', 'r', encoding='utf-8') as f:
    data = json.load(f)
    print(f"Total users: {len(data)}")
    user = data.get('8658798174')
    if user:
        print(f"User found: {json.dumps(user, indent=2)}")
    else:
        print("User 8658798174 not found.")
        
    for k, v in data.items():
        po_id = v.get('pocket_option_id')
        if po_id and '122004705' in po_id:
            print(f"Found user id {k} with PO ID {po_id}: {v.get('verified')} {v.get('deposited')}")
