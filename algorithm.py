from cs50 import SQL


db = SQL("sqlite:///hy.db")

# create tables if they dont exist
db.execute(
    "CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL, fname TEXT, lname TEXT, email TEXT, phone TEXT, class_year INT, school TEXT, gender varchar(16), hash TEXT, same_gender INT, same_class INT, party INT, bed_hour INT, alcohol INT, progress INT);"
)
db.execute("CREATE TABLE IF NOT EXISTS matches (user_id INT, match_id INT);")


# setting up lists and constants

# get hosts and guests from database based on their schools
hosts = db.execute("SELECT * FROM users WHERE school = 'Harvard';")
guests = db.execute("SELECT * FROM users WHERE school = 'Yale';")

# coefficients for the three values on which the "partiness" factor will depend on
# the bigger the coefficient the more weight the factor has
# right now factors are set to just normalize the three values between 0 and 1
bed_coef = 1 / 8
alc_coef = 1 / 2
party_coef = 1 / 5

# current_year of the game
current_year = 2024

for host in hosts:
    # normalize "party values" between 0 and 1
    if int(host["bed_hour"]) < 8:
        host["bed_hour"] += 12
    host["bed_hour"] = bed_coef * float(host["bed_hour"] - 8)
    host["alcohol"] = alc_coef * float(host["alcohol"])
    host["party"] = party_coef * float(host["party"])

    # coverting classes into years in university by formula class_year = 5-(class_year-current_year)
    host["class_year"] = 5 - (host["class_year"] - current_year)

    # the partiness is the sum of the normalized three "party values" and will be between 0 and 3
    host["partiness"] = float(host["alcohol"] + host["bed_hour"] + host["party"])

for guest in guests:
    # normalize "party values" between 0 and 1
    if int(guest["bed_hour"]) < 8:
        guest["bed_hour"] += 12
    guest["bed_hour"] = bed_coef * float(guest["bed_hour"] - 8)
    guest["alcohol"] = alc_coef * float(guest["alcohol"])
    guest["party"] = party_coef * float(guest["party"])

    # coverting classes into years in university by formula class_year = 5-(class_year-current_year)
    guest["class_year"] = 5 - (guest["class_year"] - current_year)

    # the partiness is the sum of the normalized three "party values" and will be between 0 and 3
    guest["partiness"] = float(guest["alcohol"] + guest["bed_hour"] + guest["party"])

# create 15 groups of preferences for hosts and guests with indexes: (chosen for easy calculations)
# no preferences: 0
# only gender: male - 13 female - 14
# only class: fresh - 1 soph - 2 jun - 3 sen - 4
# class and gender: freshm - 5 sophm - 6 junm - 7 senm - 8
#                   freshf - 9 sophf - 10 junf - 11 senf - 12
groups_h = []
groups_g = []

for i in range(15):
    groups_h.append([])
    groups_g.append([])

# fill up groups with the according preferences
for host in hosts:
    if host["same_class"]:
        if host["same_gender"]:
            if host["gender"] == "male":
                groups_h[4 + host["class_year"]].append(host)
            else:
                groups_h[8 + host["class_year"]].append(host)
        else:
            groups_h[host["class_year"]].append(host)
    else:
        if host["same_gender"]:
            if host["gender"] == "male":
                groups_h[13].append(host)
            else:
                groups_h[14].append(host)
        else:
            groups_h[0].append(host)

for guest in guests:
    if guest["same_class"]:
        if guest["same_gender"]:
            if guest["gender"] == "male":
                groups_g[4 + guest["class_year"]].append(guest)
            else:
                groups_g[8 + guest["class_year"]].append(guest)
        else:
            groups_g[guest["class_year"]].append(guest)
    else:
        if guest["same_gender"]:
            if guest["gender"] == "male":
                groups_g[13].append(guest)
            else:
                groups_g[14].append(guest)
        else:
            groups_g[0].append(guest)


# pairs list that will store the perfect pairs of matches
pairs = []

# create lists that will contain the unused users that get moved to groups that most closely match their preferences

unused_for_13_h = []
unused_for_14_h = []
unused_for_0_h = []

unused_for_13_g = []
unused_for_14_g = []
unused_for_0_g = []

# overall unused users list that will be used on different iterations of the algorithm
unused_h = []
unused_g = []


# algorithm function taking two groups of hosts and guests and matches them to form best possible pairs based on partiness factor
def algorithm(group_h, group_g):
    # sets of used users in the two groups
    used_h = set()
    used_g = set()
    used_h.clear()
    used_g.clear()

    # Create a list of all possible pairs and their differences in partiness factor
    all_pairs = []
    for i, h in enumerate(group_h):
        for j, g in enumerate(group_g):
            diff = abs(h["partiness"] - g["partiness"])
            all_pairs.append((diff, i, j))

    # Sort the pairs based on the difference
    all_pairs.sort()

    # Select pairs with the smallest difference, ensuring uniqueness
    for diff, i, j in all_pairs:
        if i not in used_h and j not in used_g:
            pairs.append({"user_id": group_h[i]["id"], "match_id": group_g[j]["id"]})
            pairs.append({"user_id": group_g[j]["id"], "match_id": group_h[i]["id"]})
            used_h.add(i)
            used_g.add(j)
        # Leave loop if all elements of either group are used
        if len(used_h) == len(group_h) or len(used_g) == len(group_g):
            break

    # Pair remaining unpaired elements with -1
    for i in range(len(group_h)):
        if i not in used_h:
            unused_h.append(group_h[i])

    for j in range(len(group_g)):
        if j not in used_g:
            unused_g.append(group_g[j])
    return


# pair withing groups by partiness factor
for index in range(15):
    algorithm(groups_h[index], groups_g[index])

    # Put remaining unpaired elements in the unused groups 13, 14 or 0 - based on which of the three most closely mathces their preferences
    # 13 - male only
    # 14 - female only
    # 0 - no preference
    for un in unused_h:
        if (index >= 5 and index <= 8) or index == 13:
            unused_for_13_h.append(un)
        elif (index >= 9 and index <= 12) or index == 14:
            unused_for_14_h.append(un)
        else:
            unused_for_0_h.append(un)

    for un in unused_g:
        if (index >= 5 and index <= 8) or index == 13:
            unused_for_13_g.append(un)
        elif (index >= 9 and index <= 12) or index == 14:
            unused_for_14_g.append(un)
        else:
            unused_for_0_g.append(un)
    unused_h.clear()
    unused_g.clear()


# run algorithm on unused group 13 --------------------------------------------------------
unused_h.clear()
unused_g.clear()
algorithm(unused_for_13_h, unused_for_13_g)

# put all unused into group 0
for un in unused_h:
    unused_for_0_h.append(un)

for un in unused_g:
    unused_for_0_g.append(un)


# run algorithm on unused group 14 --------------------------------------------------------
unused_h.clear()
unused_g.clear()

algorithm(unused_for_14_h, unused_for_14_g)
# put all unused into group 0
for un in unused_h:
    unused_for_0_h.append(un)

for un in unused_g:
    unused_for_0_g.append(un)


# run algorithm on unused group 0 --------------------------------------------------------
unused_h.clear()
unused_g.clear()
algorithm(unused_for_0_h, unused_for_0_g)

# Pair all unused users after all this with -1 because they have no match - essentially all are going to be from the school that had more users
for un in unused_h:
    pairs.append({"user_id": un["id"], "match_id": -1})
for un in unused_g:
    pairs.append({"user_id": un["id"], "match_id": -1})

# return pairs into a database
db.execute("DELETE FROM matches;")
for pair in pairs:
    db.execute(
        "INSERT INTO matches (user_id, match_id) VALUES (?, ?);",
        pair["user_id"],
        pair["match_id"],
    )

# print matches where if a user is matched with -1 it means that they have no match
matches = db.execute("SELECT * FROM matches;")
for match in matches:
    print(match)
