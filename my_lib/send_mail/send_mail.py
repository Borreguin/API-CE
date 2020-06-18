from email.mime.image import MIMEImage
import os

script_path = os.path.dirname(os.path.abspath(__file__))
im_path = script_path.replace("my_lib", "reportes")


def send_mail(msg_to_send:str, subject, recipients, from_email, image_list: list = None):
    from email.mime.multipart import MIMEMultipart
    from email.mime.text import MIMEText
    import smtplib

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
    SERVER = "mail.cenace.org.ec"

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


    # create server
    server = smtplib.SMTP(SERVER)

    server.starttls()

    # Login Credentials for sending the mail
    # server.login(msg['From'], password)

    # send the message via the server.
    server.sendmail(msg['From'], recipients, msg.as_string())

    server.quit()

    print("Detalles enviados a: %s:" % (msg['To']))

