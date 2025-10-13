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
    python3 -m venv .venv && pip3 install -r requirements.txt
    ```

4. Run build script (run `build.bat` on Windows):

    ```sh
    ./build.sh
    ```

5. Binary is located in `./dist/PylessDetective` (`*.exe` on Windows, `*.app` on macOS).

## Adding Levels

This may need to be done if I ever get tired of this game, so I will describe the process here.

### Map Structure (Reference)

```fs
maps/
├── map1.csv
├── map2.csv
└── map3.csv
```

### Map-packs

If you'd like to make map-packs (external folders containing levels), you're in the right place!


