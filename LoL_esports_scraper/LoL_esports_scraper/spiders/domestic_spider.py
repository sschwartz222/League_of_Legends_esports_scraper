import scrapy
import datetime as dt

'''
crawler for domestic competitions
'''
class DomesticSpider(scrapy.Spider):
    name = 'domestic'
    start_urls = [
        'https://lol.gamepedia.com/League_Championship_Series',
        'https://lol.gamepedia.com/LoL_European_Championship',
        'https://lol.gamepedia.com/League_of_Legends_Champions_Korea',
        'https://lol.gamepedia.com/LoL_Pro_League'
    ]

    '''
    initial parsing of the four regional links
    '''
    def parse(self, response):

        '''
        filter to retain only links that direct to a page with a competitive split i.e. spring 2021
        '''
        def filter_league(res, lnk):
            if 'League_Championship_Series' in str(res):
                if 'LCS' in lnk and ('Spring_Season' in lnk or 'Summer_Season' in lnk):
                    return True
                return False
            elif 'LoL_European_Championship' in str(res):
                if ('LCS' in lnk or 'LEC' in lnk) and ('Spring_Season' in lnk or 'Summer_Season' in lnk):
                    return True
                return False
            elif 'League_of_Legends_Champions_Korea' in str(res):
                if ('LCK/' in lnk or 'Champions' in lnk) and ('Winter_Season' in lnk or 'Spring_Season' in lnk or 'Summer_Season' in lnk):
                    return True
                return False
            elif 'LoL_Pro_League' in str(res):
                if 'LPL' in lnk and ('Spring_Season' in lnk or 'Summer_Season' in lnk):
                    return True
                return False
            return False

        #grabbing all links, need to filter because labeling on the website is not enough to isolate years
        year_links = response.css('div.hlist li span a')
        filtered_links = []

        #for each link grabbed, check if it fits the criteria described above
        for link in year_links:
            l = link.get()
            if filter_league(response, l):
                filtered_links.append(link)
        
        #follow each link within the filtered list
        yield from response.follow_all(filtered_links, self.parse_scoreboards)

    '''
    within each split's page, navigate to the 'Scoreboard' tab to set up for game parsing
    '''
    def parse_scoreboards(self, response):
        links = response.css('div.tabheader-top div.tabheader-content a::attr(href)')
        scoreboard_link = ''

        for link in links:
            if 'Scoreboard' in link.get():
                scoreboard_link = link
                break

        yield scrapy.Request(response.urljoin(scoreboard_link.get()), callback=self.parse_weeks)
    
    '''
    within the scoreboard tabs, navigate through each week of competition
    '''
    def parse_weeks(self, response):
        #initial page (week 1 for each scoreboard) is special cased because it has a dead link
        yield from self.parse_days(response)

        links = response.css('div.tabheader-top div.tabheader-content a::attr(href)')
        week_links = []
        
        for link in links:
            if 'Week' in link.get():
                week_links.append(link)

        yield from response.follow_all(week_links, self.parse_days)
    
    '''
    main function wrapping the parsing of the games from each day
    '''
    def parse_days(self, response):
        
        '''
        determine what split is being examined
        packaged into the yielded item so that the pipeline can
        properly split data into the right place
        '''
        def parse_split():
            #look at the first few elements of the heading text
            heading = response.css('h1.firstHeading::text').get()
            heading = heading.split('/')

            year = heading[1][:4]
            split = heading[2].split(' ')[0].lower()
            league = ''

            if heading[0] == 'Champions' or heading[0] == 'LCK':
                league = 'korea'
            elif heading[0] == 'LPL':
                league = 'china'
            elif heading[0] == 'EU LCS' or heading[0] == 'LEC':
                league = 'europe'
            elif heading[0] == 'NA LCS' or heading[0] == 'LCS':
                league = 'NA'
            
            return (league, year, split)
                
        '''
        function for parsing one game from a table
        '''        
        def parse_game(game):
            
            '''
            helper function to organize and parse the info of each player in the scoreboard
            '''
            def parse_team_info(team):
                #first parsed into list so sequential nature can be used
                #to sort players into their respective roles
                tm = []
                team_gold = 0
                team_kills = 0

                #parsing stats from the players' boxes in the table
                for player in team.css('div.sb-p'):
                    
                    champion = player.css('div.sb-p-champion span::attr(title)').get(default='')
                    summoner_spells = player.css('div.sb-p-sum span::attr(title)').getall()
                    runes = player.css('div.popup-content-inner-pretty span.markup-object span::text').getall()
                    
                    player_info = player.css('div.sb-p-info')
                    player_stats = player.css('div.sb-p-stats')

                    name = player_info.css('div.sb-p-name a::text').get(default='')
                    
                    kda = player_stats.css('div:nth-of-type(1)::text').get(default='0/0/0')
                    kda_values = kda.split('/')
                    kda = {'kills' : int(kda_values[0]), 'deaths' : int(kda_values[1]), 'assists' : int(kda_values[2])}
                    
                    cs = int(player_stats.css('div:nth-of-type(2)::text').get(default='0'))
                    
                    gold = player_stats.css('div:nth-of-type(3)::text').get(default='0k')
                    gold = 1000 * float(gold[:-1])

                    items = player.css('div.sb-p-items span::attr(title)').getall()

                    trinket = player_stats.css('div.sb-p-trinket span::attr(title)').get(default='')
                    
                    #stick it all in a dict
                    tm.append(
                        {
                            'player_name'       : name,
                            'champion'          : champion,
                            'KDA'               : kda,
                            'gold'              : gold,
                            'CS'                : cs,
                            'runes'             : runes,
                            'summoner_spells'   : summoner_spells,
                            'items'             : items,
                            'trinket'           : trinket
                        }
                    )

                    #find team stats by aggregating individual stats
                    team_gold += gold
                    team_kills += kda['kills']
                
                #players are parsed in positional order, so using list ordering is used here
                return (
                    team_gold, 
                    team_kills, 
                    {'top'       : tm[0],
                    'jungle'    : tm[1],
                    'mid'       : tm[2],
                    'bot_carry' : tm[3],
                    'support'   : tm[4]}
                )

            '''
            helper function to organize and parse bonus team and draft info
            '''
            def parse_team_extra_info(team):
                #team stats may not exist due to game changes (rift herald) or lack of information
                towers = team.css('div.sb-footer-item.sb-footer-item-towers::text').get(default='')
                inhibs = team.css('div.sb-footer-item.sb-footer-item-inhibitors::text').get(default='')
                barons = team.css('div.sb-footer-item.sb-footer-item-barons::text').get(default='')
                dragons = team.css('div.sb-footer-item.sb-footer-item-dragons::text').get(default='')
                rift_heralds = team.css('div.sb-footer-item.sb-footer-item-riftheralds::text').get(default='')

                bans = team.css('div.sb-footer-bans span::attr(title)').getall()

                return {
                    'bans'      : bans,
                    'objectives': {
                        'towers'        : towers if towers != '' else 0,
                        'inhibitors'    : inhibs if inhibs != '' else 0,
                        'barons'        : barons if barons != '' else 0,
                        'dragons'       : dragons if dragons != '' else 0,
                        'rift_heralds'  : rift_heralds if rift_heralds != '' else 0
                    }
                }

            date_time = game.css('div.sb-datetime-date span::text').get()
            date_time = date_time.split(',')

            teams = game.css('span.teamname a::text').getall()

            #0 is blue win, 1 is red win
            winner = game.css('tr:nth-of-type(2) th::attr(class)').get()
            winner = 0 if 'winner' in winner else 1

            duration = game.css('tr:nth-of-type(3) th:nth-of-type(2)::text').get()
            duration = duration.split(':')
            duration = 60 * int(duration[0]) + int(duration[1])
            
            blue_team_players = game.css('tr.sb-allw:nth-of-type(5) td.side-blue')
            blue_info = parse_team_info(blue_team_players)
            red_team_players = game.css('tr.sb-allw:nth-of-type(5) td.side-red')
            red_info = parse_team_info(red_team_players)

            blue_extra_info_query = game.css('tr.sb-allw:nth-of-type(7) td.side-blue')
            blue_extra_info = parse_team_extra_info(blue_extra_info_query)
            red_extra_info_query = game.css('tr.sb-allw:nth-of-type(7) td.side-red')
            red_extra_info = parse_team_extra_info(red_extra_info_query)

            patch = game.css('div.sb-datetime-patch a::text').get(default='N/A')

            vod = game.css('div.sb-datetime-vod a::attr(href)').get(default='N/A')

            game = {
                'datetime'          :   dt.datetime(int(date_time[0]), int(date_time[1]), int(date_time[2]), hour=int(date_time[3]), minute=int(date_time[4])),
                'season'            :   int(date_time[0])-2010,
                'blue_team'         :   teams[0],
                'red_team'          :   teams[1],   
                'winner'            :   winner,
                'duration'          :   duration,
                'blue_team_gold'    :   blue_info[0],
                'blue_team_kills'   :   blue_info[1],
                'red_team_gold'     :   red_info[0],
                'red_team_kills'    :   red_info[1],                
                'blue_team_players' :   blue_info[2],
                'red_team_players'  :   red_info[2],                
                'blue_bans'         :   blue_extra_info['bans'],
                'blue_objectives'   :   blue_extra_info['objectives'],
                'red_bans'          :   red_extra_info['bans'],
                'red_objectives'    :   red_extra_info['objectives'],
                'patch'             :   patch,
                'VOD'               :   vod
            }

            return game

        split = parse_split()

        for game in response.css('table.sb'):
            yield {
                'league' : split[0],
                'year'   : split[1],
                'season' : split[2],
                'data'   : parse_game(game)
            }
