import sqlite3
import re
import os

def read_file() -> list:
    ''' Чтение данных из файла
    1. Читаем весь файл целиком
    2. Разбиваем его по записям
    '''
    BIB_FILE_PATH = "Lab6\data"
    data = []   

    for filename in os.listdir(BIB_FILE_PATH):
        with open(os.path.join(BIB_FILE_PATH, filename), 'r', encoding="utf-8") as f:
            data = re.findall(r'@(.*?){.*?,[\s\S]([\s\S|.*?]*?})[\n]', f.read())

    return data

def recognize_data(data: list) -> list:
    ''' Выделение данных из каждый записи
    1. Получаем все поля записи в виде списка
    '''
    result = []

    for file in data:
        for field in file:
            result.append(re.findall(r'.*?(\S+) .*?=.*?{([\s\S|.*?]*?)}', field))
    
    return result

def read_lib() -> list:
    ''' Установка последовательности полей
    1. Считываем из файла данные
    2. Делим на поля и их разделители
    '''
    FILE_LIB_PATH = "Lab5\lib"
    FILE_LIB_NAME = "lib.txt"

    with open(os.path.join(FILE_LIB_PATH, FILE_LIB_NAME), 'r') as f:
        text = f.read().split("\n")

    data = []
    for elems in text:
        data.append(elems.split(" ")[0])

    return data

def authors_edit(info: str) -> str:
    ''' Форматирование поля "Author"
    1. Заменяем лишние , на пробел
    2. Убираем лишние пробелы и переносы строк
    3. Заменяем and на ,
    4. Убираем точку в конце строки
    '''
    info = re.sub(r"\,", " ", info)
    info = re.sub(r"\n", " ", info)
    info = re.sub(r" +", " ", info)
    info = re.sub(r"[.|,| ]and[.|,| ]", ", ", info)
    info = re.sub(r" +", " ", info)
    info = re.sub("\.\s", ".", info)
    info = info.strip()
    
    return info

def edit_data(title: str, info: str) -> str:
    ''' Форматирование полей
    1. Обрезаем пробелы вначале и в конце
    3. Убираем точку в конце строки
    и переносы строк
    4. Форматируем поле File
    '''
    info = info.strip()

    if (title == "Author"):
        info = authors_edit(info)
      
    info = info.replace("\n", " ")

    if (title == "File"):    
        files = re.findall(r'\:([^;]*?)\.', info)
        info = "DOI: {0}".format(', '.join(files))
  
    return info

def data_sort(book: list, data: list) -> tuple:
    ''' Форматируем поля записи
    1. Запись полей в нужном порядке
    '''
    result = []
    count = 0

    while (count < len(data)):             
        info = list(filter(lambda x: x[0] == data[count], book))

        if (info):
            result.append(edit_data(data[count], info[0][1]))
        else:
            result.append("-")
        count += 1

    res_tuple = tuple(result)

    if (res_tuple[0] == "-"):
        res_tuple = ""

    return res_tuple

def format_data(data: list) -> list:
    ''' Форматирование записей
    1. Сортировка полей записи
    2. Создание списка записей
    '''
    type = read_lib()

    book_info = []
    for book in data:
        info = data_sort(book, type)

        if (info != ""):
            book_info.append(info)
    
    return book_info

def fill_author_table(db: object, sql: object, data: list):
    ''' Заполнение таблицы "Авторы"
    1. Получение авторов из записей
    2. Сортировка авторов
    3. Добавляем авторов в таблицу, 
    если они там отсуствуют
    '''
    authors = []
    for record in data:
        author_ = record[0].split(", ")

        for i in author_:
            if (None, i) not in authors and i != 'др.':
                authors.append((None, i))

    authors.sort()
    
    for name in authors:
        sql.execute(f"SELECT name FROM author WHERE name = '{name[1]}'")
        if (sql.fetchone() is None):
            sql.execute(f"INSERT INTO author VALUES (?, ?)", name)
            db.commit()

def create_author_table(db: object, sql: object, data: list):
    ''' Инициализация таблицы "Авторы"
    1. Создаем таблицу "Авторы", еслм она отсутствует
    2. Заполняем ее данными из bib файла
    '''
    
    sql.execute("""CREATE TABLE IF NOT EXISTS author (
            id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
            name TEXT NOT NULL
        )""")

    db.commit()

    fill_author_table(db, sql, data)

def fill_journal_table(db: object, sql: object, data: list):
    '''Заполнение таблицы "Журналы"
    1. Получение журналов из записей
    2. Сортировка журналов
    3. Добавляем журналы в таблицу, 
    если они там отсуствуют 
    '''
    journals = []
    for record in data:
        if record[5] not in journals: #and record[5] != "-":
            journals.append(record[5])

    journals.sort()
       
    for name in journals:
        sql.execute(f"SELECT name FROM journal WHERE name = '{name}'")
        if (sql.fetchone() is None):
            sql.execute(f"INSERT INTO journal VALUES (?, ?)", (None, name))
            db.commit()

def create_journal_table(db: object, sql: object, data: list):
    ''' Инициализация таблицы "Журналы"
    1. Создание таблицы "Журналы", 
    если она отсуствует
    2. Заполняем ее данными из bib файла
    '''
    sql.execute("""CREATE TABLE IF NOT EXISTS journal (
            id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
            name TEXT NOT NULL
        )""")

    db.commit()

    fill_journal_table(db, sql, data)
    
def fill_article_table(db: object, sql: object, data: list):
    result = []
    count = 0

    for record in data:
        author_ = record[0].split(", ")
        rec = list(record)[3:]
        rec.pop(2)
        articl_name = 0

        authors = []

        for i in author_:           
            auth = sql.execute(f"SELECT * FROM author WHERE name = '{i}'").fetchone()
            if auth is not None:
                authors.append(auth[0])

        journal_id = sql.execute(f"SELECT * FROM journal WHERE name = '{record[5]}'").fetchone()
        if journal_id is None:
            journal_id = "-"
        else:
            journal_id = journal_id[0]

        articl_name = record[1]
        if (record[1] == ""):
            articl_name = record[2]
        
        for z in authors:
            result.append(tuple([None, count, articl_name, journal_id, z] + rec))
        
        count += 1
    
    sql.executemany(f"INSERT INTO article VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", result)
    db.commit()
    # (None, count, title/booktitle id, author id, type, editor...)

def create_article_table(db: object, sql: object, data: list):
    ''' Инициализация таблицы "Статьи"
    1. Создание таблицы "Статьи", если она отсуствует
    2. Заполняем ее данными из bib файла
    '''
    sql.execute("""drop table if exists article""")
    db.commit()

    sql.execute("""CREATE TABLE IF NOT EXISTS article (
            num INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
            article_id INTEGER NOT NULL,
            article_name TEXT NOT NULL,
            journal_id INTEGER NOT NULL,
            author_id INTEGER NOT NULL,
            type TEXT NOT NULL,
            editor TEXT NOT NULL,
            number TEXT NOT NULL,
            edition TEXT NOT NULL,
            address TEXT NOT NULL,
            publisher TEXT NOT NULL,
            school TEXT NOT NULL,
            year TEXT NOT NULL,
            volume TEXT NOT NULL,
            chapter TEXT NOT NULL,
            pages TEXT NOT NULL,
            numpages TEXT NOT NULL,
            series TEXT NOT NULL,
            note TEXT NOT NULL,
            nite TEXT NOT NULL,
            file TEXT NOT NULL,
            addendum TEXT NOT NULL,
            FOREIGN KEY (journal_id) REFERENCES journal (id)
                ON DELETE CASCADE ON UPDATE NO ACTION,
            FOREIGN KEY (author_id) REFERENCES author (id)
                ON DELETE CASCADE ON UPDATE NO ACTION
        )""")

    db.commit()

    fill_article_table(db, sql, data)

def request_db(sql: object):
    ''' Запрос в базу
    1. Получаем исходные данные
    2. Делаем запрос
    3. Выводим результат
    '''
    print("\n_______Запрос_______")
    print("Введите автора: ", sep = '', end = '')
    author_ = input()

    print("Введите журнал: ", sep = '', end = '')
    journal_ = input()   

    print("Введите год: ", sep = '', end = '')
    year_ = input()
    
    request_ = sql.execute(f"SELECT article_name FROM article "
                           f"JOIN author ON author.id = article.author_id "
                           f"JOIN journal ON journal.id = article.journal_id "
                           f"WHERE author.name = '{author_}' "
                           f"AND journal.name = '{journal_}' "
                           f"AND article.year = '{year_}'").fetchall()

    print("\nРезультат:")

    if len(request_) != 0:
        [print("{0}{1}".format("\t", i[0])) for i in request_]
    else:
        print("\tЖаль, но нам не удалось ничего найти по вашему запросу =(")

def database(data: list):
    ''' Работа с базой
    1. Создаем базу, если она отсуствует
    2. Подключаемся к базе
    3. Создаем и заполняем таблицы
    4. Выполняем запрос к базе
    '''
    DATABASE_PATH = 'Lab6\database\info.db'
    
    with sqlite3.connect(DATABASE_PATH) as db:
        sql = db.cursor()
        sql.execute('pragma encoding=UTF8')

        create_author_table(db, sql, data)
        create_journal_table(db, sql, data)
        create_article_table(db, sql, data)

        request_db(sql)
                
def main():
    ''' Главная функция
    1. Читаем файл bib
    2. Распознаем в нем данные
    3. Пишем их в файл в нужном порядке
    '''
    data = read_file()
    data = recognize_data(data)
    data = format_data(data)
    database(data)

main()