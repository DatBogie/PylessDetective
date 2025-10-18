import sys, csv, pathlib, json, os
from collections.abc import Callable
VERSION = "v0.1"
ARGS = sys.argv

DATA_PATH = "."
try:
    DATA_PATH = sys._MEIPASS
except:pass

TAB = "  "

if "--help" in ARGS or "-h" in ARGS:
    print(
f"""
PylessDetective {VERSION} Help:
{TAB}Variables:
{TAB}{TAB}--help, -h                 | Show this message.
{TAB}{TAB}--map, -m=<map_name>       | Specify a map.
{TAB}{TAB}--clue, -c=<clue_name>     | Specify a clue. [Repeatable]
{TAB}{TAB}--non-interactive, -y      | Skip asking to re-run/continue program (answers "n").
{TAB}{TAB}--output, -o=<output_path> | Specify output file path/name (JSON formatted). No output file if not specified.
{TAB}{TAB}{TAB}> eg.: `--output=result.json` => `./result.json`
{TAB}{TAB}--simple-print, -s         | Prints in a basic headerless CSV format.
{TAB}{TAB}--mode, -f=<mode>          | Program mode/function. ["suspect","clue","map"]
{TAB}{TAB}{TAB}> suspect                | Finds suspects and outputs them.
{TAB}{TAB}{TAB}> map                    | Finds all map names and outputs them.
{TAB}{TAB}{TAB}> clue                   | Finds all clues of the given map and outputs them.
{TAB}{TAB}{TAB}> map-data               | Finds data of the given map and output it. (Suspects and their respective clues.)
{TAB}{TAB}--maps-dir, -d=<map_dir>   | Specify a custom map directory.
{TAB}{TAB}{TAB}> Sample directory tree:
{TAB}{TAB}{TAB}{TAB}maps/
{TAB}{TAB}{TAB}{TAB}├── map1.csv
{TAB}{TAB}{TAB}{TAB}├── map2.csv
{TAB}{TAB}{TAB}{TAB}└── map3.csv
{TAB}{TAB}--prettify, -p             | Output prettified json format.

{TAB}Information:
{TAB}{TAB}[Repeatable] | This variable can be specified multiple times.
{TAB}{TAB}{TAB}> eg.: `--clue=tooth --clue=forgotten shoe`
"""
    )
    sys.exit(0)

NO_INTERACT = "--non-interactive" in ARGS or "-y" in ARGS
OUTPUT_PATH = None
SIMPLE_PRINT = "--simple-print" in ARGS or "-s" in ARGS
PRETTIFY = "--prettify" in ARGS or "-p" in ARGS
MODE = None
MAP_DIR = None
MAPS = {}

MAP = None
CLUES = []
EVIDENCE = []
SUSPECTS = []

def p(*x:str) -> str:
    return os.path.join(DATA_PATH,*x)

def get_path(x:str):
    return os.path.expandvars(os.path.expanduser(x))

def write_output(*x:any):
    if not OUTPUT_PATH or len(x) == 0: return
    if len(x) == 1: x = x[0]
    with open(get_path(OUTPUT_PATH),"w") as f:
        json.dump(x,f,indent=4 if PRETTIFY else None)

def output(*x:any,no_write:bool=False) -> None:
    if not OUTPUT_PATH or no_write:
        return print(*x)
    data = [v for v in x if not isinstance(v, str)]
    write_output(*data)

def clear_term():
    if OUTPUT_PATH: return
    if sys.platform == "win32":
        os.system("cls")
    else:
        os.system("clear")

def safe_len(x:any,offset:int=0) -> int|None:
    try:
        return len(x)+offset
    except:
        return None

def safe_int(x:str, offset:int=0) -> int|None:
    try:
        return int(x)+offset
    except:
        return None

def prettify_map_name(x:str):
    data = x.split("-")
    for i, v in enumerate(data):
        data[i] = v[:1].upper()+v[1:]
    return " ".join(data)

def uglify_map_name(x:str):
    data = x.split(" ")
    for i, v in enumerate(data):
        data[i] = v.lower()
    return "-".join(data)

def format_ls_item(x:str, index:int=0, length:int=1, show_index:bool=False, index_text:str="%d.", custom_index:int=None) -> str:
    if not custom_index: custom_index = index+1
    if not SIMPLE_PRINT:
        return f"{"-" if not show_index else index_text % (custom_index)} {x}\n"
    return f"{"[" if index == 0 else ""}{x}{"," if index<length-1 else "]"}"

def format_dict_item(x:str, index:int=0, length:int=1, key:str="", show_key:bool=True, key_text:str="%s:", custom_key:str=None) -> str:
    if not custom_key: custom_key = key
    if not SIMPLE_PRINT:
        return f"{"" if not show_key else key_text % (custom_key)} {x}\n"
    return f"{"{" if index == 0 else ""}{key}: {x}{"," if index<length-1 else "}"}"

def str_ls(l:list,header:str=None,show_index:bool=False,index_text:str="%d.",custom_index_func:Callable[[str,int],int]=None) -> str:
    string = f"{header}:\n" if header and not SIMPLE_PRINT else ""
    length = len(l)
    for i,x in enumerate(l):
        string+=format_ls_item(x,i,length,show_index,index_text,custom_index_func(x,i) if custom_index_func else None)
    return string

def str_dict(d:dict,header:str=None,show_key:bool=True,key_text:str="%s:",custom_key_func:Callable[[str,str],str]=None) -> str:
    string = f"{header}:\n" if header and not SIMPLE_PRINT else ""
    length = len(d.keys())
    for k,v in d.items():
        string+=format_dict_item(v,list(d.keys()).index(k),length,k,show_key,key_text,custom_key_func(v,k) if custom_key_func else None)

def get_maps() -> list[str]:
    x = [x for x in MAPS.keys()]
    x.sort()
    return x

def gen_map_data(map:str=None):
    if not map: map = MAP
    global MAPS, CLUES
    change_clues = True
    CLUES.clear()
    with open(p("maps" if not MAP_DIR else MAP_DIR,f"{map}.csv")) as f:
        reader = csv.DictReader(f)
        for row in reader:
            data = {}
            for k,v in row.items():
                if k == "Name": continue
                if change_clues: CLUES.append(k)
                data[k] = v=="1"
            MAPS[map][row["Name"]] = data
            if change_clues: change_clues = False
    CLUES.sort()

def get_map_data(map:str=None) -> dict[str:dict[str:bool]]:
    if not map: map = MAP
    if not MAPS[map]: gen_map_data(map)
    return MAPS[map]

def get_clues(map:str=None) -> list[str]:
    if not map: map = MAP
    if not CLUES: gen_map_data(map)
    return CLUES

def get_suspects(map:str=None, evidence:list[str]=None) -> list[str]:
    if not map: map = MAP
    if not evidence: evidence = EVIDENCE
    global SUSPECTS
    if not MAPS[map]: gen_map_data(map)
    SUSPECTS.clear()
    for name in MAPS[map]:
        person = MAPS[map][name]
        not_it = False
        for clue in evidence:
            if not person.get(clue):
                not_it = True
                break
        if not_it: continue
        SUSPECTS.append(name)
    return SUSPECTS

def input_yn(q:str, default_value:bool=None, header:str=None) -> bool:
    if NO_INTERACT: return False
    default_inputs = {
        "y": True,
        "n": False,
        "": default_value
    }
    if header:
        output(header)
    x = default_inputs[input(f"{q} ({"Y" if default_value else "y"}/{"n" if default_value else "N"}): ")]
    if x == None: x = False
    clear_term()
    return x

def input_strict(q:str, header:str=None, req_data:list[str]=[], req_func:Callable[[str,list[str]],bool]=lambda x, y : x in y, req_data_show_index:bool=False,run_forever:bool=False,run_forever_terminator:str="",starting_data:list[str]=None,starting_data_display_previous:bool=True) -> str|list[str]:
    x = ""
    data = starting_data or []
    i = safe_len(starting_data,1) or 1
    if header:
        output(str_ls(req_data,header,req_data_show_index))
    if run_forever:
        output(f'Enter "{run_forever_terminator}" to confirm.' if run_forever_terminator != "" else 'Leave blank and press Enter to confirm.',no_write=True)
    if starting_data and starting_data_display_previous:
        string = str_ls(starting_data,show_index=True,index_text="Enter clue #%d:")
        if string.endswith("\n"):
            string = string[:-1]
        output(string)
    while True:
        x = input(f"{q if not run_forever else q % (i)}: ")
        if run_forever and x == run_forever_terminator: break
        if req_func(x,req_data):
            if not run_forever: break
            data.append(x)
            i+=1
    clear_term()
    return x if not run_forever else data

def mode_map():
    output(str_ls(get_maps(),"Maps") if not OUTPUT_PATH else get_maps())
    sys.exit(0)

def mode_clue():
    output(str_ls(get_clues(),"Clues") if not OUTPUT_PATH else get_clues())
    sys.exit(0)

def mode_mapdata():
    if not MAPS.get(MAP):
        gen_map_data()
    output(str_dict(MAPS[MAP],f"{prettify_map_name(MAP)} Map Data") if not OUTPUT_PATH else MAPS[MAP])
    sys.exit(0)

for x in ARGS:
    if not x.startswith("--maps-dir=") and not x.startswith("-d="):
        continue
    MAP_DIR = x[11 if x.startswith("--maps-dir=") else 3:]
    break

for map in pathlib.Path(MAP_DIR if MAP_DIR else p("maps")).iterdir():
    if not map.name.endswith(".csv"): continue
    MAPS[map.name[:-4]] = {}

for x in ARGS:
    if not MAP and x.startswith("--map=") or x.startswith("-m="):
        name = x[6 if x.startswith("--map=") else 3:].lower()
        if MAPS.get(name) != None:
            MAP = name
            gen_map_data()
            continue
    if x.startswith("--clue=") or x.startswith("-c="):
        EVIDENCE.append(x[7 if x.startswith("--clue=") else 3:].lower())
        continue
    if not OUTPUT_PATH and x.startswith("--output=") or x.startswith("-o="):
        OUTPUT_PATH = x[9 if x.startswith("--output=") else 3:]
        continue
    if not MODE and x.startswith("--mode=") or x.startswith("-f="):
        MODE = x[7 if x.startswith("--mode=") else 3:].lower()
        continue
if not MODE: MODE = "suspect"

if MODE == "map":
    mode_map()

if MAP:
    if MODE == "clue":
        mode_clue()
    if MODE == "map-data":
        mode_mapdata()

if EVIDENCE:
    if not MAP:
        EVIDENCE.clear()
    if MAP:
        if not CLUES: CLUES = get_clues()
        evidence = []
        for clue in EVIDENCE:
            if clue in CLUES:
                evidence.append(clue)
        EVIDENCE = evidence.copy()
        del evidence

def prompt_map():
    maps = get_maps()
    return maps[int(input_strict("Enter map number","Maps",maps,lambda x, y: True if safe_int(x) and y[safe_int(x,-1)] else False,True))-1]

def prompt_evidence():
    return input_strict("Enter clue #%d",f"{prettify_map_name(MAP)} Clues",CLUES,run_forever=True,starting_data=EVIDENCE)

def run(root_call:bool=False, clear_evidence:bool=False):
    global MAP, CLUES, EVIDENCE, SUSPECTS
    clear_term()
    if not root_call:
        if clear_evidence:
            EVIDENCE.clear()
        SUSPECTS.clear()

    if not MAP:
        MAP = prompt_map()
        gen_map_data()

    if MAP:
        if MODE == "clue":
            mode_clue()
        if MODE == "map-data":
            mode_mapdata()

    if not root_call or not EVIDENCE:
        EVIDENCE = prompt_evidence()

    SUSPECTS = get_suspects()
    keys = list(MAPS[MAP].keys())
    output((str_ls(SUSPECTS,"Possible Suspects",True,f"- (#%d/{len(keys)})",lambda x, i: keys.index(x)+1) if SUSPECTS else "- No suspects found!") if not OUTPUT_PATH else SUSPECTS)
    if len(SUSPECTS) <= 1:
        if input_yn("Run again?",True):
            return run(clear_evidence=True)
        return
    if not input_yn("Continue?",True,"Press Enter to continue."): return
    return run()

if __name__ == "__main__":
    run(True)