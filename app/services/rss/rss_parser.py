import os, feedparser, datetime, lxml, sys

from bs4 import BeautifulSoup
from loguru import logger
from app.schemas.source import Source
from app.crud.content import get_source_item_ids
from app.core.database import get_db


current_dir = os.getcwd()
sys.path.append(current_dir)


class ProcessFeed:
    def __init__(self, url: str, source_id: int, source_contents: list) -> None:
        self.url = url
        self.source_id = source_id
        self.source_contents = source_contents

    async def launch(self):
        MAX_TRIES = 3
        TRIAL = 1
        isOkay = False

        try:
            while not isOkay:
                self.feed = feedparser.parse(self.url)
                if self.feed.bozo:
                    if TRIAL == MAX_TRIES and not isOkay:
                        break
                else:
                    isOkay = True   
                TRIAL = TRIAL + 1    
            if not isOkay:
                logger.error(self.feed.bozo_exception)
                # return None  
              
            contents = await self.analyze_feed()
            return contents

        except Exception as e:
            logger.error(f"Something went wrong: {e}")
            return None

    async def analyze_feed(self):
        items = []
        for entry in self.feed.entries:
            content_dict = {}
            content_id = entry['id'] +'_'+ str(datetime.datetime(*entry['published_parsed'][:7])).replace(' ', '_')

            """Check for the validity of the content_id"""
            if content_id in self.source_contents:
                continue
            content_dict['id'] = content_id
            content_dict['source_id'] = self.source_id
            content_dict['title'] = entry.title
            content_dict['url'] = entry.link
            content_dict['type'] = "Text"
            content_dict['body'] = await self.generate_body(entry)

            if not content_dict['body']:
                continue
            content_dict['image_url'] = await self.search_image(entry)
            
            items.append(content_dict)
        
        return items

    async def generate_body(self, entry): 
        description = None

        if 'description' in entry:
            soup = BeautifulSoup(entry.description, 'lxml')

            """some summary got just text with no tags"""
            if soup.find_all():
                paragraphs = soup.find_all('p')

                if paragraphs:
                    description = ''
                    for p in paragraphs:
                        description += p.text
                else:
                    description = soup.text
            else:
                description = entry.description

        return description

    async def search_image(self, entry):
        img_url  = None

        """The images can be gotten either from within the content, the media:thummbnail and the media:group >> media:content"""

        if 'content' in entry:
            content = BeautifulSoup(entry.content[0].value, 'lxml')
            image = content.find('img', recursive=True)
            if image:
                img_url = image['src']

        # check for the media:thumbnail
        elif 'media_thumbnail' in entry:
            img_url = entry['media_thumbnail'][0]['url']

        return img_url


async def main(source: Source):

    """Get all the children ids of each source in the batch"""
    async for db_session in get_db():
        ids = await get_source_item_ids(db = db_session, source_id = source['id'])
        if ids is None:
            return
        
        """Process the feed based on the ite url"""
        feed = ProcessFeed(source['url'], source['id'], ids)
        return await feed.launch()  
