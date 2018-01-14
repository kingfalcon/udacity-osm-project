# OpenStreetMap Data Case Study

### Map Area
Cambridge, MA, United States

- [http://www.openstreetmap.org/relation/1933745](http://www.openstreetmap.org/relation/1933745)
- Equivalent OSM data downloaded from Mapzen as a custom extract
 
I recently lived in the Boston area, including two years spent in Cambridge. Cambridge is the area of Boston I know the best, so I'd like to see how clean its OSM data is. 


## Problems Encountered in the Map
After reviewing a small subset of the Cambridge data, I noticed the following main problems in the data set:

- **Problem 1:** Several of the files had inconsistent names for street type (e.g., Ave, Ave., and Avenue for Avenue). 
- **Problem 2:** There were several cases where the city name was very inconsistent (e.g., MA- Massachussets, MA, ma for Massachusetts). 
- **Problem 3:** Many zip codes contained nine digits vs. the standard five-digit format. 
- **Problem 4:** The city field had several cases where the state was included with the city (e.g., Watertown, MA and Boston, MA), some lowercase city names (e.g., boston), and some addresses in the field (e.g., 2067 Massachusetts Avenue)

Specifically, I sought to correct problems 1-3. With additional time, I would also like to programmatically correct the issues encountered in Problem 4. 

### Problem 1: Inconsistent street types
To audit the data, first I did four things: (1) used a helper function to analyze every 5 rows of data, (2) built a list of expected street types, (3) used regular expression to scan the last word in the street name, and (4) created and printed a dictionary of all street types that were not in the expected dictionary. 

```
def audit_street_type(street_types, street_name):
    m = street_type_re.search(street_name)
    if m:
        street_type = m.group()
        if street_type not in expected:
            street_types[street_type].add(street_name)
```
Printing the dictionary that resulted from this auditing, I quickly realized that there were 3 major types of issues: (1) inconsistent capitalization, (2) streets with numbers at the end (e.g., 18th floor), and (3) streets with no street type. To resolve (1), I built a mapping dictionary with the wrong types as keys and the corrected types as values:

```
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
```

Regarding issue (2), numbers at the end of the street name, I ultimately elected to leave most of these alone as I felt values like "Suite 303" and "18th floor" could be important parts of the address for some businesses. In one case, though ("Kendall Square - 3"), the number didn't make much sense based on my intuition, and I opted to truncate to remove the number entirely. 

For issue (3), I opted to leave these rows alone as I wasn't sure what street type they truly deserved. With additional time, I would either investigate these more deeply or exclude them entirely from the resulting CSVs. 

After going through this process on the street address field, I used pandas and defaultdict to create a sorted Dataframe demonstrating how frequently each tag type appears:

```
distinct_keys = defaultdict(int)
for _,elem in ET.iterparse(SAMPLE_FILE):
    try:
        distinct_keys[elem.attrib['k']] += 1
    except:
        pass

k_df = pd.DataFrame.from_dict(distinct_keys,orient='index')
print(k_df.sort_values(by=0,ascending=False).head(50))
```
After a manual review of this data, I decided that I wanted to examine city name and postal code, as they were well-represented in the smaller data set (409 and 370 occurrences, respectively). 

### Problem 2: Inconsistent city names
TBD

### Problem 3: Inconsistent postal codes (zip codes)
TBD

# Data Overview and Additional Ideas
In this section, I have included some summary statistics about the dataset, the SQL queries used to obtain them, and some additional thoughts about the data.

### File sizes
```
cambridge.osm ......... TBD MB
cambridge.db .......... TBD MB
nodes.csv ............. TBD MB
nodes_tags.csv ........ TBD MB
ways.csv .............. TBD MB
ways_tags.csv ......... TBD MB
ways_nodes.cv ......... TBD MB  
```  

### Number of nodes
```
sqlite> --update with SQL code;
```
TBD #

### Number of ways
```
sqlite> --update with SQL code;
```
TBD #

### Number of unique users
```sql
--update with SQL code;
```
TBD #

### Number of unique cafes

```sql
sqlite> --update with SQL code;
```

```sql
--update with SQL results;
```

### Number of unique bars

```sql
sqlite> --update with SQL query;
```

```sql
--update with sql results
```

# Conclusion
TBD
