# Data Science Job Market Analysis

## Project Overview
This project analyzes the data science job market using a dataset of job postings. The analysis includes exploratory data analysis (EDA) and time series forecasting to understand current trends and predict future job postings.

## Table of Contents
1. [Data Preparation](#data-preparation)
2. [Exploratory Data Analysis](#exploratory-data-analysis)
3. [Time Series Forecasting](#time-series-forecasting)
4. [Key Findings](#key-findings)
5. [Installation and Usage](#installation-and-usage)

## Data Preparation
The project uses a cleaned dataset (`df_cleaned.csv`) containing information about data science job postings. The data includes features such as job titles, posting dates, locations, and the number of jobs.

## Exploratory Data Analysis
The EDA phase includes various visualizations and analyses:

- Distribution of job titles
- Job postings over time
- Geographical distribution of jobs
- Analysis of job skills
- Salary distributions

Key visualizations:
- Bar plots of job counts by title
- Word cloud of job titles
- Heatmap of job locations
- Time series plot of job postings
- Stacked bar chart of job skills by job title
- Box plots of salary distributions by job title

## Time Series Forecasting
The project uses Facebook's Prophet library for time series forecasting:

- Weekly and monthly forecasts for different job titles
- Cross-validation to assess model performance
- Performance metrics analysis (RMSE, MAE, MAPE)

## Key Findings
(Note: This section should be filled with actual insights from your analysis. Here are some placeholder points based on the code:)

1. The most common job titles in the dataset are [list top job titles].
2. There's a [increasing/decreasing] trend in job postings over time.
3. [City/Country] has the highest concentration of data science jobs.
4. The most in-demand skills across all job titles are [list top skills].
5. [Job Title] has the highest median salary among all job titles analyzed.
6. Short-term forecasts (up to 8 days) show high accuracy, while long-term forecasts should be used with caution.

## Installation and Usage

### Prerequisites
- Python 3.x
- pip

### Installation
1. Clone this repository:
   ```
   git clone [repository-url]
   ```
2. Navigate to the project directory:
   ```
   cd data-science-job-market-analysis
   ```
3. Install the required packages:
   ```
   pip install -r requirements.txt
   ```

### Usage
1. Run the EDA notebook:
   ```
   jupyter notebook EDA.ipynb
   ```
2. Run the time series forecasting notebook:
   ```
   jupyter notebook prophet.ipynb

   ```
## Live Demo

Check out the live version of the app: [Emerging Data Job Opportunities](https://reetusharma1209-data-jobs-app-app-32jadi.streamlit.app/)

## Contributing
Contributions to this project are welcome. Please fork the repository and submit a pull request with your changes.

## License
This project is licensed under the MIT License - see the LICENSE file for details.
