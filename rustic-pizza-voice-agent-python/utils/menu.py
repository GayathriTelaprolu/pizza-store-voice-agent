import os
import json
import gspread
from google.oauth2.service_account import Credentials

SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets.readonly",
    "https://www.googleapis.com/auth/drive.readonly",
]

_menu_cache = None


def get_sheet_client():
    creds_json = os.getenv("GOOGLE_CREDENTIALS_JSON")
    creds_dict = json.loads(creds_json)
    creds = Credentials.from_service_account_info(creds_dict, scopes=SCOPES)
    return gspread.authorize(creds)


def get_menu():
    global _menu_cache
    if _menu_cache:
        return _menu_cache
    try:
        client = get_sheet_client()
        sheet = client.open("Rustic Pizza Menu").sheet1
        rows = sheet.get_all_records()
        menu = {}
        for row in rows:
            if str(row.get("Available", "Yes")).strip() != "Yes":
                continue
            category = row["Category"].lower().replace(" ", "_")
            if category not in menu:
                menu[category] = {
                    "label": row["Category"],
                    "items": []
                }
            menu[category]["items"].append({
                "name": row["Name"],
                "price": float(row["Price"]),
                "keywords": [k.strip().lower() for k in str(row["Keywords"]).split(",")]
            })
        _menu_cache = menu
        print("Menu loaded from Google Sheets successfully!")
        return menu
    except Exception as e:
        print(f"Google Sheets error: {e} — using hardcoded menu")
        return get_hardcoded_menu()


def get_menu_text():
    menu = get_menu()
    lines = ["Rustic Pizza Menu:\n"]
    for cat in menu.values():
        lines.append(f"{cat['label']}:")
        for item in cat["items"]:
            lines.append(f"  - {item['name']}: ${item['price']:.2f}")
        lines.append("")
    return "\n".join(lines)


def find_menu_item(query: str):
    menu = get_menu()
    q = query.lower()
    best = None
    best_len = 0
    for cat in menu.values():
        for item in cat["items"]:
            for kw in item["keywords"]:
                if kw in q and len(kw) > best_len:
                    best_len = len(kw)
                    best = item
    return best


def refresh_menu():
    global _menu_cache
    _menu_cache = None
    print("Menu cache cleared — will reload on next call")
    return get_menu()


def get_hardcoded_menu():
    # Fallback menu if Google Sheets is not configured
    # To add new items: just add to this list
    # Format: {"name": "Item Name", "price": 0.00, "keywords": ["keyword1", "keyword2"]}
    return {
        "pizza": {
            "label": "Pizza",
            "items": [
                {"name": "Cheese Pizza (small)", "price": 11.25, "keywords": ["small cheese pizza", "small cheese", "cheese pizza small"]},
                {"name": "Cheese Pizza (large)", "price": 19.50, "keywords": ["large cheese pizza", "large cheese", "cheese pizza"]},
                {"name": "Margarita Pizza", "price": 17.50, "keywords": ["margarita pizza", "margherita pizza", "margarita", "margherita"]},
                {"name": "Buffalo Chicken Pizza", "price": 17.50, "keywords": ["buffalo chicken pizza", "buffalo pizza"]},
                {"name": "BBQ Chicken Pizza", "price": 17.50, "keywords": ["bbq chicken pizza", "bbq pizza", "bbq chicken"]},
                {"name": "Hawaiian Pizza", "price": 17.50, "keywords": ["hawaiian pizza", "hawaiian"]},
                {"name": "Chicken Broccoli Alfredo Pizza", "price": 17.50, "keywords": ["chicken broccoli alfredo", "broccoli alfredo pizza"]},
                {"name": "Abruzzi Pizza", "price": 24.50, "keywords": ["abruzzi pizza", "abruzzi"]},
                {"name": "Meat Lovers Pizza", "price": 24.50, "keywords": ["meat lovers pizza", "meat lover pizza", "meat lovers"]},
                {"name": "Veggie Pizza", "price": 24.50, "keywords": ["veggie pizza", "vegetable pizza", "veggie"]},
                {"name": "Mediterranean Pizza", "price": 24.50, "keywords": ["mediterranean pizza", "mediterranean"]},
                {"name": "Napoli Pizza", "price": 24.50, "keywords": ["napoli pizza", "napoli"]},
                {"name": "Moda Pizza", "price": 24.50, "keywords": ["moda pizza", "moda"]},
            ]
        },
        "calzones": {
            "label": "Calzones",
            "items": [
                {"name": "Cheese Calzone", "price": 17.50, "keywords": ["cheese calzone"]},
                {"name": "Buffalo Calzone", "price": 17.50, "keywords": ["buffalo calzone"]},
                {"name": "Steak Calzone", "price": 18.50, "keywords": ["steak calzone"]},
                {"name": "Chicken Calzone", "price": 18.50, "keywords": ["chicken calzone"]},
            ]
        },
        "pasta": {
            "label": "Pasta",
            "items": [
                {"name": "Ravioli", "price": 14.50, "keywords": ["ravioli"]},
                {"name": "Chicken Lazagna Alfredo", "price": 16.99, "keywords": ["chicken lazagna", "chicken lasagna", "lazagna"]},
                {"name": "Linguine", "price": 16.99, "keywords": ["linguine", "linguini"]},
                {"name": "Chicken Broccoli Dinner", "price": 16.99, "keywords": ["chicken broccoli dinner"]},
                {"name": "Brazilian Food", "price": 18.99, "keywords": ["brazilian food", "brazilian"]},
            ]
        },
        "subs": {
            "label": "Subs & Sandwiches",
            "items": [
                {"name": "Italian Sub", "price": 10.99, "keywords": ["italian sub"]},
                {"name": "Pilgrim Sub", "price": 10.99, "keywords": ["pilgrim sub", "pilgrim"]},
                {"name": "Chicken Parm Sub", "price": 10.99, "keywords": ["chicken parm sub", "chicken parm", "chicken parmesan"]},
                {"name": "Meatball Sub", "price": 10.99, "keywords": ["meatball sub", "meatball"]},
                {"name": "BLT", "price": 10.99, "keywords": ["blt", "bacon lettuce tomato"]},
                {"name": "Steak & Cheese", "price": 10.99, "keywords": ["steak and cheese", "steak cheese"]},
                {"name": "Tuna Melt", "price": 10.99, "keywords": ["tuna melt", "tuna"]},
                {"name": "BBQ Chicken Sub", "price": 10.99, "keywords": ["bbq chicken sub"]},
                {"name": "Cheeseburger", "price": 10.99, "keywords": ["cheeseburger", "burger"]},
                {"name": "Hot Pastry", "price": 10.99, "keywords": ["hot pastry", "pastry"]},
                {"name": "Caprese Sub", "price": 13.50, "keywords": ["caprese sub", "caprese"]},
            ]
        },
        "wraps": {
            "label": "Wraps & Rolls",
            "items": [
                {"name": "Chicken Fajita Wrap", "price": 10.99, "keywords": ["fajita wrap", "chicken fajita", "fajita"]},
                {"name": "Caesar Roll Up", "price": 13.00, "keywords": ["caesar roll up", "caesar roll"]},
                {"name": "Burrito", "price": 13.50, "keywords": ["burrito"]},
                {"name": "Burrito Bowl", "price": 13.50, "keywords": ["burrito bowl"]},
            ]
        },
        "salads": {
            "label": "Salads",
            "items": [
                {"name": "Garden Salad (small)", "price": 3.00, "keywords": ["small garden salad", "garden salad small"]},
                {"name": "Garden Salad (large)", "price": 10.50, "keywords": ["large garden salad", "garden salad"]},
                {"name": "Greek Salad (small)", "price": 3.50, "keywords": ["small greek salad", "greek salad small"]},
                {"name": "Greek Salad (large)", "price": 9.99, "keywords": ["large greek salad", "greek salad"]},
                {"name": "Caesar Salad", "price": 11.25, "keywords": ["caesar salad"]},
                {"name": "Antipasto Salad", "price": 3.99, "keywords": ["antipasto salad", "antipasto"]},
                {"name": "Steak Tips Salad", "price": 11.25, "keywords": ["steak tips salad", "steak salad"]},
            ]
        },
        "appetizers": {
            "label": "Appetizers",
            "items": [
                {"name": "Garlic Bread (small)", "price": 4.50, "keywords": ["small garlic bread", "garlic bread small"]},
                {"name": "Garlic Bread (large)", "price": 6.50, "keywords": ["large garlic bread", "garlic bread"]},
                {"name": "French Fries (small)", "price": 4.50, "keywords": ["small fries", "small french fries", "small potato fries"]},
                {"name": "French Fries (large)", "price": 6.99, "keywords": ["large fries", "large french fries", "french fries", "fries"]},
                {"name": "Wings (small)", "price": 14.99, "keywords": ["small wings", "wings small"]},
                {"name": "Wings (large)", "price": 16.99, "keywords": ["large wings", "wings"]},
                {"name": "Mozzarella Sticks (small)", "price": 7.25, "keywords": ["small mozzarella sticks", "mozzarella sticks small"]},
                {"name": "Mozzarella Sticks (large)", "price": 12.25, "keywords": ["large mozzarella sticks", "mozzarella sticks", "mozz sticks"]},
                {"name": "Jalapeno Poppers", "price": 10.25, "keywords": ["jalapeno poppers", "jalapeno"]},
                {"name": "Chicken Tenders", "price": 16.99, "keywords": ["chicken tenders", "tenders"]},
                {"name": "Empanada", "price": 4.99, "keywords": ["empanada"]},
                {"name": "Mini Calzone", "price": 4.99, "keywords": ["mini calzone"]},
            ]
        },
        "desserts": {
            "label": "Desserts",
            "items": [
                {"name": "Cheesecake", "price": 4.80, "keywords": ["cheesecake"]},
                {"name": "Chocolate Cake", "price": 4.00, "keywords": ["chocolate cake"]},
                {"name": "Tiramisu", "price": 4.00, "keywords": ["tiramisu"]},
                {"name": "Oreo Cake", "price": 4.00, "keywords": ["oreo cake", "oreo"]},
                {"name": "Sweet Italian Casserole", "price": 4.90, "keywords": ["sweet italian casserole", "italian casserole"]},
            ]
        },
    }