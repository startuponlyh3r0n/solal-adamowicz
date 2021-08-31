from selenium import webdriver
import datetime
import time
import re


#vars
start_time = datetime.datetime.now()
linkedin_search = "https://www.linkedin.com/jobs/search/?f_E=1%2C2%2C3%2C4&f_F=it%2Csale%2Cbd%2Cmrkt%2Cprjm%2Chr&keywords=startup&location=France&sortBy=DD&start="
linkedin_login = "https://www.linkedin.com/login"

linkedin_username = "junior@startuponly.com"
linkedin_pw = "%Michael6"

company_hrefs = {}
startups = []
companies_list = {}
options = webdriver.ChromeOptions()
options.add_argument("--user-data-dir=profile-celine") 
driver = webdriver.Chrome(executable_path="chromedriver", options = options)
action = webdriver.ActionChains(driver)
driver.implicitly_wait(10)

#linkedin setup
driver.get("https://linkedin.com/home")
time.sleep(1)

#scraping
for i in range (0,40):
    driver.get (linkedin_search + str(i * 25))
    driver.set_window_size(600,1080)
    time.sleep(1)
    
    #make sure it doesn't continue indefinitely
    refresh_count = 0
    while len(driver.find_elements_by_class_name("job-card-list__entity-lockup.artdeco-entity-lockup.artdeco-entity-lockup--size-4.ember-view")) == 0:
        driver.refresh()
        refresh_count+=1
        if refresh_count == 5:
            break
    if refresh_count == 5:
        continue
    
    for results in range (0,8):
        time.sleep(0.5)
        driver.execute_script("arguments[0].scrollIntoView();", driver.find_elements_by_class_name("flex-grow-1.artdeco-entity-lockup.artdeco-entity-lockup--size-4.ember-view")[-1])

    companies_with_link = driver.find_elements_by_class_name("job-card-container__link.job-card-container__company-name.ember-view")
    for company in companies_with_link:
        company_hrefs[company.text] = company.get_attribute("href")
driver.close()
print(len(company_hrefs))

#check if they're in the list already

import pygsheets
pgsh = pygsheets.authorize(service_file="sakharov-so2021-key.json")
sheet_alexandria = pgsh.open("ALEXANDRIA")
worksheet_fromscrape = sheet_alexandria[0]
nb_of_rows = worksheet_fromscrape.rows
already_imported_companies_linkedin = worksheet_fromscrape.get_col(2)
already_imported_companies_name = worksheet_fromscrape.get_col(1)

for company_href in company_hrefs:
    if (company_hrefs[company_href] not in already_imported_companies_linkedin) and (company_href not in already_imported_companies_name):
        companies_list[company_href] = company_hrefs[company_href]
print(len(companies_list))

#checking size
driver = webdriver.Chrome(executable_path="chromedriver", options = options )
driver.implicitly_wait(10)

driver.get("https://linkedin.com/home")

company_count = 0
for company in companies_list:
    company_count += 1
    driver.get(companies_list[company] + "about/")
    time.sleep(1)
    dds = driver.find_elements_by_tag_name("dd")
    for dd in dds:
        if "employés" in dd.text:
            nb_of_employees = dd.text[0:re.search(" ",dd.text).span()[0]]
            if ("2-10" == nb_of_employees) or ("11-50" == nb_of_employees) or ("0-1" == nb_of_employees):
                startups.append([company,companies_list[company]])
driver.close()
print(len(startups))

print(datetime.datetime.now()-start_time)
count = 0
for startup in startups:
    startup.extend([linkedin_search,"",str(datetime.datetime.today().date())])
    worksheet_fromscrape.insert_rows(row=nb_of_rows, number=1, values=startup, inherit=True)
    count += 1
print (str(count) + " new companies imported")
