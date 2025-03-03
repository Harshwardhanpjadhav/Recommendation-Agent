import os
from dataclasses import dataclass
from dotenv import find_dotenv, load_dotenv

dotenv_path = find_dotenv()
load_dotenv(dotenv_path)


@dataclass
class EvironmentVariable:
    mongo_url = os.getenv('MONGODB_URL')
