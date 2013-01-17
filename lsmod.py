from urllib.request import urlopen
from bs4 import BeautifulSoup


def main():
    url = 'http://docs.python.org/3/py-modindex.html'
    with urlopen(url) as f:
        soup = BeautifulSoup(f.read())
        for a in soup.select('.modindextable a'):
            print(a.text)


if __name__ == '__main__':
    main()
