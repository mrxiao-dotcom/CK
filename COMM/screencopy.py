import time
from PIL import ImageGrab, Image
import uuid
from comm import acctinfo
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.image import MIMEImage
import os

#msg_from = '1497436688@qq.com'  # 发送方邮箱
#passwd = 'oztczdijxyabieci'  # 填入发送方邮箱的授权码  oztczdijxyabieci
msg_from = "9742518@qq.com"
passwd = 'pttkldjbpewobhch'
#msg_to = '9742518@qq.com'  # 收件人
#receivers = ['9742518@qq.com,203979348@qq.com']
def sent_mail_pic(filename,receivers,acctName=""):
    subject = "程序化交易系统运行播报 [" + acctName + ']' # 主题
    msg = MIMEMultipart('related')
    content = MIMEText('<html><body><img src="cid:imageid" alt="imageid"></body></html>', 'html', 'utf-8')  # 正文
    # msg = MIMEText(content)
    msg.attach(content)
    msg['Subject'] = subject
    msg['From'] = msg_from
    #msg['To'] = msg_to
    receiver = receivers[0].split(",")
    msg['To'] = ','.join(receiver)


    file = open(filename, "rb")
    img_data = file.read()
    file.close()

    img = MIMEImage(img_data)
    img.add_header('Content-ID', 'imageid')
    msg.attach(img)

    try:
        s = smtplib.SMTP_SSL("smtp.qq.com", 465)  # 邮件服务器及端口号
        s.login(msg_from, passwd)
        s.sendmail(msg_from, receiver, msg.as_string())
        print('邮件发送成功！')

    except Exception as e:
        #print("发送失败,失败原因",e)
        #msg_from = "9742518@qq.com"
        #passwd = "pttkldjbpewobhch"
        print("发送失败,失败原因", e)

    finally:
        s.quit()
    time.sleep(3)
    os.remove(filename)


# screen_area——类似格式"A1:J10"
def excel_catch_screen(max_retries=3):

    while True:
        num_retries = 0
        try:
            sht = acctinfo.shtRuntime
            sht.range('A1:O76').api.CopyPicture()

            name = str(uuid.uuid4())  # 重命名唯一值
            new_shape_name = name[:6]
            sht.api.Paste()

            pic = sht.pictures[0]  # 当前图片
            pic.api.Copy()  # 复制图片
            time.sleep(1)
            img = ImageGrab.grabclipboard()  # 获取剪贴板的图片数据
            img_name = new_shape_name + ".PNG"
            print('保存图片', img_name,"成功！")
            img.save(img_name)  # 保存图片
            pic.delete()  # 删除sheet上的图片

            done = True
        except Exception as e:
            print(e)

            if num_retries > max_retries:
                raise
            else:
                continue
        if done:
            break


    return img_name