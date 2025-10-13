# PylessDetective

PylessDetective is a terminal application that sorts through the File for you.
You find the clues, it lists the suspect(s).

Made for the Roblox game [Armless Detective](https://www.roblox.com/games/97719631053849/Armless-Detective).

## Usage

### Windows

```cmd
PylessDetective.exe -h
```

### Other OS

```sh
PylessDetective -h
```

## Installation

### Windows/Linux

1. Download the binary from the [latest release](https://github.com/DatBogie/PylessDetective/releases/latest).

### Any OS

1. Install `git` (Google it :)).
2. Clone the repo:

    ```sh
    git clone https://github.com/DatBogie/PylessDetective.git && cd PylessDetective
    ```

3. Setup venv:

    ```sh
    python3 -m venv .venv && source ./.venv/bin/activate && pip3 install -r requirements.txt
    ```

4. Run build script (run `build.bat` on Windows):

    ```sh
    ./build.sh
    ```

5. Binary is located in `./dist/PylessDetective` (`*.exe` on Windows, `*.app` on macOS).

## Adding Levels

This may need to be done if I ever get tired of this game, so I will describe the process here.

### Reference

#### Directory Structure

> [!Important]
Map files should have unique names.

```fs
maps/
├── map1.csv
├── map2.csv
└── map3.csv
└── ...
```

#### File Format

A `1` represents that the suspect exhibits that clue. Nothing after a comma (eg. `,<- here`) represents them not exhibiting that clue.

Example level:

```csv
Name,clue1,clue2,clue3
Guy,1,,1
Person,1,1,
Individual,,1,1
```

Above, Guy exhbits `clue1` & `clue3`, but not `clue2`.

### Map-packs

If you'd like to make map-packs (external folders containing levels), you're in the right place!

1. Create a folder. Name it anything you'd like.
2. In that folder, create a file. Make sure it ends in `.csv`.
3. Open that file, henceforth referred to as "the level file," in a text editor.
4. Paste in:

    ```csv
    Name,
    ```

5. After the comma, type a shorted name of each clue, separated by commas. Eg.:

    ```csv
    Name,clue1,clue2,clue3
    ```

6. Now, go to the next line and type in the first suspect's name (make sure to write them in order of appearance in the File/ending lineup).

    Follow that up with a comma, and then put a "1" for all of their characteristic clues. Leave the rest blank. Eg.:

    ```csv
    Name,clue1,clue2,clue3
    Guy,1,,1
    ```

    In that example, "Guy" exhibits "clue1" and "clue3", but not "clue2".

    An easy way to speed this process up is to copy/paste however many commas there are in a row. Eg. for the example above:

    ```csv
    ,,,
    ```

7. Save the file. Now you're done!

    To use your map-pack in the program, find the absolute path to the map-pack folder (eg. `C:\Users\Default\Downloads\map-pack`) and paste it in the following command (use `PylessDetective.exe` on Windows):

    ```sh
    PylessDetective -d=<abs_path_to_map-pack>
    ```
