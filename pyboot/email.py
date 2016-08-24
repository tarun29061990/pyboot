import logging
import smtplib
from contextlib import contextmanager
from email.mime.application import MIMEApplication
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from smtpd import COMMASPACE


class EmailClient:
    def __init__(self, smtp_host, smtp_port, username, password, is_tls=False, is_enabled=True):
        self.__is_enabled = is_enabled
        if self.__is_enabled:
            self.__connection = smtplib.SMTP(smtp_host, smtp_port)
            if is_tls:
                self.__connection.ehlo()
                self.__connection.starttls()
            self.__connection.login(username, password)

    def send_email(self, sender, to_addresses, subject, body, body_type='plain', reply_addresses=None,
                   cc_addresses=None, bcc_addresses=None, attachments=None):
        if not self.__is_enabled:
            logging.info("Email is disabled, not sending email")
            return

        message = MIMEMultipart()
        message.set_charset('utf-8')

        message['Subject'] = subject
        message['From'] = sender
        message['To'] = self.__convert_to_strings(to_addresses)
        if cc_addresses: message['CC'] = self.__convert_to_strings(cc_addresses)
        if bcc_addresses: message['BCC'] = self.__convert_to_strings(bcc_addresses)

        if reply_addresses:
            message['Reply-To'] = self.__convert_to_strings(reply_addresses)

        message.attach(MIMEText(body, body_type, "utf-8"))
        if attachments and len(attachments) > 0:
            for attachment in attachments:
                if attachment["type"] == "file":
                    part = MIMEApplication(attachment["file"].read())
                elif attachment["type"] == "filename":
                    with open(attachment["filename"], 'rb') as f:
                        part = MIMEApplication(f.read())
                part.add_header('Content-Disposition', 'attachment', filename=attachment["name"])
                message.attach(part)

        receipients = []
        if to_addresses and isinstance(to_addresses, list):
            receipients += to_addresses
        elif isinstance(to_addresses, str):
            receipients.append(to_addresses)

        if cc_addresses and isinstance(cc_addresses, list):
            receipients += cc_addresses
        elif isinstance(cc_addresses, str):
            receipients.append(cc_addresses)

        if bcc_addresses and isinstance(bcc_addresses, list):
            receipients += bcc_addresses
        elif isinstance(bcc_addresses, str):
            receipients.append(bcc_addresses)

        logging.debug(message.as_string())
        return self.__connection.sendmail(sender, receipients, message.as_string())

    def __convert_to_strings(self, list_of_strs):
        if isinstance(list_of_strs, (list, tuple)):
            result = COMMASPACE.join(list_of_strs)
        else:
            result = list_of_strs
        return result

    def close(self):
        self.__connection.quit()

    @staticmethod
    @contextmanager
    def get(smtp_host, smtp_port, username, password, is_tls, is_enabled=True):
        email_client = EmailClient(smtp_host, smtp_port, username, password, is_tls, is_enabled)
        try:
            yield email_client  # type: EmailClient
        finally:
            email_client.close()
