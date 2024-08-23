def eda_page():
    st.title("Exploratory Data Analysis")
    
    data = load_data()
    
    st.subheader("Dataset Overview")
    st.write(data.head())
    
    st.subheader("Data Distribution")
    column = st.selectbox("Select a column for histogram", data.columns)
    fig = px.histogram(data, x=column)
    st.plotly_chart(fig)
    
    st.subheader("Correlation Heatmap")
    corr = data.corr()
    fig = px.imshow(corr, color_continuous_scale='viridis')
    st.plotly_chart(fig)
    
    st.subheader("Scatter Plot")
    x_axis = st.selectbox("Select X-axis", data.columns)
    y_axis = st.selectbox("Select Y-axis", data.columns)
    fig = px.scatter(data, x=x_axis, y=y_axis)
    st.plotly_chart(fig)
