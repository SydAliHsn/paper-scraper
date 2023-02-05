import concurrent.futures
from pathlib import Path
import re
import requests
from bs4 import BeautifulSoup


bannedWords = [
    'past', 'papers', 'lahore', 'board', 'part-1', 'inter', 'matric',  'english-medium', 'both-medium']


def remove_extra_words(toPrint):
    statement = toPrint
    database_1 = sorted(list(bannedWords), key=len)
    pattern = re.compile(r"\b(" + "|".join(database_1) + ")\\W", re.I)
    return pattern.sub("", toPrint + ' ')[:-1]


def save_img(img_url):
    response = requests.get(img_url)

    folder_name = ''
    if 'objective' in img_url:
        folder_name = 'Objective'
    elif 'subjective' in img_url:
        folder_name = 'Subjective'
    else:
        folder_name = 'Both'

    image_name = img_url.split('/')[-1]
    image_name = remove_extra_words(image_name).replace('-jpg', '.jpg')

    p = Path(f'{root_folder}/{folder_name}')
    p.mkdir(exist_ok=True, parents=True)
    with (p / image_name).open('wb') as opened_file:
        opened_file.write(response.content)


def scrape_past_papers(page_url, limit):
    html_page = requests.get(page_url).text

    soup = BeautifulSoup(html_page, 'lxml')
    papers_list_html = soup.find('ul', id='ulPastPapers')
    papers = papers_list_html.find_all(recursive=False, limit=limit)

    with concurrent.futures.ThreadPoolExecutor() as executor:
        futures = []

        for paper in papers:
            img_url = (paper.find('img').attrs['src']).lower().replace(
                'thumb', 'large')
            futures.append(executor.submit(save_img, img_url))


if __name__ == '__main__':
    page_url = input('Enter past papers page url from ilmkidunya.com: ')
    root_folder = input('Enter the folder name to save the past papers in: ')

    imgs_limit = int(input('Enter the number of papers you want: '))
    while imgs_limit > 30 or imgs_limit < 1:
        print('Paper limit can only be a positive integer less than or equal to 30!\n')
        imgs_limit = int(input('Enter again: '))

    print('Fetching Past Papers...')
    scrape_past_papers(page_url, imgs_limit)
    print('Done!', f'The past papers have been saved in {root_folder}')
