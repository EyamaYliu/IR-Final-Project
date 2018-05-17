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

            ingredient_dict[nouns] = str(portion)
       
    return ingredient_dict

###############################
#    Search for most relevant ingredient name in usda food database, return a ndbno
#for further calories check
###############################

def food_name_search(ingredient):
    most_relevant_ndbno = 0

    govApiKey = '6slUSrUJs4voS0slTRjOGGjNlaYWI873fULgtnUQ'
   
    
    #sort by name:n, or by relevancy:r
    sort = 'r'
    #Database type:either 'Standard Reference' or 'Branded+Food+Products'
    ds = 'Standard+Reference'

    search_link = 'https://api.nal.usda.gov/ndb/search/?format=json&q='+ingredient+'&sort='+sort+'&ds='+ds+'&max=25&offset=0&api_key=' + govApiKey  
    result = requests.get(search_link)
    result_json = result.json()

    #Handle no result situation, if errors in key of json, ask for a better result
    while 'errors' in result_json:
        print('\nSEARCH ERROR!')
        print('Your Input:  "'+ingredient+'"  , did not yield any result')
        ingredient = input("    Please try with a alternative input: ")
        
        updated_search_link = 'https://api.nal.usda.gov/ndb/search/?format=json&q='+ingredient+'&sort='+sort+'&ds='+ds+'&max=25&offset=0&api_key=' + govApiKey  
        update_result = requests.get(updated_search_link)
        result_json = update_result.json()        

    most_relevant_ndbno = result_json['list']['item'][0]['ndbno']

    return most_relevant_ndbno

#    Takes input from the retrived dictionary portion part, like '1 pound', '4 tablespoons'
#  and convert into either cup or grams. If can't automatically convert, it will require
#  hand input
def measurement_unification(name,portion):
    portion = portion.split()

    num_portion = 0
    #Find the numerical part of the portion
    for word in portion:
        if word.isdigit():
            num_portion = float(word)

    measurement = [line.rstrip('\n') for line in open('Measurements')]
    volume_units = ['cup','tablespoon','teaspoon','ounce','quart','gallon','pint']
    volume_unit_convert = [1.0,0.0625,0.0208333,0.125,4.0,16.0,2.0]
    weight_units = ['gram','pound']
    weight_unit_convert = [1.0,453.6]

    unit_Found = False
    volume_Indicator = False


    for word in portion:
        for unit in measurement:
            if unit in word:
                #See if the unit belongs to standard volume units
                if unit in volume_units:
                    volume_Indicator = True
                    unit_Found = True
                    num_portion = num_portion * volume_unit_convert[volume_units.index(unit)]
                #See if the unit belongs to standard weight units
                elif unit in weight_units:
                    unit_Found = True
                    num_portion = num_portion * weight_unit_convert[weight_units.index(unit)]

    #If not, hand input in estimation
    while unit_Found == False and str(num_portion).isdigit() == False:
        print('\nUNIT ERROR!')
        print("This portion: \'"+' '.join(portion)+" of "+name+"\' does not contain a standard unit.")
        num_portion = input("    Please enter an estimated weight, use unit 'gram':")
                

    if volume_Indicator == False:
        result = str(num_portion)+ ' gram'
    else:
        result = str(num_portion)+ ' cup'   
    
    print(result) 

    return result
                    


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

        ndbno = food_name_search(key)
        converted_portion = (measurement_unification(key,str(ingredient_dict[key]))).split()
        


    



