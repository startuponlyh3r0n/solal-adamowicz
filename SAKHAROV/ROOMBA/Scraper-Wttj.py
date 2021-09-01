from selenium import webdriver
import time
import re
import datetime

#vars
current_time = datetime.datetime.now()
yesterday = current_time - datetime.timedelta(days=2)

url_wttj = "https://www.welcometothejungle.com/fr/jobs?page="
url_wttj_countryTag = "&aroundQuery=France%2C%20France"
url_commerciaux = "&refinementList%5Bprofession_name.fr.Business%5D%5B%5D=Commercial&refinementList%5Bprofession_name.fr.Business%5D%5B%5D=Business%20Development&refinementList%5Bprofession_name.fr.Business%5D%5B%5D=Account%20Management&refinementList%5Bprofession_name.fr.Business%5D%5B%5D=Autres&refinementList%5Bprofession_name.fr.Business%5D%5B%5D=Acheteur&refinementList%5Borganization.size.fr%5D%5B%5D=<%2015%20salariés&refinementList%5Borganization.size.fr%5D%5B%5D=Entre%2015%20et%2050%20salariés"
url_tech = "&refinementList%5Borganization.size.fr%5D%5B%5D=<%2015%20salariés&refinementList%5Borganization.size.fr%5D%5B%5D=Entre%2015%20et%2050%20salariés&refinementList%5Bprofession_name.fr.Tech%5D%5B%5D=Dev%20Fullstack&refinementList%5Bprofession_name.fr.Tech%5D%5B%5D=Dev%20Backend&refinementList%5Bprofession_name.fr.Tech%5D%5B%5D=Project%20%2F%20Product%20Management&refinementList%5Bprofession_name.fr.Tech%5D%5B%5D=Dev%20Frontend&refinementList%5Bprofession_name.fr.Tech%5D%5B%5D=Autres&refinementList%5Bprofession_name.fr.Tech%5D%5B%5D=DevOps%20%2F%20Infra&refinementList%5Bprofession_name.fr.Tech%5D%5B%5D=Dev%20Mobile&refinementList%5Bprofession_name.fr.Tech%5D%5B%5D=Data%20Engineering&refinementList%5Bprofession_name.fr.Tech%5D%5B%5D=Data%20Science&refinementList%5Bprofession_name.fr.Tech%5D%5B%5D=Data%20Analysis"
url_marketcomm = "&refinementList%5Borganization.size.fr%5D%5B%5D=<%2015%20salariés&refinementList%5Borganization.size.fr%5D%5B%5D=Entre%2015%20et%2050%20salariés&refinementList%5Bprofession_name.fr.Marketing%20%2F%20Communication%5D%5B%5D=Marketing&refinementList%5Bprofession_name.fr.Marketing%20%2F%20Communication%5D%5B%5D=Community%20Management%20%2F%20Social%20Media&refinementList%5Bprofession_name.fr.Marketing%20%2F%20Communication%5D%5B%5D=Communication&refinementList%5Bprofession_name.fr.Marketing%20%2F%20Communication%5D%5B%5D=Traffic%20Management&refinementList%5Bprofession_name.fr.Marketing%20%2F%20Communication%5D%5B%5D=SEO%20%2F%20SEM&refinementList%5Bprofession_name.fr.Marketing%20%2F%20Communication%5D%5B%5D=Marketing%20opérationnel&refinementList%5Bprofession_name.fr.Marketing%20%2F%20Communication%5D%5B%5D=Autres&refinementList%5Bprofession_name.fr.Marketing%20%2F%20Communication%5D%5B%5D=Marketing%20développement&refinementList%5Bprofession_name.fr.Marketing%20%2F%20Communication%5D%5B%5D=Marketing%20stratégique&refinementList%5Bprofession_name.fr.Marketing%20%2F%20Communication%5D%5B%5D=Evénementiel&refinementList%5Bprofession_name.fr.Marketing%20%2F%20Communication%5D%5B%5D=Relations%20presse"
url_customer = "&refinementList%5Borganization.size.fr%5D%5B%5D=<%2015%20salariés&refinementList%5Borganization.size.fr%5D%5B%5D=Entre%2015%20et%2050%20salariés&refinementList%5Bprofession_name.fr.Relation%20client%5D%5B%5D=Autres&refinementList%5Bprofession_name.fr.Relation%20client%5D%5B%5D=Customer%20Success&refinementList%5Bprofession_name.fr.Relation%20client%5D%5B%5D=Support%20%2F%20Service%20client"
url_crea = "&refinementList%5Borganization.size.fr%5D%5B%5D=<%2015%20salariés&refinementList%5Borganization.size.fr%5D%5B%5D=Entre%2015%20et%2050%20salariés&refinementList%5Bprofession_name.fr.Créa%5D%5B%5D=Graphisme%20%2F%20Illustration&refinementList%5Bprofession_name.fr.Créa%5D%5B%5D=UX%20Design&refinementList%5Bprofession_name.fr.Créa%5D%5B%5D=Autres&refinementList%5Bprofession_name.fr.Créa%5D%5B%5D=UI%20Design&refinementList%5Bprofession_name.fr.Créa%5D%5B%5D=Motion%20Design&refinementList%5Bprofession_name.fr.Créa%5D%5B%5D=Direction%20créative&refinementList%5Bprofession_name.fr.Créa%5D%5B%5D=Production%20audiovisuelle"
job_type_list = [url_marketcomm,url_customer,url_crea,url_tech,url_commerciaux]


companies_with_recently_opened_positions = {}
companies_dict = {}
companies_list = {}


import pygsheets
pgsh = pygsheets.authorize(service_file="sakharov-so2021-key.json")
sheet_alexandria = pgsh.open("ALEXANDRIA")
worksheet_fromscrape = sheet_alexandria[0]
nb_of_rows = worksheet_fromscrape.rows
already_imported_companies_linkedin = worksheet_fromscrape.get_col(2)
already_imported_companies_name = worksheet_fromscrape.get_col(1)


#setup chrome driver
options = webdriver.ChromeOptions()
driver = webdriver.Chrome(executable_path="chromedriver")
driver.implicitly_wait(10)

for job_type in job_type_list : 
	day_status = True
	page_nb = 0
	driver.get(url_wttj + str(page_nb) + url_wttj_countryTag)
	while day_status is True:
		#get data
		entries = []
		page_nb += 1
		URL = url_wttj + str(page_nb) + url_wttj_countryTag + job_type
		driver.get(URL)
		time.sleep(3)

		refresh_count = 0
		while len(driver.find_elements_by_class_name("ais-Hits-list-item")) == 0 : 
			print ("didn't load "+str(refresh_count))
			refresh_count+=1
			driver.get(url_wttj + str(page_nb))
			driver.get(URL)
			if refresh_count > 5:
				quit()
		time.sleep(3)
		for entry_SL in driver.find_elements_by_class_name("ais-Hits-list-item"):
			innerHTML = entry_SL.get_attribute("innerHTML")
			entries.append(innerHTML)
		for entry in entries :
			company_slug = str(entry)[re.search("/companies/",str(entry)).span()[1]:re.search("/jobs/",str(entry)).span()[0]]
			job = []
			job.append(str(entry)[re.search("<h3 class=\"sc-1kkiv1h-9 sc-7dlxn3-4 ivyJep iXGQr\">",str(entry)).span()[1]:re.search("</h3>",str(entry)).span()[0]])
			if company_slug in companies_with_recently_opened_positions.keys():
				companies_with_recently_opened_positions[company_slug].append(job)
			else:
				companies_with_recently_opened_positions[company_slug] = job
			
			company_name = entry[re.search("<span class=\"ais-Highlight-nonHighlighted\">",entry).span()[1]:re.search("</span>",entry[re.search("<span class=\"ais-Highlight-nonHighlighted\">",entry).span()[1]:]).span()[0]+re.search("<span class=\"ais-Highlight-nonHighlighted\">",entry).span()[1]]
			company_url = "https://www.welcometothejungle.com/fr/companies/" + company_slug
			if company_name not in already_imported_companies_name:
				companies_list[company_name] = company_url

			start_timestamp = re.search("datetime=\"",str(entry)).span()[1]
			end_timestamp = re.search("\">",str(entry)[start_timestamp:]).span()[0]+start_timestamp
			last_timestamp = str(entry)[start_timestamp:end_timestamp]

			datetime_timestamp = datetime.datetime(year = int(last_timestamp[0:4]), month = int(last_timestamp[5:7]), day = int(last_timestamp[8:10]), hour = int(last_timestamp[11:13]), minute = int(last_timestamp[14:16]), second = int(last_timestamp[17:19]))
			if datetime_timestamp < yesterday:
				day_status = False
			if page_nb > 10:
				day_status = False
		if len(companies_list)==0:
			print('rhaaaaa')
			quit()
driver.close()

driver = webdriver.Chrome(executable_path="chromedriver")
for company in companies_list:
	driver.get(companies_list[company])
	company_linkedin_url_temp = driver.find_elements_by_class_name("sc-1552bfn-3.iTMMrn")
	linkedin_url_temp = ""
	for url in company_linkedin_url_temp:
		linkedin_url_temp += str(url.get_attribute("innerHTML"))
	if re.search("https://www.linkedin.com/company/",linkedin_url_temp) is not None:
		start_linkedin = re.search("https://www.linkedin.com/company/",linkedin_url_temp).span()[0]
		end_linkedin = re.search("\" rel=",linkedin_url_temp[start_linkedin:]).span()[0]+start_linkedin
		company_linkedin_url  = linkedin_url_temp[start_linkedin:end_linkedin]

		if (company_linkedin_url not in already_imported_companies_linkedin) and (company not in already_imported_companies_name):
			companies_dict[company] = [company_linkedin_url,job_type,str(companies_with_recently_opened_positions[company_slug])]

print(len(companies_dict))
count = 0
for company in companies_dict:
	company_data = [company]
	company_data.extend(companies_dict[company])
	company_data.append(str(datetime.datetime.today().date()))
	worksheet_fromscrape.insert_rows(row=nb_of_rows, number=1, values=company_data, inherit=True)
	count += 1
print (str(count) + " new companies imported")
print(datetime.datetime.now()-current_time)
