import rsa
import random

config = {}


class RSAInt(object):
    """
        对数字加密
        mode: develop
        recvpath: /data/recvtemp/
        stopath: /data/hxsto/
        ndcpath: /data/ndc/
        shaslat: YpuDSaoGf40u22Rs
        rsakey:
            p: 3367900313
            q: 5463458053
            n: 1534346956685563
            e: 107899477698547
            d: 190792854759163

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


class RsaPublicPrivate(object):
    """通过rsa模块实现rsa加密"""
    @staticmethod
    def create_keys():
        """
        生成公钥和私钥
        :return:
        """
        (pubkey, privkey) = rsa.newkeys(1024)
        pub = pubkey.save_pkcs1()
        with open('public.pem', 'wb+')as f:
            f.write(pub)

        pri = privkey.save_pkcs1()
        with open('private.pem', 'wb+')as f:
            f.write(pri)

    @staticmethod
    def encrypt(original_text):
        """用公钥加密"""
        with open('public.pem', 'rb') as publickfile:
            p = publickfile.read()
        pubkey = rsa.PublicKey.load_pkcs1(p)
        crypt_text = rsa.encrypt(original_text, pubkey)

        return crypt_text

    @staticmethod
    def decrypt(crypt_text):
        """用私钥解密"""
        with open('private.pem', 'rb') as privatefile:
            p = privatefile.read()
        privkey = rsa.PrivateKey.load_pkcs1(p)

        lase_text = rsa.decrypt(crypt_text, privkey).decode()  # 注意，这里如果结果是bytes类型，就需要进行decode()转化为str

        return lase_text


class GenerateRSAKey(object):

    def __init__(self):
        self.keySize = 36   # 值也可设为18, 36  1024

    def is_prime(self, num):

        if num < 2:
            return False

        lowPrimes = [
            2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47, 53, 59, 61, 67, 71, 73, 79, 83, 89, 97, 101,
            103, 107, 109, 113, 127, 131, 137, 139, 149, 151, 157, 163, 167, 173, 179, 181, 191, 193, 197, 199,
            211, 223, 227, 229, 233, 239, 241, 251, 257, 263, 269, 271, 277, 281, 283, 293, 307, 311, 313, 317,
            331, 337, 347, 349, 353, 359, 367, 373, 379, 383, 389, 397, 401, 409, 419, 421, 431, 433, 439, 443,
            449, 457, 461, 463, 467, 479, 487, 491, 499, 503, 509, 521, 523, 541, 547, 557, 563, 569, 571, 577,
            587, 593, 599, 601, 607, 613, 617, 619, 631, 641, 643, 647, 653, 659, 661, 673, 677, 683, 691, 701,
            709, 719, 727, 733, 739, 743, 751, 757, 761, 769, 773, 787, 797, 809, 811, 821, 823, 827, 829, 839,
            853, 857, 859, 863, 877, 881, 883, 887, 907, 911, 919, 929, 937, 941, 947, 953, 967, 971, 977, 983,
            991, 997
        ]

        if num in lowPrimes:
            return True
        for prime in lowPrimes:
            if num % prime == 0:
                return False

        return self.rabin_miller(num)

    @staticmethod
    def rabin_miller(num):
        s = num - 1
        t = 0
        while s % 2 == 0:
            s //= 2
            t += 1
        for trials in range(5):
            a = random.randrange(2, num - 1)
            v = pow(a, s, num)
            if v != 1:
                i = 0
                while v != (num - 1):
                    if i == t - 1:
                        return False
                    else:
                        i += 1
                        v = (v ** 2) % num
        return True

    @staticmethod
    def gcd(a, b):
        """ Return the GCD of a and b using Euclid's Algorithm """
        while a != 0:
            a, b = b % a, a
        return b

    def find_inverse(self, a, m):
        if self.gcd(a, m) != 1:
            return None

        u1, u2, u3 = 1, 0, a
        v1, v2, v3 = 0, 1, m
        while v3 != 0:
            q = u3 // v3
            v1, v2, v3, u1, u2, u3 = (u1 - q * v1), (u2 - q * v2), (u3 - q * v3), v1, v2, v3

        return u1 % m

    def large_prime(self):
        while True:
            num = random.randrange(2 ** (self.keySize - 1), 2 ** self.keySize)

            if self.is_prime(num):
                return num

    def generate_n_e_d(self):
        """生成 n e d"""
        p = self.large_prime()
        q = self.large_prime()
        n = p * q

        while True:
            e = random.randrange(2 ** (self.keySize - 1), 2 ** self.keySize)
            if self.gcd(e, (p - 1) * (q - 1)) == 1:
                if self.gcd(e, (p - 1) * (q - 1)) == 1:
                    break

        d = self.find_inverse(e, (p - 1) * (q - 1))

        return p, q, n, e, d

    @classmethod
    def decrypt(cls, content):
        deres = RSAInt.decrypt_b36(content)

        return deres

    @classmethod
    def encrypt(cls, content=None):
        if not content:
            content = int("".join([str(random.randint(0, 10)) for _ in range(16)]))

        res = RSAInt.encrypt_b36(content)

        return res


if __name__ == "__main__":

    p, q, n, e, d = GenerateRSAKey().generate_n_e_d()

    config.update({
            'rsakey': {
                'n': n,
                'e': e,
                'd': d
            }
        })

    en_ret = GenerateRSAKey.encrypt(1111)
    print(en_ret)
    de_ret = GenerateRSAKey.decrypt(en_ret)
    print(de_ret)


    RSA_debug = False
    if RSA_debug:
        # 通过RSA模块处理
        original_content = 'have a good time'.encode('utf8')
        crypt_rsa_text = RsaPublicPrivate().encrypt(original_content)
        print(crypt_rsa_text)
        lase_rsa_text = RsaPublicPrivate().decrypt(crypt_rsa_text)
        print(lase_rsa_text)

