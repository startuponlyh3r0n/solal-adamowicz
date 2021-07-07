import requests
import datetime


import pygsheets
pgsh = pygsheets.authorize(service_file="sakharov-so2021-key.json")
sheet_alexandria = pgsh.open("ALEXANDRIA")
worksheet_133CS = sheet_alexandria[2]
nb_of_rows = worksheet_133CS.rows

#Part 1: Get Clients from 2 weekdays ago

today = datetime.datetime.today().date()

current_weekday = today.weekday()
if current_weekday <= 1:
    necessary_timedelta = datetime.timedelta(days=4)
    weekend_exception_delta = datetime.timedelta(days=2)
else:
    necessary_timedelta = datetime.timedelta(days=2)
    weekend_exception_delta = datetime.timedelta(days=2)

startuponly_api_token = requests.post("https://api.startuponly.com/accounts/login", data = {"email": "marcbisiou@gmail.com", "password": "123vivaStartupOnly"}).json()["token"]

last_100_startups_url = "https://api.startuponly.com/companies?take=100&skip=0&order=%7B%22createDate%22:%22DESC%22%7D&orderBy=createDate&orderDirection=DESC"
headers = {"Authorization": "Bearer " + startuponly_api_token}
startuponly_startups_last100 = requests.get(last_100_startups_url, headers = headers).json()["data"]

clients = []

for startup in startuponly_startups_last100:

    so_startup_createDate = startup["account"]["createDate"]
    timedate_startup_createDate = datetime.datetime(int(so_startup_createDate[0:4]),int(so_startup_createDate[5:7]),int(so_startup_createDate[8:10])).date()

    subscription_status = startup["account"]["hasSubscribedOnce"]
    if (timedate_startup_createDate == (today - necessary_timedelta) or timedate_startup_createDate == (today - weekend_exception_delta)) and subscription_status == False :
        clients.append({"startup_name":startup["name"],"email":startup["account"]["email"],"createDate":startup["account"]["createDate"]})


#Part 2: Email Clients

from mailjet_rest import Client

mailjet_api_key = "5ae492014d8ce0cd7527746dcc62d9d9"
mailjet_secret_api_key = "8737c87f4e091b90b9dcf55951eb19b5"

mailjet = Client(auth=(mailjet_api_key, mailjet_secret_api_key), version='v3')
send_results = []
for client in clients:
    #Create Contact
    data = {
    'IsExcludedFromCampaigns': 'true',
    'Name': client["startup_name"],
    'Email': client["email"]
    }
    result = mailjet.contact.create(data=data)

    contact_id = result.json()["Data"][0]["ID"]

    #Give it properties
    data = {
    "Data": [
        {
        "Name": "company_name",
        "Value": client["startup_name"]
        }
    ]
    }
    mailjet.contactdata.update(id=contact_id, data=data)

    #Send Emails
    Template_ID = "2864159"
    data = {
    'FromEmail': 'celine@startuponly.com',
    'FromName': 'Celine de Clercq',
    'MJ-TemplateID': Template_ID,
    'MJ-TemplateLanguage': 'true',
    'Recipients': [
                    {
                            "Email": client["email"]
                    }
            ]
    }
    send_result = mailjet.send.create(data=data)
    send_results.append([send_result.json(),send_result.status_code])

count = 0
for result in send_results:
    export = ["company",result[0]["Sent"][0]["Email"],result[1]]
    export.append(str(datetime.datetime.today().date()))
    worksheet_133CS.insert_rows(row=nb_of_rows, number=1, values=export, inherit=True)
    count += 1

print (str(count) + " new companies emailed")
