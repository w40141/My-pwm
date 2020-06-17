import hashlib
import hmac
import json
import os
import random
import string

import fire
from typing import Tuple, Dict, Any

ROOT_PATH = os.environ["HOME"] + "/password"
CONFIG_FILE = ROOT_PATH + "/password_config.json"


class PwManager:
    def __init__(self,):
        if not os.path.exists(ROOT_PATH):
            os.makedirs(ROOT_PATH)
        self.password_path, self.start = self._make_password_path()
        self.password_file = self.password_path + "/password.json"
        self.password_dict = self._load_password()

    def _make_password_path(self) -> Tuple[str, int]:
        if os.path.isfile(CONFIG_FILE):
            password_path, num = self._load_config()
        else:
            password_path, num = self.register()
        return password_path, num

    def _load_config(self) -> Tuple[str, int]:
        with open(CONFIG_FILE, "r") as f:
            config = json.load(f)
        return config["path"], config["number"]

    def register(self) -> Tuple[str, int]:
        print("Input Password file's path. Default[" + ROOT_PATH + "] ")
        path = input()

        print("Input number. Default 0. ")
        num = int(input().strip())

        config = {"path": path, "number": num}
        with open(CONFIG_FILE, "w") as f:
            json.dump(config, f)
        return path, num

    def _load_password(self) -> Dict[str, Dict[str, Any]]:
        if os.path.isfile(self.password_file):
            with open(self.password_file) as f:
                password_dict = json.load(f)
            return password_dict
        else:
            return {}

    def _gen(self, domain: str, user_id: str, size: int = 12, symbol_flag: bool = False) -> str:
        signature = hmac.new(domain.encode(), user_id.encode(), hashlib.sha256).hexdigest()
        random.seed(signature)
        if symbol_flag:
            start = 33
            end = 127
            chars = "".join([chr(i) for i in range(start, end)])
        else:
            chars = string.ascii_uppercase + string.ascii_lowercase + string.digits
        return "".join(random.choices(chars, k=size))

    def _generate(self, domain: str) -> str:
        if domain in self.password_dict:
            return self._search(domain)
        else:
            user_id = input("Input user ID: ").strip()
            size = int(input("Input the length of a password: ").strip())
            tmp_flag = input("Is symbols valid? (Default is false.): ").strip()
            symbol_flag = True if tmp_flag else False
            password = self._gen(domain, user_id, size, symbol_flag)
            self.password_dict[domain] = {
                "user_id": user_id,
                "size": size,
                "symbol_flag": symbol_flag,
                "password": password,
            }
            self.save()
            return password

    def generate(self) -> None:
        domain = input("Input salt: ").strip()
        print(self._generate(domain))

    def _search(self, name: str) -> str:
        return self.password_dict[name]

    def show(self) -> None:
        name = input("Input name: ")
        print(self._search(name))

    def show_all(self) -> None:
        json.dumps(self.password_dict, indent=4)

    def _delete(self, name: str) -> None:
        del self.password_dict[name]

    def delete(self) -> None:
        name = input("Input name: ")
        self._delete(name)

    def change(self) -> None:
        name = input("Input name: ")
        self._delete(name)
        print(self._generate(name))

    def save(self) -> None:
        with open(self.password_file, 'w') as f:
            json.dump(self.password_dict, f)


def main() -> None:
    fire.Fire(PwManager)
