import time
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
import requests
import json
import os
from bs4 import BeautifulSoup
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

chrome_options = webdriver.ChromeOptions()
chrome_options.binary_location = os.environ.get("GOOGLE_CHROME_BIN")
chrome_options.add_argument("--headless")
chrome_options.add_argument("--disable-dev-shm-usage")
chrome_options.add_argument("--no-sandbox")
driver = webdriver.Chrome(executable_path=os.environ.get("CHROMEDRIVER_PATH"), chrome_options=chrome_options)

client = MongoClient('mongodb://abhishek:RnNVpXgM@<hostname>/profscrape?ssl=true&replicaSet=atlas-auyjwb-shard-0&authSource=admin&retryWrites=true&w=majority')

database = client['profscrape']

my_collection = database['data']

#driver = webdriver.Chrome(executable_path=driver_path)

def get_answer(ques_id,quesnum,title,quizid):
    data = {"quizid":quizid,"title":title,
            "login_name":"",
            "quizmode":"PracticeMode","trainingModule":"PracticeMode"
            ,'checkansphp':'check','ques_id':ques_id,'quesnum':quesnum
            }  
    r = requests.post(url = 'https://www.proprofs.com/quiz-school/_ajax_quizshow_free_new.php', data = data)
   
    soup=BeautifulSoup(json.loads(r.text)['html'],'html.parser')
    for options in soup.find_all('div',{'class':'answer_option'}):
        classes=options.find('label')['class']
        if 'showRightBox' in classes:
            answer=options.find('span',{'class':'m_opttxt'})
            return answer.get_text()
sample_mcq_questions=[]

def get_mcq(url):
   
        print(url)
   
        driver.get(url)

        r=requests.get(url)
        soup=BeautifulSoup(r.content,'html.parser')
        quizid=soup.find('input',{'name':'quizid'})['value']
        title=url.split('?')[1].split("=")[1]
        print(quizid)

        l=driver.find_element(By.NAME,"mySubmit")
        l.click();
        ques_box=driver.find_elements(By.CLASS_NAME, 'ques-area-box')
        qus={}
        qus['url']=url
        qus['chapter']=title
        data=[]
        for questions in ques_box:
            qid=questions.get_attribute('data-ques_id')
            qnum=questions.get_attribute('data-q_num')
            qus_ans={}
            li=[]
            question=questions.find_element(By.CLASS_NAME,'ques-print-text')
            qus_ans['question']=question.text
            
            for option in questions.find_elements(By.CLASS_NAME,'answer_option'):
                li.append(option.find_element(By.CLASS_NAME,'answer_text_container').text)
            qus_ans['choices']=li
            try:
                qus_ans['answer']=get_answer(qid,qnum,title,quizid)
                data.append(qus_ans)
            except:
                pass
        qus['data']=data
        sample_mcq_questions.append(qus)
        #driver.close()
    

#path=input("Enter File Path where Urls are there:")
#path1=input("Enter File Path where Urls are there:")
#driver_path=input("Enter Path of Chrome Driver .exe file:")
file=open("Story.txt",'r')
urls=file.readlines()
file.close()

for i in urls:
    if i!='\n':
        get_mcq(i.replace('"','').replace(",",""))
#file=open(path1,'w')
#file.write(json.dumps(sample_mcq_questions))
#file.close()
my_collection.insert_many(sample_mcq_questions)
#print(sample_mcq_questions)

