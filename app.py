from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.memory import ConversationBufferMemory
from langchain_core.output_parsers import StrOutputParser
from langchain_core.messages import HumanMessage,AIMessage,SystemMessage
import streamlit as st
from dotenv import load_dotenv
import time

load_dotenv()

st.header('🧠 - Serenica - Your Safe Space in a Noisy World.')

def stream_answer(response):
    for word in response:
        yield word
        time.sleep(0.02)

chat_history = [SystemMessage(content='You are a helpful psychiatry consultant. Users will query you about their different problems and you have to proceed accordingly. Keep note of the fact that your answers should be well rounded and short and long whenever needed. Also as you are a consultant your job is to come up with solution to the users problem.')]

model = ChatGoogleGenerativeAI(api_key='AIzaSyAD_5B9jJvIrEareYhHLMTsP-SrPku8Yns',model='gemini-2.0-flash',temperature=0.1)

query = st.chat_input('Ask Away')

if query:
    chat_history.append(HumanMessage(content=query))
    with st.chat_message('human'):
        st.markdown(query)

    with st.chat_message('ai'):
        response = model.invoke(chat_history)
        chat_history.append(AIMessage(content=response.content))
        st.write_stream(stream_answer(response.content))
        
