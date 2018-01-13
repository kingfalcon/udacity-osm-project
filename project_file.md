# OpenStreetMap Data Case Study

### Map Area
Cambridge, MA, United States

- [http://www.openstreetmap.org/relation/1933745](http://www.openstreetmap.org/relation/1933745)
- Equivalent OSM data downloaded from Mapzen as a custom extract
 
I recently lived in the Boston area, including two years spent in Cambridge. Cambridge is the area of Boston I know the best, so I'd like to see how clean its OSM data is. 


## Problems Encountered in the Map
After reviewing a small subset of the Cambridge data, I noticed the following main problems in the data set:

- **Problem 1:** Several of the files had inconsistent names for street type (e.g., Ave, Ave., and Avenue for Avenue). 
- **Problem 2:** There were several cases where the state name was very inconsistent (e.g., MA- Massachussets, MA, ma for Massachusetts). 
- **Problem 3:** Many zip codes contained nine digits vs. the standard five-digit format. 
- **Problem 4:** The city field had several cases where the state was included with the city (e.g., Watertown, MA and Boston, MA), some lowercase city names (e.g., boston), and some addresses in the field (e.g., 2067 Massachusetts Avenue)

Specifically, I sought to correct problems 1-3. With additional time, I would also like to programmatically correct the issues encountered in Problem 4. 

### P1
TBD

### P2
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
