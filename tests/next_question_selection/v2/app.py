import streamlit as st
import pandas as pd
from cat_logic import CATSimulator  # Your enhanced CAT logic
from pathlib import Path
import json
import plotly.express as px
import plotly.graph_objects as go

st.set_page_config(layout="wide", page_title="Enhanced AI Fellowship CAT Exam")

def initialize_cat():
    """Initializes or resets the CAT session."""
    qbank_path = Path('qbank.csv')
    return CATSimulator(qbank_path)

def transform_theta_to_score(theta, scale_max=15, theta_min=-3.0, theta_max=3.0):
    """Transforms a theta score to a scale (e.g., 0-15)."""
    score = scale_max * (theta - theta_min) / (theta_max - theta_min)
    return max(0, min(scale_max, round(score, 2)))

def create_constraint_chart(constraint_status):
    """Create a visual chart showing constraint fulfillment."""
    fig = go.Figure()
    
    for constraint_type, constraints in constraint_status.items():
        categories = list(constraints.keys())
        fulfilled = [status['fulfilled'] for status in constraints.values()]
        required = [status['required'] for status in constraints.values()]
        
        fig.add_trace(go.Bar(
            name=f'{constraint_type} - Fulfilled',
            x=categories,
            y=fulfilled,
            marker_color='lightblue'
        ))
        
        fig.add_trace(go.Bar(
            name=f'{constraint_type} - Required',
            x=categories,
            y=required,
            marker_color='darkblue',
            opacity=0.6
        ))
    
    fig.update_layout(
        title="Content Constraint Fulfillment",
        xaxis_title="Categories",
        yaxis_title="Count",
        barmode='overlay',
        height=300
    )
    
    return fig

# --- Main App Logic ---
st.title("🤖 Enhanced AI Fellowship Adaptive Test")
st.markdown("""
This is an **advanced** Computerized Adaptive Test (CAT) with:
- **Combined Score Selection**: Balances Fisher Information and Content Constraints
- **Adaptive Weighting**: Dynamically adjusts constraint importance during test
- **Diversity Control**: Prevents repetitive question patterns
- **Enhanced Logging**: Detailed tracking of decision-making process
""")
st.markdown("---")

# Initialize or get the session state
if 'cat_session' not in st.session_state:
    st.session_state.cat_session = initialize_cat()
    next_item, reason = st.session_state.cat_session.select_next_item()
    st.session_state.current_item = next_item
    st.session_state.test_finished = False
    st.session_state.answer_submitted = False
    st.session_state.show_feedback = False

# Get current state from session
cat = st.session_state.cat_session
item = st.session_state.current_item
total_questions_in_test = cat.blueprint['total_questions']

if not st.session_state.test_finished and item is not None:
    col1, col2, col3 = st.columns([2.5, 1.5, 1.5])

    with col1:
        # Display progress
        current_q_num = len(cat.administered_items) + 1
        st.write(f"#### Question {current_q_num} of {total_questions_in_test}")
        st.progress(current_q_num / total_questions_in_test)

        # Display the question
        st.subheader(item['content'])
        options = [opt.strip() for opt in item['options'].split(';')]

        # Show answer form only if answer hasn't been submitted
        if not st.session_state.answer_submitted:
            with st.form(key=f"q_{item['item_id']}"):
                if item['question_type'] == 'MCQ-Single':
                    user_choice = st.radio(
                        "Select your answer:",
                        options=options,
                        format_func=lambda x: x.split(') ', 1)[1] if ') ' in x else x
                    )
                elif item['question_type'] == 'MCQ-Multiple':
                    user_choice = st.multiselect(
                        "Select all correct answers:",
                        options=options,
                        format_func=lambda x: x.split(') ', 1)[1] if ') ' in x else x
                    )
                
                submitted = st.form_submit_button("Submit Answer", type="primary")

                if submitted:
                    # Process the answer
                    if item['question_type'] == 'MCQ-Single':
                        if user_choice:
                            user_answer_keys = [user_choice.split(')')[0]]
                        else:
                            user_answer_keys = []
                    else:
                        user_answer_keys = [choice.split(')')[0] for choice in user_choice]

                    # Store the answer in session state
                    st.session_state.user_answer_keys = user_answer_keys
                    st.session_state.answer_submitted = True
                    st.session_state.show_feedback = True
                    st.rerun()

        # Show feedback and next button if answer has been submitted
        if st.session_state.answer_submitted and st.session_state.show_feedback:
            # Administer the item and show feedback
            cat.administer_item(item['item_id'], st.session_state.user_answer_keys)
            
            # Show immediate feedback
            latest_log = cat.log[-1] if cat.log else {}
            
            st.markdown("---")
            st.subheader("📊 Answer Feedback")
            
            # Answer correctness
            if latest_log.get('response_correct') == 'Yes':
                st.success("✅ Correct!")
            else:
                st.error("❌ Incorrect")
                correct_answer = latest_log.get('correct_answer', [])
                st.info(f"Correct answer(s): {', '.join(correct_answer)}")
            
            # Theta change
            theta_change = latest_log.get('theta_change', 0)
            if theta_change > 0:
                st.info(f"📈 Ability estimate increased by {theta_change:.3f}")
            elif theta_change < 0:
                st.warning(f"📉 Ability estimate decreased by {abs(theta_change):.3f}")
            else:
                st.info("➡️ Ability estimate unchanged")

            # Current constraints status
            if 'constraint_status' in latest_log:
                st.markdown("### Content Balance Status")
                constraint_status = latest_log['constraint_status']
                
                # Create two columns for constraint display
                con_col1, con_col2 = st.columns(2)
                
                with con_col1:
                    st.write("**Topics:**")
                    for value, status in constraint_status.get('topic', {}).items():
                        fulfilled = status['fulfilled']
                        required = status['required']
                        ratio = status['ratio']
                        if ratio >= 1.0:
                            st.success(f"✅ {value}: {fulfilled}/{required}")
                        elif ratio >= 0.5:
                            st.warning(f"⚠️ {value}: {fulfilled}/{required}")
                        else:
                            st.error(f"❌ {value}: {fulfilled}/{required}")

                with con_col2:
                    st.write("**Cognitive Levels:**")
                    for value, status in constraint_status.get('cognitive_level', {}).items():
                        fulfilled = status['fulfilled']
                        required = status['required']
                        ratio = status['ratio']
                        if ratio >= 1.0:
                            st.success(f"✅ {value}: {fulfilled}/{required}")
                        elif ratio >= 0.5:
                            st.warning(f"⚠️ {value}: {fulfilled}/{required}")
                        else:
                            st.error(f"❌ {value}: {fulfilled}/{required}")

            # Next question button
            if st.button("➡️ Next Question", type="primary"):
                # Select next item
                next_item, reason = cat.select_next_item()
                
                # Update log with selection reason
                if cat.log:
                    cat.log[-1]['next_selection_reason'] = reason
                    
                st.session_state.current_item = next_item
                st.session_state.answer_submitted = False
                st.session_state.show_feedback = False
                
                if next_item is None or current_q_num >= total_questions_in_test:
                    st.session_state.test_finished = True
                
                st.rerun()

    with col2:
        st.info(f"#### Current Ability (θ): **{cat.theta:.3f}**")
        st.write("Updates after each answer. Positive = above average, Negative = below average")
        
        st.markdown("---")
        st.write("**Current Question Details:**")
        st.markdown(f"- **Topic:** {item['topic']}")
        st.markdown(f"- **Cognitive Level:** {item['cognitive_level']}")
        st.markdown(f"- **Difficulty (b):** `{item['b']:.2f}`")
        st.markdown(f"- **Discrimination (a):** `{item['a']:.2f}`")
        st.markdown(f"- **Guessing (c):** `{item['c']:.2f}`")
        
        # Show current constraint status chart
        if cat.log:
            constraint_status = cat._get_constraint_status()
            st.plotly_chart(create_constraint_chart(constraint_status), use_container_width=True)

    with col3:
        st.info("#### 📈 Test Progress")
        
        # Summary stats
        summary_stats = cat.get_summary_stats()
        if summary_stats:
            st.metric("Questions Answered", summary_stats['total_questions'])
            st.metric("Accuracy", f"{summary_stats['accuracy']:.2%}")
            
            # Topic distribution
            if summary_stats['topic_distribution']:
                st.write("**Topics Covered:**")
                for topic, count in summary_stats['topic_distribution'].items():
                    st.write(f"- {topic}: {count}")

        # Recent decisions log (simplified)
        st.write("**Recent Selections:**")
        if cat.log:
            for idx in range(max(0, len(cat.log)-3), len(cat.log)):
                log_entry = cat.log[idx]
                q_num = log_entry.get('q_num', idx+1)
                correct = log_entry.get('response_correct', 'N/A')
                theta_change = log_entry.get('theta_change', 0)
                
                with st.expander(f"Q{q_num}: {correct} ({theta_change:+.2f})", expanded=False):
                    st.write(f"Topic: {log_entry.get('item_topic', 'N/A')}")
                    st.write(f"Level: {log_entry.get('item_cognitive_level', 'N/A')}")
                    if 'next_selection_reason' in log_entry:
                        st.write(f"Next: {log_entry['next_selection_reason'][:50]}...")

else:
    # Test is finished
    st.success("🎉 You have completed the exam!")
    st.balloons()
    
    final_theta = cat.theta
    final_score = transform_theta_to_score(final_theta)
    summary_stats = cat.get_summary_stats()

    st.header("📊 Final Exam Results")
    
    # Results metrics
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Final Ability (θ)", f"{final_theta:.3f}")
    with col2:
        st.metric("Scaled Score", f"{final_score}/{total_questions_in_test}")
    with col3:
        st.metric("Overall Accuracy", f"{summary_stats['accuracy']:.1%}")
    with col4:
        grade = "Pass" if final_theta > 0.0 else "Needs Improvement"
        st.metric("Outcome", grade)

    # Constraint fulfillment chart
    final_constraint_status = cat._get_constraint_status()
    st.plotly_chart(create_constraint_chart(final_constraint_status), use_container_width=True)

    # Save session data
    saved_filename = cat.save_session_log()
    st.success(f"Session saved as: {saved_filename}")
    
    # Download button for the log
    with open(saved_filename, 'r') as f:
        log_data = f.read()
    
    st.download_button(
        label="📥 Download Complete Test Log",
        data=log_data,
        file_name=saved_filename,
        mime="application/json"
    )

    st.markdown("---")
    st.header("📋 Detailed Test Analysis")
    
    # Expandable detailed log
    for i, entry in enumerate(cat.log):
        q_num = entry.get('q_num', i+1)
        topic = entry.get('item_topic', 'N/A')
        cognitive = entry.get('item_cognitive_level', 'N/A')
        correct = entry.get('response_correct', 'N/A')
        theta_change = entry.get('theta_change', 0)
        
        with st.expander(f"Question {q_num}: {topic} | {cognitive} | {correct} ({theta_change:+.3f})"):
            st.markdown(f"**Question:** {entry.get('item_content', 'N/A')}")
            st.markdown(f"**Your Answer:** {entry.get('user_response', 'N/A')}")
            st.markdown(f"**Correct Answer:** {entry.get('correct_answer', 'N/A')}")
            st.markdown(f"**Item Parameters:** a={entry.get('item_discrimination_a', 'N/A'):.2f}, b={entry.get('item_difficulty_b', 'N/A'):.2f}, c={entry.get('item_guessing_c', 'N/A'):.2f}")
            st.markdown(f"**θ Before:** {entry.get('theta_before', 'N/A'):.3f}")
            st.markdown(f"**θ After:** {entry.get('theta_after', 'N/A'):.3f}")
            
            if 'next_selection_reason' in entry:
                st.info(f"**Next Question Selection:** {entry['next_selection_reason']}")

    # Restart button
    if st.button("🔄 Restart Exam"):
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        st.rerun() 