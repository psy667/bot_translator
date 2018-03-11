from gtts import gTTS
import os
import vk
import requests
import json

token = ''
YANDEX_KEY = ''
session = vk.AuthSession(access_token=token)
vkapi = vk.API(session)



def create_answer(data, token):
    user_id = data['user_id']
    vkapi.messages.setActivity(user_id=user_id,type='typing',v='5.73')

    file = open('log.txt','w')
    file.write(data['body'])
    file.close()

    if 'fwd_messages' in data:
        response = data['fwd_messages'][0]['body']
    else:
        response = data['body']

    if response == '':
        message = ['Извини, я тебя не понимаю. :(','']
        print('lol')
    else:
        try:
            message = translate(response)
        except:
            message = ['Извини, я тебя не понимаю. :c','']

    vkapi.messages.send(user_id=user_id, message=message[0], attachment=message[1],v='5.73')


def translate(text):
    lang1, lang2, text = detect(text)

    if lang2 == 'voice':
        att = save_doc(text, lang1)
        mess = ''
    else:
        '''Переводит текст с языка lang1 на lang2'''
        response = requests.post("https://translate.yandex.net/api/v1.5/tr.json/translate?key="+YANDEX_KEY+"&text="+text+"&lang="+lang1+"-"+lang2)
        response = response.text
        try:
            response = json.loads(response)
            mess = (response['text'][0])
            att = ''
        except:
            mess = 'Извини, я тебя не понимаю.'
            att = ''
    return mess, att

def detect(text):
    '''Определяет язык текста'''
    response = requests.post("https://translate.yandex.net/api/v1.5/tr.json/detect?key="+YANDEX_KEY+"&text="+text+"&hint=en,ru")
    response = response.text
    response = json.loads(response)



    if response['code'] == 200:
        lang1 = (response["lang"])
        if lang1 == 'ru':
            lang2 = 'en'
        else:
            lang2 = 'ru'

    if text[:3] == '/de' or text[:3] == '/uk' or text[:3] == '/en' or text[:3] == '/ja' or text[:3] == '/fr' or text[:3] == '/es' or text[:3] == '/zh':
        lang2 = text[1:3]
        text = text[4:]

    elif text[:3] == '/vo':
        lang2 = 'voice'
        text = text[4:]

    return lang1, lang2, text

def get_hash_photo():
    mp3_name = 'name.mp3'
    url = vkapi.docs.getMessagesUploadServer(token = token, type='audio_message', peer_id='82343463',v='5.73')
    url = url['upload_url']
    files = {'file': (mp3_name, open(mp3_name, 'rb'))}
    response = requests.post(url, files=files)
    response = response.text
    response = json.loads(response)['file']
    return(response)

def save_doc(messages, lang='ru'):
    mp3_name = 'name.mp3'
    try:
      os.remove(mp3_name)
    except:
      pass
    tts = gTTS(text=messages, lang=lang)
    tts.save(mp3_name)

    file = get_hash_photo()
    response = vkapi.docs.save(file=file,v='5.73')
    did = str(response[0]['did'])
    owner = str(response[0]['owner_id'])
    type = 'doc'
    att = type+owner+'_'+did
    return(att)
