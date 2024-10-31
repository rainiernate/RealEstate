import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go

st.set_page_config(page_title="Real Estate Analysis", layout="wide")

# Title and description
st.title("Bonney Lake Real Estate Analysis: Rambler vs 2-Story Homes")
st.markdown("Analysis of home sales comparing single-story and two-story properties")


# Load and process data
@st.cache_data
def load_data():
    df = pd.read_csv("Sold And Stats.csv")
    # Convert price and sqft to numeric, removing commas
    df['Selling Price'] = pd.to_numeric(df['Selling Price'].replace(',', '', regex=True), errors='coerce')
    df['Square Footage'] = pd.to_numeric(df['Square Footage'].replace(',', '', regex=True), errors='coerce')
    # Calculate price per sqft
    df['Price/SqFt'] = df['Selling Price'] / df['Square Footage']
    return df


df = load_data()

# Filter for 1 and 2 story homes
one_story = df[df['Style Code'] == '10 - 1 Story']
two_story = df[df['Style Code'] == '12 - 2 Story']

# Create three columns for metrics
col1, col2, col3 = st.columns(3)

# Calculate and display key metrics
with col1:
    st.metric("Number of Ramblers", f"{len(one_story)}")
    st.metric("Number of 2-Story", f"{len(two_story)}")

with col2:
    st.metric("Avg Rambler Price", f"${one_story['Selling Price'].mean():,.0f}")
    st.metric("Avg 2-Story Price", f"${two_story['Selling Price'].mean():,.0f}")

with col3:
    rambler_price_sqft = one_story['Price/SqFt'].mean()
    two_story_price_sqft = two_story['Price/SqFt'].mean()
    premium = ((rambler_price_sqft - two_story_price_sqft) / two_story_price_sqft) * 100

    st.metric("Avg Rambler $/SqFt", f"${rambler_price_sqft:.2f}")
    st.metric("Avg 2-Story $/SqFt", f"${two_story_price_sqft:.2f}")
    st.metric("Rambler Premium", f"{premium:.1f}%")

# Create two columns for charts
col1, col2 = st.columns(2)

with col1:
    # Box plot of prices
    fig_price = go.Figure()
    fig_price.add_trace(go.Box(y=one_story['Selling Price'], name='Ramblers'))
    fig_price.add_trace(go.Box(y=two_story['Selling Price'], name='2-Story'))
    fig_price.update_layout(title='Price Distribution by Home Type',
                            yaxis_title='Selling Price ($)')
    st.plotly_chart(fig_price)

with col2:
    # Box plot of price per square foot
    fig_ppsf = go.Figure()
    fig_ppsf.add_trace(go.Box(y=one_story['Price/SqFt'], name='Ramblers'))
    fig_ppsf.add_trace(go.Box(y=two_story['Price/SqFt'], name='2-Story'))
    fig_ppsf.update_layout(title='Price per SqFt Distribution by Home Type',
                           yaxis_title='Price per Square Foot ($)')
    st.plotly_chart(fig_ppsf)

# Scatter plot
fig_scatter = px.scatter(df[df['Style Code'].isin(['10 - 1 Story', '12 - 2 Story'])],
                         x='Square Footage',
                         y='Selling Price',
                         color='Style Code',
                         title='Price vs Square Footage by Home Type',
                         labels={'Selling Price': 'Selling Price ($)',
                                 'Square Footage': 'Square Footage',
                                 'Style Code': 'Home Type'})
st.plotly_chart(fig_scatter)

# Raw data viewer
st.subheader("Raw Data")
st.dataframe(df[df['Style Code'].isin(['10 - 1 Story', '12 - 2 Story'])].sort_values('Selling Price', ascending=False))

# Download button for CSV
csv = df[df['Style Code'].isin(['10 - 1 Story', '12 - 2 Story'])].to_csv(index=False)
st.download_button(
    label="Download Data as CSV",
    data=csv,
    file_name="real_estate_analysis.csv",
    mime="text/csv"
)