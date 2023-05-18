# импорты
import vk_api
import psycopg2
from datetime import datetime
from vk_api.longpoll import VkLongPoll, VkEventType
from vk_api.utils import get_random_id

from config import comunity_token, acces_token
from core import VkTools
from data_store import create_db, add_db, sel_db


class BotInterface():

    def __init__(self, comunity_token, acces_token):
        self.interface = vk_api.VkApi(token=comunity_token)
        self.api = VkTools(acces_token)
        self.params = None

    def message_send(self, user_id, message, attachment=None):
        self.interface.method('messages.send',
                              {'user_id': user_id,
                               'message': message,
                               'attachment': attachment,
                               'random_id': get_random_id()
                               }
                              )
    def choice_param(self, ev_us_id):
        '''Определение параметров для поиска'''
        longpoll_def = VkLongPoll(self.interface)

        if self.params["sex"] is None:
            self.message_send(self.params["id"],f'Укажите кого будем искать (мужчина/женщина):')
            for event in longpoll_def.listen():
                if event.type == VkEventType.MESSAGE_NEW and event.to_me:
                    if event.type == VkEventType.MESSAGE_NEW and event.to_me:
                        command = event.text.lower()
                        if command == 'мужчина':
                            gender_search=1
                        elif command == 'женщина':
                            gender_search=2
                        else:
                            self.message_send(ev_us_id, "Ответ неясен. Возможны два варианта ответа 'мужчина' или 'женщина'. Повторите. ")
                        self.params["sex"]=gender_search
        else:
            gender_search=self.params["sex"]


        if self.params["home_town"] is None:
            self.message_send(self.params["id"], f'Укажите в каком городе будем искать (ввести наименование города):')
            for event in longpoll_def.listen():
                if event.type == VkEventType.MESSAGE_NEW and event.to_me:
                    if event.type == VkEventType.MESSAGE_NEW and event.to_me:
                        city_name = event.text.lower()
                        self.params["city"]=city_name
        else:
            city_name=self.params["city"]

        if self.params["bdate"] is None:
            self.message_send(self.params["id"], f' Для поиска используется диапозон плюс/минус пять лет от указанного Вами возраста. Укажите какого возраста будем искать людей.')
            for event in longpoll_def.listen():
                if event.type == VkEventType.MESSAGE_NEW and event.to_me:
                    if event.type == VkEventType.MESSAGE_NEW and event.to_me:
                        if event.text.lower().isdigit():
                            age = event.text.lower()
                            self.params["bdate"]=datetime((datetime.now().year-age),1,1)
                        else:
                            self.message_send(ev_us_id, "Введено не числовое значение. Ожидается число.")
        else:
            age = datetime.now().year - int(self.params["bdate"].split(".")[2])

        self.message_send(self.params["id"],
                          f'Ищу пользователей, удовлетворяющих следующим параметрам:\n пол: {"мужчина" if gender_search == 1 else "женщина"}\n город: {city_name}\n возраст: {age - 5} - {age + 5} лет')
        return {"sex":gender_search, "home_town":city_name, "bdate":age}


    def event_handler(self):
        longpoll = VkLongPoll(self.interface)

        for event in longpoll.listen():
            if event.type == VkEventType.MESSAGE_NEW and event.to_me:
                command = event.text.lower()

                if command == 'привет':
                    self.params = self.api.get_profile_info(event.user_id)
                    self.message_send(event.user_id, f'здравствуй {self.params["name"]}')
                elif command == 'поиск':
                    with psycopg2.connect(database="bot_users", user="postgres", password="qwer3") as connec:
                        q=create_db(connec)
                    self.params = self.api.get_profile_info(event.user_id)
                    list_param= self.choice_param(event.user_id)
                    print(f' list_param  {list_param}')
                    print(f' self.params {self.params}')
                    users = self.api.serch_users(self.params)
                    print(users)
                    # print(user)
                    command_2 = 3
                    while command_2!=0:
                        user = users.pop()
                        # здесь логика для проверки бд
                        with psycopg2.connect(database="bot_users", user="postgres", password="qwer3") as connec:
                            q = sel_db(connec, self.params["id"], user["id"])

                        if len(q)==0:
                            photos_user = self.api.get_photos(user['id'])
                            print(f' photos_user = {photos_user}')
                            attachment = ''
                            for num, photo in enumerate(photos_user):
                                if num>0:
                                    attachment += f',photo{photo["owner_id"]}_{photo["id"]}'
                                else:
                                    attachment += f'photo{photo["owner_id"]}_{photo["id"]}'
                                if num == 2:
                                    break
                            print(f'attachment= {attachment}')
                            self.message_send(event.user_id, f'Встречайте {user["name"]}\n https://vk.com/id{user["id"]}', attachment=attachment)
                            self.message_send(event.user_id, 'Показать следующего пользователя? (да/нет): ')
                            # Добавление записи о выведенном пользователе
                            with psycopg2.connect(database="bot_users", user="postgres", password="qwer3") as connec:
                                q = add_db(connec,self.params["id"],user["id"])
                            for event in longpoll.listen():
                                if event.type == VkEventType.MESSAGE_NEW and event.to_me:
                                    command_2 = event.text.lower()
                                    if command_2 == 'да':
                                        break
                                    elif command_2=='нет':
                                        command_2=0
                                        break
                                    else:
                                        self.message_send(event.user_id, 'Ответ не ясен. Повторите! ')
                        else:
                            continue
                elif command == 'пока':
                    self.message_send(event.user_id, 'пока')
                else:
                    self.message_send(event.user_id, 'команда не опознана')


if __name__ == '__main__':
    bot = BotInterface(comunity_token, acces_token)
    bot.event_handler()


