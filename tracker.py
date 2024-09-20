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

def execute_query(query, params) -> bool:
    connection = sqlite3.connect('tracker.db')
    cursor = connection.cursor()
    cursor.execute(query, params)
    connection.commit()
    connection.close()
    return True

def insert_new_project(project_name: str, date: str, org: str) -> bool:
    query = f"""INSERT INTO tracker (project_name,date,org) VALUES (?, ?, ?)"""
    params = (project_name, date, org)
    return execute_query(query, params)

def update_project_date(project_name: str, date: str) -> bool:
    query = f"""UPDATE tracker date = ? WHERE project_name = ?"""
    params = (query, (date, project_name))
    return execute_query(query, params)

def purge_db() -> bool:
    execute_query("DELETE FROM tracker", ())
    execute_query("DELETE FROM sqlite_sequence WHERE name='tracker'", ())
    print("Tracker table successfully purged")
    return True