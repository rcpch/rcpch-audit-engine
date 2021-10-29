import os
import zipfile
from requests import request
import os

def download_latest_snomed():
    url="https://uk.nhs/sct-clinical"
    headers = {"x-key": "af7988af183500b83f97b1527da429d0e2202e9f"}
    downloaded = request.get(url=url, headers=headers)
    path = os.path.join(os.path.dirname(__file__), 'snomed.db')

    with open(file=path, mode="wb") as savedFile:
        savedFile.write(downloaded.content)


def extract(dir):
    extract_folder = os.path.join(dir,"extracts")
    for allfiles in os.listdir(dir):
        if allfiles.split('.')[-1] == 'zip':
            file_path = os.path.join(dir, allfiles)
            unzip_file(file_path, extract_folder)

def unzip_file(filename: str, extract_folder="extracts"):
    with zipfile.ZipFile(filename, 'r') as snomed_zip_file:
        snomed_zip_file.extractall(extract_folder)
