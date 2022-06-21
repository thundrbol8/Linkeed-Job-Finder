from django.http import HttpResponse
from django.shortcuts import render

import csv
from datetime import datetime
import requests
from bs4 import BeautifulSoup
import json


def homepage(request):
    return render(request, 'index.html')


def get_url(position, location):
    
    template = 'https://in.indeed.com/jobs?q={}&l={}'
    position = position.replace(' ', '+')
    location = location.replace(' ', '+')
    url = template.format(position, location)
    return url

def get_record(card):
    
    job_title = card.h2.a.span.get('title')
    company_name = card.find('span', 'companyName').text.strip()
    job_location = card.find('div', 'companyLocation').text.strip()
    date_posted = card.find('span' , 'date').text.strip()
    job_url = "https://in.indeed.com" + card.h2.a.get('href')
    
    if date_posted[0] == 'P':
        date_posted = date_posted[:6] + " " + date_posted[6:]
        
    else:
        date_posted = "Posted" + date_posted[14:]
        
    record = (job_title , company_name , job_location , date_posted , job_url)
    return record


def jobs(request):
    """Run the main program routine"""
    position = request.POST.get('profile')
    location = request.POST.get('location')
    
    indeed_jobs = []
    linkedin_jobs = []
    url = get_url(position , location)
    
    # extract the job data
    while True:
        response = requests.get(url)
        soup = BeautifulSoup(response.text, 'html.parser')
        cards = soup.find_all('div', 'job_seen_beacon')
        for card in cards:
            job_record = get_record(card)
            indeed_jobs.append(job_record)
        try:
            url = 'https://www.indeed.com' + soup.find('a', {'aria-label': 'Next'}).get('href')
        except AttributeError:
            break 
    
    url = "https://linkedin-jobs-search.p.rapidapi.com/"

    payload = {
        "search_terms": str(position),
        "location": str(location),
        "page": "1",
        "fetch_full_text": "yes"
    }
    headers = {
        "content-type": "application/json",
        "X-RapidAPI-Key": "535f89e2b6msh0fab4aaec2b0d77p1b9efajsncc9decb0b138",
        "X-RapidAPI-Host": "linkedin-jobs-search.p.rapidapi.com"
    }

    response = requests.request("POST", url, json=payload, headers=headers)

    json_data = json.loads(response.text)

    for rows in json_data:
        job_record = (rows['job_title'] , rows['company_name'] , rows['job_location'] , rows['posted_date'] , rows['job_url'])
        linkedin_jobs.append(job_record);

    result = {'indeed' : indeed_jobs , 'linkedin' : linkedin_jobs}

    return render(request , 'jobLists.html' , result)

