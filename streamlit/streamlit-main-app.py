import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px
import plotly.graph_objs as go
from sklearn.preprocessing import LabelEncoder
from collections import Counter
from wordcloud import WordCloud
import folium
from folium.plugins import HeatMap
from streamlit_folium import folium_static
import pickle
import zipfile
import io
from PIL import Image
from scipy import stats

# Load data
@st.cache_data
def load_data():
    df_cleaned = pd.read_csv('Data/output/df_cleaned.csv')
    df_cleaned['job_posted_date'] = pd.to_datetime(df_cleaned['job_posted_date'])
    df_cleaned['date_only'] = df_cleaned['job_posted_date'].dt.date
    return df_cleaned

def process_skills(skills_string):
    skills_string = skills_string.replace('[', '').replace(']', '').replace('\'', '').replace(',', '')
    skills_list = skills_string.split()
    skills_list = ['power bi' if skill.lower() in ['power', 'bi'] else skill.lower() for skill in skills_list]
    skills_list = [skill for skill in skills_list if skill not in ['not', 'specified']]
    return skills_list

def extract_zip(zip_file):
    with zipfile.ZipFile(zip_file, 'r') as zipf:
        return {file_info.filename: zipf.read(file_info.filename) for file_info in zipf.infolist()}

def job_history_page(df):
    st.title("Job Market Exploratory Data Analysis")

    st.sidebar.header("Navigation")
    analysis_type = st.sidebar.selectbox("Choose Analysis", 
        ["Job Titles", "Job Trends", "Job Locations", "Job Postings Over Time", "Companies", "Salaries", "Skills"])

    if analysis_type == "Job Titles":
        st.subheader("Job Titles Analysis")
        
        job_title_counts = df['job_title_short'].value_counts()
        fig = px.bar(x=job_title_counts.index, y=job_title_counts.values, 
                     labels={'x': 'Job Title', 'y': 'Number of Jobs'}, 
                     title='Number of Jobs by Title')
        st.plotly_chart(fig)

        wordcloud = WordCloud(width=800, height=400, background_color='white').generate(' '.join(df['job_title_short']))
        fig, ax = plt.subplots(figsize=(10, 5))
        ax.imshow(wordcloud, interpolation='bilinear')
        ax.axis('off')
        st.pyplot(fig)

    elif analysis_type == "Job Trends":
        st.subheader("Job Trends Analysis")

        job_title_colors = {
            'Data Engineer': 'blue',
            'Data Analyst': 'green',
            'Data Scientist': 'red',
            'Machine Learning Engineer': 'purple',
            'Cloud Engineer': 'orange',
            'Business Analyst': 'pink',
            'Software Engineer': 'cyan'
        }

        fig, axes = plt.subplots(nrows=len(job_title_colors), ncols=1, sharex=True, figsize=(14, 24))
        axes = axes.flatten()

        for i, (job_title, color) in enumerate(job_title_colors.items()):
            filtered_df = df[df['job_title_short'] == job_title]
            jobs_per_day = filtered_df.groupby(filtered_df['job_posted_date'].dt.date).size()
            
            axes[i].plot(jobs_per_day.index, jobs_per_day.values, 
                         linestyle='-', color=color, label=f'{job_title} (Original)')
            
            x_values = np.arange(len(jobs_per_day))
            y_values = jobs_per_day.values
            slope, intercept, r_value, p_value, std_err = stats.linregress(x_values, y_values)
            trend_line = slope * x_values + intercept
            
            axes[i].plot(jobs_per_day.index, trend_line, 
                         linestyle='--', color='black', label=f'{job_title} (Trend)')
            
            axes[i].set_title(job_title)
            axes[i].set_ylabel('Number of Jobs')
            axes[i].legend()

        plt.xlabel('Date')
        plt.tight_layout()
        st.pyplot(fig)

    elif analysis_type == "Job Locations":
        st.subheader("Job Locations Analysis")
        
        st.write("Job Locations Heatmap")
        heat_data = [[row['latitude'], row['longitude']] for index, row in df.iterrows()]
        m = folium.Map(location=[df['latitude'].mean(), df['longitude'].mean()], zoom_start=4)
        HeatMap(heat_data).add_to(m)
        folium_static(m)

    elif analysis_type == "Job Postings Over Time":
        st.subheader("Job Postings Over Time")
        
        jobs_per_day = df.groupby(df['job_posted_date'].dt.date).size()
        fig = px.line(x=jobs_per_day.index, y=jobs_per_day.values, 
                      labels={'x': 'Date', 'y': 'Number of Jobs Posted'},
                      title='Number of Jobs Posted Over Time')
        st.plotly_chart(fig)

    elif analysis_type == "Companies":
        st.subheader("Top Companies")
        
        company_job_counts = df['company_name'].value_counts().head(10)
        fig = px.bar(x=company_job_counts.index, y=company_job_counts.values,
                     labels={'x': 'Company Name', 'y': 'Number of Jobs'},
                     title='Top 10 Companies by Number of Jobs')
        st.plotly_chart(fig)

    elif analysis_type == "Salaries":
        st.subheader("Salary Analysis")
        
        fig = px.box(df, x='job_title_short', y='salary_year_avg', 
                     labels={'job_title_short': 'Job Title', 'salary_year_avg': 'Average Annual Salary'},
                     title='Salary Distribution by Job Title')
        st.plotly_chart(fig)

        fig = px.histogram(df, x='salary_year_avg', nbins=30,
                           labels={'salary_year_avg': 'Average Annual Salary'},
                           title='Distribution of Average Annual Salary')
        st.plotly_chart(fig)

    elif analysis_type == "Skills":
        st.subheader("Top Job Skills")
        
        all_skills = ' '.join(df['job_skills'].dropna())
        skills_list = process_skills(all_skills)
        skills_counts = Counter(skills_list)
        skills_df = pd.DataFrame.from_dict(skills_counts, orient='index').reset_index()
        skills_df.columns = ['Skill', 'Count']
        skills_df = skills_df.sort_values(by='Count', ascending=False).head(20)
        
        fig = px.bar(skills_df, x='Skill', y='Count', 
                     title='Top 20 Job Skills')
        st.plotly_chart(fig)

def job_finder_page(df_cleaned):
    st.title("Job Finder")

    st.sidebar.header("Navigation")
    st.sidebar.button("Job post history")
    st.sidebar.button("Job finder")

    uploaded_file = st.file_uploader("Upload ZIP file containing models and plots", type="zip")

    job_types = [
        'Data Engineer', 'Data Analyst', 'Data Scientist',
        'Machine Learning Engineer', 'Cloud Engineer',
        'Business Analyst', 'Software Engineer'
    ]

    selected_job_type = st.selectbox("Select Job Type", job_types)

    if uploaded_file and selected_job_type:
        file_contents = extract_zip(uploaded_file)
        
        model_file_name = f'model_files/{selected_job_type}_job_prediction_model.pkl'
        plot_file_name = f'forecast_plots/{selected_job_type}_forecast.png'
        
        model_bytes = file_contents.get(model_file_name)
        if model_bytes:
            model = pickle.loads(model_bytes)
            
            future_dates = pd.date_range(start='2024-09-01', end='2024-12-31', freq='D')
            future_df = pd.DataFrame({'ds': future_dates})
            
            forecast = model.predict(future_df)
            
            st.subheader(f"Job Postings Forecast for {selected_job_type}")
            fig = go.Figure()
            fig.add_trace(go.Scatter(x=forecast['ds'], y=forecast['yhat'], mode='lines', name='Forecast'))
            fig.add_trace(go.Scatter(x=forecast['ds'], y=forecast['yhat_lower'], fill=None, mode='lines', line_color='rgba(0,100,80,0.2)', name='Lower Bound'))
            fig.add_trace(go.Scatter(x=forecast['ds'], y=forecast['yhat_upper'], fill='tonexty', mode='lines', line_color='rgba(0,100,80,0.2)', name='Upper Bound'))
            fig.update_layout(title=f'Job Postings Forecast for {selected_job_type}', xaxis_title='Date', yaxis_title='Number of Job Postings')
            st.plotly_chart(fig)

        plot_bytes = file_contents.get(plot_file_name)
        if plot_bytes:
            image = Image.open(io.BytesIO(plot_bytes))
            st.image(image, caption=f'{selected_job_type} Forecast Plot')
    
    st.header("Additional Filters")
    country = st.selectbox("Select country", df_cleaned['job_country'].unique())

    all_skills = ' '.join(df_cleaned['job_skills'].dropna())
    processed_skills = process_skills(all_skills)
    skill_counts = Counter(processed_skills)
    top_25_skills = [skill for skill, _ in skill_counts.most_common(25)]

    selected_skills = st.multiselect("Select skills (Top 25)", top_25_skills)

    # Display some statistics based on the selected filters
    if selected_job_type and country:
        filtered_df = df_cleaned[(df_cleaned['job_title_short'] == selected_job_type) & 
                                 (df_cleaned['job_country'] == country)]
        
        st.subheader(f"Statistics for {selected_job_type} in {country}")
        st.write(f"Total number of job postings: {len(filtered_df)}")
        st.write(f"Average salary: ${filtered_df['salary_year_avg'].mean():,.2f}")
        st.write(f"Most common skills: {', '.join([skill for skill, _ in skill_counts.most_common(5)])}")

def main():
    st.set_page_config(layout="wide", page_title="Job Market Analysis")
    
    df_cleaned = load_data()
    
    st.sidebar.title("Navigation")
    page = st.sidebar.radio("Go to", ["EDA", "Job Finder"])
    
    if page == "EDA":
        job_history_page(df_cleaned)
    elif page == "Job Finder":
        job_finder_page(df_cleaned)

if __name__ == "__main__":
    main()