import matplotlib.pyplot as plt
import seaborn as sns
import os
import folium
from wordcloud import WordCloud
import pandas as pd
import numpy as np

# Load the dataset


# Load the DataFrame from the CSV file
df = pd.read_csv('Data/output/df_cleaned.csv')


# Create a directory to save the plots if it doesn't exist
if not os.path.exists('eda_plots'):
    os.makedirs('eda_plots')

# 1. Distribution of Job Titles
job_title_counts = df['job_title_short'].value_counts()
plt.figure(figsize=(12, 8))
sns.barplot(x=job_title_counts.index, y=job_title_counts.values, palette='husl')
plt.xticks(rotation=90)
plt.xlabel('Job Title')
plt.ylabel('Number of Jobs')
plt.title('Number of Jobs by Title')
plt.tight_layout()
plt.savefig('eda_plots/jobs_by_title.png')
plt.close()

# 2. Job Titles Word Cloud
text = ' '.join(df['job_title_short'].dropna())
wordcloud = WordCloud(width=800, height=400, background_color='white').generate(text)
plt.figure(figsize=(10, 5))
plt.imshow(wordcloud, interpolation='bilinear')
plt.axis('off')
plt.title('Job Titles Word Cloud')
plt.tight_layout()
plt.savefig('eda_plots/job_titles_wordcloud.png')
plt.close()

# 3. Job Locations Heatmap
heat_data = [[row['latitude'], row['longitude']] for index, row in df.iterrows()]
m = folium.Map(location=[df['latitude'].mean(), df['longitude'].mean()], zoom_start=2)
folium.plugins.HeatMap(heat_data).add_to(m)
m.save('eda_plots/job_locations_heatmap.html')

# 4. Job Posting Trends by Job Title
df['job_posted_date'] = pd.to_datetime(df['job_posted_date'])
job_title_colors = {
    'Data Engineer': 'blue', 'Data Analyst': 'green', 'Data Scientist': 'red',
    'Machine Learning Engineer': 'purple', 'Cloud Engineer': 'orange',
    'Business Analyst': 'pink', 'Software Engineer': 'cyan'
}
fig, axes = plt.subplots(nrows=len(job_title_colors), ncols=1, sharex=True, figsize=(14, 16))
axes = axes.flatten()
for i, (job_title, color) in enumerate(job_title_colors.items()):
    filtered_df = df[df['job_title_short'] == job_title]
    jobs_per_day = filtered_df.groupby(filtered_df['job_posted_date'].dt.date).size()
    axes[i].plot(jobs_per_day.index, jobs_per_day.values, linestyle='-', color=color, label=f'{job_title} (Original)')
    x_values = np.arange(len(jobs_per_day))
    z = np.polyfit(x_values, jobs_per_day.values, 1)
    p = np.poly1d(z)
    axes[i].plot(jobs_per_day.index, p(x_values), linestyle='--', color='black', label=f'{job_title} (Trend)')
    axes[i].set_title(job_title)
    axes[i].set_ylabel('Number of Jobs')
    axes[i].legend()
plt.xlabel('Date')
plt.tight_layout()
plt.savefig('eda_plots/job_posting_trends.png')
plt.close()

# 5. Job Posting Sources and Schedule Types
df['job_via'] = df['job_via'].str.replace('via', '', regex=False).str.replace(r'.*Trabajo.*', 'Trabajo', regex=True)
job_via_counts = df['job_via'].value_counts()
sorted_job_via_counts = job_via_counts.sort_values(ascending=False).head(10)
top_15_df = df[df['job_via'].isin(sorted_job_via_counts.index)]
job_schedule_colors = {'Full-time': 'blue', 'Part-time': 'green', 'Contract': 'orange'}
plot_data = top_15_df.groupby(['job_via', 'job_schedule_type']).size().unstack().fillna(0)
plot_data = plot_data.loc[sorted_job_via_counts.index]
plt.figure(figsize=(12, 8))
ax = plot_data.plot(kind='barh', stacked=True, color=[job_schedule_colors.get(x, 'grey') for x in plot_data.columns], figsize=(12, 8))
ax.invert_yaxis()
plt.subplots_adjust(left=0.2, right=0.8, top=0.9, bottom=0.1)
plt.xlabel('Number of Jobs')
plt.ylabel('Job Via')
plt.title('Number of Jobs by Job Via (Top 10) with Job Schedule Type')
plt.legend(title='Job Schedule Type', bbox_to_anchor=(1.05, 1), loc='upper left')
plt.tight_layout()
plt.savefig('eda_plots/job_sources_and_schedules.png')
plt.close()

# 6. Job Schedule Type Distribution
job_schedule_counts = df['job_schedule_type'].value_counts()
plt.figure(figsize=(8, 8))
plt.pie(job_schedule_counts, labels=job_schedule_counts.index, autopct='%1.1f%%', colors=sns.color_palette('pastel'))
plt.title('Job Schedule Type Distribution')
plt.savefig('eda_plots/job_schedule_distribution.png')
plt.close()

# 7. Top Companies and Countries for Job Postings
company_job_counts = df['company_name'].value_counts().head(10)
company_countries = df.groupby('company_name')['job_country'].agg(lambda x: x.mode()[0])
country_job_counts = df['job_country'].value_counts().head(10)
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(20, 8))
sns.barplot(x=country_job_counts.index, y=country_job_counts.values, palette=sns.color_palette("magma", len(country_job_counts)), ax=ax1)
ax1.set_xticklabels(ax1.get_xticklabels(), rotation=45, ha='right')
ax1.set_xlabel('Country')
ax1.set_ylabel('Number of Job Postings')
ax1.set_title('Top 10 Countries by Job Postings')
sns.barplot(x=company_job_counts.index, y=company_job_counts.values, palette=sns.color_palette("magma", len(company_job_counts)), ax=ax2)
ax2.set_xticklabels(ax2.get_xticklabels(), rotation=45, ha='right')
ax2.set_xlabel('Company Name')
ax2.set_ylabel('Number of Jobs')
ax2.set_title('Top 10 Companies by Number of Jobs')
for i, company in enumerate(company_job_counts.index):
    country = company_countries[company]
    ax2.text(i, company_job_counts.values[i]/2, country, ha='center', va='center', rotation=90, color='white')
plt.tight_layout()
plt.savefig('eda_plots/top_companies_and_countries.png')
plt.close()

# 8. Top Skills by Job Title
skills_expanded = []
for _, row in df.dropna(subset=['job_skills']).iterrows():
    job_title = row['job_title_short']
    skills = row['job_skills'].replace('[', '').replace(']', '').replace("'", '').replace(',', '').split()
    skills = [skill.lower() for skill in skills]
    skills = ['power bi' if skill in ['power', 'bi'] else skill for skill in skills]
    skills = [skill for skill in skills if skill not in ['not', 'specified']]
    for skill in skills:
        skills_expanded.append((skill, job_title))
skills_df = pd.DataFrame(skills_expanded, columns=['Skill', 'job_title_short'])
skills_counts = skills_df.groupby(['Skill', 'job_title_short']).size().unstack(fill_value=0)
top_skills_counts = skills_counts.sum(axis=1).sort_values(ascending=False).head(20)
top_skills_df = skills_counts.loc[top_skills_counts.index]
custom_order = ['Data Engineer', 'Data Analyst', 'Data Scientist', 'Machine Learning Engineer', 'Cloud Engineer', 'Business Analyst', 'Software Engineer']
plt.figure(figsize=(12, 8))
ax = top_skills_df.plot(kind='barh', stacked=True, figsize=(12, 8), colormap='magma')
ax.invert_yaxis()
handles, labels = ax.get_legend_handles_labels()
legend_dict = dict(zip(labels, handles))
ordered_handles = [legend_dict[label] for label in custom_order if label in legend_dict]
plt.legend(handles=ordered_handles, labels=[label for label in custom_order if label in legend_dict], title='Job Title')
plt.xlabel('Count')
plt.ylabel('Skill')
plt.title('Top 20 Job Skills by Job Title')
plt.tight_layout()
plt.savefig('eda_plots/top_skills_by_job_title.png')
plt.close()

# 9. Salary vs. Job Frequency
grouped_df = df.groupby('job_title_short').agg({'num_jobs': 'sum', 'salary_year_avg': 'mean'}).reset_index()
plt.figure(figsize=(12, 8))
sns.scatterplot(x='salary_year_avg', y='num_jobs', size='num_jobs', hue='job_title_short', data=grouped_df, palette='plasma', sizes=(100, 2000))
plt.xlabel('Average Annual Salary')
plt.ylabel('Total Number of Jobs')
plt.title('Salary vs. Total Job Frequency by Job Title')
plt.legend(title='Job Title', bbox_to_anchor=(1.05, 1), loc='upper left')
plt.grid(True)
plt.tight_layout()
plt.savefig('eda_plots/salary_vs_job_frequency.png')
plt.close()

print("All plots have been saved in the 'eda_plots' directory.")
