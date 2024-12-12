import pandas as pd
import os
import re




def cut_article_value(text):
    match = re.search(r'\(Артикул (\d+)\)', text)
    if match:
        return match.group(1)
    return None


def remove_article(text):
    return re.sub(r'\(.*?\)', '', text).strip()


def main():

    result = list()

    try:
        name_mk = "/Only_doors"
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
                    'type': cut_article_value(string[2]),
                    'material': string[3],
                    'price': string[4]
                })


    except (IndentationError, FileNotFoundError, UnboundLocalError):
        print("Directory not found")


    for e in result:
        print(e)


if __name__ == '__main__':
    main()
