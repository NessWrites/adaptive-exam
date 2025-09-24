import streamlit as st
import pandas as pd
from cat_logic import CATSimulator
from pathlib import Path

st.set_page_config(layout="wide", page_title="AI Fellowship CAT Exam")

def initialize_cat():
    """Initializes or resets the CAT session."""
    qbank_path= Path('qbank.csv')
    return CATSimulator(qbank_path)

def transform_theta_to_score(theta, scale_max=15, theta_min=-3.0, theta_max=3.0):
    """Transforms a theta score to a scale (e.g., 0-15)."""
    score = scale_max * (theta - theta_min) / (theta_max - theta_min)
    return max(0, min(scale_max, round(score, 2)))

# --- Main App Logic ---
st.title("🧑‍💻 AI Fellowship Adaptive Test")
st.markdown("This is a demonstration of a computerized adaptive test (CAT). The system selects questions based on your estimated ability level to maximize measurement precision. Questions will get harder or easier based on your answers.")
st.markdown("---")

# Initialize or get the session state
if 'cat_session' not in st.session_state:
    st.session_state.cat_session = initialize_cat()
    next_item, reason = st.session_state.cat_session.select_next_item()
    st.session_state.current_item = next_item
    st.session_state.cat_session.log.append({'initial_reason': reason}) # Log initial selection
    st.session_state.test_finished = False

# Get current state from session
cat = st.session_state.cat_session
item = st.session_state.current_item
total_questions_in_test = cat.test_length

if not st.session_state.test_finished and item is not None:
    col1, col2, col3 = st.columns([2, 1, 1])

    with col1:
        current_q_num = len(cat.administered_items) + 1
        st.write(f"#### Question {current_q_num} of {total_questions_in_test}")
        st.progress(current_q_num / total_questions_in_test)

        st.subheader(item['content'])
        options = [opt.strip() for opt in item['options'].split(';')]

        with st.form(key=f"q_{item['item_id']}"):
            if item['question_type'] == 'MCQ-Single':
                user_choice = st.radio(
                    "Select your answer:",
                    options=options,
                    format_func=lambda x: x.split(') ', 1)[1]
                )
            elif item['question_type'] == 'MCQ-Multiple':
                user_choice = st.multiselect(
                    "Select all correct answers:",
                    options=options,
                    format_func=lambda x: x.split(') ', 1)[1]
                )
            
            submitted = st.form_submit_button("Submit Answer")

            if submitted:
                if item['question_type'] == 'MCQ-Single':
                    user_answer_keys = [user_choice.split(')')[0]] if user_choice else []
                else:
                    user_answer_keys = [choice.split(')')[0] for choice in user_choice]

                cat.administer_item(item['item_id'], user_answer_keys)
                
                next_item, reason = cat.select_next_item()
                
                if cat.log:
                    cat.log[-1]['scs_decision_for_next'] = reason
                    
                st.session_state.current_item = next_item
                
                if next_item is None or current_q_num >= total_questions_in_test:
                    st.session_state.test_finished = True
                
                st.rerun()

    with col2:
        st.info(f"#### Current Ability Estimate ($\Theta$): **{cat.theta:.3f}**")
        st.write("This score updates after each answer. A positive score indicates above-average ability, while a negative score indicates below-average ability on the measured trait.")
        st.markdown("---")
        st.write("**Item Parameters (for nerds):**")
        st.markdown(f"- **Topic:** {item['topic']}")
        st.markdown(f"- **Cognitive Level:** {item['cognitive_level']}")
        st.markdown(f"- **Difficulty (b):** `{item['b']:.2f}` (Higher is harder)")
        st.markdown(f"- **Discrimination (a):** `{item['a']:.2f}` (Higher means more informative)")
        st.markdown(f"- **Guessing (c):** `{item['c']:.2f}` (Probability of guessing correctly)")

    with col3:
        st.info("#### ⚙️ Real-time Test Log")
        if cat.log:
            # Display logs in reverse order for real-time feel
            for idx in range(len(cat.log)-1, -1, -1):
                log_entry = cat.log[idx]
                if 'q_num' in log_entry:
                    with st.expander(f"Question {log_entry['q_num']} Details", expanded=(idx == len(cat.log)-1)):
                        st.markdown(f"**Question:** {log_entry['item_content'][:50]}...")
                        st.markdown(f"**Topic:** {log_entry.get('item_topic', 'N/A')}")
                        st.markdown(f"**Cognitive Level:** {log_entry.get('item_cognitive_level', 'N/A')}")
                        st.markdown(f"**Correct:** {log_entry['response_correct']}")
                        st.markdown(f"**$\Theta$ Change:** {log_entry['theta_change']:+.3f}")
                        
                        if 'scs_decision_for_next' in log_entry:
                            st.markdown("**Next Question Selection:**")
                            st.warning(log_entry['scs_decision_for_next'])

else:
    st.success("🎉 You have completed the exam!")
    st.balloons()
    
    final_theta = cat.theta
    final_score = transform_theta_to_score(final_theta)

    st.header("Final Exam Results")
    col1, col2 = st.columns(2)
    with col1:
        st.metric(label="Final Ability Score ($\Theta$)", value=f"{final_theta:.3f}")
    with col2:
        st.metric(label=f"Scaled Score (out of {total_questions_in_test})", value=f"{final_score}")
    
    grade = "Pass" if final_theta > 0.0 else "Needs Improvement"
    st.write(f"**Outcome:** {grade}")

    st.markdown("---")
    st.header("📜 Detailed Test Log")
    st.write("This log shows the step-by-step process of the adaptive test.")

    for entry in cat.log:
        if 'q_num' in entry: # Skip initial log entry
            with st.expander(f"**Question {entry['q_num']}: {entry['item_content'][:50]}...**"):
                st.markdown(f"##### Question Details")
                st.text(f"  - Item ID: {entry['item_id']}")
                st.text(f"  - Topic: {entry.get('item_topic', 'N/A')}")
                st.text(f"  - Cognitive Level: {entry.get('item_cognitive_level', 'N/A')}")
                st.text(f"  - Difficulty (b-parameter): {entry['item_difficulty_b']:.3f}")

                st.markdown(f"##### Your Performance")
                color = "green" if entry['response_correct'] == 'Yes' else "red"
                st.markdown(f"  - Your Response was <span style='color:{color}; font-weight:bold;'>{entry['response_correct']}</span>.", unsafe_allow_html=True)

                st.markdown(f"##### Ability ($\Theta$) Update")
                st.markdown(f"  - $\Theta$ before answer: `{entry['theta_before']:.3f}`")
                st.markdown(f"  - $\Theta$ after answer:  `{entry['theta_after']:.3f}`")
                st.markdown(f"  - Change in $\Theta$: `{entry['theta_change']:+.3f}`")
                
                st.markdown(f"##### Next Question Selection Logic")
                st.info(f"**Reasoning:** {entry.get('scs_decision_for_next', 'End of test.')}")


    if st.button("Restart Exam"):
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        st.rerun()