from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait
from pyquery import PyQuery as pq
import json
import pymongo
from openpyxl import Workbook

options = webdriver.ChromeOptions()
options.add_argument('--user-agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.108 Safari/537.36"')
browser = webdriver.Chrome(options=options)
wait = WebDriverWait(browser, 30)

MONGO_URL = 'localhost'
MONGO_DB = '51job'
MONGO_COLLECTION = '金融/投资/证券'
client = pymongo.MongoClient(MONGO_URL)
db = client[MONGO_DB]
lines = []
MAX_PAGE = 200

def get_page(page):
    print('第', page, '页')
    try:
        url = 'https://search.51job.com/list/030200,000000,0000,03,9,99,%2B,2,1.html?lang=c&stype=1&postchannel=0000&workyear=99&cotype=99&degreefrom=99&jobterm=99&companysize=99&lonlat=0%2C0&radius=-1&ord_field=0&confirmdate=9&fromType=&dibiaoid=0&address=&line=&specialarea=00&from=&welfare='
        browser.get(url)
        if page > 1:
            input = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, '.p_in > .mytxt')))
            submit = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, '.p_in > .og_but')))
            input.clear()
            input.send_keys(page)
            submit.click()
        wait.until(EC.text_to_be_present_in_element((By.CSS_SELECTOR, '.p_in ul > .on'), str(page)))
        wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, '.dw_table .el')))
        get_job_data()
    except TimeoutException:
        get_page(page)


def get_job_data():
    html = browser.page_source
    doc = pq(html)
    items = doc('.dw_table div.el').items()
    for item in items:
        data = {}
        data['职位名'] = item.find('.t1 span a').text()
        data['公司名'] = item.find('.t2 a').text()
        data['工作地点'] = item.find('.t3').text()
        data['薪资'] = item.find('.t4').text()
        data['发布时间'] = item.find('.t5').text()
        datalist = [data['职位名'], data['公司名'], data['工作地点'], data['薪资'], data['发布时间']]
        lines.append(datalist)
        save_job_data(lines)


def save_job_data(lines):
    #保存到Excel
    workbook = Workbook()
    worksheet = workbook.active
    worksheet.append(['职位名','公司名', '工作地点', '薪资', '发布时间'])
    for line in lines:
        worksheet.append(line)
    workbook.save('51job.xlsx')
#    #保存为txt
#    with open('51jobdata.txt', 'a', encoding='utf-8') as f:
#        f.write(json.dumps(data, ensure_ascii=False)+ '\n')
#    #保存到 mongoDB
#    try:
#        if db[MONGO_COLLECTION].insert(data):
#            print('存储到MONGODB成功')
#    except Exception:
#        print('存储到MONGODB失败')


def main():
    for i in range(1, MAX_PAGE + 1):
        get_page(i)


if __name__ == '__main__':
    main()
