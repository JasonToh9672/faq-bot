from chat_history import ChatHistory

class FAQBot:
    def __init__(self, faq_path, user_name):
        self.faq = self.load_faq(faq_path)
        self.history =  ChatHistory(user_name)

    def load_faq(self, path):
        file_dict = {}
        try:
            with open(path, "r", encoding="utf-8") as f:
                for line in f:
                    if line.strip() != "": #strip will remove whitespace and \n
                        pair = line.strip().split("|")
                        file_dict[pair[0]] = pair[1]
        except FileNotFoundError:
            print(f"The file on {path} does not exist.")
        return file_dict

    def find_answer(self, question):
        question = question.lower().strip()
        for key in self.faq: # Using "in" with Dictionaries only checks the keys, not the values.
            if key in question:
                return self.faq[key]
        return "Sorry, I don't know the answer to that."

    def ask(self, question):
        answer = self.find_answer(question)
        self.history.add("user", question)
        self.history.add("assistant",answer)
        return answer

    def save_log(self, path):
        with open(path, "w", encoding="utf-8") as f:
            for msg in self.history.messages:
                f.write(f"[{msg['time']}]:{msg['role']}:{msg['content']}\n") # must add \n else will all in one line