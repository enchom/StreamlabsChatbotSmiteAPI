import os
import sys
import json
import hashlib
from datetime import datetime

API_URL = 'http://api.smitegame.com/smiteapi.svc'
LANG = '1'

class Division:
    Qualifying = 0
    Bronze_V = 1
    Bronze_IV = 2
    Bronze_III = 3
    Bronze_II = 4
    Bronze_I = 5
    Silver_V = 6
    Silver_IV = 7
    Silver_III = 8
    Silver_II = 9
    Silver_I = 10
    Gold_V = 11
    Gold_IV = 12
    Gold_III = 13
    Gold_II = 14
    Gold_I = 15
    Platinum_V = 16
    Platinum_IV = 17
    Platinum_III = 18
    Platinum_II = 19
    Platinum_I = 20
    Diamond_V = 21
    Diamond_IV = 22
    Diamond_III = 23
    Diamond_II = 24
    Diamond_I = 25
    Master = 26
    Grandmaster = 27

    @staticmethod
    def get_name(div_id):
        for attr in dir(Division):
            attr_val = getattr(Division, attr)
            if isinstance(attr_val, int):
                if attr_val == div_id:
                    return attr.replace('_', ' ')
        return None


class Portal:
    UNKNOWN = -1
    HIREZ = 1
    STEAM = 5
    PS4 = 9
    XBOX = 10
    SWITCH = 22
    DISCORD = 25

    @staticmethod
    def get_name(div_id):
        for attr in dir(Portal):
            attr_val = getattr(Portal, attr)
            if isinstance(attr_val, int):
                if attr_val == div_id:
                    return attr
        return None

class Queue:
    ARENA = 435
    JOUST = 448
    CONQUEST = 426
    ASSAULT = 445
    CLASH = 466
    CONQUEST_LEAGUE = 451
    JOUST_LEAGUE = 450
    MOTD = 434
    JOUST_CUSTOM = 441
    SIEGE = 459
    DUEL = 440
    ARENA_AI_MEDIUM = 468
    JOUST_AI_MEDIUM = 456
    ARENA_TUTORIAL = 462
    ARENA_CUSTOM = 438
    CONQUEST_CUSTOM = 429
    CONQUEST_AI_MEDIUM = 461
    ARENA_AI_EASY = 457
    CONQUEST_AI_EASY = 476
    JOUST_AI_EASY = 474
    CONQUEST_LEAGUE_CONTROLLER = 504
    ARENA_PRACTICE_MEDIUM = 472
    JOUST_LEAGUE_CONTROLLER = 503
    ASSAULT_CUSTOM = 446
    ASSAULT_AI_MEDIUM = 454
    JOUST_PRACTICE_MEDIUM = 473
    ARENA_PRACTICE_EASY = 443
    CLASH_CUSTOM = 467
    CLASH_AI_MEDIUM = 469
    ASSAULT_AI_EASY = 481
    SIEGE_CUSTOM = 460
    CONQUEST_PRACTICE_MEDIUM = 475
    JOUST_PRACTICE_EASY = 464
    DUEL_CONTROLLER = 502
    CONQUEST_PRACTICE_EASY = 458
    CLASH_AI_EASY = 478
    ASSAULT_PRACTICE_MEDIUM = 480
    ASSAULT_PRACTICE_EASY = 479
    CLASH_PRACTICE_MEDIUM = 477
    CLASH_PRACTICE_EASY = 470
    CLASH_TUTORIAL = 471
    BASIC_TUTORIAL = 436

    @staticmethod
    def get_name(div_id):
        for attr in dir(Queue):
            attr_val = getattr(Queue, attr)
            if isinstance(attr_val, int):
                if attr_val == div_id:
                    return attr
        return None
        
class SmiteClient(object):
    def GET(self, url, headers):
        return json.loads(json.loads(self.Parent.GetRequest(url, headers))['response'])

    def set_auth_key(self, auth_key):
        self.auth_key = auth_key

    def set_dev_id(self, dev_id):
        self.dev_id = dev_id

    def __init__(self, Parent, dev_id, auth_key, logger=lambda x: None):
        self.Parent = Parent
        self.dev_id = dev_id
        self.auth_key = auth_key
        self.logger = logger
        self.session = None
        self.god_mapping = None


    def ping(self):
        """
        A quick way of validating access to the Hi-Rez API.
        """
        return self.GET(API_URL + '/pingjson', {})

    def get_data_used(self):
        """
        Returns API Developer daily usage limits and the current status against those limits.
        """
        return self._make_request('getdataused')

    def get_hirez_server_status(self):
        """
        Function returns UP/DOWN status for the primary game/platform environments.  Data is cached once a minute.
        """
        return self._make_request('gethirezserverstatus')

    def get_patch_info(self):
        """
        Function returns information about current deployed patch. Currently, this information only includes patch version.
        """
        return self._make_request('getpatchinfo')

    def get_gods(self):
        """
        Returns all Gods and their various attributes.
        """
        return self._make_request('getgods', LANG)

    def get_god_leaderboard(self, god, queue):
        """
        Returns the current season's leaderboard for a god/queue combination. [only queues 440, 450, 451]

        :param god: God id or name. If a name is given the internal mapping will translate it. If the internal mapping
        is not already initialised, an extra query will be spent.
        :param queue: Queue id - Only supported ones are 440 (Duel), 450 (Ranked Joust) and 451 (Ranked Conquest).
        Refer to the enum class Queue
        """
        if isinstance(god, str):
            god = self._translate_god_name(god)
        return self._make_request('getgodleaderboard', '{0}/{1}'.format(god, queue))

    def get_god_skins(self, god):
        """
        Returns all available skins for a particular God.

        :param god: God id or name. If a name is given the internal mapping will translate it. If the internal mapping
        is not already initialised, an extra query will be spent.
        """
        if isinstance(god, str):
            god = self._translate_god_name(god)
        return self._make_request('getgodskins', '{0}/{1}'.format(god, LANG))

    def get_god_recommended_items(self, god):
        """
        Returns the Recommended Items for a particular God.

        :param god: God id or name. If a name is given the internal mapping will translate it. If the internal mapping
        is not already initialised, an extra query will be spent.
        """
        if isinstance(god, str):
            god = self._translate_god_name(god)
        return self._make_request('getgodrecommendeditems', '{0}/{1}'.format(god, LANG))

    def get_items(self):
        """
        Returns all Items and their various attributes.
        """
        return self._make_request('getitems', LANG)

    def get_player(self, player, portal_id=None):
        """
        Returns league and other high level data for a particular player.

        :param player: Player id or name
        :param portal_id: (optional, not recommended) Portal id. Refer to the enum class Portal
        """
        if portal_id is None:
            return self._make_request('getplayer', str(player))
        else:
            return self._make_request('getplayer', '{0}/{1}'.format(player, portal_id))

    def get_player_id_by_name(self, player_name):
        """
        Function returns a list of Hi-Rez playerId values (expected list size = 1) for playerName provided.
        The playerId returned is expected to be used in various other endpoints to represent the player/individual
        regardless of platform.

        :param player_name: Player name
        """
        return self._make_request('getplayeridbyname', str(player_name))

    def get_friends(self, player):
        """
        Return the Smite User names of each of the player's friends. [PC only]

        :param player: Player name or id
        """
        return self._make_request('getfriends', str(player))

    def get_god_ranks(self, player):
        """
        Returns the Rank and Worshippers value for each God a player has played.

        :param player: Player name or id
        """
        return self._make_request('getgodranks', str(player))

    def get_player_achievements(self, player_id):
        """
        Returns select achievement totals (Double kills, Tower Kills, First Bloods, etc) for the specified playerId.

        :param player_id: Player id
        """
        return self._make_request('getplayerachievements', str(player_id))

    def get_player_status(self, player):
        """
        Returns player status as follows:
        0 - Offline
        1 - In Lobby  (basically anywhere except god selection or in game)
        2 - God Selection (player has accepted match and is selecting god before start of game)
        3 - In Game (match has started)
        4 - Online (player is logged in, but may be blocking broadcast of player state)
        5 - Unknown (player not found)

        :param player: Player name or id
        """
        return self._make_request('getplayerstatus', str(player))

    def get_match_history(self, player):
        """
        Gets recent matches and high level match statistics for a particular player

        :param player: Player name or id
        """
        return self._make_request('getmatchhistory', str(player))

    def get_queue_stats(self, player, queue):
        """
        Returns match summary statistics for a (player, queue) combination grouped by gods played.

        :param player: Player name or id
        :param queue: Queue id - Only supported ones are 440 (Duel), 450 (Ranked Joust) and 451 (Ranked Conquest).
        Refer to the enum class Queue
        """
        return self._make_request('getqueuestats', '{0}/{1}'.format(player, queue))


    def get_match_details(self, match_id):
        """
        Returns the statistics for a particular completed match.

        :param match_id: Match id
        """
        return self._make_request('getmatchdetails', str(match_id))

    def get_match_ids_by_queue(self, queue, date, hour, minute_window):
        """
        Lists all Match IDs for a particular Match Queue; useful for API developers interested in constructing
        data by Queue. To limit the data returned, an {hour} parameter was added (valid values: 0 - 23).
        Also, a returned "active_flag" means that there is no match information/stats for the corresponding match.
        Usually due to a match being in-progress, though there could be other reasons.

        :param queue: Queue id - Only supported ones are 440 (Duel), 450 (Ranked Joust) and 451 (Ranked Conquest).
        Refer to the enum class Queue
        :param date: Date in YYYYMMDD format
        :param hour: Hour as a number from 0 to 23
        :param minute_window: A number from 0 to 5 indicating the 10-minute window within the hour
        """
        params = '{0}/{1}/{2},{3}'.format(queue, date, hour, str(minute_window*10) if minute_window != 0 else '00')
        return self._make_request('getmatchidsbyqueue', params)

    def get_match_player_details(self, match_id):
        """
        Returns player information for a live match.

        :param match_id: Match id
        """
        return self._make_request('getmatchplayerdetails', str(match_id))

    def get_top_matches(self):
        """
        Lists the 50 most watched / most recent recorded matches.
        """
        return self._make_request('gettopmatches')

    def get_league_leaderboard(self, queue, tier, round):
        """
        Returns the top players for a particular league (as indicated by the queue/tier/round parameters).
        Note: the "Season" for which the Round is associated is by default the current/active Season.

        :param queue: Queue id - Only supported ones are 440 (Duel), 450 (Ranked Joust) and 451 (Ranked Conquest).
        Refer to the enum class Queue
        :param tier: Division id - refer to the enum class Division
        :param round: Split in current season
        """
        return self._make_request('getleagueleaderboard', '{0}/{1}/{2}'.format(queue, tier, round))

    def get_team_details(self, clan_id):
        """
        Lists the number of players and other high level details for a particular clan.

        :param clan_id: Clan id
        """
        return self._make_request('getteamdetails', str(clan_id))

    def get_team_players(self, clan_id):
        """
        Lists the players for a particular clan.

        :param clan_id: Clan id
        """
        return self._make_request('getteamplayers', str(clan_id))

    def get_esports_pro_league_details(self):
        """
        Returns the matchup information for each matchup for the current eSports Pro League season. An important
        return value is "match_status" which represents a match being scheduled (1), in-progress (2), or complete (3)
        """
        return self._make_request('getesportsproleaguedetails')

    def get_motd(self):
        """
        Returns information about the 20 most recent Match-of-the-Days.
        """
        return self._make_request('getmotd')


    def _cache_god_ids(self):
        god_data = self.get_gods()
        self.god_mapping = {}
        for god in god_data:
            self.god_mapping[god['Name'].lower()] = god['id']

    def _translate_god_name(self, god_name):
        if self.god_mapping is None:
            self._cache_god_ids()
        return self.god_mapping[god_name.lower()]

    def _make_signature(self, method, timestamp):
        return hashlib.md5(self.dev_id + method + self.auth_key + timestamp).hexdigest()

    def _get_timestamp(self):
        return datetime.utcnow().strftime("%Y%m%d%H%M%S")

    def _create_session(self):
        ts = self._get_timestamp()
        request = API_URL + '/createsessionjson/{0}/{1}/{2}'.format(self.dev_id, self._make_signature('createsession', ts), ts)
        response = self.GET(request, {})

        if response['ret_msg'] != 'Approved':
            self.logger('[ERROR] Could not create session: ' + response['ret_msg'])
        return response['session_id']

    def _get_session(self):
        if self.session is None or not self._test_session(self.session):
            self.session = self._create_session()
        return self.session

    def _test_session(self, session):
        ts = self._get_timestamp()
        request = API_URL + '/testsessionjson/{0}/{1}/{2}/{3}'.format(self.dev_id,
                                                                self._make_signature('testsession', ts), session, ts)
        try:
            return 'successful' in self.GET(request, {})
        except:
            return False

    def _make_request(self, method, params=None):
        ts = self._get_timestamp()
        request = API_URL + '/{0}json/{1}/{2}/{3}/{4}'.format(method, self.dev_id, self._make_signature(method, ts),
                                                              self._get_session(), ts)
        
        if params is not None:
            request += '/{}'.format(params)
        return self.GET(request, {})
