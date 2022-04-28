#!/usr/bin/env python3

import time
import sys
import requests
import ddddocr

ocr = ddddocr.DdddOcr(old=True, show_ad=False)


def current_timestamp13():
    return int(round(time.time() * 1000))


def szpd_get_image_code(session: requests.Session, path: str):
    now_ts = current_timestamp13()
    payload = {'a': str(now_ts)}
    r = session.get("https://msjw.ga.sz.gov.cn/crj/crjmsjw/wsyy/getImgCode", params=payload)
    with open(path, "wb") as f:
        f.write(r.content)
    return r.content


def ocr_code(path: str):
    with open(path, 'rb') as f:
        image = f.read()
    return ocr.classification(image)


def ocr_content(content):
    return ocr.classification(content)


def get_id_num():
    if len(sys.argv) >= 2:
        return sys.argv[1]
    try:
        with open("id.txt", 'r') as f:
            id_bum = f.read()
            return str(id_bum)
    except FileNotFoundError as _:
        print("[-] 参数指定 ID 或使用 ID 文件[id.txt]")
        exit(1)


def szpd_get_process(session: requests.Session, id_num, code):
    now_ts = current_timestamp13()
    payload = {'_': str(now_ts)}

    if len(id_num) == 18:
        data = f"sfzh={id_num}&rylb=R&inputCode={code}"
    else:
        data = f"ywbh={id_num}&inputCode={code}"
    headers = {
        "Accept": "application/json",
        "Content-Type": "application/x-www-form-urlencoded",

    }
    r = session.post("https://msjw.ga.sz.gov.cn/crj/wechat/wssb/ajax/bzjdcx2", params=payload, data=data,
                     headers=headers)
    return r.json()


def check():
    id_num = get_id_num()
    if len(id_num) < 13:
        print("[-] 13位业务号或者18位身份证号！")
        return None, None, None
    max_count = 5
    img_path = "code.jpeg"
    session = requests.session()
    for i in range(max_count):
        img = szpd_get_image_code(session, img_path)
        code = ocr_content(img)
        print("[+] code ocr result: ", code)
        r = szpd_get_process(session, id_num, code)

        if r["success"] == 0:
            msg = r["message"]
            print(f"[-] get process failed, msg: {msg}, retry[{i + 1}] ...")
            time.sleep(1)
        else:
            poc_type = r["data"][0]["zjzltext"]
            poc_jd = r["data"][0]["simpbzjd"]
            poc_full_jd = r["data"][0]["fullbzjd"]
            print(f"[+] 查询成功!!!, ID: {id_num}, 项目类型：{poc_type}, 状态: {poc_jd}【{poc_full_jd}】")
            return poc_type, poc_jd, poc_full_jd

    return None, None, None


if __name__ == '__main__':
    check()
