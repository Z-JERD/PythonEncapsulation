import smtplib
from email.mime.text import MIMEText
from email.header import Header

"""
发送邮件前的准备：
    1. 去邮箱手动开启smtp服务
    2. 得到授权码(登录使用)
"""

SenderConfig = {
	"server": "smtp.163.com",           # SMTP服务器地址
    "port": 465                         # SMTP服务器端口
    "user": "13466776842@163.com",      # 发件人邮件地址
    "password": "VOOOCCWADIBJKHDW",     # 授权码
    
}

# 邮件接收人列表
ReceiverList = [
    'zhj_java@163.com'
]


def html_content(content):
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


def send_mail(title, content, html_style=False):
    """
    发送邮件
    :param title: 邮件标题
    :param content: 邮件内容
    :param html_style： 文件内容是否为html
    :return:
    """
    status = 1
    try:
        mail_sp = smtplib.SMTP_SSL(SenderConfig["server"], SenderConfig["port"])
        mail_sp.login(SenderConfig["user"], SenderConfig["password"])
    except Exception as e:
        raise ValueError("登录邮箱失败")

    msg = MIMEText(content, 'html', 'utf-8') if html_style else MIMEText(content)
    msg['Subject'] = Header(title, 'utf-8')
    msg['From'] = SenderConfig["user"]

    try:
        mail_sp.sendmail(SenderConfig["user"], ReceiverList, msg.as_string())
    except Exception as e:
        status = 0
        raise ValueError("邮件发送失败")
    finally:
        mail_sp.quit()

    return "邮件发送成功" if status == 1 else "邮件发送失败"


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
    content = html_content(content)
    ret = send_mail("测试",  content, True)
    print(ret)
