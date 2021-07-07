import requests
import random
import datetime
import re

if datetime.date.today().isocalendar()[2]!=3:
    quit()
    
#get all recent job ads
startuponly_api_token = requests.post("https://api.startuponly.com/accounts/login", data = {"email": "marcbisiou@gmail.com", "password": "123vivaStartupOnly"}).json()["token"]
startuponly_jobs_100 = requests.get("https://api.startuponly.com/jobs?take=100&skip=0&order=%7B%22createDate%22:%22DESC%22%7D&orderBy=createDate&orderDirection=DESC", headers = {"Authorization": "Bearer " + startuponly_api_token}).json()["data"]

#filter out the uninteresting ones
good_companies = {}
companies_list = []
last_2_weeks = datetime.date.today()-datetime.timedelta(days=14)
for job in startuponly_jobs_100:
    if (job["visibilityStatus"] == "Published") and (job["validationStatus"] == "Validated") and ("profilePictureUrl" in list(job["company"]["account"].keys())):
        so_json_createdDate = job["publishDate"]
        published_date = datetime.date(int(so_json_createdDate[0:4]),int(so_json_createdDate[5:7]),int(so_json_createdDate[8:10]))
        if published_date >= last_2_weeks:
            companies_list.append(job)
            if job["company"]["slug"] in good_companies.keys():
                good_companies[job["company"]["slug"]] += 1
            else:
                good_companies[job["company"]["slug"]] = 1

#get ALEXANDRIA Logs
import pygsheets
pgsh = pygsheets.authorize(service_file="sakharov-so2021-key.json")
sheet_alexandria = pgsh.open("ALEXANDRIA")
worksheet_bernays = sheet_alexandria[3]
nb_of_rows = worksheet_bernays.rows
already_imported_companies_slug = worksheet_bernays.get_col(2)

#find the company that posted the most
best_company = {"":0}
for company in good_companies : 
    if company not in already_imported_companies_slug:
        if good_companies[company] > int(list(best_company.values())[0]):
            best_company = {company:good_companies[company]}



#format company data for pixelixe

company_slug = list(best_company.keys())[0]
for company in companies_list:
    if list(best_company.keys())[0] == company["company"]["slug"]:
        company_email = company["company"]["account"]["email"]
company_data = requests.get("https://api.startuponly.com/companies/" + company_slug, headers = {"Authorization": "Bearer " + startuponly_api_token}).json()
company_name = company_data["name"]
nb_of_ads = list(best_company.values())[0]

if company_data["account"]["profilePictureUrl"] == None:
    company_logo = "https://startuponly.com/_nuxt/img/5817a76.jpg"
else:
    company_logo = company_data["account"]["profilePictureUrl"]
    
if len(company_data["description"]) > 1:
    if re.search("\n", company_data["description"]) is not None:
        smallest_match = re.search("\n", company_data["description"]).span()[0]
    else: 
        smallest_match = len(company_data["description"])

    if re.search("\.", company_data["description"]) is not None:
        if re.search(".", company_data["description"]).span()[0] < smallest_match:
            smallest_match = re.search("\.", company_data["description"]).span()[0]

    if company_name in company_data["description"][0:smallest_match]:
        company_description = company_data["description"][0:smallest_match]
else:
    company_description = ""

#create (randomized) post text
post_text = ""
if random.randrange(0,2,1) == 1:
    post_text += "Notre Startup"
else:
    post_text += "La Startup"

if random.randrange(0,2,1) == 1:
    post_text += " de la semaine c'est "
    post_text += company_name
else:
    post_text += " pour cette semaine c'est "
    post_text += "@"+company_name

if nb_of_ads >= 3:
    post_text += "! Ils viennent d'ouvrir " + str(nb_of_ads) + " postes sur StartupOnly.\n"
post_text += "Retrouvez leurs annonces sur startuponly.com\n\n"
if len(company_description) > 1:
    post_text += "Leur description :\n" + company_description
print(post_text)

#create visual with Pixelixe v1
data = {"json":'{"template_name": "ClientHebdomadaire","api_key": "LyfZqI9fLEcxCOqZ0Yhf7EB51RF3", "base64":"true", "modifications": [ {"name": "image-4","type": "image","image_url":"' +company_logo+ '" ,"width": "139.672px", "height": "139.672px", "visible": "true"}, {"name": "text-2","type": "text","text":"' + company_name + '" ,"color": "rgb(0, 0, 0)","font-size": "50px","visible": "true"}]}'}
image = requests.post("https://studio.pixelixe.com/api/graphic/automation/v1", data=data)


#recover image
print(image)
prefix = "data:image/jpeg;base64,"
image_base64 = prefix + image.content.decode("utf-8")[16:]


#updload img
media_payload = {'file': str(image_base64), 
        'fileName': "best-company-img"+str(datetime.date.today())+".png",
        'description': "best_company_image" }
headers = {'Authorization': 'Bearer Z8ZDME2-B7R49PF-HWYQAJ1-NH9Y43V'}

image_upload = requests.post('https://app.ayrshare.com/api/media/upload', headers=headers, json = media_payload)
print (image_upload)
image_url = image_upload.json()['url']


post_payload = {'post': post_text, 
        'platforms': ['facebook', 'linkedin'],
        'mediaUrls': [image_url],
        }

#use img and create post
post = requests.post('https://app.ayrshare.com/api/post', json=post_payload, headers=headers)
print(post.json())

#send email to company


from mailjet_rest import Client

mailjet_api_key = "5ae492014d8ce0cd7527746dcc62d9d9"
mailjet_secret_api_key = "8737c87f4e091b90b9dcf55951eb19b5"

mailjet = Client(auth=(mailjet_api_key, mailjet_secret_api_key), version='v3')

if str(mailjet.contact.get(id = company_email)) != "<Response [200]>":
    data = {
    'Name': company_name,
    'Email': company_email
    }
    result = mailjet.contact.create(data=data)

    contact_id = result.json()["Data"][0]["ID"]

    #Give it properties
    data = {
    "Data": [
        {
        "Name": "company_name",
        "Value": company_name
        }
    ]
    }
    mailjet.contactdata.update(id=contact_id, data=data)
    
#Send Email
Template_ID = "2983791"
data = {
'FromEmail': 'celine@startuponly.com',
'FromName': 'Celine de Clercq',
'MJ-TemplateID': Template_ID,
'MJ-TemplateLanguage': 'true',
'Recipients': [
                {
                        "Email": company_email
                }
        ]
}
send_result = mailjet.send.create(data=data)
print(send_result)

#send company to ALEXANDRIA
alexandria_company = ["Charlie", company_slug, company_email, str(datetime.date.today())]
worksheet_bernays.insert_rows(row=nb_of_rows, number=1, values=alexandria_company, inherit=True)
