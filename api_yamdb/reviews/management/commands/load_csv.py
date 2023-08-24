import csv
import os

from django.core.management import BaseCommand
from django.db import IntegrityError

from api_yamdb.settings import CSV_FILES_DIR
from reviews.models import (
    Category,
    Comment,
    Genre,
    Review,
    Title
)
from users.models import User

MODEL_CLASSES = {
    'category': Category,
    'genre': Genre,
    'titles': Title,
    'users': User,
    'review': Review,
    'comments': Comment,
}

FIELDS = {
    'category': ('category', Category),
    'title_id': ('title', Title),
    'genre_id': ('genre', Genre),
    'author': ('author', User),
    'review_id': ('review', Review),
}


def change_value(data_csv):
    data_csv_copy = data_csv.copy()
    for field_key, field_value in data_csv.items():
        if field_key in FIELDS.keys():
            field_key0 = FIELDS[field_key][0]
            data_csv_copy[field_key0] = FIELDS[field_key][1].objects.get(
                pk=field_value)
    return data_csv_copy


def open_csv_file(file_name):
    csv_file = file_name + '.csv'
    csv_path = os.path.join(CSV_FILES_DIR, csv_file)
    try:
        with (open(csv_path, encoding='utf-8')) as file:
            return list(csv.reader(file))
    except FileNotFoundError:
        print(f'Файл {csv_file} не найден.')
        return


def load_csv_file(file_name, class_name):
    table_not_load = f'Таблица {class_name.__qualname__} не загружена.'
    table_load = f'Таблица {class_name.__qualname__} успешно загружена.'
    data = open_csv_file(file_name)
    rows = data[1:]
    for row in rows:
        data_csv = dict(zip(data[0], row))
        data_csv = change_value(data_csv)
        try:
            table = class_name(**data_csv)
            table.save()
        except (ValueError, IntegrityError) as error:
            print(f'Ошибка в загружаемых данных: {error}. '
                  f'{table_not_load}')
    print(table_load)


class Command(BaseCommand):
    def handle(self, *args, **options):
        for key, value in MODEL_CLASSES.items():
            print(f'Загрузка таблицы {value.__qualname__}')
            load_csv_file(key, value)
