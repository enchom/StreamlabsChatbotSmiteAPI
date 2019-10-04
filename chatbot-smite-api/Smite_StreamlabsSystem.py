#---------------------------
#   Import Libraries
#---------------------------
import os
import sys
import json
import random
sys.path.append(os.path.dirname(__file__))

import clr
clr.AddReference("IronPython.Modules.dll")

#   Import Smite API
from Smite_Api import SmiteClient
from Smite_Api import Division
from Smite_Api import Portal
from Smite_Api import Queue
#   Import your Settings class
from Settings_Module import MySettings
#---------------------------
#   [Required] Script Information
#---------------------------
ScriptName = 'Smite API'
Website = ''
Description = '!duelrank <player> and !godrank <player> <god> (add your smite dev id and auth key from the settings UI)'
Creator = 'Enchom'
Version = '1.0.0.2'

#---------------------------
#   Define Global Variables
#---------------------------
SettingsFile = ""
ScriptSettings = None
SmiteApi = None

#---------------------------
#   [Required] Initialize Data (Only called on load)
#---------------------------
def Init():
    global SettingsFile, ScriptSettings, SmiteApi
    #   Create Settings Directory
    directory = os.path.join(os.path.dirname(__file__), 'Settings')
    if not os.path.exists(directory):
        os.makedirs(directory)

    #   Load settings
    SettingsFile = os.path.join(os.path.dirname(__file__), 'Settings', 'settings.json')
    ScriptSettings = MySettings(SettingsFile)

    #   Smite API
    SmiteApi = SmiteClient(ScriptSettings.DevId, ScriptSettings.AuthKey, lambda x: Parent.Log(ScriptName, str(x)))

    return

#---------------------------
#   [Required] Execute Data / Process messages
#---------------------------
def Execute(data):
    if data.IsChatMessage():
        words = list(map(lambda x: x.lower(), data.Message.split(' ')))

        # !godrank <player> <god> returns stats about
        if words[0] == '!godrank':
            if len(words) < 3:
                Parent.SendStreamMessage('Usage: !godrank <player> <god>')
                return

            player = words[1]
            god = ' '.join(words[2:])

            player_found = True
            try:
                ranks = SmiteApi.get_god_ranks(player)
                if len(ranks) == 0:
                    player_found = False
            except:
                player_found = False

            if not player_found:
                Parent.SendStreamMessage('Could not find player ' + str(player))
                return

            god_rank = None
            for rank in ranks:
                if rank['god'].lower() == god.lower():
                    god_rank = rank
            if god_rank is None:
                Parent.SendStreamMessage('Could not find god ' + str(god))
                return

            response = 'Player {0} on {1} stats: '.format(player, god) + \
                       'Worshippers: {0} | Win/Loss: {1}/{2} | Kills/Deaths: {3}/{4}'\
                            .format(god_rank['Worshippers'], god_rank['Wins'], god_rank['Losses'],
                                   god_rank['Kills'], god_rank['Deaths'])
            Parent.SendStreamMessage(response)
        # !duelrank <player> returns current duel rank for a given player (with default player Enchom)
        elif words[0] == '!duelrank':
            if len(words) < 2:
                player = 'Enchom'  # Default
            else:
                player = words[1]

            player_found = True
            try:
                player_data = SmiteApi.get_player(player)
                if len(player_data) == 0:
                    player_found = False
                else:
                    player_data = player_data[0]
            except:
                player_found = False

            if not player_found:
                Parent.SendStreamMessage('Could not find player ' + str(player))
                return

            rank = Division.get_name(player_data['RankedDuel']['Tier']).replace('_', ' ')
            Parent.SendStreamMessage('Player {0} is in {1}'.format(player, rank))
        elif words[0] == '!quota':
            try:
                quota = SmiteApi.get_data_used()[0]
            except:
                Parent.SendStreamMessage('Could not fetch quotas')
                return
            requests_left = quota['Request_Limit_Daily'] - quota['Total_Requests_Today']
            Parent.SendStreamMessage('{} queries left for today'.format(requests_left))

    return

#---------------------------
#   [Required] Tick method (Gets called during every iteration even when there is no incoming data)
#---------------------------
def Tick():
    return

#---------------------------
#   [Optional] Reload Settings (Called when a user clicks the Save Settings button in the Chatbot UI)
#---------------------------
def ReloadSettings(json_data):
    global ScriptSettings, SmiteApi
    json_data = json.loads(json_data)
    ScriptSettings.reload(json_data)
    SmiteApi.set_auth_key(ScriptSettings.AuthKey)
    SmiteApi.set_dev_id(ScriptSettings.DevId)

    ui_path = os.path.join(os.path.dirname(__file__), 'UI_Config.json')
    with open(ui_path, 'r') as f:
        json_ui = json.load(f)
    json_ui['DevId']['value'] = json_data['DevId']
    json_ui['AuthKey']['value'] = json_data['AuthKey']
    with open(ui_path, 'w') as f:
        f.write(json.dumps(json_ui, indent=4, sort_keys=True))

    return

#---------------------------
#   [Optional] Unload (Called when a user reloads their scripts or closes the bot / cleanup stuff)
#---------------------------
def Unload():
    return

#---------------------------
#   [Optional] ScriptToggled (Notifies you when a user disables your script or enables it)
#---------------------------
def ScriptToggled(state):
    return
