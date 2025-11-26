import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from cat_logic import MIRTCATSimulator
from conventional_test import ConventionalTestSimulator
from pathlib import Path
import json
import datetime

st.set_page_config(layout="wide", page_title="MIRT CAT System", page_icon="🧠")

def initialize_mirt_cat(model_type='3PL'):
    """Initialize the MIRT CAT system with database connection.
    
    Args:
        model_type: '2PL', '3PL', or 'Conventional' to select the test type
    """
    try:
        if model_type == 'Conventional':
            return ConventionalTestSimulator()
        else:
            return MIRTCATSimulator(model_type=model_type)
    except Exception as e:
        st.error(f"Failed to initialize test system: {e}")
        st.error("Please check your database configuration and ensure:")
        st.error("1. PostgreSQL is running")
        st.error("2. .env file exists with correct DB_PASSWORD")
        st.error("3. Database 'adaptive_exam_db' exists")
        st.error("4. User has proper permissions")
        st.stop()


def save_results(results):
    """Save examinee results to CSV file."""
    results_file = Path('examinee_results.csv')
    
    rows = []
    timestamp = results['timestamp']
    model_type = results.get('model_type')
    detailed_log = results.get('detailed_log')
    
    if detailed_log:
        # Write one row per administered item
        for entry in detailed_log:
            if 'q_num' not in entry:
                continue
            row = {
                'timestamp': timestamp,
                'model_type': model_type,
                'q_num': entry.get('q_num'),
                'item_id': entry.get('item_id'),
                'topic': entry.get('item_topic'),
                'cognitive_level': entry.get('item_cognitive_level'),
                'a': entry.get('item_discrimination_a'),
                'b': entry.get('item_difficulty_b'),
                'c': entry.get('item_guessing_c'),
                'response_correct': entry.get('response_correct'),
            }
            # Include theta metrics when available (IRT only)
            if 'theta_before' in entry and 'theta_after' in entry and 'theta_change' in entry:
                try:
                    row['theta_before_general'] = float(entry['theta_before'][0])
                    row['theta_after_general'] = float(entry['theta_after'][0])
                    row['theta_change_general'] = float(entry['theta_change'][0])
                except Exception:
                    pass
            rows.append(row)
    else:
        # Fallback: single summary row
        row = {
            'timestamp': timestamp,
            'model_type': model_type,
            'total_items': len(results.get('administered_items', [])),
            'administered_items': ';'.join(map(str, results.get('administered_items', []))),
            'responses': ';'.join(map(str, results.get('responses', []))),
        }
        if 'score_percent' in results:
            row['score_percent'] = results['score_percent']
        rows.append(row)
    
    df = pd.DataFrame(rows)
    
    if results_file.exists():
        existing_df = pd.read_csv(results_file)
        df = pd.concat([existing_df, df], ignore_index=True)
    
    df.to_csv(results_file, index=False)
    return results_file

def create_radar_chart(diagnostic_profile):
    """Create a radar chart for ability profiles."""
    # Prepare data for radar chart
    categories = []
    values = []
    
    # Add general ability
    categories.append('General')
    values.append(diagnostic_profile['General Ability']['score'])
    
    # Add topic abilities
    for topic, data in diagnostic_profile['Topic Abilities'].items():
        categories.append(topic.replace(' ', '<br>'))
        values.append(data['score'])
    
    # Add cognitive abilities
    for level, data in diagnostic_profile['Cognitive Abilities'].items():
        categories.append(f"{level}<br>Level")
        values.append(data['score'])
    
    # Create radar chart
    fig = go.Figure()
    
    fig.add_trace(go.Scatterpolar(
        r=values,
        theta=categories,
        fill='toself',
        name='Ability Profile',
        line_color='rgb(50, 50, 200)',
        fillcolor='rgba(50, 50, 200, 0.1)'
    ))
    
    fig.update_layout(
        polar=dict(
            radialaxis=dict(
                visible=True,
                range=[-3, 3],
                tickvals=[-2, -1, 0, 1, 2],
                ticktext=['Well Below', 'Below', 'Average', 'Above', 'Well Above']
            )
        ),
        showlegend=False,
        title="Multidimensional Ability Profile",
        title_x=0.5
    )
    
    return fig

def create_dimension_bars(diagnostic_profile):
    """Create bar chart for dimension scores."""
    dimensions = []
    scores = []
    colors = []
    
    # General ability
    dimensions.append('General')
    scores.append(diagnostic_profile['General Ability']['score'])
    colors.append('blue')
    
    # Topic abilities
    for topic, data in diagnostic_profile['Topic Abilities'].items():
        dimensions.append(topic)
        scores.append(data['score'])
        colors.append('green' if data['score'] > 0 else 'red')
    
    # Cognitive abilities
    for level, data in diagnostic_profile['Cognitive Abilities'].items():
        dimensions.append(f"{level} Level")
        scores.append(data['score'])
        colors.append('purple' if data['score'] > 0 else 'orange')
    
    fig = px.bar(
        x=dimensions,
        y=scores,
        title="Ability Scores by Dimension",
        labels={'x': 'Dimension', 'y': 'Ability Score (θ)'},
        color=scores,
        color_continuous_scale='RdYlBu'
    )
    
    fig.add_hline(y=0, line_dash="dash", line_color="black", 
                  annotation_text="Average", annotation_position="bottom right")
    
    fig.update_layout(showlegend=False, xaxis_tickangle=-45)
    
    return fig

def create_content_coverage_chart(topic_counts, cognitive_counts):
    """Create chart showing content coverage."""
    fig = make_subplots(
        rows=1, cols=2,
        subplot_titles=('Topic Coverage', 'Cognitive Level Coverage'),
        specs=[[{"type": "bar"}, {"type": "bar"}]]
    )
    
    # Topic coverage
    fig.add_trace(
        go.Bar(x=list(topic_counts.keys()), y=list(topic_counts.values()), 
               name="Topics", marker_color='lightblue'),
        row=1, col=1
    )
    
    # Cognitive level coverage
    fig.add_trace(
        go.Bar(x=list(cognitive_counts.keys()), y=list(cognitive_counts.values()), 
               name="Levels", marker_color='lightcoral'),
        row=1, col=2
    )
    
    fig.add_hline(y=2, line_dash="dash", line_color="red", row=1, col=1,
                  annotation_text="Minimum", annotation_position="top right")
    
    fig.update_layout(showlegend=False, title_text="Content Balance During Test")
    fig.update_xaxes(tickangle=-45)
    
    return fig

# --- Sidebar for Navigation ---
st.sidebar.title("🧠 MIRT CAT System")
page = st.sidebar.selectbox("Navigate", 
                           ["Take Test", "Admin Dashboard", "System Info"])

if page == "Take Test":
    # --- Main Test Interface ---
    st.title("🧠 Multidimensional AI Fellowship Adaptive Test")
    st.markdown("""
    This is an advanced **Multidimensional Computerized Adaptive Test (MIRT CAT)** that measures your ability across:
    - **1 General AI/ML Factor** (overall competency)
    - **Topic-Specific Factors** (dynamically loaded from database)
    - **Cognitive Level Factors** (Knowledge, Application, Analysis)
    
    The system uses sophisticated psychometric models to provide detailed diagnostic profiles.
    **Test Length:** 20 questions with balanced topic coverage.
    """)
    st.markdown("---")
    
    # Model selection dropdown (show before initialization to allow choice)
    model_type = st.selectbox(
        "Select Test Model:",
        options=['Conventional', '2PL', '3PL'],
        index=2,  # Default to 3PL
        key='model_selection',
        help="Conventional: Random selection. 2PL: 2-Parameter Logistic. 3PL: 3-Parameter Logistic"
    )
    
    # Initialize or get the session state
    if 'mirt_cat_session' not in st.session_state or st.session_state.get('model_type') != model_type:
        try:
            with st.spinner("Initializing MIRT CAT System..."):
                st.session_state.model_type = model_type
                st.session_state.mirt_cat_session = initialize_mirt_cat(model_type=model_type)
                next_item, reason = st.session_state.mirt_cat_session.select_next_item()
                if next_item is None:
                    st.error("Failed to select next item. Please try refreshing.")
                    st.stop()
                st.session_state.current_item = next_item
                st.session_state.mirt_cat_session.log.append({'initial_reason': reason})
                st.session_state.test_finished = False
        except Exception as e:
            st.error(f"Initialization failed: {str(e)}")
            import traceback
            st.code(traceback.format_exc())
            st.stop()

    # Get current state
    cat = st.session_state.mirt_cat_session if 'mirt_cat_session' in st.session_state else None
    item = st.session_state.current_item if 'current_item' in st.session_state else None
    total_questions = cat.test_length if cat else 20

    if not st.session_state.test_finished and item is not None:
        # Create three columns for layout
        col1, col2, col3 = st.columns([3, 2, 2])

        with col1:
            # Question display
            current_q_num = len(cat.administered_items) + 1
            st.write(f"#### Question {current_q_num} of {total_questions}")
            st.progress(current_q_num / total_questions)

            # Display question text
            st.subheader(item['content'])
            
            # Display question image if available
            if item.get('img_url'):
                try:
                    st.image(item['img_url'], use_container_width=True, caption="Question Diagram")
                except Exception as e:
                    st.warning(f"Could not load image: {e}")
            
            # Handle options - parse options_metadata (now just a list of labels)
            import json
            
            options = []
            options_metadata = item.get('options_metadata', '')
            
            if options_metadata:
                try:
                    # options_metadata is now just a JSON array of label strings
                    options = json.loads(options_metadata) if isinstance(options_metadata, str) else options_metadata
                except (json.JSONDecodeError, TypeError) as e:
                    print(f"Error parsing options_metadata: {e}")
                    options = []
            
            # Fallback: generate generic options if none found
            if not options:
                n_choices = item.get('n_choices', 4)
                options = [f"{chr(65+i)}" for i in range(n_choices)]
            
            # Helper function to render option (can be text or image)
            def render_option(opt):
                """Check if option is an image URL and render accordingly"""
                if isinstance(opt, str):
                    # Check if it's an image URL
                    if opt.startswith('http') and any(opt.lower().endswith(ext) for ext in ['.jpg', '.jpeg', '.png', '.gif', '.webp', '.svg']):
                        return opt  # Return URL for image
                return opt
            
            # Create option display items
            option_displays = []
            for i, opt in enumerate(options):
                display_label = f"{chr(65+i)}. {opt}" if not opt.startswith('http') else f"{chr(65+i)}. [Image]"
                option_displays.append((display_label, opt))

            with st.form(key=f"mirt_q_{item['item_id']}"):
                if item['question_type'] == 'single' or item.get('n_choices', 4) == 1:
                    # Single choice - display as radio buttons
                    option_values = []
                    for i, opt in enumerate(options):
                        option_values.append(opt)
                        # If option is an image URL, display it
                        if opt.startswith('http') and any(opt.lower().endswith(ext) for ext in ['.jpg', '.jpeg', '.png', '.gif', '.webp', '.svg']):
                            try:
                                st.image(opt, width=200, caption=f"Option {chr(65+i)}")
                            except Exception:
                                st.write(f"Option {chr(65+i)}: [Image]")
                        else:
                            st.write(f"{chr(65+i)}. {opt}")
                    
                    user_choice = st.radio(
                        "Select your answer:",
                        options=option_values,
                        key=f"q_{item['item_id']}_radio",
                        format_func=lambda x: f"Option {chr(65+option_values.index(x))}"
                    )
                else:
                    user_choice = st.multiselect(
                        "Select all correct answers:",
                        options=options,
                        key=f"q_{item['item_id']}_multi"
                    )
                
                submitted = st.form_submit_button("Submit Answer", type="primary")

                if submitted:
                    # Convert user choice to index (0-based)
                    if item['question_type'] == 'single':
                        # Find the index of the selected option
                        user_answer_index = options.index(user_choice)
                        user_answer_keys = [user_answer_index]
                    else:
                        # Multiple choice - get indices
                        user_answer_keys = [options.index(choice) for choice in user_choice if choice in options]

                    cat.administer_item(item['item_id'], user_answer_keys)
                    
                    next_item, reason = cat.select_next_item()
                    
                    if cat.log:
                        cat.log[-1]['scs_decision_for_next'] = reason
                        
                    st.session_state.current_item = next_item
                    
                    if next_item is None or current_q_num >= total_questions:
                        st.session_state.test_finished = True
                    
                    st.rerun()

        with col2:
            if st.session_state.get('model_type') == 'Conventional':
                # Conventional: show only overall score (percentage correct)
                total_answered = len(cat.administered_items)
                correct = sum(cat.responses) if total_answered > 0 else 0
                accuracy = (correct / total_answered * 100.0) if total_answered > 0 else 0.0
                st.info("#### 🧮 Overall Score")
                st.metric("Score", f"{accuracy:.1f}%")
            else:
                # Real-time ability estimates for IRT models
                st.info("#### 🎯 Current Ability Estimates")
                
                # General ability (most important)
                general_theta = cat.theta_vector[0]
                st.metric("General AI/ML Ability", f"{general_theta:.3f}")
                
                # Show top 3 topic strengths/weaknesses
                topic_thetas = cat.theta_vector[1:7]
                topic_names = cat.topic_dimensions
                topic_data = list(zip(topic_names, topic_thetas))
                topic_data.sort(key=lambda x: x[1], reverse=True)
                
                st.write("**Top Topic Strengths:**")
                for i, (topic, theta) in enumerate(topic_data[:3]):
                    st.write(f"{i+1}. {topic}: {theta:.2f}")
            
            # Content coverage (hide entirely for Conventional)
            if st.session_state.get('model_type') != 'Conventional':
                st.markdown("---")
                st.write("#### 📊 Content Balance")
                
                # Topic coverage
                st.write("**Topic Coverage:**")
                for topic, count in cat.topic_counts.items():
                    color = "🟢" if count >= cat.min_items_per_topic else "🔴"
                    st.write(f"{color} {topic}: {count}/{cat.min_items_per_topic}")
                
                # Cognitive level coverage
                st.write("**Cognitive Levels:**")
                for level, count in cat.cognitive_counts.items():
                    st.write(f"• {level}: {count}")

        with col3:
            if st.session_state.get('model_type') != 'Conventional':
                # Item information and recent activity (IRT models only)
                st.info("#### 🔍 Current Item Info")
                st.markdown(f"**Model:** {st.session_state.get('model_type', '3PL')}")
                st.markdown(f"**Topic:** {item['topic']}")
                st.markdown(f"**Cognitive Level:** {item['cognitive_level']}")
                
                if st.session_state.get('model_type') == '2PL':
                    b_2pl = item.get('b_2pl') or item.get('b', 0)
                    a_2pl = item.get('a_2pl') or item.get('a', 0)
                    st.markdown(f"**Difficulty (b):** {b_2pl:.2f}")
                    st.markdown(f"**Discrimination (a):** {a_2pl:.2f}")
                else:
                    st.markdown(f"**Difficulty (b):** {item.get('b', 0):.2f}")
                    st.markdown(f"**Discrimination (a):** {item.get('a', 0):.2f}")
                    st.markdown(f"**Guessing (c):** {item.get('c', 0):.2f}")
                
                st.markdown("---")
                st.write("#### 📝 Recent Activity")
                
                if cat.log:
                    recent_logs = cat.log[-3:] if len(cat.log) >= 3 else cat.log
                    for log_entry in reversed(recent_logs):
                        if 'q_num' in log_entry:
                            correct_emoji = "✅" if log_entry['response_correct'] == 'Yes' else "❌"
                            st.write(f"Q{log_entry['q_num']}: {correct_emoji} {log_entry['item_topic']}")

    else:
        # Test completion page
        st.success("🎉 Test Completed!")
        st.balloons()

        if st.session_state.get('model_type') == 'Conventional':
            # Conventional completion: show only overall score (percentage correct)
            total_answered = len(cat.administered_items)
            correct = sum(cat.responses) if total_answered > 0 else 0
            accuracy = (correct / total_answered * 100.0) if total_answered > 0 else 0.0
            st.header("🧮 Overall Score")
            st.metric("Score", f"{accuracy:.1f}%")
            # Save results
            if hasattr(cat, 'export_results'):
                results = cat.export_results()
                save_results(results)

        else:
            # IRT completion: diagnostics and export
            diagnostic_report = cat.get_diagnostic_report()

            # Save results
            results = cat.export_results()
            results_file = save_results(results)

            st.header("📊 Your Multidimensional Ability Profile")

            # Create visualizations
            col1, col2 = st.columns(2)

            with col1:
                radar_fig = create_radar_chart(diagnostic_report['diagnostic_profile'])
                st.plotly_chart(radar_fig, use_container_width=True)

            with col2:
                bars_fig = create_dimension_bars(diagnostic_report['diagnostic_profile'])
                st.plotly_chart(bars_fig, use_container_width=True)

            # Content coverage chart
            coverage_fig = create_content_coverage_chart(
                diagnostic_report['content_coverage']['topics'],
                diagnostic_report['content_coverage']['cognitive_levels']
            )
            st.plotly_chart(coverage_fig, use_container_width=True)
        
        # Detailed results
        st.header("📋 Detailed Results")
        
        if st.session_state.get('model_type') == 'Conventional':
            # Conventional completion: show only overall score
            total_answered = len(cat.administered_items)
            correct = sum(cat.responses) if total_answered > 0 else 0
            accuracy = (correct / total_answered * 100.0) if total_answered > 0 else 0.0
            st.header("🧮 Overall Score")
            st.metric("Score", f"{accuracy:.1f}%")
        else:
            # IRT model results
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.subheader("🌟 General Ability")
                general_score = diagnostic_report['theta_estimates']['General']
                general_se = diagnostic_report['standard_errors']['General']
                st.metric("General AI/ML Ability", 
                         f"{general_score:.3f}", 
                         help=f"Standard Error: ±{general_se:.3f}")
                st.write(f"**Interpretation:** {diagnostic_report['diagnostic_profile']['General Ability']['interpretation']}")
            
            with col2:
                st.subheader("📚 Topic Strengths")
                topic_profile = diagnostic_report['diagnostic_profile']['Topic Abilities']
                topic_scores = [(topic, data['score']) for topic, data in topic_profile.items()]
                topic_scores.sort(key=lambda x: x[1], reverse=True)
                
                for topic, score in topic_scores[:3]:
                    interpretation = topic_profile[topic]['interpretation']
                    st.write(f"**{topic}:** {score:.3f} ({interpretation})")
            
            with col3:
                st.subheader("🧠 Cognitive Profile")
                cognitive_profile = diagnostic_report['diagnostic_profile']['Cognitive Abilities']
                for level, data in cognitive_profile.items():
                    st.write(f"**{level}:** {data['score']:.3f} ({data['interpretation']})")
        
        # Detailed diagnostic interpretation (IRT models only)
        if st.session_state.get('model_type') != 'Conventional':
            st.header("🔍 Diagnostic Interpretation")
            
            # IRT model interpretation
            with st.expander("📈 Strengths and Development Areas", expanded=True):
                general_theta = diagnostic_report['theta_estimates']['General']
                
                # Strengths
                strengths = []
                development_areas = []
                
                for topic, data in topic_profile.items():
                    relative_score = data['relative_to_general']
                    if relative_score > 0.5:
                        strengths.append(f"**{topic}** (θ = {data['score']:.2f}, +{relative_score:.2f} above general)")
                    elif relative_score < -0.5:
                        development_areas.append(f"**{topic}** (θ = {data['score']:.2f}, {relative_score:.2f} below general)")
                
                if strengths:
                    st.write("**🌟 Relative Strengths:**")
                    for strength in strengths:
                        st.write(f"• {strength}")
                
                if development_areas:
                    st.write("\n**📈 Development Opportunities:**")
                    for area in development_areas:
                        st.write(f"• {area}")
                
                if not strengths and not development_areas:
                    st.write("Your abilities are well-balanced across all topic areas relative to your general ability level.")
        
        # Test statistics and detailed log (IRT models only)
        if st.session_state.get('model_type') != 'Conventional':
            st.header("📊 Test Statistics")
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric("Total Items", len(cat.administered_items))
            with col2:
                correct_responses = sum(cat.responses)
                st.metric("Correct Answers", f"{correct_responses}/{len(cat.responses)}")
            with col3:
                accuracy = correct_responses / len(cat.responses) if cat.responses else 0
                st.metric("Accuracy", f"{accuracy:.1%}")
            with col4:
                avg_se = np.mean(list(diagnostic_report['standard_errors'].values()))
                st.metric("Avg. Standard Error", f"{avg_se:.3f}")
            
            with st.expander("📝 Detailed Test Log"):
                for entry in cat.log:
                    if 'q_num' in entry:
                        st.write(f"**Question {entry['q_num']}:** {entry['item_content'][:80]}...")
                        col1, col2, col3 = st.columns(3)
                        with col1:
                            st.write(f"Topic: {entry['item_topic']}")
                            st.write(f"Cognitive Level: {entry['item_cognitive_level']}")
                            # Item parameters
                            a_val = entry.get('item_discrimination_a')
                            b_val = entry.get('item_difficulty_b')
                            c_val = entry.get('item_guessing_c')
                            st.write(f"a: {a_val if a_val is not None else '-'}")
                            st.write(f"b: {b_val if b_val is not None else '-'}")
                            st.write(f"c: {c_val if c_val is not None else '-'}")
                        with col2:
                            correct_color = "green" if entry['response_correct'] == 'Yes' else "red"
                            st.markdown(f"Response: <span style='color:{correct_color}'>{entry['response_correct']}</span>", 
                                      unsafe_allow_html=True)
                        with col3:
                            theta_change = entry['theta_change'][0]  # General factor change
                            st.write(f"General θ Change: {theta_change:+.3f}")
                        # Debug answers
                        ca = entry.get('correct_answer_indices')
                        ua = entry.get('user_answer_indices')
                        if ca is not None and ua is not None:
                            st.write(f"Correct idx: {ca} | Your idx: {ua}")
                        st.write("---")
        
        # Restart option
        if st.button("🔄 Take Another Test"):
            # Close database connection before restarting
            if 'mirt_cat_session' in st.session_state:
                st.session_state.mirt_cat_session.close_database_connection()
            
            for key in list(st.session_state.keys()):
                if key.startswith('mirt_cat'):
                    del st.session_state[key]
            if 'test_finished' in st.session_state:
                del st.session_state['test_finished']
            if 'current_item' in st.session_state:
                del st.session_state['current_item']
            st.rerun()

elif page == "Admin Dashboard":
    st.title("👨‍💼 Admin Dashboard")
    st.markdown("View and analyze results from all examinees.")
    
    results_file = Path('examinee_results.csv')
    
    if results_file.exists():
        df = pd.read_csv(results_file)
        
        st.header("📈 Cohort Analytics")
        
        # Summary statistics
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Total Examinees", len(df))
        with col2:
            avg_general = df['theta_General'].mean()
            st.metric("Avg General Ability", f"{avg_general:.3f}")
        with col3:
            std_general = df['theta_General'].std()
            st.metric("Standard Deviation", f"{std_general:.3f}")
        with col4:
            avg_items = df['total_items'].mean()
            st.metric("Avg Items Administered", f"{avg_items:.1f}")
        
        # Distribution plots
        st.header("📊 Ability Distributions")
        
        # General ability distribution
        fig_general = px.histogram(df, x='theta_General', 
                                 title="General Ability Distribution",
                                 labels={'theta_General': 'General Ability (θ)', 'count': 'Frequency'},
                                 nbins=20)
        fig_general.add_vline(x=0, line_dash="dash", line_color="red", 
                            annotation_text="Average", annotation_position="top right")
        st.plotly_chart(fig_general, use_container_width=True)
        
        # Topic abilities comparison
        topic_columns = [col for col in df.columns if col.startswith('theta_') and col != 'theta_General']
        topic_data = df[topic_columns].melt(var_name='Dimension', value_name='Ability')
        topic_data['Dimension'] = topic_data['Dimension'].str.replace('theta_', '')
        
        fig_topics = px.box(topic_data, x='Dimension', y='Ability',
                          title="Topic Ability Distributions")
        fig_topics.update_xaxes(tickangle=-45)
        st.plotly_chart(fig_topics, use_container_width=True)
        
        # Data table
        st.header("📋 Detailed Results")
        
        # Select columns to display
        display_cols = st.multiselect(
            "Select columns to display:",
            df.columns.tolist(),
            default=['timestamp', 'total_items', 'theta_General'] + 
                   [col for col in df.columns if col.startswith('theta_')][:6]
        )
        
        if display_cols:
            st.dataframe(df[display_cols], use_container_width=True)
        
        # Download option
        csv = df.to_csv(index=False)
        st.download_button(
            label="📥 Download Full Dataset",
            data=csv,
            file_name=f"mirt_cat_results_{datetime.date.today()}.csv",
            mime="text/csv"
        )
        
    else:
        st.info("No results available yet. Complete some tests to see data here.")
        
        # Option to create sample data for demonstration
        if st.button("Create Sample Data"):
            sample_data = []
            np.random.seed(42)
            
            for i in range(20):
                # Generate sample results
                general_ability = np.random.normal(0, 1)
                
                sample = {
                    'timestamp': pd.Timestamp.now() - pd.Timedelta(days=np.random.randint(0, 30)),
                    'total_items': 15,
                    'administered_items': ';'.join(map(str, np.random.choice(range(1, 51), 15, replace=False))),
                    'responses': ';'.join(map(str, np.random.binomial(1, 0.6, 15))),
                    'theta_General': general_ability
                }
                
                # Add topic abilities
                topics = ['ANN', 'CNN', 'Ensemble Models', 'Linear Models', 'MLOps', 'Statistics']
                for topic in topics:
                    sample[f'theta_{topic}'] = general_ability + np.random.normal(0, 0.5)
                    sample[f'se_{topic}'] = np.random.uniform(0.3, 0.8)
                
                # Add cognitive abilities
                cognitive_levels = ['Knowledge', 'Application', 'Analysis']
                for level in cognitive_levels:
                    sample[f'theta_{level}'] = general_ability + np.random.normal(0, 0.3)
                    sample[f'se_{level}'] = np.random.uniform(0.4, 0.7)
                
                # Add content coverage
                for topic in topics:
                    sample[f'topic_count_{topic}'] = np.random.randint(1, 4)
                
                for level in cognitive_levels:
                    sample[f'cognitive_count_{level}'] = np.random.randint(2, 8)
                
                sample_data.append(sample)
            
            sample_df = pd.DataFrame(sample_data)
            sample_df.to_csv(results_file, index=False)
            st.success(f"Created {len(sample_data)} sample examinee records!")
            st.rerun()

elif page == "System Info":
    st.title("ℹ️ MIRT CAT System Information")
    
    st.header("🧮 Model Specifications")
    
    with st.expander("Multidimensional IRT Model", expanded=True):
        st.markdown("""
        **Model Type:** Compensatory Multidimensional 3-Parameter Logistic (M3PL)
        
        **Mathematical Formulation:**
        ```
        P(θ) = c + (1-c) / (1 + exp(-1.7 * Σ(a_j * θ_j) + 1.7*b))
        ```
        
        Where:
        - θ = [θ_General, θ_ANN, θ_CNN, θ_Ensemble, θ_Linear, θ_MLOps, θ_Stats, θ_Knowledge, θ_Application, θ_Analysis]
        - a_j = discrimination parameter for dimension j
        - b = difficulty parameter
        - c = guessing parameter
        """)
    
    with st.expander("Dimension Structure"):
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("""
            **Primary Factors:**
            - General (all items load here)
            
            **Topic-Specific Factors:**
            - Artificial Neural Networks (ANN)
            - Convolutional Neural Networks (CNN)  
            - Ensemble Models
            - Linear Models
            - MLOps
            - Statistics
            """)
        
        with col2:
            st.markdown("""
            **Cognitive Level Factors:**
            - Knowledge (recall, recognition)
            - Application (using concepts)
            - Analysis (evaluation, synthesis)
            
            **Total Dimensions:** 10
            - 1 General + 6 Topics + 3 Cognitive = 10
            """)
    
    with st.expander("Item Selection Algorithm"):
        st.markdown("""
        **Shadow Test Approach:**
        1. Calculate multidimensional Fisher Information for all remaining items
        2. Apply content constraints:
           - Minimum 2 items per topic area
           - Balanced cognitive level coverage
        3. Select item with maximum information from feasible set
        4. For first item: random selection from top 5 most informative
        
        **Content Constraints:**
        - Test Length: 20 items
        - Minimum per topic: 2 items
        - Topics: Dynamically loaded from database
        - Cognitive Levels: Knowledge, Application, Analysis
        """)
    
    with st.expander("Ability Estimation"):
        st.markdown("""
        **Method:** Expected A Posteriori (EAP) with Monte Carlo Integration
        
        **Prior:** Multivariate Normal(μ=0, Σ=2I)
        
        **Update Process:**
        1. Generate samples from prior distribution
        2. Calculate likelihood for each sample given responses
        3. Compute posterior weights
        4. EAP estimate = weighted average of samples
        5. Standard error = weighted standard deviation
        
        **Integration:** 1000 Monte Carlo samples per update
        """)
    
    st.header("📊 Psychometric Properties")
    
    # Load and display item bank statistics if available
    try:
        # Try to connect to database and get statistics
        from cat_logic import MIRTCATSimulator
        cat_sim = MIRTCATSimulator()
        qbank = cat_sim.full_qbank
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("Item Bank Statistics")
            st.metric("Total Items", len(qbank))
            st.metric("Topics Covered", qbank['topic_dimension'].nunique())
            st.metric("Cognitive Levels", qbank['cognitive_dimension'].nunique())
            
            # Difficulty distribution
            fig_difficulty = px.histogram(qbank, x='b', title="Item Difficulty Distribution",
                                        labels={'b': 'Difficulty (b parameter)', 'count': 'Frequency'})
            st.plotly_chart(fig_difficulty, use_container_width=True)
        
        with col2:
            st.subheader("Item Parameters")
            st.write("**Discrimination (a):**")
            st.write(f"Mean: {qbank['a'].mean():.3f}")
            st.write(f"Range: {qbank['a'].min():.3f} - {qbank['a'].max():.3f}")
            
            st.write("**Difficulty (b):**")
            st.write(f"Mean: {qbank['b'].mean():.3f}")
            st.write(f"Range: {qbank['b'].min():.3f} - {qbank['b'].max():.3f}")
            
            st.write("**Guessing (c):**")
            st.write(f"Mean: {qbank['c'].mean():.3f}")
            st.write(f"Range: {qbank['c'].min():.3f} - {qbank['c'].max():.3f}")
            
            # Topic distribution
            fig_topics = px.pie(qbank['topic_dimension'].value_counts().reset_index(), 
                              values='count', names='topic_dimension', 
                              title="Items by Topic")
            st.plotly_chart(fig_topics, use_container_width=True)
        
    except Exception as e:
        st.warning(f"Database connection failed: {e}. Please ensure the database is properly configured.")
    
    st.header("🔧 Technical Requirements")
    
    with st.expander("Dependencies"):
        st.markdown("""
        **Python Libraries:**
        - streamlit >= 1.28.0
        - pandas >= 1.5.0
        - numpy >= 1.24.0
        - scipy >= 1.10.0
        - plotly >= 5.15.0
        
        **Database Required:**
        - PostgreSQL database with questions table
        - IRT parameters (a, b, c) must be populated
        - topic_dimension and cognitive_dimension columns
        
        **Output Files Generated:**
        - `examinee_results.csv` (all test results)
        """)
    
    with st.expander("Performance Considerations"):
        st.markdown("""
        **Computational Complexity:**
        - EAP estimation: O(n_samples × n_items × n_dimensions)
        - Fisher Information: O(n_items × n_dimensions²)
        - Content constraints: O(n_items × n_constraints)
        
        **Memory Usage:**
        - Theta vector: 10 dimensions per examinee
        - Item bank: ~50 items × 13 parameters
        - Results storage: expandable CSV format
        
        **Scalability:**
        - Concurrent users: Limited by Streamlit session management
        - Item bank size: Linear scaling up to ~1000 items
        - Result storage: CSV suitable for <10k examinees
        """)
    
    st.header("📚 References & Resources")
    
    st.markdown("""
    **Key References:**
    - Reckase, M. D. (2009). *Multidimensional Item Response Theory*. Springer.
    - van der Linden, W. J. (2005). *Linear Models for Optimal Test Design*. Springer.
    - Chalmers, R. P. (2012). mirt: A Multidimensional Item Response Theory Package for the R Environment.
    
    **Psychometric Standards:**
    - AERA/APA/NCME Standards for Educational and Psychological Testing (2014)
    - ITC Guidelines for Computer-Based and Internet-Delivered Testing (2019)
    """)

# Footer
st.sidebar.markdown("---")
st.sidebar.markdown("**MIRT CAT System v2.0**")
st.sidebar.markdown("Advanced Psychometric Assessment Platform")
st.sidebar.markdown("Built with Streamlit & Python")