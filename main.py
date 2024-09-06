from bs4 import BeautifulSoup
import requests
from typing import NamedTuple
import sqlite3


class Professor(NamedTuple):
    name: str
    avatar: str
    objectivity: float = 1.0
    loyalty: float = 1.0
    professionalism: float = 1.0
    harshness: float = 1.0


class DatabaseManager:
    def __init__(self, file_name: str):
        self.connection = sqlite3.connect(file_name)
        self.cursor = self.connection.cursor()
        self.cursor.execute("DROP TABLE IF EXISTS Professors")
        self.cursor.execute("""CREATE TABLE IF NOT EXISTS Professors (
                            id INTEGER PRIMARY KEY, 
                            name TEXT NOT NULL,
                            avatar TEXT NOT NULL,
                            objectivity INTEGER NOT NULL,
                            loyalty INTEGER NOT NULL,
                            professionalism INTEGER NOT NULL,
                            harshness INTEGER NOT NULL
                            )""")

    def write_to_db(self, professor_data: Professor):
        self.cursor.execute("""
            INSERT INTO Professors (name, avatar, objectivity, loyalty, professionalism, harshness)
            VALUES (?, ?, ?, ?, ?, ?)""", 
            (professor_data.name,professor_data.avatar,professor_data.objectivity,
             professor_data.loyalty,professor_data.professionalism,professor_data.harshness)
        )
        self.connection.commit()


manager = DatabaseManager('db.sqlite')

first_page_link = 'https://www.spbstu.ru/university/about-the-university/staff/'
links = [first_page_link]

r = requests.get(first_page_link)
soup = BeautifulSoup(r.text, "html.parser")

pages_ul = soup.find("ul", class_="pagination")
last_page = 0
pages_li = list(pages_ul.descendants)
for li_tag in range(2, len(pages_li), 2):
    try:
        last_page = int(pages_li[li_tag].text)
    except ValueError:
        pass

for i in range(2, last_page + 1):
    links.append("https://www.spbstu.ru/university/about-the-university/staff/?arrFilter_ff%5BNAME%5D=&" +
                 "arrFilter_pf%5BPOSITION%5D=&arrFilter_pf%5BSCIENCE_TITLE%5D=&arrFilter_pf%5BSECTION_ID_1%5D=849&" +
                 "arrFilter_pf%5BSECTION_ID_2%5D=&arrFilter_pf%5BSECTION_ID_3%5D=&" +
                 f"del_filter=%D0%A1%D0%B1%D1%80%D0%BE%D1%81%D0%B8%D1%82%D1%8C&PAGEN_1={i}&SIZEN_1=20"
                 )


def simple_parce(tag, tag_class):
    arr = []
    parce_tag_lines = soup.find_all(tag, class_=tag_class)
    for element in parce_tag_lines:
        arr.append(element)
    return arr


for link in links:
    r = requests.get(link)
    r.encoding = 'utf-8'
    soup = BeautifulSoup(r.text, "html.parser")

    parce_tag_names = simple_parce('div', 'col-sm-9 col-md-10')
    parce_tag_images = simple_parce('div', 'col-sm-3 col-md-2')
    for professor in range(len(parce_tag_names)):
        professors_name = parce_tag_names[professor].h3.a.text
        professors_avatar = 'https://www.spbstu.ru' + parce_tag_images[professor].img['src']
        manager.write_to_db(Professor(name=professors_name, avatar=professors_avatar))
