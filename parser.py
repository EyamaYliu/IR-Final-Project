#!/usr/bin/env python3

import re
from bs4 import BeautifulSoup
from urllib import parse, request
#import tldextract
import nltk
import requests
import json




############################################
#Request Api json with given ApiKey
govApiKey = '6slUSrUJs4voS0slTRjOGGjNlaYWI873fULgtnUQ'

sampleJsonQuery = 'https://api.nal.usda.gov/ndb/V2/reports?ndbno=01009&type=b&format=json&api_key='+ govApiKey

r = requests.get(sampleJsonQuery)

dict1 = r.json()

print(dict1['foods'][0]['food']['desc']['name'])

############################################

#Definiations 

#Get recipe, input is url, output is all ingredient
def get_recipe_ingredients(root, html):

    ing_lines = []
    soup = BeautifulSoup(html, 'html.parser')
    for link in soup.find_all('label'):
        title = link.get('title')
        if title:
            ing_lines.append(str(title))
    return ing_lines

#Handle numbers like 2 1/3, convert string into float number
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

#Extract nouns from a sentence, input:string, output:string
def noun_extract(key):
    #FIND NOUNS IN STRING
    is_noun = lambda pos: (pos == 'NN' or pos == "NNS" or pos == "VB")
    # do the nlp stuff
    tokenized = nltk.word_tokenize(key)
    #print(nltk.pos_tag(tokenized))
    #only want nouns
    nouns = [word for (word, pos) in nltk.pos_tag(tokenized) if is_noun(pos)]
    nouns = ' '.join(nouns)
    return nouns

def ing_dict_creator(site):

    r = request.urlopen(site)

    measurement = [line.rstrip('\n') for line in open('Measurements')]



    #print(measurement)

    ingredient_lines = get_recipe_ingredients(site,r.read())


    ingredient_dict = {}

    for lines in ingredient_lines:
        #Indicate if a unit is detected in the lines
        YesUnit = False
        #Get rid of all parentheses
        lines = re.sub('[(){}<>,.:]','',lines)
        lines = lines.split(' ')
        #print(lines)
        for word in lines:
            for unit in measurement:
                #Check if line contains standard unit
                if unit in word:
                    portion = ' '.join(lines[lines.index(word)-1:lines.index(word)+1])
                    key = ' '.join(lines[lines.index(word)+1:])
                    #print(key)

                    nouns = noun_extract(key)

                    ingredient_dict[nouns] = portion
                    YesUnit = True
        if not YesUnit:
            numpos = 0
            for i in range(len(lines)):
                #print(lines[i])
                if '/' in lines[i]:
                    lines[i] = divider(lines,lines[i])
                    numpos = i
            portion = lines[numpos]
            key = ' '.join(lines[numpos+1:])

            #FIND RELEVANT FOOD NOUNS IN STRING
            nouns = noun_extract(key)

            ingredient_dict[nouns] = portion
       
    return ingredient_dict

#    Search for most relevant ingredient name in usda food database, return a ndbno
#for further calories check
def food_name_search(ingredient):

    govApiKey = '6slUSrUJs4voS0slTRjOGGjNlaYWI873fULgtnUQ'

    ingredient = '+'.join(ingredient.split())
   
    
    #sort by name:n, or by relevancy:r
    sort = 'r'
    #Database type:either 'Standard Reference' or 'Branded+Food+Products'
    ds = 'Standard+Reference'

    search_link = 'https://api.nal.usda.gov/ndb/search/?format=json&q='+ingredient+'&sort='+sort+'&ds='+ds+'&max=25&offset=0&api_key=' + govApiKey

    print(search_link)
    
    result = requests.get(search_link)

    result_json = result.json()
    most_relevant_ndbno = result_json['list']['item'][0]['ndbno']
    print(most_relevant_ndbno)



    return most_relevant_ndbno




if __name__ == '__main__':

    ####################################
    #Link to specific recipe page on 'AllRecipes', need to be changed into 
    #input instead of static link
    #TODO
    ###################################
    site = 'https://www.allrecipes.com/recipe/72985/feta-chicken-salad/'

    ####################
    #Run ingredient dictionary creator module with passed in site url
    #####################    

    ingredient_dict = ing_dict_creator(site)

    for key in ingredient_dict:
        #temp = ingredient_dict[key].split()
        
        print(key)
        ndbno = food_name_search(key)
    #ndbno = 
    #ndbno = food_name_search('oil')


'https://api.nal.usda.gov/ndb/search/?format=json&q=bell+pepper&sort=r&ds=Standard+Reference&max=25&offset=0&api_key=6slUSrUJs4voS0slTRjOGGjNlaYWI873fULgtnUQ'

    



