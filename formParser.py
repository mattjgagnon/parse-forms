'''
    This Python program scrapes pages to extract form field names, values, and types.

    Name:       Form Parser
    Creator:    Matt Gagnon <mattjgagnon@gmail.com>
    Created:    2012-05-04
    Revised:    2022-09-25
    Version:    1.1
    Python:     3.8.3
'''

import getopt
import logging
logging.basicConfig(
    level=logging.DEBUG,
    filename='formParser.log',
    filemode='w',
    format='%(name)s - %(levelname)s - %(message)s'
)
import sys
import urllib
import urllib.request as urllib2
from bs4 import BeautifulSoup

def main(formUrl):
    data = []

    try:
        page = urllib2.urlopen(formUrl).read()
    except urllib2.URLError as e:
        logging.error('An error occurred:')
        logging.error(e)
        return []
    except ValueError as e:
        logging.error('Unexpected value for URL')
        logging.error(e)
        return []
    else:
        try:
            tree = BeautifulSoup(page, features="html.parser")
        except:
            logging.error('Could not open the page'+formUrl)
            return []
        else:
            print('Trying tp parse forms on '+formUrl+'...')
            forms = tree.findAll('form')
            removeScriptTags(tree)

            if (forms == ''):
                return []

            for form in forms:
                data = getFormData(tree, form)

            return data

def removeScriptTags(tree):
    # extract and remove all script tags in the form
    # as they tend to mess up the parsing of values
    [script.extract() for script in tree('script')]


def getFormData(tree, form):
    data = []

    for superType in ['input', 'select', 'textarea']:
        fieldData = getFieldData(tree, superType)

        if fieldData:
            data.append(fieldData)

    return data

def getFieldData(tree, superType):
    data = []

    for field in tree.find_all(superType):
        fieldData = {
            'name'  : getInputFieldName(field),
            'type'  : getInputFieldType(field),
            'value' : getInputFieldValue(superType, field)
        }

        if fieldData:
            data.append(fieldData)

    return data

def getInputFieldValue(superType, field):
    fieldValue = ''

    if superType == 'input':
        if any('value' in s for s in field.attrs):
            return field['value']
    elif superType == 'select':
        return getSelectFieldValues(field)
    elif superType == 'textarea':
        return field.text

    return fieldValue

def getSelectFieldValues(field):
    fieldValues = {}

    for option in field.contents:
        try:
            # try to assign the value to the key
            # option.text is visible form text
            fieldValue[option.text] = option['value']
        except KeyError as e:
            if option.text:
                fieldValue[option.text] = option.text
        except AttributeError as e:
            pass
        except TypeError as e:
            pass

        fieldValues.append(fieldValue)

    return fieldValues


def getInputFieldName(field):
    if any('name' in s for s in field.attrs):
        return field['name']
    else:
        return field.name

def getInputFieldType(field):
    if field.find('select'):
        return 'select'

    if field.find('textarea'):
        return 'textarea'

    if field.get('type') == None:
        return 'text'
    else:
        return field.get('type')

def getUrl():
    if sys.argv[1:]:
        arg = sys.argv[1:]
        url = arg[0]

        if url.find('http') == -1:
            return 'http://'+url
        else:
            return url
    else:
        return 'https://github.com/mattjgagnon'


if __name__ == "__main__":
    url = getUrl()
    formData = main(url)
    print(formData)
