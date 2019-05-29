# ArtStation Scraper

This is my personal project created to download images from [ArtStation](https://www.artstation.com/) website. The program will download artworks from specified artists to specified download location. In the download location, the program will create and name directories using the artist names, then save the artworks to the corresponding directories. When running this program, it will check each directory to see if update is needed such that only new uploads will be downloaded.

![alt text](doc/download.gif?raw=true "download")

![alt text](doc/result.png?raw=true "result")

## Instructions

1. install [Python 3.6+](https://www.python.org/)

2. install `requests` library

    ```bash
    pip install --user requests
    ```

3. edit `config.json` file in `data` folder manually or via command line interface

    - `artists`: the artist id shown in URL
    - `save directory`: the save directory path

## Usage

display help message

```bash
$ python main.py -h

usage: main.py [-h] [-f FILE] [-l] [-s SAVE_DIR] [-a  [ID ...]]
               [-d all [ID ...]] [-c all [ID ...]] [-t THREADS] [-r]

optional arguments:
  -h, --help       show this help message and exit
  -f FILE          set config file
  -l               list current settings
  -s SAVE_DIR      set save directory path
  -a  [ID ...]     add artist ids
  -d all [ID ...]  delete artist ids
  -c all [ID ...]  clear artists update info
  -t THREADS       set the number of threads
  -r               run program

```

run the program with current configuration (i.e. update artists' artworks)

```bash
python main.py
```

add artist IDs then run the program

```bash
python main.py -a wlop trungbui42 -r
```

load `temp.json` file in `data` folder then add artist IDs. Note that `temp.json` is only used for this instance and is not a replacement for the default `config.json` file

```bash
python main.py -f data/temp.json -a wlop trungbui42
```

clear update information (i.e. re-download artworks), set threads to 24, then run the program

```bash
python main.py -c all -t 24 -r
```

## Challenges

1. get all artwork URLs of an artist from a specific URL. There are two ways to do this: through AJAX URL or through normal URL. The former is preferred as it returns a JSON object that is easy to work with. However, ArtStation has a security check that prevents direct access to the AJAX URL. Below are some of the methods I tried:

    - Attempt 1: for AJAX URL, the request works in browser but not in Python, so I change the request headers to match the one sent in browser to hopefully bypass the security check, which includes modifying `user-agent`, `cookies`, etc. Unfortunately, this does not work.

    - Solution 1: for AJAX URL, use `Selenium` with [ChromeDriver](https://sites.google.com/a/chromium.org/chromedriver/) to request the link. This only works if the driver is not in headless mode. I tried modifying the request headers, but to no avail. This is therefore not a good solution because: (1) the users are going to see the browser automation, which may not be desirable, and (2), the performance is not great due to the driver itself and the prevention of headless mode.

    - Solution 2: use normal URL and parse the plain HTML to get the information. The trick is to use the artist's website instead of the portfolio page, as the latter is generated dynamically from the AJAX request and thus contains no valuable content.

2. update mechanism

    - Attempt 1: download artworks from newest to oldest until an existing file is found on the disk. This does not work well with the multi-threading implementation, as it makes the program a lot more complicated in order to deal with thread stopping condition

    - Attempt 2: record the last visited artwork information for each artist to check if update is needed. This does not work if the newest upload was deleted by the artist, as the stored information cannot be found in the retrieved HTML. One solution is to record a list of all downloaded artwork information for each artist, then compare it with the parsed data, but this wastes a lot of unnecessary space and memory

    - Solution: find the file names while parsing the artwork IDs such that the former can be used to compare with the existing files on disk. If there is a match, then the function will return a list of artworks from newest to the point in which the match was found.

## Todo

- add more functionality (e.g. ranking)