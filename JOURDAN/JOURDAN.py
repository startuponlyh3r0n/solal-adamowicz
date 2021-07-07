from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import requests
import datetime
import csv
import time
import unicodedata

#vars
already_existing_candidates = []

linkedin_researches = {
    "https://www.linkedin.com/talent/hire/275535401/discover/recruiterSearch?savedSearch=urn%3Ali%3Ats_cap_saved_search%3A1613200643&savedSearchAction=GET&searchContextId=f0faf016-939e-44c4-99c5-541cbf157596&searchHistoryId=10292933033&searchRequestId=6cbf975a-3a53-4c2d-9ce7-ecdc2abe7ff4&start=":75, #Commercial CDI
    "https://www.linkedin.com/talent/hire/275535401/discover/recruiterSearch?savedSearch=urn%3Ali%3Ats_cap_saved_search%3A1613222323&savedSearchAction=GET&searchContextId=5ee387eb-ea7e-4c75-901a-9cf7d4865ce0&searchHistoryId=10292934913&searchRequestId=10e465e1-1240-4cb5-a3f6-527a8366f449&start=":100, #Commercial Stage
    "https://www.linkedin.com/talent/search/advanced?searchContextId=7897e739-c6d9-4e1a-aa96-30e7d66a0c4c&searchHistoryId=10292943553&searchRequestId=2b6f7a7c-5316-4600-926b-8ad7d72a9c57&start=":50, #Tech CDI
    "https://www.linkedin.com/talent/search?searchContextId=816410c0-dfc7-4930-bc83-c5d56252adc4&searchHistoryId=10292943553&searchRequestId=658a7db1-c793-4697-aeda-9a3204e17c60&start=":75, #Tech Stage
    "https://www.linkedin.com/talent/hire/275535401/discover/recruiterSearch?savedSearch=urn%3Ali%3Ats_cap_saved_search%3A1613200643&savedSearchAction=GET&searchContextId=2b7f7646-7f71-4c8b-a659-ef835924c2d5&searchHistoryId=10292977253&searchRequestId=6ecbc30d-d60b-4878-b478-9b7fb380146a&start=":50, #Market&Comm CDI
    "https://www.linkedin.com/talent/hire/275535401/discover/recruiterSearch?savedSearch=urn%3Ali%3Ats_cap_saved_search%3A1617730923&savedSearchAction=GET&searchContextId=585551bd-6d02-4d16-9eda-3ced9a89d035&searchHistoryId=10292977253&searchRequestId=bb2cd1ae-d9de-4c48-9cb5-aeacaa4b0a6c&start=":100, #Market&Comm Stage
    }

linkedin_candidate_profiles = {}
dropcontact_batch = []

#get all candidates from JOURDAN Lemlist
jourdan_leads = requests.get('https://api.lemlist.com/api/campaigns/cam_uxTTSAwJBvL5mPap5/export/list?state=all', auth=('', '2d4adb5af04759b8a6f1249608835b96'))
#csv formating
with open('JOURDAN/JOURDAN_Lemlist_Leads.csv','wb') as csv_file:
	csv_file.write(jourdan_leads.content)
with open('JOURDAN/JOURDAN_Lemlist_Leads.csv','r') as csv_file:
	file = csv.reader(csv_file, delimiter=',')
	for row in file:
		already_existing_candidates.append(row[5])


#driver setup
options = webdriver.ChromeOptions()
options.add_argument("--user-data-dir=profile-julie")
options.add_argument("--remote-debugging-port=9222")  # this

driver = webdriver.Chrome(executable_path="chromedriver", options = options)
driver.implicitly_wait(10)

#scraaaape
start_time = datetime.datetime.now()
for research in linkedin_researches:
    page = 0
    fucked_count = 0
    nb_scraped_candidates = 0
    while nb_scraped_candidates < linkedin_researches[research]:
        linkedin_candidate_pages = {}
        driver.get(research + str(page*25))
        time.sleep(3)
        candidates = driver.find_elements_by_class_name("artdeco-entity-lockup__title.ember-view")
        for candidate in candidates:
            candidate_name = candidate.text
            candidate_html = candidate.get_attribute("innerHTML")
            candidate_page_link_start = candidate_html.find("href=\"")+6
            candidate_page_link_end = candidate_html.find("\"",candidate_page_link_start,len(candidate_html))
            candidate_page_link = candidate_html[candidate_page_link_start:candidate_page_link_end]
            linkedin_candidate_pages[candidate_name]=candidate_page_link

        if fucked_count == 3:
            print("fuck")
            break
        if len(linkedin_candidate_pages) == 0:
            page = 0
            fucked_count +=1
            continue

        for candidate_page in linkedin_candidate_pages:
            driver.get(linkedin_candidate_pages[candidate_page])
            try:
                linkedin_profile_link = driver.find_element_by_class_name("personal-info__link").get_attribute("href")
                current_company = driver.find_elements_by_class_name("position-item__company-link")[0].text
            except:
                continue
            if linkedin_profile_link not in already_existing_candidates:
                linkedin_candidate_profiles[candidate_page] = [linkedin_profile_link,current_company,research]
                nb_scraped_candidates += 1
        print(nb_scraped_candidates)
        print(linkedin_researches[research])
        page += 1
driver.close()
print(str(len(linkedin_candidate_profiles)) + " profiles")
print(datetime.datetime.now()-start_time)

#format for dropcontact
count = 0
for profile in linkedin_candidate_profiles:
    first_name = profile[:profile.find(' ')]
    last_name = profile[profile.find(' '):]
    if linkedin_candidate_profiles[profile][2] == "https://www.linkedin.com/talent/hire/275535401/discover/recruiterSearch?savedSearch=urn%3Ali%3Ats_cap_saved_search%3A1613200643&savedSearchAction=GET&searchContextId=f0faf016-939e-44c4-99c5-541cbf157596&searchHistoryId=10292933033&searchRequestId=6cbf975a-3a53-4c2d-9ce7-ecdc2abe7ff4&start=" or linkedin_candidate_profiles[profile][2]  == "https://www.linkedin.com/talent/hire/275535401/discover/recruiterSearch?savedSearch=urn%3Ali%3Ats_cap_saved_search%3A1613222323&savedSearchAction=GET&searchContextId=5ee387eb-ea7e-4c75-901a-9cf7d4865ce0&searchHistoryId=10292934913&searchRequestId=10e465e1-1240-4cb5-a3f6-527a8366f449&start=":
        candidate_category = "businnes"
    if linkedin_candidate_profiles[profile][2] == "https://www.linkedin.com/talent/search/advanced?searchContextId=7897e739-c6d9-4e1a-aa96-30e7d66a0c4c&searchHistoryId=10292943553&searchRequestId=2b6f7a7c-5316-4600-926b-8ad7d72a9c57&start=" or linkedin_candidate_profiles[profile][2] == "https://www.linkedin.com/talent/search?searchContextId=816410c0-dfc7-4930-bc83-c5d56252adc4&searchHistoryId=10292943553&searchRequestId=658a7db1-c793-4697-aeda-9a3204e17c60&start=":
        candidate_category = "tech"
    if linkedin_candidate_profiles[profile][2] == "https://www.linkedin.com/talent/hire/275535401/discover/recruiterSearch?savedSearch=urn%3Ali%3Ats_cap_saved_search%3A1613200643&savedSearchAction=GET&searchContextId=2b7f7646-7f71-4c8b-a659-ef835924c2d5&searchHistoryId=10292977253&searchRequestId=6ecbc30d-d60b-4878-b478-9b7fb380146a&start=" or linkedin_candidate_profiles[profile][2] == "https://www.linkedin.com/talent/hire/275535401/discover/recruiterSearch?savedSearch=urn%3Ali%3Ats_cap_saved_search%3A1617730923&savedSearchAction=GET&searchContextId=585551bd-6d02-4d16-9eda-3ced9a89d035&searchHistoryId=10292977253&searchRequestId=bb2cd1ae-d9de-4c48-9cb5-aeacaa4b0a6c&start=":
        candidate_category = "marketing & communication"
    candidate_data = {"first_name":first_name,"last_name":last_name,"linkedin":linkedin_candidate_profiles[profile][0],"company":linkedin_candidate_profiles[profile][1],"category":candidate_category}
    dropcontact_batch.append(candidate_data)

#send to dropcontact
Dropcontact_apiKey = "ZIAvGMbQzNIwOf9uhor2FuzUHgZdE2"
dropcontact_batches = []
for i in range(0,(int(len(dropcontact_batch)/200))+1):
    dropcontact_batches.append(dropcontact_batch[(i*200):(i*200)+200])

dropcontact_result = []
for batch in dropcontact_batches:
    dropcontact_batch_request = requests.post("https://api.dropcontact.io/batch",json={"data": batch,'siren': False,},headers={'Content-Type': 'application/json','X-Access-Token': Dropcontact_apiKey})
    request_id = dropcontact_batch_request.json()["request_id"]
    dropcontact_batch_result = requests.get("https://api.dropcontact.io/batch/" + request_id, headers={'X-Access-Token': Dropcontact_apiKey}).json()

    sleeping_time = 0
    while dropcontact_batch_result["success"] is False:
        sleeping_time += 30
        time.sleep(30)
        print ("still buffering : " + str(sleeping_time) + " seconds")
        dropcontact_batch_result = requests.get("https://api.dropcontact.io/batch/" + request_id, headers={'X-Access-Token': Dropcontact_apiKey}).json()

    dropcontact_result.extend(dropcontact_batch_result["data"])


#send to lemlist
lemlist_jourdan_campaignId = requests.get("https://api.lemlist.com/api/campaigns", auth=("", "2d4adb5af04759b8a6f1249608835b96")).json()[2]["_id"]

count = 0
for candidate_data in dropcontact_result:
  if "email" in candidate_data:
    count += 1
    if "first_name" not in candidate_data:
        candidate_data["first_name"] = dropcontact_batch[dropcontact_result.index(candidate_data)]["first_name"]
        print("first_name was missing")
    if "last_name" not in candidate_data:
        candidate_data["last_name"] = dropcontact_batch[dropcontact_result.index(candidate_data)]["last_name"]
        print("last_name was missing")
    if "linkedin" not in candidate_data:
        candidate_data["linkedin"] = dropcontact_batch[dropcontact_result.index(candidate_data)]["linkedin"]
        print("linkedin was missing")
    data = unicodedata.normalize('NFKD', '{"firstName":"'+candidate_data["first_name"]+'","lastName":"'+candidate_data["last_name"]+'","linkedinUrl":"'+candidate_data["linkedin"]+'"}').encode('ASCII', 'ignore').decode('utf-8')
    send_to_lemlist = requests.post("https://api.lemlist.com/api/campaigns/" + lemlist_jourdan_campaignId + "/leads/" + candidate_data["email"][0]["email"] + "?deduplicate=true", headers = {"Content-Type": "application/json"}, data = data, auth = ("", "2d4adb5af04759b8a6f1249608835b96"))
    if str(send_to_lemlist) != "<Response [200]>":
      print (send_to_lemlist.content)

print (str(count) + " emails found out of " + str(len(dropcontact_batch)))
print(datetime.datetime.now()-start_time)
