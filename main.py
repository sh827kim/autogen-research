from typing import Annotated

from autogen import ConversableAgent, UserProxyAgent, AssistantAgent

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



# agent = ConversableAgent(
#     "chatbot",
#     llm_config=llm_config,
#     code_execution_config = False,
#     function_map=None,
#     human_input_mode="NEVER"
# )
#
#
# reply = agent.generate_reply(messages=[{"content": "Tell me a joke.", "role": "user"}])
# print(reply)


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
