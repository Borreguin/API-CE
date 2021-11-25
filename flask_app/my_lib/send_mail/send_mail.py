from email.mime.application import MIMEApplication
from email.mime.image import MIMEImage
import traceback
import os
from os.path import basename

from flask_app.settings.LogDefaultConfig import LogDefaultConfig

script_path = os.path.dirname(os.path.abspath(__file__))
im_path = script_path.replace("my_lib", "reportes")
log = LogDefaultConfig("mail.log").logger


def send_mail(msg_to_send:str, subject, recipients, from_email, image_list: list = None, files: list=None):
    from email.mime.multipart import MIMEMultipart
    from email.mime.text import MIMEText
    import smtplib
    import ssl
    # Create context (to specify TLS version)
    sc = ssl.create_default_context()
    sc.options |= ssl.OP_NO_TLSv1_2 | ssl.OP_NO_TLSv1_3
    # sc.minimum_version = ssl.TLSVersion.TLSv1_1
    sc.check_hostname = False
    sc.verify_mode = ssl.CERT_NONE

    try:
        im_to_append = list()
        # configure images if is needed
        if image_list is not None and isinstance(image_list, list):
            # This assumes the images are in "templates" folder
            for ix, image in enumerate(image_list):
                if "/" in image:
                    image_l = image.replace("./", "")
                    image_l = image_l.split("/")
                    to_check = os.path.join(im_path, *image_l)
                else:
                    to_check = os.path.join(im_path, image)

                if os.path.exists(to_check):
                    # redefine src= in html file (cid:image1)
                    msg_to_send = msg_to_send.replace(image, f"cid:image{ix}")
                    im_to_append.append(to_check)

        # configuraciones generales:
        SERVER = "mail.cenace.gob.ec"

        # create message object instance
        msg = MIMEMultipart('related')

        # setup the parameters of the message
        # password = "cenace.123"
        # recipients = ["mbautista@cenace.org.ec","ems@cenace.org.ec"]
        msg['From'] = from_email
        msg['To'] = ", ".join(recipients)
        msg['Subject'] = subject
        msg.preamble = """"""

        # add in the message body as HTML content
        HTML_BODY = MIMEText(msg_to_send, 'html')
        msg.attach(HTML_BODY)

        # adding messages to the mail (only the ones that where found)
        for ix, image in enumerate(im_to_append):
            try:
                fp = open(os.path.join(im_path, image), 'rb')
                msgImage = MIMEImage(fp.read())
                fp.close()
                # Define the image's ID as referenced above
                msgImage.add_header('Content-ID', f'<image{ix}>')
                msg.attach(msgImage)
            except:
                pass

        # Add files if is needed:
        for f in files or []:
            with open(f, "rb") as fil:
                part = MIMEApplication(
                    fil.read(),
                    Name=basename(f)
                )
            # After the file is closed
            part['Content-Disposition'] = 'attachment; filename="%s"' % basename(f)
            msg.attach(part)

        # create server
        server = smtplib.SMTP(SERVER)

        server.starttls()

        # Login Credentials for sending the mail
        # server.login(msg['From'], password)

        # send the message via the server.
        server.sendmail(msg['From'], recipients, msg.as_string())

        server.quit()
        return True, f"Correo enviado correctamente. Detalles enviados a: {msg['To']}"
    except Exception as e:
        tb = traceback.format_exc()
        log.error(tb)
        return False, f"Error al enviar el correo electrónico: {str(e)}"
