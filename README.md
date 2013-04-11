# 5C Course API

Check out the 5C courses being offered this Fall!  <br><br>
The [root URL](http://course-api.herokuapp.com) lists the departments covered so far. If you want a specific department, just request that path!  <br><br>
Let's say you want to find all [Literature](http://course-api.herokuapp.com/lit) classes taught on Fridays. No problem!

### Python example

1.    Import a library which will get the data for you.  
      `import urllib2`

2.    Grab the data and store it in a variable.  
      `request = urllib2.urlopen('http://course-api.herokuapp.com/econ')`

3.    The request data is stored in a format called [JSON](http://en.wikipedia.org/wiki/JSON), but Python has a library which converts that JSON into a normal Python dict. Let's do that now!  
      `import json`  
      `lit_data = json.load(request)`  
`for course in lit_data:`  
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;`if 'F' in course['days']:`  
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;`print course`  

### Routes

You'll probably want the [master list](http://course-api.herokuapp.com/master) of all courses in all departments, so use the route: `http://course-api.herokuapp.com/master`<br>

And, like the Literature example above, you can access a specific department by requesting: `http://course-api.herokuapp.com/<dept_name_here>`<br>
<br>
Finally, you can navigate to a specific [course](http://course-api.herokuapp.com/art/120) or even a specific [section](http://course-api.herokuapp.com/art/120/2) with the following format: `http://course-api.herokuapp.com/<dept>/<course_id>/<section_id>`<br>