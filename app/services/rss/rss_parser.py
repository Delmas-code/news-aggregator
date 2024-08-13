import json, os, feedparser, datetime, lxml, asyncio, sys
current_dir = os.getcwd()
sys.path.append(current_dir)

from bs4 import BeautifulSoup
from assets.getSources import get_sources_in_batch, create_item
from loguru import logger
from app.schemas.content import ContentCreate


current_file_path = os.path.abspath(__file__)

class ProcessFeed:
    def __init__(self, url: str, source_id: int) -> None:
        self.url = url
        self.source_id = source_id

    async def launch(self):
        try:
            self.feed = feedparser.parse(self.url)
            if self.feed.bozo:
                logger.error(self.feed.bozo_exception)
            
            await self.save_content()
            return

        except Exception as e:
            logger.error(f"Something went wrong: {e}")
    
    async def save_content(self):
        async for item in self.analyze_feed():
            # create a db session add item to the db
            new_item = ContentCreate(**item)
            created_item = await create_item(new_item)

            logger.success(f"item created sucessfully: {item['id'], item['title']}")
        
    async def analyze_feed(self):
        for entry in self.feed.entries:
            content_dict = {}
            content_id = entry['id'] +'_'+ str(datetime.datetime(*entry['published_parsed'][:7])).replace(' ', '_')
            content_dict['id'] = content_id
            content_dict['source_id'] = self.source_id
            content_dict['title'] = entry.title
            content_dict['url'] = entry.link
            content_dict['type'] = "Text"
            content_dict['body'] = await self.generate_body(entry)
            content_dict['image_url'] = await self.search_image(entry)

            yield content_dict

    async def generate_body(self, entry):
        if entry.description:
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
        

"""A momentary method for saving all the sources"""
def saveSources(data):
    with open(os.path.join(current_file_path, '..', 'assets', 'sources.json'), "+w") as fp:
        json.dump(data, fp, indent=4)
        fp.close()

async def main():
    async for batch in get_sources_in_batch(10,):
        batch = [{**record.__dict__} for record in batch]
        for item in batch:
            """Process the feed based on the ite url"""
            feed = ProcessFeed(item['url'], item['id'])
            await feed.launch()   

if __name__ == "__main__":
    asyncio.run(main())