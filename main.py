import sys,csv,pathlib

MAPS = {}

for map in pathlib.Path("./maps").iterdir():
    MAPS[map.name[:-4]] = {}

map = None
evidence = []
clues = []
suspects = []

args = sys.argv

if "--help" in args:
    print(
"""
PylessDetective Help:
\tVariables:
\t\t--help | Show this message.
\t\t--map=<map_name> | Specify a map.
\t\t--clue=<clue_name> | Specify a clue. [Repeatable]

\tInformation:
\t\t[Repeatable] | This variable can be specified multiple times.
\t\t\t> eg.: `PylessDetective --clue=tooth --clue=forgotten shoe`
"""
    )
    sys.exit(0)

for x in args:
    if x.startswith("--map=") and not map:
        name = x[6:].lower()
        print(name)
        if MAPS.get(name) != None:
            map = name
            continue
    if x.startswith("--clue="):
        evidence.append(x[7:].lower())

if not map:
    name = ""
    message = "Map Names:\n"
    for x in MAPS.keys():
        message+=f"- {x}\n"
    print(message)
    while True:
        name = input("Enter map name: ")
        if not name: continue
        name = name.lower()
        if MAPS.get(name) != None:
            map = name
            break
    print()

firstFlag = True
with open(f"./maps/{map}.csv") as f:
    reader = csv.DictReader(f)
    for row in reader:
        data = {}
        for k,v in row.items():
            if k == "Name": continue
            if firstFlag: clues.append(k)
            data[k] = v=="1"
        MAPS[map][row["Name"]] = data
        if firstFlag: firstFlag = False

def run(firstRun:bool=False):
    global map,evidence,clues,suspects
    if not firstRun or not evidence:
        i = 1
        message = "Clue Names:\n"
        for x in clues:
            message+=f"- {x}\n"
        message+="\n(Leave blank and press enter to confirm)"
        print(message)
        while True:
            clue = input(f"Enter evidence #{i}: ")
            if not clue: break
            clue = clue.lower()
            if clue in clues:
                i+=1
                evidence.append(clue)
        print()

    for name in MAPS[map]:
        person = MAPS[map][name]
        not_it = False
        for clue in evidence:
            if not person[clue]:
                not_it = True
                break
        if not_it: continue
        suspects.append(name)

    if suspects:
        message = "Potential suspects:\n"
        for x in suspects:
            message+=f"- {x}\n"
        print(message)
    else:
        print("No suspects found; you screwed up!\n")
    again = input("Run again? (Y/n)")
    if not again or again.lower() == "y" or again.lower() == "yes":
        run()

if __name__ == "__main__":
    run(True)