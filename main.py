from bs4 import BeautifulSoup
import requests
import magic
import os
import shutil

def scrape_data():
    try:
        os.mkdir("output")
    except FileExistsError:
        shutil.rmtree("output")
        os.mkdir("output")

    used_urls = []

    base_url = 'https://olymp-vana.haridus.ee/'
    base_requests = requests.get(base_url)
    base_soup = BeautifulSoup(base_requests.text, 'html.parser')

    all_years_urls = []
    all_years_urls_dict = {}
    print("Iga õppeaasta lehed:")
    for ref in base_soup.find_all('a', href=True):
        if ref.string:
            if "õa" in ref.string.lower():
                year = ref.string.lower()
                url = f"https://olymp-vana.haridus.ee/{ref['href']}"
                used_urls.append(url)
                all_years_urls.append(url)
                all_years_urls_dict[url] = year

                os.mkdir(f"output/{year.strip().replace('/', '_')}")
                print(f"{year} - {url}")

    all_years_subjects_urls = []
    all_years_subjects_urls_dict = {}
    print("\nIga õppeaasta õppeainete lehed:")
    for year_url in all_years_urls:
        year_requests = requests.get(year_url)
        year_soup = BeautifulSoup(year_requests.text, 'html.parser')

        for ref in year_soup.find('div', id='main').find_all('a', href=True):
            if ref.string:
                if "õppeained" in ref.string.lower():
                    year = all_years_urls_dict[year_url]
                    url = f"https://olymp-vana.haridus.ee/{ref['href']}"
                    used_urls.append(url)
                    all_years_subjects_urls.append(url)
                    all_years_subjects_urls_dict[url] = year
                    print(f"{all_years_urls_dict[year_url]} - {url}")

    all_subjects_urls = []
    print("")
    for year_subjects_url in all_years_subjects_urls:
        current_year = all_years_subjects_urls_dict[year_subjects_url]
        print(f"\n{current_year} õppeained ja nende lehed:")

        year_subjects_requests = requests.get(year_subjects_url)
        year_subjects_soup = BeautifulSoup(year_subjects_requests.text, 'html.parser')

        for ref in year_subjects_soup.find('div', id='main').find_all('a', href=True):
            if f"https://olymp-vana.haridus.ee/{ref['href']}" not in all_years_urls:
                subject = ref.string.lower().capitalize()
                url = f"https://olymp-vana.haridus.ee/{ref['href']}"
                used_urls.append(url)
                os.mkdir(f"output/{current_year.strip().replace('/', '_')}/{subject.strip().replace('/', '_')}")
                all_subjects_urls.append(url)
                print(f"    {subject} - {url}")

                all_filesdirs_requests = requests.get(url)
                all_filedirs_soup = BeautifulSoup(all_filesdirs_requests.text, 'html.parser')
                for filedir in all_filedirs_soup.find('div', id='main').find_all('a', href=True):
                    if filedir.string:
                        if "http" not in filedir.string.lower() and "õppeained" not in filedir.string.lower() and f"https://olymp-vana.haridus.ee/{filedir['href']}" not in all_years_urls:
                            filedir_url = f"https://olymp-vana.haridus.ee/{filedir['href']}"
                            used_urls.append(filedir_url)
                            filedir_headers = requests.get(filedir_url, stream=True).headers
                            all_subjects_urls.append(filedir_url)

                            if filedir_headers["Content-Type"] != "text/html":
                                file_data = requests.get(filedir_url).content
                                with open(f"output/{current_year.strip().replace('/', '_')}/{subject.strip().replace('/', '_')}/{filedir.string.strip().replace('/', '_')}", "wb") as file:
                                    file.write(file_data)
                                print(f"        {filedir.string} - {filedir_url}")
                            else:
                                print(f"        {filedir.string} - {filedir_url}")
                                dir_name = filedir.string.lower().capitalize()
                                try:
                                    os.mkdir(f"output/{current_year.strip().replace('/', '_')}/{subject.strip().replace('/', '_')}/{dir_name.strip().lower().capitalize().replace('/', '_')}")
                                except FileExistsError:
                                    pass
                                dir_url = f"https://olymp-vana.haridus.ee/{filedir["href"]}"
                                used_urls.append(dir_url)
                                dir_requests = requests.get(dir_url)
                                dir_soup = BeautifulSoup(dir_requests.text, 'html.parser')
                                if dir_soup.find('div', id='main'):
                                    for sub_filedir in dir_soup.find('div', id='main').find_all('a', href=True):
                                        if sub_filedir.string:
                                            if "http" not in sub_filedir.string.lower() and "õppeained" not in sub_filedir.string.lower() and f"https://olymp-vana.haridus.ee/{sub_filedir['href']}" not in all_years_urls:
                                                sub_filedir_url = f"https://olymp-vana.haridus.ee/{sub_filedir['href']}"
                                                used_urls.append(sub_filedir_url)
                                                sub_filedir_headers = requests.get(sub_filedir_url, stream=True).headers

                                                if sub_filedir_headers["Content-Type"] != "text/html":
                                                    file_data = requests.get(sub_filedir_url).content
                                                    with open(f"output/{current_year.strip().replace('/', '_')}/{subject.strip().replace('/', '_')}/{dir_name.strip().lower().capitalize().replace('/', '_')}/{sub_filedir.string.replace('/', '_')}", "wb") as file:
                                                        file.write(file_data)
                                                    print(f"            {sub_filedir.string} - {sub_filedir_url}")
                                                else:
                                                    print(f"            {sub_filedir.string} - {sub_filedir_url}")
                                                    sub_dir_name = sub_filedir.string.lower().capitalize()
                                                    os.mkdir(f"output/{current_year.strip().replace('/', '_')}/{subject.strip().replace('/', '_')}/{dir_name.strip().lower().capitalize().replace('/', '_')}/{sub_dir_name.strip().lower().capitalize().replace('/', '_')}")
                                                    sub_dir_url = f"https://olymp-vana.haridus.ee/{sub_filedir["href"]}"
                                                    used_urls.append(sub_dir_url)
                                                    sub_dir_requests = requests.get(sub_dir_url)
                                                    sub_dir_soup = BeautifulSoup(sub_dir_requests.text, 'html.parser')
                                                    if sub_dir_soup.find('div', id='main'):
                                                        for sub_sub_filedir in sub_dir_soup.find('div', id='main').find_all('a', href=True):
                                                            if "http" not in sub_sub_filedir.string.lower() and "õppeained" not in sub_sub_filedir.string.lower() and f"https://olymp-vana.haridus.ee/{sub_sub_filedir['href']}" not in all_years_urls and f"https://olymp-vana.haridus.ee/{sub_sub_filedir['href']}" not in all_subjects_urls and f"https://olymp-vana.haridus.ee/{sub_sub_filedir['href']}" not in used_urls:
                                                                sub_sub_filedir_url = f"https://olymp-vana.haridus.ee/{sub_sub_filedir['href']}"
                                                                sub_sub_filedir_headers = requests.get(sub_sub_filedir_url, stream=True).headers

                                                                if sub_sub_filedir_headers["Content-Type"] != "text/html":
                                                                    file_data = requests.get(sub_sub_filedir_url).content
                                                                    with open(f"output/{current_year.strip().replace('/', '_')}/{subject.strip().replace('/', '_')}/{dir_name.strip().lower().capitalize().replace('/', '_')}/{sub_filedir.string.strip().lower().capitalize().replace('/', '_')}/{sub_sub_filedir.string.strip().lower().capitalize().replace('/', '_')}", "wb") as file:
                                                                        file.write(file_data)
                                                                    print(f"                {sub_sub_filedir.string} - {sub_sub_filedir_url}")

# Removing random empty directory artifacts
def delete_empty_folders(root):
   for dirpath, dirnames, filenames in os.walk(root, topdown=False):
      for dirname in dirnames:
         full_path = os.path.join(dirpath, dirname)
         if not os.listdir(full_path): 
            os.rmdir(full_path)

def is_pdf(filepath):
    try:
        with open(filepath, 'rb') as f:
            header = f.read(5)
            return header == b'%PDF-'  # PDFs start with "%PDF-"
    except Exception as e:
        print(f"Error reading file {filepath}: {e}")
        return False

# Renaming all files to have their corresponding file extentions
def rename_files_in_directory(directory_path):

    # Walk through all files and subdirectories
    for root, dirs, files in os.walk(directory_path):
        for filename in files:
            filepath = os.path.join(root, filename)

            # Detect the MIME type of the file
            mime_type = magic.from_file(filepath, mime=True)

            # If MIME type is not PDF, check for PDF signature manually
            if mime_type != 'application/pdf' and is_pdf(filepath):
                mime_type = 'application/pdf'

            # Map MIME types to file extensions
            ext = None
            if 'application/pdf' in mime_type:
                ext = '.pdf'
            elif mime_type.startswith('text/'):
                ext = '.txt'
            elif mime_type == 'application/msword':
                ext = '.doc'  # Older Word format
            elif mime_type == 'application/vnd.openxmlformats-officedocument.wordprocessingml.document':
                ext = '.docx'  # Newer Word format
            elif mime_type == 'application/vnd.ms-excel':
                ext = '.xls'  # Older Excel format
            elif mime_type == 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet':
                ext = '.xlsx'  # Newer Excel format
            elif mime_type == 'application/vnd.ms-powerpoint':
                ext = '.ppt'  # Older PowerPoint format
            elif mime_type == 'application/vnd.openxmlformats-officedocument.presentationml.presentation':
                ext = '.pptx'  # Newer PowerPoint format
            elif mime_type == 'application/vnd.oasis.opendocument.spreadsheet':
                ext = '.ods'  # OpenDocument Spreadsheet format

            # If an extension was found, rename the file
            if ext:
                new_filename = filename + ext
                new_filepath = os.path.join(root, new_filename)
                os.rename(filepath, new_filepath)
                # print(f"Renamed {filepath} to {new_filepath}")
            else:
                filepath = os.path.join(root, filename)
                print(f"No suitable extension found for {filepath}!")



if __name__ == "__main__":
    scrape_data()
    directory_path = './output'
    delete_empty_folders(directory_path)
    rename_files_in_directory(directory_path)