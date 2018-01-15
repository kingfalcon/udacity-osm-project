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

def update_state_name(name):
    if name in mapping_keys: #If the bad key is in the mapping dictionary, then perform a substitute, otherwise leave as-is
        good = mapping[name]
        return good
    else:
        return name

