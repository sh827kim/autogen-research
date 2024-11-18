from autogen import ConversableAgent

from config import llm_config

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


topic = "AI 윤리"

chat_results = topic_agent.initiate_chats(
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


