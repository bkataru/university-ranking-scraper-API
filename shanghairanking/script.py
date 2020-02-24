from bs4 import BeautifulSoup, NavigableString
import requests
from fuzzywuzzy import process

subject_page_url = 'http://www.shanghairanking.com/Shanghairanking-Subject-Rankings/index.html'
ranking_base = 'http://www.shanghairanking.com/shanghairanking-subject-rankings/'

def get_obj_from_attr(obj_list, param):
    target_obj = dict()
    for obj in obj_list:
        if obj['name'] == param:
            target_obj = obj
            break

    return target_obj

def get_subject_data(subject):
    subject_page = requests.get(subject_page_url)
    soup = BeautifulSoup(subject_page.content, 'html.parser')
    subject_tags = soup.find_all(lambda tag: tag.name == 'a' and 'subject-' in str(tag.get('class')))
    subject_objs = []
    subject_list = []
    for tag in subject_tags:
        subject_list.append(tag.contents[0])
        subject_objs.append({
            'name': tag.contents[0],
            'id': str(tag.get('href')).split('.')[0]
        })

    fuzzy_result = process.extract(subject, subject_list, limit=5)
    results = []
    for res in fuzzy_result:
        target_sub = get_obj_from_attr(subject_objs, res[0])
        results.append({
            'name': res[0],
            'id': target_sub['id']
        })

    return results

print('=' * 50)
def get_ranking_data(subject_id):
    main_page = requests.get(subject_id + subject_id + '.html')
    scrape_txt = main_page.content

    soup = BeautifulSoup(main_page.content, 'html.parser')
    table = soup.find_all('table')[0]
    table = table.children

    uni_list = []
    for tr in table:
        if not isinstance(tr, NavigableString) \
                and not isinstance(list(list(tr.children)[1].children)[0], NavigableString) \
                and not isinstance(list(tr.children)[2], NavigableString)\
                and not isinstance(list(tr.children)[3], NavigableString):

            rank = list(list(tr.children)[0])[0]
            name = list(list(tr.children)[1].children)[0].contents[0]
            # This works don't break it
            location = list(list(tr.children)[2].children)[0].get('src').split('/')[::-1][0].split('.')[0]
            if len(list(list(tr.children)[3])) > 0:
                total_score = list(list(tr.children)[3])[0]
            else:
                total_score = 'NO SCORE'
            pub_score = list(list(tr.children)[4])[0]
            cnci_score = list(list(tr.children)[5])[0]
            ic_score = list(list(tr.children)[6])[0]
            top_score = list(list(tr.children)[7])[0]
            award_score = list(list(tr.children)[8])[0]

            parsed_obj = {
                'name': name,
                'rank': rank,
                'location': location,
                'total_score': total_score,
                'pub_score': pub_score,
                'cnci_score': cnci_score,
                'ic_score': ic_score,
                'top_score': top_score,
                'award_score': award_score
            }

            uni_list.append(parsed_obj)

    return uni_list

# subject_id is the id from the subject object returned form the check_subject_exists function
def get_uni_ranking_data(uni_name, subject_id):
    uni_data = get_ranking_data(subject_id)
    names_list = []
    for obj in uni_data:
        names_list.append(obj['name'])

    fuzzy_name = process.extractOne(uni_name, names_list)[0]
    uni_obj = get_obj_from_attr(uni_data, fuzzy_name)

    return uni_obj

# uni_list: either a list of objects returned from get_uni_ranking_data or a list of strings of uni names
def compare_unis(uni_list, subject_id):
    if all(isinstance(x, dict) for x in uni_list):
        pass
    elif all(isinstance(x, str) for x in uni_list):
        pass
    else:
        raise ValueError('uni_list is not homogenous or follows input format')
