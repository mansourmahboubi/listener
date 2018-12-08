#!/usr/bin/python3
from telethon import TelegramClient, events
# from curd import curd
import csv


def main():
    session_name = 'conf/listener.session'
    api_id = 'Your_api_id'
    api_hash = 'Your_api_hash'
    client = TelegramClient(session_name, api_id, api_hash)
    # db = curd(dbhost='', dbuser='', dbpwd='', dbname='')
    symble = []
    restricted_symble = []

    with open('list/Watch.csv', 'r') as csv_file:
        csv_reader = csv.reader(csv_file)
        next(csv_reader)
        for line in csv_reader:
            symble.append(line[0])
    with open('list/UnWatch.csv', 'r') as csv_file:
        csv_reader = csv.reader(csv_file)
        for line in csv_reader:
            restricted_symble.append(line[0])

    @client.on(events.NewMessage)
    async def my_event_handler(event):
        for j in symble:
            if j in event.raw_text:
                if j in restricted_symble:
                    continue
                # f_symble = {'message': event.raw_text, 'symble': j}
                # db.insert(table='', data=f_symble)
                # print(event.raw_text, " symbol : ", j)
                await client.send_message('self', event.raw_text)
                await event.forward_to('user_name')

    client.start()
    client.run_until_disconnected()


if __name__ == '__main__':
    main()
