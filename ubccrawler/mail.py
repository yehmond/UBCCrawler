import smtplib
from email.mime.text import MIMEText

port = 465
smtp_server = "smtp.gmail.com"
sender_email = <your_email>
password = <your_password>


def send_mail(dict, receiver_email):

    content = ""
    content += "Good news! A spot in " + dict["Course Name: "] + " has opened!" + "\n" + "\n"

    for word in dict:
        content += word
        content += dict[word]
        content += "\n"

    content += "\n"
    content += "\n"
    content += "\n"
    content += "This email was automatically generated by UBCCrawler"

    msg = MIMEText(content)
    msg['From'] = sender_email
    msg['To'] = receiver_email
    msg['Subject'] = 'A Spot has Opened!'

    try:
        with smtplib.SMTP_SSL('{0}:{1}'.format(smtp_server, port)) as server:
            server.login(sender_email, password)
            server.send_message(msg)
    except smtplib.SMTPRecipientsRefused as e:
        print(e)
