from dotenv import load_dotenv
import asyncio
from local_agent.agent import PersonalAssistant
from local_agent.db_service import DBService
import uuid




async def main():
    ## load all environment values
    load_dotenv()
    db_service = DBService()
    agent = PersonalAssistant()
    session_id = str(uuid.uuid4())
    await agent.start_conversation(session_id)

    while(True):
        query = input("What is your query? ")
        await agent.ask_agent(session_id, query)


if __name__ == "__main__":
    asyncio.run(main())
