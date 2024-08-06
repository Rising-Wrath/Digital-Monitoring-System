import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# Sample data
data = {
    'Subject': ['Data Structures', 'Operating Systems', 'Database Management Systems', 'Computer Networkss'],
    'Attendance': [25, 25, 23, 10],
    'Avg_Attendance': [24, 15, 22, 21],
    'Total_Class': [30, 30, 25, 22]
}

# Create a DataFrame
df = pd.DataFrame(data)

# Streamlit app
st.title('Semester 1 Attendance')
 # Table
st.subheader('Data Table')
st.table(df)

col1,col2=st.columns(2)

with col1:

    # Line chart
    st.subheader('Line Chart')
    fig, ax = plt.subplots()
    ax.plot(df['Subject'], df['Attendance'], label='Attendance', marker='o', color='cyan')
    ax.plot(df['Subject'], df['Avg_Attendance'], label='Avg. Attendance', marker='o', color='orange')
    ax.plot(df['Subject'], df['Total_Class'], label='Total Class', marker='o', color='green')
    for i, txt in enumerate(df['Attendance']):
        ax.annotate(txt, (df['Subject'][i], df['Attendance'][i]), color='cyan')
    for i, txt in enumerate(df['Avg_Attendance']):
        ax.annotate(txt, (df['Subject'][i], df['Avg_Attendance'][i]), color='orange')
    for i, txt in enumerate(df['Total_Class']):
        ax.annotate(txt, (df['Subject'][i], df['Total_Class'][i]), color='green')
    ax.set_facecolor("none")
    fig.patch.set_alpha(0.0)
    ax.legend()
    ax.set_title('Semester 1', color='white')
    ax.tick_params(colors='white')
    ax.yaxis.label.set_color('white')
    ax.xaxis.label.set_color('white')
    for spine in ax.spines.values():
        spine.set_edgecolor('white')
    st.pyplot(fig)

with col2:
    # Bar chart
    st.subheader('Bar Chart')
    fig, ax = plt.subplots()
    bar_width = 0.35
    index = np.arange(len(df))
    bar1 = ax.bar(index, df['Attendance'], bar_width, label='Attendance', color='cyan')
    bar2 = ax.bar(index, df['Avg_Attendance'], bar_width, bottom=df['Attendance'], label='Avg. Attendance', color='orange')
    for i, txt in enumerate(df['Attendance']):
        ax.annotate(txt, (index[i], df['Attendance'][i] / 2), ha='center', va='center', color='black')
    for i, txt in enumerate(df['Avg_Attendance']):
        ax.annotate(txt, (index[i], df['Attendance'][i] + df['Avg_Attendance'][i] / 2), ha='center', va='center', color='black')
    ax.set_facecolor("none")
    fig.patch.set_alpha(0.0)
    ax.set_xticks(index)
    ax.set_xticklabels(df['Subject'], color='white')
    ax.legend()
    ax.set_title('Semester 1', color='white')
    ax.tick_params(colors='white')
    for spine in ax.spines.values():
        spine.set_edgecolor('white')
    st.pyplot(fig)





col1,col2=st.columns(2)
with col1:
    # Combined bar chart
    st.subheader('Combined Bar Chart')
    fig, ax = plt.subplots()
    bar_width = 0.2
    index = np.arange(len(df))
    
    # Plotting the bars
    bar1 = ax.bar(index - bar_width, df['Attendance'], bar_width, label='Attendance', color='cyan')
    bar2 = ax.bar(index, df['Avg_Attendance'], bar_width, label='Avg. Attendance', color='orange')
    bar3 = ax.bar(index + bar_width, df['Total_Class'], bar_width, label='Total Class', color='green')
    
    # Adding text labels on the bars
    for i in range(len(df)):
        ax.annotate(df['Attendance'][i], (index[i] - bar_width, df['Attendance'][i] + 0.5), ha='center', color='white')
        ax.annotate(df['Avg_Attendance'][i], (index[i], df['Avg_Attendance'][i] + 0.5), ha='center', color='white')
        ax.annotate(df['Total_Class'][i], (index[i] + bar_width, df['Total_Class'][i] + 0.5), ha='center', color='white')
    
    # Customizing the appearance
    ax.set_facecolor("none")
    fig.patch.set_alpha(0.0)
    ax.set_xticks(index)
    ax.set_xticklabels(df['Subject'], color='white')
    ax.legend()
    ax.set_title('Semester 1 Combined', color='white')
    ax.tick_params(colors='white')
    for spine in ax.spines.values():
        spine.set_edgecolor('white')
    
    st.pyplot(fig)    
      
   
    
with col2:
       # Pie chart
       st.subheader('Pie Chart')
       pie_labels = df['Subject']
       pie_sizes = df['Attendance']
       fig, ax = plt.subplots()
       ax.pie(pie_sizes, labels=pie_labels, autopct='%1.1f%%', startangle=140, textprops={'color':'white'})
       ax.set_facecolor("none")
       fig.patch.set_alpha(0.0)
       ax.set_title('Attendance Distribution', color='white')
       st.pyplot(fig)
       