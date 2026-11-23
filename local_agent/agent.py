from google.adk.agents.llm_agent import Agent
from google.adk.sessions import InMemorySessionService
from google.adk.runners import Runner
from google.genai import types


class PersonalAssistant:

    def __init__(self, rag_service):
        ## Barebone setup
        self.__APP_NAME = "weather_tutorial_app"
        self.__USER_ID = "user_1"
        self.__session_service = InMemorySessionService()
        self.__current_session = None
        self.__runner = None
        self.__rag_service = rag_service
        self.__root_agent = Agent(
            model='gemini-3.6-flash',
            name='root_agent',
            description="You are personal agent.",
            instruction=""" 
                You are helpful personal agent, you answer questions related to history of India only, and If the user asks about Old Sage novel, use the 
                query tool which is RAG tool, it will give you the document related to the query. Answer them to the answer.
            """,
            tools=[self.__rag_service.query],
        )

    async def __start_session(self, session_id):
        self.__current_session = await self.__session_service.create_session(
            app_name=self.__APP_NAME,
            user_id=self.__USER_ID,
            session_id=session_id
        )
        print(f"Session created: App='{self.__APP_NAME}', User='{self.__USER_ID}', Session='{session_id}'")

    async def start_conversation(self, session_id):
        await self.__start_session(session_id)
        self.__runner = Runner(
            agent=self.__root_agent,  # The agent we want to run
            app_name=self.__APP_NAME,  # Associates runs with our app
            session_service=self.__session_service  # Uses our session manager
        )

    async def __call_agent_async(self, query: str, session_id):
        """Sends a query to the agent and prints the final response."""
        print(f"\n>>> User Query: {query}")

        # Prepare the user's message in ADK format
        content = types.Content(role='user', parts=[types.Part(text=query)])

        final_response_text = "Agent did not produce a final response."  # Default

        # Key Concept: run_async executes the agent logic and yields Events.
        # We iterate through events to find the final answer.
        async for event in self.__runner.run_async(user_id=self.__USER_ID, session_id=session_id, new_message=content):
            # You can uncomment the line below to see *all* events during execution
            # print(f"  [Event] Author: {event.author}, Type: {type(event).__name__}, Final: {event.is_final_response()}, Content: {event.content}")

            # Key Concept: is_final_response() marks the concluding message for the turn.
            if event.is_final_response():
                if event.content and event.content.parts:
                    # Assuming text response in the first part
                    final_response_text = event.content.parts[0].text
                elif event.actions and event.actions.escalate:  # Handle potential errors/escalations
                    final_response_text = f"Agent escalated: {event.error_message or 'No specific message.'}"
                # Add more checks here if needed (e.g., specific error codes)
                break  # Stop processing events once the final response is found

        print(f"<<< Agent Response: {final_response_text}")

    async def ask_agent(self, session_id, query):
        try:
            await self.__call_agent_async(query, session_id)
        except Exception as e:
            print("Error encountered during the processing")     

    # Mock tool implementation
    def __get_current_time(self, city: str) -> dict:
        """Returns the current time in a specified city."""
        return {"status": "success", "city": city, "time": "10:30 AM"}


