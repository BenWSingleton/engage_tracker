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
        #open = project.find('span', class_='open')
        #print(open)
        #if open.text:
        #    status = "Open"
        #else:
        #    status = "Active"
        projects_list.append(
            {"project_name":name,
             "date":        date,
             "link":        link,
             "status":      "temp"
            }
        )
    return pd.DataFrame(projects_list)

def get_projects_from_db():
    connection = sqlite3.connect('tracker.db')
    df = pd.read_sql_query("SELECT * FROM tracker WHERE status != 'Deleted'", connection)
    connection.close()
    return df

def get_updates():
    projects_in_db = get_projects_from_db()
    projects_on_pg = get_current_dates()
    existing = projects_in_db['project_name'].tolist()
    latest = projects_on_pg['project_name'].tolist()
    removed_projects = set(existing).difference(latest)
    new_projects = set(latest).difference(existing)
    temp = pd.merge(projects_on_pg, projects_in_db, on='project_name', suffixes=('_pg', '_db'))
    to_update = temp[temp['date_db'] != temp['date_pg']][['project_name', 'date_pg']]
    for _, row in to_update.iterrows():
        update_project_date(row['project_name'], row['date_pg'])

def execute_query(query, params) -> bool:
    connection = sqlite3.connect('tracker.db')
    cursor = connection.cursor()
    cursor.execute(query, params)
    connection.commit()
    connection.close()
    return True

def insert_new_project(project_name: str, date: str, org: str, status: str) -> bool:
    query = f"""INSERT INTO tracker (project_name,date,org,status) VALUES (?, ?, ?, ?)"""
    params = (project_name, date, org, status)
    return execute_query(query, params)

def update_project_date(project_name: str, date: str) -> bool:
    query = f"""UPDATE tracker date = ? WHERE project_name = ?"""
    params = (date, project_name)
    return execute_query(query, params)

def update_project_status(project_name: str, status: str) -> bool:
    query = f"""UPDATE tracker status = ? WHERE project_name = ?"""
    params = (status, project_name)
    return execute_query(query, params)

def purge_db() -> bool:
    execute_query("DELETE FROM tracker", ())
    execute_query("DELETE FROM sqlite_sequence WHERE name='tracker'", ())
    print("Tracker table successfully purged")
    return True