# --------------------------------------------
# Imports - PyShiny EXPRESS VERSION
# --------------------------------------------

from shiny import reactive, render, req
import plotly.express as px
from shiny.express import input, ui
from shinywidgets import render_plotly
import random
from datetime import datetime
from collections import deque
import pandas as pd
from scipy import stats
from faicons import icon_svg
from pathlib import Path 

# Set the update interval
UPDATE_INTERVAL_SECS = 5
DEQUE_SIZE = 5
reactive_value_wrapper = reactive.value(deque(maxlen=DEQUE_SIZE))

# Load the dataset
tips = px.data.tips()

# Create title
ui.page_opts(title="Tips Dashboard", fillable=True)

# Create sidebar with inputs
with ui.sidebar(open="desktop"):
    ui.h5("Filters")
    
    # Filter for sex
    ui.input_checkbox_group(
        "selected_sex", 
        label="Select Sex", 
        choices=["Male", "Female"], 
        selected=["Male", "Female"], 
        inline=True
    )

    # Filter for smoker or not
    ui.input_checkbox_group(
        "selected_smoker",
        label="Smoker",
        choices=["Yes", "No"],
        selected=["Yes", "No"],
        inline=True
    )

    # Filter for day
    ui.input_checkbox_group(
        "selected_day",
        label="Select Day",
        choices=["Thur", "Fri", "Sat", "Sun"],
        selected=["Thur", "Fri", "Sat", "Sun"],
        inline=True
    )

    # Filter for time
    ui.input_checkbox_group(
        "selected_time",
        label="Select Meal Time",
        choices=["Lunch", "Dinner"],
        selected=["Lunch", "Dinner"],
        inline=True
    )

    # Create a slider for the total bill
    ui.input_slider("total_bill_range", "Total Bill Range", 0, 60, (15,35))

# Main Content
with ui.layout_columns(fill=False):
    with ui.value_box(
        showcase=icon_svg("person"),
        theme="bg-gradient-blue-green"
    ):
        "Total Tippers"

        @render.text
        def total_tippers():
            filtered = filtered_data()
            total_count = len(filtered)
            return f"{total_count} Tippers"

    with ui.value_box(
        showcase=icon_svg("credit-card"),
        theme="bg-gradient-red-orange"
    ):
        "Average Bill Per Table"
        @render.text
        def display_avg_bill():
            _, df, _ = reactive_tips_combined()
            avg_bill = df['avgBill'].mean() if not df.empty else 0

            return f"${avg_bill:.2f}"

    with ui.value_box(
        showcase=icon_svg("dollar-sign"),
        theme="bg-gradient-green-yellow"
    ):
        "Average Tip Per Table"
        @render.text
        def average_tip_pt():
            _, df, _ = reactive_tips_combined()
            avg_tip = df['avgTip'].mean() if not df.empty else 0

            return f"${avg_tip:.2f}"

# Data table and Scatterplot
with ui.layout_columns(fill=False):
    with ui.card():
        "Data Table"
        @render.data_frame
        def tipping_df():
            return filtered_data()

    with ui.card(full_screen=True):
        ui.card_header("Which Sex Tips More?")
        @render_plotly
        def scatterplot_with_regression():
            filtered = filtered_data()
            fig = px.scatter(
                filtered,
                x="tip",
                y="total_bill",
                color="smoker",
                labels={"total_bill": "Total Bill ($)", "tip": "Tip ($)"},
                title="Scatterplot: Total Bill vs Tip"
            )
            return fig

# Reactive calc functions
@reactive.calc()
def filtered_data():
    req(input.selected_sex(), input.selected_smoker(), input.selected_day(), input.selected_time(), input.total_bill_range())

    # Print input values to check if the reactive values are being captured
    print(f"Sex selection: {input.selected_sex}")
    print(f"Smoker selection: {input.selected_smoker}")
    print(f"Day selection: {input.selected_day}")
    print(f"Dining time selection: {input.selected_time}")
    print(f"Total bill range: {input.total_bill_range}")

    # Filter the data based on inputs
    filtered = tips[
        (tips["sex"].isin(input.selected_sex())) &
        (tips["smoker"].isin(input.selected_smoker())) &
        (tips["day"].isin(input.selected_day())) &
        (tips["time"].isin(input.selected_time())) &
        (tips["total_bill"].between(*input.total_bill_range()))
    ]
    return filtered

@reactive.calc()
def reactive_tips_combined():
    reactive.invalidate_later(UPDATE_INTERVAL_SECS)
    avg_tip = round(random.uniform(1, 50), 1)
    avg_bill = round(random.uniform(1, 50), 1)
    timestamp_value = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    new_entry = {"avgTip": avg_tip, "avgBill": avg_bill, "timestamp": timestamp_value}
    reactive_value_wrapper.get().append(new_entry)
    deque_snapshot = reactive_value_wrapper.get()
    df = pd.DataFrame(deque_snapshot)
    return deque_snapshot, df, new_entry