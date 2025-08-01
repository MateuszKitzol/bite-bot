import os
import asyncio
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from pydantic import BaseModel, SecretStr
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.runnables import ConfigurableField
from langchain_core.tools import tool
from langchain.callbacks.base import AsyncCallbackHandler
from langchain_core.messages import AIMessage, ToolMessage, BaseMessage, HumanMessage

from tools import final_answer, get_food_nutrients

# Correctly load the .env file from the backend directory
load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), '.env'))

# Constants and Configuration
OPENAI_API_KEY = SecretStr(os.environ["OPENAI_API_KEY"])

# Initialize LangChain
llm = ChatOpenAI(
    model="gpt-4o-mini",
    temperature=0.0,
    streaming=True,
    api_key=OPENAI_API_KEY
).configurable_fields(
    callbacks=ConfigurableField(
        id="callbacks",
        name="callbacks",
        description="A list of callbacks to use for streaming",
    )
)

prompt = ChatPromptTemplate.from_messages([
    ("system", """
     You are a helpful AI assistant that helps users to make their recipes healthier by proposing always 3 various minor modifications to make it healthier.
     Remember the user's personal details (age, sex, height, weight, health targets, exercise level) that you would possibly get in user first message for future interactions.
     At the really beginning you should ask user to deliver a recipe that the user wants to make it healthier and from time to time you can ask them if they have another one to work on?
     Please do not use the same tool more than 5 times in a row. That's really important. 
     """),
    MessagesPlaceholder(variable_name="chat_history"),
    ("human", "{input}"),
    MessagesPlaceholder(variable_name="agent_scratchpad"),
])

tools = [final_answer, get_food_nutrients]
# note when we have sync tools we use tool.func, when async we use tool.coroutine
name2tool = {tool.name: tool.coroutine for tool in tools}

# Streaming Handler
class QueueCallbackHandler(AsyncCallbackHandler):
    def __init__(self, queue: asyncio.Queue):
        self.queue = queue
        self.final_answer_seen = False

    async def __aiter__(self):
        while True:
            if self.queue.empty():
                await asyncio.sleep(0.1)
                continue
            token_or_done = await self.queue.get()
            if token_or_done == "<<DONE>>":
                return
            if token_or_done:
                yield token_or_done
    
    async def on_llm_new_token(self, *args, **kwargs) -> None:
        chunk = kwargs.get("chunk")
        if chunk and chunk.message.additional_kwargs.get("tool_calls"):
            if chunk.message.additional_kwargs["tool_calls"][0]["function"]["name"] == "final_answer":
                self.final_answer_seen = True
        self.queue.put_nowait(kwargs.get("chunk"))
    
    async def on_llm_end(self, *args, **kwargs) -> None:
        if self.final_answer_seen:
            self.queue.put_nowait("<<DONE>>")
        else:
            self.queue.put_nowait("<<STEP_END>>")

async def execute_tool(tool_call: AIMessage) -> ToolMessage:
    tool_name = tool_call.tool_calls[0]["name"]
    tool_args = tool_call.tool_calls[0]["args"]
    tool_out = await name2tool[tool_name](**tool_args)
    return ToolMessage(
        content=f"{tool_out}",
        tool_call_id=tool_call.tool_calls[0]["id"]
    )

# Agent Executor
INITIAL_MESSAGE = AIMessage(content="""
📝 This chat is designed to help you improve your recipes and make them healthier!

🙋‍♂️ To personalize your experience, you can share a few optional details: 
Age, sex, height, weight, your health or fitness goals, and your activity level.

🔒 This information won’t be stored in any database and is only used temporarily 
to better understand your needs and optimize the model’s responses.

🌱 Let's become healthier, one step at a time!
""")

class CustomAgentExecutor:
    def __init__(self, max_iterations: int = 20):
        self.chat_history: list[BaseMessage] = [INITIAL_MESSAGE]
        self.user_profile: dict = {}
        self.max_iterations = max_iterations
        self.agent = (
            {
                "input": lambda x: x["input"],
                "chat_history": lambda x: x["chat_history"],
                "agent_scratchpad": lambda x: x.get("agent_scratchpad", [])
            }
            | prompt
            | llm.bind_tools(tools, tool_choice="any")
        )

    def reset(self):
        self.chat_history = [INITIAL_MESSAGE]
        self.user_profile = {}

    async def invoke(self, input: str, streamer: QueueCallbackHandler, verbose: bool = False) -> dict:
        # invoke the agent but we do this iteratively in a loop until
        # reaching a final answer
        count = 0
        final_answer: str | None = None
        agent_scratchpad: list[AIMessage | ToolMessage] = []
        # streaming function
        async def stream(query: str) -> list[AIMessage]:
            print(f"Query length: {len(query)}")
            print(f"Chat history length: {len(self.chat_history)} messages")
            for i, msg in enumerate(self.chat_history):
                if hasattr(msg, 'content'):
                    print(f"  Chat history message {i} content length: {len(msg.content)}")
                elif hasattr(msg, 'tool_calls'):
                    print(f"  Chat history message {i} tool_calls length: {len(str(msg.tool_calls))}")
            print(f"Agent scratchpad length: {len(agent_scratchpad)} messages")
            for i, msg in enumerate(agent_scratchpad):
                if hasattr(msg, 'content'):
                    print(f"  Agent scratchpad message {i} content length: {len(msg.content)}")
                elif hasattr(msg, 'tool_calls'):
                    print(f"  Agent scratchpad message {i} tool_calls length: {len(str(msg.tool_calls))}")
            response = self.agent.with_config(
                callbacks=[streamer]
            )
            # we initialize the output dictionary that we will be populating with
            # our streamed output
            outputs = []
            # now we begin streaming
            async for token in response.astream({
                "input": query,
                "chat_history": self.chat_history,
                "agent_scratchpad": agent_scratchpad
            }):
                tool_calls = token.additional_kwargs.get("tool_calls")
                if tool_calls:
                    # first check if we have a tool call id - this indicates a new tool
                    if tool_calls[0]["id"]:
                        outputs.append(token)
                    else:
                        outputs[-1] += token
                else:
                    pass
            return [
                AIMessage(
                    content=x.content,
                    tool_calls=x.tool_calls,
                    tool_call_id=x.tool_calls[0]["id"]
                ) for x in outputs
            ]

        while count < self.max_iterations:
            # invoke a step for the agent to generate a tool call
            tool_calls = await stream(query=input)
            # gather tool execution coroutines
            tool_obs = await asyncio.gather(
                *[execute_tool(tool_call) for tool_call in tool_calls]
            )
            # append tool calls and tool observations to the scratchpad in order
            id2tool_obs = {tool_call.tool_call_id: tool_obs for tool_call, tool_obs in zip(tool_calls, tool_obs)}
            for tool_call in tool_calls:
                agent_scratchpad.extend([
                    tool_call,
                    id2tool_obs[tool_call.tool_call_id]
                ])
            
            count += 1
            # if the tool call is the final answer tool, we stop
            found_final_answer = False
            for tool_call in tool_calls:
                if tool_call.tool_calls[0]["name"] == "final_answer":
                    final_answer_call = tool_call.tool_calls[0]
                    final_answer = final_answer_call["args"]["answer"]
                    found_final_answer = True
                    break
            
            # Only break the loop if we found a final answer
            if found_final_answer:
                break
            
        # add the final output to the chat history, we only add the "answer" field
        self.chat_history.extend([
            HumanMessage(content=input),
            AIMessage(content=final_answer if final_answer else "No answer found")
        ])
        # return the final answer in dict form
        return final_answer_call if final_answer else {"answer": "No answer found", "tools_used": []}

# Initialize agent executor
agent_executor = CustomAgentExecutor()
