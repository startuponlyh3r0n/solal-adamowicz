import requests
import csv
import datetime

if datetime.date.today().isocalendar()[2]!=1:
	quit()

past_two_weeks = []
for i in range(0,15):
    past_two_weeks.append(str(datetime.date.today()-datetime.timedelta(i)))


#get lemlist ppl
cyrus_leads = requests.get('https://api.lemlist.com/api/campaigns/cam_GP3xafdpXMB4KH8dN/export/', auth=('', '2d4adb5af04759b8a6f1249608835b96'))

with open('133CS/CYRUS.csv','wb') as csv_file:
	csv_file.write(cyrus_leads.content)

leads_stats = {}
replied = {}
with open('133CS/CYRUS.csv','r') as csv_file:
	file = csv.reader(csv_file, delimiter=',')
	for row in file:
		leads_stats[row[0]] = [row[39],row[58],row[93],row[112],row[120],row[139],row[147],row[166],row[174],row[193],row[201],row[220]]


#check if they've replied this week
for lead in leads_stats:
    for date in leads_stats[lead]:
        if date != '':
            if date[:10] in past_two_weeks:
                replied[lead[lead.find("@")+1:]] = date[:10]


#check newly onboarded
startuponly_api_token = requests.post("https://api.startuponly.com/accounts/login", data = {"email": "marcbisiou@gmail.com", "password": "123vivaStartupOnly"}).json()["token"]

last_companies_url = "https://api.startuponly.com/companies?take=100&skip=0&order=%7B%22createDate%22:%22DESC%22%7D&orderBy=createDate&orderDirection=DESC"
headers = {"Authorization": "Bearer " + startuponly_api_token}
last_companies = requests.get(last_companies_url, headers = headers).json()["data"]

weeks_new_companies = []

for company in last_companies:
    if company["account"]["createDate"][:10] in past_two_weeks:
        weeks_new_companies.append(company["account"]["email"][company["account"]["email"].find("@")+1:])


#compare
to_check = []
for company in replied:
    if company not in weeks_new_companies:
        to_check.append(company)

from mailjet_rest import Client

mailjet_api_key = "5ae492014d8ce0cd7527746dcc62d9d9"
mailjet_secret_api_key = "8737c87f4e091b90b9dcf55951eb19b5"
mailjet = Client(auth=(mailjet_api_key, mailjet_secret_api_key), version='v3')
data = {
	'FromEmail': 'celine@startuponly.com',
	'FromName': 'Céliiiine',
	'Subject': 'Helo Greg !!',
	'Text-part': 'Hello Greg, Pour bien commencer la semaine, voici une liste des boites qui ont répondu récemment mais ne se sont pas inscrites :) ' + str(to_check) + 'Bonne journée, ta Céline chérie xoxo PS: Dans Lemlist tu peux clicker sur replied pour avoir une liste centralisée des messages reçus ;)',
	'Html-part': '<b>Hello Greg,</b><br><br><br> Pour bien commencer la semaine, voici une liste des boites qui ont répondu récemment mais ne se sont pas inscrites :)<br><br> ' + str(to_check) + '<br><br><br>Bonne journée,<br> ta Céline chérie<br> xoxo <br><br> PS: Dans Lemlist tu peux clicker sur replied pour avoir une liste centralisée des messages reçus ;)',
	'Recipients': [{'Email':'admin@startuponly.com'}]
}
result = mailjet.send.create(data=data)
print(result.json())
print (result.status_code)

