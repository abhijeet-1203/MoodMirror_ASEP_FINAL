import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from wordcloud import WordCloud
from datetime import datetime
from sentiment_analysis import analyze_sentiment_vader, get_keywords
from utils import save_entry, load_entries
import plotly.express as px 
import random  
from utils import export_to_pdf
import streamlit as st
import nltk
import ssl
import os
from pathlib import Path
from nltk_loader import loader  # This will ensure data is available
from auth_system import show_auth
import calendar
import numpy as np
from statsmodels.tsa.arima.model import ARIMA
from sklearn.preprocessing import MinMaxScaler
from sleep_integration import show_sleep_analysis


# Authentication check
if "authenticated" not in st.session_state:
    show_auth()
    st.stop()  # Stop execution if not authenticated

st.set_page_config(page_title="MoodMirror", page_icon="🪞", layout="centered")

# Add logout button to sidebar (anywhere in your sidebar section)
if st.sidebar.button("Logout"):
    del st.session_state["authenticated"]
    del st.session_state["username"]
    st.rerun()

# Display username in sidebar
st.sidebar.markdown(f"**Logged in as:** {st.session_state.get('username', '')}")

# Create a custom NLTK data directory in the app folder
nltk_data_dir = Path(__file__).parent / "nltk_data"
nltk_data_dir.mkdir(exist_ok=True)
nltk.data.path.append(str(nltk_data_dir))

# Bypass SSL verification for NLTK downloads (common in restricted environments)
try:
    _create_unverified_https_context = ssl._create_unverified_context
except AttributeError:
    pass
else:
    ssl._create_default_https_context = _create_unverified_https_context

# Download NLTK data with error handling
try:
    nltk.download('punkt', download_dir=str(nltk_data_dir), quiet=True)
    nltk.download('averaged_perceptron_tagger', download_dir=str(nltk_data_dir), quiet=True)
    nltk.download('brown', download_dir=str(nltk_data_dir), quiet=True)
except Exception as e:
    print(f"NLTK data download warning: {str(e)}")




# Inject manifest and service worker
st.markdown("""
<link rel="manifest" href="/static/manifest.json">
<script>
  if ("serviceWorker" in navigator) {
    navigator.serviceWorker.register("/static/service-worker.js")
  }
</script>
""", unsafe_allow_html=True)


# Add cursor CSS immediately after
st.markdown("""
<style>
    /* Nuclear option - forces pointer cursor on ALL sidebar hover states */
    .stSidebar *:hover {
        cursor: pointer !important;
    }
</style>
""", unsafe_allow_html=True)

st.title("🧠 MoodMirror - AI Mental Health Journal")

st.sidebar.header("Navigation")
page = st.sidebar.selectbox("Choose a page", ["New Entry", "View Emotional Trends", "WordCloud", "Mood Calendar","Advanced Mood Analytics"])


if page == "New Entry":
    st.subheader("Write Your Journal Entry")
    journal_text = st.text_area("Today's Thoughts...", height=300)


    if st.button("Analyze and Save"):
        if journal_text.strip() != "":
            sentiment, score = analyze_sentiment_vader(journal_text)
            keywords = get_keywords(journal_text)
            save_entry(datetime.now().strftime("%Y-%m-%d"), journal_text, sentiment, score, keywords)
            st.success(f"Entry saved! Detected sentiment: **{sentiment}** (Score: {score:.2f})")
        else:
            st.warning("Please write something before saving!")


elif page == "View Emotional Trends":
    st.subheader("Your Emotional Trends Over Time")
    df = load_entries()
    
    if not df.empty:
        # Convert dates and sort
        df['Date'] = pd.to_datetime(df['Date'])
        df = df.sort_values('Date')
        
        # --- [1. LINE CHART] --- (Keep your existing time series plot)
        fig_line = plt.figure(figsize=(10, 5))
        sns.lineplot(x='Date', y='Score', data=df, marker='o')
        plt.ylim(-1, 1)
        plt.axhline(0, color='gray', linestyle='--')
        st.pyplot(fig_line)

         # --- [2. ROLLING AVERAGE LINE CHART] ---
        st.subheader("7-Day Rolling Average of Sentiment")
        
        # Convert 'Date' column to datetime
        df['Date'] = pd.to_datetime(df['Date'], errors='coerce')

        # Drop rows where 'Date' is NaT (invalid or missing)
        df = df.dropna(subset=['Date'])

        # Sort by date to ensure proper rolling behavior
        df = df.sort_values('Date')

        # Calculate 7-day rolling average
        rolling_avg = df.set_index('Date')['Score'].rolling('7D').mean()

        # Plot the rolling average
        st.line_chart(rolling_avg, use_container_width=True)

        
        # --- [3. NEW PIE CHART] ---
        st.subheader("Mood Distribution")
        mood_counts = df['Sentiment'].value_counts()

        
        # Create interactive pie chart
        fig_pie = px.pie(
            mood_counts,
            names=mood_counts.index,
            values=mood_counts.values,
            color=mood_counts.index,
            color_discrete_map={
                'Positive': '#4CAF50',  # Green
                'Neutral': '#FFC107',    # Amber
                'Negative': '#F44336'    # Red
            },
            hole=0.3  # Creates a donut chart
        )
        fig_pie.update_traces(textposition='inside', textinfo='percent+label')
        st.plotly_chart(fig_pie, use_container_width=True)
        
                # --- [MOOD STATS] ---
        st.subheader("Your Mood Statistics")
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Total Entries", len(df))
        col2.metric("Most Common Mood", df['Sentiment'].mode()[0])
        col3.metric("Positivity Ratio", f"{(mood_counts.get('Positive', 0) / len(df) * 100):.1f}%")
        col4.metric("Avg. Sentiment Score", f"{df['Score'].mean():.2f}")

        st.markdown("<div style='margin-top: 40px;'></div>", unsafe_allow_html=True)

elif page == "WordCloud":
    st.subheader("Visualize Your Frequent Thoughts")
    
    df = load_entries()
    
    if not df.empty:
        # Sentiment filter dropdown
        sentiment_filter = st.selectbox(
            "Filter by sentiment",
            ["All"] + list(df['Sentiment'].unique())
        )

        # Filter the dataframe by selected sentiment
        if sentiment_filter != "All":
            filtered_df = df[df['Sentiment'] == sentiment_filter]
        else:
            filtered_df = df

        # Combine and clean entries
        text_entries = filtered_df['Entry'].dropna().astype(str)
        text = " ".join(text_entries)

        if text.strip():  # ✅ Only generate if there's meaningful text
            # Generate and display the WordCloud
            wordcloud = WordCloud(width=800, height=400, background_color='white').generate(text)
            fig, ax = plt.subplots(figsize=(10, 5))
            ax.imshow(wordcloud, interpolation='bilinear')
            ax.axis('off')
            st.pyplot(fig)
        else:
            st.warning("⚠️ No valid text available for the selected sentiment to generate a WordCloud.")

        # Show the keyword frequency table (also filtered)
        st.subheader("Keyword Frequency")
        keyword_entries = filtered_df['Keywords'].dropna().astype(str)
        keywords = " ".join(keyword_entries).split(", ")
        freq = pd.Series(keywords).value_counts()
        if not freq.empty:
            st.dataframe(freq.head(10))
        else:
            st.warning("⚠️ No keywords found for the selected sentiment.")
    else:
        st.info("No entries yet to generate a WordCloud.")


    
elif page == "Mood Calendar":
    st.subheader("📅 Mood Calendar")
    
    # Get current month/year
    now = datetime.now()
    col1, col2 = st.columns(2)
    with col1:
        selected_month = st.selectbox(
    "Select Month", 
    list(calendar.month_name[1:]), 
    index=now.month - 1, 
    key="main_mood_month",
    label_visibility="collapsed"
)

    with col2:
        selected_year = st.selectbox(
    "Select Year", 
    range(now.year - 2, now.year + 3), 
    index=2, 
    key="main_mood_year",
    label_visibility="collapsed"
)

    
    selected_month_num = list(calendar.month_name).index(selected_month)
    
# Load and filter data - MODIFIED TO CALCULATE AVERAGE
    df = load_entries()
    if not df.empty:
        df['Date'] = pd.to_datetime(df['Date'])
        # Group by date and calculate average score
        month_df = df[(df['Date'].dt.month == selected_month_num) & 
                     (df['Date'].dt.year == selected_year)]
        
        # Calculate average sentiment per day
        avg_sentiment = month_df.groupby(month_df['Date'].dt.day)['Score'].mean()
        # Convert average score back to sentiment category
        def score_to_sentiment(score):
            if score >= 0.05: return 'Positive'
            elif score <= -0.05: return 'Negative'
            else: return 'Neutral'
            
        month_df = month_df.groupby(month_df['Date'].dt.day).agg({
            'Score': 'mean',
            'Entry': 'count'
        }).reset_index()
        month_df['Sentiment'] = month_df['Score'].apply(score_to_sentiment)
    else:
        month_df = pd.DataFrame()
    
    # Calendar setup
    cal = calendar.monthcalendar(selected_year, selected_month_num)
    mood_colors = {
        'Positive': '#4CAF50',
        'Neutral': '#FFC107',
        'Negative': '#F44336'
    }
    
    # Container for calendar with fixed width
    calendar_container = st.container()
    
    with calendar_container:
        # Month title
        st.markdown(
            f"<h3 style='text-align:center; margin-bottom:15px;'>{selected_month} {selected_year}</h3>",
            unsafe_allow_html=True
        )
        
        # Weekday headers
        weekdays = "".join([f"""
        <th style='
            width: 86px;
            text-align: center;
            padding: 8px 0;
            font-size: 14px;
        '>{day[:3]}</th>
        """ for day in calendar.day_abbr])
    

    # Build the entire calendar HTML
    calendar_html = """
    <style>
        .calendar-wrapper {
            width: 100%;
            display: flex;
            justify-content: center;
            align-items: center;
            flex-direction: column;
        }
        .mood-calendar {
            width: 604px;
            border-collapse: separate;
            border-spacing: 4px;
        }
        .mood-day {
            width: 86px;
            height: 86px;
            text-align: center;
            vertical-align: middle;
            border-radius: 8px;
            background-color: #f5f5f5;
            font-size: 16px;
            font-weight: normal;
        }
        .mood-day.has-entry {
            font-weight: bold;
            color: white;
        }
        .legend-container {
            margin-top: 20px;
            text-align: center;
        }
        .legend-item {
            display: inline-block;
            margin: 0 10px;
        }
        .legend-color {
            display: inline-block;
            width: 16px;
            height: 16px;
            border-radius: 50%;
            margin-right: 6px;
        }
    </style>
    <div class='calendar-wrapper'>
        <table class='mood-calendar'>
            <thead>
                <tr>
    """

    # Add weekday headers
    for day in calendar.day_abbr:
        calendar_html += f"<th style='text-align: center; padding: 8px 0; font-size: 14px;'>{day[:3]}</th>"
    calendar_html += "</tr></thead><tbody>"

    # Calendar cells
    for week in cal:
        calendar_html += "<tr>"
        for day in week:
            if day == 0:
                calendar_html += "<td class='mood-day'></td>"
            else:
                date_str = f"{selected_year}-{selected_month_num:02d}-{day:02d}"
                cell_style = ""
                tooltip = ""
                mood = None

                if not month_df.empty and day in month_df['Date'].values:
                    day_data = month_df[month_df['Date'] == day].iloc[0]
                    mood = day_data['Sentiment']
                    color = mood_colors.get(mood, "#f5f5f5")
                    cell_style = f"background-color: {color};"
                    tooltip = f"title='Avg mood: {mood} (Score: {day_data['Score']:.2f})'"
                    calendar_html += f"<td class='mood-day has-entry' style='{cell_style}' {tooltip}>{day}</td>"
                else:
                    # Default cell
                    calendar_html += f"<td class='mood-day'>{day}</td>"
        calendar_html += "</tr>"
    calendar_html += "</tbody></table>"

    # Legend HTML
    calendar_html += """
        <div class='legend-container'>
            <div class='legend-item'>
                <div class='legend-color' style='background-color: #4CAF50;'></div><span>Positive</span>
            </div>
            <div class='legend-item'>
                <div class='legend-color' style='background-color: #FFC107;'></div><span>Neutral</span>
            </div>
            <div class='legend-item'>
                <div class='legend-color' style='background-color: #F44336;'></div><span>Negative</span>
            </div>
        </div>
    </div>
    """

    st.markdown(calendar_html, unsafe_allow_html=True)

elif page == "Advanced Mood Analytics":

    # ===== 1. PREDICTIVE ANALYSIS =====
    st.subheader("Predictive Analysis : Mood Forecast")
    st.markdown("<div style='margin-top: 20px;'></div>", unsafe_allow_html=True)
    df = load_entries()

    if not df.empty:
        # Only continue if enough data is available
        if len(df) >= 14:  # At least 2 weeks of data for prediction
            # Prepare the data
            df['Date'] = pd.to_datetime(df['Date'])
            forecast_df = df.groupby('Date')['Score'].mean().to_frame()

            # Ensure daily frequency till today
            today = pd.Timestamp.today().normalize()
            full_range = pd.date_range(start=forecast_df.index.min(), end=today)
            forecast_df = forecast_df.reindex(full_range)
            forecast_df['Score'].interpolate(method='linear', inplace=True)

            # Fit ARIMA model
            model = ARIMA(forecast_df['Score'], order=(2, 1, 2))  # ARIMA(p,d,q)
            model_fit = model.fit()

            # Forecast next 7 days from TODAY
            forecast = model_fit.forecast(steps=7)

            # Generate dates from today+1 to today+7
            future_dates = pd.date_range(start=today + pd.Timedelta(days=1), periods=7)

            # Plot the forecast
            fig_forecast = plt.figure(figsize=(10, 4))
            plt.plot(forecast_df.index[-14:], forecast_df['Score'][-14:], label='Recent Sentiment')
            plt.plot(future_dates, forecast, marker='o', linestyle='--', color='red', label='Forecast')
            plt.axhline(0, color='gray', linestyle='--')
            plt.title("Forecasted Mood Trend (Next 7 Days)")
            plt.ylabel("Sentiment Score")
            plt.xlabel("Date")
            plt.legend()
            st.pyplot(fig_forecast)

            # Mood Dip Warning
            if forecast.min() < -0.5:
                st.warning("⚠️ Potential mood dip detected in the next week. Take care and prioritize self-care.")
            else:
                st.success("✅ No significant mood dips predicted in the upcoming week.")
        else:
            st.info("📉 Not enough data for prediction. Add more daily entries to enable forecasts.")

    
    # ===== 2. SLEEP/MOOD INTEGRATION =====
    st.markdown("---")
    st.subheader("Sleep/Mood Integration")
    from sleep_integration import show_sleep_analysis
    show_sleep_analysis()
    


# ADDITIONAL FEATURES SECTION

# --- Writing Prompts ---

st.sidebar.markdown("---")  # Visual separator
with st.sidebar.expander("💡 Writing Prompts"):
    if st.button("Get Random Prompt"):
        prompts = [
            "What made you smile today?",
            "What challenge did you overcome?",
            "What are you grateful for right now?",
            "Describe a moment you felt proud."
        ]
        st.session_state.prompt = random.choice(prompts)
    
    if 'prompt' in st.session_state:
        st.markdown(f"**Your Prompt:**\n\n{st.session_state.prompt}")
        if st.button("Clear Prompt"):
            del st.session_state.prompt

# --- PDF Export ---
st.sidebar.markdown("---")
with st.sidebar.expander("📤 Export Journal"):
    if st.button("Generate PDF Report"):
        try:
            with st.spinner("Creating PDF..."):
                entries = load_entries()

                if entries.empty:
                    st.warning("⚠️ No journal entries available to export.")
                else:
                    st.success(f"📝 Entries loaded: {len(entries)}")  # debug print
                    pdf_bytes = export_to_pdf(entries)
                    
                    if not pdf_bytes:
                        st.error("⚠️ PDF generation returned empty data.")
                    else:
                        st.download_button(
                            label="Download PDF",
                            data=pdf_bytes,
                            file_name=f"mood_journal_{datetime.now().date()}.pdf",
                            mime="application/pdf"
                        )
        except Exception as e:
            st.error(f"Export failed: {e}")




# [End of file - nothing should come after]
