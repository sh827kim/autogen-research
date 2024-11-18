# Tool 정의
import functools
import operator
from typing import Annotated, Literal, TypedDict, Sequence

from dotenv import load_dotenv
from langchain_core.messages import BaseMessage, AIMessage, ToolMessage
from langchain_core.output_parsers import JsonOutputParser
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.runnables import ConfigurableField
from langchain_core.tools import tool
from langchain_openai import AzureChatOpenAI
from pydantic import BaseModel

load_dotenv()
llm = (AzureChatOpenAI(azure_deployment='gpt-4o', api_version="2024-06-01", http_client=http_client, http_async_client=http_async_client, temperature=temperature, max_tokens=300, cache=True)
.configurable_alternatives(
    ConfigurableField(id="model"),
    default_key="gpt-4o",
    mini=AzureChatOpenAI(azure_deployment='gpt-4o-mini', api_version="2024-06-01", http_client=http_client, http_async_client=http_async_client, temperature=temperature, max_tokens=300, cache=True),
))

@tool
def search_vehicles(order_by: Annotated[Literal["ASC", "DESC"], "order condition"])-> list[dict]:
    """Search vehicles"""
    print(order_by)
    return [
        {
            "id":1,
            "name":"붕붕이",
            "last_transfer_date":"2024-11-18"
        },
        {
            "id":2,
            "name":"빵빵이",
            "last_transfer_date":"2024-11-17"
        },
        {
            "id":3,
            "name":"부릉이",
            "last_transfer_date":"2024-11-16"
        }
    ]

@tool
def search_vehicle_owners(order_by: Annotated[Literal["ASC", "DESC"], "order condition"]) -> list[dict]:
    """Search vehicle owners"""
    return [
        {
            "id":1,
            "name":"홍길동",
            "vehicle_id":1
        },
        {
            "id":2,
            "name":"김길동",
            "vehicle_id":2
        },
        {
            "id":3,
            "name":"박길동",
            "vehicle_id":3
        }
    ]

@tool
def send_vehicle_to_repair_shop(vehicle_id:Annotated[str, "Vehicle ID to be sent to the repair shop"]) -> dict:
    """Send vehicle to repair shop"""
    return {
        "vehicle_id":vehicle_id,
        "result":"Success"
    }

@tool
def send_vehicle_to_home(vehicle_id:Annotated[str, "Vehicle ID to be sent to home"]) -> dict:
    """Send vehicle to home"""
    return {
        "vehicle_id":vehicle_id,
        "result":"Success"
    }

@tool
def send_sms(phone_number:Annotated[str, "phone number"], content:Annotated[str, "Content to send SMS"]) -> dict:
    """Send SMS"""
    print("--------- SMS Contents ---------")
    print(f"{phone_number}\n{content}")
    print("--------- SMS Done ---------")
    return {
        "result":"Success"
    }

class AgentState(TypedDict):
    messages: Annotated[Sequence[BaseMessage], operator.add]
    next: str

class RouteResult(BaseModel):
    next: Literal['Searcher', 'RobotController', 'Postman']


supervisor_output_parser = JsonOutputParser(pydantic_object=RouteResult)

supervisor_agent = ChatPromptTemplate.from_messages([
    ("system", "당신은 다른 에이전트들의 작업을 감독하고, 적절한 에이전트를 선택하여 작업을 진행하는 감독자 역할입니다. 주어진 주제와 이전 의견들을 고려하여 적절한 에이전트를 선택하고, 해당 에이전트에게 작업을 지시해주세요. 작업이 끝나면 END 를 호출하세요. 주어진 에이전트는 Searcher, RobotController, Postman 이 있습니다.\n {format_instructions}"),
    MessagesPlaceholder(variable_name="messages"),
]).partial(format_instructions=supervisor_output_parser.get_format_instructions()) | llm

searcher_agent = ChatPromptTemplate.from_messages([
    ("system", "당신은 차량 정보 검색 역할을 담당하는 에이전트입니다. 주어진 주제와 이전 의견들을 고려하여 관련 정보를 도구를 활용하여 검색하고, 검색 결과를 제시해주세요. 단, 하나의 도구만 선택해야합니다. 주어진 도구:{tools}"),
    MessagesPlaceholder(variable_name="messages"),
]).partial(tools=", ".join(tool.name for tool in [search_vehicles, search_vehicle_owners])) | llm


robot_controller_agent = ChatPromptTemplate.from_messages([
    ("system", "당신은 차량을 제어하는 역할을 담당하는 에이전트입니다. 주어진 주제와 이전 의견들을 고려하여 관련 정보를 도구를 활용하여 차량을 제어하고, 결과를 제시해주세요. 단, 하나의 도구만 선택해야합니다. 주어진 도구:{tools}"),
    MessagesPlaceholder(variable_name="messages"),
]).partial(tools=", ".join(tool.name for tool in [send_vehicle_to_repair_shop, send_vehicle_to_home])) | llm


postman_agent = ChatPromptTemplate.from_messages([
    ("system", "당신은 SMS 발송을 담당하는 에이전트입니다. 주어진 주제와 이전 의견들을 고려하여 관련 정보를 도구를 활용하여 SMS를 발송하고, 결과를 제시해주세요. 단, 하나의 도구만 선택해야합니다. 주어진 도구:{tools}"),
    MessagesPlaceholder(variable_name="messages"),
]).partial(tools=", ".join(tool.name for tool in [send_sms])) | llm

def supervisor_route(state:AgentState):
    result = supervisor_agent.invoke(state)
    parsed_result = RouteResult.model_validate(supervisor_output_parser.invoke(result))
    result = AIMessage(**result.dict(exclude={"name"}), name="Supervisor")
    return {
        "messages": [result],
        "next": parsed_result.next
    }

def agent_route(state:AgentState, agent, name:str):
    result = agent.invoke(state)
    if isinstance(result, ToolMessage):
        pass
    return {
        "messages": [AIMessage(**result.dict(exclude={"type", "name"}), name=name)],
    }

searcher_agent_node = functools.partial(agent_route, agent=searcher_agent, name="Searcher")
robot_controller_agent_node = functools.partial(agent_route, agent=robot_controller_agent, name="RobotController")
postman_agent_node = functools.partial(agent_route, agent=postman_agent, name="Postman")

