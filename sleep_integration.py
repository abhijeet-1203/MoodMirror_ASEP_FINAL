# sleep_integration.py
import streamlit as st
import pandas as pd
import plotly.express as px
from utils import load_entries


def show_sleep_analysis():
    """Simple and user-friendly sleep vs. mood correlation view"""

    # Step 1: Add sleep data

    st.markdown("_Track how your sleep may be affecting your mood._")

    if "sleep_data" not in st.session_state:
        st.session_state.sleep_data = pd.DataFrame(columns=['Date', 'SleepHours'])

    with st.form("sleep_form"):
        sleep_date = st.date_input("Select Date")
        sleep_hours = st.slider("How many hours did you sleep?", 0.0, 12.0, 7.0, 0.5)
        submitted = st.form_submit_button("Save Sleep Data")
        if submitted:
            new_entry = pd.DataFrame({
                'Date': [sleep_date.strftime('%Y-%m-%d')],
                'SleepHours': [sleep_hours]
            })
            st.session_state.sleep_data = pd.concat([st.session_state.sleep_data, new_entry], ignore_index=True)
            st.success("✅ Sleep data saved!")

    # Step 2: Correlate sleep with mood if both datasets are present
    mood_df = load_entries()
    sleep_df = st.session_state.sleep_data

    if not mood_df.empty and not sleep_df.empty:
        st.markdown("### 📊 Sleep vs. Mood Analysis")
        st.markdown("_We analyze if there's a connection between your sleep and mood._")

        # Merge on date
        combined = pd.merge(mood_df, sleep_df, on="Date", how="inner")

        if not combined.empty:
            # Calculate correlation
            corr = combined['SleepHours'].corr(combined['Score'])

            # Friendly conclusion
            if corr >= 0.5:
                conclusion = "🟢 More sleep seems to be linked to better mood!"
            elif corr <= -0.5:
                conclusion = "🔴 More sleep seems to be linked to lower mood."
            else:
                conclusion = "🟡 No strong link between sleep and mood yet."

            # Show stats
            st.metric("Correlation (Sleep vs. Mood Score)", f"{corr:.2f}")
            st.info(conclusion)

            # Chart
            fig = px.scatter(
                combined,
                x='SleepHours',
                y='Score',
                trendline='ols',
                labels={
                    'SleepHours': 'Hours Slept',
                    'Score': 'Mood Score'
                },
                title="Sleep Duration vs Mood Score"
            )
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.warning("No matching dates between mood and sleep logs. Try logging sleep and mood for the same day.")
    else:
        st.info("Please log both mood and sleep data to see your personal insights.")
