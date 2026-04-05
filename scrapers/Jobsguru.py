# -*- coding: utf-8 -*-
"""
Created on Wed Jan  8 14:23:02 2025

@author: Oreoluwa
"""

#This block of code consists of import statements
import requests
from bs4 import BeautifulSoup
#search_term = input('What role are you looking for? ')


def jobDesc(job_link):
    job_response = requests.get(job_link)
    job_soup = BeautifulSoup(job_response.content,'html.parser')
    job_document = job_soup.find("div",class_ = "main-content-section")
    clearfix = job_document.find("div", class_ = "clearfix")
    
    
    
    job_details = clearfix.find_all(["p","li"])
    
    job_desc = ""
    
    for detail in job_details:
        job_desc += detail.get_text()
    
    return job_desc

#This function scrapes the website "Jobgurus.com" and returns the results
def Jobsguru(search_term):

    
    url = f'https://www.jobgurus.com.ng/jobs?search_keyword={search_term}&specialization=&work_level='
    
    response = requests.get(url)     
    job_list = []
    
    
    #This block of code scrapes the website and finds the Job Title and Job Link of each job
    if response:
           soup = BeautifulSoup(response.content,'html.parser') 
           #document = soup.find("div", class_ = "main-content-section")
           jobs = soup.find_all("div", class_ = "panel-body")
           
          # print(job)
          
           for job in jobs:
               # This creates a dictionary to store job details
               job_post = {} 
               
               try:
                   job_title = job.h2.text.strip()
                   job_post['Job Title'] = job_title
                   
                   job_link = job.a['href'] 
                   job_post['Job Link'] = job_link
                   
                   
               except:
                   continue
               
                #This block of code scrapes the url of each individual job and fetches the Job Location and Job Mode of each job
               job_response = requests.get(job_link)
               if job_response:
                   job_soup = BeautifulSoup(job_response.content, "html.parser")
                   job_doc = job_soup.find("div", class_ = "main-content-section")
                   job_desc = job_doc.find("div", class_ = 'clearfix')
                   job_meta = job_desc.find_all("p")[3].get_text(separator = '')
                   
                   try:
                       job_location = job_meta.split("\n")[0]
                       job_location = job_location.split(":")[-1].strip()
                       job_post['Job Location'] = job_location
                   except:
                       continue     
                   
                   try:
                       job_mode = job_meta.split("\n")[1]
                       job_mode = job_mode.split(":")[-1].strip()
                       job_post['Job Mode'] = job_mode
                       job_post['Job Source'] = 'Jobgurus.com'
                       
                   
                   except:
                       continue
                   
                   try:
                        job_post['Job Description'] = jobDesc(job_link)
                   except:
                       continue
               
                 
               #This block of code appends all the results of a list and returns the list at the end of the loop 
               job_list.append(job_post)
           return job_list
               
    
