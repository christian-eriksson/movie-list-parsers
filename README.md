# Movie List Parser

Collection of scripts that can be used to find imdb and download lists to
`*.csv`-files, create imdb formatted lists from [top250.info](http://top250.info/)
and parse imdb formatted `*.csv` into a format that can be used by the
[jellyfin-list-populator](https://github.com/christian-eriksson/jellyfin-list-populator).

## Search lists manually

You can manually search IMDB for lists related to specific keywords and export
(download) them as `*.csv`, for example on [duckduckgo](https://duckduckgo.com/):

`<search-term> site:imdb.com[/list]`

## Automatically find lists

Can find lists on specific keywords and download them. Especially useful if you
want lists with many movies on specific topics, e.g. winter movies, skateboard
movies, etc.

**Usage:** `./download_imdb_lists.py <keyword_string> [<dir_path>] [<max_list_count>]`

**Output:** Will seach duckduck.go using the keyword string and download the
first `<max_list_count>` lists it finds to `<dir_path>/<keyword_string>.csv`.
The defaults are `<dir_path>=/tmp` and `<max_list_count>=10`, when downloading
the csv spaces in `<keyword_string>` will be replaced with `_`.

**Example:** `./download_imdb_lists.py "winter movies" ~/winter-lists 100`

## Find previous IMDB Top 250 entries

The list of IMDB 250 titles is parsed from historical information available at
[top250.info](http://www.top250.info/). The list holds previous and current (as
of the day it was created) entries of IMDB's 250 List. Useful if you want to
maintain a collection of "really good" movies.

**Usage:** `./parse_top250_to_imdb_list.py [<start-date>]`

**Output:** prints a list of all movies that has been on top250 since
`<start-date>`. The start date should be provided in the format `YYYY-MM-DD`,
default start date is `1996-04-26`. The list will have duplicate titles
(imdb ids) if the title has been on the list more than once (and most have).

The row format of the output will be the same as if you download an IMDB list,
though the dates (bothe the `Created` and `Modified`) will reflect when the
title was on the list.

Note that running this script will take a long time, especially with the default
start date. A tip is to save the output and merge with a new list it if you want
to update the list (the Position numbering won't match but I'll leave it as a
exercise to fix if you need it).

**Example:** `./parse_top250_to_imdb_list.py 2022-07-27 > top-250.csv`

## Parse IMDB lists to create Jellyfin lists

You can prepare a list to be used with the [jellyfin-list-populator](https://github.com/christian-eriksson/jellyfin-list-populator)
by running the `parse_imdb_lists.py` script.

**Usage:** `./parse_imdb_lists.py [--allow-duplicates] <path>`

**Output:** Prints a csv lists with the following headings:
`imdb-id,title,seasons,episodes`. The `seasons` and `episodes` headings are
`|`-separated lists of integers indicating possible season/-s and episode/-s if
such could be parsed. This is parsed from the description field in the IMDB
list if it matches the regex:
`r".*season (\d+)(-(\d+))?(: ep\. (\d+)(-(\d+))?)?.*"`, basically if it contains
something like: `season 1: ep. 3`, `season 3-4`. `season 5: ep. 10-11`, etc.

The `<path>` argument can be either a `*.csv` file or a directory containing
`*.csv` files.

The `--allow-duplicates` (or `-d`) option will allow a `imdb-id` to show up
more than once in the output. The default is to filter duplicates out.
