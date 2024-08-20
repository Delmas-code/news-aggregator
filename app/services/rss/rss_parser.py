import os, feedparser, datetime, lxml, asyncio, sys
current_dir = os.getcwd()
sys.path.append(current_dir)

from bs4 import BeautifulSoup
from app.services.assets.crud_manager import ( 
    get_sources_in_batch, 
    create_item, 
    get_source_item_ids
)
from loguru import logger
from app.schemas.content import ContentCreate


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
            else:    
                await self.save_content()
            return

        except Exception as e:
            logger.error(f"Something went wrong: {e}")
    
    async def save_content(self):
        async for item in self.analyze_feed():
            # create a db session add item to the 

            new_item = ContentCreate(**item)
            created_item = await create_item(new_item)
  
            if created_item is not None:
                logger.success(f"item created sucessfully: {created_item, self.source_id}")
        
    async def analyze_feed(self):
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

            yield content_dict

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
        

async def main():
    async for batch in get_sources_in_batch(10,):
        batch = [{**record.__dict__} for record in batch]

        for item in batch:

            """Get all the children ids of each source in the batch"""
            ids = await get_source_item_ids(item['id'])
            if ids is None:
                return

            """Process the feed based on the ite url"""
            feed = ProcessFeed(item['url'], item['id'], ids)
            await feed.launch()   

if __name__ == "__main__":
    asyncio.run(main())
    
