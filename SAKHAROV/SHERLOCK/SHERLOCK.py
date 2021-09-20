import requests
import pygsheets
import csv
import time
import datetime
import unicodedata

data_dropcontact = []

#Import PBCache to Sheets
pb_cache = requests.get ("https://cache1.phantombooster.com/TZPMKRxwMeQ/Jo3Fc0fvKwg7Dq9ygnj2wg/Leads%20From%20Scrape%20(PB).csv").content

with open("SAKHAROV/SHERLOCK/PhantomBuster_Cache_Export.csv", "wb") as pb_csv:
    pb_csv.write(pb_cache)
    pb_csv.close()

pgsh = pygsheets.authorize(service_file="sakharov-so2021-key.json")
sheet_alexandria = pgsh.open("ALEXANDRIA")
leads_worksheet = sheet_alexandria[1]


initial_nb_of_rows = leads_worksheet.rows

with open("SAKHAROV/SHERLOCK/PhantomBuster_Cache_Export.csv", 'r') as pb_csv:
  reader = csv.reader(pb_csv, skipinitialspace=True, delimiter=',', quotechar='"')
  data = list(reader)
  pb_csv.close()
cleaned_data = []
for value in data[1:]:
    if value[1] == '':
        cleaned_data.append(value)
leads_worksheet.update_values('A1',values=cleaned_data)

leads_worksheet.refresh()
print(initial_nb_of_rows, leads_worksheet.rows+1)
for i in range (initial_nb_of_rows,leads_worksheet.rows):
  if leads_worksheet.get_value("K" + str(i)) == '':
    leads_worksheet.update_value("K" + str(i),"=INDEX(CompanyList_FromScrape_Import!A:A;EQUIV(A"+str(i)+";CompanyList_FromScrape_Import!B:B;0))")
  if leads_worksheet.get_value("L" + str(i)) == '':
    leads_worksheet.update_value("L" + str(i),"=INDEX(CompanyList_FromScrape_Import!B:B;EQUIV(A"+str(i)+";CompanyList_FromScrape_Import!B:B;0))")

for i in range(initial_nb_of_rows-10, leads_worksheet.rows+1):
  active_row = leads_worksheet.get_row(i)
  if active_row[3] != '' and active_row[12] == '':
      lead = {"first_name":active_row[5],"last_name":active_row[6],"linkedin":active_row[3],"company":active_row[10],"company_linkedin":active_row[11]}
      data_dropcontact.append(lead)
      print (active_row[5])
  if active_row[0] != '' and active_row[12] == '':
    leads_worksheet.update_value("M"+str(i),"Traité : " + str(datetime.datetime.today().date()))
print(len(data_dropcontact))
if len(data_dropcontact) == 0:
    exit()

Dropcontact_apiKey = "ZIAvGMbQzNIwOf9uhor2FuzUHgZdE2"

if len(data_dropcontact) < 240:
  dropcontact_batch_request = requests.post("https://api.dropcontact.io/batch",json={"data": data_dropcontact,'siren': False,},headers={'Content-Type': 'application/json','X-Access-Token': Dropcontact_apiKey})
  request_id = dropcontact_batch_request.json()["request_id"]
  dropcontact_batch_result = requests.get("https://api.dropcontact.io/batch/" + request_id, headers={'X-Access-Token': Dropcontact_apiKey}).json()

  sleeping_time = 0
  while dropcontact_batch_result["success"] is False:
    sleeping_time += 30
    time.sleep(30)
    print ("still buffering : " + str(sleeping_time) + " seconds")
    dropcontact_batch_result = requests.get("https://api.dropcontact.io/batch/" + request_id, headers={'X-Access-Token': Dropcontact_apiKey}).json()
  result = dropcontact_batch_result["data"]

else:
  nb = (len(data_dropcontact)-(len(data_dropcontact)%240))/240
  lists = []
  if len(data_dropcontact)%240 != 1:
    nb +=1
  for i in range(0,nb):
      j=i*240
      lists[i] = data_dropcontact[0+j:240+j]
  result = []
  for list in lists:
      dropcontact_batch_request = requests.post("https://api.dropcontact.io/batch",json={"data": list,'siren': False,},headers={'Content-Type': 'application/json','X-Access-Token': Dropcontact_apiKey})
      request_id = dropcontact_batch_request.json()["request_id"]
      dropcontact_batch_result = requests.get("https://api.dropcontact.io/batch/" + request_id, headers={'X-Access-Token': Dropcontact_apiKey}).json()
      sleeping_time = 0
      while dropcontact_batch_result["success"] is False:
        sleeping_time += 30
        time.sleep(30)
        print ("still buffering : " + str(sleeping_time) + " seconds")
        dropcontact_batch_result = requests.get("https://api.dropcontact.io/batch/" + request_id, headers={'X-Access-Token': Dropcontact_apiKey}).json()
    
      result.extend(dropcontact_batch_result["data"])
        
lemlist_cyrus_campaignId = requests.get("https://api.lemlist.com/api/campaigns", auth=("", "2d4adb5af04759b8a6f1249608835b96")).json()[1]["_id"]

count = 0
for lead_data in result:
  if "email" in lead_data:
    count += 1
    if "first_name" not in lead_data:
        lead_data["first_name"] = data_dropcontact[dropcontact_batch_result["data"].index(lead_data)]["first_name"]
        print("first_name was missing")
    if "last_name" not in lead_data:
        lead_data["last_name"] = data_dropcontact[dropcontact_batch_result["data"].index(lead_data)]["last_name"]
        print("last_name was missing")
    if "linkedin" not in lead_data:
        lead_data["linkedin"] = data_dropcontact[dropcontact_batch_result["data"].index(lead_data)]["linkedin"]
        print("linkedin was missing")
    data = unicodedata.normalize('NFKD', '{"firstName":"'+lead_data["first_name"]+'","lastName":"'+lead_data["last_name"]+'","companyName": "'+lead_data["company"]+'","linkedinUrl":"'+lead_data["linkedin"]+'"}').encode('ASCII', 'ignore').decode('utf-8')
    send_to_lemlist = requests.post("https://api.lemlist.com/api/campaigns/" + lemlist_cyrus_campaignId + "/leads/" + lead_data["email"][0]["email"] + "?deduplicate=true", headers = {"Content-Type": "application/json"}, data = data, auth = ("", "2d4adb5af04759b8a6f1249608835b96"))
    if str(send_to_lemlist) != "<Response [200]>":
      print (send_to_lemlist.content)

print (str(count) + " emails found out of " + str(len(data_dropcontact)))
