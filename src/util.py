import json
from enum import Enum, unique
from collections import namedtuple
import re

class Decision(Enum):
    other = 1               # this post is not subject to moderation
    watch = 2               # watch this post for further changes
    found_fanart = 3        # post is a piece of found fanart
    original_content = 4    # post is original content
    invalid_source = 5      # post is found fanart with improper sourcing

def load_regex_list(filename):
    """ Loads all lines in a file as seperate strings.

        Args:
            filename (str): filepath to the file

        Returns:
            list: a set of strings read from the file
    """
    with open(filename, 'r') as target_file:
        return [re.compile(s.replace('\n', '')) for s in target_file]

def convert(name, dictionary):
    """ Converts a dictionary into a namedtuple
        
        Args:
            name (str): the name of the tuple
            dictionary (dict): the dictionary to convert

        Returns:
            namedtuple: the converted namedtuple
    """
    return namedtuple(name, dictionary.keys())(**dictionary)

def load_json(filename):
    """ Loads a JSON file as a namedtuple
        
        Args:
            filename (str): The file path to the file to load.

        Returns:
            namedtuple: named set of key-value pairs from the JSON object
    """
    with open(filename, 'r') as target_file:
        return convert("json", json.load(target_file))
