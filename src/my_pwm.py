import hashlib
import hmac
import os
import pickle
import pprint
import random
import string
from typing import Any, Dict

import fire
import pyperclip

ROOT_PATH = os.environ["HOME"] + "/password"
CONFIG_FILE = ROOT_PATH + "/password_config.pickle"


class MyPwm:
    def __init__(self,):
        if not os.path.exists(ROOT_PATH):
            os.makedirs(ROOT_PATH)

        config = self._make_password_path()
        self.password_path = config["path"]
        self.seed = config["seed"]
        self.password_file = self.password_path + "/password.pickle"
        self.password_dict = self._load_password()

    def _make_password_path(self) -> Dict[str, str]:
        if os.path.isfile(CONFIG_FILE):
            return self._load_config()
        else:
            return self._register()

    def _load_config(self) -> Dict[str, str]:
        with open(CONFIG_FILE, "rb") as f:
            return pickle.load(f)

    def _register(self) -> Dict[str, str]:
        path = input("Input Password file's path. Default[" + ROOT_PATH + "] ")
        if not os.path.isdir(path):
            path = ROOT_PATH

        seed = input("Input seed.")

        config = {"path": path, "seed": seed}
        with open(CONFIG_FILE, "wb") as f:
            pickle.dump(config, f)
        return config

    def _load_password(self) -> Dict[str, Any]:
        if os.path.isfile(self.password_file):
            with open(self.password_file, "rb") as f:
                return pickle.load(f)
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
        random.seed(signature + self.seed)
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
        self._save()
        return password

    def _generate(self, domain: str) -> str:
        if domain in self.password_dict:
            return self._search(domain)["password"]
        else:
            return self._gen(domain)

    def register(self) -> None:
        print("Now: Path is %s and seed is %d." % (self.password_path, self.seed))
        self._register()

    def _input_domain(self) -> str:
        flag = "n"
        while flag != "y":
            domain = input("Input domain: ")
            flag = input("domain: " + domain + "? y or n: ")
        return domain

    def generate(self) -> None:
        domain = self._input_domain()
        password = self._generate(domain)
        print(password)
        pyperclip.copy(password)

    def _search(self, domain: str) -> Dict[str, Any]:
        return self.password_dict[domain]

    def show(self) -> None:
        domain = self._input_domain()
        pprint.pprint(self._search(domain))

    def show_all(self) -> None:
        pprint.pprint(self.password_dict)

    def _delete(self, domain: str) -> None:
        del self.password_dict[domain]

    def delete(self) -> None:
        domain = self._input_domain()
        self._delete(domain)

    def change(self) -> None:
        domain = self._input_domain()
        self._delete(domain)
        print(self._generate(domain))

    def _save(self) -> None:
        with open(self.password_file, "wb") as f:
            pickle.dump(self.password_dict, f)


def main() -> None:
    fire.Fire(MyPwm)
