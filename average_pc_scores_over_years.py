import argparse
import requests
import matplotlib.pyplot as plt
import numpy as np
from bs4 import BeautifulSoup

# years = ['1995', '1996', '1997', '1998', '1999', '2000', '2001', '2002', '2003', '2004', '2005', '2006', '2007', '2008', '2009', '2010', '2011', '2012', '2013', '2014', '2015', '2016', '2017', '2018', '2019']

# Call the program like this:
# python3 average_pc_scores_over_years.py -l 2000 2001 2002 -p pc

ap = argparse.ArgumentParser()
ap.add_argument("-y", "--years", nargs='+', required=True,
	help="""
        Space-separated list of years to get data for.
        Should obvoiously only contain years that Metacritic has data for.
    """)
ap.add_argument("-p", "--platform", required=True,
	help="""
        The platform to get data for.
        Can be one of the following:
        all, pc, ps4, xboxone, switch, wii-u, 3ds, vita, ios.
    """)
args = vars(ap.parse_args())

# platform can be:
# 'all', 'pc', 'ps4', 'xboxone', 'switch', 'wii-u', '3ds', 'vita', 'ios'
def get_game_score_over_years(platform, years):
    total = {}
    boxplot_data = {}
    for year in years:
        page_number = 0
        url = "https://www.metacritic.com/browse/games/score/metascore/year/{}/all?view=condensed&sort=desc&year_selected={}&page={}".format(platform, year, page_number)
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2228.0 Safari/537.3'}
        print('Checking number of pages for year {}'.format(year))
        r = requests.get(url, headers=headers)
        soup = BeautifulSoup(r.content, 'html.parser')

        no_data = soup.find('p', {'class': 'no_data'})
        if no_data is not None and 'No Results Found' in no_data:
            print('The {} platform has no data for year {}'.format(platform, year))
            print()
            continue

        pages = soup.find('li', {'class': 'page last_page'})
        if pages is None:
            print('This year has only 1 page')
            page_number = 1
        else:
            for page in pages:
                for page_elem in page:
                    if page_elem.isdigit():
                        print('Last page is {}'.format(page_elem))
                        # page_elem is the visible page number 1-indexed.
                        # in the url it is 0-indexed
                        page_number = int(page_elem)

        values = []
        for page in range(page_number):
            url = "https://www.metacritic.com/browse/games/score/metascore/year/{}/all?view=condensed&sort=desc&year_selected={}&page={}".format(platform, year, page)
            print('Getting data for year {} on page {}/{}'.format(year, page+1, page_number))
            r = requests.get(url, headers=headers)
            soup = BeautifulSoup(r.content, 'html.parser')

            scores = soup.find('ol', {'class': 'list_products list_product_condensed'})
            if scores is None:
                print('No scores for the {} platform for year {}'.format(platform, year))
                continue

            for elem in scores.find_all('li', {'class': 'stat product_avguserscore'}):
                score_list = elem.select('.textscore')
                for score in score_list:
                    if 'tbd' in score:
                        print('Score is tbd, continuing...')
                        continue
                    score = float(BeautifulSoup.renderContents(score))
                    values.append(score)

        avg = sum(values) / len(values)
        total[year] = avg
        boxplot_data[year] = values
        print('Count of scores for year {}: {}'.format(year, len(values)))
        print()
    return (total, boxplot_data)

def plot_data(boxplot_data, graph_data):
    # Create a figure instance
    fig = plt.figure(1, figsize=(9, 6))
    labels, data = [*zip(*boxplot_data.items())]
    plt.boxplot(data)
    plt.xticks(range(1, len(labels) + 1), labels)
    plt.title(args['platform'])
    plt.xlabel('Years')
    plt.ylabel('Score')
    fig.show()

    gig = plt.figure(2, figsize=(9, 6))
    plt.bar(range(len(total)), list(total.values()), align='center')
    plt.xticks(range(len(total)), list(total.keys()))
    plt.title(args['platform'])
    plt.xlabel('Years')
    plt.ylabel('Score')
    gig.show()

    # to force the two images to keep being open
    input()

(total, boxplot_data) = get_game_score_over_years(args['platform'], args['years'])

plot_data(boxplot_data, total)
