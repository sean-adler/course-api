# 5C Course API

Check out the 5C courses being offered this Fall.  
The root lists the departments covered so far. If you want a specific department, just request that path!  
Let's say you want to find all Friday classes taught in the Econ departments at the 5Cs. No problem!

### Python instructions

1.    Import a library which will grab the data for you.  
      `import urllib2`

2.    Grab the data and store it in a variable.  
      `request = urllib2.urlopen('http://course-api.herokuapp.com/econ')`

3.    Now load it into a Python dict, and happy hacking!  
      `import json`  
      `data = json.load(request)`  
`for course in data['econ']:`  
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;`if 'F' in course['days']:`  
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;`print course`  