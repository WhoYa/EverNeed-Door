import pandas as pd
import os
import re
from setting import NAME_MK_DIRECTORY, NAME_MK_DIRECTORY_WITH_PHOTO


def cut_article_value(text):
    match = re.search(r'\(артикул (\d+)\)', text)
    if match:
        return match.group(1)
    return None


def remove_article(text):
    return re.sub(r'\(.*?\)', '', text).strip()


def main():
    global directory_path
    result = list()
    list_name_with_not_find_photo_door = list()

    try:
        name_mk = "/" + NAME_MK_DIRECTORY
        directory_path = os.getcwd() + name_mk
        files_and_folders = os.listdir(directory_path)

        if len(files_and_folders) > 1:
            print("Директория должана содержать один файл с форматом: xlsx")
            exit()
        else:
            path_file = directory_path + "/" + files_and_folders[0]

            df = pd.read_excel(path_file, engine='openpyxl')
            for string in df.itertuples():
                result.append({
                    'name': string[1],
                    'description': remove_article(string[2]),
                    'article': cut_article_value(string[2].lower()),
                    'material': string[3],
                    'price': string[4],
                    'image_path': None
                })


    except (IndentationError, FileNotFoundError, UnboundLocalError):
        print(f"Directory not found with {directory_path}")

    try:
        name_mk = "/" + NAME_MK_DIRECTORY_WITH_PHOTO
        directory_path = os.getcwd() + name_mk
        files_and_folders = os.listdir(directory_path)

        if len(files_and_folders) > 0:
            image_extensions = {".jpg", ".jpeg", ".png", ".bmp", ".gif", ".tiff"}

            for filename in os.listdir(directory_path):
                if os.path.isfile(os.path.join(directory_path, filename)) and os.path.splitext(filename)[
                    1].lower() in image_extensions:
                    name_image = os.path.basename(os.path.join(directory_path, filename)).lower()
                    print(cut_article_value(name_image))
                    for d in result:
                        if d['article'] == cut_article_value(name_image):
                            d['image_path'] = os.path.join(directory_path, filename)
                        else:
                            continue

                else:
                    list_name_with_not_find_photo_door.append(os.path.join(directory_path, filename))

        else:
            print("Директория пуста, добавьте фото в формате 'name_file + (Артикул + 442342)'")
            exit()

    except (IndentationError, FileNotFoundError, UnboundLocalError):
        print(f"Directory not found with {directory_path}")

    for _ in result:
        print(_)


if __name__ == '__main__':
    main()
