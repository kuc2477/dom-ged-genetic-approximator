import requests
from dgg.types import DOMTree, Step

# html = requests.get('https://en.wikipedia.org/wiki/Hamming_distance').content.strip()
html = '''
<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.1//EN"
"http://www.w3.org/TR/xhtml11/DTD/xhtml11.dtd">
<html xmlns="http://www.w3.org/1999/xhtml" xml:lang="en">
<head>
<title>Your page title here</title>
</head>
<body>
<h1>Your major heading here</h1>
<p>
This is a regular text paragraph.
</p>
<ul>
<li>
First bullet of a bullet list.
</li>
<li>
This is the <em>second</em> bullet. 
</li>
</ul>
</body>
</html>
'''
tree = DOMTree(html)
append_step = Step(Step.A, content='asdfasdfasdfasdfasdf')
delete_step = Step(Step.D)
