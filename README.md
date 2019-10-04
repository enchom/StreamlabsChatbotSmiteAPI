# Streamlabs Chatbot Smite API
This is a simple script that offers access to Smite's API through Streamlabs Chatbot.

## Requirements
You need Streamlabs Chatbot that's set up with Python 2.7.13 (the only version supported by Streamlabs so far). The project does not have
any external dependencies.

You also need to have access to Smite API, i.e. a developer id and an authentication key.

## How to use
The script in its current form has a few example commands implemented. Your main code should be in 'Smite_StreamlabsSystem.py', but you're
free to modify any of the files you'd like.

When you first import the script make sure you add your developer id and authentication key through the UI settings.

## Interpreting API call results
All API calls return different data structures of different size. All data returned is in the form of Python dictionary format so the best 
way to examine the output is to log it as JSON. Since the chatbot will swallow any default prints, you could instead output data to a file 
instead for logging purposes. Logging from the bot's internal log option `Parent.Log` is also possible, but inconvenient for big JSONs. 

For example, to convert a Python dictionary to a good-looking json:

`pretty_json = json.dumps(data, indent=4, sort_keys=True)`

## Quota considerations
Every time a query is made the session is verified as well. This effectively makes you use 2 queries for each single query. Hence, the daily
quota is effectively 3750 queries instead of 7500.

## God names vs God ids
Most API calls involving gods use a god id. This is inconvenient since the ids are not logically ordered and must be extracted 
from a 'getgods' API call that returns a lot of information. To reduce this overhead, this script internally caches all god ids
after the first call to getgods and hence lets you freely use god names instead of ids.
