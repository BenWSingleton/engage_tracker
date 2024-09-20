from bs4 import BeautifulSoup
import requests
import sqlite3
import pandas as pd

def get_current_dates():
    engage_list = requests.get('https://engage.pittsburghpa.gov/projects').content
    soup = BeautifulSoup(engage_list, 'lxml')
    projects = soup.find_all("article", class_="h-entry")
    projects_list = []
    for project in projects:
        name = project.find('h4', class_='p-name').text
        date = project.find('time', class_='dt-updated').text
        link = project.find('a')['href']
        projects_list.append(
            {"project_name":name,
             "date":        date,
             "link":        link}
        )
    return pd.DataFrame(projects_list)

def get_projects_from_db():
    connection = sqlite3.connect('tracker.db')
    df = pd.read_sql_query("SELECT * FROM tracker", connection)
    connection.close()
    return df

def get_updates():
    return

def insert_new_project(project_name, date, org):
    connection = sqlite3.connect('tracker.db')
    cursor = connection.cursor()
    query = f"""INSERT INTO tracker (project_name,date,org) VALUES ('{project_name}', '{date}', '{org}')"""
    cursor.execute(query)
    connection.commit()
    connection.close()

def update_project_date(project_name, date):
    connection = sqlite3.connect('tracker.db')
    cursor = connection.cursor()
    query = f"""UPDATE tracker
    date = {date}
    WHERE project_name = {project_name}
    """

def purge_db():
    connection = sqlite3.connect('tracker.db')
    cursor = connection.cursor()
    query = "DELETE FROM tracker"
    cursor.execute(query)
    connection.commit()
    connection.close()
    return "Tracker table successfully purged"

#insert_new_project('test1', 'test2', 'test3')

print(get_projects_from_db())