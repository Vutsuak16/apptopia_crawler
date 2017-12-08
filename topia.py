import requests
from bs4 import BeautifulSoup
from lxml import html
import pandas as pd
#from urllib.request import urlretrieve
import shutil


USERNAME = "xxxxxx"
PASSWORD = "xxxxx"

LOGIN_URL = "https://apptopia.com/users/sign_in"

itunes_dict={"app_id":[],"dau":[],"mau":[],"eng":[],"about":[],"total_downloads":[],"revenue":[]}
android_dict={"app_id":[],"dau":[],"mau":[],"eng":[],"about":[],"total_downloads":[],"revenue":[]}


def main():

    session_requests = requests.session()

    result = session_requests.get(LOGIN_URL)

    tree = html.fromstring(result.text)
    authenticity_token = list(set(tree.xpath("//input[@name='authenticity_token']/@value")))[0]
    

    # Create payload
    payload = {
            "user[email]": USERNAME, 
            "user[password]": PASSWORD,
            "authenticity_token":authenticity_token
            }

    # Perform login
    login = session_requests.post(LOGIN_URL, data = payload, headers = dict(referer = LOGIN_URL))


    df_itunes_ids=pd.read_excel("about_data.xlsx",error_bad_lines=False)["IOS_App_ID"]
    df_itunes_ids=df_itunes_ids.dropna(axis=0,how="all")
   

    for i in df_itunes_ids:

        g=open("performance/itunes/"+(str(int(i))+".csv"),'wb')
        URL_USAGE= "https://apptopia.com/apps/itunes_connect/"+str(int(i))+"/usage"
        URL_ABOUT =  "https://apptopia.com/apps/itunes_connect/"+str(int(i))+"/about"
        URL_DOWNLOADS_REVENUES="https://apptopia.com/apps/itunes_connect/"+str(int(i))+"/downloads_and_revenue"
        
        itunes_dict["app_id"].append(i)

        r = session_requests.get(URL_USAGE, headers = dict(referer = URL_USAGE))
        soup = BeautifulSoup(r.content, 'html.parser')

        try:
            itunes_dict["dau"].append(soup.find("div","total-dau text-xxxl text-light").text)
            itunes_dict["mau"].append(soup.find("div","total-mau text-xxxl text-light").text)
            itunes_dict["eng"].append(soup.find("div","total-eng text-xxxl text-light").text)
        
        except:
            pass
        
       
        r = session_requests.get(URL_DOWNLOADS_REVENUES, headers = dict(referer = URL_DOWNLOADS_REVENUES))
        soup = BeautifulSoup(r.content, 'html.parser')
        
        try:

            itunes_dict["total_downloads"].append(soup.find("div","total-dls text-xxxl text-light").text)
            itunes_dict["revenue"].append(soup.find("div","bg-gray text-xxs-center m-t-xs m-b-0").text)
            
        except:
            pass



        about=""
        r = session_requests.get(URL_ABOUT, headers = dict(referer = URL_ABOUT))
        soup = BeautifulSoup(r.content, 'html.parser')

        try:
            for node in soup.find_all("div", "app-description text-xs m-b-xs"):
                about = ''.join(node.findAll(text=True))
            itunes_dict["about"].append(about)
        except:
            pass

     

        

    df_itunes=pd.DataFrame(dict([ (k,pd.Series(v)) for k,v in itunes_dict.items() ]))
    df_itunes.to_csv("itunes.csv",sep=",")
main()