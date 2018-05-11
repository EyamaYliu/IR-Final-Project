#!/usr/bin/env python3

import re
from bs4 import BeautifulSoup
from urllib import parse, request
#import tldextract

def get_links(root, html):

    ing_lines = []
    soup = BeautifulSoup(html, 'html.parser')
    for link in soup.find_all('label'):
        title = link.get('title')
        if title:
            ing_lines.append(str(title))
    return ing_lines
        

site = 'https://www.allrecipes.com/recipe/68532/curried-coconut-chicken/?internalSource=previously%20viewed&referringContentType=home%20page&clickId=cardslot%203'
r = request.urlopen(site)

measurement = [line.rstrip('\n') for line in open('Measurements')]


print(measurement)


ingredient_lines = get_links(site,r.read())

for lines in ingredient_lines:
    lines = lines.split(' ')
    for word in lines:
        if word in measurement:
            print(word)
    print(lines)


