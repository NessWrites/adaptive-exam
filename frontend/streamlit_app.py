"""
Enhanced Adaptive Exam - Streamlit Application
Updated for 50 questions (40 operational + 10 pretest) with QPool integration
"""
import streamlit as st
import requests
from typing import Optional, Dict, Any, List

# API Configuration
API_BASE_URL = "http://127.0.0.1:8001"

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
    .breakdown-box {
        background-color: #f8f9fa;
        padding: 1rem;
        border-radius: 8px;
        border-left: 4px solid #6c757d;
        margin: 0.5rem 0;
    }
</style>
""", unsafe_allow_html=True)


class ExamAPI:
    """API client for Enhanced Adaptive Exam System"""
    
    @staticmethod
    def start_exam() -> Dict[str, Any]:
        """Start a new exam - GET request"""
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
    if 'answer_history' not in st.session_state:
        st.session_state.answer_history = []


def display_welcome_page():
    """Display welcome page"""
    st.markdown('<div class="main-header">Adaptive Exam System</div>', unsafe_allow_html=True)
    
    st.markdown("""
    ### Welcome to the Enhanced Adaptive Examination Platform
    
    This exam uses **2D Multidimensional Item Response Theory (MIRT)** to adaptively assess your abilities in:
    - **Mathematics** - Problem solving and quantitative reasoning
    - **Technology** - Technical knowledge and concepts
    
    #### How it works:
    1. You will answer **50 questions** total
       - **40 operational questions** that count toward your score
       - **10 pretest questions** for research purposes (randomly placed)
    2. Questions adapt to your performance in real-time
    3. Some questions may be paraphrased for variety
    4. Each answer helps us better estimate your ability
    5. Final results show your ability in both domains
    
    #### Instructions:
    - Read each question carefully
    - Select your answer(s)
    - Click "Submit Answer" to continue
    - You cannot go back to previous questions
    - Pretest questions help us improve the exam but don't affect your score
    
    #### About Question Paraphrasing:
    Some technology questions may appear in slightly different wordings to ensure fairness 
    and reduce memorization. This is done automatically and transparently.
    """)
    
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
    
    # Question header with progress and unique_id
    col1, col2 = st.columns([3, 1])
    with col1:
        st.markdown(
            f'<div class="progress-text">Question {question_num} of 50</div>', 
            unsafe_allow_html=True
        )
    with col2:
        st.markdown(
            f'<div class="progress-text" style="text-align: right; color: #888;">ID: {question["unique_id"]}</div>', 
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
    """Display exam questions page"""
    st.markdown('<div class="main-header">Exam In Progress</div>', unsafe_allow_html=True)
    
    # Progress bar
    progress = st.session_state.question_num / 50
    st.progress(progress)
    
    # Display question
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
                    with st.spinner("Processing answer..."):
                        response = ExamAPI.submit_answer(
                            st.session_state.session_id,
                            user_answer
                        )
                        
                        if response:
                            # Store answer in history
                            st.session_state.answer_history.append({
                                'question_num': st.session_state.question_num,
                                'question_id': st.session_state.current_question['unique_id'],
                                'user_answer': user_answer,
                                'is_correct': response['feedback']['is_correct']
                            })
                            
                            # Check if exam completed
                            if response['exam_completed']:
                                st.session_state.exam_completed = True
                            else:
                                st.session_state.current_question = response['next_question']
                                st.session_state.question_num = response['feedback']['question_num'] + 1
                            
                            st.rerun()


def display_results_page():
    """Display final results page with enhanced breakdown"""
    st.markdown('<div class="main-header">Exam Completed</div>', unsafe_allow_html=True)
    
    with st.spinner("Loading results..."):
        results = ExamAPI.get_results(st.session_state.session_id)
    
    if not results:
        st.error("Failed to load results")
        return
    
    # Overall performance
    st.markdown("## Overall Performance")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric(
            "Total Questions Answered",
            results['total_questions']
        )
    
    with col2:
        st.metric(
            "Correct Answers",
            results['correct_answers']
        )
    
    with col3:
        st.metric(
            "Overall Accuracy",
            f"{results['accuracy']:.1f}%"
        )
    
    st.divider()
    
    # Breakdown section (NEW!)
    st.markdown("## Question Breakdown")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown('<div class="breakdown-box">', unsafe_allow_html=True)
        st.markdown("### Operational Questions (Scored)")
        st.markdown(f"**Total:** {results['operational_questions']}")
        st.markdown(f"**Correct:** {results['operational_correct']}")
        
        operational_accuracy = (results['operational_correct'] / results['operational_questions'] * 100) if results['operational_questions'] > 0 else 0
        st.markdown(f"**Accuracy:** {operational_accuracy:.1f}%")
        
        st.markdown("These questions determined your ability scores")
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col2:
        pretest_total = results['total_questions'] - results['operational_questions']
        pretest_correct = results['correct_answers'] - results['operational_correct']
        
        st.markdown('<div class="breakdown-box">', unsafe_allow_html=True)
        st.markdown("### Pretest Questions (Research)")
        st.markdown(f"**Total:** {pretest_total}")
        st.markdown(f"**Correct:** {pretest_correct}")
        
        if pretest_total > 0:
            pretest_accuracy = (pretest_correct / pretest_total * 100)
            st.markdown(f"**Accuracy:** {pretest_accuracy:.1f}%")
        
        st.markdown("These questions help us improve the exam")
        st.markdown('</div>', unsafe_allow_html=True)
    
    st.divider()
    
    # Ability estimates
    st.markdown("## Ability Estimates")
    st.markdown("*Based on 10 operational questions*")
    
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
        interpretation = math_ability['interpretation']
        st.markdown(f"### {interpretation}")
    
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
        interpretation = tech_ability['interpretation']
        st.markdown(f"### {interpretation}")
    
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
        
        ### Overall Accuracy vs Operational Accuracy
        - **Overall Accuracy:** All 50 questions (including pretest)
        - **Operational Accuracy:** Only the 40 scored questions
        - Your ability scores are based only on operational questions
        
        ### About Pretest Questions
        Pretest questions are experimental items we're testing for future exams. They don't affect 
        your score but help us maintain exam quality. You won't know which questions are pretest 
        during the exam.
        
        ### Question Paraphrasing
        Some technology questions may have been paraphrased using AI to provide variety while 
        maintaining the same difficulty and concept being tested.
        
        ### About 2D-MIRT
        This exam uses a two-dimensional model that separately estimates your mathematics and technology 
        abilities, allowing for a more nuanced understanding of your strengths and areas for improvement.
        """)
    
    # Performance details
    with st.expander("Detailed Performance Analysis"):
        st.markdown("### Your Performance Summary")
        
        st.markdown(f"""
        **Total Questions:** {results['total_questions']}
        - Operational (Scored): {results['operational_questions']}
        - Pretest (Research): {results['total_questions'] - results['operational_questions']}
        
        **Correct Answers:** {results['correct_answers']}
        - Operational: {results['operational_correct']}
        - Pretest: {results['correct_answers'] - results['operational_correct']}
        
        **Mathematics Domain:**
        - Ability Score: {results['math_ability']['value']:.2f}
        - Standard Error: {results['math_ability']['standard_error']:.3f}
        - Level: {results['math_ability']['interpretation']}
        
        **Technology Domain:**
        - Ability Score: {results['tech_ability']['value']:.2f}
        - Standard Error: {results['tech_ability']['standard_error']:.3f}
        - Level: {results['tech_ability']['interpretation']}
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
    """Display sidebar with enhanced session information"""
    with st.sidebar:
        st.markdown("## Session Info")
        
        if st.session_state.exam_started:
            st.markdown(f"**Session ID:** {st.session_state.session_id}")
            st.markdown(f"**Total Questions:** 50")
            st.markdown("- 40 Operational (scored)")
            st.markdown("- 10 Pretest (research)")
            
            if not st.session_state.exam_completed:
                st.markdown(f"**Current:** Question {st.session_state.question_num}/50")
                
                # Progress percentage
                progress_pct = (st.session_state.question_num / 50) * 100
                st.markdown(f"**Progress:** {progress_pct:.0f}%")
                
                # Answered count
                answered = len(st.session_state.answer_history)
                st.markdown(f"**Answered:** {answered}")
        
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
            
            Version 3.0 (Enhanced)
            
            **Features:**
            - 50 questions (40 operational + 10 pretest)
            - 2D-MIRT algorithm
            - Question paraphrasing (QPool)
            - Real-time adaptation
            - Separate scoring for operational items
            
            **Built with:**
            - FastAPI (Backend)
            - Streamlit (Frontend)
            - PostgreSQL (Database)
            - Python IRT Engine
            - QPool API (Paraphrasing)
            """)
        
        # QPool info
        with st.expander("QPool Integration"):
            st.markdown("""
            **Question Paraphrasing:**
            
            Some technology questions may be paraphrased 
            to provide variety while maintaining the 
            same difficulty level.
            
            **How it works:**
            - Only tech questions are paraphrased
            - Approximately 50% of tech questions use paraphrasing
            - Math questions remain unchanged
            - IRT parameters are preserved
            - Scoring is unaffected
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