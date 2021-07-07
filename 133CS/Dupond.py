import requests
import datetime

if datetime.date.today().isocalendar()[2]!=3:
	quit()

today = datetime.datetime.today()
last_monday = today - datetime.timedelta(days = 9)
last_sunday = today - datetime.timedelta(days = 3)

import pygsheets
pgsh = pygsheets.authorize(service_file="sakharov-so2021-key.json")
sheet_alexandria = pgsh.open("ALEXANDRIA")
worksheet_133CS = sheet_alexandria[2]
nb_of_rows = worksheet_133CS.rows

candidates_from_a_week_ago = []
startuponly_api_token = requests.post("https://api.startuponly.com/accounts/login", data = {"email": "marcbisiou@gmail.com", "password": "123vivaStartupOnly"}).json()["token"]
startuponly_candidates_last1k = requests.get("https://api.startuponly.com/candidates?take=1000&skip=0&order=%7B%22createDate%22:%22DESC%22%7D&orderBy=createDate&orderDirection=DESC", headers = {"Authorization": "Bearer " + startuponly_api_token}).json()["data"]

for candidate in startuponly_candidates_last1k :
	
	so_json_createdDate = candidate["account"]["createDate"]
	createdDate = datetime.datetime(int(so_json_createdDate[0:4]),int(so_json_createdDate[5:7]),int(so_json_createdDate[8:10]))
	
	if last_monday <= createdDate <= last_sunday and len(candidate["appliedJobIds"]) <= 3 :
		candidates_from_a_week_ago.append({"firstname":candidate["firstname"],"lastname":candidate["lastname"],"email": candidate["account"]["email"],"createDate":candidate["account"]["createDate"]})


from mailjet_rest import Client

mailjet_api_key = "5ae492014d8ce0cd7527746dcc62d9d9"
mailjet_secret_api_key = "8737c87f4e091b90b9dcf55951eb19b5"

mailjet = Client(auth=(mailjet_api_key, mailjet_secret_api_key), version='v3')

send_results = []
for candidate in candidates_from_a_week_ago:

	c_firstname = candidate["firstname"]
	c_lastname = candidate["lastname"]
	c_email = candidate["email"]
	c_createDate = candidate["createDate"]
	print (c_firstname,c_lastname,c_email,c_createDate)
	#Create Contact
	
	data = {
	'IsExcludedFromCampaigns': 'true',
	'Name': c_firstname + c_lastname,
	'Email': c_email
	}
	result = mailjet.contact.create(data=data)
	print(result)
	contact_id = result.json()["Data"][0]["ID"]

	#Give it properties
	data = {
	"Data": [
		{
		"Name": "firstname",
		"Value": c_firstname
		}
	]
	}
	mailjet.contactdata.update(id=contact_id, data=data)

	#Send Emails
	Template_ID = "2855736"
	data = {
	'FromEmail': 'celine@startuponly.com',
	'FromName': 'Celine de Clercq',
	'MJ-TemplateID': Template_ID,
	'MJ-TemplateLanguage': 'true',
	'Recipients': [
					{
							"Email": c_email
					}
			]
	}
	send_result = mailjet.send.create(data=data)
	send_results.append([send_result.json(),send_result.status_code])
	

count = 0
for result in send_results:
	export = ["candidate",result[0]["Sent"][0]["Email"],result[1]]
	export.append(str(datetime.datetime.today().date()))
	worksheet_133CS.insert_rows(row=nb_of_rows, number=1, values=export, inherit=True)
	count += 1

print (str(count) + " new candidates emailed")
