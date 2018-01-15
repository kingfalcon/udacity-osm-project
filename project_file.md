# OpenStreetMap Data Case Study

### Map Area
Cambridge, MA, United States

- [http://www.openstreetmap.org/relation/1933745](http://www.openstreetmap.org/relation/1933745)
- Equivalent OSM data downloaded from Mapzen as a custom extract
 
I recently lived in the Boston area, including two years spent in Cambridge. Cambridge is the area of Boston I know the best, so I'd like to assess the quality of its OSM data. 


## Problems Encountered in the Map
After reviewing a small subset of the Cambridge data, I noticed the following main problems in the data set:

- **Problem 1:** Several of the files had inconsistent names for street type (e.g., Ave, Ave., and Avenue for Avenue). 
- **Problem 2:** There were several cases where the state name was very inconsistent (e.g., MA- Massachussets, MA, ma for Massachusetts). 
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

### Problem 2: Inconsistent state names
To address this issue, I followed a very similar path as for (1): First I created a list of expected values and a mapping dictionary I'd use to fix any issues. After doing that, I reviewed a dictionary of "bad" values so I could know how to proceed. After concluding that these values were not what I wanted in my final data set, I updated my mapping table:

```
mapping = { "MA- MASSACHUSETTS": "Massachusetts",
            "MA": "Massachusetts",
            "ma":"Massachusetts",
          }
```
With this complete, I then wrote an update function that would sub in the desired name when the bad name was encountered:

```
def update_state_name(name, mapping):
    if name in mapping_keys: #If the bad key is in the mapping dictionary, then perform a substitute, otherwise leave as-is
        good = mapping[name]
        return good
    else:
        return name
```
Fortunately, this was sufficient to address the issues. One interesting thing to note relative to Problem 1 is that I did not need to use the regular expression module. In this case, the entire field contained the value of interest (city name) whereas previously we were only looking at the last word in a given string. As a result, this meant we could do direct matches rather than use regular expression to search within the contents of the string. 

### Problem 3: Inconsistent postal codes (zip codes)
The issues in the postal code field were much simpler to resolve, overall. Similar to previous efforts, I build an list of expected zip codes, iterated through the data, and returned zip codes that were not contained. From my personal experience, I quickly realized that something was wrong: many of the zip codes were not from Cambridge, but rather neighboring communities like Somerville, Medford, and Arlington. However, as I reflected on why this issue may have presented itself, I remembered that I obtained the initial OSM file from Mapzen, which gave me all the data within a rectangular set of coordinates. With this in mind, I realized this is perfectly valid data for the region I was considering and opted to augment the expected list with these new zip codes. 

With that resolved, I generated another dictionary of zip codes and realized there was still the issue of nine-digit zip codes whereas my preferred format is five digits. In order to address this, I created an update function that took the five leftmost digits whenever a zip code had length equal to 10 (a nine-digit zip code plus the interior hyphen): 
```
def update_zip(name, mapping):
    elif len(name) == 10: #If the zip is 9-digit format, take the left-most five digits
        return name[0:5]
    else:
        return name
```

Although this approach worked quite well on the selected data set, there is a small, but nonzero chance there are other formats of zip codes that are exactly 10 digits, but are not in the format of a nine-digit zip code. However, I did not encounter this issue in the course of my data cleaning, so I accepted this trade-off in favor of keeping this solution very simple. 

With the zip codes cleaning script written, I proceeded with writing a script to iteratively parse the OSM data, call data cleaning functions as appropriate, and write to CSVs. After doing that, I loaded the CSVs into SQL so I could begin querying the data and learning the summary statistics. 

### Converting the data into CSVs
Once I had written scripts to handle each of the three issues (street_names.py, state.py, zip_codes.py), I proceeded to write a script to iteratively parse the data, call the update functions, and output the results into a series of CSVs. To do this, I first imported a series of modules to help with this goal, including the three scripts I had written:
```
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
```
Given that all of the fields I corrected are tags, I cleaned the data as I was iterating through the tags. Here's an example of what I did for `node_tags`, a process I followed for `ways_tags` as well: 
```
if m:
    split_key = re.split(':',j.get('k'),maxsplit=1)
    tags_dict['id'] = node_attribs['id']
    tags_dict['key'] = split_key[1]
    if split_key[1] == 'state':
        tags_dict['value'] = state.update_state_name(j.get('v'))
    elif split_key[1] == 'street':
        tags_dict['value'] = street_names.update_street_name(j.get('v'))
    elif split_key[1] == 'postcode':
        tags_dict['value'] = zip_code.update_zip(j.get('v'))
    else: 
        tags_dict['value'] = j.get('v')
```
After implementing all the cleaning scripts, I moved onto validation: 
```
if __name__ == '__main__':
    # Note: Validation is ~ 10X slower. For the project consider using a small
    # sample of the map when validating.
    process_map(OSM_PATH, validate=True)
```
Unfortunately, after running for ~20 minutes, the validator spit out an error saying that one of my 'values' contained a null, which was not permitted according to the schema that I loaded for the data set. Specifically, the error was occuring for the data point with id equal to '4913173622'. After investigating the source of the problem, I realized that the raw street name included a trailing space, and my street_name.py script was not properly designed to handle this edge case. As a result, I updated my script and the data set validated successfully. 

# Data Overview and Additional Ideas
In this section, I have included some summary statistics about the dataset, the SQL queries used to obtain them, and some additional thoughts about the data.

### File sizes
```
cambridge.osm ......... 97 MB
cambridge.db .......... 77 MB
nodes.csv ............. 34 MB
nodes_tags.csv ........ 2 MB
ways.csv .............. 5 MB
ways_tags.csv ......... 6 MB
ways_nodes.cv ......... 12 MB  
```  

### Number of nodes
```sql
select count(distinct id) 
from nodes;
```
437289

### Number of ways
```sql
select count(distinct id) 
from ways;
```
75106

### Number of unique users
```sql
select count(distinct uid) 
from 
(select distinct uid from nodes 
union 
select distinct uid from ways);
```
976

### Number of unique cafes

```sql
select count(distinct id) 
from nodes_tags 
where value = 'cafe';
```
177

### Number of unique bars

```sql
select count(distinct id) 
from nodes_tags 
where value = 'bar';
```
44

### Top 10 amenities

```sql
select value, count(distinct id) 
from nodes_tags 
where key = 'amenity' 
group by 1 
order by 2 desc 
limit 10;
```
```
bench,504
restaurant,458
bicycle_parking,232
cafe,177
school,145
library,136
fast_food,122
place_of_worship,95
bicycle_rental,86
waste_basket,81
```


### Top 10 node types

```sql
select b.type, count(distinct a.id) 
from nodes a 
inner join nodes_tags b 
on a.id = b.id 
group by 1 
order by 2 desc 
limit 10;
```
```
regular,16205
addr,1730
gnis,629
source,126
massgis,97
fire_hydrant,64
surveillance,62
camera,58
contact,57
name,48
```

### Top 10 users who have entered in addresses in this data set
```sql
with addresses as ( 
select * 
from nodes a 
inner join nodes_tags b 
on a.id = b.id 
where b.type = 'addr' 
) 

select user, count(distinct id) as num_addresses
from addresses 
group by 1  
order by 2 desc 
limit 10;
```

```
mterry,212
"Peter Dobratz",151
amillar,141
probiscus,104
wheelmap_visitor,68
kalanz,63
FTA,60
MDIV,37
morganwahl,35
sankeytm,31
```
Mterry has contributed the most addresses with 212!

### Other ideas about the data set
As mentioned earlier in the write-up, the city field also featured a host of inconsistent data, including commas, state abbreviations, and city names that weren't entered in title case. In the future, OSM could consider two types of solutions to address this issue: (1) a solution that prevents the bad data from being entered in the first place, and (2) a solution that encourages users to find and fix errors like these. 

For the first type of solution, one idea is to provide data validation checks and/or automatic corrections when the data is manually entered or submitted via API to the OSM database. For example, the OSM database could automatically title case any node corresponding to the city field of an address, or reject a contribution outright if there are extraneous commas. The major benefits of this approach are that the data would likely be cleaner and downstream data cleaning (and therefore analysis) would likely take less time. However, the downside of this approach is that it might be frustrating for frequent contributors: since they are contributing the most, they are likely to run into the most errors. If those most frequent users then stop contributing to OSM altogether out of frustration, it would be a major loss for the site. Here is a [nice discussion on Stack Overflow] (https://stackoverflow.com/questions/8407325/pros-and-cons-catching-database-errors-vs-validating-user-input) about the relative merits of automated data validation. 

For the second type of solution, one idea is to reward users who fix others' data entry issues by creating an on-site badge system that power users could use to show off their dedication to other users on the site. Implementing such a system would be nearly cost-less, and would help ensure that users feel like their contributions are valued. On the flipside, however, implementing such a system could present other issues: the biggest power users might then start editing others work instead of focusing on adding new ways and nodes themselves, which may not be aligned with how OSM wants to engage their power users. For ideas on how to implementate this, we can look to Waze, which provides a [helpful wiki] (https://wiki.waze.com/wiki/Your_Rank_and_Points) explaining how it uses points and badges to encourage certain user actions. 

In order to explore both of these solutions, OSM could A/B test these changes to investigate what impact they have on previously established key performance indicators. 

# Conclusion
As a result of going through this data, I cleaned up a number of things, including inconsistent street types, inconsistent state names, and inconsistent postal codes. Furthermore, while cleaning these three fields, I also observed that the city field could use data auditing and cleaning as well if I had additional time. Finally, I iteratively wrote the cleaned data to CSVs, loaded the CSVs into a SQL database, and used a variety of queries to understand the structure and nature of the data set. Additional work I would like to do includes analyzing how the distribution of amenity types has trended over time to test my hypothesis that the number of cafes and restaurants in Cambridge has increased over the last few years. 
