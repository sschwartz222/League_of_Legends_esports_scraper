BOT_NAME = 'LoL_esports_scraper'

SPIDER_MODULES = ['LoL_esports_scraper.spiders']
NEWSPIDER_MODULE = 'LoL_esports_scraper.spiders'

ROBOTSTXT_OBEY = True

ITEM_PIPELINES = {
   'LoL_esports_scraper.pipelines.LolEsportsScraperPipeline': 300,
}
