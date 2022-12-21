from filemime import filemime
from config import token
import requests
import vk_api
import os

def get_info(session, field, val, info):
    ''' Получение заданной информации о себе
    через токен
    '''
    onwer_id = session.method("users.get", {field: val})[0][info]

    return onwer_id

def load_image(vk, owner_id, filepath):
    ''' Загрузка картинок для поста
    1. Подключаемся к серверу загрузок
    2. Загружаем картинку
    3. Получаем ее метаданные
    '''
    destination = vk.photos.getWallUploadServer()
    meta_data  = requests.post(destination['upload_url'], files={'photo': open(filepath, 'rb')}).json()
    photo = vk.photos.saveWallPhoto(user_id = owner_id, **meta_data )[0]

    return photo

def load_file(vk, filepath, filename):
    ''' Загрузка файла для поста
    1. Подключаемся к серверу загрузок
    2. Загружаем файл
    3. Получаем его метаданные
    '''
    destination = vk.docs.getWallUploadServer()
    meta_data = requests.post(destination['upload_url'], files={'file': open(filepath, 'rb')}).json()
    doc = vk.docs.save(file = meta_data['file'], title=filename, tags=[])

    return doc

def load_attachment(vk, owner_id):
    ''' Загрузка вложения для поста
    1. Определяем тип каждого файла
    2. В зависимости от типа загружаем его 
    на сервер и добавляем в список загруженных

    '''
    ATTACHMENTS_FOLDER = "Lab4\\data\\"

    fileObj = filemime()
    attachments = []

    for filename in os.listdir(ATTACHMENTS_FOLDER):

        filepath = '{0}{1}'.format(ATTACHMENTS_FOLDER, filename)
        file_type = fileObj.load_file(filepath, mimeType = True).split('/')[0]

        if (file_type == 'image'):
            loaded_image = load_image(vk, owner_id, filepath)
            attachments.append('photo{0}_{1}'.format(str(loaded_image['owner_id']), str(loaded_image['id'])))

        else: 
            loaded_file = load_file(vk, filepath, filename)
            attachments.append('doc{0}_{1}'.format(str(loaded_file['doc']['owner_id']), str(loaded_file['doc']['id'])))

    return attachments

def wall_post(vk, owner_id):
    ''' Публикация поста на своей стене
    1. Получаем список прикрепленных файлов
    2. Публикуем пост
    '''
    MESSAGE = "Hello World!"
    FRIENDS_ONLY = 1
    
    attachments = load_attachment(vk, owner_id)

    vk.wall.post(owner_id = owner_id, 
                      friends_only = FRIENDS_ONLY, 
                      message = MESSAGE,
                      attachments = attachments)

def get_friends(session, owner_id):
    ''' Получение своего списка друзей
    1. Получаем список id всех друзей
    2. С помощью id получаем их фамилию и имя
    '''
    friends = session.method("friends.get", {"user_id": owner_id})
    print("\nСписок друзей:")

    for friend in friends["items"]:
        user = session.method("users.get", {"user_ids": friend})
        print(f"\t{user[0]['first_name']} {user[0]['last_name']}")

def main():
    ''' Главная функция
    1. Подключаемся к сессии
    2. Получам id и фамилию через токен
    3. Получаем фамилию юзера с id=1
    4. Делаем пост на своей стене
    5. Выводим всех своих друзей
    '''
    session = vk_api.VkApi(token = token)
    vk = session.get_api()

    owner_id = get_info(session, "token", token, "id")
    owner_name = get_info(session, "token", token, "first_name")
    
    print(f"Имя пользователя: {owner_name}\nId пользователя: {owner_id}\n")

    USER_ID = 1
    user_name = get_info(session, "user_id", USER_ID, "first_name")
    print("Имя пользователя с id = {0}: {1}".format(USER_ID, user_name))

    wall_post(vk, owner_id)
    get_friends(session, owner_id)