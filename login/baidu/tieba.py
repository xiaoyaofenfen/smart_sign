import time
import json
import re
import requests
import execjs
import rsa
import base64


class TIEBA:

    js_path = 'login.js'
    headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_4) AppleWebKit/537.36 '
                             '(KHTML, like Gecko) Chrome/57.0.2987.133 Safari/537.36',
               }

    def __init__(self):
        # 全局的session
        self.session = requests.session()
        self.session.get('https://tieba.baidu.com/index.html', headers=self.headers, verify=False)

    def setLoginJsPath(self, path):
        self.js_path = path

    def _get_runntime(self):
        """
        :param path: 加密js的路径,注意js中不要使用中文！估计是pyexecjs处理中文还有一些问题
        :return: 编译后的js环境，不清楚pyexecjs这个库的用法的请在github上查看相关文档
        """
        phantom = execjs.get()  # 这里必须为phantomjs设置环境变量，否则可以写phantomjs的具体路径
        with open(self.js_path, 'r') as f:
            source = f.read()
        return phantom.compile(source)

    def get_gid(self):
        return self._get_runntime().call('getGid')

    def get_callback(self):
        return self._get_runntime().call('getCallback')

    def _get_curtime(self):
        return int(time.time() * 1000)

    # 抓包也不是百分百可靠啊,这里?getapi一定要挨着https://passport.baidu.com/v2/api/写，才会到正确的路由
    def get_token(self, gid, callback):
        cur_time = self._get_curtime()
        get_data = {
            'tpl': 'netdisk',
            'subpro': 'netdisk_web',
            'apiver': 'v3',
            'tt': cur_time,
            'class': 'login',
            'gid': gid,
            'logintype': 'basicLogin',
            'callback': callback
        }
        self.headers.update(
            dict(Referer='https://tieba.baidu.com/index.html', Accept='*/*', Connection='keep-alive', Host='passport.baidu.com'))
        resp = self.session.get(url='https://passport.baidu.com/v2/api/?getapi', params=get_data, headers=self.headers, verify=False)
        if resp.status_code == 200 and callback in resp.text:
            # 如果json字符串中带有单引号，会解析出错，只有统一成双引号才可以正确的解析
            # data = eval(re.search(r'.*?\((.*)\)', resp.text).group(1))
            data = json.loads(re.search(r'.*?\((.*)\)', resp.text).group(1).replace("'", '"'))
            return data.get('data').get('token')
        else:
            print('获取token失败')
            return None

    def get_rsa_key(self, token, gid, callback):
        cur_time = self._get_curtime()
        get_data = {
            'token': token,
            'tpl': 'netdisk',
            'subpro': 'netdisk_web',
            'apiver': 'v3',
            'tt': cur_time,
            'gid': gid,
            'callback': callback,
        }
        resp = self.session.get(url='https://passport.baidu.com/v2/getpublickey', headers=self.headers, params=get_data, verify=False)
        if resp.status_code == 200 and callback in resp.text:
            data = json.loads(re.search(r'.*?\((.*)\)', resp.text).group(1).replace("'", '"'))
            return data.get('pubkey'), data.get('key')
        else:
            print('获取rsa key失败')
            return None

    def encript_password(self, password, pubkey):
        pub = rsa.PublicKey.load_pkcs1_openssl_pem(pubkey.encode('utf-8'))
        encript_passwd = rsa.encrypt(password.encode('utf-8'), pub)
        return base64.b64encode(encript_passwd).decode('utf-8')

    def login(self, token, gid, callback, rsakey, username, password):
        post_data = {
            'staticpage': 'https://tieba.baidu.com/tb/static-common/html/pass/v3Jump.html',
            'charset': 'utf-8',
            'token': token,
            'tpl': 'netdisk',
            'subpro': 'netdisk_web',
            'apiver': 'v3',
            'tt': self._get_curtime(),
            'codestring': '',
            'safeflg': 0,
            'u': 'https://tieba.baidu.com/index.html',
            'isPhone': '',
            'detect': 1,
            'gid': gid,
            'quick_user': 0,
            'logintype': 'basicLogin',
            'logLoginType': 'pc_loginDialog',
            'idc': '',
            'loginmerge': 'true',
            'splogin': 'rate',
            'username': username,
            'password': password,
            # 返回的key
            'rsakey': rsakey,
            'crypttype': 12,
            'ppui_logintime': 10280,
            'countrycode': '',
            'fp_uid': '7892ee6189604bcab199be5c7ac68165',
            'dv': 'MDExAAoA6QALAY0AEwAAAF00AAkCACKHhS0sqKioqKiOubntrOKl97b7pPur-Kj3z5DPvMmrxq_bDQIAH5GRj5iC1pfZnsyNwJ_AkMOTzPSr9Jn8kfOW5LTVptUNAgAFkZGPnJwNAgAFkZGWNjYHAgAEkZGRkQYCACiRkZG7u7u68fHx9XR0dGGhoaGn5-fn5GBgYGYmJiYlfX19eeLi4uA2EwIAJpGzs7Pbr9ur2OLN4pb_mviZt9W03bnM4oHug6zFq8-q0vyU4I3hBAIABpOTkZClnQUCAASRkZGaAQIABpGQkJkYthUCAAiRkZDMcZVN6BYCACOzx6ycsoO7i7KCsYKyi7-JuI6_jL6IuY20g7uIvIm4iLyFtxcCABaQkJOTguGV_JP93fWBqNOn1azXocCyEAIAAZENAgAFkZGEwcEJAgAmi4nLyp2dnZ2dg4iI3J3TlMaHypXKmsmZxv6h_pP2m_mc7r7frN8HAgAEkZGRkQcCAASRkZGRDQIAH5GRt_Xvu_q086HgrfKt_a7-oZnGmfSR_J77idm4y7g',
            'callback': 'parent.' + callback
        }
        resp = self.session.post(url='https://passport.baidu.com/v2/api/?login', data=post_data, headers=self.headers, verify=False)
        if 'err_no=0' in resp.text:
            print('登录成功')
        else:
            print('登录失败')

    def dailySign(self, formId):
        headersForFormSign = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_4) AppleWebKit/537.36 '
                                            '(KHTML, like Gecko) Chrome/57.0.2987.133 Safari/537.36',
                              'Host': 'tieba.baidu.com',
                              'Upgrade-Insecure-Requests': '1',
                              'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                              'Accept-Encoding': 'gzip, deflate, sdch, br',
                              'Accept-Language': 'zh-CN,zh;q=0.8',
                              'Referer': 'https://tieba.baidu.com/index.html',
                              'X-Requested-With': 'XMLHttpRequest'
                              }
        urlHost = 'https://tieba.baidu.com//f?ie=utf-8&kw={0}'.format(formId)
        resp = self.session.get(url=urlHost,
                                headers=headersForFormSign, verify=False)
        html = resp.text
        tbs = ''
        tbsPattern = re.compile('\'tbs\': "([0-9a-zA-Z]+)"')
        lines = html.split('\n')
        for line in lines:
            if len(line) == 0:
                continue
            line = line.strip()
            if len(line) == 0:
                continue

            match = tbsPattern.match(line)
            if match:
                tbs = match.group(1)
                break

        if len(tbs) == 0:
            return False

        headersForAdd = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_4) AppleWebKit/537.36 '
                                         '(KHTML, like Gecko) Chrome/57.0.2987.133 Safari/537.36',
                           'Host': 'tieba.baidu.com',
                         'Origin': 'https://tieba.baidu.com',
                           'Referer': urlHost,
                           'X-Requested-With': 'XMLHttpRequest',
                           'Accept': 'application/json, text/javascript, */*; q=0.01',
                           'Accept-Encoding': 'gzip, deflate, sdch',
                           'Accept-Language': 'zh-CN,zh;q=0.8',
                           'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8'
                           }
        formData = {
            'ie': 'utf-8',
            'kw': formId,
            'tbs': tbs
        }
        resp = self.session.post(
            url='https://tieba.baidu.com/sign/add',
            headers=headersForAdd,
            data=formData,
            verify=False)  # use verify=false is not a good option, need fix
        jdata = {}
        if resp.status_code == 200:
            responseXml = resp.content.decode(resp.encoding)
            jdata = json.loads(responseXml)
            print(jdata)
            if jdata['no'] == 0 or jdata['no'] == 1101:
                return True
        return False
