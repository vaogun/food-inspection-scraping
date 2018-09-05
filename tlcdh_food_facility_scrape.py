"""
Script for scraping Toledo-Lucas County Department of Health food facility
inspection data (rough draft).
"""

from bs4 import BeautifulSoup
from datetime import datetime
import requests
import csv

DATETIME = datetime.now().strftime("%Y-%m-%d-%H-%M-%S")
FACILTIIES_FILE_NAME = 'health_dept_facilites-' + DATETIME + '.csv'
INSPECTIONS_FILE_NAME = 'health_dept_inspections-' + DATETIME + '.csv'
WESBSITE_PREFIX = 'https://healthspace.com'
EXTENDED_PREFIX ='https://healthspace.com/Clients/Ohio/Toledo-Lucas/web.nsf/'
HEALTH_DEPARTMENT_FOOD_FACILITY_LINKS = [
    EXTENDED_PREFIX + 'Food-ByInspectionDate?OpenView&Count=1001',
    EXTENDED_PREFIX + 'Food-ByInspectionDate?OpenView&Count=1000&start=1001',
    EXTENDED_PREFIX + 'Food-ByInspectionDate?OpenView&Count=1000&start=2001'
]

def get_column_headers(dictionary):
    "Returns dictionary keys for use as csv file column headers."
    return dictionary[0].keys()

def get_facilities(links):
    "Returns a list of food inspection facilites."
    food_facilities = []
    for link in links:
        parsed_website = get_parsed_website(link)
        table = parsed_website.find('tbody')
        for table_row in table.find_all('tr'):
            row_data = table_row.find_all('td')
            facility = {}
            facility['FacilityName'] = row_data[0].text
            facility['FacilityLink'] = WESBSITE_PREFIX + get_href(table_row)
            facility['Address'] = row_data[1].text
            facility['LastInspectionDate'] = row_data[2].text
            food_facilities.append(facility)
    return food_facilities

def get_href(table_row):
    "Returns table row's href link."
    return table_row.find('a', href=True)['href']

def get_inspections(links):
    "Returns a list of facility inspections."
    food_inspections = []
    for link in links:
        parsed_website = get_parsed_website(link)
        tables = [table for table in parsed_website.find_all('table')]
        first_table = tables[0].find_all('td')
        second_table = tables[1].find_all('td')
        for table_row in tables[4].find_all('tr'):
            inspection = {}
            row_data = table_row.find_all('td')
            inspection['FacilityName'] = utf8(first_table[1].text)
            inspection['FacilityLocation'] = utf8(first_table[3].text)
            inspection['FacilityType'] = utf8(second_table[1].text)
            inspection['FacilityRiskRating'] = utf8(second_table[3].text)
            inspection['Link'] = utf8(EXTENDED_PREFIX + get_href(table_row))
            inspection['InspectionDate'] = utf8(row_data[1].text[2:])
            inspection['Criticals'] = utf8(row_data[2].text.split('c')[0])
            inspection['NonCriticals'] = utf8(get_non_criticals(row_data))
            inspection['FacilityPhone'] = utf8(second_table[5].text)
            food_inspections.append(inspection)
    return food_inspections

def get_non_criticals(table_row): 
    "Returns number of non-critical inspection violations."
    return table_row[2].text.split('&')[1].split('n')[0]
    
def get_parsed_website(link):
    "Returns parsed html of link."
    return BeautifulSoup(requests.get(link).text, 'lxml')

def utf8(text):
    "Returns utf-8 encoded text."
    return u''.join((text)).encode('utf-8').strip()

def write_dictionaries_to_csv(file_name, dictionaries):
    "Write dictionary to csv file."
    with open(file_name, 'wb') as output:
        dict_writer = csv.DictWriter(output, get_column_headers(dictionaries))
        dict_writer.writeheader()
        dict_writer.writerows(dictionaries)

facilities = get_facilities(HEALTH_DEPARTMENT_FOOD_FACILITY_LINKS)
write_dictionaries_to_csv(FACILTIIES_FILE_NAME, facilities)
inspection_links = [facility['FacilityLink'] for facility in facilities]
inspections = get_inspections(inspection_links)
write_dictionaries_to_csv(INSPECTIONS_FILE_NAME, inspections)
