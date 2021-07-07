import requests
import datetime

if datetime.date.today().isocalendar()[2]!=3:
	quit()


import pygsheets
pgsh = pygsheets.authorize(service_file="sakharov-so2021-key.json")
sheet_alexandria = pgsh.open("ALEXANDRIA")
worksheet_133CS = sheet_alexandria[2]
nb_of_rows = worksheet_133CS.rows
	
today = datetime.datetime.today()
last_monday = today - datetime.timedelta(days = 10)
last_sunday = today - datetime.timedelta(days = 3)

startuponly_api_token = requests.post("https://api.startuponly.com/accounts/login", data = {"email": "marcbisiou@gmail.com", "password": "123vivaStartupOnly"}).json()["token"]
startuponly_jobs_last100 = requests.get("https://api.startuponly.com/jobs?take=50&skip=0&order=%7B%22createDate%22:%22DESC%22%7D&orderBy=createDate&orderDirection=DESC", headers = {"Authorization": "Bearer " + startuponly_api_token}).json()["data"]

jobs_from_last_week = []
for job in startuponly_jobs_last100:
    so_json_createdDate = job["createDate"]
    createdDate = datetime.datetime(int(so_json_createdDate[0:4]),int(so_json_createdDate[5:7]),int(so_json_createdDate[8:10]))
	
    if (last_monday <= createdDate <= last_sunday) and (job["visibilityStatus"] == "Draft"):
	        jobs_from_last_week.append({"company_name":job["company"]["name"],"email": job["company"]["account"]["email"],"createDate":job["createDate"]})


from mailjet_rest import Client

mailjet_api_key = "5ae492014d8ce0cd7527746dcc62d9d9"
mailjet_secret_api_key = "8737c87f4e091b90b9dcf55951eb19b5"

mailjet = Client(auth=(mailjet_api_key, mailjet_secret_api_key), version='v3')
send_results = []

for job in jobs_from_last_week:
    #Create Contact
    if str(mailjet.contact.get(id = job["email"])) != "<Response [200]>":
        data = {
        'IsExcludedFromCampaigns': 'true',
        'Name': job["company_name"],
        'Email': job["email"]
        }
        result = mailjet.contact.create(data=data)

        contact_id = result.json()["Data"][0]["ID"]

        #Give it properties
        data = {
        "Data": [
            {
            "Name": "company_name",
            "Value": job["company_name"]
            }
        ]
        }
        mailjet.contactdata.update(id=contact_id, data=data)
        
    #Send Emails
    Template_ID = "2971826"
    data = {
    'FromEmail': 'celine@startuponly.com',
    'FromName': 'Celine de Clercq',
    'MJ-TemplateID': Template_ID,
    'MJ-TemplateLanguage': 'true',
    'Recipients': [
                    {
                            "Email": job["email"]
                    }
            ]
    }
    send_result = mailjet.send.create(data=data)
    send_results.append([send_result.json(),send_result.status_code])

