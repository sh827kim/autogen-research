from autogen import GroupChat, GroupChatManager

from config import llm_config
from sequential_chat import topic_agent, economic_agent, social_agent, environmental_agent, ethical_agent



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
