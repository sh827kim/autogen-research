# Tool 정의
import functools
import operator
from datetime import datetime
from typing import Annotated, Literal, TypedDict, Sequence

from langchain_core.messages import BaseMessage, AIMessage, HumanMessage
from langchain_core.output_parsers import JsonOutputParser
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.tools import tool
from langgraph.checkpoint.memory import MemorySaver
from langgraph.constants import START, END
from langgraph.graph import StateGraph
from langgraph.prebuilt import create_react_agent
from pydantic import BaseModel

from config import llm


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
    print(f"{phone_number}\n{content}")
    return {
        "result":"Success"
    }

# 상태 관리 클래스 정의
class AgentState(TypedDict):
    messages: Annotated[Sequence[BaseMessage], operator.add]
    next: str

# Supervisor Node 결과 클래스 정의
class RouteResult(BaseModel):
    next: Literal['Searcher', 'RobotController', 'Postman', 'Finisher']

# Supervisor Node 실행 및 다음 Node 결정 함수
def supervisor_node(state:AgentState):
    result = supervisor_agent.invoke(state)

    parsed_result = RouteResult.model_validate(supervisor_output_parser.invoke(result))
    result = AIMessage(content=result.content, name="Supervisor")
    return {
        "messages": [result],
        "next": parsed_result.next
    }

# Agent Node 실행 함수
def agent_route(state:AgentState, agent, name:str):
    messages = agent.invoke(state)
    result = messages['messages'][-1]

    return {
        "messages": [AIMessage(content=result.content, name=name)],
    }

# Agent 정의
supervisor_output_parser = JsonOutputParser(pydantic_object=RouteResult)
supervisor_agent = ChatPromptTemplate.from_messages([
    ("system", "당신은 다른 에이전트들의 작업을 감독하고, 적절한 에이전트를 선택하여 작업을 진행하는 감독자 역할입니다. 주어진 주제와 이전 의견들을 고려하여 적절한 에이전트를 선택하고, 해당 에이전트에게 작업을 지시해주세요. 작업이 끝나면 Finisher 를 호출하세요. 주어진 에이전트는 Searcher, RobotController, Postman, Finisher 가 있습니다.\n {format_instructions}"),
    MessagesPlaceholder(variable_name="messages"),
]).partial(format_instructions=supervisor_output_parser.get_format_instructions()) | llm

searcher_agent = create_react_agent(
    llm,
    tools = [search_vehicles, search_vehicle_owners],
    state_modifier="당신은 차량 정보 검색 역할을 담당하는 에이전트입니다. 주어진 주제와 이전 의견들을 고려하여 관련 정보를 도구를 활용하여 검색하고, 검색 결과를 제시해주세요. 단, 선택사항에 없는 도구는 사용할 수 없으며, 모르는 정보는 모른다고 답변해주세요. 없는 도구에 대해 시스템 내부에서 처리할거라 가정하면 안됩니다. 당신은 다음 에이전트를 선택할 권한이 없습니다."
)

robot_controller_agent = create_react_agent(
    llm,
    tools = [send_vehicle_to_repair_shop, send_vehicle_to_home],
    state_modifier="당신은 차량을 제어하는 역할을 담당하는 에이전트입니다. 이전 채팅 이력들을 고려하여 관련 정보를 도구를 활용하여 차량을 제어하세요. 단, 선택사항에 없는 도구는 사용할 수 없으며, 모르는 정보는 모른다고 답변해주세요. 없는 도구에 대해 시스템 내부에서 처리할거라 가정하면 안됩니다. 당신은 다음 에이전트를 선택할 권한이 없습니다."
)

postman_agent = create_react_agent(
    llm,
    tools = [send_sms],
    state_modifier="당신은 SMS 발송을 담당하는 에이전트입니다. 주어진 주제와 이전 의견들을 고려하여 관련 정보를 도구를 활용하여 SMS를 발송하고, 결과를 제시해주세요. 단, 선택사항에 없는 도구는 사용할 수 없으며, 모르는 정보는 모른다고 답변해주세요. 없는 도구에 대해 시스템 내부에서 처리할거라 가정하면 안됩니다. 당신은 다음 에이전트를 선택할 권한이 없습니다."
)


# 그래프 생성

workflow = StateGraph(AgentState)
workflow.add_node("Supervisor", supervisor_node)
workflow.add_node("Searcher", functools.partial(agent_route, agent=searcher_agent, name="Searcher"))
workflow.add_node("RobotController", functools.partial(agent_route, agent=robot_controller_agent, name="RobotController"))
workflow.add_node("Postman", functools.partial(agent_route, agent=postman_agent, name="Postman"))

workflow.add_edge(START, "Supervisor")
workflow.add_conditional_edges(
    "Supervisor",
    lambda state: state["next"],
    {
        "Searcher": "Searcher",
        "RobotController": "RobotController",
        "Postman": "Postman",
        "Finisher": END
    }
)

for node in ["Searcher", "RobotController", "Postman"]:
    workflow.add_edge(node, "Supervisor")

memory = MemorySaver()
graph = workflow.compile(checkpointer=memory)

# 질문 생성 및 그래프 실행
question = "가장 최근 데이터를 보낸 차량을 정비소로 보내고, 정비소로 보낸 차량의 정보를 SMS로 보내주세요. 제 휴대폰 번호는 010-0000-0000입니다."

graph_stream = graph.stream({"messages":[HumanMessage(content=question)]}, config={"configurable": {"thread_id":"2"}})

start_time = datetime.now()
print(f"대화 시작 : {start_time.strftime('%Y-%m-%d %H:%M:%S')}")
for message in graph_stream:
    valueList = list(message.values())

    message = valueList[0]['messages'][0]
    print("--------------------------------------------------------------------------------\n")
    print(f"Next Agent : {message.name}\n")
    print(f"{message.content}\n")

end_time = datetime.now()
print(f"대화 종료 : {end_time.strftime('%Y-%m-%d %H:%M:%S')}")
print(f"대화 소요 시간 : {end_time - start_time}")
