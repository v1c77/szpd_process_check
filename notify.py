#!/usr/bin/env python3

import time
import mac_say
from check import check


def notify():
    while True:
        poc_type, poc_jd, poc_full_jd = check()
        if poc_jd is None or poc_jd == "制证":
            print("[-] retry later...")
            time.sleep(60 * 10)
        else:
            break

    while True:
        tts_notify("好了好了好了好了好了!")
        time.sleep(3)


def tts_notify(word):
    mac_say.say(["-v", "Ting-Ting", word])


if __name__ == '__main__':
    notify()
