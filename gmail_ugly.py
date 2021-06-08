import smtplib
import time
from API_tokens.Gmail_info import sender_email_id, sender_email_id_password

# Python code to illustrate Sending mail
# to multiple users
# from your Gmail account


# Open a file to retrieve it's content and strip to make it into a list.
def get_mail_list():
    with open("text_files\email-adresses.txt", "r", encoding="utf-8") as f:
        mail_List = [line.strip() for line in f]
        # print("\n" "Mail recipients" "\n" "{}" "\n".format(mail_List))
        return mail_List


# Open a file to retrieve it's content and make it into a str object "message"
def get_email_message():
    with open("text_files\mail_message.txt", "r", encoding="utf-8") as m:
        message = m.read()
        subject = "Python Mail"
        message_with_subject = "Subject: {}\n\n{}".format(subject, message)
        return message_with_subject.encode("utf-8")


def send_email():
    for i in range(len(get_mail_list())):
        s = smtplib.SMTP("smtp.gmail.com", 587)
        # s.set_debuglevel(1)
        s.starttls()
        s.login(sender_email_id, sender_email_id_password)
        for mailspam in range(1):
            s.sendmail(sender_email_id, get_mail_list(), get_email_message())
        s.quit()


def main():
    get_mail_list()
    get_email_message()
    send_email()


if __name__ == "__main__":
    main()
#
