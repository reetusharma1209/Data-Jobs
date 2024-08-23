import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px
import plotly.graph_objs as go
from wordcloud import WordCloud
import folium
from folium.plugins import HeatMap
from streamlit_folium import folium_static
from collections import Counter
from scipy import stats

# Load data
@st.cache_data
def load_data():
    df = pd.read_csv('Data/output/df_cleaned.csv')
    df['job_posted_date'] = pd.to_datetime(df['job_posted_date'])
    df['date_only'] = df['job_posted_date'].dt.date
    return df

def process_skills(skills_string):
    skills_string = skills_string.replace('[', '').replace(']', '').replace('\'', '').replace(',', '')
    skills_list = skills_string.split()
    skills_list = ['power bi' if skill.lower() in ['power', 'bi'] else skill.lower() for skill in skills_list]
    skills_list = [skill for skill in skills_list if skill not in ['not', 'specified']]
    return skills_list

def main():
    st.set_page_config(layout="wide", page_title="Job Market Analysis Presentation")
    
    df = load_data()

    st.title("Job Market Analysis Project")
    st.write("An in-depth exploration of job trends in the data science and technology sectors")

    sections = [
        "Introduction",
        "Job Landscape Overview",
        "Geographical Distribution",
        "Temporal Trends",
        "Skill Analysis",
        "Salary Insights",
        "Future Predictions",
        "Conclusion"
    ]

    section = st.sidebar.radio("Navigate Presentation", sections)

    if section == "Introduction":
        st.header("Introduction")
        st.write("""
        Welcome to our Job Market Analysis project. This presentation will take you through a comprehensive 
        analysis of job trends in the data science and technology sectors. We'll explore various aspects of 
        the job market, from geographical distribution to skill demands and salary trends.
        
        Our analysis is based on a rich dataset of job postings, which we've processed and analyzed to extract 
        meaningful insights. Throughout this presentation, you'll encounter interactive visualizations that 
        allow you to explore the data in depth.
        
        Let's begin our journey through the current landscape of tech jobs!
        """)

        st.subheader("Dataset Overview")
        st.write(f"Total number of job postings analyzed: {len(df)}")
        st.write(f"Date range of data: from {df['job_posted_date'].min().date()} to {df['job_posted_date'].max().date()}")
        st.write(f"Number of unique job titles: {df['job_title_short'].nunique()}")
        st.write(f"Number of countries: {df['job_country'].nunique()}")

    elif section == "Job Landscape Overview":
        st.header("Job Landscape Overview")
        
        st.subheader("Distribution of Job Titles")
        job_title_counts = df['job_title_short'].value_counts()
        fig = px.bar(x=job_title_counts.index, y=job_title_counts.values, 
                     labels={'x': 'Job Title', 'y': 'Number of Jobs'}, 
                     title='Number of Jobs by Title')
        st.plotly_chart(fig)

        st.subheader("Word Cloud of Job Titles")
        wordcloud = WordCloud(width=800, height=400, background_color='white').generate(' '.join(df['job_title_short']))
        fig, ax = plt.subplots(figsize=(10, 5))
        ax.imshow(wordcloud, interpolation='bilinear')
        ax.axis('off')
        st.pyplot(fig)

        st.write("""
        The bar chart and word cloud above provide a visual representation of the most common job titles in our dataset. 
        This gives us an immediate sense of which roles are in high demand in the current job market.
        """)

    elif section == "Geographical Distribution":
        st.header("Geographical Distribution of Jobs")

        st.subheader("Job Locations Heatmap")
        heat_data = [[row['latitude'], row['longitude']] for index, row in df.iterrows()]
        m = folium.Map(location=[df['latitude'].mean(), df['longitude'].mean()], zoom_start=2)
        HeatMap(heat_data).add_to(m)
        folium_static(m)

        st.write("""
        The heatmap above shows the global distribution of job postings. Brighter areas indicate a higher concentration of job opportunities. 
        This visualization helps us identify the major hubs for tech and data science jobs worldwide.
        """)

        st.subheader("Top Countries for Job Postings")
        top_countries = df['job_country'].value_counts().head(10)
        fig = px.bar(x=top_countries.index, y=top_countries.values, 
                     labels={'x': 'Country', 'y': 'Number of Jobs'}, 
                     title='Top 10 Countries by Number of Job Postings')
        st.plotly_chart(fig)

    elif section == "Temporal Trends":
        st.header("Temporal Trends in Job Postings")

        st.subheader("Job Postings Over Time")
        jobs_per_day = df.groupby(df['job_posted_date'].dt.date).size()
        fig = px.line(x=jobs_per_day.index, y=jobs_per_day.values, 
                      labels={'x': 'Date', 'y': 'Number of Jobs Posted'},
                      title='Number of Jobs Posted Over Time')
        st.plotly_chart(fig)

        st.write("""
        This time series plot shows how the number of job postings has changed over time. It helps us identify any 
        seasonal patterns or overall trends in job market activity.
        """)

        st.subheader("Job Type Trends")
        job_types = df['job_title_short'].unique()
        selected_job_type = st.selectbox("Select a job type to view its trend", job_types)

        filtered_df = df[df['job_title_short'] == selected_job_type]
        jobs_per_day = filtered_df.groupby(filtered_df['job_posted_date'].dt.date).size()

        x_values = np.arange(len(jobs_per_day))
        y_values = jobs_per_day.values
        slope, intercept, r_value, p_value, std_err = stats.linregress(x_values, y_values)
        trend_line = slope * x_values + intercept

        fig = go.Figure()
        fig.add_trace(go.Scatter(x=jobs_per_day.index, y=jobs_per_day.values, mode='lines', name='Actual'))
        fig.add_trace(go.Scatter(x=jobs_per_day.index, y=trend_line, mode='lines', name='Trend'))
        fig.update_layout(title=f'Job Posting Trend for {selected_job_type}', xaxis_title='Date', yaxis_title='Number of Jobs')
        st.plotly_chart(fig)

    elif section == "Skill Analysis":
        st.header("Skill Analysis")

        all_skills = ' '.join(df['job_skills'].dropna())
        skills_list = process_skills(all_skills)
        skills_counts = Counter(skills_list)
        skills_df = pd.DataFrame.from_dict(skills_counts, orient='index').reset_index()
        skills_df.columns = ['Skill', 'Count']
        skills_df = skills_df.sort_values(by='Count', ascending=False).head(20)

        st.subheader("Top 20 In-Demand Skills")
        fig = px.bar(skills_df, x='Skill', y='Count', title='Top 20 Job Skills')
        st.plotly_chart(fig)

        st.write("""
        This chart showcases the most in-demand skills based on our job posting data. It provides valuable insights 
        into what employers are looking for and can guide professionals in their skill development journey.
        """)

        st.subheader("Skill Co-occurrence")
        selected_skill = st.selectbox("Select a skill to see co-occurring skills", skills_df['Skill'])
        co_occurring_skills = df[df['job_skills'].str.contains(selected_skill, case=False, na=False)]['job_skills'].str.cat(sep=',')
        co_occurring_skills = process_skills(co_occurring_skills)
        co_occurring_counts = Counter(co_occurring_skills)
        co_occurring_df = pd.DataFrame.from_dict(co_occurring_counts, orient='index').reset_index()
        co_occurring_df.columns = ['Skill', 'Count']
        co_occurring_df = co_occurring_df[co_occurring_df['Skill'] != selected_skill].sort_values(by='Count', ascending=False).head(10)

        fig = px.bar(co_occurring_df, x='Skill', y='Count', title=f'Top 10 Skills Co-occurring with {selected_skill}')
        st.plotly_chart(fig)

    elif section == "Salary Insights":
        st.header("Salary Insights")

        st.subheader("Salary Distribution by Job Title")
        fig = px.box(df, x='job_title_short', y='salary_year_avg', 
                     labels={'job_title_short': 'Job Title', 'salary_year_avg': 'Average Annual Salary'},
                     title='Salary Distribution by Job Title')
        st.plotly_chart(fig)

        st.write("""
        This box plot shows the distribution of salaries for different job titles. It helps us understand the salary 
        ranges for various roles and identify which positions tend to offer higher compensation.
        """)

        st.subheader("Salary vs. Experience")
        fig = px.scatter(df, x='job_experience_required', y='salary_year_avg', 
                         color='job_title_short', 
                         labels={'job_experience_required': 'Years of Experience Required', 'salary_year_avg': 'Average Annual Salary'},
                         title='Salary vs. Experience by Job Title')
        st.plotly_chart(fig)

        st.write("""
        This scatter plot illustrates the relationship between required experience and offered salary across different job titles. 
        It can help job seekers understand how their experience level might influence their earning potential.
        """)

    elif section == "Future Predictions":
        st.header("Future Predictions")
        st.write("""
        Based on our analysis of historical data and current trends, we can make some predictions about the future of the job market 
        in the tech and data science sectors:

        1. Continued Growth: We expect the demand for data science and tech roles to continue growing, especially in areas like 
           machine learning, AI, and cloud computing.

        2. Skill Evolution: The rapid pace of technological change means that in-demand skills will continue to evolve. Continuous 
           learning and adaptation will be crucial for professionals in this field.

        3. Remote Work: The trend towards remote work is likely to persist, potentially leading to more globally distributed teams 
           and opportunities.

        4. Emphasis on Soft Skills: While technical skills remain crucial, we anticipate an increasing emphasis on soft skills such 
           as communication, problem-solving, and adaptability.

        5. Specialization: As the field matures, we may see more specialized roles emerging, catering to niche areas within data 
           science and technology.
        """)

        st.subheader("Predict Future Job Postings")
        st.write("""
        For more precise predictions, you can use the Job Finder tool, which utilizes machine learning models to forecast 
        job postings based on historical data and trends.
        """)

    elif section == "Conclusion":
        st.header("Conclusion")
        st.write("""
        Our analysis of the job market in the data science and technology sectors reveals a dynamic and rapidly evolving landscape. 
        Key takeaways include:

        1. The job market is showing robust growth, with increasing demand across various roles in data science and technology.

        2. There's a global distribution of opportunities, with certain regions emerging as major hubs for tech jobs.

        3. Skills in high demand include both technical abilities (like Python, SQL, and machine learning) and soft skills.

        4. Salaries vary significantly based on job role, experience, and location, with certain specializations commanding higher compensation.

        5. The job market is likely to continue evolving, with new roles and skills emerging in response to technological advancements.

        For professionals and job seekers in this field, staying updated with the latest skills and industry trends will be crucial for 
        long-term career success. Employers should focus on creating competitive packages and fostering environments that support continuous 
        learning and development to attract and retain top talent.

        Thank you for exploring this Job Market Analysis with us!
        """)

if __name__ == "__main__":
    main()