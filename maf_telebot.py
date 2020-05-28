import telebot
import random
import datetime
import threading
import time

MVP_word = ''
MVP_leader_id = 0
MVP_voices = {}

class leader:
    def __init__(self):
        self.list = []
        self.maf_num = 0
        self.red_num = 0
        self.roles = []
        self.mafs = [-1]*3
        self.kom = -1
        self.don = -1
        self.speaker = 0
        self.round = 0
        self.ty_beacon = 0
        self.fouls = []
        self.log = ''
        self.roles_str = ''
        self.MVP = 0


leaders = {}

bot = telebot.TeleBot('1064953384:AAGxg3o_S1ymOjfH5znmDpA55ISKi9G-euM');

def voit(message):
    global MVP_voices
    if not message.text.isdigit() or int(message.text) > len(leaders[MVP_leader_id].list) or int(message.text) <= 0:
        bot.send_message(message.chat.id, 'Неверный формат ввода. Напишите одну цифру, под которой в списке указан ваш кандидат:\n'+
                         leaders[MVP_leader_id].roles_str)
        bot.register_next_step_handler(message, voit)
    MVP_voices[message.chat.id] = int(message.text)
    bot.send_message(message.chat.id, 'Спасибо. Вы проголосовали за игрока ' +
                     leaders[MVP_leader_id].list[int(message.text)-1] + '.')

def keyboarder(d): #ключ - текст, значение - дата
    keyboard = telebot.types.InlineKeyboardMarkup()
    for i in list(d.keys()):
        keyboard.add(telebot.types.InlineKeyboardButton(text = i, callback_data = d[i]))
    return keyboard


def auto_list(message):
    bot.send_message(message.chat.id, 'Один\nДва\nТри\nЧетыре\nПять\nШесть\nСемь\nВосемь\nДевять\nДесять')

def list_forming(message):
    global leaders     
    leaders[message.chat.id].list = message.text.split()
    random.shuffle(leaders[message.chat.id].list)
    leaders[message.chat.id].list_str = ''
    for i, item in enumerate(leaders[message.chat.id].list, 1):
        leaders[message.chat.id].list_str += str(i) + '. ' + item + '\n'
            
    bot.send_message(message.chat.id, 'рандомлю...\n\n' + leaders[message.chat.id].list_str,
                     reply_markup = keyboarder({'Мафия': 'one_maf_game',
                                                'Дон/Мафия/Комиссар': 'two_maf_game',
                                                'Дон/Мафия/Мафия/Комиссар': 'three_maf_game'}))
    leaders[message.chat.id].roles = ['']*len(leaders[message.chat.id].list)
    
    
def roles_forming(_id):
    leaders[_id].roles_str = ''
    for i in range(0, len(leaders[_id].list)):
##        print(type(i), type(leaders[_id].don))
        if i == leaders[_id].don:
            leaders[_id].roles[i] = 'd'
        elif i in leaders[_id].mafs:
            leaders[_id].roles[i] = 'm'
        elif i == leaders[_id].kom:
            leaders[_id].roles[i] = 'k'
        else:
            leaders[_id].roles[i] = 'r'
    d = {'k':'коммисар', 'r':'мирный', 'm':'мафия', 'd':'дон'}
    for i, item in enumerate(leaders[_id].roles):
        leaders[_id].roles_str += str(i+1)
        leaders[_id].roles_str += '. '
        leaders[_id].roles_str += leaders[_id].list[i]
        leaders[_id].roles_str += ' - '
        leaders[_id].roles_str += d[item]
        leaders[_id].roles_str += '\n'
    
    bot.send_message(_id, 'рандомлю...\n\n' + leaders[_id].roles_str)
                     


##ЧТЕНИЕ СООБЩЕНИЙ
@bot.message_handler(content_types=['text'])
def get_text_messages(message):
    global leaders
    global MVP_word
    global MVP_leader_id
    print('message!')
    if message.text.lower() == '/start':
        leaders[message.chat.id] = leader()
        bot.send_message(message.from_user.id, 'Регистрирую новую игру. Введите список',
                         reply_markup = keyboarder({'test':'auto_list'}))
        bot.register_next_step_handler(message, list_forming)
    elif message.text.lower().split()[0].lower() == 'mvp':
        MVP_word = message.text.lower().split()[1].lower()
        MVP_leader_id = message.chat.id
        bot.send_message(message.chat.id, 'Голосвание открыто. Секретное слово: \'{}\'.'.format(MVP_word))
        
    elif message.text.lower() == 'debug':
        print(leaders.get(message.chat.id, 'not registred').list)
        print(leaders.get(message.chat.id, 'not registred').mafs)
        print(leaders.get(message.chat.id, 'not registred').don)
        print(leaders.get(message.chat.id, 'not registred').kom)
        print(leaders.get(message.chat.id, 'not registred').roles)
        print(leaders.get(message.chat.id, 'not registred').MVP)
        print(MVP_word, MVP_leader_id, MVP_voices)
    elif message.text.lower() == MVP_word:
        bot.send_message(message.from_user.id, 'Голосвание за лучшего играка матча (MVP):\n'+
                         leaders[MVP_leader_id].roles_str)
        bot.register_next_step_handler(message, voit)
    elif ('mvp' in message.text.lower().split()) and ('stop' in message.text.lower().split()):
        d = {}
        if MVP_voices == {}:
            bot.send_message(message.from_user.id, 'Никто не проголосовал.')
            return
        for i in MVP_voices.values():
            if i in list(d.keys()):
                d[i] += 1
            else:
                d[i] = 1
        print(MVP_voices, d)
        ans = [list(d.keys())[0]]
        for i in list(d.keys()):
            if d[i] > d[ans[0]]:
                ans = [i]
            elif d[i] == d[ans[0]]:
                ans.append(i)
        leaders[message.chat.id].MVP = random.choice(ans) - 1
        bot.send_message(message.from_user.id, 'Голосвание завершено. Выбран игрок №{} - {}.'.format(leaders[message.chat.id].MVP+1,
                                            leaders[message.chat.id].list[leaders[message.chat.id].MVP]))
        

        

##КОНТРОЛЬ КНОПОК
@bot.callback_query_handler(func=lambda call: True)
def callback_worker(call):
    if call.data == 'one_maf_game':
        leaders[call.message.chat.id].mafs.append(random.randint(0, len(leaders[call.message.chat.id].list)))
        roles_forming(call.message.chat.id)
    elif call.data == 'two_maf_game':
        leaders[call.message.chat.id].mafs = random.sample(list(range(0, len(leaders[call.message.chat.id].list))), 2)
        leaders[call.message.chat.id].don = leaders[call.message.chat.id].mafs[0]
        leaders[call.message.chat.id].kom = leaders[call.message.chat.id].don
        while leaders[call.message.chat.id].kom in leaders[call.message.chat.id].mafs:
            leaders[call.message.chat.id].kom = random.randint(0, len(leaders[call.message.chat.id].list))
        roles_forming(call.message.chat.id)
    elif call.data == 'three_maf_game':
        leaders[call.message.chat.id].mafs = random.sample(list(range(0, len(leaders[call.message.chat.id].list))), 3)
        leaders[call.message.chat.id].don = leaders[call.message.chat.id].mafs[0]
        leaders[call.message.chat.id].kom = leaders[call.message.chat.id].don
        while leaders[call.message.chat.id].kom in leaders[call.message.chat.id].mafs:
            leaders[call.message.chat.id].kom = random.randint(0, len(leaders[call.message.chat.id].list))
        roles_forming(call.message.chat.id)
    elif call.data == 'auto_list':
        auto_list(call.message)
    return
        
bot.polling(none_stop=True, interval = 0)
