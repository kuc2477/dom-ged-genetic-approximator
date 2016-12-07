import random
import requests
from dgg.types import DOMTree, Step
from dgg.logics import *

# html = requests.get('https://en.wikipedia.org/wiki/Hamming_distance').content.strip()
html1 = '''
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

html2 = '''
<HTML>
<HEAD>
<TITLE>Your Title Here</TITLE>
</HEAD>
<BODY BGCOLOR="FFFFFF">
<CENTER><IMG SRC="clouds.jpg" ALIGN="BOTTOM"> </CENTER>
<HR>
<a href="http://somegreatsite.com">Link Name</a>
is a link to another nifty site
<H1>This is a Header</H1>
<H2>This is a Medium Header</H2>
Send me mail at <a href="mailto:support@yourcompany.com">
support@yourcompany.com</a>.
<P> This is a new paragraph!
<P> <B>This is a new paragraph!</B>
<BR> <B><I>This is a new sentence without a paragraph break, in bold italics.</I></B>
<HR>
</BODY>
</HTML>
'''

tree1 = DOMTree(html1)
tree2 = DOMTree(html2)
append_step = Step(Step.A, len(tree1), content='asdfasdfasdfasdfasdf')
delete_step = Step(Step.D, len(tree1))
dumb_steps = dumb_deletion_steps_for(tree1)
