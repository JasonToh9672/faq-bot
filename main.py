from faq_bot import FAQBot
from rich import print
from rich.console import Console

console = Console()

if __name__ == "__main__":
    bot = FAQBot("faq.txt", "Toh")
    bot.load_log("log.json")
    while True:
        question = console.input("[green]You:[/green] ").strip()
        if question.lower() == "quit":
            print("Goodbye!")
            break
        elif question == "":
            print("Please type a question.")
        else:
            print(f"[cyan]Bot[/cyan]: {bot.ask(question)}") #use .ask() because .find_answer only give answer but no save
    bot.history.show()
    print(f"Total messages: {bot.history.count()}")

    bot.save_log("log.json")