from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
import streamlit as st
from dotenv import load_dotenv
import time

load_dotenv()

st.set_page_config(
    page_title="Serenica - Your Safe Space",
    page_icon="🧠",
    layout="wide"
)

st.header('🧠 Serenica - Your Safe Space in a Noisy World')
st.subheader("*A supportive AI companion for mental wellness*")

# Add disclaimer
with st.expander("⚠️ Important Disclaimer"):
    st.warning("""
    **Please note:** This AI assistant is designed to provide general support and information only. 
    It is not a substitute for professional medical advice, diagnosis, or treatment. 
    
    If you're experiencing a mental health crisis or having thoughts of self-harm, 
    please contact:
    - Emergency Services: 911 (US) or your local emergency number
    - National Suicide Prevention Lifeline: 988 (US)
    - Crisis Text Line: Text HOME to 741741
    
    Always consult with qualified healthcare professionals for personalized medical advice.
    """)

def stream_answer(response):
    for word in response.split():
        yield word + " "
        time.sleep(0.04)

if 'chat_history' not in st.session_state:
    st.session_state.chat_history = [
        SystemMessage(content="""You are Serenica, a compassionate and knowledgeable mental health support assistant. 
        
        Your role is to:
        - Provide empathetic, non-judgmental support
        - Offer evidence-based coping strategies and techniques
        - Help users understand their emotions and thoughts
        - Suggest practical steps for mental wellness
        - Encourage professional help when appropriate
        
        Guidelines:
        - Always be warm, understanding, and supportive
        - Provide balanced responses - concise when appropriate, detailed when needed
        - Focus on solutions and coping strategies
        - Acknowledge the user's feelings and validate their experiences
        - Never diagnose or provide medical advice
        - Encourage professional help for serious concerns
        - Use a conversational, friendly tone
        
        Remember: You're here to support, not replace professional mental health care.""")
    ]

# Initialize the model
@st.cache_resource
def load_model():
    return ChatGoogleGenerativeAI(
        model='gemini-2.0-flash-exp',  
        temperature=0.3,  
        max_tokens=1000
    )

model = load_model()

for message in st.session_state.chat_history[1:]:  # Skip the system message
    if isinstance(message, HumanMessage):
        with st.chat_message("user"):
            st.markdown(message.content)
    elif isinstance(message, AIMessage):
        with st.chat_message("assistant"):
            st.markdown(message.content)

query = st.chat_input("Share what's on your mind... 💭")

if query:

    st.session_state.chat_history.append(HumanMessage(content=query))
    
    with st.chat_message("user"):
        st.markdown(query)
    
    with st.chat_message("assistant"):
        try:
            with st.spinner("Thinking..."):
                response = model.invoke(st.session_state.chat_history)
                
            st.session_state.chat_history.append(AIMessage(content=response.content))
            
            st.write_stream(stream_answer(response.content))
            
        except Exception as e:
            st.error(f"I'm sorry, I encountered an error: {str(e)}")
            st.info("Please try again or refresh the page if the issue persists.")

with st.sidebar:
    st.markdown("### 🌟 Quick Mental Health Tips")
    st.markdown("""
    - **Deep Breathing**: Take 5 deep breaths when feeling anxious
    - **Grounding**: Name 5 things you can see, 4 you can touch, 3 you can hear
    - **Self-Care**: Prioritize sleep, nutrition, and gentle movement
    - **Connect**: Reach out to trusted friends or family
    - **Professional Help**: Consider therapy or counseling when needed
    """)
    
    st.markdown("### 📞 Crisis Resources")
    st.markdown("""
    - **988 Suicide & Crisis Lifeline**: 988
    - **Crisis Text Line**: Text HOME to 741741
    - **SAMHSA Helpline**: 1-800-662-4357
    """)
    
    if st.button("🗑️ Clear Chat History"):
        st.session_state.chat_history = st.session_state.chat_history[:1]  
        st.rerun()

st.markdown("---")
st.markdown(
    "<div style='text-align: center; color: #666;'>"
    "💙 Remember: You're not alone, and it's okay to ask for help. 💙"
    "</div>", 
    unsafe_allow_html=True
)
