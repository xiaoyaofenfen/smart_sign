import time
import json
import re
import requests
import execjs
import rsa
import base64
import re
import platform
import os
import json


class DUOWAN:
    session = requests.session()

    def __init__(self):
        headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_4) AppleWebKit/537.36 '
                                 '(KHTML, like Gecko) Chrome/57.0.2987.133 Safari/537.36',
                   }

        # 全局的session
        self.session.get('http://bbs.duowan.com/index.html', headers=headers)

        self.duowanJs = ''

    def setDuowanJs(self, path):
        self.duowanJs = path

    def getOAuthToken(self):
        headersForToken = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_4) AppleWebKit/537.36 '
                                         '(KHTML, like Gecko) Chrome/57.0.2987.133 Safari/537.36',
                           'Host': 'bbs.duowan.com',
                           'Origin': 'http://bbs.duowan.com',
                           'Referer': 'http://bbs.duowan.com/index.html',
                           'X-Requested-With': 'XMLHttpRequest',
                           'Accept': 'application/json, text/javascript, */*; q=0.01',
                           'Accept-Encoding': 'gzip, deflate, sdch',
                           'Accept-Language': 'zh-CN,zh;q=0.8',
                           'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8'
                           }
        formData = {
            'callbackURL': 'http://bbs.duowan.com/login.php?mod=callback',
            'denyCallbackURL': 'http://bbs.duowan.com/login.php?mod=denycallback'
        }
        resp = self.session.post(
            url='http://bbs.duowan.com/login.php?mod=getauthorizedurl',
            headers=headersForToken,
            data=formData)
        if resp.status_code == 200:
            responseXml = resp.content.decode(resp.encoding)
            jdata = json.loads(responseXml)
            pattern = re.compile('.*oauth_token=([0-9a-zA-Z]+)')
            match = pattern.match(jdata['url'])
            if match:
                return match.group(1)
        return ''

    def login(self, userName, password, oauthToken):
        referer = 'https://lgn.yy.com/lgn/oauth/authorize.do?oauth_token={0}&denyCallbackURL=http%3A%2F%2Fbbs.duowan.com%2Flogin.php%3Fmod%3Ddenycallback&cssid=5031&UIStyle=xqlogin&rdm={1}'.format(oauthToken, self.getRdm())
        headersForLogin = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_4) AppleWebKit/537.36 '
                                         '(KHTML, like Gecko) Chrome/57.0.2987.133 Safari/537.36',
                           'Host': 'lgn.yy.com',
                           'Origin': 'https://lgn.yy.com',
                           'Referer': referer,
                           'X-Requested-With': 'XMLHttpRequest',
                           'Accept': '*/*',
                           'Accept-Encoding': 'gzip, deflate, sdch',
                           'Accept-Language': 'zh-CN,zh;q=0.8',
                           'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8'
                           }
        formData = {
            'username': userName,
            'pwdencrypt': self.__getEncyptPassword(password),
            'oauth_token': oauthToken,
            'denyCallbackURL': 'http://bbs.duowan.com/login.php?mod=denycallback',
            'UIStyle': 'xqlogin',
            'appid': 5031,
            'cssid': 5031,
            'mxc': '',
            'vk': '',
            'isRemMe': 0,
            'mmc': '',
            'vv': '',
            'hiido': 1
        }
        resp = self.session.post(
            url='https://lgn.yy.com/lgn/oauth/x2/s/login_asyn.do',
            headers=headersForLogin,
            data=formData,
            verify=False)  # use verify=false is not a good option, need fix
        if resp.status_code == 200:
            responseXml = resp.content.decode(resp.encoding)
            jdata = json.loads(responseXml)
            print(jdata)
            return jdata['code'] == '0'
        return False

    def _get_runntime(self):
        """
        :param path: 加密js的路径,注意js中不要使用中文！估计是pyexecjs处理中文还有一些问题
        :return: 编译后的js环境，不清楚pyexecjs这个库的用法的请在github上查看相关文档
        """
        phantom = execjs.get()  # 这里必须为phantomjs设置环境变量，否则可以写phantomjs的具体路径
        with open(self.duowanJs, 'r') as f:
            source = f.read()
        return phantom.compile(source)

    def getRdm(self):
        return self._get_runntime().call('getRDM')

    def __getEncyptPassword(self, password):
        return password


