import streamlit as st
import pandas as pd
import plotly.express as px

# --- PAGE CONFIGURATION ---
st.set_page_config(
    page_title="Global App Review Dashboard",
    page_icon="📊",
    layout="wide"
)

# --- DATA LOADING AND CACHING ---
# Use Streamlit's caching to load data only once
@st.cache_data
def load_data(path):
    df = pd.read_csv(path)
    # Convert review_date to datetime objects for time series analysis
    df['review_date'] = pd.to_datetime(df['review_date'])
    return df

# Load your dataset
df = load_data('cleaned_reviews.csv')


# --- MAIN PAGE ---

# --- HEADER ---
st.title("📊 Global App Review Sentiment Dashboard")
st.markdown("This dashboard provides an interactive way to analyze multilingual sentiment from app reviews.")


# --- SIDEBAR FOR FILTERS ---
st.sidebar.header("Filter Your Data")

# Filter by Country
selected_countries = st.sidebar.multiselect(
    "Select Countries",
    options=df['user_country'].unique(),
    default=df['user_country'].unique() # Default to all countries
)

# Filter by App Category
selected_categories = st.sidebar.multiselect(
    "Select App Categories",
    options=df['app_category'].unique(),
    default=df['app_category'].unique()
)

# Filter the dataframe based on sidebar selections
filtered_df = df[
    df['user_country'].isin(selected_countries) &
    df['app_category'].isin(selected_categories)
]

# Display a summary of the filtered data
st.sidebar.metric(label="Total Reviews Analyzed", value=len(filtered_df))


# --- DASHBOARD VISUALIZATIONS ---

# Create two columns for layout
col1, col2 = st.columns(2)

# --- CHART 1: Overall Sentiment Distribution (Pie Chart) ---
with col1:
    st.subheader("Overall Sentiment Distribution")
    sentiment_counts = filtered_df['sentiment'].value_counts()
    fig_pie = px.pie(
        values=sentiment_counts.values,
        names=sentiment_counts.index,
        title="Sentiment Breakdown",
        color=sentiment_counts.index,
        color_discrete_map={
            'positive': 'green',
            'negative': 'red',
            'neutral': 'grey'
        }
    )
    st.plotly_chart(fig_pie, use_container_width=True)


# --- CHART 2: Sentiment by Country (Bar Chart) ---
with col2:
    st.subheader("Sentiment by Country")
    sentiment_by_country = filtered_df.groupby(['user_country', 'sentiment']).size().reset_index(name='count')
    fig_bar = px.bar(
        sentiment_by_country,
        x='user_country',
        y='count',
        color='sentiment',
        title="Review Counts per Country",
        barmode='group',
        color_discrete_map={
            'positive': 'green',
            'negative': 'red',
            'neutral': 'grey'
        }
    )
    st.plotly_chart(fig_bar, use_container_width=True)


# --- CHART 3: Sentiment Over Time (Line Chart) ---
st.subheader("Sentiment Trends Over Time")
# Resample data by month for a cleaner trend line
filtered_df['month'] = filtered_df['review_date'].dt.to_period('M').astype(str)
sentiment_over_time = filtered_df.groupby(['month', 'sentiment']).size().reset_index(name='count')

fig_line = px.line(
    sentiment_over_time,
    x='month',
    y='count',
    color='sentiment',
    title="Monthly Review Sentiment",
    markers=True,
    color_discrete_map={
        'positive': 'green',
        'negative': 'red',
        'neutral': 'grey'
    }
)
st.plotly_chart(fig_line, use_container_width=True)

# --- Optional: Display Raw Filtered Data ---
if st.checkbox("Show Raw Data Table"):
    st.subheader("Filtered Review Data")
    st.dataframe(filtered_df)