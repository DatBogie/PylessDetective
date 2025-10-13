import sys,csv,pathlib,json,os

args = sys.argv

DATA_PATH = "."

try:
    DATA_PATH = sys._MEIPASS
except:pass

def p(x:str):
    return os.path.join(DATA_PATH,x)

if "--help" in args or "-h" in args:
    print(
"""
PylessDetective Help:
\tVariables:
\t\t--help, -h | Show this message.
\t\t--map, -m=<map_name> | Specify a map.
\t\t--clue, -c=<clue_name> | Specify a clue. [Repeatable]
\t\t--non-interactive, -y | Skip all input() calls.
\t\t--output, -o=<output_path> | Specify output file path/name (JSON formatted). No output file if not specified.
\t\t\t> eg.: `--output=result.json` => `./result.json`
\t\t--simple-print, -s | Prints in a basic headerless CSV format.
\t\t--mode, -f=<mode> | Program mode/function. ["suspect","clue","map"]
\t\t\t> suspect | Finds suspects and prints/outputs them.
\t\t\t> clue | Finds all clues of the given map and prints/outputs them.
\t\t\t> map | Finds all map names and prints/outputs them.
\t\t--maps-dir, -d=<map_dir> | Specify a custom map directory.
\t\t\t> Sample directory tree:
\t\t\t\tmaps/
\t\t\t\t├── map1.csv
\t\t\t\t├── map2.csv
\t\t\t\t└── map3.csv

\tInformation:
\t\t[Repeatable] | This variable can be specified multiple times.
\t\t\t> eg.: `--clue=tooth --clue=forgotten shoe`
"""
    )
    sys.exit(0)

NO_INTERACT = "--non-interactive" in args or "-y" in args
OUTPUT_PATH = None
SIMPLE_PRINT = "--simple-print" in args or "-s" in args
MODE = None

MAP_DIR = None
for x in args:
    if not x.startswith("--maps-dir=") and not x.startswith("-d="):
        continue
    MAP_DIR = x[11 if x.startswith("--maps-dir=") else 3:]
    break

MAPS = {}
for map in pathlib.Path(MAP_DIR if MAP_DIR else p("maps")).iterdir():
    if not map.name.endswith(".csv"): continue
    MAPS[map.name[:-4]] = {}

map = None
clues = []
evidence = []
suspects = []

for x in args:
    if not map and x.startswith("--map=") or x.startswith("-m="):
        name = x[6 if x.startswith("--map=") else 3:].lower()
        if MAPS.get(name) != None:
            map = name
            continue
    if x.startswith("--clue=") or x.startswith("-c="):
        evidence.append(x[7 if x.startswith("--clue=") else 3:].lower())
        continue
    if not OUTPUT_PATH and x.startswith("--output=") or x.startswith("-o="):
        OUTPUT_PATH = x[9 if x.startswith("--output=") else 3:]
        continue
    if not MODE and x.startswith("--mode=") or x.startswith("-f="):
        MODE = x[7 if x.startswith("--mode=") else 3:].lower()
        continue

if not MODE: MODE = "suspect"

if MODE == "map":
    out_data = []
    message = "" if SIMPLE_PRINT else "Map Names:\n"
    for x in MAPS.keys():
        out_data.append(x)
        message+=f"{x}," if SIMPLE_PRINT else f"- {x}\n"
    if SIMPLE_PRINT and message.endswith(","): message = message[:-1]
    if not OUTPUT_PATH:
        print(message)
    else:
        with open(OUTPUT_PATH,"w") as f:
            json.dump(out_data,f)
    sys.exit(0)

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
with open(p(f"maps/{map}.csv")) as f:
    reader = csv.DictReader(f)
    for row in reader:
        data = {}
        for k,v in row.items():
            if k == "Name": continue
            if firstFlag: clues.append(k)
            data[k] = v=="1"
        MAPS[map][row["Name"]] = data
        if firstFlag: firstFlag = False

if MODE == "clue":
    out_data = []
    message = "" if SIMPLE_PRINT else "Clue Names:\n"
    for x in clues:
        out_data.append(x)
        message+=f"{x}," if SIMPLE_PRINT else f"- {x}\n"
    if SIMPLE_PRINT and message.endswith(","): message = message[:-1]
    if not OUTPUT_PATH:
        print(message)
    else:
        with open(OUTPUT_PATH,"w") as f:
            json.dump(out_data,f)
    sys.exit(0)

def run(firstRun:bool=False):
    global map,evidence,clues,suspects
    suspects.clear()
    if not firstRun: evidence.clear()
    if not NO_INTERACT and (not firstRun or not evidence):
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

    out_data = []
    if suspects:
        message = "Potential suspects:\n"
        keys = list(MAPS[map].keys())
        for x in suspects:
            message+=f"- (#{keys.index(x)+1}/{len(keys)}) {x}\n"
            if OUTPUT_PATH:
                out_data.append(x)
        if not OUTPUT_PATH: print(message)
    else:
        if not OUTPUT_PATH: print("No suspects found; you messed up!\n")
    if OUTPUT_PATH:
        with open(OUTPUT_PATH,"w") as f:
            json.dump(out_data,f)
    if not NO_INTERACT:
        again = input("Run again? (Y/n): ")
        if not again or again.lower() == "y" or again.lower() == "yes":
            run()

if __name__ == "__main__":
    run(True)