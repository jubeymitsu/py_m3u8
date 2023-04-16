import requests
import m3u8
from Crypto.Cipher import AES
from Crypto.Util.Padding import unpad

import os

index_url = "nQ0IWhTo/index.m3u8"
key_pub = "o/key.pub"

# Получаем этот самый m3u8 файл
m3u8_data = m3u8.load(
index_url  # Вставляем наш полученный ранее url
)

segments = m3u8_data.data.get('segments')
print(segments)

# Парсим файл в более удобный формат
segments_data = {}

for segment in segments:
    segment_uri = segment.get('uri')
    extended_segment = {
        "segment_method": None,
        "method_uri": None
    }
    if segment.get('key').get('method') == "AES-128":
        extended_segment['segment_method'] = True
        extended_segment['method_uri'] = segment.get('key').get('uri')

        segments_data[segment_uri] = extended_segment

# И наконец качаем все сегменты с расшифровкой
uris = segments_data.keys()

downloaded_segments = []
for uri in uris:
    # Используем начальный url где мы подменяем index.m3u8 на наш сегмент
    audio = requests.get(url=index_url.replace("index.m3u8", uri))
    # Сохраняем .ts файл
    downloaded_segments.append(audio.content)
    # Если у сегмента есть метод, то расшифровываем его
    if segments_data.get(uri).get('segment_method') is not None:
        # Качаем ключ
        key_uri = segments_data.get(uri).get('method_uri')
        key = requests.get(url=key_pub)

        iv = downloaded_segments[-1][0:16]
        ciphered_data = downloaded_segments[-1][16:]

        # print(key.content)
        # print(iv)

        cipher = AES.new(key.content, AES.MODE_CBC, iv=iv)
        data = unpad(cipher.decrypt(ciphered_data), AES.block_size)
        downloaded_segments[-1] = data

complete_segments = b''.join(downloaded_segments)
# print(complete_segments)

with open('/Users/macbookpro/PycharmProjects/pytest/temp.ts', 'w+b') as f:
  f.write(complete_segments)