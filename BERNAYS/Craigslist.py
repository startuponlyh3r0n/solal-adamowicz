import requests
import random
import datetime

if (datetime.date.today().isocalendar()[2]!=2) and (datetime.date.today().isocalendar()[2]!=4):
    print("wrong day")
    quit()
    
week_number = datetime.date.today().isocalendar()[1]
weekday_number = datetime.date.today().isocalendar()[2]

if (week_number%2) == 0:
    if weekday_number == 2:
        category = "Commerce"
    if weekday_number == 4:
        category = "Créa"
else:
    if weekday_number == 2:
        category = "Tech"
    if weekday_number == 4:
        category = "Marketing & Comm"


#Get All Jobs from this past Month
startuponly_api_token = requests.post("https://api.startuponly.com/accounts/login", data = {"email": "marcbisiou@gmail.com", "password": "123vivaStartupOnly"}).json()["token"]
startuponly_jobs_100 = requests.get("https://api.startuponly.com/jobs?take=100&skip=0&order=%7B%22createDate%22:%22DESC%22%7D&orderBy=createDate&orderDirection=DESC", headers = {"Authorization": "Bearer " + startuponly_api_token}).json()["data"]

#Get Alexandria Logs
import pygsheets
pgsh = pygsheets.authorize(service_file="sakharov-so2021-key.json")
sheet_alexandria = pgsh.open("ALEXANDRIA")
worksheet_bernays = sheet_alexandria[3]
nb_of_rows = worksheet_bernays.rows
already_imported_companies_slug = worksheet_bernays.get_col(2)
#Filter by category then by company(if already in ALEXANDRIA?) then by number of views/number of applications

jobs_list = []
last_month = datetime.date.today()-datetime.timedelta(days=30)
for job in startuponly_jobs_100:
    if (job["category"]["name"]==category) and (job["visibilityStatus"] == "Published") and (job["validationStatus"] == "Validated") and ("profilePictureUrl" in list(job["company"]["account"].keys())):
        so_json_createdDate = job["publishDate"]
        published_date = datetime.date(int(so_json_createdDate[0:4]),int(so_json_createdDate[5:7]),int(so_json_createdDate[8:10]))
        if (published_date >= last_month) and (job["company"]["slug"] not in already_imported_companies_slug):
            jobs_list.append(job)


best_job_data = {"":0}
for job in jobs_list:
    if job["views"] > list(best_job_data.values())[0]:
        best_job_data = {job["company"]["name"]: job["views"]}
        best_job = job

job_types = {'9edc1ced-c2a6-4e60-9cfa-2e5a2d96b9e8': "Stage", '2a5d0460-4fc9-4414-932d-5d031bd80f1e': "Alternance", 'a4808229-1422-4bc3-ab46-e50712dc6190': "CDI", '497890d0-b5d4-4065-a4f6-503fbe4b58c8': "CDD/Freelance", 'a74030f3-695f-4808-93de-1304bccc42ca': "Associé(e)"}
#Get data: company name, job name, job category, job level ?, ...
job_name = best_job["name"]
job_company = best_job["company"]["name"]
company_email = best_job["company"]["account"]["email"]
job_type = job_types[best_job["contractTypeId"]]
job_link = "startuponly.com/company/" +best_job["company"]["slug"] +"/"+ best_job["slug"]
if best_job["company"]["account"]["profilePictureUrl"] == None:
    job_logo = "https://startuponly.com/_nuxt/img/5817a76.jpg"
else:
    job_logo = best_job["company"]["account"]["profilePictureUrl"]
#Generate Post Text

post_text_generator = {"var1":["Le job ", "Le poste ", "L'offre ", "L'annonce "],"var2":[" du moment !"," de ce moment !"," de la semaine !"," de cette semaine !", " pour cette semaine !"], "var3":["Vous avez un ami en recherche ?", "Vous connaissez des gens en recherche ?"], "var4":[" recrute pour un "," ouvre un poste pour un ", " a ouvert un poste pour un ", " cherche des talents pour un ", " cherche des candidats pour un "]}
post_text = ""
post_first_sentence = post_text_generator["var1"][random.randrange(0,4,1)]
if category == "Commerce":
    post_first_sentence += "Commercial"
else:
    post_first_sentence += category
post_first_sentence += post_text_generator["var2"][random.randrange(0,5,1)]
post_text += post_first_sentence + "\n"
post_text += job_name + "\n\n"
post_text += post_text_generator["var3"][random.randrange(0,2,1)]
post_text += "\n@" + job_company + post_text_generator["var4"][random.randrange(0,5,1)] + job_type
post_text += "\nPostulez et partagez :)\n"
post_text += job_link

print(post_text)

#Generate Post Image

data = {"json":'{"template_name": "PosteBiHebdo","api_key": "LyfZqI9fLEcxCOqZ0Yhf7EB51RF3", "base64":"true", "modifications": [{"name": "text-2","type": "text","text": "'+job_company+'","color": "rgb(0, 0, 0)","font-size": "30px","visible": "true"},{"name": "text-3","type": "text","text": "'+post_first_sentence+'","color": "rgb(0, 0, 0)","font-size": "30px","visible": "true"},{"name": "image-4","type": "image","image_url": "'+job_logo+'","width": "139.672px", "height": "139.672px", "visible": "true"}]}'}
image = requests.post("https://studio.pixelixe.com/api/graphic/automation/v1", data=data)

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


#Send to Alexandria
alexandria_company = ["Craigslist", best_job["company"]["slug"], company_email, str(datetime.date.today())]
worksheet_bernays.insert_rows(row=nb_of_rows, number=1, values=alexandria_company, inherit=True)

#Send an email to the company


from mailjet_rest import Client

mailjet_api_key = "5ae492014d8ce0cd7527746dcc62d9d9"
mailjet_secret_api_key = "8737c87f4e091b90b9dcf55951eb19b5"

mailjet = Client(auth=(mailjet_api_key, mailjet_secret_api_key), version='v3')

if str(mailjet.contact.get(id = company_email)) != "<Response [200]>":
    data = {
    'Name': job_company,
    'Email': company_email
    }
    result = mailjet.contact.create(data=data)

    contact_id = result.json()["Data"][0]["ID"]

    #Give it properties
    data = {
    "Data": [
        {
        "Name": "company_name",
        "Value": job_company
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
