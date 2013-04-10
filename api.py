from flask import Flask, abort, render_template
import requests
from bs4 import BeautifulSoup
from pprint import pprint
import time
import json
import os
import re
import threading
import boto
from boto.s3.key import Key
from ConfigParser import ConfigParser


#############
## GLOBALS ##
#############

PARSER = ConfigParser()
PARSER.read('app.cfg')
AWS_ACCESS_KEY = PARSER.get('aws', 'AWS_ACCESS_KEY')
AWS_SECRET_ACCESS_KEY = PARSER.get('aws', 'AWS_SECRET_ACCESS_KEY')

## Set up AWS global vars used to update our json data file
CONN = boto.connect_s3(AWS_ACCESS_KEY,
                       AWS_SECRET_ACCESS_KEY)
BUCKET = CONN.get_bucket('course-api')

## Update DEPARTMENTS dict once a day
LAST_UPDATE = time.time()
UPDATE_FREQ = 24*60*60


## Set up global application object and the global course dictionary
APP = Flask(__name__)
DEPARTMENTS = {}

BASEURL = 'https://portal.claremontmckenna.edu/ics/Portlets/CRM/CXWebLinks/Port\
let.CXFacultyAdvisor/CXFacultyAdvisorPage.aspx?SessionID={25715df1-32b9-42bf-90\
33-e5630cfbf34a}&MY_SCP_NAME=/cgi-bin/course/pccrscatarea.cgi&DestURL=http://cx\
-cmc.cx.claremont.edu:51081/cgi-bin/course/pccrslistarea.cgi?crsarea=%s&yr=2013\
&sess=FA'

DEPT_IDS = 'CSCI DANC ECON BIOL CHEM ENGR GOVT PHIL LIT MATH \
PSYC HIST ART'.split()
DEPT_TRS = []


###############
## FUNCTIONS ##
###############

def create_list(dept_id):
    """Takes as input the name of a department `dept_id' and creates a list
       of dictionaries, each containing information for one course in that
       department."""
    r = requests.get(BASEURL % dept_id)
    soup = BeautifulSoup(r.text)
    table = soup.find_all('table')[-1]  # last table is `All Sections'
    DEPT_TRS = table.find_all('tr', class_='glb_data_dark')

    course_list = []

    for i,t in enumerate(DEPT_TRS):
        course = course_dict(get_td_tags(t), i, DEPT_TRS)
        if course not in course_list:
            course_list.append(course)

    for c in course_list:  # remove `None' values b/c of crosslists
        if not c: course_list.remove(c)

    return course_list

def abort_if_dept_doesnt_exist(dept_id):
    if dept_id not in DEPARTMENTS:
        abort(404, message="Department %s doesn't exist" % dept_id)

def get_list(dept_id):
    """Takes as input the name of a department `dpt_id' and returns its value
       in the global DEPARTMENTS dictionary. We assume we've already populated
       this global dict with values using `create_list()'."""
    abort_if_dept_doesnt_exist(dept_id)
    return DEPARTMENTS[dept_id]

def remove_spaces(string):
    """Returns a string, truncated at the first occurrence of two consecutive
       spaces."""
    return string[:string.find('  ')]

def get_td_tags(tr_tag):
    """Takes a <tr> tag as input and returns all the <td> tags
       contained inside. Strips all whitespace and the `Textbook Info'
       string after the course title."""
    tds = [str(td.text.strip()) for td in tr_tag.find_all('td')]
    tds[-1] = remove_spaces(tds[-1])
    return tds

## EDGE CASES:
    ## <tr> of length 12 (lab):
       ## missing `start' and `end' fields
       ## insert(-1, 'N/A') twice
    
    ## <tr> of length 8 (lab):
       ## missing `course' (course is blank), `section', `instructor',
       ##   `reg_limit', `status', 'hours',
    
    ## <tr> of length 7 (crosslisted):
       ## throw it out? or make a note in original course's tag,
       ## which is the immediately previous <tr> tag?

def course_dict(td_tags, index, dept_trs):
    """Takes as input a <tr> tag representing a 5C course, and returns
       a dict containing the course's attributes:
       `course'
       `section'
       `instructor'
       `reg_limit'
       `status'
       `hours'
       `campus'
       `bldg'
       `room'
       `days'
       `start'
       `end'
       `title'
    And returns placeholder values ('N/A' or '') for any attribute that
    does not exist in the <tr> tag."""
    length = len(td_tags)
    course = {}

    if length == 6:
        ## Lab
        prev_course = get_td_tags(dept_trs[index-1])
        course['course'] = remove_spaces(prev_course[0])  # add `lab' to this field?
        course['section'] =  prev_course[1]
        course['instructor'] = prev_course[2]
        course['reg_limit'] = prev_course[3]
        course['status'] = prev_course[4]
        course['hours'] = 'N/A'
        course['campus'] = td_tags[1]
        course['bldg'] = td_tags[2]
        course['room'] = td_tags[3]
        course['days'] = 'TBA'
        course['start'] = 'TBA'
        course['end'] = 'TBA'
        course['title'] = td_tags[5]
    
    elif length == 7:
        # Crosslisted course -- decide what to do here
        # Example: CS 140 is crosslisted as Math 168.
        # Store a pointer to Math 168 in the CS 140 course, or ignore it?
        return
    
    elif length == 8:
        prev_course = get_td_tags(dept_trs[index-1])
        course['course'] = remove_spaces(prev_course[0])  # add `lab' to this field?
        course['section'] =  prev_course[1]
        course['instructor'] = prev_course[2]
        course['reg_limit'] = prev_course[3]
        course['status'] = prev_course[4]
        course['hours'] = 'N/A'
        course['campus'] = td_tags[1]
        course['bldg'] = td_tags[2]
        course['room'] = td_tags[3]
        course['days'] = td_tags[4].replace('-', '')
        course['start'] = td_tags[5]
        course['end'] = td_tags[6]
        course['title'] = td_tags[7]
        return course
    
    elif length == 12:
        course['course'] = remove_spaces(td_tags[0])
        course['section'] = td_tags[1]
        course['instructor'] = td_tags[2]
        course['reg_limit'] = td_tags[3]
        course['status'] = td_tags[4]
        course['hours'] = td_tags[5]
        course['campus'] = td_tags[7]
        course['bldg'] = td_tags[8]
        course['room'] = td_tags[9]
        course['days'] = td_tags[10].replace('-', '')
        course['start'] = 'N/A'
        course['end'] = 'N/A'
        course['title'] = td_tags[11]
        return course
    
    elif length == 14:
        course['course'] = remove_spaces(td_tags[0])
        course['section'] = td_tags[1]
        course['instructor'] = td_tags[2]
        course['reg_limit'] = td_tags[3]
        course['status'] = td_tags[4]
        course['hours'] = td_tags[5]
        course['campus'] = td_tags[7]
        course['bldg'] = td_tags[8]
        course['room'] = td_tags[9]
        course['days'] = td_tags[10].replace('-', '')
        course['start'] = td_tags[11]
        course['end'] = td_tags[12]
        course['title'] = td_tags[13]
        return course
    
    else:
        print 'oops - %d inner <td> tags at index %d' % (length, index)
        return {}

def update_depts_if_necessary():
    global LAST_UPDATE
    global UPDATE_FREQ

    if LAST_UPDATE + UPDATE_FREQ < int(time.time()):  # scrape every 1 day
        LAST_UPDATE = time.time()
        thread = threading.Thread(target=scrape_and_update_s3)
        thread.start()

def scrape_and_update_s3():
    global DEPARTMENTS
    
    k = Key(BUCKET, 'api-json')
    DEPARTMENTS = update_departments(DEPT_IDS)
    k.set_contents_from_string(json.dumps(DEPARTMENTS))

def update_departments(dept_ids):
    """Takes as input a list of departments `dept_ids' and returns a dictionary
       of lists, each list containing dictionaries, one for each course in that
       department. The result is a dictionary we can index into, given a proper
       id."""
    t1 = time.time()
    DEPARTMENTS = {}
    for d in dept_ids:
        print d
        DEPARTMENTS[d] = create_list(d)
    print time.time() - t1
    return DEPARTMENTS

def erase_data():
    """Erases the data of the `api-json' file on AWS."""
    k = Key(BUCKET, 'api-json')
    k.set_contents_from_string('')

def find_course(dept_id, course_id):
    courses = []
    pattern = r'[0-9]+'
    
    for course in DEPARTMENTS[dept_id.upper()]:
        match = re.findall(pattern, course_id)
        if match and match[0] in course['course']:
            courses.append(course)
    return courses

def find_course_and_section(dept_id, course_id, section):
    sections = []
    for course in find_course(dept_id, course_id):
        if course['section'] == section:
            sections.append(course)
    return sections

def abort_if_dept_doesnt_exist(dept_id):
    if dept_id.upper() not in DEPARTMENTS:
        abort(404)

def jsonify(*args):
    return APP.response_class(json.dumps(*args, indent=2),
                              mimetype='application/json')


## Initially populate our depts dictionary
if DEPARTMENTS == {}:
    DEPARTMENTS = update_departments(DEPT_IDS)


############
## ROUTES ##
############

@APP.route('/')
def index():
    update_depts_if_necessary()
    index_dict = { 'departments':
                   ['/'+k.lower() for k in DEPARTMENTS.keys()]
                 }
    return jsonify(index_dict)

@APP.route('/<dept_id>/')
def show_department(dept_id):
    update_depts_if_necessary()
    abort_if_dept_doesnt_exist(dept_id)
    dept_dict = jsonify(DEPARTMENTS[dept_id.upper()])
    return dept_dict

@APP.route('/<string:dept_id>/<string:course_id>/')
def show_course(dept_id, course_id):
    update_depts_if_necessary()
    ## All course IDs are 3 digits; fix if necessary
    while len(course_id) < 3:
        course_id = '0' + course_id

    course_dict = find_course(dept_id, course_id)
    return jsonify(course_dict)
    # TODO -- 404 if bad input

@APP.route('/<string:dept_id>/<string:course_id>/<string:section>/')
def show_course_and_section(dept_id, course_id, section):
    update_depts_if_necessary()
    ## All course IDs are 3 digits; fix if necessary
    while len(course_id) < 3:
        course_id = '0' + course_id

    ## All section IDs are 2 digits; fix if necessary
    if len(section) < 2:
        section = '0' + section

    section_dict = find_course_and_section(dept_id, course_id, section)
    return jsonify(section_dict)

@APP.route('/readme')
def readme():
    return render_template('README.html')


def deploy(heroku=True):
    """Simple deploy script -- we use different host/port values depending on
       if we want to test this locally, or actually push it to Heroku."""
    if heroku is True:
        if __name__ == '__main__':
            ## Bind to PORT if defined, otherwise default to 5000.
            port = int(os.environ.get('PORT', 5000))
            APP.run(host='0.0.0.0', port=port)
    else:
        ## We run the app locally:
        if __name__ == '__main__':
            APP.run(debug=True)

deploy(heroku=True)
