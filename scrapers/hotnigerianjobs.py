# -*- coding: utf-8 -*-
from bs4 import BeautifulSoup
import requests
import re
from datetime import datetime

# Function to extract the job description for each job
def jobDesc(job_link):
    try:
        job_response = requests.get(job_link, timeout=10)
        job_soup = BeautifulSoup(job_response.content, 'html.parser')
        document = job_soup.find("div", class_="mycase")
        if not document: return "Description not available."
        
        content = document.find("div", class_="mycase4")
        if not content: return "Description not available."
        
        texts = content.find_all(["p", "li"])
        return "".join([text.get_text() for text in texts])
    except:
        return "Description not available."

# Improved date conversion using a dictionary for speed and safety
def date_conversion(date_str):
    months = {
        "january": "01", "february": "02", "march": "03", "april": "04",
        "may": "05", "june": "06", "july": "07", "august": "08",
        "september": "09", "october": "10", "november": "11", "december": "12"
    }
    try:
        # Expected format: "17th April 2026,"
        parts = date_str.strip().replace(",", "").split(" ")
        day = parts[0][:-2] # Removes 'st', 'nd', 'rd', 'th'
        month_name = parts[1].lower()
        year = parts[2]

        month = months.get(month_name)
        if not month: return "Wrong"
        
        formatted_str = f"{day}/{month}/{year}"
        return datetime.strptime(formatted_str, "%d/%m/%Y")
    except:
        return "Wrong"

def hotnigerianjobs(search_term):
    url = f"https://www.hotnigerianjobs.com/index.php?qid={search_term}"
    
    try:
        response = requests.get(url, timeout=15)
        if not response: return []
    except:
        return []

    def extract_text(text):
        pattern = r"is located in (.*?) State"
        match = re.search(pattern, text)
        return f"{match.group(1)} State" if match else "Location Not Available."

    job_list = []
    soup = BeautifulSoup(response.content, 'html.parser')
    wrapper = soup.find("div", class_="wrapper")
    if not wrapper: return []
    
    jobs = wrapper.find_all("div", class_="mycase")
    
    for job in jobs:
        job_post = {}
        
        try:
            # 1. Title
            job_post['Job Title'] = job.h1.text.strip() if job.h1 else "No Title"
            
            # 2. Link - Adding index check to prevent IndexError
            spans = job.find_all("span", class_="semibio")
            if len(spans) > 1 and spans[1].a:
                job_link = spans[1].a['href']
                job_post['Job Link'] = job_link
            else:
                continue # Skip if no link found

            # 3. Location & Description
            job_desc_div = job.find("div", class_='mycase4')
            job_post['Job Location'] = extract_text(job_desc_div.text) if job_desc_div else "Not Specified"
            job_post['Job Description'] = jobDesc(job_link)
            
            # 4. Employment Type (THE FIX FOR THE CRASH)
            job_response = requests.get(job_link, timeout=10)
            job_soup = BeautifulSoup(job_response.content, 'html.parser')
            
            # Get the second to last mycase4 div
            detail_containers = job_soup.find_all("div", class_="mycase4")
            if len(detail_containers) >= 2:
                job_document = detail_containers[-2]
                
                # SAFE ACCESS: Check if divs exist before indexing [1]
                inner_divs = job_document.find_all("div")
                if len(inner_divs) > 1:
                    # Check nested divs for index [1]
                    nested_divs = inner_divs[1].find_all("div")
                    raw_text = nested_divs[1].text if len(nested_divs) > 1 else inner_divs[1].text
                    
                    match = re.search(r"Employment Type:\s*(.+)", raw_text)
                    job_post['Job Mode'] = match.group(1).strip() if match else "Not Specified"
                else:
                    job_post['Job Mode'] = "Not Specified"

                # 5. Application Closing Date
                date_divs = job_document.find_all("div")
                if len(date_divs) >= 2:
                    date_text_parts = date_divs[-2].text.split("\n")
                    if len(date_text_parts) > 1:
                        closing_date = date_text_parts[1].strip()
                        
                        if closing_date != "Not Specified":
                            converted = date_conversion(closing_date)
                            if converted != "Wrong" and converted < datetime.now():
                                continue # Skip outdated jobs
                            job_post['Application Closing Date'] = closing_date

            job_post['Job Source'] = "hotnigerianjobs.com"
            job_list.append(job_post)

        except Exception as e:
            print(f"Skipping a job due to error: {e}")
            continue
            
    return job_list
