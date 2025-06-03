from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
import streamlit as st
from dotenv import load_dotenv
import time
import json
import os
from datetime import datetime
import uuid

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
    - Emergency Services: 15 or 1122 (Pakistan)
    - Mental Health Helpline: 042-35761999
    - Umang Pakistan Helpline: 0317-4004473
    
    Always consult with qualified healthcare professionals for personalized medical advice.
    """)

def stream_answer(response):
    for word in response.split():
        yield word + " "
        time.sleep(0.04)

def save_conversation_log(session_id, user_message, bot_response):
    """Save conversation to a JSON file"""
    log_entry = {
        "session_id": session_id,
        "timestamp": datetime.now().isoformat(),
        "user_message": user_message,
        "bot_response": bot_response
    }
    
    os.makedirs("conversation_logs", exist_ok=True)
    log_file = f"conversation_logs/conversations_{session_id}.json"
    
    try:
        if os.path.exists(log_file):
            with open(log_file, 'r', encoding='utf-8') as f:
                logs = json.load(f)
        else:
            logs = []
        
        logs.append(log_entry)
        
        with open(log_file, 'w', encoding='utf-8') as f:
            json.dump(logs, f, indent=2, ensure_ascii=False)
            
    except Exception as e:
        st.error(f"Error saving log: {str(e)}")

def save_feedback(session_id, feedback_score, feedback_text=""):
    """Save feedback to a JSON file"""
    feedback_entry = {
        "session_id": session_id,
        "timestamp": datetime.now().isoformat(),
        "feedback_score": feedback_score,
        "feedback_text": feedback_text
    }
    
    os.makedirs("conversation_logs", exist_ok=True)
    feedback_file = f"conversation_logs/feedback_{session_id}.json"
    
    try:
        if os.path.exists(feedback_file):
            with open(feedback_file, 'r', encoding='utf-8') as f:
                feedbacks = json.load(f)
        else:
            feedbacks = []
        
        feedbacks.append(feedback_entry)
        
        with open(feedback_file, 'w', encoding='utf-8') as f:
            json.dump(feedbacks, f, indent=2, ensure_ascii=False)
            
    except Exception as e:
        st.error(f"Error saving feedback: {str(e)}")

def get_all_conversations():
    """Get all conversation data"""
    all_conversations = []
    log_dir = "conversation_logs"
    
    if os.path.exists(log_dir):
        for filename in os.listdir(log_dir):
            if filename.startswith("conversations_") and filename.endswith(".json"):
                filepath = os.path.join(log_dir, filename)
                try:
                    with open(filepath, 'r', encoding='utf-8') as f:
                        conversations = json.load(f)
                        all_conversations.extend(conversations)
                except:
                    continue
    
    return all_conversations

def get_all_feedback():
    """Get all feedback data"""
    all_feedback = []
    log_dir = "conversation_logs"
    
    if os.path.exists(log_dir):
        for filename in os.listdir(log_dir):
            if filename.startswith("feedback_") and filename.endswith(".json"):
                filepath = os.path.join(log_dir, filename)
                try:
                    with open(filepath, 'r', encoding='utf-8') as f:
                        feedback = json.load(f)
                        all_feedback.extend(feedback)
                except:
                    continue
    
    return all_feedback

def show_admin_panel():
    """Show admin panel with password protection"""
    st.markdown("### 🔐 Admin Login")
    
    password = st.text_input("Enter admin password:", type="password")
    
    if password == "admin123":
        st.success("✅ Admin access granted")
        
        # Get data
        conversations = get_all_conversations()
        feedback_data = get_all_feedback()
        
        # Basic stats
        st.markdown("### 📊 Statistics")
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Total Conversations", len(conversations))
        
        with col2:
            unique_sessions = len(set([conv['session_id'] for conv in conversations]))
            st.metric("Unique Users", unique_sessions)
            
        with col3:
            st.metric("Total Feedback", len(feedback_data))
            
        with col4:
            if feedback_data:
                avg_rating = sum([f['feedback_score'] for f in feedback_data]) / len(feedback_data)
                st.metric("Average Rating", f"{avg_rating:.1f}⭐")
            else:
                st.metric("Average Rating", "No data")
        
        # Feedback breakdown
        if feedback_data:
            st.markdown("### ⭐ Feedback Breakdown")
            ratings = [f['feedback_score'] for f in feedback_data]
            
            col1, col2, col3, col4, col5 = st.columns(5)
            for i, col in enumerate([col1, col2, col3, col4, col5], 1):
                count = ratings.count(i)
                with col:
                    st.metric(f"{i} Star", count)
        
        # Download data
        st.markdown("### 📥 Download Data")
        col1, col2 = st.columns(2)
        
        with col1:
            if conversations:
                conv_text = json.dumps(conversations, indent=2, ensure_ascii=False)
                st.download_button(
                    "📄 Download Conversations",
                    conv_text,
                    f"conversations_{datetime.now().strftime('%Y-%m-%d')}.json",
                    "application/json"
                )
        
        with col2:
            if feedback_data:
                feedback_text = json.dumps(feedback_data, indent=2, ensure_ascii=False)
                st.download_button(
                    "⭐ Download Feedback",
                    feedback_text,
                    f"feedback_{datetime.now().strftime('%Y-%m-%d')}.json",
                    "application/json"
                )
                    
    elif password:
        st.error("❌ Invalid password")

# Initialize session states
if 'session_id' not in st.session_state:
    st.session_state.session_id = str(uuid.uuid4())

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

if 'conversation_count' not in st.session_state:
    st.session_state.conversation_count = 0

if 'feedback_given' not in st.session_state:
    st.session_state.feedback_given = False

if 'show_feedback' not in st.session_state:
    st.session_state.show_feedback = False

# Initialize the model
@st.cache_resource
def load_model():
    return ChatGoogleGenerativeAI(
        model='gemini-2.0-flash-exp',  
        temperature=0.3,  
        max_tokens=1000
    )

model = load_model()

# Display chat history
for message in st.session_state.chat_history[1:]:  # Skip system message
    if isinstance(message, HumanMessage):
        with st.chat_message("user"):
            st.markdown(message.content)
    elif isinstance(message, AIMessage):
        with st.chat_message("assistant"):
            st.markdown(message.content)

# Chat input
query = st.chat_input("Share what's on your mind... 💭")

if query:
    st.session_state.chat_history.append(HumanMessage(content=query))
    st.session_state.conversation_count += 1
    
    with st.chat_message("user"):
        st.markdown(query)
    
    with st.chat_message("assistant"):
        try:
            with st.spinner("Thinking..."):
                response = model.invoke(st.session_state.chat_history)
                
            st.session_state.chat_history.append(AIMessage(content=response.content))
            
            # Save conversation
            save_conversation_log(
                st.session_state.session_id,
                query,
                response.content
            )
            
            st.write_stream(stream_answer(response.content))
            
        except Exception as e:
            st.error(f"I'm sorry, I encountered an error: {str(e)}")
            st.info("Please try again or refresh the page if the issue persists.")

# Feedback section
if (st.session_state.conversation_count >= 3 and 
    not st.session_state.feedback_given):
    
    if not st.session_state.show_feedback:
        st.markdown("---")
        if st.button("📝 Share Your Feedback", type="primary"):
            st.session_state.show_feedback = True
            st.rerun()

# Show feedback form
if st.session_state.show_feedback and not st.session_state.feedback_given:
    st.markdown("---")
    st.markdown("### 📝 How was your experience?")
    
    with st.form("feedback_form"):
        # Star rating
        feedback_score = st.selectbox(
            "Rate your experience:",
            [1, 2, 3, 4, 5],
            format_func=lambda x: "⭐" * x + f" ({x}/5)"
        )
        
        feedback_text = st.text_area(
            "Additional comments (optional):",
            placeholder="Share your thoughts..."
        )
        
        col1, col2 = st.columns(2)
        with col1:
            submitted = st.form_submit_button("Submit Feedback", type="primary")
        with col2:
            skip_feedback = st.form_submit_button("Skip")
        
        if submitted:
            save_feedback(st.session_state.session_id, feedback_score, feedback_text)
            st.session_state.feedback_given = True
            st.session_state.show_feedback = False
            st.success("Thank you for your feedback! 🙏")
            st.rerun()
            
        if skip_feedback:
            st.session_state.feedback_given = True
            st.session_state.show_feedback = False
            st.rerun()

# Sidebar
with st.sidebar:
    st.markdown("### 🌟 Quick Mental Health Tips")
    st.markdown("""
    - **Deep Breathing**: Take 5 deep breaths when feeling anxious
    - **Grounding**: Name 5 things you can see, 4 you can touch, 3 you can hear
    - **Self-Care**: Prioritize sleep, nutrition, and gentle movement
    - **Connect**: Reach out to trusted friends or family
    - **Professional Help**: Consider therapy or counseling when needed
    """)
    
    st.markdown("### 📞 Pakistan Crisis Resources")
    st.markdown("""
    - **Emergency Services**: 15 or 1122
    - **Mental Health Helpline**: 042-35761999
    - **Umang Pakistan**: 0317-4004473
    - **Rozan Helpline**: 0800-22444 (Toll-free)
    - **Taskeen Helpline**: 0317-8282374
    - **KTH Crisis Helpline**: 021-32250223
    """)
    
    if st.button("🗑️ Clear Chat History"):
        st.session_state.chat_history = st.session_state.chat_history[:1]  
        st.session_state.conversation_count = 0
        st.session_state.feedback_given = False
        st.session_state.show_feedback = False
        st.session_state.session_id = str(uuid.uuid4())
        st.rerun()

# Admin Panel
with st.sidebar.expander("🔧 Admin Panel"):
    show_admin_panel()

st.markdown("---")
st.markdown(
    "<div style='text-align: center; color: #666;'>"
    "💙 Remember: You're not alone, and it's okay to ask for help. 💙"
    "</div>", 
    unsafe_allow_html=True
)
