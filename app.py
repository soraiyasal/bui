import streamlit as st
import pandas as pd
from bs4 import BeautifulSoup
import re

# Define the allowed Baitul Ilm locations for filtering
# allowed_baitul_ilm = [
#     "Central London", "West London", "East London", "North London", "Northwest", "Reading", "South London",
#     "Birmingham", "Leicester", "Dublin", "BAI Online (Saturday)", "BAI Online (Sunday)", "Aga Khan Centre",
#     "Leeds / Bradford", "Manchester",     "Farsi Online BAI 1 - GC",
#     "Farsi Online BAI 2 - GC",
#     "Farsi Online BAI 1 - GC",
#     "Farsi Online BAI 4 - GC",
#     "Frankfurt",
#     "Essen",
#     "Frankfurt",
#     "Farsi Online BAI 4 - GC",
#     "Frankfurt",
#     "Farsi Online BAI 1 - GC",
#     "Munich",
#     "Frankfurt",
#     "Farsi Online BAI 3 - GC",
#     "Farsi Online BAI 2 - GC",
#     "Hamburg",
#     "Berlin"
# ]

allowed_baitul_ilm = [
    "Dublin",
    "West London",
    "Central London",
    "North London",
    "Northwest London",
    "East London",
    "BAI Online (Saturday)",
    "South London",
    "Birmingham",
    "Leeds/Bradford",
    "Leicester",
    "Manchester",
    "Reading",
    "BAI Online (Sunday)",
    "Aga Khan Centre"
]


# Define specific rows to exclude based on Baitul Ilm, Area, and Class Name
# excluded_rows = [
#     ("Aga Khan Centre", "London", "Secondary 1"),
#     ("Central London", "London", "Secondary 2"),
#     ("Dublin", "Region", "Secondary 1"),
#     ("Reading", "Region", "Secondary 3"),
#     ("Reading", "Region", "Secondary 4")
# ]

excluded_rows = [

]
 

# Helper function to calculate attendance and rates for any number of weeks
def attendance_per_week(chd_data, total_students):
    attendance_values = chd_data.split(",")
    week_columns = [int(value) if value.isdigit() else 0 for value in attendance_values]
    rates = [(week / total_students) * 100 if total_students > 0 else 0 for week in week_columns]
    return week_columns, rates

# Streamlit App UI
st.title("HTML File Upload and Processing App")
st.write("Upload an HTML file to parse, filter, and display attendance data.")

uploaded_file = st.file_uploader("Choose an HTML file", type=["html"])

if uploaded_file:
    content = uploaded_file.read().decode("utf-8")
    soup = BeautifulSoup(content, "html.parser")
    
    attendance_w_results = []

    # Find all the rows in the HTML table
    rows = soup.find_all("tr")

    for row in rows:
        img = row.find("img")
        if img and "quickchart.io" in img["src"]:
            chart_url = img["src"]
            chd_match = re.search(r"chd=t:([0-9,]+)", chart_url)
            if chd_match:
                chd_data = chd_match.group(1)

                # Extract the number of students from the correct column (usually column 6 or 7)
                cells = row.find_all("td")
                total_students = int(cells[6].get_text(strip=True)) if len(cells) > 6 and cells[6].get_text(strip=True).isdigit() else None

                if total_students and total_students > 0:
                    week_data, rates = attendance_per_week(chd_data, total_students)
                else:
                    week_data = [0] * len(chd_data.split(","))
                    rates = [0] * len(chd_data.split(","))

                class_name = cells[2].get_text(strip=True) if len(cells) > 2 else "Unknown Class"
                baitul_ilm = cells[0].get_text(strip=True) if len(cells) > 0 else "Unknown"
                area = cells[1].get_text(strip=True) if len(cells) > 1 else "Unknown"
                
                # Apply Filtering
                if (
                    "Secondary" in class_name and 
                    baitul_ilm in allowed_baitul_ilm and 
                    (baitul_ilm, area, class_name) not in excluded_rows
                ):
                    attendance_w_results.append(
                        (baitul_ilm, area, class_name, total_students if total_students else 0) + tuple(week_data) + tuple(rates)
                    )

    # Generate column names dynamically
    if attendance_w_results:
        num_weeks = len(attendance_w_results[0]) - 4
        week_columns = [f"W{i+1} Attendance" for i in range(num_weeks // 2)]
        rate_columns = [f"W{i+1} Attendance Rate (%)" for i in range(num_weeks // 2)]
        columns = ["Baitul Ilm", "Area", "Class Name", "Total Students"] + week_columns + rate_columns

        # Create DataFrame
        df = pd.DataFrame(attendance_w_results, columns=columns)
        
        st.write("### Filtered Attendance Data")
        st.dataframe(df)

        # Download button for CSV
        csv = df.to_csv(index=False).encode("utf-8")
        st.download_button("Download CSV", csv, "attendance_summary_filtered.csv", "text/csv")
    else:
        st.write("No valid attendance data found.")
