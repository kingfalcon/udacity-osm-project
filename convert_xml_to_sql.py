
# coding: utf-8

# In[3]:


import state
import zip_code
import street_names
import csv
import codecs
import pprint
import re
import xml.etree.cElementTree as ET
import cerberus
import schema

OSM_PATH = "cambridge.osm"

NODES_PATH = "nodes.csv"
NODE_TAGS_PATH = "nodes_tags.csv"
WAYS_PATH = "ways.csv"
WAY_NODES_PATH = "ways_nodes.csv"
WAY_TAGS_PATH = "ways_tags.csv"

LOWER_COLON = re.compile(r'^([a-z]|_)+:([a-z]|_)+')
PROBLEMCHARS = re.compile(r'[=\+/&<>;\'"\?%#$@\,\. \t\r\n]')

SCHEMA = schema.schema

# Make sure the fields order in the csvs matches the column order in the sql table schema
NODE_FIELDS = ['id', 'lat', 'lon', 'user', 'uid', 'version', 'changeset', 'timestamp']
NODE_TAGS_FIELDS = ['id', 'key', 'value', 'type']
WAY_FIELDS = ['id', 'user', 'uid', 'version', 'changeset', 'timestamp']
WAY_TAGS_FIELDS = ['id', 'key', 'value', 'type']
WAY_NODES_FIELDS = ['id', 'node_id', 'position']


def shape_element(element, node_attr_fields=NODE_FIELDS, way_attr_fields=WAY_FIELDS,
                  problem_chars=PROBLEMCHARS, default_tag_type='regular'):
    """Clean and shape node or way XML element to Python dict"""

    node_attribs = {}
    way_attribs = {}
    way_nodes = []
    tags = []  # Handle secondary tags the same way for both node and way elements
    if element.tag == 'node':
        for i in node_attr_fields:
            node_attribs[i] = element.get(i)
        for j in element.iter('tag'):  
            tags_dict = {}
            if re.match(problem_chars,j.get('k')):
                continue
            m = re.match(LOWER_COLON,j.get('k'))
            if m:
                split_key = re.split(':',j.get('k'),maxsplit=1)
                tags_dict['id'] = node_attribs['id']
                tags_dict['key'] = split_key[1]
                if split_key[1] == 'state': #call update fuctions to perform data cleaning
                    tags_dict['value'] = state.update_state_name(j.get('v'))
                elif split_key[1] == 'street':
                    tags_dict['value'] = street_names.update_street_name(j.get('v'))
                elif split_key[1] == 'postcode':
                    tags_dict['value'] = zip_code.update_zip(j.get('v'))
                else: 
                    tags_dict['value'] = j.get('v')
                tags_dict['type'] = split_key[0]
            else:
                tags_dict['id'] = node_attribs['id']
                tags_dict['key'] = j.get('k')
                tags_dict['value'] = j.get('v')
                tags_dict['type'] = 'regular'
            tags.append(tags_dict)
        return {'node': node_attribs, 'node_tags': tags}
    elif element.tag == 'way':
        for i in way_attr_fields:
            way_attribs[i] = element.get(i)
        count = 0
        for x in element.iter('nd'):
            wn_dict = {}
            wn_dict['id'] = way_attribs['id']
            wn_dict['node_id'] = x.get('ref')
            wn_dict['position'] = count
            count += 1
            way_nodes.append(wn_dict)
        for j in element.iter('tag'):
            way_tags_dict = {}
            if re.match(problem_chars,j.get('k')):
                continue
            m = re.match(LOWER_COLON,j.get('k'))
            if m:
                split_key = re.split(':',j.get('k'),maxsplit=1)
                way_tags_dict['id'] = way_attribs['id']
                way_tags_dict['key'] = j.get('k')
                if split_key[1] == 'state': #call update functions to perform data cleaning
                    way_tags_dict['value'] = state.update_state_name(j.get('v'))
                elif split_key[1] == 'street':
                    way_tags_dict['value'] = street_names.update_street_name(j.get('v'))
                elif split_key[1] == 'postcode':
                    way_tags_dict['value'] = zip_code.update_zip(j.get('v'))
                else: 
                    way_tags_dict['value'] = j.get('v')
                way_tags_dict['type'] = split_key[0]
            else:
                way_tags_dict['id'] = way_attribs['id']
                way_tags_dict['key'] = j.get('k')
                way_tags_dict['value'] = j.get('v')
                way_tags_dict['type'] = 'regular'
            tags.append(way_tags_dict)
        return {'way': way_attribs, 'way_nodes': way_nodes, 'way_tags': tags}


# ================================================== #
#               Helper Functions                     #
# ================================================== #
def get_element(osm_file, tags=('node', 'way', 'relation')):
    """Yield element if it is the right type of tag"""

    context = ET.iterparse(osm_file, events=('start', 'end'))
    _, root = next(context)
    for event, elem in context:
        if event == 'end' and elem.tag in tags:
            yield elem
            root.clear()


def validate_element(element, validator, schema=SCHEMA):
    """Raise ValidationError if element does not match schema"""
    if validator.validate(element, schema) is not True:
        field, errors = next(iter(validator.errors.items())) 
        message_string = "\nElement of type '{0}' has the following errors:\n{1}"
        error_string = pprint.pformat(errors)
        
        raise Exception(message_string.format(field, error_string))


class UnicodeDictWriter(csv.DictWriter, object):
    """Extend csv.DictWriter to handle Unicode input"""

    def writerow(self, row):
        super(UnicodeDictWriter, self).writerow(row)

    def writerows(self, rows):
        for row in rows:
            self.writerow(row)


# ================================================== #
#               Main Function                        #
# ================================================== #
def process_map(file_in, validate):
    """Iteratively process each XML element and write to csv(s)"""

    with codecs.open(NODES_PATH, 'w',encoding='utf8') as nodes_file,         codecs.open(NODE_TAGS_PATH, 'w',encoding='utf8') as nodes_tags_file,         codecs.open(WAYS_PATH, 'w',encoding='utf8') as ways_file,         codecs.open(WAY_NODES_PATH, 'w',encoding='utf8') as way_nodes_file,         codecs.open(WAY_TAGS_PATH, 'w',encoding='utf8') as way_tags_file:

        nodes_writer = UnicodeDictWriter(nodes_file, NODE_FIELDS)
        node_tags_writer = UnicodeDictWriter(nodes_tags_file, NODE_TAGS_FIELDS)
        ways_writer = UnicodeDictWriter(ways_file, WAY_FIELDS)
        way_nodes_writer = UnicodeDictWriter(way_nodes_file, WAY_NODES_FIELDS)
        way_tags_writer = UnicodeDictWriter(way_tags_file, WAY_TAGS_FIELDS)

        nodes_writer.writeheader()
        node_tags_writer.writeheader()
        ways_writer.writeheader()
        way_nodes_writer.writeheader()
        way_tags_writer.writeheader()

        validator = cerberus.Validator()

        for element in get_element(file_in, tags=('node', 'way')):
            el = shape_element(element)
            if el:
                if validate is True:
                    validate_element(el, validator)

                if element.tag == 'node':
                    nodes_writer.writerow(el['node'])
                    node_tags_writer.writerows(el['node_tags'])
                elif element.tag == 'way':
                    ways_writer.writerow(el['way'])
                    way_nodes_writer.writerows(el['way_nodes'])
                    way_tags_writer.writerows(el['way_tags'])


if __name__ == '__main__':
    # Note: Validation is ~ 10X slower. For the project consider using a small
    # sample of the map when validating.
    process_map(OSM_PATH, validate=False)

