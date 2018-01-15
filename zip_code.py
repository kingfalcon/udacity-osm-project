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
mapping = {}


#Create list of mapping keys
mapping_keys = []
for k,v in mapping.items():
    mapping_keys.append(k)

def update_zip(name):
    if name in mapping_keys: #If the bad key is in the mapping dictionary, then perform a substitute
        good = mapping[name]
        return good
    elif len(name) == 10: #If the zip is 9-digit format, take the left-most five digits
        return name[0:5]
    else:
        return name

