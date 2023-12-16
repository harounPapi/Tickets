### Documentation

#### Application Overview

This Streamlit application is designed to analyze and visualize ticketing data. It features two main pages:

1. **Dashboard**: Displays visualizations of the ticketing data.
2. **Add Data**: Allows users to upload CSV data and save analysis results.

#### Page Descriptions

- **Dashboard Page**:
  - If data exists in `ticket_analysis_results.csv`, it displays various charts:
    - Bar charts for comparing total vs. resolved tickets (assigned and reported) for each worker.
    - Pie charts showing the time distribution per ticket for each worker.
  - If no data is available, it prompts to upload data in the "Add Data" page.

- **Add Data Page**:
  - Users can upload a CSV file with ticketing data.
  - After selecting a worker and specifying dates, the app calculates and displays ticket counts and statuses.
  - Users can save the analysis to `ticket_analysis_results.csv` by clicking the "Save Analysis to CSV" button.

#### Modifying the Code

- **To Add New Features or Pages**:
  - Add new functions for each feature/page.
  - Update the `main` function with new page choices and corresponding function calls.

- **To Change Visualizations**:
  - In `display_dashboard`, modify or add new `st.write`, `st.bar_chart`, `st.pyplot`, etc., calls as per requirements.
  - Use different plotting libraries (like Seaborn or Plotly) for more advanced visualizations.

- **To Alter Data Analysis Logic**:
  - Modify `categorize_status`, `add_percentage_column`, or `save_to_csv` functions.
  - Add new calculations or data processing steps within `add_data`.

#### Running the Application

1. Ensure Python and Streamlit are installed.
2. Place the code in a Python file (e.g., `tickets.py`).
3. Run the application using `streamlit run tickets.py`.

#### Updating the Requirements

- If additional libraries are used, add them to `requirements.txt`.
- Use `pip freeze > requirements.txt` to automatically generate the file with current environment package versions.

