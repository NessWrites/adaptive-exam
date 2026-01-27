"""
Adaptive Exam - Streamlit Application
Interactive exam interface for 2D MIRT Adaptive Testing System
"""
import streamlit as st
import requests
from typing import Optional, Dict, Any, List
import time

# API Configuration
API_BASE_URL = "http://127.0.0.1:8000"

# Page configuration
st.set_page_config(
    page_title="Adaptive Exam System",
    page_icon="📝",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .question-box {
        background-color: #f0f2f6;
        padding: 2rem;
        border-radius: 10px;
        border-left: 5px solid #1f77b4;
        margin: 1rem 0;
    }
    .question-text {
        font-size: 1.3rem;
        font-weight: 500;
        color: #262730;
        margin-bottom: 1.5rem;
    }
    .feedback-correct {
        background-color: #d4edda;
        color: #155724;
        padding: 1rem;
        border-radius: 5px;
        border-left: 5px solid #28a745;
    }
    .feedback-incorrect {
        background-color: #f8d7da;
        color: #721c24;
        padding: 1rem;
        border-radius: 5px;
        border-left: 5px solid #dc3545;
    }
    .progress-text {
        font-size: 1.1rem;
        color: #555;
        margin-bottom: 0.5rem;
    }
    .ability-score {
        font-size: 1.5rem;
        font-weight: bold;
        padding: 1rem;
        border-radius: 8px;
        text-align: center;
        margin: 0.5rem 0;
    }
    .math-score {
        background-color: #e3f2fd;
        color: #1976d2;
    }
    .tech-score {
        background-color: #f3e5f5;
        color: #7b1fa2;
    }
</style>
""", unsafe_allow_html=True)


class ExamAPI:
    """API client for Adaptive Exam System"""
    
    @staticmethod
    def start_exam(n_questions: int = 40, user_id: Optional[str] = None) -> Dict[str, Any]:
        """Start a new exam session"""
        try:
            response = requests.post(
                f"{API_BASE_URL}/exam/start",
                json={"n_questions": n_questions, "user_id": user_id},
                timeout=10
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            st.error(f"Failed to start exam: {e}")
            return None
    
    @staticmethod
    def submit_answer(session_id: int, user_answer: Any) -> Dict[str, Any]:
        """Submit answer and get next question"""
        try:
            response = requests.post(
                f"{API_BASE_URL}/exam/submit-answer",
                json={"session_id": session_id, "user_answer": user_answer},
                timeout=10
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            st.error(f"Failed to submit answer: {e}")
            return None
    
    @staticmethod
    def get_results(session_id: int) -> Dict[str, Any]:
        """Get final exam results"""
        try:
            response = requests.get(
                f"{API_BASE_URL}/exam/results/{session_id}",
                timeout=10
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            st.error(f"Failed to get results: {e}")
            return None


def initialize_session_state():
    """Initialize Streamlit session state variables"""
    if 'exam_started' not in st.session_state:
        st.session_state.exam_started = False
    if 'session_id' not in st.session_state:
        st.session_state.session_id = None
    if 'current_question' not in st.session_state:
        st.session_state.current_question = None
    if 'user_answer' not in st.session_state:
        st.session_state.user_answer = None
    if 'feedback' not in st.session_state:
        st.session_state.feedback = None
    if 'exam_completed' not in st.session_state:
        st.session_state.exam_completed = False
    if 'session_info' not in st.session_state:
        st.session_state.session_info = None
    if 'show_feedback' not in st.session_state:
        st.session_state.show_feedback = False


def display_welcome_page():
    """Display welcome page with exam configuration"""
    st.markdown('<div class="main-header">📝 Adaptive Exam System</div>', unsafe_allow_html=True)
    
    st.markdown("""
    ### Welcome to the Adaptive Examination Platform
    
    This exam uses **2D Multidimensional Item Response Theory (MIRT)** to adaptively assess your abilities in:
    - 🔢 **Mathematics** - Problem solving and quantitative reasoning
    - 💻 **Technology** - Technical knowledge and concepts
    
    #### How it works:
    1. Questions are selected based on your current ability estimate
    2. Difficulty adapts to your performance in real-time
    3. More informative questions are prioritized
    4. Your ability is estimated using advanced psychometric models
    """)
    
    st.divider()
    
    # Exam configuration
    col1, col2 = st.columns(2)
    
    with col1:
        user_id = st.text_input("👤 Enter Your Name (Optional)", placeholder="John Doe")
    
    with col2:
        n_questions = st.number_input(
            "📊 Number of Questions",
            min_value=5,
            max_value=100,
            value=40,
            step=5
        )
    
    st.divider()
    
    # Start button
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button("🚀 Start Exam", use_container_width=True, type="primary"):
            with st.spinner("Initializing exam..."):
                response = ExamAPI.start_exam(n_questions=n_questions, user_id=user_id or None)
                
                if response:
                    st.session_state.exam_started = True
                    st.session_state.session_id = response['session']['session_id']
                    st.session_state.current_question = response['question']
                    st.session_state.session_info = response['session']
                    st.rerun()


def display_question(question: Dict[str, Any]):
    """Display current question"""
    st.markdown('<div class="question-box">', unsafe_allow_html=True)
    
    # Question header
    col1, col2 = st.columns([3, 1])
    with col1:
        st.markdown(f'<div class="progress-text">Question {question["question_num"]} of {question["total_questions"]}</div>', 
                   unsafe_allow_html=True)
    with col2:
        st.markdown(f'**Type:** {question["question_type"]}')
    
    # Question text
    st.markdown(f'<div class="question-text">{question["question_text"]}</div>', unsafe_allow_html=True)
    
    # Image if present
    if question.get('image_url'):
        st.image(question['image_url'], use_column_width=True)
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Answer options
    if question['question_type'] == 'MCQ':
        # Single choice
        options_dict = {chr(65 + i): opt for i, opt in enumerate(question['options'])}
        
        selected = st.radio(
            "Select your answer:",
            options=list(options_dict.keys()),
            format_func=lambda x: f"{x}. {options_dict[x]}",
            key=f"mcq_{question['unique_id']}"
        )
        
        return selected
    
    elif question['question_type'] == 'MSQ':
        # Multiple choice
        st.write("**Select all that apply:**")
        
        selected = []
        options_dict = {chr(65 + i): opt for i, opt in enumerate(question['options'])}
        
        for letter, option_text in options_dict.items():
            if st.checkbox(f"{letter}. {option_text}", key=f"msq_{question['unique_id']}_{letter}"):
                selected.append(letter)
        
        return selected if selected else None
    
    return None


def display_feedback(feedback: Dict[str, Any]):
    """Display answer feedback"""
    if feedback['is_correct']:
        st.markdown('<div class="feedback-correct">', unsafe_allow_html=True)
        st.markdown("### ✅ Correct!")
    else:
        st.markdown('<div class="feedback-incorrect">', unsafe_allow_html=True)
        st.markdown("### ❌ Incorrect")
        
        # Show correct answer
        correct = feedback['correct_answer']
        if isinstance(correct, list):
            correct_str = ", ".join(correct)
        else:
            correct_str = correct
        st.markdown(f"**Correct answer:** {correct_str}")
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Current ability estimates
    st.divider()
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown('<div class="ability-score math-score">', unsafe_allow_html=True)
        st.markdown("🔢 **Math Ability**")
        st.markdown(f"{feedback['theta_math']:.2f}")
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col2:
        st.markdown('<div class="ability-score tech-score">', unsafe_allow_html=True)
        st.markdown("💻 **Tech Ability**")
        st.markdown(f"{feedback['theta_tech']:.2f}")
        st.markdown('</div>', unsafe_allow_html=True)


def display_exam_page():
    """Display exam questions page"""
    st.markdown('<div class="main-header">📝 Exam In Progress</div>', unsafe_allow_html=True)
    
    # Progress bar
    if st.session_state.session_info:
        progress = st.session_state.current_question['question_num'] / st.session_state.current_question['total_questions']
        st.progress(progress)
    
    # Show feedback if answer was just submitted
    if st.session_state.show_feedback and st.session_state.feedback:
        display_feedback(st.session_state.feedback)
        
        if st.button("➡️ Next Question", use_container_width=True, type="primary"):
            st.session_state.show_feedback = False
            st.rerun()
        return
    
    # Display question
    if st.session_state.current_question:
        user_answer = display_question(st.session_state.current_question)
        
        st.divider()
        
        # Submit button
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            if st.button("✓ Submit Answer", use_container_width=True, type="primary", 
                        disabled=(user_answer is None)):
                if user_answer:
                    with st.spinner("Submitting answer..."):
                        response = ExamAPI.submit_answer(
                            st.session_state.session_id,
                            user_answer
                        )
                        
                        if response:
                            st.session_state.feedback = response['feedback']
                            st.session_state.show_feedback = True
                            
                            if response['exam_completed']:
                                st.session_state.exam_completed = True
                            else:
                                st.session_state.current_question = response['next_question']
                            
                            st.rerun()


def display_results_page():
    """Display final results page"""
    st.markdown('<div class="main-header">🎉 Exam Completed!</div>', unsafe_allow_html=True)
    
    with st.spinner("Loading results..."):
        results = ExamAPI.get_results(st.session_state.session_id)
    
    if not results:
        st.error("Failed to load results")
        return
    
    # Overall performance
    st.markdown("## 📊 Your Performance")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric(
            "Total Questions",
            results['total_questions']
        )
    
    with col2:
        st.metric(
            "Correct Answers",
            results['correct_answers']
        )
    
    with col3:
        st.metric(
            "Accuracy",
            f"{results['accuracy']:.1f}%"
        )
    
    st.divider()
    
    # Ability estimates
    st.markdown("## 🎯 Ability Estimates")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 🔢 Mathematics")
        math_ability = results['math_ability']
        
        st.metric(
            "Ability Score (θ)",
            f"{math_ability['value']:.2f}",
            help="Higher values indicate greater ability"
        )
        st.metric(
            "Standard Error",
            f"{math_ability['standard_error']:.2f}",
            help="Lower values indicate more precise estimates"
        )
        
        # Interpretation
        interpretation = math_ability['interpretation']
        color = {
            'Exceptional': '🟢',
            'Above Average': '🔵',
            'Average': '🟡',
            'Below Average': '🟠',
            'Needs Improvement': '🔴'
        }.get(interpretation, '⚪')
        
        st.markdown(f"**Level:** {color} {interpretation}")
    
    with col2:
        st.markdown("### 💻 Technology")
        tech_ability = results['tech_ability']
        
        st.metric(
            "Ability Score (θ)",
            f"{tech_ability['value']:.2f}",
            help="Higher values indicate greater ability"
        )
        st.metric(
            "Standard Error",
            f"{tech_ability['standard_error']:.2f}",
            help="Lower values indicate more precise estimates"
        )
        
        # Interpretation
        interpretation = tech_ability['interpretation']
        color = {
            'Exceptional': '🟢',
            'Above Average': '🔵',
            'Average': '🟡',
            'Below Average': '🟠',
            'Needs Improvement': '🔴'
        }.get(interpretation, '⚪')
        
        st.markdown(f"**Level:** {color} {interpretation}")
    
    st.divider()
    
    # Understanding your scores
    with st.expander("📖 Understanding Your Scores"):
        st.markdown("""
        ### Ability Score (θ - theta)
        - **Range:** Typically -3 to +3
        - **Mean:** 0 (average performance)
        - **Standard Deviation:** 1
        
        **Interpretation:**
        - **> +1.5:** Exceptional ability
        - **+0.5 to +1.5:** Above average
        - **-0.5 to +0.5:** Average
        - **-1.5 to -0.5:** Below average
        - **< -1.5:** Needs improvement
        
        ### Standard Error
        The uncertainty in your ability estimate. Lower values mean we're more confident in your score.
        
        ### About 2D-MIRT
        This exam uses a two-dimensional model that separately estimates your mathematics and technology abilities,
        allowing for a more nuanced understanding of your strengths and areas for improvement.
        """)
    
    # Restart button
    st.divider()
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button("🔄 Take Another Exam", use_container_width=True, type="primary"):
            # Reset session state
            for key in list(st.session_state.keys()):
                del st.session_state[key]
            st.rerun()


def display_sidebar():
    """Display sidebar with session information"""
    with st.sidebar:
        st.markdown("## 📊 Session Info")
        
        if st.session_state.exam_started and st.session_state.session_info:
            st.markdown(f"**Session ID:** {st.session_state.session_id}")
            
            if st.session_state.session_info.get('user_id'):
                st.markdown(f"**User:** {st.session_state.session_info['user_id']}")
            
            st.markdown(f"**Questions:** {st.session_state.session_info['n_questions']}")
            
            if st.session_state.current_question:
                st.markdown(f"**Progress:** {st.session_state.current_question['question_num']}/{st.session_state.current_question['total_questions']}")
            
            st.divider()
            
            # Current abilities (if exam in progress)
            if not st.session_state.exam_completed and st.session_state.feedback:
                st.markdown("### Current Estimates")
                st.markdown(f"🔢 Math: **{st.session_state.feedback['theta_math']:.2f}**")
                st.markdown(f"💻 Tech: **{st.session_state.feedback['theta_tech']:.2f}**")
        
        st.divider()
        
        # API Status
        st.markdown("## 🔌 API Status")
        try:
            response = requests.get(f"{API_BASE_URL}/health", timeout=2)
            if response.status_code == 200:
                st.success("✅ Connected")
            else:
                st.error("❌ API Error")
        except:
            st.error("❌ Disconnected")
        
        st.markdown(f"**URL:** `{API_BASE_URL}`")
        
        st.divider()
        
        # About
        with st.expander("ℹ️ About"):
            st.markdown("""
            **Adaptive Exam System**
            
            Version 1.0.0
            
            Built with:
            - FastAPI (Backend)
            - Streamlit (Frontend)
            - 2D-MIRT Algorithm
            - PostgreSQL
            """)


def main():
    """Main application"""
    initialize_session_state()
    display_sidebar()
    
    if not st.session_state.exam_started:
        display_welcome_page()
    elif st.session_state.exam_completed:
        display_results_page()
    else:
        display_exam_page()


if __name__ == "__main__":
    main()