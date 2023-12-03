################################################################################ 
# 
#       AUTHOR: 
#           Brigham Thornock 
#  DESCRIPTION: 
#           Reads in three html files 2023_Maldivian_presidential_election.html,
#           American_Revolutionary_War.html, and Katalin_Karikó.html.
#           Extracts every sentence that mentions a date, part of speech tags each
#           sentence with a custom tag 'DATE' for dates, then calculates days since
#           provided epoch for each date.
#
#           Adapted from Human Language Technologies class assignment
# DEPENDENCIES: 
#           Created with Python 3.11.5 
#           re, nltk, datetime, BeautifulSoup
# 
################################################################################

import nltk
from bs4 import BeautifulSoup
import re
from nltk.tokenize import sent_tokenize, word_tokenize
import datetime

month_dict = {
            'jan': 1,
            'feb': 2,
            'mar': 3,
            'apr': 4,
            'may': 5,
            'jun': 6,
            'jul': 7,
            'aug': 8,
            'sep': 9, 
            'oct': 10,
            'nov': 11,
            'dec': 12
    }

date_reg = re.compile('[A-Za-z]+ \d{1,2}, \d{4}|' +\
                      '\d{1,2}\/\d{1,2}\/\d{2,4}|' +\
                        '\d{4}-\d{2}-\d{2}|' +\
                            '\d{1,2} [A-Za-z]+ \d{4}')

def divider(text="", char="=", divider_length=80):
    if not (text==""):
        text = ' ' + text + ' '
    return text.center(divider_length, char)

def clean_text(text):
    text = text.strip()
    text = re.sub('\[.*?\]', '', text)
    text = re.sub('<.*?>', '', text)
    return text

def monthToNum(month):
    if month in month_dict.keys():
        return month_dict[month]
    else:
        return -1

def str_to_date(date):
    if date[0].isalpha():
        month, day, year = date.split()
        month = monthToNum(month[:3].lower())
        day = day[:-1]

        if month < 0:
            return -1

    elif '/' in date:
        month, day, year = date.split('/')
        if len(year) < 4:
            year = '20' + year

    elif '-' in date:
        year, month, day = date.split('-')

    elif date[0].isdigit():
        day, month, year = date.split()
        month = monthToNum(month[:3].lower())

        if month < 0:
            return -1

    return datetime.date(int(year), int(month), int(day))


def process_dates(sentence, start_date):
    temp_sent = sentence
    sent_dict = {}
    
    date_matches = re.finditer(date_reg, sentence)

    for match in date_matches:
        date_str = match.group()
        date_obj = str_to_date(date_str)

        if date_obj == -1:
            continue
        
        date_id = f'DATE_{len(sent_dict)+1:06d}'
        
        sent_dict[date_id] = {}
        sent_dict[date_id]['date_str'] = date_str
        sent_dict[date_id]['date'] = date_obj
        sent_dict[date_id]['days_since'] = (sent_dict[date_id]['date'] - start_date).days
        
        temp_sent = temp_sent.replace(date_str, date_id)

    words = word_tokenize(temp_sent)

    for i in range(len(words)):
        if 'DATE_' in words[i]:
            words[i] = sent_dict[words[i]]['date_str']

    
    default_pos_tags = nltk.pos_tag(words)
    custom_tagger =  nltk.RegexpTagger([(date_reg, 'DATE')], backoff=nltk.DefaultTagger('NN'))
    pos_tags = [(token, custom_tagger.tag([token])[0][1]) if re.match(date_reg, token) else (token, tag) for token, tag in default_pos_tags]

    sent_dict['pos_tags'] = pos_tags

    return sent_dict


sent_list = []
war_end = 0
with open('2023_Maldivian_presidential_election.html', 'r', encoding='utf-8') as election_html, open('American_Revolutionary_War.html', 'r', encoding='utf-8') as war_html, open('Katalin_Karikó.html', 'r', encoding='utf-8') as katalin_html:
    soup_list = []
    soup_list.append(BeautifulSoup(war_html.read(), 'html.parser'))
    soup_list.append(BeautifulSoup(election_html.read(), 'html.parser'))
    soup_list.append(BeautifulSoup(katalin_html.read(), 'html.parser'))

    
    for soup in soup_list:
        p_tags = soup.find_all('p')
        citations = soup.find_all('cite')

        text = '. '.join([clean_text(tag.get_text()) for tag in p_tags if not tag.get_text().isspace()]) 
        text = re.sub('\.+', '.', text)

        sentences = sent_tokenize(text.lower())
        sentences += [clean_text(citation.get_text()).lower() for citation in citations if not citation.get_text().isspace()]
        
        sent_list += sentences

        if war_end == 0:
            war_end = len(sent_list) - 1

date_index = 1
for index, sent in enumerate(sent_list):

    if index <= war_end:
        start_date = datetime.date(1783, 9, 3)
    else:
        start_date = datetime.date(2023, 10, 4)

    sent_dict = process_dates(sent, start_date)

    
    if len(sent_dict.keys()) > 1:
        days_since = ''
        for key, date_info in sent_dict.items():
            if key == 'pos_tags':
                continue

            if date_info['days_since'] < 0:
                days_since += date_info['date'].strftime('%B %d, %Y').ljust(20) + f"{-1 * date_info['days_since']} days until " + start_date.strftime('%B %d, %Y') + '\n'
            else:
                days_since += date_info['date'].strftime('%B %d, %Y').ljust(20) + f"{date_info['days_since']} days since " + start_date.strftime('%B %d, %Y') + '\n'
                
    else:
        continue
    
    
    print(divider(text=f'Sentence: {date_index:06d}') + '\n' \
        + sent + '\n' \
            + f"{sent_dict['pos_tags']}\n\n"\
                + days_since)

    date_index += 1
