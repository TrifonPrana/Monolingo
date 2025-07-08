from config import monolingo_api_token
import telebot 
import logging
import json
import random


TOKEN = monolingo_api_token

#Создаем бота-обьект
bot = telebot.TeleBot(TOKEN)

user_data = {}#Формат: {message.from_user.id: {user_dict}}

try:
    with open("user_data.json", "r",encoding="utf-8") as json_file:
        user_data = json.load(json_file)
except FileNotFoundError:
    with open("user_data.json", "w", encoding="utf-8") as json_file:
            user_data_w = {}
            json.dump(user_data_w, json_file, ensure_ascii=False, indent=4)     
    

#Обработчик команды /start
@bot.message_handler(commands=["start"])
def handle_start(message):
    bot.send_message(message.chat.id,"Привет!Я твой бот помощник.Я могу помочь тебе учить языки!")

#Обработчик команды /help
@bot.message_handler(commands=["help"])
def handle_help(message):
    help_text = (
        "Я могу помочь тебе учить языки! Вот список команд:\n"
        "/start - Привет!\n"
        "/help - Показать это сообщение\n"
        "/addword <слово> <перевод> - Добавить слово и его перевод в словарь\n"
        "/delword <слово> - Удалить слово и его перевод из словаря\n"
        "/mywords - Посмотри все слова в своем словаре\n"
        "/learn <кол-во слов> - Начни урок, где ты будешь переводить слова из своего списка!\n"
    )
    bot.send_message(message.chat.id, help_text)


#Обработчик команды /addword
@bot.message_handler(commands=["addword"])
def handle_addword(message):
    global user_data
    global user_dict
    chat_id = str(message.chat.id)
    user_dict = user_data.get(chat_id, {})

    words = message.text.split()[1:]
    if len(words) == 2:
        word, translation = words[0].lower(), words[1].lower()
        if word in user_dict:
            bot.send_message(chat_id, "Это слово уже есть в словаре!")
            return
        user_dict[words[0]] = words[1]
        user_data[chat_id] = user_dict

        with open("user_data.json", "w", encoding="utf-8") as json_file:
            json.dump(user_data, json_file, ensure_ascii=False, indent=4)
        
        bot.send_message(chat_id, f'Слово "{word}" и его перевод "{translation}" успешно добавлены!')
    else:
        bot.send_message(chat_id, 'Пожалуйста, введите слово и его перевод в формате: /addword <слово> <перевод>')
    
#Обработчик команды /learn
@bot.message_handler(commands=["learn"])
def handle_learn(message):
    global words_number
    try:
        words_number = int(message.text.split()[1])
    except TypeError:
        bot.send_message(message.chat.id,"Вы неправильно ввели кол-во слов для изучения.Используйте только арабские цифры.")
        return
    except IndexError:
        bot.send_message(message.chat.id,"Вы неправильно ввели кол-во слов для изучения.Введите в формате /learn <кол-во слов>.")
        return
    
    user_words = user_data.get(str(message.chat.id),{}) 

    global score
    score = 0

    bot.send_message(message.chat.id,"Хорошо,сейчас начнется урок!")

    ask_translation(message.chat.id,user_words,words_number)
    
def ask_translation(chat_id,user_words,words_left):  
    if words_left > 0:
        try:
            word = random.choice(list(user_words.keys()))
        except IndexError:
            bot.send_message(chat_id,"Ваш словарь пуст.Добавьте слова с помощью команды /addword.")
            return
        translation = user_words[word]
        bot.send_message(chat_id,f'Напиши перевод слова "{word}".')

        bot.register_next_step_handler_by_chat_id(chat_id,check_translation,translation,words_left) 
    else: 
        bot.send_message(chat_id,f"Урок окончен!Вы набрали {score}/{words_number*10} баллов!")
        
def check_translation(message,correct_translation,words_left):
    global score
    user_translation = message.text.strip().lower()
    if user_translation == correct_translation.lower():
        frazes = ["Правильно!"
                  ,"Молодец!","Отлично!","Супер!","Замечательно!","Прекрасно!","Продолжай в том же духе!"]
        bot.send_message(message.chat.id,random.choice(frazes))
        score += 10
    else:
        bot.send_message(message.chat.id,f'Неправильно!Правильный перевод "{correct_translation}".')
        score -= 5

    ask_translation(message.chat.id,user_data[str(message.chat.id)],words_left-1)


#Обработчик команды /delword
@bot.message_handler(commands=["delword"])
def handle_delword(message):
    global user_data
    chat_id = str(message.chat.id)
    if len(user_data[chat_id]) <= 0:
        bot.send_message(chat_id,"Ваш словарь пуст!")
        return

    try:
        word = message.text.split()[1]
    except IndexError:
        bot.send_message(chat_id, "Пожалуйста, введите команду в формате: /delword <слово которе вы хотите удалить>.")
        return
    if word not in user_data[chat_id].keys():
        bot.send_message(chat_id, "У вас в словаре нет такого слова!")
        return
    translation = user_data[chat_id][word]
    del user_data[chat_id][word]

    with open("user_data.json", "w", encoding="utf-8") as json_file:
        json.dump(user_data, json_file, ensure_ascii=False, indent=4)

    bot.send_message(chat_id, f'Слово "{word}" и его перевод "{translation}" успешно удалены!')

#Обработчик команды /mywords
@bot.message_handler(commands=["mywords"])
def handle_mywords(message):    
    chat_id = str(message.chat.id)


    if len(user_data[chat_id]) <= 0:
        bot.send_message(chat_id, "Ваш словарь пуст. Добавьте слова с помощью команды /addword.")
        return
    
    bot.send_message(chat_id,"Ваши слова в списке:")
    for word,translation in user_data[chat_id].items():
        bot.send_message(chat_id,f"{word} - {translation}")



if __name__ == "__main__": 
    logging.basicConfig(level=logging.INFO)
    logging.info("Бот запущен!")


    #Запуск бота
    bot.polling(none_stop=True)