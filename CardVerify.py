import re


class CodeVerify(object):

    @staticmethod
    def phone_verify(phone_code, phone_type=0):
        """
        "校验手机号码
        :param phone_code:
        :param phone_type: 校验类型 0：手机号/固话  1: 校验手机号 2:校验固话
        :return:
        """
        error_msg = None
        phone_code = phone_code.strip()

        assert phone_code and isinstance(phone_code, str), "联系方式类型有误"
        assert phone_type in [0, 1, 2], "联系方式校验类型有误"

        if phone_type == 0:
            """
            校验联系方式,可以是手机号,也可以是座机号
            """
            error_msg = "联系方式有误,请核实"

            if re.match(r"^1[3-9][0-9]{9}$", phone_code):

                error_msg = None

            elif re.match(r"(^86|\+86|\(86\)|\（86\）|0086|\+0086|\(0086\)|\（0086\）)(\s[1]|[1])[0-9][0-9]{9}$",
                          phone_code):

                error_msg = None

            elif re.match("^0[0-9]{2}[-| ]?[0-9]{8}$", phone_code) or \
                    re.match("^0[0-9]{3}[-| ]?[0-9]{7}$", phone_code) or \
                    re.match("^0[0-9]{2}[-| ]?[0-9]{8}[-| ]{1,2}[0-9]{1,5}$", phone_code) or \
                    re.match("^0[0-9]{3}[-| ]?[0-9]{7}[-| ]{1,2}[0-9]{1,5}$", phone_code):

                error_msg = None

        elif phone_type == 1:

            if len(phone_code) < 11:
                error_msg = "手机号码位数不足11位"
            else:

                if len(phone_code) == 11:

                    if not re.match(r"^1[3-9][0-9]{9}$", phone_code):
                        error_msg = "手机号有误"

                else:

                    if not re.match(
                            r"(^86|\+86|\(86\)|\（86\）|0086|\+0086|\(0086\)|\（0086\）)(\s[1]|[1])[0-9][0-9]{9}$",
                            phone_code):
                        error_msg = "手机号有误,请检查86区号和11位手机号码"

        elif phone_type == 2:
            """
            区号3位 电话号码8位
            区号4位 电话号码7位
            分机号 1-5位
            """

            if re.match("^0[0-9]{2}[-| ]?[0-9]{8}$", phone_code) or \
                    re.match("^0[0-9]{3}[-| ]?[0-9]{7}$", phone_code) or \
                    re.match("^0[0-9]{2}[-| ]?[0-9]{8}[-| ]{1,2}[0-9]{1,5}$", phone_code) or \
                    re.match("^0[0-9]{3}[-| ]?[0-9]{7}[-| ]{1,2}[0-9]{1,5}$", phone_code):

                error_msg = None
            else:
                error_msg = "座机号有误"

        assert not error_msg, error_msg

        return phone_code

    @staticmethod
    def email_verify(email_code):
        """校验邮箱"""

        email_code = email_code.strip()

        error_msg = "电子邮箱格式不正确"

        if re.match(r"^\w+([-+.]\w+)*@\w+([-.]\w+)*\.\w+([-.]\w+)*$", email_code):

            error_msg = None

        assert not error_msg, error_msg

        return email_code

    @staticmethod
    def is_valid_card(id_card):
        """校验码核对"""

        if isinstance(id_card, int):
            id_card = str(id_card)

        items = [int(item) for item in id_card[:-1]]

        # 加权因子表
        factors = (7, 9, 10, 5, 8, 4, 2, 1, 6, 3, 7, 9, 10, 5, 8, 4, 2)

        # 计算17位数字各位数字与对应的加权因子的乘积
        copulas = sum([a * b for a, b in zip(factors, items)])

        # 校验码表
        ckcodes = ('1', '0', 'X', '9', '8', '7', '6', '5', '4', '3', '2')

        return ckcodes[copulas % 11].upper() == id_card[-1].upper()

    @staticmethod
    def id_card_verify(id_card, check_code=True):
        """
        :param id_card:
        :param check_code:是否校验校验码
        :return:
        """

        id_card = id_card.strip()

        error_msg = "身份证号不足18位"

        if id_card and isinstance(id_card, str) and len(id_card) == 18:
            if re.match(r'([1-9]\d{5}[12]\d{3}(0[1-9]|1[012])(0[1-9]|[12][0-9]|3[01])\d{3}[0-9xX])$', id_card):

                error_msg = None

                if check_code:

                    valid_res = CodeVerify.is_valid_card(id_card)

                    if not valid_res:
                        error_msg = "最后一位校验码与前17位数字不匹配,请核实"
            else:
                error_msg = "身份证值有误,请核实"

        assert not error_msg, error_msg

        return id_card

    @staticmethod
    def zh_verify(content, v_type=0):
        """
        校验是否含有中文
        :param content:
        :param v_type: 0: 含有中文 1: 全是中文
        :return:
        """
        error_msg = None

        content = content.strip()

        if content and v_type in [0, 1]:
            if v_type == 0:

                for _ in content:

                    if '\u4e00' <= _ <= '\u9fa5':

                        error_msg = "含有中文字符"

                        break
            else:
                for _ in content:

                    if not ('\u4e00' <= _ <= '\u9fa5'):

                        error_msg = "含有非中文字符"

                        break
        else:
            error_msg = "检测内容不能为空"

        assert not error_msg, error_msg

        return content


if __name__ == "__main__":
    pass





