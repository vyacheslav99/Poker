import os
import json
import random


def reload_res():
    s = input('Вы сейчас собираетесь перетереть существующий ресурс тем, что найдется в исходниках.'
              ' Вы точно уверены, что это надо сделать? [ДА: Y/y/Д/д, НЕТ: N/n/Н/н]')

    if s not in ['Y','y','Д','д']:
        print('Сборка ресурсов отменена!\n')
        return

    print('Building resources')

    data = []
    rootdir = './resources/anecdots'

    for fn in os.listdir(rootdir):
        with open(f'{rootdir}/{fn}', 'r') as f:
            contents = f.read()
            contents = contents.split('\n\n')
            data.extend(contents)

    print('Writing res file')

    with open('./resources/bikes.json', 'wb') as f:
        f.write(json.dumps(data).encode())

    print('Done!\n')


def test():
    with open('./resources/bikes.json', 'rb') as f:
        data = json.loads(f.read().decode())
        n = 10 if len(data) >= 10 else len(data)
        print(f'Вот {n} случано выбранных анекдотов из того, что есть сейчас:\n\n')

        for r in range(n):
            print(random.choice(data))
            print('\n *** \n')

if __name__ == '__main__':
    reload_res()
    test()