#!/usr/bin/env python3

import re
from bs4 import BeautifulSoup
from urllib import parse, request
#import tldextract
import nltk

def get_links(root, html):

    ing_lines = []
    soup = BeautifulSoup(html, 'html.parser')
    for link in soup.find_all('label'):
        title = link.get('title')
        if title:
            ing_lines.append(str(title))
    return ing_lines


#Convert inputs like 1 3/4 into a float number
def divider(lines,num):

    pos = lines.index(num)
    sum = 0
    while pos != 0:
        pos = pos - 1
        try:
            sum += float(lines[pos])
        except:
            continue
    num = num.split('/')
    return float(num[0])/float(num[1])+sum


site = 'https://www.allrecipes.com/recipe/68532/curried-coconut-chicken/?internalSource=previously%20viewed&referringContentType=home%20page&clickId=cardslot%203'

r = request.urlopen(site)

measurement = [line.rstrip('\n') for line in open('Measurements')]



#print(measurement)

ingredient_lines = get_links(site,r.read())
ingredient_dict = {}

def noun_extracter(sentence):
    #FIND RELEVANT FOOD NOUNS IN STRING
    is_noun = lambda pos: pos == 'NN'
    # do the nlp stuff
    tokenized = nltk.word_tokenize(sentence)
    #only want nouns
    nouns = [word for (word, pos) in nltk.pos_tag(tokenized) if is_noun(pos)]
    nouns = ' '.join(nouns)
    print(nouns)
    return nouns
    

for lines in ingredient_lines:
    YesUnit = False
    #Get rid of all parentheses
    lines = re.sub('[(){}<>]','',lines)
    lines = lines.split(' ')
    for word in lines:
        for unit in measurement:
            #Check if line contains standard unit
            if unit in word:
                portion = ' '.join(lines[lines.index(word)-1:lines.index(word)+1])
                key = ' '.join(lines[lines.index(word)+1:])
                #print(key)

                ingredient_dict[key] = portion
                YesUnit = True
    if not YesUnit:
        numpos = 0
        for i in range(len(lines)):
            if '/' in lines[i]:
                lines[i] = divider(lines,lines[i])
                numpos = i
        portion = lines[numpos]
        key = ' '.join(lines[numpos+1:])



        ingredient_dict[key] = portion





print(ingredient_dict)


search_site = 'www.calorieking.com/food/search.php?keywords='
