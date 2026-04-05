# -*- coding: utf-8 -*-
"""
Created on Mon Jan  6 12:07:12 2025

@author: Oreoluwa
"""

#Import dependencies
import requests
from bs4 import BeautifulSoup



#title = input("What job are you looking for? ")  # Job title
#location = input("Where do you want to work? ")  # Job location

#Function to extract the job description for each job
def jobDesc(job_link):
    job_response = requests.get(job_link)
    job_soup = BeautifulSoup(job_response.content,'html.parser')
    
    job_document = job_soup.find("div",class_ = "show-more-less-html__markup show-more-less-html__markup--clamp-after-5 relative overflow-hidden")
    
    job_details = job_document.find_all(["","p","li"])
    
    
    job_desc = ""
    for detail in job_details:
        job_desc += detail.get_text()
        
    return job_desc
    

def linkedln(title,location):
    start = 0  # Starting point for pagination
    
    # Construct the URL for LinkedIn job search
    list_url = f"https://www.linkedin.com/jobs-guest/jobs/api/seeMoreJobPostings/search?keywords={title}&location={location}&start={start}"
    
    # Send a GET request to the URL and store the response
    response = requests.get(list_url)
    
    #This block of code gets the HTML, parses the response and finds all list items(jobs postings)
    list_data = response.text
    list_soup = BeautifulSoup(list_data, "html.parser")
    page_jobs = list_soup.find_all("li")
        
        
    #Create an empty list to store the job postings
    id_list = []
    
    #This block of code iterates through job postings to find job ids
    try:
        for job in page_jobs:
            base_card_div = job.find("div", {"class": "base-card"})
            job_id = base_card_div.get("data-entity-urn").split(":")[3]
            id_list.append(job_id)
    except:
        pass
        
        
    # Initialize an empty list to store job information
    job_list = []
    
    # This block of code loops through the list of job IDs and gets each URL
    for job_id in id_list:
        
        # This constructs the URL for each job using the job ID
        job_url = f"https://www.linkedin.com/jobs-guest/jobs/api/jobPosting/{job_id}"
        temp_job_url = f"https://www.linkedin.com/jobs/search/?currentJobId={job_id}"
        
        # This sends a GET request to the job URL and parse the reponse
        job_response = requests.get(job_url)
        job_soup = BeautifulSoup(job_response.text, "html.parser")
        
         # This creates a dictionary to store job details
        job_post = {}
        
        # Try to extract and store the job title
        try:
            job_post["Job Title"] = job_soup.find("h2", {"class":"top-card-layout__title font-sans text-lg papabear:text-xl font-bold leading-open text-color-text mb-0 topcard__title"}).text.strip() + " at " + job_soup.find("a", {"class": "topcard__org-name-link topcard__flavor--black-link"}).text.strip()
        except:
            continue
            
        
       
        # This block of code tries to extract and store the number of applicants
        try:
            job_post["Job Location"] = location
        except:
            continue
            
            
        try:
            job_post["Job Link"] = temp_job_url
        except:
            continue
        
        
        try:
            job_post['Job Description'] = jobDesc(job_url)
        except:
            continue
        
        job_post['Job_Mode'] = "Not Specified"
        job_post['Job Source'] = "LinkedIn.com"  
        #This block of code appends all the results of a list and returns the list at the end of the loop
        job_list.append(job_post)
    return job_list
        
