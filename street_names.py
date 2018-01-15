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

