# -*- coding: utf-8 -*-
"""
Created on Wed Jan  8 13:20:55 2025

@author: Oreoluwa
"""
#This block of code consists of import statements
import requests
from bs4 import BeautifulSoup

#Function to extract the job description of each job
def jobDesc(job_link):
    
    job_response = requests.get(job_link)
    
    job_soup = BeautifulSoup(job_response.content, 'html.parser')
    job_document = job_soup.find("li",class_ = "job-description")
    
    job_info = job_document.find("ul", class_ = "job-key-info")
    
    infos = job_info.find_all("li")
    
    job_key_info = ""
    for info in infos:
        job_key_info += "\n"+ info.get_text()
        
    job_details = job_document.find("div", class_ = "job-details")
    details = job_details.find_all(["p","li"])
    
    key_job_details = ""
    for detail in details:
        key_job_details += "\n" + detail.get_text()
    
    job_desc = job_key_info + key_job_details
    return job_desc


#This function scrapes the website "MyJobMag.com" and returns the results
def MyJobMag(search_term,location):
    base_url = 'https://www.myjobmag.com/'
    url = f'https://www.myjobmag.com/search/jobs?q={search_term}&location={location}&location-sinput={location}'
    
    response = requests.get(url)
    job_list = []
    
    
    #This block of code scrapes the website and finds the Job Title, Job Location and Job Link of each job
    if response:
        soup = BeautifulSoup(response.content,'html.parser')
        document = soup.find("div",class_ = 'content-wrap2' )
        jobs = document.find_all("li",class_='job-list-li')
        
        
        for job in jobs:
            # This creates a dictionary to store job details
            job_post = {}
            
            
            try:
                job_title = job.h2.text.strip()
                job_post['Job Title'] = job_title
            except: 
                continue
            try:
                
                job_location = location + ' State'
                job_post['Job Location'] = job_location
            except:
                continue
            try:
                
                job_link =  base_url + job.h2.a['href']
                job_post['Job Link'] = job_link
            except:
                continue
            
            try:
                job_post['Job Description'] = jobDesc(job_link)
            except:
                continue
            
            #This block of code scrapes each individual job's url and finds the mode of each job
            try:
                job_response = requests.get(job_link)
                job_doc = BeautifulSoup(job_response.content,"html.parser")
                job_doc = job_doc.find("div",class_ ="read-left-section")
                job_desc = job_doc.find("ul", class_ = "job-key-info")
                job_type = job_desc.find("li")
                job_type = job_type.find("span", class_ = "jkey-info")
                job_type = job_type.text
                
                
                job_post['Job Mode'] = job_type
                
            except:
                job_post['Job Mode'] = "Not Specified"
            
            job_post['Job Source'] = "MyJobMag.com"
            
                
            #This block of code appends all the results of a list and returns the list at the end of the loop
            job_list.append(job_post)
        return job_list
        
       