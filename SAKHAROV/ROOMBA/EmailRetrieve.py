#LinkedIn Email Retrieve
def clean(text):
    # clean text for creating a folder
    return "".join(c if c.isalnum() else "_" for c in text)

def get_last_email_code():
    import imaplib
    import email
    import re
    imap = imaplib.IMAP4_SSL("imap.gmail.com")
    imap.login("startuponly.transfert@gmail.com","Koutoush1")

    status, messages = imap.select("INBOX")

    res, msg = imap.fetch("1", "(RFC822)")
    for response in msg:
        if isinstance(response, tuple):
            # parse a bytes email into a message object
            msg = email.message_from_bytes(response[1])
            # if the email message is multipart
            if msg.is_multipart():
                # iterate over email parts
                for part in msg.walk():
                    # extract content type of email
                    content_type = part.get_content_type()
                    content_disposition = str(part.get("Content-Disposition"))
                    try:
                        # get the email body
                        body = part.get_payload(decode=True).decode()
                    except:
                        pass
                    if content_type == "text/plain" and "attachment" not in content_disposition:
                        # print text/plain emails and skip attachments
                        print(body)
                        code_match = re.search("Veuillez vous servir de ce code de vérification pour terminer votre identification\xa0: ",body).span()[1]
                        code = body[code_match:code_match+6]
                        return code
            else:
                # extract content type of email
                content_type = msg.get_content_type()
                # get the email body
                body = msg.get_payload(decode=True).decode()
                if content_type == "text/plain":
                    # print only text email parts
                    print(body)
                    code_match = re.search("Veuillez vous servir de ce code de vérification pour terminer votre identification\xa0: ",body).span()[1]
                    code = body[code_match:code_match+6]
                    return code
    imap.close()
    imap.logout()

linkedin_code = get_last_email_code()
print(linkedin_code)
