import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# Setting full-width layout
st.set_page_config(page_title="Sri Lanka Hotel Insights", layout="wide")

#  DATA LOADING
df = pd.read_csv("cleaned_hotels_data.csv")
df = df.rename(columns={"Logitiute": "Longitude"})  

#  SIDEBAR NAVIGATION 
st.sidebar.title(" Hotel Analytics Dashboard")
page = st.sidebar.radio("Navigate to:", ["Overview & Summary", "Dashboard"], index=0)  

#  OVERVIEW PAGE 
if page == "Overview & Summary":
   
    import base64

    def get_base64_image(image_path):
        with open(image_path, "rb") as img_file:
            encoded = base64.b64encode(img_file.read()).decode()
        return f"data:image/jpg;base64,{encoded}"

    image_base64 = get_base64_image("Hotelbackground.jpeg")  

    st.markdown(
        f"""
        <style>
        .stApp {{
            background-image: linear-gradient(rgba(0, 0, 0, 0.4), rgba(0, 0, 0, 0.4)),
                              url("{image_base64}");
            background-size: cover;
            background-position: center;
            background-repeat: no-repeat;
            background-attachment: fixed;
        }}
        </style>
        """,
        unsafe_allow_html=True
    )
    st.title("Sri Lanka Classified Hotels Dashboard")
    st.subheader("About")
    st.markdown("""
    This dashboard presents an interactive analysis of classified hotels in Sri Lanka. 
    It is designed to support tourism development and urban planning by revealing key patterns 
    in hotel distribution, size, grades, and regional presence.
    """)

    st.subheader("Dataset Summary")
    st.markdown("This dataset includes hotel name, district, address, rooms, grade, region, coordinates, and classification details.")
    st.write("### Descriptive Statistics:")
    st.dataframe(df.describe(include='all').transpose(), use_container_width=True)

#  DASHBOARD PAGE 
elif page == "Dashboard":
    # Sidebar filters
    st.sidebar.markdown("#### 🎯 Filter the data below:")

    # District filter
    all_districts = ["All"] + list(df["District"].unique())
    selected_districts = st.sidebar.multiselect("Select District(s):", options=all_districts, default=["All"])
    districts = df["District"].unique() if "All" in selected_districts else selected_districts

    # Room range filter
    room_range = st.sidebar.slider("Select Room Range:", min_value=int(df["Rooms"].min()), max_value=int(df["Rooms"].max()), value=(int(df["Rooms"].min()), int(df["Rooms"].max())))

    # Grade range filter
    grade_range = st.sidebar.slider("Select Grade Range:", min_value=int(df["Grade"].min()), max_value=int(df["Grade"].max()), value=(int(df["Grade"].min()), int(df["Grade"].max())))

    # Filter data
    df_filtered = df[
        (df["District"].isin(districts)) &
        (df["Rooms"].between(room_range[0], room_range[1])) &
        (df["Grade"].between(grade_range[0], grade_range[1]))
    ]

    st.title("Sri Lanka Classified Hotels Dashboard")
    st.subheader("Explore classified hotel trends, types, and distribution across the island")

    # Show dataset
    with st.expander("View Complete Hotel Dataset"):
        if st.checkbox("Show complete dataset"):
            st.dataframe(df, use_container_width=True)

    #  KPIs 
    kpi1, kpi2, kpi3 = st.columns(3)

    # Total Hotels
    kpi1.metric("Total Hotels", len(df_filtered))

    # Avg. Rooms with NaN check
    avg_rooms = df_filtered["Rooms"].mean()
    kpi2.metric("Avg. Rooms", int(avg_rooms) if not pd.isna(avg_rooms) else 0) 

    # Avg. Grade with NaN check
    avg_grade = df_filtered["Grade"].mean()
    kpi3.metric("Avg. Grade", round(avg_grade, 2) if not pd.isna(avg_grade) else 0)  

    if df_filtered.empty:
        st.warning("⚠️ No data available for selected filters. Please adjust them.")
        st.stop()

    #  INSIGHTS 
    st.markdown("### 📊 Key Insights")

    # Insight 1: Hotel Distribution by Province
    st.markdown("#### Insight 1: Hotel Distribution by Region")
    province_counts = df_filtered['Region'].value_counts().reset_index()
    province_counts.columns = ['Region', 'Count']
    fig1 = px.bar(province_counts, x='Region', y='Count', color='Region', title='Number of Hotels by Province')
    st.plotly_chart(fig1, use_container_width=True)

    # Insight 2: Star Category Distribution
    st.markdown("#### Insight 2: Hotel Grade Category Distribution")
    star_counts = df_filtered['Grade'].value_counts().reset_index()
    star_counts.columns = ['Grade', 'Count']
    fig2 = px.pie(star_counts, names='Grade', values='Count', hole=0.4, title='Distribution of Hotel Star Ratings')
    st.plotly_chart(fig2, use_container_width=True)

    # Insight 3: Hotel Classification by Type
    st.markdown("#### Insight 3: Hotel Classification by Type")
    if 'Hotel_Type' in df_filtered.columns:
        type_counts = df_filtered['Hotel_Type'].value_counts().reset_index()
        type_counts.columns = ['Hotel Type', 'Count']
        fig3 = px.bar(type_counts, x='Count', y='Hotel Type', orientation='h', title='Hotel Types in Sri Lanka')
        st.plotly_chart(fig3, use_container_width=True)
    else:
        st.warning("Column 'Hotel_Type' not found in dataset.")

    # Insight 4: Top 10 Cities with Most Hotels
    st.markdown("#### Insight 4: Top 10 Districts with Most Hotels")
    top_cities = df_filtered['District'].value_counts().head(10).reset_index()
    top_cities.columns = ['District', 'Count']
    fig4 = px.bar(top_cities, x='District', y='Count', color='District', title='Top 10 Districts with Most Hotels')
    st.plotly_chart(fig4, use_container_width=True)

    # Insight 5: Interactive Filter by Province and Star Rating
    st.markdown("#### Insight 5: Explore Hotels by Province and Star Rating")
    provinces = sorted(df['Region'].dropna().unique())
    stars = sorted(df['Grade'].dropna().unique())
    col1, col2 = st.columns(2)
    with col1:
        selected_province = st.selectbox("Select Region", provinces)
    with col2:
        selected_star = st.selectbox("Select Hotel Grade", stars)
    filtered_df = df[(df['Region'] == selected_province) & (df['Grade'] == selected_star)]
    st.markdown(f"**{len(filtered_df)} hotels** found in **{selected_province}** with a **{selected_star}** rating.")
    st.dataframe(filtered_df)

    # Insight 6: Hotel Distribution by Size Category
    st.markdown("#### Insight 6: Hotel Distribution by Size Category")
    if 'Hotel_Size_Category' in df_filtered.columns:
        size_counts = df_filtered['Hotel_Size_Category'].value_counts().reset_index()
        size_counts.columns = ['Size Category', 'Count']
        fig6 = px.bar(size_counts, x='Size Category', y='Count', color='Size Category', title='Hotel Size Category Distribution')
        st.plotly_chart(fig6, use_container_width=True)
    else:
        st.warning("Column 'Hotel_Size_Category' not found in dataset.")

    # Additional Insight: Grade Distribution by Hotel Size Category
    st.markdown("#### Insight 7: Grade Distribution by Hotel Size Category")
    if 'Hotel_Size_Category' in df_filtered.columns:
        fig = px.box(df_filtered, x='Hotel_Size_Category', y='Grade', color='Hotel_Size_Category',
                     title='Grade Distribution by Hotel Size')
        st.plotly_chart(fig, use_container_width=True)

    # Insight 8
    st.markdown("#### Insight 8: Grade vs Number of Rooms")
    chart_type = st.radio("Select chart type:", ["Line Chart", "Scatter Plot"], horizontal=True)

    if chart_type == "Line Chart":
        grade_rooms = df_filtered.groupby("Grade")["Rooms"].mean().reset_index()
        fig8 = px.line(grade_rooms, x='Grade', y='Rooms', markers=True, title='Average Rooms per Grade Category')
    else:
        fig8 = px.scatter(df_filtered, x='Grade', y='Rooms', color='Grade', trendline='ols',
                          title='Do Higher-Graded Hotels Have More Rooms?')

    st.plotly_chart(fig8, use_container_width=True)

    st.subheader("9. Geographical Distribution of Hotels on Map")

    if {'Latitude', 'Longitude'}.issubset(df.columns):
        st.markdown("This map shows the location of classified hotels. Hover to see details.")

        fig_map = px.scatter_mapbox(
            df,
            lat='Latitude',
            lon='Longitude',
            color='Grade',  
            hover_name='Name',
            hover_data=['Region', 'Address', 'Grade'],
            zoom=6,
            height=600
        )

        fig_map.update_layout(
            mapbox_style='open-street-map',
            margin={"r":0,"t":0,"l":0,"b":0},
            dragmode='zoom'
        )

        st.plotly_chart(fig_map, use_container_width=True)
    else:
        st.warning("Latitude and Longitude columns are missing for map visualization.")

    #  DOWNLOAD BUTTON 
    csv = df_filtered.to_csv(index=False)
    st.download_button("📥 Download Filtered Data", data=csv, file_name="filtered_hotels.csv", mime="text/csv")











