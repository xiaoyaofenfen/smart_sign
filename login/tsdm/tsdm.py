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


class TSDM:
    session = requests.session()

    def __init__(self):
        headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_4) AppleWebKit/537.36 '
                                 '(KHTML, like Gecko) Chrome/57.0.2987.133 Safari/537.36',
                   }

        # 全局的session
        self.session.get('http://www.tsdm.me', headers=headers)

    def getCaptcahImage(self, saveImageFilePath=''):
        headersForCaptcha = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_4) AppleWebKit/537.36 '
                                           '(KHTML, like Gecko) Chrome/57.0.2987.133 Safari/537.36',
                             'Host': 'www.tsdm.me',
                             'Accept': 'image/webp,image/*,*/*;q=0.8',
                             'Referer': 'http://www.tsdm.me/member.php?mod=logging&action=login',
                             'Accept-Encoding': 'gzip, deflate, sdch',
                             'Accept-Language': 'zh-CN,zh;q=0.8'
                             }
        resp = self.session.get(url='http://www.tsdm.me/plugin.php?id=oracle:verify', headers=headersForCaptcha)
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
        resp = self.session.get(url='http://www.tsdm.me/member.php?mod=logging&action=login', headers=headersForHomePage)
        if resp.status_code == 200:
            return resp.content.decode(resp.encoding)
        return ''

    def getHashCodeFromPage(self):
        result = {'loginhash': '', 'formhash': ''}
        html = self.getLoginHomePage()
        if len(html) == 0:
            return result

        loginhashPattern = re.compile('<div id="main_messaqge_([0-9a-zA-Z]+)">')
        formhashPattern = re.compile('<input type="hidden" name="formhash" value="([0-9a-zA-Z]+)" />')
        lines = html.split('\n')
        for line in lines:
            if len(line) == 0:
                continue
            line = line.strip()
            if len(line) == 0:
                continue

            match = loginhashPattern.match(line)
            if match:
                result['loginhash'] = match.group(1)

            match = formhashPattern.match(line)
            if match:
                result['formhash'] = match.group(1)
        return result

    def login(self, userName, password, captcha, loginhash, formhash):
        headersForLogin= {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_4) AppleWebKit/537.36 '
                                            '(KHTML, like Gecko) Chrome/57.0.2987.133 Safari/537.36',
                              'Origin': 'http://www.tsdm.me',
                          'Referer': 'http://www.tsdm.me/member.php?mod=logging&action=login',
                              'Upgrade-Insecure-Requests': '1',
                              'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                              'Accept-Encoding': 'gzip, deflate, sdch',
                              'Accept-Language': 'zh-CN,zh;q=0.8',
                          'Content-Type': 'application/x-www-form-urlencoded'
                              }
        formData = {
            'formhash': formhash,
            'referer': 'http://www.tsdm.me/./',
            'loginfield': 'username',
            'username': userName,
            'password': password,
            'tsdm_verify': captcha,
            'questionid': 0,
            'answer': ''

        }
        resp = self.session.post(url='http://www.tsdm.me//member.php?mod=logging&action=login&loginsubmit=yes&loginhash={0}&inajax=1'.format(loginhash),
                           headers=headersForLogin,
                           data=formData)
        return resp.status_code == 200

if __name__ == '__main__':
    tsdm = TSDM()
    tsdm.getCaptcahImage(r'D:\Workspace\python\project\smart_sign\login\tsdm\captcha\captcha.jpg')
    print(tsdm.getLoginHomePage())
