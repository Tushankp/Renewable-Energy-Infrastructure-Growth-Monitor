# renewable_energy_dashboard_upload.py
import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import io
import warnings
import tempfile
import os
warnings.filterwarnings('ignore')

# Set page configuration
st.set_page_config(
    page_title="Renewable Energy Dashboard",
    page_icon="🌍",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        color: #2E86AB;
        text-align: center;
        padding: 1rem;
        background: linear-gradient(90deg, #2E86AB, #A23B72);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    .sub-header {
        font-size: 1.5rem;
        color: #1B3B6F;
        margin-top: 1rem;
        border-bottom: 2px solid #2E86AB;
        padding-bottom: 0.5rem;
    }
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1.5rem;
        border-radius: 15px;
        color: white;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        margin: 0.5rem 0;
        transition: transform 0.3s ease;
    }
    .metric-card:hover {
        transform: translateY(-5px);
    }
    .stProgress > div > div > div > div {
        background: linear-gradient(90deg, #2E86AB, #A23B72);
    }
    .upload-section {
        background: #f8f9fa;
        padding: 2rem;
        border-radius: 15px;
        border: 2px dashed #2E86AB;
        margin-bottom: 2rem;
    }
    .data-preview {
        max-height: 400px;
        overflow-y: auto;
        border: 1px solid #ddd;
        border-radius: 10px;
        padding: 1rem;
        background: white;
    }
</style>
""", unsafe_allow_html=True)

# Title and description
st.markdown('<h1 class="main-header">🌍 Renewable Energy Analysis Dashboard</h1>', unsafe_allow_html=True)
st.markdown("""
<div style='text-align: center; margin-bottom: 2rem;'>
    <p style='font-size: 1.1rem; color: #666;'>
        Upload your renewable energy data or use sample data to explore insights into global renewable energy capacity, 
        growth trends, and regional analysis.
    </p>
</div>
""", unsafe_allow_html=True)

# Sample data generation function
@st.cache_data
def generate_sample_data():
    """Generate sample renewable energy data for demonstration"""
    np.random.seed(42)
    
    # Create sample data
    regions = ['Africa', 'Americas', 'Asia', 'Europe', 'Oceania']
    technologies = ['Solar photovoltaic', 'Onshore wind energy', 'Renewable hydropower', 
                   'Solid biofuels', 'Offshore wind energy', 'Geothermal energy']
    
    data = []
    for year in range(2010, 2024):
        for region in regions:
            for tech in technologies:
                for _ in range(np.random.randint(10, 30)):
                    country = f"Country_{np.random.randint(1, 50)}"
                    capacity = np.random.uniform(10, 5000)
                    growth_rate = np.random.uniform(-10, 30)
                    generation = capacity * np.random.uniform(1000, 2000)  # Convert to GWh
                    
                    data.append({
                        'Region Indicator': region,
                        'Country': country,
                        'Technology': tech,
                        'Year': year,
                        'Electricity Installed Capacity (MW)': capacity,
                        'Electricity Generation (GWh)': generation,
                        'Growth_Rate (%)': growth_rate
                    })
    
    df = pd.DataFrame(data)
    return df

# Function to compute growth rates
def compute_growth_rate(df):
    """Calculate growth rates from capacity data"""
    if 'Year' not in df.columns or 'Electricity Installed Capacity (MW)' not in df.columns:
        return None
    
    # Sort by region and year
    df_sorted = df.sort_values(['Region Indicator', 'Technology', 'Year'])
    
    # Calculate previous year's capacity
    df_sorted['Prev_Year_Capacity'] = df_sorted.groupby(['Region Indicator', 'Technology'])['Electricity Installed Capacity (MW)'].shift(1)
    
    # Calculate growth rate
    df_sorted['Growth_Rate (%)'] = (
        (df_sorted['Electricity Installed Capacity (MW)'] - df_sorted['Prev_Year_Capacity'])
        / df_sorted['Prev_Year_Capacity'] * 100
    )
    
    # Remove rows where growth rate cannot be calculated
    df_growth = df_sorted.dropna(subset=['Growth_Rate (%)'])
    return df_growth

# File upload section
st.markdown("""
<div class="upload-section">
    <h3 style='color: #2E86AB; margin-bottom: 1rem;'> Upload Your Data</h3>
</div>
""", unsafe_allow_html=True)

col1, col2 = st.columns([2, 1])

with col1:
    upload_option = st.radio(
        "Choose data source:",
        ["Upload CSV/Excel file", "Use sample data", "Enter data manually"],
        horizontal=True
    )
    
    uploaded_file = None
    df = None
    
    if upload_option == "Upload CSV/Excel file":
        uploaded_file = st.file_uploader(
            "Choose a file",
            type=['csv', 'xlsx', 'xls'],
            help="Upload your renewable energy data file (CSV or Excel)"
        )
        
        if uploaded_file is not None:
            try:
                # Read the uploaded file
                if uploaded_file.name.endswith('.csv'):
                    df = pd.read_csv(uploaded_file)
                else:
                    df = pd.read_excel(uploaded_file)
                
                st.success(f" File '{uploaded_file.name}' uploaded successfully!")
                
            except Exception as e:
                st.error(f"Error reading file: {str(e)}")
                st.info("Please check your file format and try again.")
    
    elif upload_option == "Use sample data":
        if st.button("Generate Sample Data", use_container_width=True):
            df = generate_sample_data()
            st.success(" Sample data generated successfully!")
    
    else:  # Enter data manually
        st.info("""
        **Manual Data Entry Format:**
        - Region Indicator: Text
        - Country: Text  
        - Technology: Text
        - Year: Number
        - Electricity Installed Capacity (MW): Number
        - Electricity Generation (GWh): Number (optional)
        """)
        
        # Create a data editor for manual entry
        manual_data = st.data_editor(
            pd.DataFrame(columns=[
                'Region Indicator', 'Country', 'Technology', 
                'Year', 'Electricity Installed Capacity (MW)', 'Electricity Generation (GWh)'
            ]),
            num_rows="dynamic",
            use_container_width=True
        )
        
        if not manual_data.empty:
            df = manual_data
            st.success(" Manual data entered successfully!")

with col2:
    # Quick stats when data is loaded
    if df is not None:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.metric("Rows Loaded", f"{len(df):,}")
        st.metric("Columns", f"{len(df.columns)}")
        st.metric("Data Range", f"{df['Year'].min() if 'Year' in df.columns else 'N/A'}-{df['Year'].max() if 'Year' in df.columns else 'N/A'}")
        st.markdown('</div>', unsafe_allow_html=True)

# Data preview and validation
if df is not None:
    st.markdown('<h3 class="sub-header"> Data Preview</h3>', unsafe_allow_html=True)
    
    # Show data preview
    st.dataframe(df.head(), use_container_width=True)
    
    # Data information
    with st.expander(" Data Information", expanded=False):
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.write("**Column Names:**")
            st.write(df.columns.tolist())
        
        with col2:
            st.write("**Data Types:**")
            st.write(df.dtypes)
        
        with col3:
            st.write("**Missing Values:**")
            st.write(df.isnull().sum())
    
    # Data cleaning options
    st.markdown('<h3 class="sub-header"> Data Cleaning</h3>', unsafe_allow_html=True)
    
    cleaning_options = st.multiselect(
        "Select cleaning operations:",
        ["Remove duplicate rows", "Fill missing values", "Convert data types", "Filter by year range"],
        default=["Remove duplicate rows"]
    )
    
    df_clean = df.copy()
    
    if "Remove duplicate rows" in cleaning_options:
        initial_rows = len(df_clean)
        df_clean = df_clean.drop_duplicates()
        st.info(f"Removed {initial_rows - len(df_clean)} duplicate rows")
    
    if "Fill missing values" in cleaning_options:
        col1, col2 = st.columns(2)
        with col1:
            numeric_cols = df_clean.select_dtypes(include=[np.number]).columns.tolist()
            if numeric_cols:
                fill_method = st.selectbox(
                    "Fill method for numeric columns:",
                    ["Mean", "Median", "Zero", "Forward fill", "Backward fill"]
                )
                
                if st.button("Fill Missing Values", key="fill_numeric"):
                    if fill_method == "Mean":
                        df_clean[numeric_cols] = df_clean[numeric_cols].fillna(df_clean[numeric_cols].mean())
                    elif fill_method == "Median":
                        df_clean[numeric_cols] = df_clean[numeric_cols].fillna(df_clean[numeric_cols].median())
                    elif fill_method == "Zero":
                        df_clean[numeric_cols] = df_clean[numeric_cols].fillna(0)
                    elif fill_method == "Forward fill":
                        df_clean[numeric_cols] = df_clean[numeric_cols].fillna(method='ffill')
                    else:
                        df_clean[numeric_cols] = df_clean[numeric_cols].fillna(method='bfill')
                    
                    st.success("Missing values filled!")
    
    if "Filter by year range" in cleaning_options and 'Year' in df_clean.columns:
        min_year = int(df_clean['Year'].min())
        max_year = int(df_clean['Year'].max())
        year_range = st.slider(
            "Select year range:",
            min_value=min_year,
            max_value=max_year,
            value=(min_year, max_year)
        )
        df_clean = df_clean[(df_clean['Year'] >= year_range[0]) & (df_clean['Year'] <= year_range[1])]
    
    # Calculate growth rates
    df_growth = compute_growth_rate(df_clean)
    
    # Rename columns for consistency
    if 'Electricity Installed Capacity (MW)' in df_clean.columns:
        df_clean['Capacity_MW'] = df_clean['Electricity Installed Capacity (MW)']
    if 'Electricity Generation (GWh)' in df_clean.columns:
        df_clean['Generation_GWh'] = df_clean['Electricity Generation (GWh)']
    
    # Main dashboard section
    st.markdown("---")
    st.markdown('<h2 class="main-header">📈 Dashboard Analysis</h2>', unsafe_allow_html=True)
    
    # Sidebar for filters
    st.sidebar.markdown("##  Filters")
    
    # Year filter
    if 'Year' in df_clean.columns:
        year_min = int(df_clean['Year'].min())
        year_max = int(df_clean['Year'].max())
        selected_years = st.sidebar.slider(
            "Year Range",
            year_min, year_max,
            (year_min, year_max)
        )
        df_filtered = df_clean[(df_clean['Year'] >= selected_years[0]) & (df_clean['Year'] <= selected_years[1])]
    else:
        df_filtered = df_clean
    
    # Region filter
    if 'Region Indicator' in df_filtered.columns:
        regions = ['All'] + sorted(df_filtered['Region Indicator'].unique().tolist())
        selected_region = st.sidebar.selectbox("Region", regions)
        if selected_region != 'All':
            df_filtered = df_filtered[df_filtered['Region Indicator'] == selected_region]
    
    # Technology filter
    if 'Technology' in df_filtered.columns:
        technologies = ['All'] + sorted(df_filtered['Technology'].unique().tolist())
        selected_tech = st.sidebar.selectbox("Technology", technologies)
        if selected_tech != 'All':
            df_filtered = df_filtered[df_filtered['Technology'] == selected_tech]
    
    # Key metrics
    st.markdown("###  Key Metrics")
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        if 'Capacity_MW' in df_filtered.columns:
            total_capacity = df_filtered['Capacity_MW'].sum() / 1000
            st.metric("Total Capacity (GW)", f"{total_capacity:,.1f}")
    
    with col2:
        if 'Generation_GWh' in df_filtered.columns:
            total_generation = df_filtered['Generation_GWh'].sum() / 1000
            st.metric("Total Generation (TWh)", f"{total_generation:,.1f}")
    
    with col3:
        if 'Country' in df_filtered.columns:
            country_count = df_filtered['Country'].nunique()
            st.metric("Countries", country_count)
    
    with col4:
        if 'Technology' in df_filtered.columns:
            tech_count = df_filtered['Technology'].nunique()
            st.metric("Technologies", tech_count)
    
    # Visualization tabs
    tab1, tab2, tab3, tab4 = st.tabs([" Overview", " Regional", " Technology", " Export"])
    
    with tab1:
        # Capacity over time
        if 'Year' in df_filtered.columns and 'Capacity_MW' in df_filtered.columns:
            yearly_capacity = df_filtered.groupby('Year')['Capacity_MW'].sum().reset_index()
            fig1 = px.line(
                yearly_capacity, 
                x='Year', 
                y='Capacity_MW',
                title='Total Capacity Over Time',
                markers=True,
                line_shape='spline'
            )
            fig1.update_layout(
                xaxis_title="Year",
                yaxis_title="Capacity (MW)",
                template='plotly_white'
            )
            st.plotly_chart(fig1, use_container_width=True)
        
        # Growth rate analysis
        if df_growth is not None and not df_growth.empty:
            fig2 = px.box(
                df_growth,
                x='Technology' if 'Technology' in df_growth.columns else 'Region Indicator',
                y='Growth_Rate (%)',
                title='Growth Rate Distribution',
                color='Technology' if 'Technology' in df_growth.columns else 'Region Indicator'
            )
            st.plotly_chart(fig2, use_container_width=True)
    
    with tab2:
        if 'Region Indicator' in df_filtered.columns and 'Capacity_MW' in df_filtered.columns:
            # Regional capacity distribution
            regional_capacity = df_filtered.groupby('Region Indicator')['Capacity_MW'].sum().reset_index()
            fig3 = px.pie(
                regional_capacity,
                values='Capacity_MW',
                names='Region Indicator',
                title='Regional Capacity Distribution',
                hole=0.4
            )
            st.plotly_chart(fig3, use_container_width=True)
            
            # Regional trend
            regional_trend = df_filtered.groupby(['Year', 'Region Indicator'])['Capacity_MW'].sum().reset_index()
            fig4 = px.line(
                regional_trend,
                x='Year',
                y='Capacity_MW',
                color='Region Indicator',
                title='Regional Capacity Trends',
                line_shape='spline'
            )
            st.plotly_chart(fig4, use_container_width=True)
    
    with tab3:
        if 'Technology' in df_filtered.columns and 'Capacity_MW' in df_filtered.columns:
            # Technology distribution
            tech_dist = df_filtered.groupby('Technology')['Capacity_MW'].sum().reset_index()
            fig5 = px.bar(
                tech_dist.sort_values('Capacity_MW', ascending=True),
                x='Capacity_MW',
                y='Technology',
                orientation='h',
                title='Technology Capacity Distribution',
                color='Capacity_MW',
                color_continuous_scale='Viridis'
            )
            st.plotly_chart(fig5, use_container_width=True)
            
            # Technology adoption over time
            tech_trend = df_filtered.groupby(['Year', 'Technology'])['Capacity_MW'].sum().reset_index()
            fig6 = px.area(
                tech_trend,
                x='Year',
                y='Capacity_MW',
                color='Technology',
                title='Technology Adoption Over Time'
            )
            st.plotly_chart(fig6, use_container_width=True)
    
    with tab4:
        st.markdown("###  Export Data and Visualizations")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("#### Export Data")
            
            # Export cleaned data
            if st.button(" Export Cleaned Data as CSV", use_container_width=True):
                csv = df_clean.to_csv(index=False)
                st.download_button(
                    label="Download CSV",
                    data=csv,
                    file_name="cleaned_renewable_energy_data.csv",
                    mime="text/csv",
                    use_container_width=True
                )
            
            # Export growth data
            if df_growth is not None and not df_growth.empty:
                if st.button(" Export Growth Data as CSV", use_container_width=True):
                    csv = df_growth.to_csv(index=False)
                    st.download_button(
                        label="Download CSV",
                        data=csv,
                        file_name="growth_rate_data.csv",
                        mime="text/csv",
                        use_container_width=True
                    )
        
        with col2:
            st.markdown("#### Export Report")
            
            # Generate report
            if st.button(" Generate Analysis Report", use_container_width=True):
                report = f"""
                # Renewable Energy Analysis Report
                
                ## Summary
                - Total Records: {len(df_clean):,}
                - Time Period: {df_clean['Year'].min() if 'Year' in df_clean.columns else 'N/A'} - {df_clean['Year'].max() if 'Year' in df_clean.columns else 'N/A'}
                - Regions: {df_clean['Region Indicator'].nunique() if 'Region Indicator' in df_clean.columns else 'N/A'}
                - Technologies: {df_clean['Technology'].nunique() if 'Technology' in df_clean.columns else 'N/A'}
                - Countries: {df_clean['Country'].nunique() if 'Country' in df_clean.columns else 'N/A'}
                
                ## Key Metrics
                - Total Capacity: {df_clean['Capacity_MW'].sum() / 1000:,.1f} GW (if available)
                - Average Growth Rate: {df_growth['Growth_Rate (%)'].mean() if df_growth is not None and not df_growth.empty else 'N/A'}%
                
                ## Data Quality
                - Missing Values: {df.isnull().sum().sum()}
                - Duplicate Rows Removed: {len(df) - len(df_clean)}
                """
                
                st.download_button(
                    label="Download Report (TXT)",
                    data=report,
                    file_name="renewable_energy_report.txt",
                    mime="text/plain",
                    use_container_width=True
                )
        
        # Save visualizations
        st.markdown("#### Save Visualizations")
        if st.button(" Save Current Dashboard as HTML", use_container_width=True):
            # Create a simple HTML report
            html_content = """
            <html>
            <head>
                <title>Renewable Energy Dashboard Report</title>
                <style>
                    body { font-family: Arial, sans-serif; margin: 40px; }
                    .header { color: #2E86AB; text-align: center; }
                    .metric { background: #f4f4f4; padding: 20px; margin: 10px; border-radius: 10px; }
                </style>
            </head>
            <body>
                <h1 class="header">Renewable Energy Analysis Report</h1>
                <p>Generated on: """ + pd.Timestamp.now().strftime("%Y-%m-%d %H:%M:%S") + """</p>
                <div class="metric">
                    <h3>Data Summary</h3>
                    <p>Total Records: """ + str(len(df_clean)) + """</p>
                    <p>Analysis completed successfully.</p>
                </div>
            </body>
            </html>
            """
            
            st.download_button(
                label="Download HTML Report",
                data=html_content,
                file_name="renewable_energy_dashboard_report.html",
                mime="text/html",
                use_container_width=True
            )
    
    # Sidebar information
    st.sidebar.markdown("---")
    st.sidebar.markdown("###  Data Information")
    
    if df is not None:
        st.sidebar.info(f"""
        **Loaded Data:**
        - Rows: {len(df):,}
        - Columns: {len(df.columns)}
        - Memory: {df.memory_usage(deep=True).sum() / 1024**2:.1f} MB
        """)
    
    st.sidebar.markdown("###  Tools")
    if st.sidebar.button("Clear Cache", use_container_width=True):
        st.cache_data.clear()
        st.success("Cache cleared!")
    
else:
    # Show welcome message when no data is loaded
    st.markdown("""
    <div style='text-align: center; padding: 4rem; background: #f8f9fa; border-radius: 15px;'>
        <h3 style='color: #666; margin-bottom: 1rem;'> Ready to Analyze Your Data?</h3>
        <p style='color: #888;'>Upload your renewable energy data to get started with interactive visualizations and insights.</p>
        <div style='margin-top: 2rem;'>
            <span style='background: #2E86AB; color: white; padding: 10px 20px; border-radius: 25px; display: inline-block;'>
                 Use the options above to upload your data
            </span>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Show sample data structure
    with st.expander(" Expected Data Format", expanded=True):
        st.markdown("""
        **Recommended columns for analysis:**
        
        | Column | Type | Description |
        |--------|------|-------------|
        | Region Indicator | Text | Geographic region (e.g., Africa, Asia) |
        | Country | Text | Country name |
        | Technology | Text | Energy technology type |
        | Year | Integer | Year of data |
        | Electricity Installed Capacity (MW) | Float | Installed capacity in megawatts |
        | Electricity Generation (GWh) | Float | Electricity generation in gigawatt-hours |
        
        **Example CSV format:**
        ```csv
        Region Indicator,Country,Technology,Year,Electricity Installed Capacity (MW),Electricity Generation (GWh)
        Africa,Country_A,Solar photovoltaic,2020,1500,2500
        Asia,Country_B,Wind energy,2021,3200,5800
        Europe,Country_C,Hydropower,2022,5000,12000
        ```
        """)

# Footer
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #666; font-size: 0.9rem; padding: 1rem;'>
    <p> Renewable Energy Analysis Dashboard | Created with Streamlit | Upload your data for instant insights</p>
    <p style='font-size: 0.8rem; color: #888;'>
        Supports CSV, Excel, and manual data entry • Interactive visualizations • Real-time analysis
    </p>
</div>
""", unsafe_allow_html=True)