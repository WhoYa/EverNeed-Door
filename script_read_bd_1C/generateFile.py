import random
import pandas as pd
import os
import shutil

from script_read_bd_1C.setting import NAME_MK_DIRECTORY_WITH_PHOTO
from setting import NAME_MK_DIRECTORY, NAME_FILE_XLSX



def main():

    names = [
        "Дверь входная с ковкой", "Дверь межкомнатная с зеркалом", "Дверь стеклянная для офиса",
        "Дверь стальная", "Дверь с отделкой из дерева", "Дверь с декоративным стеклом",
        "Дверь из массива дерева", "Дверь для сауны", "Дверь с шумоизоляцией", "Дверь с ковкой"
    ]

    descriptions = [
        f"Дверь с ковкой и металлическим покрытием (Артикул {random.randint(100000, 999999)})",
        "Дверь с зеркальной отделкой (Артикул 23456)",
        f"Стеклянная дверь с алюминиевой рамой (Артикул {random.randint(100000, 999999)})",
        "Стальная дверь с порошковым покрытием (Артикул 45678)",
        f"Дверь с отделкой из натурального дерева (Артикул {random.randint(100000, 999999)})",
        "Дверь с декоративным стеклом и металлической рамой (Артикул 67890)",
        f"Межкомнатная дверь из массива (Артикул {random.randint(100000, 999999)})",
        "Дверь для бани с термостойким покрытием (Артикул 89012)",
        f"Дверь с хорошей шумоизоляцией (Артикул {random.randint(100000, 999999)})",
        "Дверь с художественной ковкой (Артикул 11234)"
    ]

    materials = [
        "Металл, стекло", "Дерево, стекло", "Стекло, алюминий", "Сталь, порошковое покрытие",
        "Дерево, металл", "Стекло, металл", "Дерево, МДФ", "Стекло, алюминий", "Дерево, пластик", "Металл, МДФ"
    ]

    generated_data = {
        "Название двери": [random.choice(names) for _ in range(100)],
        "Описание двери": [random.choice(descriptions) for _ in range(100)],
        "Материалы": [random.choice(materials) for _ in range(100)],
        "Цена": [round(random.uniform(2500, 8000), 2) for _ in range(100)]
    }

    directory = os.getcwd() + "/" + NAME_MK_DIRECTORY

    try:
        shutil.rmtree(directory)
        print(f"Директория {directory} и её содержимое успешно удалены или обновлены")
    except FileNotFoundError:
        print(f"Директория {directory} не найдена.")
    except OSError as e:
        print(f"Ошибка при удалении директории: {e}")

    name_directory ="/" + create_directory(NAME_MK_DIRECTORY)
    df_large = pd.DataFrame(generated_data)
    name_file = "/" + NAME_FILE_XLSX
    file_path_large = os.getcwd() + name_directory + name_file + ".xlsx"
    df_large.to_excel(file_path_large, index=False)

    create_directory(NAME_MK_DIRECTORY_WITH_PHOTO)


def create_directory(name_dr):
    name_directory = name_dr
    os.makedirs(name_directory, exist_ok=True)
    return name_directory


if __name__ == '__main__':
    main()
