
# coding: utf-8

# In[2]:


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
street_type_re = re.compile(r'\b\S+\.?$', re.IGNORECASE)


expected = ["Street", "Avenue", "Boulevard", "Drive", "Court", "Place", "Square", "Lane", "Road", 
            "Trail", "Parkway", "Commons","Terrace"]

#mapping
mapping = { "St": "Street",
            "St.": "Street",
            "Ave":"Avenue",
            "Ave.":"Avenue",
            "Rd.":"Road",
            "Rd":"Road",
            "Ct":"Court",
            "Ct.":"Court",
            "Pkwy":"Parkway"
            }


#Create list of mapping keys
mapping_keys = []
for k,v in mapping.items():
    mapping_keys.append(k)


def audit_street_type(street_types, street_name):
    m = street_type_re.search(street_name)
    if m:
        street_type = m.group()
        if street_type not in expected:
            street_types[street_type].add(street_name)


def is_street_name(elem):
    return (elem.attrib['k'] == "addr:street")


def audit(osmfile):
    osm_file = open(osmfile, "r",encoding='utf8')
    street_types = defaultdict(set)
    for event, elem in ET.iterparse(osm_file,events=("start",)):
        if elem.tag == "node" or elem.tag == "way":
            for tag in elem.iter("tag"):
                if is_street_name(tag):
                    audit_street_type(street_types, tag.attrib['v'])
    osm_file.close()
    return street_types
      
    
def st_types(file):
    st_types = audit(file)
    pprint.pprint(dict(st_types))

    
def update_street_name(name):
    m = street_type_re.search(name)
    if name == 'argus place':
        return name.title()
    elif name == 'Kendall Square - 3':
        return 'Kendall Square'
    elif m:
        bad_suffix = m.group()
        if m.group() in mapping_keys: #If the bad key is in the mapping dictionary, then perform a substitute, otherwise leave as-is
            good_suffix = mapping[bad_suffix]
            return re.sub(bad_suffix,good_suffix,name)
        else:
            return name
    else:
        return name

