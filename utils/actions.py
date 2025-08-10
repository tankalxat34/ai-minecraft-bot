"""
Основные функции бота, которые надо прописать заранее.
"""
import datetime

def log(text: str):
    print("\t" * 2, f"[{str(datetime.datetime.now())}]", text)
