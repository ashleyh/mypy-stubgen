from urllib.request import urlopen
from bs4 import BeautifulSoup
import argparse


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--version', default='3.2',
            help='which Python version to list modules for')

    args = parser.parse_args()

    url = 'http://docs.python.org/{}/py-modindex.html'.format(args.version)
    with urlopen(url) as f:
        soup = BeautifulSoup(f.read())
        for a in soup.select('.modindextable a'):
            print(a.text)


if __name__ == '__main__':
    main()
