import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from cat_logic import MIRTCATSimulator
from pathlib import Path
import json
import datetime

st.set_page_config(layout="wide", page_title="MIRT CAT System", page_icon="🧠")

def initialize_mirt_cat():
    base_dir = Path(__file__).resolve().parent.parent  # go up from v3/ to project/
    qbank_path = base_dir / "qbank.csv"
    multidimensional_qbank_path = base_dir / "multidimensional_qbank.csv"

    print("Resolved paths:")
    print(qbank_path, qbank_path.exists())
    print(multidimensional_qbank_path, multidimensional_qbank_path.exists())

    return MIRTCATSimulator(qbank_path, multidimensional_qbank_path)


def save_results(results):
    """Save examinee results to CSV file."""
    results_file = Path('examinee_results.csv')
    
    # Flatten the results for CSV storage
    flat_results = {
        'timestamp': results['timestamp'],
        'total_items': len(results['administered_items']),
        'administered_items': ';'.join(map(str, results['administered_items'])),
        'responses': ';'.join(map(str, results['responses']))
    }
    
    # Add theta estimates for all dimensions
    for i, dim_name in enumerate(results['dimension_names']):
        flat_results[f'theta_{dim_name}'] = results['theta_vector'][i]
        flat_results[f'se_{dim_name}'] = results['theta_se_vector'][i]
    
    # Add content coverage
    for topic, count in results['topic_counts'].items():
        flat_results[f'topic_count_{topic}'] = count
    
    for level, count in results['cognitive_counts'].items():
        flat_results[f'cognitive_count_{level}'] = count
    
    # Create DataFrame and append to file
    df = pd.DataFrame([flat_results])
    
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
    - **6 Topic-Specific Factors** (ANN, CNN, Ensemble Models, Linear Models, MLOps, Statistics)
    - **3 Cognitive Level Factors** (Knowledge, Application, Analysis)
    
    The system uses sophisticated psychometric models to provide detailed diagnostic profiles.
    """)
    st.markdown("---")

    # Initialize or get the session state
    if 'mirt_cat_session' not in st.session_state:
        with st.spinner("Initializing MIRT CAT System..."):
            st.session_state.mirt_cat_session = initialize_mirt_cat()
            next_item, reason = st.session_state.mirt_cat_session.select_next_item()
            st.session_state.current_item = next_item
            st.session_state.mirt_cat_session.log.append({'initial_reason': reason})
            st.session_state.test_finished = False

    # Get current state
    cat = st.session_state.mirt_cat_session
    item = st.session_state.current_item
    total_questions = cat.test_length

    if not st.session_state.test_finished and item is not None:
        # Create three columns for layout
        col1, col2, col3 = st.columns([3, 2, 2])

        with col1:
            # Question display
            current_q_num = len(cat.administered_items) + 1
            st.write(f"#### Question {current_q_num} of {total_questions}")
            st.progress(current_q_num / total_questions)

            st.subheader(item['content'])
            options = [opt.strip() for opt in item['options'].split(';')]

            with st.form(key=f"mirt_q_{item['item_id']}"):
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
                    if item['question_type'] == 'MCQ-Single':
                        user_answer_keys = [user_choice.split(')')[0]] if user_choice and ')' in user_choice else []
                    else:
                        user_answer_keys = [choice.split(')')[0] for choice in user_choice if ')' in choice]

                    cat.administer_item(item['item_id'], user_answer_keys)
                    
                    next_item, reason = cat.select_next_item()
                    
                    if cat.log:
                        cat.log[-1]['scs_decision_for_next'] = reason
                        
                    st.session_state.current_item = next_item
                    
                    if next_item is None or current_q_num >= total_questions:
                        st.session_state.test_finished = True
                    
                    st.rerun()

        with col2:
            # Real-time ability estimates
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
            
            # Content coverage progress
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
            # Item information and test log
            st.info("#### 🔍 Current Item Info")
            st.markdown(f"**Topic:** {item['topic']}")
            st.markdown(f"**Cognitive Level:** {item['cognitive_level']}")
            st.markdown(f"**Difficulty (b):** {item['b']:.2f}")
            st.markdown(f"**Discrimination (a):** {item['a']:.2f}")
            
            st.markdown("---")
            st.write("#### 📝 Recent Activity")
            
            # Show last few responses
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
        
        # Get diagnostic report
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
        
        # Detailed diagnostic interpretation
        st.header("🔍 Diagnostic Interpretation")
        
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
        
        # Test statistics
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
        
        # Detailed log
        with st.expander("📝 Detailed Test Log"):
            for entry in cat.log:
                if 'q_num' in entry:
                    st.write(f"**Question {entry['q_num']}:** {entry['item_content'][:80]}...")
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.write(f"Topic: {entry['item_topic']}")
                        st.write(f"Cognitive Level: {entry['item_cognitive_level']}")
                    with col2:
                        correct_color = "green" if entry['response_correct'] == 'Yes' else "red"
                        st.markdown(f"Response: <span style='color:{correct_color}'>{entry['response_correct']}</span>", 
                                  unsafe_allow_html=True)
                    with col3:
                        theta_change = entry['theta_change'][0]  # General factor change
                        st.write(f"General θ Change: {theta_change:+.3f}")
                    st.write("---")
        
        # Restart option
        if st.button("🔄 Take Another Test"):
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
        - Test Length: 15 items
        - Minimum per topic: 2 items
        - Topics: ANN, CNN, Ensemble Models, Linear Models, MLOps, Statistics
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
        qbank = pd.read_csv('qbank.csv')
        multidimensional_qbank = pd.read_csv('multidimensional_qbank.csv')
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("Item Bank Statistics")
            st.metric("Total Items", len(qbank))
            st.metric("Topics Covered", qbank['topic'].nunique())
            st.metric("Cognitive Levels", qbank['cognitive_level'].nunique())
            
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
            fig_topics = px.pie(qbank['topic'].value_counts().reset_index(), 
                              values='count', names='topic', 
                              title="Items by Topic")
            st.plotly_chart(fig_topics, use_container_width=True)
        
    except FileNotFoundError:
        st.warning("Item bank files not found. Please ensure qbank.csv and multidimensional_qbank.csv are available.")
    
    st.header("🔧 Technical Requirements")
    
    with st.expander("Dependencies"):
        st.markdown("""
        **Python Libraries:**
        - streamlit >= 1.28.0
        - pandas >= 1.5.0
        - numpy >= 1.24.0
        - scipy >= 1.10.0
        - plotly >= 5.15.0
        
        **Data Files Required:**
        - `qbank.csv` (original question bank)
        - `multidimensional_qbank.csv` (Q-matrix)
        
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