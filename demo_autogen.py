from typing import Annotated, Literal

from autogen import ConversableAgent, GroupChat, GroupChatManager

from config import llm_config
# Tool 정의
def search_vehicles(order_by: Annotated[Literal["ASC", "DESC"], "order condition"])-> list[dict]:
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

def search_vehicle_owners(order_by: Annotated[Literal["ASC", "DESC"], "order condition"]) -> list[dict]:
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

def send_vehicle_to_repair_shop(vehicle_id:Annotated[str, "Vehicle ID to be sent to the repair shop"]) -> dict:
    return {
        "vehicle_id":vehicle_id,
        "result":"Success"
    }

def send_vehicle_to_home(vehicle_id:Annotated[str, "Vehicle ID to be sent to home"]) -> dict:
    return {
        "vehicle_id":vehicle_id,
        "result":"Success"
    }

def send_sms(phone_number:Annotated[str, "phone number"], content:Annotated[str, "Content to send SMS"]) -> dict:
    print("--------- SMS Contents ---------")
    print(f"{phone_number}\n{content}")
    print("--------- SMS Done ---------")
    return {
        "result":"Success"
    }

# Agent 정의
supervisor_agent = ConversableAgent(
    name="supervisor_agent",
    system_message="당신은 다른 에이전트들의 작업을 감독하고, 적절한 에이전트를 선택하여 작업을 진행하는 감독자 역할입니다. 주어진 주제와 이전 의견들을 고려하여 적절한 에이전트를 선택하고, 해당 에이전트에게 작업을 지시해주세요. 작업이 끝나면 'TERMINATE'를 입력해주세요.",
    is_termination_msg=lambda x: x.get("content", "") and x.get("content", "").rstrip().endswith("TERMINATE"),
    llm_config=llm_config,
    human_input_mode="NEVER"
)

searcher_agent = ConversableAgent(
    name="vehicle_searcher_agent",
    system_message="당신은 차량 정보 검색 역할을 담당하는 에이전트입니다. 주어진 주제와 이전 의견들을 고려하여 관련 정보를 도구를 활용하여 검색하고, 검색 결과를 제시해주세요. 단, 하나의 도구만 선택해야합니다.",
    llm_config=llm_config,
    human_input_mode="NEVER"
)

vehicle_controller_agent = ConversableAgent(
    name="vehicle_controller_agent",
    system_message="당신은 자동차를 제어 역할을 담당하는 에이전트입니다. 주어진 주제와 이전 의견들을 고려하여 주어진 도구를 활용하여 자동차를 제어해주세요.",
    llm_config=llm_config,
    human_input_mode="NEVER"
)

postman_agent = ConversableAgent(
    name="postman_agent",
    system_message="당신은 SMS 발송을 담당하는 에이전트입니다. 주어진 주제와 이전 의견들을 고려하여 주어진 도구를 활용하여 SMS를 발송해주세요.",
    llm_config=llm_config,
    human_input_mode="NEVER"
)

# Tool 실행용 Agent 정의
tool_executor = ConversableAgent(
    name="tool_executor",
    llm_config=False,
    human_input_mode="NEVER"
)


# Tool 등록
searcher_agent.register_for_llm(name="search_vehicles", description="차량 목록 검색")(search_vehicles)
searcher_agent.register_for_llm(name="search_vehicle_owners", description="차주 목록 검색")(search_vehicle_owners)

vehicle_controller_agent.register_for_llm(name="send_vehicle_to_repair_shop", description="차량을 정비소로 보내기")(send_vehicle_to_repair_shop)
vehicle_controller_agent.register_for_llm(name="send_vehicle_to_home", description="차량을 집으로 보내기")(send_vehicle_to_home)

postman_agent.register_for_llm(name="send_sms", description="문자 전송")(send_sms)


tool_executor.register_for_execution(name="search_vehicles")(search_vehicles)
tool_executor.register_for_execution(name="search_vehicle_owners")(search_vehicle_owners)

tool_executor.register_for_execution(name="send_vehicle_to_repair_shop")(send_vehicle_to_repair_shop)
tool_executor.register_for_execution(name="send_vehicle_to_home")(send_vehicle_to_home)

tool_executor.register_for_execution(name="send_sms")(send_sms)

# GroupChat 생성
group_chat = GroupChat(
    agents=[
        supervisor_agent,
        searcher_agent,
        vehicle_controller_agent,
        postman_agent,
        tool_executor
    ],
    messages=[],
    max_round=10,
)

group_chat_manager = GroupChatManager(
    groupchat=group_chat,
    llm_config=llm_config,
)

question = "가장 최근 데이터를 보낸 차량을 정비소로 보내고, 정비소로 보낸 차량의 정보를 SMS로 보내주세요. 제 휴대폰 번호는 010-0000-0000입니다."


# 대화 시작
chat_result = supervisor_agent.initiate_chat(
    group_chat_manager,
    message=question,
    summary_method="reflection_with_llm"
)

# print(chat_result.chat_history)
# print(chat_result.summary)
