from langchain_openai import ChatOpenAI
from langchain_core.prompts import (SystemMessagePromptTemplate, ChatPromptTemplate)

template = """
You're a creative consultant brainstorming names for businesses.

You must follow the following principles:
{principles}

Please generate a numerical list of five catchy names for a start-up in the {industry} industry that deals with {context}?

Here is an example of the format:
1. Name1
2. Name2
3. Name3
4. Name4
5. Name5
"""

# A more complex example of using LangChain with prompt templates and LCEL
def main():
    model = ChatOpenAI()
    system_prompt = SystemMessagePromptTemplate.from_template(template)
    chat_prompt = ChatPromptTemplate.from_messages([system_prompt])

    chain = chat_prompt | model

    result = chain.invoke({
        "industry": "technology",
        "context": "artificial intelligence solutions",
        "principles": "1. Be unique and memorable 2. Reflect innovation and cutting-edge technology 3. Easy to pronounce and spell 4. Convey trust and reliability"
    })

    print(result.content)

if __name__ == "__main__":
    main()