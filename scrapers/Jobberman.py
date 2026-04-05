# -*- coding: utf-8 -*-
"""
Created on Sun Feb  2 14:11:02 2025

@author: Oreoluwa
"""

import requests
from bs4 import BeautifulSoup


search_term = 'Data Scientist'
location = "Nationwide"
base_url = 'https://www.jobberman.com/jobs'


def jobDesc(job_link):
    job_response = requests.get(job_link)
    job_soup = BeautifulSoup(job_response.content,'html.parser')
    
    job_document = job_soup.find('article',class_ = 'job__details')
    
    job_details_div = job_document.find_all("div",class_ = "py-5 px-4 border-b border-gray-300 md:p-5")
    
    
    job_desc = ""
    for div in job_details_div:
        details = div.find_all(["p","li"])
        
        for detail in details:
            job_desc += detail.get_text()
            
    return job_desc



def jobberman(search_term,location):
    url = f'https://www.jobberman.com/jobs?location={location}&q={search_term}'
    
    response = requests.get(url)
    soup = BeautifulSoup(response.content, "html.parser")
    
    document = soup.find("main", class_ = 'min-h-screen main-content')
    jobs = document.find_all("div",class_ = "flex flex-grow-0 flex-shrink-0 w-full")
    
    job_list = []
    job_post = {}
    for job in jobs:
        
        try:
            job_title = job.find_all("p")[0].get_text(separator = " ").strip()
            company = job.find_all("p")[1].get_text(separator = " ").strip()
            
            job_post["Job Title"] = job_title + " at " + company
            
        except:
            continue
        
        try:
            job_link = job.a['href']
            job_post["Job Link"] = job_link
        except:
            continue
        
        try:
            job_post['Job Description'] = jobDesc(job_link)
            
        except:
            continue
        
       
        
        job_post["Job Location"] = location
        
        job_post["Job Mode"] = "Not Specified"
        
        job_post['Source'] = "Jobberman.com"
        
        job_list.append(job_post)
    return job_list
    
 

    
