from asyncore import write
import re
import os

def authors_edit(info):
    ''' Форматирование поля "Author"
    1. Заменяем лишние , на пробел
    2. Убираем лишние пробелы и переносы строк
    3. Заменяем and на ,
    4. Убираем точку в конце строки
    '''
    #info = re.sub(r"\,", " ", info)
    info = re.sub(r" +|\n", " ", info)
    info = re.sub(r"[.|,| ]and[.|,| ]", ", ", info)
    info = info.strip()

    if (info[-1] == "."):
        info = info[:-1]
    
    return info

def lang_format_data(lang, rus, eng, info):
    ''' В зависимости от языка форматируем поля
    '''
    if (lang == "russian"):
        info = "{0} {1}".format(rus, info)
    else:
        info = "{0} {1}".format(eng, info)
    
    return info

def edit_data(title, info, lang, mark, length):
    ''' Форматирование полей
    1. Обрезаем пробелы вначале и в конце
    3. Убираем точку в конце строки
    и переносы строк
    4. Форматируем поле File
    '''
    ext = ""
    result = ""

    info = info.strip()

    if (title == "Author"):
        info = authors_edit(info)
    
    if (title == "Volume"):
        info = lang_format_data(lang, "Том", "Vol.", info)
    
    if (title == "Pages" or title == "Numpages"):
        info = lang_format_data(lang, "С.", "P.", info)
    
    if (title == "Journal" or title == "Type"):
        ext = " "

    if (info[len(info)-1] == "."):
        info = info[:-1]
      
    info = info.replace("\n", " ")

    if (title == "File"):    
        files = re.findall(r'\:([^;]*?)\.', info)
        info = "DOI: {0}".format(', '.join(files))

    if (length == 0):
        result = info
    else:
        result = "{0}{1} {2}".format(ext, mark, info)
  
    return result

def language(book):
    ''' Получаем язык записи (если есть)
    1. Ищем язык в записи
    2. Выбираем язык из записи
    '''
    lang = list(filter(lambda x: x[0] == 'Language', book))

    if (len(lang) != 0):
        lang = lang[0][1]

    return lang

def data_sort(book, data, marks):
    ''' Форматируем поля записи
    1. Запись полей в нужном порядке
    '''
    result = ""
    count = 0
    
    lang = language(book)

    while (count < len(data)):             
        info = list(filter(lambda x: x[0] == data[count], book))

        if (info):
            result += edit_data(data[count], info[0][1], lang, marks[count], len(result))
        count += 1

    result = result.strip()
    if len(result):
        result = "{0}{1}".format(result, "\n")

    return result

def read_lib():
    ''' Установка последовательности полей
    1. Считываем из файла данные
    2. Делим на поля и их разделители
    '''
    FILE_LIB_PATH = "Lab5\lib"
    FILE_LIB_NAME = "lib.txt"

    with open(os.path.join(FILE_LIB_PATH, FILE_LIB_NAME), 'r') as f:
        text = f.read().split("\n")

    data = []
    marks = []
    for elems in text:
        data.append(elems.split(" ")[0])
        marks.append(elems.split(" ")[1])

    return data, marks

def write_file(data):
    ''' Запись готовых данных в файл
    1. Сортировка полей записи
    2. Запись готовой строки в файл
    '''
    OUT_FILE_FOLDER = "Lab5\output"
    OUT_FILE_NAME = "output.txt"
    
    type, marks = read_lib()

    book_info = ""
    with open(os.path.join(OUT_FILE_FOLDER, OUT_FILE_NAME), 'w+', encoding="utf-8") as f:
        for book in data:
            book_info = data_sort(book, type, marks)
            f.write(book_info)          

def recognize_data(data):
    ''' Выделение данных из каждый записи
    1. Получаем все поля записи в виде списка
    '''
    result = []

    for file in data:
        for field in file:
            result.append(re.findall(r'.*?(\S+) .*?=.*?{([\s\S|.*?]*?)}', field))
    
    return result

def read_file():
    ''' Чтение данных из файла
    1. Читаем весь файл целиком
    2. Разбиваем его по записям
    '''
    BIB_FILE_PATH = "Lab5\data"
    data = []   

    for filename in os.listdir(BIB_FILE_PATH):
        with open(os.path.join(BIB_FILE_PATH, filename), 'r', encoding="utf-8") as f:
            data = re.findall(r'@(.*?){.*?,[\s\S]([\s\S|.*?]*?})[\n]', f.read())

    return data

def main():
    ''' Главная функция
    1. Читаем файл bib
    2. Распознаем в нем данные
    3. Пишем их в файл в нужном порядке
    '''
    data = read_file()
    data = recognize_data(data)
    write_file(data)

main()