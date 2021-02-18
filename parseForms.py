'''
    This Python program parses forms to extract the field names and values.

    Name:       Parse Forms
    Creator:    Matt Gagnon <mattjgagnon@gmail.com>
    Created:    2012-05-04
    Revised:
    Version:    1.0
    Python:     2.6
    To do:
    Execution:  fetch a web page with form(s) on it
                use BeautifulSoup to parse the form inputs and values
                return a dictionary object of the information collected
                optionally display the field object
'''

# =============
# CONFIGURATION
# =============
# url     = 'http://www.crmtool.net/WebForm.asp?W=1282&F=1248' # for testing
url     = 'http://google.com' # for testing
debug   = True  # for testing - prints the form tags and field inputs

# =========
# FUNCTIONS
# =========
def parseForms(formUrl, labelWrapper = '', display = False):
    '''
        This function parses form data from the supplied url and returns all
        forms and their inputs on the page as a dictionary.

        The function uses a third-party module named BeautifulSoup.
        Accepts a valid url and a variable for printing the fields.
    '''

    # import the url modules
    import urllib, urllib2

    # import our html parser
    from BeautifulSoup import BeautifulSoup

    # create a dictionary object to hold the forms
    data = []
    fieldInputs = ['input', 'select', 'textarea']

    try:
        # request url and read server response
        page = urllib2.urlopen(formUrl).read()
    except urllib2.URLError, e:
        # check if a reason was given
        if hasattr(e, 'reason'):
            print 'We failed to reach a server.'
            print 'Reason:', e.reason
        # check if there was a code given
        elif hasattr(e, 'code'):
            print 'The server could not fulfill the request.'
            print 'Error code:', e.code
    except ValueError, e:
        print 'unexpected value for URL'
    else:
        try:
            # try to open the data source
            tree = BeautifulSoup(page)
        except:
            # exception occurred
            print 'could not open the page'
        else:
            # find all the forms
            forms = tree.findAll('form')

            # extract and remove all script tags in the form
            # as they tend to mess up the parsing of values
            [script.extract() for script in tree('script')]
            action = ''
            method = ''

            # check if forms exist
            if (forms != ''):
                for form in forms:
                    # check if the form has a method attribute
                    if any('method' in s for s in form.attrs):
                        method = form['method']

                    # check if the form has an action attribute
                    if any('action' in s for s in form.attrs):
                        action = form['action']

                    # get the label associated with the form inputs
                    fieldLabel = getLabel(form, labelWrapper)

                    # print the form start tag
                    if display:
                        printFormStart(action, method)

                    # loop through each form input type
                    for superType in fieldInputs:
                        # loop through each field input
                        for field in tree.findAll(superType):
                            # create a dictionary object of field data
                            fieldData = {}

                            # get a name input attribute, if one exists
                            fieldName = getName(field)

                            # assign the input type (text, checkbox, radio, etc.)
                            # based on the given super type (input, select, textarea)
                            fieldType = getType(field, superType)

                            # check if the input is a standard input
                            if superType == 'input':
                                fieldValue = ''

                                # check if the input has a value attribute
                                if any('value' in s for s in field.attrs):
                                    fieldValue = field['value']

                            # check if the input is a select
                            elif superType == 'select':
                                # create a new dictionary object to hold options
                                fieldValue = {}

                                # loop through the options
                                for option in field.contents:
                                    try:
                                        # try to assign the value to the key
                                        # option.text is visible form text
                                        fieldValue[option.text] = option['value']
                                    except KeyError, e:
                                        if option.text:
                                            fieldValue[option.text] = option.text
                                    except AttributeError, e:
                                        pass
                                    except TypeError, e:
                                        pass

                            # check if the input is a textarea
                            elif superType == 'textarea':
                                # assign the tag text
                                fieldValue = field.text

                            # assign the attribute data to the field
                            fieldData = {
                                'label' : fieldLabel,
                                'name'  : fieldName,
                                'type'  : fieldType,
                                'value' : fieldValue}

                            if display:
                                # print the field input HTML (mainly for testing)
                                printField(fieldLabel, fieldName, fieldType, fieldValue)

                            # check if the data exists and append
                            if fieldData:
                                data.append(fieldData)
                                    # print the form start tag
                    if display:
                        printFormEnd()

            else:
                # no forms exist
                print 'no forms found on the page'

    # return the forms
    return data

def getLabel(form = '', labelWrapper = ''):
    '''
        Need to write this function.
        This function gets the label for a form input control.

        It will search the obvious places first, like <label> and <td>,
        but will also check text surrounding the form input.
    '''
    if labelWrapper == '':
        labelWrapper = 'label'

    labels = []
    fieldLabel = ''

    print '--- all labels ---'
    for fieldLabel in form.findAll(labelWrapper):
        if fieldLabel.text != '&nbsp;':
            labels.append(fieldLabel.text)
            print fieldLabel.text

#    print labels

    return fieldLabel

def getName(field):
    '''
        This function accepts a field input object and returns the name attribute.
    '''

    # check if the field has a name attribute
    if any('name' in s for s in field.attrs):
        fieldName = field['name']
    else:
        fieldName = ''

    return fieldName

def getType(field, superType):
    '''
        This function accepts a field input object and returns the type attribute.
    '''

    # check if type is not in field attributes
    if superType == 'input':
        if field.find('type') != '':
            fieldType = field['type']
        else:
            fieldType = 'text'
    elif superType == 'select':
        fieldType = 'select'
    else:
        fieldType = 'textarea'

    return fieldType

def printFormEnd():
    '''
        This function simply prints an ending HTML form tag.
    '''

    print '</form>'

def printField(fieldLabel, fieldName, fieldType, fieldValue):
    '''
        This is a general function for printing form inputs.
    '''

    if fieldType == 'select':
        printSelect(fieldLabel, fieldName, fieldValue)
    elif fieldType == 'textarea':
        printTextarea(fieldLabel, fieldName, fieldValue)
    else:
        printInput(fieldLabel, fieldName, fieldType, fieldValue)

def printFormStart(action = '', method = 'post'):
    '''
        This function accepts an optional form action and method and prints
        them in an HTML form tag.
    '''

    print '<form action="'+action+'" method="'+method+'">'

def printInput(fieldLabel, fieldName, fieldType, fieldValue):
    '''
        This function accepts name, type, and value field input attributes
        and prints them in an HTML input tag.
    '''

    if fieldType == 'hidden':
        print '<input name="'+fieldName+'" type="'+fieldType+'" value="'+fieldValue+'">'
    else:
        printLabelStart(fieldLabel)
        print '<input name="'+fieldName+'" type="'+fieldType+'" value="'+fieldValue+'">'
        printLabelEnd()

def printLabelEnd():
    '''
        This function simply prints an ending HTML label tag.
    '''

    print '</label>'
    print ''

def printLabelStart(labelText = ''):
    '''
        This function accepts an optional field input label and prints
        an HTML label tag.
    '''

    print '<label>',labelText

def printSelect(fieldLabel, fieldName, fieldValue):
    '''
        This function accepts name and options field input attributes and
        prints then in an HTML select tag.
    '''

    printLabelStart(fieldLabel)
    print '<select name="'+fieldName+'">'

    for option in sorted(fieldValue.items()):
        print '<option value="'+option[1]+'">'+option[0]+'</option>'

    print '</select>'
    printLabelEnd()

def printTextarea(fieldLabel, fieldName, fieldValue):
    '''
        This function accepts name and value field input attributes and
        prints them in an HTML textarea tag.
    '''

    printLabelStart(fieldLabel)
    print '<textarea name="'+fieldName+'">'+fieldValue+'</textarea>'
    printLabelEnd()

# ============
# MAIN PROGRAM
# ============
#formData = parseForms(url, labelWrapper, debug)
formData = parseForms(url, 'td')

print formData
