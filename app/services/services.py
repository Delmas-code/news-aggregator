import os, sys, asyncio, json
current_dir = os.getcwd()
sys.path.append(current_dir)

from app.crud import source as source_crud
from app.services.assets.source_serializer import user_schema
from rss.rss_parser import main as rss_main
from audiotranscription.audio import main as audio_main
from app.core.database import get_db


async def process_batch(batch):
    for item in batch:
        """serialize the item using marshmallow serializer"""
        serialized_item = user_schema.dump(item)
        type = serialized_item['type']

        if type == "rss":

            """call the rss service"""
            result = await rss_main(serialized_item)
        
        if type == "audio":

            """call the audio service"""
            result = await audio_main(serialized_item)

        """Call the NLP Processor"""

        print(f"\n {result} \n")

async def main():

    """Get the sources in chunks"""
    # Get a db session
    async for db_session in get_db():
        # get the individual chunk
        async for batch in source_crud.get_sources_in_batch(db_session, limit=10):

            await process_batch(batch)
            

if __name__ == "__main__":
    asyncio.run(main())
