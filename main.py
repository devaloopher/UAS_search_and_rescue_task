print("UAS Image Processing Task for Round 2 \n")

#processing criteria

#adding dictionaries
age_score = {"children_stars" : 3, "elderly_triangle" : 2, "adults_square" : 1}
severity_score = {"severe_red" : 3, "mild_yellow" : 2, "safe_green" : 1}
# dictionary for 1 person while list for multiple people(casualties)
casualties = [{"age" : "children_stars", "severity" : "severe_red"}, {"age" : "adults_square", "severity" : "safe_green"}]

# calculation priority score defining function
def priority_score(casualty):
  return age_score[casualty["age"]] * severity_score[casualty["severity"]]
for casualty in casualties:
  casualty["priority"] = priority_score(casualty)
print(casualties)

# sorting cuz different casualties have different priorities and higher priority casualty needs to be assigned to camps first.
## Return a new sorted list from the items in iterable. Has two optional arguments which must be specified as keyword arguments. key specifies a function of one argument that is used to extract a comparison key from each element in iterable (for example, key=str.lower). The default value is None (compare the elements directly). reverse is a boolean value.
## using sorted instead of .sort cuz sorted() is a function and we need original data in the future and .sort() modifies the list in place so list is lost.

casualties_sorted = sorted(casualties, key=lambda x: x["priority"], reverse=True)   # sorting acc to priority  # reverse=True we use cuz sorting gives ascending order and we want highest priority first so reverse is used.
print("\nSorted Casualties:")
for a in casualties_sorted:
    print(a)

# now assigning casualties to different camps - camps can have limited casualties and the camps need to remember who has alr been assigned
# setting up a dict for camps which will again contain another dict of capacity and if they've been assigned which is an empty list

camps = {"blue" : {"capacity" : 4, "assigned" : []}, "pink" : {"capacity" : 3, "assigned" : []}, "grey" : {"capacity" : 2, "assigned" : []}}
