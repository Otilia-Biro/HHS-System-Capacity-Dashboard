# -*- coding: utf-8 -*-
import pandas as pd
import streamlit as st
import matplotlib.pyplot as plt

st.set_page_config(page_title="System Capacity & Care Load Analytics Dashboard", layout="wide")

st.title("System Capacity & Care Load Analytics Dashboard")

# ===========================
# Load Dataset
# ===========================
try:
    df = pd.read_csv("cleaned_hhs_dataset.csv")
    st.success("Dataset loaded successfully!")
except FileNotFoundError:
    st.error("ERROR: cleaned_hhs_dataset.csv not found in the project folder.")
    st.stop()  # Stop the app if file not found

# ===========================
# Sidebar Options
# ===========================
st.sidebar.header("Dashboard Options")

numeric_cols = df.select_dtypes(include=['number']).columns.tolist()

# Columns for KPIs and histograms
selected_cols = st.sidebar.multiselect(
    "Select numeric columns for KPIs and plots", numeric_cols, default=numeric_cols
)

# Columns for interactive line/scatter charts
interactive_cols = st.sidebar.multiselect(
    "Select 2-3 numeric columns for interactive chart", numeric_cols, default=numeric_cols[:2]
)

# ===========================
# Key KPIs
# ===========================

st.subheader("Key Metrics")
kpi_cols = selected_cols[:4]  # first 4 columns
kpi_values = {}

for col in kpi_cols:
    kpi_values[col] = {
        "Mean": round(df[col].mean(), 2),
        "Min": df[col].min(),
        "Max": df[col].max(),
        "Sum": df[col].sum()
    }

for col, metrics in kpi_values.items():
    st.metric(label=f"{col} (Mean)", value=metrics["Mean"], delta=f"Min {metrics['Min']}, Max {metrics['Max']}")

st.subheader("Key Insights")
st.write("""
- Most variables show high numeric variance
- Certain metrics dominate total values
- Distribution suggests skew in numeric indicators
""")

# ===========================
# Dataset Preview
# ===========================
st.subheader("Dataset Preview")
st.dataframe(df.head())

# ===========================
# Summary Statistics
# ===========================
st.subheader("Summary Statistics (numeric columns)")
st.write(df[selected_cols].describe())

# ===========================
# Histograms
# ===========================
if selected_cols:
    st.subheader("Histograms for Selected Columns")
    df[selected_cols].hist(figsize=(12, 8))
    st.pyplot(plt)
else:
    st.warning("No numeric columns selected for plotting.")

# ===========================
# Interactive Charts
# ===========================
if len(interactive_cols) >= 2:
    st.subheader("Interactive Line/Scatter Chart")
    x_col = st.selectbox("X-axis", interactive_cols, index=0)
    y_col = st.selectbox("Y-axis", interactive_cols, index=1)

    chart_type = st.radio("Chart Type", ["Line", "Scatter"])

    fig, ax = plt.subplots(figsize=(10, 5))
    if chart_type == "Line":
        ax.plot(df[x_col], df[y_col], marker='o')
        ax.set_xlabel(x_col)
        ax.set_ylabel(y_col)
        ax.set_title(f"Line Chart: {y_col} vs {x_col}")
    else:
        ax.scatter(df[x_col], df[y_col])
        ax.set_xlabel(x_col)
        ax.set_ylabel(y_col)
        ax.set_title(f"Scatter Plot: {y_col} vs {x_col}")

    st.pyplot(fig)

else:
    st.info("Select at least 2 numeric columns for interactive chart.")

# ===========================
# Top & Bottom Values + Outliers
# ===========================
st.subheader("Top & Bottom Values")

for col in selected_cols:
    st.markdown(f"**{col}**")
    top_vals = df[col].nlargest(3)
    bottom_vals = df[col].nsmallest(3)
    st.write("Top 3 values:", top_vals.values)
    st.write("Bottom 3 values:", bottom_vals.values)

# Detect outliers using IQR
st.subheader("Outliers Detection (IQR Method)")
outliers_dict = {}

for col in selected_cols:
    Q1 = df[col].quantile(0.25)
    Q3 = df[col].quantile(0.75)
    IQR = Q3 - Q1
    lower_bound = Q1 - 1.5 * IQR
    upper_bound = Q3 + 1.5 * IQR
    outliers = df[(df[col] < lower_bound) | (df[col] > upper_bound)][col]
    if not outliers.empty:
        outliers_dict[col] = outliers

if outliers_dict:
    for col, values in outliers_dict.items():
        st.markdown(f"**Outliers in {col}**")
        st.write(values.values)
else:
    st.write("No outliers detected in selected numeric columns.")