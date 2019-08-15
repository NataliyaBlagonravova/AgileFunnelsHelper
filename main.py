import datetime
import requests
import json
import pandas as pd
from pandas import DataFrame
import telebot
import pytz
import math

from telebot import types

custom_ids = {
    'webinar': 482987,
    'country': 482989,
    'city': 482991,
    'ip':482993,
    'start_time':482995,
    'end_time':482997,
    'total_time':482999,
    'buttons':483003,
    'source':483001,
    'comments':483587,
    'phone':93069
}

def create_item(user_data):
    item =  {
        'name': user_data['name'],
        'tags': user_data['webinar'],
        'custom_fields':[
        {
        'id': custom_ids['webinar'],
        'values': [{
          'value' : user_data['webinar']
                  }]
        },
        {
        'id': custom_ids['country'],
        'values': [{
          'value' : user_data['country']
                  }]
        },
        {
        'id': custom_ids['city'],
        'values': [{
          'value' : user_data['city']
                  }]
        },
        {
        'id': custom_ids['ip'],
        'values': [{
          'value' : user_data['ip']
                  }]
        },
        {
        'id': custom_ids['start_time'],
        'values': [{
          'value' : user_data['start_time']
                  }]
        },
        {
        'id': custom_ids['end_time'],
        'values': [{
          'value' : user_data['end_time']
                  }]
        },
        {
        'id': custom_ids['total_time'],
        'values': [{
          'value' : user_data['total_time']
                  }]
        },
        {
        'id': custom_ids['buttons'],
        'values': [{
          'value' : user_data['buttons']
                  }]
        },
        {
        'id': custom_ids['source'],
        'values': [{
          'value' : user_data['source']
                  }]
        },
        {
        'id': custom_ids['phone'],
        'values': [{
          'value' : user_data['phone'],
          'enum'  : "WORK"
                  }]
        },
        {
        'id': custom_ids['comments'],
        'values': [{
          'value' : user_data['comments']
                  }]
        }]
    }
    return item

def is_contact_in_crm(user_data):
  URL = 'https://agilefunnels.amocrm.ru/private/api/auth.php'
  user_login = 'chekmchekm@yandex.ru'
  user_hash = '21b83fa01534cfd856912f7de84a82b2a9abd65d'
  data = {'USER_LOGIN': user_login, 'USER_HASH':user_hash}
  session = requests.Session()
  r = session.post(url = URL, data = data)

  parms =  {'limit_rows': '500'}

  r = session.get(url = 'https://agilefunnels.amocrm.ru/api/v2/contacts', params = parms)


  if r.status_code == 204:
    print('База пуста')
    return False

  data = r.json()
  data1 = data['_embedded']
  items = data1['items']

  for item in items:
    custom_fields = item['custom_fields']
    number = None
    webinar = None
    for field in custom_fields:
      if field['id'] == custom_ids['webinar']:
        values = field['values']
        webinar = values[0]['value']
      if field['id'] == custom_ids['phone']:
        values = field['values']
        number = values[0]['value']
      if number == user_data['phone'] and webinar == user_data['webinar']:
        print(webinar, ' ', number)
        return True

  return False




def upload_df_to_crm(df):
  URL = 'https://agilefunnels.amocrm.ru/private/api/auth.php'
  user_login = 'chekmchekm@yandex.ru'
  user_hash = '21b83fa01534cfd856912f7de84a82b2a9abd65d'
  data = {'USER_LOGIN': user_login, 'USER_HASH': user_hash}
  session = requests.Session()
  r = session.post(url = URL, data = data)

  for index, row in df.iterrows():


    user_data = {
    'name': row['Имя'] if row['Имя'] != None else '',
    'phone': row['Телефон'] if row['Телефон'] != None else '',
    'webinar':row['Вебинар'] if row['Вебинар'] != None else '',
    'country':row['Страна'] if row['Страна'] != None else '',
    'city':row['Город'] if row['Город'] != None else '',
    'ip':row['IP'] if row['IP'] != None else '',
    'start_time':row['Время начала'] if row['Время начала'] != None else '',
    'end_time':row['Время завершения'] if row['Время завершения'] != None else '',
    'total_time':row['Время просмотра'] if row['Время просмотра'] != None else '',
    'buttons':row['Нажал на кнопки'] if row['Нажал на кнопки'] != 'nan' else '',
    'source': row['Источник трафика'] if row['Источник трафика'] != None else '',
    'comments':row['Комментарии'] if row['Комментарии'] != None else ''
    }




    data = {
    'add': []
    }


    if not is_contact_in_crm(user_data):
      data['add'].append(create_item(user_data))
      r = session.post('https://agilefunnels.amocrm.ru/api/v2/contacts', data = json.dumps(data))
      print("Result is:%s"%r.text)
    else:
      print('In CRM')



def getWebinarId(day, month, year, is_new):
  str_year = str(year)

  str_month = str(month)
  if month < 10:
    str_month = '0' + str_month

  str_day = str(day)
  if day < 10:
    str_day = '0' + str_day

  if is_new:
    return '9598:WebEvolutionLife*'+ str_year +'-'+ str_month + '-'+ str_day +'T19:00:00'
  return '9598:EvolutionLifeWebinar*'+ str_year +'-'+ str_month + '-'+ str_day +'T19:00:00'


def str_to_time(time_str):
  return datetime.datetime.strptime(time_str,'%H:%M:%S')

def time_to_str(time):
  return time.strftime('%H:%M:%S')

def merge_rows(row_1, row_2):
    start_time_1  = str_to_time(row_1['Время начала'])
    start_time_2 = str_to_time(row_2['Время начала'])
    end_time_1 = str_to_time(row_1['Время завершения'])
    end_time_2 = str_to_time(row_2['Время завершения'])

    start_time = start_time_1
    if start_time_2 < start_time_1:
        start_time = start_time_2

    end_time = end_time_1
    if end_time_2 > end_time_1:
        end_time = end_time_2

    row_2['Время начала'] = time_to_str(start_time)
    row_2['Время завершения'] = time_to_str(end_time)
    if row_1['IP'] != row_2['IP']:
        row_2['IP'] = row_2['IP'] + ' ' + row_1['IP']


    if row_1['Нажал на кнопки'] != row_2['Нажал на кнопки']:
        row_2['Нажал на кнопки'] = row_2['Нажал на кнопки'] + " " + row_1['Нажал на кнопки']

    if row_1['Источник трафика'] != row_2['Источник трафика']:
        row_2['Источник трафика'] = row_2['Источник трафика'] + " " + row_1['Источник трафика']

    if start_time_1 < start_time_2:
        row_2['Комментарии'] = row_1['Комментарии'] + '' + row_2['Комментарии']
    else:
        row_2['Комментарии'] = row_2['Комментарии'] + '' + row_2['Комментарии']

    print('start: ' + time_to_str(start_time))
    print('end: ' + time_to_str(end_time))

    return row_2

def getLastWebnarDate():
  now = datetime.datetime.now(pytz.timezone('Europe/Moscow'))

  day = now.day
  month = now.month
  year = now.year
  hour = now.hour

  if hour < 23:
    day = getYestedayDate().day
    month = getYestedayDate().month
    year = getYestedayDate().year

  return day, month, year



def getLastWebinarId(is_new):
  day, month, year = getLastWebnarDate()
  return getWebinarId(day, month, year, is_new)


def getYestedayDate():
  return datetime.datetime.now(pytz.timezone('Europe/Moscow'))- datetime.timedelta(days=1)

def getBase(is_new):
  bizon_token = 'rxuVsxjnESgeO4sgs3VHlbd4sgohNrxMuNjlohVHgmd4iljhN'
  bizon_headers = {'X-Token': bizon_token}

  url = 'https://online.bizon365.ru/api/v1/webinars/reports/get?webinarId=' + getLastWebinarId(is_new)


  print(getLastWebinarId(is_new))

  req = requests.get(url, headers=bizon_headers)

  result = req.json()

  report = result['report']
  rep = report['report']
  y = json.loads(rep)
  viewers = y['usersMeta']

  messages = report['messages']
  messages = json.loads(messages)





  cliens_messages = []

  for id in messages:
    cliens_messages.append([id, str(messages.get(id)).strip('[]')])


  df1 = DataFrame(cliens_messages ,columns=['id', 'Комментарии'])


  rating = y['rating']

  df2 = DataFrame(rating ,columns=['id'])

  cliens_info = []

  for item in viewers:
    viewer = viewers.get(item)

    user_id = item
    username = ''
    phone = ''
    country = ''
    city = ''
    ip = ''
    finished = False
    view = 0
    viewTill = 0
    weight = 0

    clickBanner = ''
    clickFile = ''
    utm_source = ''

    if 'username' in viewer:
        username = viewer['username']

    if 'phone' in viewer:
        phone = viewer['phone']

    if 'country' in viewer:
        country = viewer['country']

    if 'city' in viewer:
        city = viewer['city']

    if 'ip' in viewer:
        ip = viewer['ip']

    if 'finished' in viewer:
        finished = viewer['finished']

    if 'view' in viewer:
        view = viewer['view']
        date1 = datetime.datetime.fromtimestamp(view/1000.0, pytz.timezone('Europe/Moscow'))
        start_time = date1.strftime('%H:%M:%S')


    if 'viewTill' in viewer:
        viewTill = viewer['viewTill']
        date2 = datetime.datetime.fromtimestamp(viewTill/1000.0, pytz.timezone('Europe/Moscow'))
        finish_time = date2.strftime('%H:%M:%S')

    if 'weight' in viewer:
        weight = viewer['weight']

    if 'clickBanner' in viewer:
        clickBanner = viewer['clickBanner']

    if 'clickFile' in viewer:
        clickFile = viewer['clickFile']

    if 'utm_source' in viewer:
        utm_source = viewer['utm_source']

    day, month, year = getLastWebnarDate()
    webinar_name = 'Вебинар ' + str(day) + '.' + str(month) + '.' + str(year)


    cliens_info.append([user_id, webinar_name, username, phone, country, city, ip, start_time, finish_time, '111', clickFile, utm_source])

  df = DataFrame(cliens_info ,columns=['id', 'Вебинар', 'Имя', 'Телефон', 'Страна', 'Город', 'IP', 'Время начала', 'Время завершения', 'Время просмотра','Нажал на кнопки', 'Источник трафика'])


  df3 = pd.merge(df, df1, on='id')

  df_sorted = df3.sort_values(by=['Телефон'])

  last_phone = None
  prev_row = None
  prev_index = 0
  for index, row in df_sorted.iterrows():
      phone = row['Телефон']
      if last_phone == phone:
          print("Дубликат: ", phone)
          merge_row = merge_rows(row, prev_row)
          df_sorted.drop(index=prev_index, inplace=True)
          df_sorted.loc[index] = merge_row

      last_phone = phone
      prev_row = row
      prev_index = index


  print('Дублекаты по номеру телефона удалены')


  for index, row in df_sorted.iterrows():
      start_time =  str_to_time(row['Время начала'])
      end_time =  str_to_time(row['Время завершения'])
      watched_time = end_time - start_time
      df_sorted.loc[index]['Время просмотра'] = str(watched_time)


  df_sorted = df_sorted.sort_values(by=['Время просмотра'], ascending=False)

  df_sorted.drop(columns='id', inplace=True)

  file_name = webinar_name + '2.csv'

  upload_df_to_crm(df_sorted)

  df_sorted.to_csv(file_name, index=False)

  return file_name



TOKEN = '848616404:AAFByzTdfhdG5G7tfhFGxpbEOwakitBqpmw'
bot = telebot.TeleBot(TOKEN)

@bot.message_handler(commands=['start', 'go'])
def start_handler(message):
    markup = types.ReplyKeyboardMarkup()
    #markup.row('Новый вебинар')
    markup.row('Старый вебинар')
    bot.send_message(message.chat.id, "Какую базу выгрузить?", reply_markup=markup)


@bot.message_handler(content_types=['text'])

def send_text(message):
    now = datetime.datetime.now(pytz.timezone('Europe/Moscow'))
    if message.text == 'Новый вебинар':
        bot.send_message(message.chat.id, 'Сейчас выгружу актуальную базу на '+ now. strftime("%H:%M"))
        bot.send_message(message.chat.id, 'База обновляется ежедневно в 23:00')

        filename = getBase(False)
        doc = open(filename, 'rb')

        bot.send_document(message.chat.id, doc)
        bot.send_message(message.chat.id, 'Не забудь загрузить базу на гугл-диск   https://drive.google.com/drive/folders/1upyq0Uc2CqU93R_148BIgBQg5Gh6oV-V?usp=sharing')

    if message.text == 'Старый вебинар':
        bot.send_message(message.chat.id, 'Сейчас выгружу актуальную базу на ' + now. strftime("%H:%M"))
        bot.send_message(message.chat.id, 'База обновляется ежедневно в 23:00')

        filename = getBase(False)
        doc = open(filename, 'rb')

        bot.send_document(message.chat.id, doc)
        bot.send_message(message.chat.id, 'База выгружена CRM')


