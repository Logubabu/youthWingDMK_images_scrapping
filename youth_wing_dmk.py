from time import sleep
from bs4 import BeautifulSoup
import pandas as pd
import requests
from selenium.webdriver.chrome.options import Options
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait as wait

def chrome_render():
    chrome_options = Options()
    chrome_options.add_argument("log-level=3")  # disable logging
    # chrome_options.add_argument("--headless")  # run in headless mode
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    path =r"D:/chromedriver.exe"

    return webdriver.Chrome(path, options=chrome_options, service_log_path="NUL")

def page_soup(page_source):
    response = BeautifulSoup(page_source, "html.parser")
    return response

browser = chrome_render()

browser.get('https://www.youthwingdmk.in/publications/photo')
browser.maximize_window()

soup = page_soup(browser.page_source)
reports = soup.find("div", attrs={"class": "reports"})
row = reports.find("div", attrs={"class": "row"})
contents = row.find_all("div", attrs={"class": "ng-star-inserted"})
try:
    date=[]
    description=[]
    fileNames=[]
    for i,content in enumerate(contents[121:],122):
        sleep(3)
        print("i",i)
        card=content.find("div", attrs={"class": "card"})
        date.append(card.find("p",attrs={"class": "date-time"}).text)
        sleep(3)
        try:
            venue = wait(browser, 5).until(EC.element_to_be_clickable((By.XPATH,f'/html/body/app-root/div/div/app-pub-page/app-pub-list/div/div[2]/div/div[{i}]/app-pub-card/div/div/h5')))
            venue.click()
        except Exception as e:
            venue = wait(browser, 5).until(EC.element_to_be_clickable((By.XPATH,f'/html/body/app-root/div/div/app-pub-page/app-pub-list/div/div[2]/div/div[{i}]/app-pub-card/div/div/h5')))
            browser.execute_script("arguments[0].scrollIntoView();", venue)
            browser.execute_script("$(arguments[0]).click();", venue)
        sleep(2)
        res = page_soup(browser.page_source)
        report_wrapper=res.find("div", attrs={"class": "report-wrapper"})
        description.append(report_wrapper.find("h2").text)
        images=report_wrapper.find_all("img", attrs={"class": "image"})
        name=[]
        for idx,img in enumerate(images,1):
            # print("idx",idx)
            img_url=img.attrs["src"]
            file=f"{i}-{idx}.jpg"

            with open(file, 'wb') as f:
                f.write(requests.get(img_url).content)
            name.append(file)

        fileNames.append(name)
        browser.find_element(By.XPATH,'/html/body/app-root/div/div/app-pub-details/div[2]/div/div[2]/div/div[1]/a').click()
        sleep(2)


        print(name)
except Exception as e:
    print("error")


youthWing_data = pd.DataFrame({
    "Date": date,
    "Descriptions": description,
    "File Name": fileNames
})

youthWing_data.to_excel("youth wing.xlsx",index=False)
print("Finish")

browser.quit()  #to close window
