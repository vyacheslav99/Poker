import os
import json
import random
import argparse


def reload_res(source_dir: str):
    if not source_dir:
        print('Не указана папка с исходниками!')
        return

    print(f'Source folder {source_dir}')
    s = input('Вы сейчас собираетесь перетереть существующий ресурс тем, что найдется в исходниках.'
              ' Вы точно уверены, что это надо сделать? [ДА: Y/y/Д/д, НЕТ: N/n/Н/н]')

    if s not in ['Y','y','Д','д']:
        print('Сборка ресурсов отменена!\n')
        return

    print('Building resources')

    data = []
    cnt = 0

    for fn in os.listdir(source_dir):
        cnt += 1
        with open(f'{source_dir}/{fn}', 'r') as f:
            contents = f.read()
            contents = contents.split('\n\n')
            data.extend(contents)

    print(f'Found source files: {cnt}')
    print(f'Fond total texts: {len(data)}')
    print('Writing res file')

    with open('./resources/bikes.json', 'wb') as f:
        f.write(json.dumps(data).encode())

    print('Done!\n')


def test():
    with open('./resources/bikes.json', 'rb') as f:
        data = json.loads(f.read().decode())
        n = 10 if len(data) >= 10 else len(data)
        print(f'Вот {n} случано выбранных текстов из того, что есть сейчас:\n\n')

        for r in range(n):
            print(random.choice(data))
            print('\n *** \n')


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--build', '-b', action='store_true',
                    help='Пересобрать файл текстовых ресурсов из исходников. Существующий файл будет перезаписан новым.'
                         'Исходники - все текстовые файлы в указанной папке, содержащие тексты (афоризмы, анектоды), '
                         'разделенные пустой строкой.')
    ap.add_argument('--source', '-s', help='Папка с исходными текстами. Все текстовые файлы (*.txt) '
                                           'в этой папке будут обработаны и собраны в ресурс текстов.')
    ap.add_argument('--test', '-t', action='store_true',
                    help='Протестировать результат или текущий собранный ресурс - выведет случайные 10 текстов')
    args = ap.parse_args()

    if args.build:
        reload_res(args.source)

    if args.test:
        test()


if __name__ == '__main__':
    main()