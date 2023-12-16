import streamlit as st
import pandas as pd
import numpy as np
from datetime import timedelta
import os
import matplotlib.pyplot as plt


def categorize_status(status):
    categories = ['resolved', 'closed', 'assigned', 'delayed', 'feedback', 'inprogress']
    return status if status in categories else 'other'

def add_percentage_column(status_counts, total):
    percentages = (status_counts / total * 100).round(2).astype(str) + '%'
    return pd.DataFrame({'Count': status_counts, 'Percentage': percentages})

def check_existing_data(file_name, start_date, end_date, worker):
    if os.path.exists(file_name):
        df = pd.read_csv(file_name)
        df['Start Date'] = pd.to_datetime(df['Start Date'])
        df['End Date'] = pd.to_datetime(df['End Date'])
        start_date = pd.to_datetime(start_date)
        end_date = pd.to_datetime(end_date)
        return any((df['Start Date'] == start_date) & (df['End Date'] == end_date) & (df['Worker'] == worker))
    return False

def save_to_csv(start_date, end_date, selected_entity, assigned_table, reported_table, average_hours_per_assigned, average_hours_per_reported, total_hours):
    file_name = 'ticket_analysis_results.csv'
    if check_existing_data(file_name, start_date, end_date, selected_entity):
        st.warning('Entry already exists with the same Start Date, End Date, and Worker!')
        return

    data_to_save = {
        'Start Date': start_date,
        'End Date': end_date,
        'Worker': selected_entity,
        'Total Reported Tickets': reported_table['Count'].get('Total', 0),
        'Total Assigned Tickets': assigned_table['Count'].get('Total', 0),
        'Resolved Reported Tickets Count': reported_table['Count'].get('resolved', 0),
        'Resolved Assigned Tickets Count': assigned_table['Count'].get('resolved', 0),
        'Percentage of Resolved Reported Tickets': reported_table['Percentage'].get('resolved', '0%'),
        'Percentage of Resolved Assigned Tickets': assigned_table['Percentage'].get('resolved', '0%'),
        'Average Work Days per Assigned Resolved Ticket': average_hours_per_assigned,
        'Average Work Days per Reported Resolved Ticket': average_hours_per_reported,
        'Total Work Days': total_hours / 8
    }

    df_to_save = pd.DataFrame([data_to_save])
    df_to_save.to_csv(file_name, index=False, mode='a', header=not os.path.exists(file_name))
    st.success('Data saved successfully!')

def main():
    st.sidebar.title("Navigation")
    page = st.sidebar.radio("Choose a Page", ["Dashboard", "Add Data"])

    if page == "Dashboard":
        display_dashboard()
    else:
        add_data()

def display_dashboard():
    st.title("Dashboard")

    file_name = 'ticket_analysis_results.csv'
    if os.path.exists(file_name) and os.path.getsize(file_name) > 0:
        data = pd.read_csv(file_name)

        st.write("Data Overview:")
        st.dataframe(data)

        # Bar Chart: Total Assigned vs Resolved Assigned Tickets
        st.write("Total Assigned vs Resolved Assigned Tickets by Worker")
        assigned_chart_data = data[['Worker', 'Total Assigned Tickets', 'Resolved Assigned Tickets Count']].set_index('Worker')
        st.bar_chart(assigned_chart_data)

        # Bar Chart: Total Reported vs Resolved Reported Tickets
        st.write("Total Reported vs Resolved Reported Tickets by Worker")
        reported_chart_data = data[['Worker', 'Total Reported Tickets', 'Resolved Reported Tickets Count']].set_index('Worker')
        st.bar_chart(reported_chart_data)

        # Pie Charts: Time Spent per Ticket for Each Worker
        for i, row in data.iterrows():
            st.write(f"Time Distribution per Ticket for {row['Worker']}")
            labels = ['Average Time per Assigned Resolved Ticket', 'Average Time per Reported Resolved Ticket']
            sizes = [row['Average Work Days per Assigned Resolved Ticket'], row['Average Work Days per Reported Resolved Ticket']]
            fig, ax = plt.subplots()
            ax.pie(sizes, labels=labels, autopct='%1.1f%%', startangle=90)
            ax.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle.
            st.pyplot(fig)

    else:
        st.write("No data available. Please go to 'Add Data' to input data.")



def add_data():
    st.title("Add Data to CSV")

    uploaded_file = st.file_uploader("Upload your CSV file", type=["csv"])
    
    if uploaded_file is not None:
        data = pd.read_csv(uploaded_file)
        first_set = data[['Reporter', 'Category', 'Status']]
        second_set = data[['Assigned To', 'Category.1', 'Status.1']]
        unique_entities = pd.concat([first_set['Reporter'], second_set['Assigned To']]).dropna().unique()
        selected_entity = st.selectbox("Select an entity:", unique_entities)

        start_date = st.date_input("Start Date")
        end_date = st.date_input("End Date")

        if start_date and end_date and selected_entity:
            total_days = np.busday_count(start_date, end_date + timedelta(days=1))
            total_work_hours = total_days * 8

            resolved_tickets_assigned_count = second_set[second_set['Assigned To'] == selected_entity]['Status.1'].apply(categorize_status).value_counts().get('resolved', 0)
            resolved_tickets_reported_count = first_set[first_set['Reporter'] == selected_entity]['Status'].apply(categorize_status).value_counts().get('resolved', 0)

            average_hours_per_assigned = total_work_hours / resolved_tickets_assigned_count / 8 if resolved_tickets_assigned_count else 0
            average_hours_per_reported = total_work_hours / resolved_tickets_reported_count / 8 if resolved_tickets_reported_count else 0

            assigned_categorized_statuses = second_set[second_set['Assigned To'] == selected_entity]['Status.1'].apply(categorize_status)
            assigned_status_counts = assigned_categorized_statuses.value_counts()
            assigned_total = assigned_status_counts.sum()
            assigned_status_counts.loc['Total'] = assigned_total
            assigned_table = add_percentage_column(assigned_status_counts, assigned_total)
            st.write(f"Status counts for tickets assigned to {selected_entity}:")
            st.table(assigned_table)

            reported_categorized_statuses = first_set[first_set['Reporter'] == selected_entity]['Status'].apply(categorize_status)
            reported_status_counts = reported_categorized_statuses.value_counts()
            reported_total = reported_status_counts.sum()
            reported_status_counts.loc['Total'] = reported_total
            reported_table = add_percentage_column(reported_status_counts, reported_total)
            st.write(f"Status counts for tickets reported by {selected_entity}:")
            st.table(reported_table)

            if st.button("Save Analysis to CSV"):
                save_to_csv(start_date, end_date, selected_entity, assigned_table, reported_table, average_hours_per_assigned, average_hours_per_reported, total_work_hours)

if __name__ == "__main__":
    main()