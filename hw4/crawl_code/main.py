
import json
import urllib2
import urlparse
from bs4 import BeautifulSoup

import config

OUTPUT_DATA = {}


def get_url_data(url):
    ''' Get web page data from given url
    '''
    request = urllib2.Request(url, headers={'User-Agent': 'Magic Browser'})
    response = urllib2.urlopen(request)
    return response


def get_country_asn_data(url, country):
    '''Find ASN information by converting table in HTML page to dictionary
    '''
    global OUTPUT_DATA

    print 'Getting ASN for country {0}'.format(country)

    data = get_url_data(url).read()

    soup = BeautifulSoup(data, 'html.parser')
    table = soup.find(lambda tag: tag.name == 'table' and tag['id'] == 'asns')

    if table is None:
        print 'No active ASNs found for country {0}'.format(country)
        return

    rows = table.findAll(lambda tag: tag.name == 'tr')

    headers = [s.text for s in soup.findAll('th')]

    for row in rows[1:]:
        d = [s.text for s in row.findAll('td')]

        data = dict(zip(headers[1:], d[1:]))
        data['Country'] = country
        OUTPUT_DATA[d[0].strip('ASN')] = data


def dump_to_file():
    '''Dump output to given file
    '''
    with open(config.OUTPUT_FILE, 'wb') as f:
        json.dump(OUTPUT_DATA, f, indent=4, sort_keys=True)


def main():
    '''Find ASN information from given website
    '''
    url = '{0}{1}'.format(config.HOME_PAGE_URL, config.START_PAGE)
    data = get_url_data(url).read()

    soup = BeautifulSoup(data, 'html.parser')
    for tag in soup.findAll('a', href=True):
        if '/country/' not in tag['href']:
            continue

        link = urlparse.urljoin(config.HOME_PAGE_URL, tag['href'])
        if not link:
            continue

        country = tag['href'].strip('/country/')
        get_country_asn_data(link, country)

    dump_to_file()


if __name__ == '__main__':
    main()
