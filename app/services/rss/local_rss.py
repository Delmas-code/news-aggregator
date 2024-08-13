from bs4 import BeautifulSoup
import os

class ProcessLocalFeeds:
    def __init__(self, filePath, fileFormat = 'xml') -> None:
        
        if os.path.exists(filePath):
            f = open(filePath, "rb") #We consider it to be a file
            doc = f.read()
            
        self.soup = BeautifulSoup(doc, 'lxml')

        if(self.soup.rss):
            self.handleRss()
        
        elif(self.soup.feed):
            self.handleFeed()
        
        assert(self.soup), "Invalid file format"

        f.close()

    def handleRss(self):
        items = self.soup.find_all("item")

        for item in items:
            title = item.title.text
            link = item.link.text
            
            desc = BeautifulSoup(str(item), 'lxml')
            new_desc = BeautifulSoup(str(desc.encoded.text), 'xml')
            
            final_desc = new_desc.find('p')

            print(f"This is the description : \n\n\t {final_desc.text}")
            
            print("\n\n------------------\n\n") 

    def handleFeed(self):
        items = self.soup.find_all("entry")

        for item in items:
            title = item.title.text
            link = item.link['href']
            print(f"Page Title: {title} \nLink : {link} \n------------------\n")    
