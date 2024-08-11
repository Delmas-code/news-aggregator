from bs4 import BeautifulSoup
import feedparser
import json, os, requests
from .assets.getSources import get_sources_in_batch

current_file_path = os.path.abspath(__file__)

class ProcessFeed:

    def __init__(self, url: str, source_id: int) -> None:
        self.url = url
        self.source_id = source_id

    async def launch(self):
        result = await self.fetch_url(self.url)
        status, response = result["status"], result["response"]
        assert(status), response
            
        self.soup = BeautifulSoup(response, features='lxml-xml')

        await self.saveContent()
        
        assert(self.soup), "Invalid file format"


    async def fetch_url(self, page_url):
        try:
            response = requests.get(page_url)
            response.raise_for_status()
            
            # Handle the response based on the status code
            if response.status_code == 200:
                return {'status': True, "response": response.content}
            
            elif response.status_code == 404:
                return {'status': False, "response": "Page not found"}
                
            elif response.status_code == 500:
                return {'status': False, "response": "Server error"}
                
            else:
                return {'status': False, "response": "unexpected status code"}
            
        except Exception as exc:
            return {"status": False, "response": exc}
        

    async def saveContent(self): 
        type = 'Text'
        image_url = None
        
        if(self.soup.rss):
            async for item in self.handleRss():
                # print(f"{json.dumps(item, indent=4)}\n\n")
                pass
        
        elif(self.soup.feed):
            for item in self.handleRss():
                pass


    async def handleRss(self):
        items = self.soup.find_all("item")

        for item in items:
            item_object = {
                'title' : item.title.text,
                'link' : item.link.text,
                'pub_date' : item.pubDate.text,
                'guid' : item.guid.text,
            }

            '''get the body, based on either the description or the body'''

            description = item.find('description')

            print(type(description))

            content_encoded = item.find('content:encoded')

            if description:
                paragraphs = description.find('p')

                if paragraphs:
                    """Process the paragraphs"""
                    print(f"{len(paragraphs)} paragraphs found")
                
                else:
                    print("Not paragraphs")
            
            yield item_object

            
    async def handleFeed(self):
        items = self.soup.find_all("entry")

        for item in items:
            title = item.title.text
            link = item.link['href']


def saveSources(data):
    fp = open(os.path.join(current_file_path, '..', 'assets', 'sources.json'), "+w")
    
    fp.write(json.dumps(data))
    fp.close()


async def main():
    async for batch in get_sources_in_batch(5, field = 'name', value="Coursera"):

        batch = [{**record.__dict__} for record in batch]
        for item in batch:
            """Process the feed based on the ite url"""
            feed = ProcessFeed(item['url'], item['id'])
            await feed.launch()   
