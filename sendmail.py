import smtplib
import os
import datetime
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication
from email.mime.image import MIMEImage
from email.header import Header

import pandas as pd

"""
发送邮件前的准备：
    个人邮箱 如qq邮箱 163邮箱：
        1. 去邮箱手动开启smtp服务
        2. 得到授权码(登录使用)
    企业邮箱：
        已默认开启smtp, 登录密码使用账号密码即可
        
参考文档： https://blog.csdn.net/u010652755/article/details/104321576
"""

SenderConfig = {
    "user": "13466776842@163.com",      # 发件人邮件地址
    "password": "VOOOCCWADIBJKHDW",     # 授权码
    "server": "smtp.163.com",           # SMTP服务器地址
    "port": 465                         # SMTP服务器端口
}


# 邮件接收人列表
ReceiverList = [
    '763464046@qq.com'
]


class MailSend(object):
    def __init__(self):
        self.status = 1

    @staticmethod
    def login_mailbox():
        """登录邮箱"""
        try:
            mail_sp = smtplib.SMTP_SSL(SenderConfig["server"], SenderConfig["port"])
            mail_sp.login(SenderConfig["user"], SenderConfig["password"])
        except Exception as e:
            raise ValueError("登录邮箱失败")

        return mail_sp

    def send_mail(self, msg):

        mail_sp = self.login_mailbox()

        try:
            mail_sp.sendmail(SenderConfig["user"], ReceiverList, msg.as_string())
        except Exception as e:
            self.status = 0
            raise ValueError("邮件发送失败")
        finally:
            mail_sp.quit()

        return "邮件发送成功" if self.status == 1 else "邮件发送失败"

    def send_mail_appendix(self, subject: str, appendix_info: list, content: str = None):
        """
        发送带附件的邮件
        :param subject: 邮件标题
        :param appendix_info: 附件信息 [{"file_path": "xx", "file_name": "xxx"}]
        :param content: 邮件正文
        :return:
        """

        msg = MIMEMultipart()
        msg['Subject'] = Header(subject, 'utf-8')
        msg['From'] = SenderConfig["user"]

        # 构建正文
        if content:
            part_text = MIMEText(content)
            msg.attach(part_text)

        # 添加附件
        for v in appendix_info:
            file_path, file_name = v["file_path"], v.get("file_name")
            if not file_name:
                file_name = os.path.basename(file_path)
            # 打开附件
            part_attach = MIMEApplication(open(file_path, 'rb').read())
            # 为附件命名
            part_attach.add_header('Content-Disposition', 'attachment', filename=file_name)
            # 添加附件
            msg.attach(part_attach)

        result = self.send_mail(msg)

        return result

    def send_mail_image(self, subject: str, image_path: list, content: str = ""):
        """
        邮件内容为图片
        :param subject: 邮件标题
        :param image_path: 图片路径
        :param content: 邮件正文
        :return:
        """
        # related: 邮件内容的格式，采用内嵌的形式进行展示
        msg = MIMEMultipart()                       # 邮件体对象
        msg['Subject'] = Header(subject, 'utf-8')
        msg['From'] = SenderConfig["user"]

        image_src = ""
        image_path = [image_path] if isinstance(image_path, str) else image_path
        assert isinstance(image_path, list), '图片路径有误'

        for index, v in enumerate(image_path, 1):

            assert os.path.exists(v), '%s 文件不存在' % v

            src_id = "image_%s" % index
            image_src += '<p><img src="cid:%s" width="500" height="500"></p>' % src_id

            message_img = MIMEImage(open(v, 'rb').read())
            message_img.add_header('Content-ID', '%s' % src_id)

            msg.attach(message_img)

        html_file = """
                 <html><body><h1>%s</h1>%s</body></html> 
                """ % (content, image_src)
        msg.attach(MIMEText(html_file, 'html', 'utf8'))

        result = self.send_mail(msg)

        return result

    def send_mail_text(self, title, content, html_style=False):
        """
        发送邮件正文
        :param title: 邮件标题
        :param content: 邮件内容
        :param html_style： 文件内容是否为html
        :return:
        """

        msg = MIMEText(content, 'html', 'utf-8') if html_style else MIMEText(content)
        msg['Subject'] = Header(title, 'utf-8')
        msg['From'] = SenderConfig["user"]

        result = self.send_mail(msg)

        return result

    @classmethod
    def html_content(cls, content):
        """HTML内容"""

        html_head = """
        
           <!DOCTYPE html>
                <head>
                    <title>Leapin-resetpassword</title>
                    <style>
                            table {
                                border-collapse: collapse;
                            }		
                                    
                            th{
                                width: 100px;
                                height: 40px;	
                                border: 1px solid black;
                                font-size: 12px;
                                text-align: center;
                            }			
                
                    </style>
                </head>
                
                <body>
    
        """


        html_thead = """
            <table>
                    <tr>
                        <th>开始时间</th>
                        <th>结束时间</th>
                        <th>自购设备分账比 </th>
                        <th>中数设备分账比 </th>
                        <th>添加人</th>
                        <th>添加时间</th>
                    </tr>
        """

        tbody = ""

        for index, v in enumerate(content):
            start_time, end_time = v.get("start_time"), v.get("end_time")
            huaxia_own, huaxia_lease = v.get("huaxia_own"), v.get("huaxia_lease")
            user_name, save_time = v.get("user_name"), v.get("save_time")

            td = """
                       <tr>
                           <th>%s</th>
                           <th>%s</th>
                           <th>%s</th>
                           <th>%s</th>
                           <th>%s</th>
                           <th>%s</th>
                       </tr>
                             
                    """ % (start_time, end_time, huaxia_own, huaxia_lease, user_name, save_time)

            tbody += td

        res = html_head + '\n' + html_thead + tbody + "</table></body><!DOCTYPE html>"

        return res

    @classmethod
    def html_form_file(cls, title, file_path, excel_file = True):
        """读取excel/csv文件中内容,以正文形式显示"""

        if not os.path.exists(file_path):
            assert False, '文件不存在'

        pd.set_option('display.max_colwidth', -1)  # 设置表格数据完全显示（不出现省略号）
        flag = False
        for v in ["utf-8", "gbk", "gb18030"]:
            try:

                merge_data = pd.read_excel(file_path, keep_default_na=False,  encoding=v) if excel_file else \
                    pd.read_csv(file_path, keep_default_na=False, encoding=v)
                flag = True
                break
            except Exception as e:
                pass

        assert flag, '文件解析有误'

        # DataFrame数据转化为HTML表格形式
        content = merge_data.to_html(escape=False, index=False)

        html_head = """
        <head>
            <meta charset="utf-8">
            <STYLE TYPE="text/css" MEDIA=screen>

                table.dataframe {
                    border-collapse: collapse;
                    border: 2px solid #a19da2;
                    /*居中显示整个表格*/
                    margin: auto;
                }

                table.dataframe thead {
                    border: 2px solid #000000;
                    background: #f1f1f1;
                    padding: 10px 10px 10px 10px;
                    color: #333333;
                }

                table.dataframe tbody {
                    border: 2px solid #000000;
                    padding: 10px 10px 10px 10px;
                }

                table.dataframe tr {

                }

                table.dataframe th {
                    vertical-align: top;
                    font-size: 14px;
                    padding: 10px 10px 10px 10px;
                    color:#191970;
                    text-align: center;
                }

                table.dataframe td {
                    text-align: center;
                    padding: 10px 10px 10px 10px;
                }

                body {
                    font-family: 宋体;
                }

                h1 {
                    color: #5db446
                }
                
                div.header h1 {
                    color: #000000;
                    font-family: 黑体;
                }

                div.header h2 {
                    color: #000000;
                    font-family: 黑体;
                }

                div.content h2 {
                    text-align: center;
                    font-size: 28px;
                    text-shadow: 2px 2px 1px #de4040;
                    color: #fff;
                    font-weight: bold;
                    background-color: #191970;
                    line-height: 1.5;
                    margin: 20px 0;
                    box-shadow: 10px 10px 5px #888888;
                    border-radius: 5px;
                }

                h3 {
                    font-size: 22px;
                    background-color: rgba(0, 2, 227, 0.71);
                    text-shadow: 2px 2px 1px #de4040;
                    color: rgba(239, 241, 234, 0.99);
                    line-height: 1.5;
                }

                h4 {
                    color: #e10092;
                    font-family: 楷体;
                    font-size: 20px;
                    text-align: center;
                }

                td img {
                    /*width: 60px;*/
                    max-width: 300px;
                    max-height: 300px;
                }

            </STYLE>
        </head>
        """

        html_body = """
            <body>

            <div align="center" class="header">
                <!--标题部分的信息-->
                <h1 align="center">{title}</h1>
                <h2 align="right">{today}</h2>
            </div>

            <hr>

            <div class="content">
                <!--正文内容-->

                <div>
                    <h4></h4>
                    {df_html}

                </div>
                <hr>

                <p style="text-align: center">

                </p>
            </div>
            </body>
            """.format(title=title, today=datetime.datetime.now().date(), df_html=content)

        html_msg = "<html>" + html_head + html_body + "</html>"

        html_msg = html_msg.replace('\n', '').encode("utf-8")

        return html_msg

    @classmethod
    def scheduled_task(cls, cmd_list):
        """
        :param cmd_list:
        :return:
        定时任务
        command = "python " + os.getcwd() + "/" + "demo.py  %s" % 0.78

            demo.py: 待执行的文件, 需要传参就加上 %s

            在demo.py，首先导入import sys，然后可以获取刚刚传递过来的参数

            import sys
            print(sys.argv[1])

        cmd_list = [command, ....]
        """
        while True:
            ts_start = datetime.datetime.now()
            if ts_start.hour == 10:  # 每天10点定时运行task脚本
                for cmd in cmd_list:
                    os.system(cmd)


if __name__ == "__main__":

    content = [
            {
                "start_time": "2020-02-11",
                "end_time": "2020-09-11",
                "huaxia_own": "43%",
                "huaxia_lease": "42%",
                "user_name": "xxx",
                "save_time": "2020-02-11"

            },
            {
                "start_time": "2020-02-11",
                "end_time": "2020-09-11",
                "huaxia_own": "43%",
                "huaxia_lease": "42%",
                "user_name": "xxx",
                "save_time": "2020-02-11"

            }
        ]

    
