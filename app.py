import streamlit as st
import pandas as pd
import numpy as np
from scipy.stats import norm
import plotly.graph_objects as go
import plotly.express as px

# Set page config
st.set_page_config(page_title="Life Expectancy Calculator", layout="wide")

def calculate_life_expectancy(age, sex, bmi_status, smoker, diabetes, heart_disease, cancer_history, exercise_level):
    # Base remaining life expectancy from CDC life tables (2021 data)
    # These are approximate values based on remaining years of life
    base_remaining_years = {
        'Male': {
            range(0, 20): 76,
            range(20, 30): 57,
            range(30, 40): 47,
            range(40, 50): 38,
            range(50, 60): 29,
            range(60, 70): 21,
            range(70, 80): 14,
            range(80, 90): 8,
            range(90, 101): 4,
        },
        'Female': {
            range(0, 20): 81,
            range(20, 30): 62,
            range(30, 40): 52,
            range(40, 50): 42,
            range(50, 60): 33,
            range(60, 70): 24,
            range(70, 80): 16,
            range(80, 90): 9,
            range(90, 101): 5,
        }
    }
    
    # Find the appropriate age range and get base remaining years
    base_remaining = 0
    for age_range, years in base_remaining_years[sex].items():
        if age in age_range:
            base_remaining = years
            break
    
    # Calculate risk factor adjustments
    # Adjustments become smaller with age to reflect diminishing impact
    age_factor = max(0.2, 1 - (age / 100))  # Reduces impact of factors with age
    
    adjustments = 0
    
    # BMI status impact
    if bmi_status == "Overweight (BMI 25-29.9)":
        adjustments -= 1 * age_factor
    elif bmi_status == "Obese (BMI 30+)":
        adjustments -= 3 * age_factor
        
    # Smoking impact
    if smoker == "Current smoker":
        adjustments -= 10 * age_factor
    elif smoker == "Former smoker":
        adjustments -= 3 * age_factor
        
    # Health conditions
    if diabetes:
        adjustments -= 7.5 * age_factor
    if heart_disease:
        adjustments -= 8 * age_factor
    if cancer_history:
        adjustments -= 5 * age_factor
        
    # Exercise impact
    if exercise_level == "Moderate (1-2 times/week)":
        adjustments += 2 * age_factor
    elif exercise_level == "Active (3+ times/week)":
        adjustments += 4 * age_factor
        
    # Calculate final life expectancy
    life_expectancy = age + max(1, base_remaining + adjustments)
    
    # Standard deviation varies with age and remaining life expectancy
    std_dev = max(1, (life_expectancy - age) * 0.15)
    
    return life_expectancy, std_dev

def generate_death_causes(age, sex):
    # More detailed causes of death by age group (CDC data)
    if age < 25:
        causes = {
            "Accidents": 40,
            "Suicide": 15,
            "Homicide": 15,
            "Cancer": 10,
            "Heart Disease": 5,
            "Other": 15
        }
    elif age < 45:
        causes = {
            "Accidents": 25,
            "Cancer": 20,
            "Heart Disease": 20,
            "Suicide": 10,
            "Liver Disease": 5,
            "Other": 20
        }
    elif age < 65:
        causes = {
            "Cancer": 30,
            "Heart Disease": 25,
            "Accidents": 10,
            "Diabetes": 10,
            "Respiratory Disease": 10,
            "Other": 15
        }
    else:
        causes = {
            "Heart Disease": 30,
            "Cancer": 25,
            "Respiratory Disease": 15,
            "Alzheimer's": 10,
            "Stroke": 10,
            "Other": 10
        }
    
    return causes

def main():
    st.title("Life Expectancy Calculator")
    st.write("Estimate your life expectancy based on various risk factors")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Personal Information")
        age = st.number_input("Current Age", min_value=1, max_value=100, value=30)
        sex = st.selectbox("Sex", ["Male", "Female"])
        bmi_status = st.selectbox(
            "Weight Status",
            ["Normal weight", "Overweight (BMI 25-29.9)", "Obese (BMI 30+)"]
        )
        smoker = st.selectbox(
            "Smoking Status",
            ["Never smoked", "Former smoker", "Current smoker"]
        )
    
    with col2:
        st.subheader("Health Conditions")
        diabetes = st.checkbox("Diabetes")
        heart_disease = st.checkbox("Heart Disease")
        cancer_history = st.checkbox("Cancer History")
        exercise_level = st.selectbox(
            "Exercise Frequency",
            ["Sedentary", "Moderate (1-2 times/week)", "Active (3+ times/week)"]
        )
    
    # Calculate life expectancy
    life_expectancy, std_dev = calculate_life_expectancy(
        age, sex, bmi_status, smoker, diabetes, heart_disease, 
        cancer_history, exercise_level
    )
    
    # Create distribution plot with more careful x-axis range
    x_range = max(20, int(life_expectancy - age))  # Ensure meaningful range
    x = np.linspace(age, age + x_range, 100)
    y = norm.pdf(x, life_expectancy, std_dev)
    
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=x, y=y,
        fill='tozeroy',
        name='Life Expectancy Distribution'
    ))
    fig.update_layout(
        title='Estimated Life Expectancy Distribution',
        xaxis_title='Age',
        yaxis_title='Probability Density',
        showlegend=False,
        xaxis_range=[age, age + x_range]
    )
    
    # Display results
    st.subheader("Results")
    remaining_years = life_expectancy - age
    st.write(f"Current Age: {age}")
    st.write(f"Estimated Years Remaining: {remaining_years:.1f} years")
    st.write(f"Estimated Life Expectancy: {life_expectancy:.1f} years")
    st.write(f"95% Confidence Interval: {life_expectancy - 2*std_dev:.1f} to {life_expectancy + 2*std_dev:.1f} years")
    
    st.plotly_chart(fig)
    
    # Display causes of death
    st.subheader("Leading Causes of Death")
    causes = generate_death_causes(age, sex)
    
    # Create pie chart for causes of death
    fig_causes = px.pie(
        values=list(causes.values()),
        names=list(causes.keys()),
        title='Estimated Leading Causes of Death'
    )
    st.plotly_chart(fig_causes)
    
    # Disclaimer
    st.markdown("""
    **Disclaimer:** This calculator provides rough estimates based on population-level statistics 
    and should not be used for medical decisions. Consult healthcare professionals for 
    personalized medical advice.
    
    **Data Sources:**
    - CDC Life Tables (2021)
    - CDC Leading Causes of Death data
    - Various epidemiological studies on risk factors
    
    **Note:** Life expectancy calculations become less certain with age and multiple health conditions.
    Risk factor impacts are reduced with age to reflect real-world patterns.
    """)

if __name__ == "__main__":
    main()
