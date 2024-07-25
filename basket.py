class Basket:
    def __init__(self):
        self.user_items = {}
    
    def add(self, user_id: int, menu_item_id: int) -> None:
        if user_id not in self.user_items:
            self.user_items[user_id] = {}
        
        if menu_item_id in self.user_items[user_id]:
            self.user_items[user_id][menu_item_id] = self.user_items[user_id][menu_item_id] + 1
        else:
            self.user_items[user_id][menu_item_id] = 1
    
    def get_user_items(self, user_id: int) -> dict:
        if user_id not in self.user_items:
            return {}
        
        return self.user_items[user_id]

    def clear(self, user_id: int) -> None:
        self.user_items[user_id] = {}


