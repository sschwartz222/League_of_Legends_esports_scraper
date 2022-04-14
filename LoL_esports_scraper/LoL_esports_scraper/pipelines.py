import json
from itemadapter import ItemAdapter
from scrapy.exporters import JsonItemExporter

class LolEsportsScraperPipeline:

    files = { 
        'results_china_2014_spring' : [],
        'results_china_2014_summer' : [],
        'results_europe_2014_spring' : [],
        'results_europe_2014_summer' : [],
        'results_NA_2014_spring' : [],
        'results_NA_2014_summer' : [],
        'results_korea_2014_winter' : [],
        'results_korea_2014_spring' : [],
        'results_korea_2014_summer' : [],

        'results_china_2015_spring' : [],
        'results_china_2015_summer' : [],
        'results_europe_2015_spring' : [],
        'results_europe_2015_summer' : [],
        'results_NA_2015_spring' : [],
        'results_NA_2015_summer' : [],
        'results_korea_2015_spring' : [],
        'results_korea_2015_summer' : [],

        'results_china_2016_spring' : [],
        'results_china_2016_summer' : [],
        'results_europe_2016_spring' : [],
        'results_europe_2016_summer' : [],
        'results_NA_2016_spring' : [],
        'results_NA_2016_summer' : [],
        'results_korea_2016_spring' : [],
        'results_korea_2016_summer' : [],

        'results_china_2017_spring' : [],
        'results_china_2017_summer' : [],
        'results_europe_2017_spring' : [],
        'results_europe_2017_summer' : [],
        'results_NA_2017_spring' : [],
        'results_NA_2017_summer' : [],
        'results_korea_2017_spring' : [],
        'results_korea_2017_summer' : [],

        'results_china_2018_spring' : [],
        'results_china_2018_summer' : [],
        'results_europe_2018_spring' : [],
        'results_europe_2018_summer' : [],
        'results_NA_2018_spring' : [],
        'results_NA_2018_summer' : [],
        'results_korea_2018_spring' : [],
        'results_korea_2018_summer' : [],

        'results_china_2019_spring' : [],
        'results_china_2019_summer' : [],
        'results_europe_2019_spring' : [],
        'results_europe_2019_summer' : [],
        'results_NA_2019_spring' : [],
        'results_NA_2019_summer' : [],
        'results_korea_2019_spring' : [],
        'results_korea_2019_summer' : [],

        'results_china_2020_spring' : [],
        'results_china_2020_summer' : [],
        'results_europe_2020_spring' : [],
        'results_europe_2020_summer' : [],
        'results_NA_2020_spring' : [],
        'results_NA_2020_summer' : [],
        'results_korea_2020_spring' : [],
        'results_korea_2020_summer' : [],

        'results_china_2021_spring' : [],
        'results_china_2021_summer' : [],
        'results_europe_2021_spring' : [],
        'results_europe_2021_summer' : [],
        'results_NA_2021_spring' : [],
        'results_NA_2021_summer' : [],
        'results_korea_2021_spring' : [],
        'results_korea_2021_summer' : [],

        'results_all_games' : []
    }

    def close_spider(self, spider):
        #after all info has been parsed, sort results and ship the info into json files
        for key, value in self.files.items():
            #want to sort each result set by game date/time descending (most recent first)
            to_json_sorted = sorted(value, key=(lambda x : x['datetime']))
            to_json_sorted.reverse()

            f = open('results/'+key+'.json', 'wb')

            exporter = JsonItemExporter(f)
            exporter.start_exporting()

            for entry in to_json_sorted:
                exporter.export_item(entry)

            exporter.finish_exporting()        


    def process_item(self, item, spider):
        for key in self.files.keys():
            #looking through the result lists to see if there is a matching one
            #if not then the item must have been an erroneous scrape or it is from
            #pre-2014, when naming conventions for the pages were a little different (currently unsupported)
            if item['league'] in key and item['year'] in key and item['season'] in key:
                self.files[key].append(ItemAdapter(item['data']).asdict())
                self.files['results_all_games'].append(ItemAdapter(item['data']).asdict())

                return item