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
def parseForms(formUrl, label_wrapper = '', display = False):
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
                    field_label = getLabel(form, label_wrapper)

                    # print the form start tag
                    if display:
                        printFormStart(action, method)

                    # loop through each form input type
                    for super_type in fieldInputs:
                        # loop through each field input
                        for field in tree.findAll(super_type):
                            # create a dictionary object of field data
                            fieldData = {}

                            # get a name input attribute, if one exists
                            field_name = getName(field)

                            # assign the input type (text, checkbox, radio, etc.)
                            # based on the given super type (input, select, textarea)
                            field_type = getType(field, super_type)

                            # check if the input is a standard input
                            if super_type == 'input':
                                field_value = ''

                                # check if the input has a value attribute
                                if any('value' in s for s in field.attrs):
                                    field_value = field['value']

                            # check if the input is a select
                            elif super_type == 'select':
                                # create a new dictionary object to hold options
                                field_value = {}

                                # loop through the options
                                for option in field.contents:
                                    try:
                                        # try to assign the value to the key
                                        # option.text is visible form text
                                        field_value[option.text] = option['value']
                                    except KeyError, e:
                                        if option.text:
                                            field_value[option.text] = option.text
                                    except AttributeError, e:
                                        pass
                                    except TypeError, e:
                                        pass

                            # check if the input is a textarea
                            elif super_type == 'textarea':
                                # assign the tag text
                                field_value = field.text

                            # assign the attribute data to the field
                            fieldData = {
                                'label' : field_label,
                                'name'  : field_name,
                                'type'  : field_type,
                                'value' : field_value}

                            if display:
                                # print the field input HTML (mainly for testing)
                                printField(field_label, field_name, field_type, field_value)

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

def getLabel(form = '', label_wrapper = ''):
    '''
        Need to write this function.
        This function gets the label for a form input control.

        It will search the obvious places first, like <label> and <td>,
        but will also check text surrounding the form input.
    '''
    if label_wrapper == '':
        label_wrapper = 'label'

    labels = []
    field_label = ''

    print '--- all labels ---'
    for field_label in form.findAll(label_wrapper):
        if field_label.text != '&nbsp;':
            labels.append(field_label.text)
            print field_label.text

#    print labels

    return field_label

def getName(field):
    '''
        This function accepts a field input object and returns the name attribute.
    '''

    # check if the field has a name attribute
    if any('name' in s for s in field.attrs):
        field_name = field['name']
    else:
        field_name = ''

    return field_name

def getType(field, super_type):
    '''
        This function accepts a field input object and returns the type attribute.
    '''

    # check if type is not in field attributes
    if super_type == 'input':
        if field.find('type') != '':
            field_type = field['type']
        else:
            field_type = 'text'
    elif super_type == 'select':
        field_type = 'select'
    else:
        field_type = 'textarea'

    return field_type

def printFormEnd():
    '''
        This function simply prints an ending HTML form tag.
    '''

    print '</form>'

def printField(field_label, field_name, field_type, field_value):
    '''
        This is a general function for printing form inputs.
    '''

    if field_type == 'select':
        printSelect(field_label, field_name, field_value)
    elif field_type == 'textarea':
        printTextarea(field_label, field_name, field_value)
    else:
        printInput(field_label, field_name, field_type, field_value)

def printFormStart(action = '', method = 'post'):
    '''
        This function accepts an optional form action and method and prints
        them in an HTML form tag.
    '''

    print '<form action="'+action+'" method="'+method+'">'

def printInput(field_label, field_name, field_type, field_value):
    '''
        This function accepts name, type, and value field input attributes
        and prints them in an HTML input tag.
    '''

    if field_type == 'hidden':
        print '<input name="'+field_name+'" type="'+field_type+'" value="'+field_value+'">'
    else:
        printLabelStart(field_label)
        print '<input name="'+field_name+'" type="'+field_type+'" value="'+field_value+'">'
        printLabelEnd()

def printLabelEnd():
    '''
        This function simply prints an ending HTML label tag.
    '''

    print '</label>'
    print ''

def printLabelStart(label_text = ''):
    '''
        This function accepts an optional field input label and prints
        an HTML label tag.
    '''

    print '<label>',label_text

def printSelect(field_label, field_name, field_value):
    '''
        This function accepts name and options field input attributes and
        prints then in an HTML select tag.
    '''

    printLabelStart(field_label)
    print '<select name="'+field_name+'">'

    for option in sorted(field_value.items()):
        print '<option value="'+option[1]+'">'+option[0]+'</option>'

    print '</select>'
    printLabelEnd()

def printTextarea(field_label, field_name, field_value):
    '''
        This function accepts name and value field input attributes and
        prints them in an HTML textarea tag.
    '''

    printLabelStart(field_label)
    print '<textarea name="'+field_name+'">'+field_value+'</textarea>'
    printLabelEnd()

# ============
# MAIN PROGRAM
# ============
#formData = parseForms(url, label_wrapper, debug)
formData = parseForms(url, 'td')

#print formData
