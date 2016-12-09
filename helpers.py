import os
import multiprocessing
import time
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

n = 1000
cpu_count = multiprocessing.cpu_count()
pool = multiprocessing.Pool(cpu_count * 2)

tree1 = DOMTree(html1)
tree2 = DOMTree(html2)

dumb_sequence = dumb_sequence_for(tree1, tree2)
initial_sequences = sequences_from_dumb_sequence(dumb_sequence, n=n)
entire_fitnesses = []

start = time.time()
def log(i):
    print(
        'evaluating {} sequences took {} seconds'
        .format(i + 1, time.time() - start)
    )

for i, s in enumerate(initial_sequences):
    entire_fitnesses.append(s.evaluate(html1, html2, base=dumb_sequence))
    if i % 50 == 0:
        log(i)
