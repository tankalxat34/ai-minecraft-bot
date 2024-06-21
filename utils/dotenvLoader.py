import os
import pathlib
from dotenv import load_dotenv

def loadDotEnv():
    dotenv_path = os.path.join(pathlib.Path(os.path.dirname(__file__)).absolute().parent, '.env')
    if os.path.exists(dotenv_path):
        load_dotenv(dotenv_path)

if __name__ == "__main__":
    print(pathlib.Path(os.path.dirname(__file__)).absolute().parent)