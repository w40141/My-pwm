import datetime
import hashlib
import hmac
import json
import os
import random
import string
from typing import Any, Dict

import fire
import pyperclip
import qrcode

ROOT_PATH = os.environ["HOME"] + "/password"
CONFIG_FILE = ROOT_PATH + "/password_config.json"


class MyPwm:
    def __init__(self,):
        if not os.path.exists(ROOT_PATH):
            os.makedirs(ROOT_PATH)

        config = self._make_password_path()
        self.password_path = config["path"]
        self.seed = config["seed"]
        self.params_file = config["params_file"]
        self.seed_params_dict = self._load_params()
        self.params_dict = self.seed_params_dict[self.seed]

    def _make_password_path(self) -> Dict[str, str]:
        if os.path.isfile(CONFIG_FILE):
            with open(CONFIG_FILE, "r") as f:
                return json.load(f)
        else:
            return self._register()

    def _register(self) -> Dict[str, str]:
        path = input("Input Password file's path. Default[" + ROOT_PATH + "] ")
        if not os.path.isdir(path):
            path = ROOT_PATH

        seed = input("Input seed: ")

        today = datetime.datetime.today()
        params_file = ROOT_PATH + "/%s.json" % today.strftime("%Y_%m_%d_%H_%M")

        config = {"path": path, "seed": seed, "params_file": params_file}
        with open(CONFIG_FILE, "w") as f:
            json.dump(config, f)
        return config

    def register(self) -> None:
        print("Now: Path is %s and seed is %s." % (self.password_path, self.seed))
        self._register()

    def _load_params(self) -> Dict[str, Any]:
        if os.path.isfile(self.params_file):
            with open(self.params_file, "r") as f:
                return json.load(f)
        else:
            return {self.seed: {}}

    # def _gen(self, domain: str) -> str:
    def _generate(self, domain: str) -> str:
        flag = "n"
        while flag != "y":
            user_id = input("Input user ID: ")
            try:
                size = int(input("Input the length of a password. Default is 16: "))
            except ValueError:
                size = 16
            passphrase = input("Input passphrase. Default is "": ")
            symbol_flag = True if input("Is symbols valid? (Default is false.): ") else False
            print("user id: " + user_id)
            print("size: " + str(size))
            print("passphrase: " + passphrase)
            print("symbol_flag: " + str(symbol_flag))
            flag = input("Generate (y or n): ")
        self.params_dict[domain] = {
            "user_id": user_id,
            "size": size,
            "passphrase": passphrase,
            "symbol_flag": symbol_flag,
        }
        return self._gen_password(domain)

    def _gen_password(self, domain: str):
        user_id = self.params_dict[domain]["user_id"]
        size = self.params_dict[domain]["size"]
        if "passphrase" in self.params_dict[domain]:
            passphrase = self.params_dict[domain]["passphrase"]
        else:
            passphrase = ""
        symbol_flag = self.params_dict[domain]["symbol_flag"]
        signature = hmac.new(domain.encode(), user_id.encode(), hashlib.sha256).hexdigest()
        random.seed(signature + self.seed + passphrase)
        if symbol_flag:
            chars = "".join([chr(i) for i in range(33, 127)])
        else:
            chars = string.ascii_uppercase + string.ascii_lowercase + string.digits
        return "".join(random.choices(chars, k=size))

    def _input_domain(self) -> str:
        flag = "n"
        while flag != "y":
            domain = input("Input domain: ")
            flag = input("domain: " + domain + "? y or n: ")
        return domain

    def generate(self, mode: str = "normal") -> None:
        domain = self._input_domain()
        if domain in self.params_dict:
            password = self._gen_password(domain)
        else:
            password = self._generate(domain)
        self._print(password, mode)

    def _print(self, password: str, mode: str) -> None:
        mode_dict = {
            "normal": self._print_normal,
            "qr": self._print_qr,
        }
        print(password)
        mode_dict[mode](password)

    def _print_normal(self, password: str) -> None:
        pyperclip.copy(password)

    def _print_qr(self, password: str) -> None:
        qr = qrcode.QRCode()
        qr.add_data(password)
        qr.print_ascii()

    def show(self, mode: str = "normal") -> None:
        domain = self._input_domain()
        if domain in self.params_dict:
            password = self._gen_password(domain)
        else:
            print("Do you want to make new domain's password?")
            if "y" == input("(y or n): "):
                password = self._generate(domain)
            else:
                password = ""
        self._print(password, mode)

    def show_all(self) -> None:
        for domain, params in self.params_dict.items():
            print(domain + ": ")
            for k, v in params.items():
                print("\t" + k + ": " + str(v))

    def _delete(self, domain: str) -> None:
        del self.params_dict[domain]

    def delete(self) -> None:
        domain = self._input_domain()
        self._delete(domain)
        # self._save()

    def delete_all(self):
        flag = "n"
        while flag != "y":
            flag = input("Do you want to delete all domain?: y or n: ")
        self.seed_params_dict = {self.seed: {}}

    def change(self, mode="normal") -> None:
        domain = self._input_domain()
        self._delete(domain)
        password = self._generate(domain)
        self._print(password, mode)

    def _save(self) -> None:
        with open(self.params_file, "w") as f:
            json.dump(self.seed_params_dict, f, indent=4)


def main() -> None:
    mypwm = MyPwm()
    fire.Fire(mypwm)
    mypwm._save()
