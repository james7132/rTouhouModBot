import json
from collections import namedtuple

def load_list(filename):
    """ Loads all lines in a file as seperate strings in a set.

        Args:
            filename (str): filepath to the file

        Returns:
            set: a set of strings read from the file
    """
    with open(filename, 'r') as target_file:
        return set(s.replace('\n', '') for s in target_file)

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
