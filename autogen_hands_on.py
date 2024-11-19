from typing import Annotated

from autogen import UserProxyAgent, AssistantAgent, ConversableAgent, GroupChatManager, GroupChat

from config import llm_config

def plus(
        a: Annotated[float, "The first number to add"],
        b: Annotated[float, "The second number to add"]
) -> Annotated[float, "The sum of the two numbers"]:
    return a + b

def minus(
        a: Annotated[float, "The first number to subtract"],
        b: Annotated[float, "The second number to subtract"]
) -> Annotated[float, "The difference of the two numbers"]:
    return a - b

def multiply(
        a: Annotated[float, "The first number to multiply"],
        b: Annotated[float, "The second number to multiply"]
) -> Annotated[float, "The product of the two numbers"]:
    return a * b

def divide(
        a: Annotated[float, "The first number to divide"],
        b: Annotated[float, "The second number to divide"]
) -> Annotated[float, "The quotient of the two numbers"]:
    return a / b

def simple_calculator_chat():
    user_proxy = UserProxyAgent(
        name="user",
        llm_config=False,
        is_termination_msg=lambda x: x.get("content", "") and x.get("content", "").rstrip().endswith("TERMINATE"),
        human_input_mode="NEVER",
        code_execution_config=False,
    )

    assistant = AssistantAgent(
        name="assistant",
        llm_config=llm_config,
        system_message="Only use the tools you have been provided with. Reply TERMINATE when the task is done.",
    )


    assistant.register_for_llm(name="plus", description="Add two numbers")(plus)
    assistant.register_for_llm(name="minus", description="Subtract two numbers")(minus)
    assistant.register_for_llm(name="multiply", description="Multiply two numbers")(multiply)
    assistant.register_for_llm(name="divide", description="Divide two numbers")(divide)

    user_proxy.register_for_execution(name="plus")(plus)
    user_proxy.register_for_execution(name="minus")(minus)
    user_proxy.register_for_execution(name="multiply")(multiply)
    user_proxy.register_for_execution(name="divide")(divide)



    user_proxy.initiate_chat(
        assistant,
        message="2 + 3 * 7 / 3 - 2 ?"
    )


topic_agent = ConversableAgent(
    name="topic_agent",
    system_message="당신은 토론할 주제를 제시하는 역할입니다. 현재 사회적으로 중요한 주제를 하나 선정하여 제시해주세요.",
    llm_config=llm_config,
    human_input_mode="NEVER"
)

economic_agent = ConversableAgent(
    name="economic_agent",
    system_message="당신은 경제학자입니다. 주어진 주제에 대해 경제적 관점에서 의견을 제시해주세요.",
    llm_config=llm_config,
    human_input_mode="NEVER"
)

social_agent = ConversableAgent(
    name="social_agent",
    system_message="당신은 사회학자입니다. 주어진 주제와 이전 의견들을 고려하여 사회적 관점에서 의견을 제시해주세요.",
    llm_config=llm_config,
    human_input_mode="NEVER"
)

environmental_agent = ConversableAgent(
    name="environmental_agent",
    system_message="당신은 환경학자입니다. 주어진 주제와 이전 의견들을 고려하여 환경적 관점에서 의견을 제시해주세요.",
    llm_config=llm_config,
    human_input_mode="NEVER"
)

ethical_agent = ConversableAgent(
    name="ethical_agent",
    system_message="당신은 윤리학자입니다. 주어진 주제와 이전 의견들을 고려하여 윤리적 관점에서 의견을 제시해주세요.",
    llm_config=llm_config,
    human_input_mode="NEVER"
)

def run_sequential_chat():

    topic = "AI 윤리"

    topic_agent.initiate_chats(
        [
            {
                "recipient": economic_agent,
                "message": f"다음 주제에 대해 경제적 관점에서 의견을 제시해주세요: {topic}",
                "max_turns": 2,
                "summary_method": "last_msg"
            },
            {
                "recipient": social_agent,
                "message": f"다음 주제에 대해 사회적 관점에서 의견을 제시해주세요: {topic}",
                "max_turns": 2,
                "summary_method": "last_msg"
            },
            {
                "recipient": environmental_agent,
                "message": f"다음 주제에 대해 환경적 관점에서 의견을 제시해주세요: {topic}",
                "max_turns": 2,
                "summary_method": "last_msg"
            },
            {
                "recipient": ethical_agent,
                "message": f"다음 주제에 대해 윤리적 관점에서 의견을 제시해주세요: {topic}",
                "max_turns": 2,
                "summary_method": "last_msg"
            }
        ]
    )

def run_group_chat():
    group_chat = GroupChat(
        agents=[
            topic_agent,
            economic_agent,
            social_agent,
            environmental_agent,
            ethical_agent,
        ],
        messages=[],
        max_round=6,
    )

    group_chat_manager = GroupChatManager(
        groupchat=group_chat,
        llm_config=llm_config,
    )

    chat_result = topic_agent.initiate_chat(
        group_chat_manager,
        message="AI 윤리에 대해 대화를 나눠주세요",
        summary_method="reflection_with_llm"
    )
