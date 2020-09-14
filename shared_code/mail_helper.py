import json
import os
from azure.identity import DefaultAzureCredential
from msgraphcore import GraphSession
from pprint import pprint

import smtplib

scopes = ['mail.read']
credential = DefaultAzureCredential()
graph_session = GraphSession(credential, scopes)

def GetCredential(): 
    credential = DefaultAzureCredential()
    return credential

def post_send():
    body = {
        'message': {
            'subject': 'LV Item In Stock',
            'body': {
                'contentType': 'Text',
                'content': 'Bag is in stock'
            },
            'toRecipients': [
                {
                    'emailAddress': {
                        'address': 'sukin0701@gmail.com'
                    }
                }
            ]}
    }

    result = graph_session \
        .post('/me/sendMail',
              data=json.dumps(body),
              scopes=['mail.send'],
              headers={'Content-Type': 'application/json'}
              )
    pprint(result.status_code)

def send_smtp():
    username='mchen.private@outlook.com'
    password=  os.environ['userPassword']
    mailServer = smtplib.SMTP('smtp-mail.outlook.com', 587)
    mailServer.ehlo()
    mailServer.starttls()
    mailServer.ehlo()
    mailServer.login(username, password)

    sender = 'mchen.private@outlook.com'
    receivers = ['mchen.public@outlook.com', 'sukin0701@gmail.com']

    message = """From: Michael <mchen.private@outlook.com>
    To: Michael <mchen.public@outlook.com>
    Subject: Product Stock Alert

    Product is in stock.
    https://ca.louisvuitton.com/eng-ca/products/pochette-accessoires-monogram-005656
    """

    try:
        mailServer.sendmail(sender, receivers, message)
        print("Email sent success")
    except smtplib.SMTPDataError as err:
        print("Unable to send email")
        print(err)




def get_messages():
    result = graph_session.get('/users/f1e3c96bdc6c6f1f/messages', scopes=['https://graph.microsoft.com/.default'])
    pprint(result.json())
    return result



if __name__ == '__main__':
    print(os.environ['AZURE_SUBSCRIPTION_ID'])
    print(os.environ['AZURE_CLIENT_ID'])
    print(os.environ['AZURE_TENANT_ID'])
    print(os.environ['AZURE_CLIENT_SECRET'])
    # print(GetCredential().get_token("https://graph.microsoft.com/.default").token)
    send_smtp()