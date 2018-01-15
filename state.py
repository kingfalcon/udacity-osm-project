
# coding: utf-8

# In[1]:


from collections import defaultdict
import pprint
import re
import pandas as pd
import numpy as np

import xml.etree.ElementTree as ET  # Use cElementTree or lxml if too slow

OSM_FILE = "cambridge.osm"  # Replace this with your osm file
SAMPLE_FILE = "sample.osm"

k = 5 # Parameter: take every k-th top level element

def get_element(osm_file, tags=('node', 'way', 'relation')):
    """Yield element if it is the right type of tag

    Reference:
    http://stackoverflow.com/questions/3095434/inserting-newlines-in-xml-file-generated-via-xml-etree-elementtree-in-python
    """
    context = iter(ET.iterparse(osm_file, events=('start', 'end')))
    _, root = next(context)
    for event, elem in context:
        if event == 'end' and elem.tag in tags:
            yield elem
            root.clear()


with open(SAMPLE_FILE, 'wb') as output:
    output.write(bytes('<?xml version="1.0" encoding="UTF-8"?>\n',encoding='utf-8'))
    output.write(bytes('<osm>\n  ',encoding='utf-8'))

    # Write every kth top level element
    for i, element in enumerate(get_element(OSM_FILE)):
        if i % k == 0:
            output.write(ET.tostring(element, encoding='utf-8'))

    output.write(bytes('</osm>',encoding='utf-8'))

OSMFILE = SAMPLE_FILE
#state_re = re.compile(r'\b\S+\.?$', re.IGNORECASE)


expected = ["Massachusetts"]

#mapping
mapping = { "MA- MASSACHUSETTS": "Massachusetts",
            "MA": "Massachusetts",
            "ma":"Massachusetts",
            "Ma":"Massachusetts",
          }


#Create list of mapping keys
mapping_keys = []
for k,v in mapping.items():
    mapping_keys.append(k)


def audit_state(state_types, state_name):
    if state_name not in expected:
        state_types[state_name].add(state_name)
    #m = state_re.search(state_name)
    #if m:
        #state = m.group()
        #if state not in expected:
            #state_types[state].add(state_name)


def is_state(elem):
    return (elem.attrib['k'] == "addr:state")


def audit(osmfile):
    osm_file = open(osmfile, "r",encoding='utf8')
    state_types = defaultdict(set)
    for event, elem in ET.iterparse(osm_file,events=("start",)):
        if elem.tag == "node" or elem.tag == "way":
            for tag in elem.iter("tag"):
                if is_state(tag):
                    audit_state(state_types, tag.attrib['v'])
    osm_file.close()
    return state_types

        
def st_types(file):
    st_types = audit(file)
    pprint.pprint(dict(st_types))

def update_state_name(name):
    if name in mapping_keys: #If the bad key is in the mapping dictionary, then perform a substitute, otherwise leave as-is
        good = mapping[name]
        return good
    else:
        return name

