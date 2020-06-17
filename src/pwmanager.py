import hashlib
import hmac
import os
import pickle
import random
import string
from typing import Any, Dict, Tuple

import fire

ROOT_PATH = os.environ["HOME"] + "/password"
CONFIG_FILE = ROOT_PATH + "/password_config.pickle"


class PwManager:
    def __init__(self,):
        if not os.path.exists(ROOT_PATH):
            os.makedirs(ROOT_PATH)
        self.password_path, self.start = self._make_password_path()
        self.password_file = self.password_path + "/password.pickle"
        self.password_dict = self._load_password()

    def _make_password_path(self) -> Tuple[str, int]:
        if os.path.isfile(CONFIG_FILE):
            password_path, num = self._load_config()
        else:
            password_path, num = self._register()
        return password_path, num

    def _load_config(self) -> Tuple[str, int]:
        with open(CONFIG_FILE, "rb") as f:
            config = pickle.load(f)
        return config["path"], config["number"]

    def _register(self):
        path = input("Input Password file's path. Default[" + ROOT_PATH + "] ")
        if not os.path.isdir(path):
            path = ROOT_PATH

        try:
            num = int(input("Input number. Default 0. "))
        except ValueError:
            num = 0

        config = {"path": path, "number": num}
        with open(CONFIG_FILE, "wb") as f:
            pickle.dump(config, f)
        return path, num

    def _load_password(self) -> Dict[str, Dict[str, Any]]:
        if os.path.isfile(self.password_file):
            with open(self.password_file, "rb") as f:
                password_dict = pickle.load(f)
            return password_dict
        else:
            return {}

    def _gen(self, domain: str) -> str:
        flag = "n"
        while flag != "y":
            user_id = input("Input user ID: ")
            try:
                size = int(input("Input the length of a password. Default is 16: "))
            except ValueError:
                size = 16
            symbol_flag = True if input("Is symbols valid? (Default is false.): ") else False
            print("user id: " + user_id)
            print("size: " + str(size))
            print("symbol_flag: " + str(symbol_flag))
            flag = input("Generate (y or n): ")
        signature = hmac.new(domain.encode(), user_id.encode(), hashlib.sha256).hexdigest()
        random.seed(signature)
        if symbol_flag:
            chars = "".join([chr(i) for i in range(33, 127)])
        else:
            chars = string.ascii_uppercase + string.ascii_lowercase + string.digits
        password = "".join(random.choices(chars, k=size))
        self.password_dict[domain] = {
            "user_id": user_id,
            "size": size,
            "symbol_flag": symbol_flag,
            "password": password,
        }
        self.save()
        return password

    def _generate(self, domain: str) -> str:
        if domain in self.password_dict:
            return self._search(domain)
        else:
            return self._gen(domain)

    def register(self) -> None:
        self._register()

    def _input_domain(self):
        flag = "n"
        while flag != "y":
            domain = input("Input domain: ")
            flag = input("domain: " + domain + "? y or n: ")
        return domain

    def generate(self) -> None:
        domain = self._input_domain()
        print(self._generate(domain))

    def _search(self, domain: str) -> str:
        return self.password_dict[domain]

    def show(self) -> None:
        domain = self._input_domain()
        print(self._search(domain))

    def show_all(self) -> None:
        for k, v in self.password_dict.items():
            print(k, v)

    def _delete(self, domain: str) -> None:
        del self.password_dict[domain]

    def delete(self) -> None:
        domain = self._input_domain()
        self._delete(domain)

    def change(self) -> None:
        domain = self._input_domain()
        self._delete(domain)
        print(self._generate(domain))

    def save(self) -> None:
        with open(self.password_file, "wb") as f:
            pickle.dump(self.password_dict, f)


def main() -> None:
    fire.Fire(PwManager)
