
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


expected =  ['02118',
    '02119',
    '02120',
    '02130',
    '02134',
    '02135',
    '02445',
    '02446',
    '02447',
    '02467',
    '02108',
    '02114',
    '02115',
    '02116',
    '02215',
    '02128',
    '02129',
    '02150',
    '02151',
    '02152',
    '02124',
    '02126',
    '02131',
    '02132',
    '02136',
    '02109',
    '02110',
    '02111',
    '02113',
    '02121',
    '02122',
    '02124',
    '02125',
    '02127',
    '02210',
    '02138',
    '02139',
    '02140',
    '02141',
    '02142',
    '02238']

#initial mapping
mapping = { #tbd,
            }


#Create list of mapping keys
mapping_keys = []
for k,v in mapping.items():
    mapping_keys.append(k)


def audit_state(state_types, state_name):
    if state_name not in expected:
        state_types[state_name].add(state_name)


def is_zip(elem):
    return (elem.attrib['k'] == "addr:postcode")


def audit(osmfile):
    osm_file = open(osmfile, "r",encoding='utf8')
    state_types = defaultdict(set)
    for event, elem in ET.iterparse(osm_file,events=("start",)):
        if elem.tag == "node" or elem.tag == "way":
            for tag in elem.iter("tag"):
                if is_zip(tag):
                    audit_state(state_types, tag.attrib['v'])
    osm_file.close()
    return state_types
        
def st_types(file):
    st_types = audit(file)
    pprint.pprint(dict(st_types))

def update_zip(name):
    if name in mapping_keys: #If the bad key is in the mapping dictionary, then perform a substitute
        good = mapping[name]
        return good
    elif len(name) == 10: #If the zip is 9-digit format, take the left-most five digits
        return name[0:5]
    else:
        return name

