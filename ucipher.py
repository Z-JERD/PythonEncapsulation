
import os
import re
import json
import datetime
from hashlib import sha1, md5

import scrypt
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from itsdangerous import SignatureExpired, BadSignature, BadData


config = {
        'rsakey': {
            "p": 3367900313,
            "q": 5463458053,
            "n": 1534346956685563,
            "e": 107899477698547,
            "d": 190792854759163,
        },
        "md5_salt": '!@#$%*^',
        "jwt_secret_key": "JWTSignature@Token",
        "jwt_salt": "$6$/F4U5TjpwXotMbuX"
    }


class AccountChecker(object):
    """校验名称"""
    _account_checker_re = re.compile(r"^[\u4e00-\u9fa5\u3040-\u309f\u30a0-\u30ffA-Za-z_0-9()（）【】《》-]+$")

    @classmethod
    def account_name_check(cls, name):

        assert cls._account_checker_re.match(name) != None, '用户名称不符合要求,请使用中文字母数字等常见字符'

        assert not name.startswith('('), '用户名称不符合要求,不能以括号开头'
        assert not name.startswith(')'), '用户名称不符合要求,不能以括号开头'

        assert not name.startswith('（'), '用户名称不符合要求,不能以括号开头'
        assert not name.startswith('）'), '用户名称不符合要求,不能以括号开头'

        assert not name.startswith('【'), '用户名称不符合要求,不能以括号开头'
        assert not name.startswith('】'), '用户名称不符合要求,不能以括号开头'

        assert not name.startswith('《'), '用户名称不符合要求,不能以括号开头'
        assert not name.startswith('》'), '用户名称不符合要求,不能以括号开头'

        assert not name.startswith('-'), '用户名称不符合要求,不能以符号开头'
        assert not name.endswith('-'), '用户名称不符合要求,不能以符号结尾'

        assert not name.startswith('—'), '用户名称不符合要求,不能以符号开头'
        assert not name.endswith('—'), '用户名称不符合要求,不能以符号结尾'

        assert not name.startswith('_'), '用户名称不符合要求,不能以符号开头'
        assert not name.endswith('_'), '用户名称不符合要求,不能以符号结尾'

        return


class PasswordChecker(object):
    """
        密码检测
    """

    def check(self, password):
        self.check_length(password)
        self.check_number(password)
        self.check_letter(password)
        self.check_weak(password)

        return

    @staticmethod
    def check_length(pswd):
        assert len(pswd) >= 6, '密码长度不能小于6'

    @staticmethod
    def check_number(pswd):
        assert not pswd.isdigit(), '密码不能是纯数字'

    @staticmethod
    def check_letter(pswd):
        assert (sum([1 for _l in pswd if _l.isalpha()]) >= 1), '密码必须包含字母'

    def check_weak(self, pswd):
        """检测密码是否常见, 可把常见密码放到数据库中,取值对比"""
        pass


class ScryptHash(object):
    """加密解密处理
       参考文档： https://pypi.org/project/scrypt/
        1. scrypt               加密和解密 可逆 可用于账户密码,也可用作token
        2. MD5                  用于账户密码  不可逆
    """

    @staticmethod
    def encrypt(password, salt=None):
        salt = salt if salt else os.urandom(32).hex()
        pwd = scrypt.encrypt(password, salt, maxtime=0.5).hex()
        return pwd, salt

    @staticmethod
    def decrypt(encrypted_password, salt):
        return scrypt.decrypt(bytes.fromhex(encrypted_password), salt)

    @staticmethod
    def simhash(password):
        r1 = sha1(password.encode()).hexdigest()[-10:].encode()
        r2 = sha1(r1).hexdigest()[-2:]

        return r2

    @classmethod
    def v1_decrypt(cls, account, password):
        """md5生成摘要密码 salt不要放在代码中"""
        s = account + password + config["md5_salt"]
        return md5(s.encode()).hexdigest()


class RsaHash(object):
    """
        对数字进行进行加密处理(可逆), 如利用user_id 生成token
    """
    @staticmethod
    def encrypt(a):

        return pow(a, config['rsakey']['d'], config['rsakey']['n'])

    @staticmethod
    def decrypt(b):
        return pow(b, config['rsakey']['e'], config['rsakey']['n'])

    @classmethod
    def encrypt_b36(cls, a):
        return cls.encrypt(a)
        # return mpz(cls.encrypt(a)).digits(36) # 转成字符串

    @classmethod
    def decrypt_b36(cls, b):
        return cls.decrypt(b)
        # return cls.decrypt(int(b, 36)) # 转成十进制


class JwtHash(object):
    """
        JWT 生成Token
        参考文档：https://www.toutiao.com/a6693750591094522375/
                 https://www.jianshu.com/p/537b356d34c9

        更改token有效期:
            1.token自动延期
                签发两个token
                一个为access token，用于用户后续的各个请求中携带的认证信息
                另一个是refresh token，为access token过期后，用于申请一个新的access token
            2. 用户退出：
                直接抛弃access token与refresh token
    """
    access_term_validity = 4 * 60 * 60              # 默认有效期1小时
    refresh_term_validity = 30 * 24 * 60 * 60
    palyload_keys = {                               # palyload中的数据
        "user_id", "user_name", "create_time", "expire_time"
    }

    @staticmethod
    def generate_token(create_time, term_validity, palyload_data):
        expire_time = create_time + datetime.timedelta(seconds=term_validity)
        palyload_data["create_time"] = create_time.strftime('%Y-%m-%d %X')
        palyload_data["expire_time"] = expire_time.strftime('%Y-%m-%d %X')

        s = Serializer(
            secret_key=config["jwt_secret_key"],
            salt=config["jwt_salt"],
            expires_in=term_validity
        )

        return s.dumps(palyload_data).decode('utf-8')

    @classmethod
    def encrypt(cls, palyload, extension=False):
        """加密"""
        refresh_token = None
        create_time = datetime.datetime.now()
        palyload_data = {v: None for v in cls.palyload_keys}
        palyload_data.update(palyload)

        access_token = cls.generate_token(create_time, cls.access_term_validity, palyload_data)
        if not extension:
            refresh_token = cls.generate_token(create_time, cls.refresh_term_validity, palyload_data)

        return access_token, refresh_token

    @classmethod
    def decrypt(cls, jwttoken):
        """解密"""
        s = Serializer(
            secret_key=config["jwt_secret_key"],
            salt=config["jwt_salt"],
        )
        try:
            jwt_data = s.loads(jwttoken)
        except SignatureExpired as e:
            assert False, 'Token已过期'
        except BadSignature as e:
            encoded_payload = e.payload
            if encoded_payload is not None:
                try:
                    s.load_payload(encoded_payload)
                except BadData:
                    assert False, 'Token被篡改'
            assert False, 'Token有误'
        except Exception as e:
            assert False, '未知错误【解析Token】'
        assert not set(jwt_data.keys()) - set(cls.palyload_keys), 'Token不合法'

        return jwt_data

    @classmethod
    def token_extension(cls, refresh_token):
        """tocken延期"""
        jwt_playload = cls.decrypt(refresh_token)
        access_token, _ = cls.encrypt(jwt_playload, extension=True)

        return access_token



if __name__ == "__main__":
    pass