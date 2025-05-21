"""Handles buying, selling, and upgrading items with Redis tracking"""

import redis_helpers

def buy_item(item_name, price):
    """Purchases an item from the shop and updates Redis balance"""
    current_gold = read_session("player:gold") or 0
    if current_gold >= price:
        write_session("player:gold", current_gold - price)
        print(f"Bought {item_name} for {price} gold.")
    else:
        print(f"Not enough gold to buy {item_name}.")

def get_gold_balance():
    """Retrieves player's gold balance from Redis"""
    return read_session("player:gold")
