import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go


st.set_page_config(page_title="Real Estate Analysis", layout="wide")

# Title and description
st.title("Bonney Lake Real Estate Analysis: Rambler vs 2-Story Homes")

# Add search criteria in an expander
with st.expander("📋 Data Collection Criteria", expanded=True):
    st.markdown("""
    ### Search Parameters Used:
    - **Square Footage:** 1,800 - 2,200 sq ft
    - **Time Frame:** Sold within last 720 days
    - **Location:** Bonney Lake (98391)
    - **Home Types:** Single Story (Rambler) and Two Story homes only

    *Analysis based on MLS data pulled October 2024*
    """)

# Add disclaimer
st.warning("""
    📢 **Important Note:** 
    This analysis represents typical rambler vs 2-story sales in the area. Premium or luxury properties 
    (like ramblers with large lot sizes, highly desirable sub-communities, detached garages or high-end finishes) may command different premiums than shown here. 
    This data should be used as a general market reference only, not for specific property valuations.
""")


@st.cache_data
def load_data():
    df = pd.read_csv("Sold And Stats.csv")
    # Convert price and sqft to numeric, removing commas
    df['Selling Price'] = pd.to_numeric(df['Selling Price'].replace(',', '', regex=True), errors='coerce')
    df['Square Footage'] = pd.to_numeric(df['Square Footage'].replace(',', '', regex=True), errors='coerce')
    # Ensure listing number is stored as a string without commas
    df['Listing Number'] = df['Listing Number'].astype(str).replace(',', '', regex=True)
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
    # Box plot of prices with Listing Number in hover data
    fig_price = go.Figure()
    fig_price.add_trace(
        go.Box(
            y=one_story['Selling Price'],
            name='Ramblers',
            customdata=one_story['Listing Number'],  # Add Listing Number as custom data
            hovertemplate="Listing #: %{customdata}<br>Price: $%{y:,.0f}"  # Use hovertemplate to display
        )
    )
    fig_price.add_trace(
        go.Box(
            y=two_story['Selling Price'],
            name='2-Story',
            customdata=two_story['Listing Number'],  # Add Listing Number as custom data
            hovertemplate="Listing #: %{customdata}<br>Price: $%{y:,.0f}"
        )
    )
    fig_price.update_layout(
        title='Price Distribution by Home Type',
        yaxis_title='Selling Price ($)'
    )
    st.plotly_chart(fig_price, use_container_width=True)


with col2:
    # Box plot of price per square foot with Listing Number in hover data
    fig_ppsf = go.Figure()
    fig_ppsf.add_trace(
        go.Box(
            y=one_story['Price/SqFt'],
            name='Ramblers',
            customdata=one_story['Listing Number'],  # Add Listing Number as custom data
            hovertemplate="Listing #: %{customdata}<br>$/SqFt: $%{y:.2f}"
        )
    )
    fig_ppsf.add_trace(
        go.Box(
            y=two_story['Price/SqFt'],
            name='2-Story',
            customdata=two_story['Listing Number'],  # Add Listing Number as custom data
            hovertemplate="Listing #: %{customdata}<br>$/SqFt: $%{y:.2f}"
        )
    )
    fig_ppsf.update_layout(
        title='Price per SqFt Distribution by Home Type',
        yaxis_title='Price per Square Foot ($)'
    )
    st.plotly_chart(fig_ppsf, use_container_width=True)


# Scatter plot
# Update the scatter plot section with hover data
fig_scatter = px.scatter(
    df[df['Style Code'].isin(['10 - 1 Story', '12 - 2 Story'])],
    x='Square Footage',
    y='Selling Price',
    color='Style Code',
    title='Price vs Square Footage by Home Type',
    labels={
        'Selling Price': 'Selling Price ($)',
        'Square Footage': 'Square Footage',
        'Style Code': 'Home Type',
        'Listing Number': 'MLS #'  # Add label for MLS number
    },
    hover_data={
        'Listing Number': True,  # Add MLS number to hover
        'Selling Price': ':$,.0f',  # Format price with comma and no decimals
        'Square Footage': ':,.0f',  # Format sqft with comma
        'Style Code': True
    }
)

# Update layout for better hover display
fig_scatter.update_traces(
    hovertemplate="<br>".join([
        "MLS #: %{customdata[0]}",
        "Price: %{y:$,.0f}",
        "SqFt: %{x:,.0f}",
        "Type: %{customdata[3]}"
    ])
)

st.plotly_chart(fig_scatter, use_container_width=True)

# Raw data viewer
st.subheader("Raw Data")
# Create a copy of the dataframe with Listing Number formatted as a plain string
df_display = df[df['Style Code'].isin(['10 - 1 Story', '12 - 2 Story'])].sort_values('Selling Price', ascending=False)
df_display['Listing Number'] = df_display['Listing Number'].astype(str).replace(',', '', regex=True)
st.dataframe(df_display)

# Download button for CSV
csv = df[df['Style Code'].isin(['10 - 1 Story', '12 - 2 Story'])].to_csv(index=False)
st.download_button(
    label="Download Data as CSV",
    data=csv,
    file_name="real_estate_analysis.csv",
    mime="text/csv"
)