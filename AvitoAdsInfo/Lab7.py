from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium import webdriver
import time
import os

def browser_options() -> None:
    ''' Установка настроек браузера
    1. Окно во весь экран
    2. User-Agent - Chrome
    '''
    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument("start-maximized")
    chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/106.0.0.0 Safari/537.36")
    return chrome_options

def browser_caps() -> None:
    ''' Установка параметров загрузки страниц
    1. Не дожидаемся полной загрузки страницы
    '''
    caps = DesiredCapabilities().CHROME
    caps["pageLoadStrategy"] = "eager"
    return caps

def search(driver: object) -> None:
    ''' Поиск запроса
    1. Находим поле для ввода
    2. Выполняем поиск
    '''
    SEARCH_TEXT = 'iphone 14'
    SEARCH_BOX = 'downshift-input'

    elem = driver.find_element(By.ID, SEARCH_BOX)
    elem.clear()
    elem.send_keys(SEARCH_TEXT)
    elem.send_keys(Keys.RETURN)

def records_check_page(driver: object, result: list, count: int) -> list:
    ''' Поиск описаний внутри объявлений
    1. Ищем блок с описанием и берем из него текст
    2. Ищем блок с названием и берем из него текст
    3. Ищем блок с ценой и берем из него текст
    4. Формируем запись
    5. Добавляем полученную запись в список объявлений
    '''
    
    AD_NOT_AVAILABLE = "Объявление недоступно"

    records = driver.find_elements(By.CLASS_NAME, "iva-item-titleStep-pdebR")
    
    for record in records:
    
        record.click()
        driver.switch_to.window(driver.window_handles[1])

        try:
            description = driver.find_element(By.XPATH, "//div[@data-marker='item-view/item-description']").text
            name = driver.find_element(By.XPATH, "//span[@data-marker='item-view/title-info']").text
            
            price = driver.find_element(By.XPATH, "//span[@class='js-item-price style-item-price-text-_w822 text-text-LurtD text-size-xxl-UPhmI']").text
        except Exception as es:
            description = name = price = AD_NOT_AVAILABLE

        result.append("\nЗапись №{0}\nНазвание: {1}\nЦена: {2}\nОписание:\n{3}\n\n".format("{0}".format(count + 1), name, price, description))
            
        driver.close()
        driver.switch_to.window(driver.window_handles[0])
    
        count += 1
        time.sleep(1)
        
    return result, count

def write_file(data: list) -> None:
    ''' Запись описаний в файл
    '''
    OUT_FILE_FOLDER = "Открытые информационные системы\\Lab7\\output"
    OUT_FILE_NAME = "output.txt"

    with open(os.path.join(OUT_FILE_FOLDER, OUT_FILE_NAME), 'w+', encoding="utf-8") as f:
        for record in data:
            f.write(record)

def parse_start() -> None:
    ''' Обработка объявлений на страницах
    1. Применяем параметры драйвера
    2. Проходим по странице
    3. Парсим данные с каждой записи на странице
    4. Переходим на следующую страницу
    '''
    DRIVER_PATH = 'Открытые информационные системы\\Lab7\\chromedriver\\chromedriver'
    MAX_PAGE = 1
    result = []
    
    chrome_options = browser_options()
    desired_capabilities = browser_caps()
    
    driver = webdriver.Chrome(executable_path = DRIVER_PATH, chrome_options=chrome_options, desired_capabilities = desired_capabilities)
    driver.get("https://www.avito.ru/")

    search(driver)

    next_button = True
    curr_page = 0
    count = 0

    while (next_button and curr_page < MAX_PAGE):

        result, count = records_check_page(driver, result, count)
        
        color = driver.find_element(By.XPATH, "//span[@data-marker='pagination-button/next']").value_of_css_property('color')
        if (color == 'rgba(0, 156, 240, 1)'):
            driver.find_element(By.XPATH, "//span[@data-marker='pagination-button/next']").click()
            curr_page += 1
        else:
            next_button = False

    write_file(result)
    print("Готово!")

    while(True):    
       pass

if __name__ == '__main__':
    parse_start()