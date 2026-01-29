"""
Adaptive Exam with Pretest Support - Streamlit Application
50 questions total: 40 operational (scored) + 10 pretest (calibration)
"""
import streamlit as st
import requests
from typing import Optional, Dict, Any, List

# API Configuration
API_BASE_URL = "http://127.0.0.1:8000"

# Page configuration
st.set_page_config(
    page_title="Adaptive Exam",
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
    .progress-text {
        font-size: 1.1rem;
        color: #555;
        margin-bottom: 0.5rem;
    }
    .ability-score {
        font-size: 1.5rem;
        font-weight: bold;
        padding: 1.5rem;
        border-radius: 8px;
        text-align: center;
        margin: 0.5rem 0;
    }
    .math-score {
        background-color: #e3f2fd;
        color: #1976d2;
        border: 2px solid #1976d2;
    }
    .tech-score {
        background-color: #f3e5f5;
        color: #7b1fa2;
        border: 2px solid #7b1fa2;
    }
    .info-note {
        background-color: #fff3cd;
        border-left: 5px solid #ffc107;
        padding: 1rem;
        margin: 1rem 0;
        border-radius: 5px;
    }
</style>
""", unsafe_allow_html=True)


class ExamAPI:
    """API client for Adaptive Exam System with Pretest Support"""
    
    @staticmethod
    def start_exam() -> Dict[str, Any]:
        """Start a new exam - GET request, no parameters"""
        try:
            response = requests.get(
                f"{API_BASE_URL}/exam/start",
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
    if 'question_num' not in st.session_state:
        st.session_state.question_num = 1
    if 'exam_completed' not in st.session_state:
        st.session_state.exam_completed = False


def display_welcome_page():
    """Display welcome page"""
    st.markdown('<div class="main-header">Adaptive Exam System</div>', unsafe_allow_html=True)
    
    st.markdown("""
    ### Welcome to the Adaptive Examination Platform
    
    This exam uses **2D Multidimensional Item Response Theory (MIRT)** to adaptively assess your abilities in:
    - **Mathematics** - Problem solving and quantitative reasoning
    - **Technology** - Technical knowledge and concepts
    
    #### How it works:
    1. You will answer **50 questions** total
    2. Questions adapt to your performance in real-time
    3. Each answer helps us better estimate your ability
    4. Final results show your ability in both domains
    
    #### Instructions:
    - Read each question carefully
    - Select your answer(s)
    - Click "Submit Answer" to continue
    - You cannot go back to previous questions
    """)
    
    # Info note about scoring
    st.markdown("""
    <div class="info-note">
    <strong>Note:</strong> Your final score is based on 40 scored questions. 
    Some questions are used for research purposes and do not affect your score.
    </div>
    """, unsafe_allow_html=True)
    
    st.divider()
    
    # Start button
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button("Start Exam", use_container_width=True, type="primary"):
            with st.spinner("Initializing exam..."):
                response = ExamAPI.start_exam()
                
                if response:
                    st.session_state.exam_started = True
                    st.session_state.session_id = response['session_id']
                    st.session_state.current_question = response['question']
                    st.session_state.question_num = 1
                    st.rerun()


def display_question(question: Dict[str, Any], question_num: int):
    """Display current question"""
    st.markdown('<div class="question-box">', unsafe_allow_html=True)
    
    # Question header
    st.markdown(
        f'<div class="progress-text">Question {question_num} of 50</div>', 
        unsafe_allow_html=True
    )
    
    # Question text
    st.markdown(
        f'<div class="question-text">{question["question_text"]}</div>', 
        unsafe_allow_html=True
    )
    
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
            key=f"mcq_{question['unique_id']}_{question_num}"
        )
        
        return selected
    
    elif question['question_type'] == 'MSQ':
        # Multiple choice
        st.write("**Select all that apply:**")
        
        selected = []
        options_dict = {chr(65 + i): opt for i, opt in enumerate(question['options'])}
        
        for letter, option_text in options_dict.items():
            if st.checkbox(
                f"{letter}. {option_text}", 
                key=f"msq_{question['unique_id']}_{question_num}_{letter}"
            ):
                selected.append(letter)
        
        return selected if selected else None
    
    return None


def display_exam_page():
    """Display exam questions page - no feedback shown"""
    st.markdown('<div class="main-header">Exam In Progress</div>', unsafe_allow_html=True)
    
    # Progress bar
    progress = st.session_state.question_num / 50
    st.progress(progress)
    
    # Display question directly (no feedback step)
    if st.session_state.current_question:
        user_answer = display_question(
            st.session_state.current_question, 
            st.session_state.question_num
        )
        
        st.divider()
        
        # Submit button
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            if st.button(
                "Submit Answer", 
                use_container_width=True, 
                type="primary",
                disabled=(user_answer is None)
            ):
                if user_answer:
                    with st.spinner("Loading next question..."):
                        response = ExamAPI.submit_answer(
                            st.session_state.session_id,
                            user_answer
                        )
                        
                        if response:
                            # No feedback display - just move to next question
                            if response['exam_completed']:
                                st.session_state.exam_completed = True
                            else:
                                st.session_state.current_question = response['next_question']
                                st.session_state.question_num = response['feedback']['question_num'] + 1
                            
                            st.rerun()


def display_results_page():
    """Display final results page"""
    st.markdown('<div class="main-header">Exam Completed</div>', unsafe_allow_html=True)
    
    with st.spinner("Loading results..."):
        results = ExamAPI.get_results(st.session_state.session_id)
    
    if not results:
        st.error("Failed to load results")
        return
    
    # Overall performance
    st.markdown("## Your Performance")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric(
            "Scored Questions",
            results['total_questions'],
            help="Questions that counted toward your score"
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
    
    # Info about pretest items
    st.markdown("""
    <div class="info-note">
    <strong>Scoring Note:</strong> You answered 50 questions total. 
    Your score is based on 40 scored questions. The remaining 10 questions 
    were used for research and quality improvement.
    </div>
    """, unsafe_allow_html=True)
    
    st.divider()
    
    # Ability estimates
    st.markdown("## Ability Estimates")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### Mathematics")
        math_ability = results['math_ability']
        
        # Display score box
        st.markdown('<div class="ability-score math-score">', unsafe_allow_html=True)
        st.markdown(f"**Ability Score (θ)**<br>{math_ability['value']:.2f}", unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
        
        st.metric(
            "Standard Error",
            f"{math_ability['standard_error']:.3f}",
            help="Lower values indicate more precise estimates"
        )
        
        # Interpretation
        st.markdown(f"### {math_ability['interpretation']}")
    
    with col2:
        st.markdown("### Technology")
        tech_ability = results['tech_ability']
        
        # Display score box
        st.markdown('<div class="ability-score tech-score">', unsafe_allow_html=True)
        st.markdown(f"**Ability Score (θ)**<br>{tech_ability['value']:.2f}", unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
        
        st.metric(
            "Standard Error",
            f"{tech_ability['standard_error']:.3f}",
            help="Lower values indicate more precise estimates"
        )
        
        # Interpretation
        st.markdown(f"### {tech_ability['interpretation']}")
    
    st.divider()
    
    # Understanding your scores
    with st.expander("Understanding Your Scores"):
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
        Typical range: 0.3 to 1.0
        
        ### Accuracy
        The percentage of **scored questions** you answered correctly. Note that in adaptive testing, 
        this is less important than your theta score, as harder questions are worth "more" in determining ability.
        
        ### About 2D-MIRT
        This exam uses a two-dimensional model that separately estimates your mathematics and technology 
        abilities, allowing for a more nuanced understanding of your strengths and areas for improvement.
        
        ### About Pretest Items
        Some questions in this exam are being tested for future use. These questions do not affect your 
        score but help us improve the exam quality over time. You won't know which questions are pretest 
        items - just answer all questions to the best of your ability.
        """)
    
    # Restart button
    st.divider()
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button("Take Another Exam", use_container_width=True, type="primary"):
            # Reset session state
            for key in list(st.session_state.keys()):
                del st.session_state[key]
            st.rerun()


def display_sidebar():
    """Display sidebar with session information"""
    with st.sidebar:
        st.markdown("## Session Info")
        
        if st.session_state.exam_started:
            st.markdown(f"**Session ID:** {st.session_state.session_id}")
            st.markdown(f"**Total Questions:** 50")
            
            if not st.session_state.exam_completed:
                st.markdown(f"**Current:** Question {st.session_state.question_num}/50")
                
                # Progress percentage
                progress_pct = (st.session_state.question_num / 50) * 100
                st.markdown(f"**Progress:** {progress_pct:.0f}%")
        
        st.divider()
        
        # API Status
        st.markdown("## API Status")
        try:
            response = requests.get(f"{API_BASE_URL}/health", timeout=2)
            if response.status_code == 200:
                st.success("Connected")
            else:
                st.error("API Error")
        except:
            st.error("Disconnected")
        
        st.markdown(f"**URL:** `{API_BASE_URL}`")
        
        st.divider()
        
        # About
        with st.expander("About"):
            st.markdown("""
            **Adaptive Exam System**
            
            Version 3.0 (With Pretest)
            
            **Features:**
            - 50 total questions
            - 40 scored (adaptive)
            - 10 pretest (calibration)
            - 2D-MIRT algorithm
            - Real-time adaptation
            
            **Built with:**
            - FastAPI (Backend)
            - Streamlit (Frontend)
            - PostgreSQL (Database)
            - Python IRT Engine
            
            **Pretest Items:**
            Some questions help us improve 
            the exam but don't affect your 
            score. This is standard practice 
            in professional testing (GRE, 
            GMAT, etc.)
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