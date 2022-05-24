import os
import sys
import shutil
from zipfile import ZipFile
from bs4 import BeautifulSoup as bs


class EPUB:
    def __init__(self, epub_file):
        self.epub = ZipFile(epub_file)
        self.filename = os.path.splitext(self.epub.filename)[0]

    def get_images(self):
        namelist = self.epub.namelist()
        for f in namelist:
            if os.path.splitext(f)[1] == '.opf':
                opf_file = os.path.join(self.temp_dir, f)
                opf_dir = os.path.dirname(opf_file)
        with open(opf_file, 'r', encoding='utf-8') as f:
            doc = f.read()
        opf = bs(doc, 'lxml')

        spine = opf.find('spine')
        itemref = spine.find_all('itemref')
        pages = [x.attrs['idref'] for x in itemref]

        images = []
        for page in pages:
            item = opf.find('item', attrs={'id': page})
            html_file = os.path.join(opf_dir, item.attrs['href'])
            with open(html_file, 'r', encoding='utf-8') as f:
                html = bs(f.read(), 'lxml')
            img = html.find('img')
            img_src = img.attrs['src']
            img_file = os.path.join(os.path.split(html_file)[0], img_src)
            img_file = os.path.normpath(img_file)
            images.append(img_file)
        return images

    def extract(self):
        self.temp_dir = os.path.join(self.filename, 'temp')
        self.epub.extractall(self.temp_dir)

        images = self.get_images()
        pid_len = len(str(len(images)))
        for id, img in enumerate(images):
            suffix = os.path.splitext(img)[1]
            pid = str(id+1).zfill(pid_len)
            new_path = os.path.join(self.filename, str(pid) + suffix)
            shutil.move(img, new_path)
        shutil.rmtree(self.temp_dir)


def traverse_dir(path):
    files = []
    for f in os.listdir(path):
        if os.path.splitext(f)[1] == '.epub':
            files.append(os.path.join(path, f))
    return files


def get_files():
    files = []
    argv = sys.argv[1:]
    if argv:
        for i in argv:
            if os.path.isfile(i):
                files.append(i)
            elif os.path.isdir(i):
                files += traverse_dir(i)
    else:
        files = traverse_dir('.')
    return files


if __name__ == '__main__':
    files = get_files()
    for f in files:
        epub = EPUB(f)
        epub.extract()
