from dotenv import load_dotenv
from agent import PersonalAssistant
from db_service import DBService
from rag_service import RAGService
import uuid
import asyncio


async def main():
    ## load all environment values
    load_dotenv()
    db_service = DBService()
    agent = PersonalAssistant()
    rag_service = RAGService(db_service)
    # session_id = str(uuid.uuid4())
    # await agent.start_conversation(session_id)

    # while(True):
    #     query = input("What is your query? ")
    #     await agent.ask_agent(session_id, query)
    rag_service.embedd_docs("old_sage_story.pdf")

if __name__ == "__main__":
    asyncio.run(main())
