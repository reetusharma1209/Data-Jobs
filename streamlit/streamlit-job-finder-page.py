def job_finder_page():
    st.title("Job Finder")
    
    # User input widgets
    st.subheader("Enter Your Information")
    
    education = st.dropdown("Location")
    skills = st.multiselect("Skills" )
    experience = st.slider("Prediction interval")
   
    
    
    # Make prediction
    if st.button("Find Jobs"):
        # Prepare input data for the model
        input_data = {
            'Education': job_country,
            'Experience': experience,
            'Skills': skills,
            'Job_Type': job_type
        }
        
        # Convert input data to format expected by the model
        # This part depends on how your model expects the input
        model_input = pd.DataFrame([input_data])
        
        # Make prediction
        prediction = model.predict(model_input)
        
        # Display results
        st.subheader("Recommended Jobs")
        results = pd.DataFrame({
            'Job Title': prediction,
            'Company': ['Company A', 'Company B', 'Company C'],
            'Location': ['New York', 'San Francisco', 'Chicago']
        })
        st.table(results)
