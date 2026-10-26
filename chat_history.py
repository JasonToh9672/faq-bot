from datetime import datetime

class ChatHistory:
    def __init__(self, user_name):
        self.user_name = user_name
        self.messages = []

    def add(self, role, content):
        role_list = ["user", "assistant", "system"]
        if role not in role_list:
            raise ValueError ("The role must be either 'user', 'assistant' or 'system'")
        self.messages.append({"time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),"role": role, "content": content})

    def count(self):
        return len(self.messages)

    def show(self):
        for msg in self.messages:
            print(f"{msg['time']} {msg['role']}:{msg['content']}")