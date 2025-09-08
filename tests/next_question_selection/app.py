import streamlit as st
import pandas as pd
from cat_logic import CATSimulator

st.set_page_config(layout="centered", page_title="AI Fellowship CAT Exam")

def initialize_cat():
    """Initializes the CAT session."""
    return CATSimulator(qbank_path='qbank.csv')

# --- Main App Logic ---
st.title("🤖 AI Fellowship Adaptive Test")

# Initialize or get the session state
if 'cat_session' not in st.session_state:
    st.session_state.cat_session = initialize_cat()
    st.session_state.current_item = st.session_state.cat_session.select_next_item()
    st.session_state.test_finished = False

cat = st.session_state.cat_session
item = st.session_state.current_item

if not st.session_state.test_finished:
    # Display progress
    total_questions = len(cat.qbank)
    current_q_num = len(cat.administered_items) + 1
    st.write(f"**Question {current_q_num} of {total_questions}**")

    st.info(f"Current Ability Estimate ($\Theta$): **{cat.theta:.3f}**")
    
    st.markdown("---")
    
    # Display the question
    st.subheader(item['content'])
    options = [opt.strip() for opt in item['options'].split(';')]
    option_labels = [f"{opt.split(')')[0]})" for opt in options]
    
    with st.form(key=f"q_{item['item_id']}"):
        user_choice = st.radio(
            "Select your answer:",
            options=options,
            format_func=lambda x: x.split(') ')[1]
        )
        submitted = st.form_submit_button("Submit Answer")

        if submitted:
            user_answer_key = user_choice.split(')')[0]
            is_correct = (user_answer_key == item['correct_answer'])
            
            # Administer item and update state
            cat.administer_item(item['item_id'], is_correct)
            
            # Select next item
            st.session_state.current_item = cat.select_next_item()
            if st.session_state.current_item is None or current_q_num >= 15: # Stop after 15 questions for demo
                st.session_state.test_finished = True
            
            st.rerun()

else:
    # Test is finished
    st.success("🎉 You have completed the exam!")
    st.balloons()
    
    final_theta = cat.theta
    st.subheader("Final Exam Results")
    st.metric(label="Final Ability Score ($\Theta$)", value=f"{final_theta:.3f}")
    
    # You can map theta to a grade here. e.g., using a predefined scale.
    grade = "Pass" if final_theta > 0.5 else "Needs Improvement"
    st.write(f"**Grade:** {grade}")

    st.markdown("---")
    st.write("### Your Response History:")
    
    history_df = pd.DataFrame({
        'Question': [item['content'][:40] + '...' for item in cat.administered_items],
        'Your Response': ['Correct' if r == 1 else 'Incorrect' for r in cat.responses],
        'Question Difficulty (b)': [f"{item['b']:.2f}" for item in cat.administered_items]
    })
    st.dataframe(history_df)

    if st.button("Restart Exam"):
        st.session_state.clear()
        st.rerun()