import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# Load data
@st.cache_data
def load_data():
    return pd.read_excel("Smart_Issue_Clusters_and_Tags.xlsx")

df = load_data()

st.title("📊 Smart Issue Clustering & Pattern Dashboard")

# Sidebar: Cluster Definitions
with st.sidebar:
    st.header("📖 Cluster Descriptions")
    st.markdown("""
    - **Cluster 0**: Access/user request-related issues
    - **Cluster 1**: Workflow or environment issues (e.g. GuidingCare, PROD)
    - **Cluster 2**: Script/assessment-related problems
    - **Cluster 3**: Complaints or documentation
    - **Cluster 4**: Member data, test plans, ID management
    """)

# Search bar
search_query = st.text_input("🔍 Search Issues by Summary or Tag")
if search_query:
    df = df[df['Summary'].str.contains(search_query, case=False, na=False) | 
            df['Suggested Tag'].str.contains(search_query, case=False, na=False)]

# Date range filter
if 'Created' in df.columns:
    df['Created'] = pd.to_datetime(df['Created'], errors='coerce')
    start_date, end_date = st.date_input("Filter by Created Date Range", [df['Created'].min(), df['Created'].max()])
    df = df[(df['Created'] >= pd.to_datetime(start_date)) & (df['Created'] <= pd.to_datetime(end_date))]

# Status filter
status_options = df['Status'].dropna().unique()
selected_statuses = st.multiselect("Filter by Status", status_options, default=list(status_options))
df = df[df['Status'].isin(selected_statuses)]

# Filter by cluster or tag
selected_cluster = st.selectbox("Select Cluster", sorted(df['Cluster'].unique()))
filtered_df = df[df['Cluster'] == selected_cluster]

st.subheader(f"👥 Issues in Cluster {selected_cluster}")
st.dataframe(filtered_df[['Issue key', 'Summary', 'Suggested Tag', 'Status']])

# Show cluster keyword breakdown
st.markdown("---")
st.subheader("🖥 Suggested Tags Overview")
st.bar_chart(df['Suggested Tag'].value_counts())

# Trend Chart
st.markdown("---")
st.subheader("📅 Issue Trend Over Time")

if 'Created' in df.columns:
    trend_data = df.groupby(df['Created'].dt.to_period('M')).size()
    trend_data.index = trend_data.index.astype(str)
    st.line_chart(trend_data)
else:
    st.warning("Created date column not available for trend analysis.")

# 2D Chart - Cluster vs Suggested Tags
st.markdown("---")
st.subheader("🗺️ Cluster vs Suggested Tags (2D Heatmap)")
heatmap_data = df.groupby(['Cluster', 'Suggested Tag']).size().unstack(fill_value=0)
fig, ax = plt.subplots(figsize=(10, 6))
sns.heatmap(heatmap_data, annot=True, fmt="d", cmap="Blues", ax=ax)
st.pyplot(fig)

# Export filtered data
st.markdown("---")
st.subheader("📥 Export Filtered Data")
@st.cache_data
def convert_df_to_csv(dataframe):
    return dataframe.to_csv(index=False).encode('utf-8')

csv_data = convert_df_to_csv(filtered_df)
st.download_button(label="Download CSV", data=csv_data, file_name='filtered_issues.csv', mime='text/csv')
