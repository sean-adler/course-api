# 5C Course API

Check out the 5C courses being offered this Fall.  
The root lists the departments covered so far. If you want a specific department, just request that path!  
Let's say you want to find all Friday classes taught in the Econ departments at the 5Cs. No problem!

### Python example

1.    Import a library which will grab the data for you.  
      `import urllib2`

2.    Grab the data and store it in a variable.  
      `request = urllib2.urlopen('http://course-api.herokuapp.com/econ')`

3.    Now load it into a Python dict. Happy hacking!  
      `import json`  
      `econ_data = json.load(request)`  
`for course in econ_data:`  
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;`if 'F' in course['days']:`  
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;`print course`  

### Routes

You can access a specific department by requesting `http://course-api.herokuapp.com/<dept>`.<br>
<br>
If you want the master list of all courses in all deparments, request `http://course-api.herokuapp.com/master`.<br>
<br>
Finally, you can navigate to specific courses or sections with the following format: `http://course-api.herokuapp.com/<dept>/<course_id>/<section_id>`.<br>