from langchain_openai import ChatOpenAI
from langchain_core.messages import AIMessage, SystemMessage, HumanMessage

# A simple example of using LangChain to interact with OpenAI's chat models
def main():
    chat = ChatOpenAI(temperature=0.9, model="gpt-4o-mini")
    messages = [
        SystemMessage(content="Act as a senior software engineer at a startup company"),
        HumanMessage(content="Please can you provide a random funny dark joke about engineers?")
    ]
    response = chat.invoke(messages)
    print(response.content)

if __name__ == "__main__":
    main()