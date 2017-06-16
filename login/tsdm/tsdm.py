import time
import json
import re
import requests
import execjs
import rsa
import base64
import pytesseract
from PIL import Image
import re

headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_4) AppleWebKit/537.36 '
                         '(KHTML, like Gecko) Chrome/57.0.2987.133 Safari/537.36',
           }

# 全局的session
session = requests.session()
session.get('http://www.tsdm.me', headers=headers)


class TSDM:

    def getCaptcahImage(self, saveImageFilePath=''):
        headersForCaptcha = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_4) AppleWebKit/537.36 '
                                           '(KHTML, like Gecko) Chrome/57.0.2987.133 Safari/537.36',
                             'Host': 'www.tsdm.me',
                             'Accept': 'image/webp,image/*,*/*;q=0.8',
                             'Referer': 'http://www.tsdm.me/member.php?mod=logging&action=login',
                             'Accept-Encoding': 'gzip, deflate, sdch',
                             'Accept-Language': 'zh-CN,zh;q=0.8'
                             }
        resp = session.get(url='http://www.tsdm.me/plugin.php?id=oracle:verify', headers=headersForCaptcha)
        if resp.status_code == 200:
            with open(saveImageFilePath, 'wb') as file:
                file.write(resp.content)
                file.flush()
                file.close()
        else:
            return False
        return True

    def getLoginHomePage(self):
        headersForHomePage = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_4) AppleWebKit/537.36 '
                                           '(KHTML, like Gecko) Chrome/57.0.2987.133 Safari/537.36',
                             'Host': 'www.tsdm.me',
                             'Upgrade-Insecure-Requests': '1',
                             'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                             'Accept-Encoding': 'gzip, deflate, sdch',
                             'Accept-Language': 'zh-CN,zh;q=0.8'
                             }
        resp = session.get(url='http://www.tsdm.me/member.php?mod=logging&action=login', headers=headersForHomePage)
        if resp.status_code == 200:
            return resp.content.decode(resp.encoding)
        return ''

    def __getHashCodeFromPage(self):
        result = {'loginhash': '', 'formhash': ''}
        html = self.getLoginHomePage()
        if len(html) == 0:
            return result



    def login(self):
        pass


if __name__ == '__main__':
    tsdm = TSDM()
    tsdm.getCaptcahImage(r'D:\Workspace\python\project\smart_sign\login\tsdm\captcha\captcha.jpg')
    print(tsdm.getLoginHomePage())
