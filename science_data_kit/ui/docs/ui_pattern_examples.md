# UI Pattern Examples

This document provides examples of how to use the standardized UI patterns in the Science Data Kit application.

## UI Constants

The `ui_constants.py` file provides standardized constants for colors, typography, and spacing.

```python
from science_data_kit.ui.components.ui_constants import *

# Use color constants
st.markdown(f'<div style="color: {COLOR_PRIMARY};">Primary Color Text</div>', unsafe_allow_html=True)

# Use typography constants
st.markdown(f'<div style="font-size: {FONT_SIZE_16}px; font-family: {FONT_FAMILY_SANS_SERIF};">Styled Text</div>', unsafe_allow_html=True)

# Use spacing constants
st.markdown(f'<div style="padding: {PADDING_10}px; margin: {MARGIN_20}px;">Spaced Content</div>', unsafe_allow_html=True)
```

## Button Templates

The `button_templates.py` file provides standardized button templates.

```python
from science_data_kit.ui.components.templates.button_templates import *

# Primary button
if primary_button('Save', key='save_button', help='Save the current data'):
    st.success('Data saved!')

# Secondary button
if secondary_button('Cancel', key='cancel_button'):
    st.warning('Operation cancelled')

# Danger button
if danger_button('Delete', key='delete_button', help='Delete the current data'):
    st.error('Data deleted!')

# Full-width button
if full_width_button('Submit', key='submit_button'):
    st.success('Form submitted!')
```

## Input Templates

The `input_templates.py` file provides standardized input templates.

```python
from science_data_kit.ui.components.templates.input_templates import *

# Text input
name = standard_text_input('Name', placeholder='Enter your name', key='name_input')

# Number input
age = standard_number_input('Age', min_value=0, max_value=120, value=30, key='age_input')

# Selectbox
option = standard_selectbox('Select an option', options=['Option 1', 'Option 2', 'Option 3'], key='option_select')

# File uploader
uploaded_file = standard_file_uploader('Upload a file', type=['csv', 'xlsx'], key='file_upload')
```

## Visualization Templates

The `visualization_templates.py` file provides standardized visualization templates.

```python
from science_data_kit.ui.components.templates.visualization_templates import *
import pandas as pd

# Create sample data
data = pd.DataFrame({
    'Category': ['A', 'B', 'C', 'D', 'E'],
    'Value': [10, 25, 15, 30, 20],
    'Value2': [5, 15, 10, 20, 25]
})

# Bar chart
bar_chart_img = standard_bar_chart(
    data=data,
    x_column='Category',
    y_column='Value',
    title='Sample Bar Chart',
    show_values=True
)
st.image(f'data:image/png;base64,{bar_chart_img}')

# Line chart
line_chart_img = standard_line_chart(
    data=data,
    x_column='Category',
    y_columns=['Value', 'Value2'],
    title='Sample Line Chart',
    show_markers=True
)
st.image(f'data:image/png;base64,{line_chart_img}')

# Scatter plot
scatter_plot_img = standard_scatter_plot(
    data=data,
    x_column='Value',
    y_column='Value2',
    title='Sample Scatter Plot'
)
st.image(f'data:image/png;base64,{scatter_plot_img}')
```

## Layout Templates

The `layout_templates.py` file provides standardized layout templates.

```python
from science_data_kit.ui.components.templates.layout_templates import *

# Page header
page_header('Dashboard', subtitle='Overview of key metrics', icon='📊')

# Section header
section_header('Data Analysis', description='Analysis of the imported data', level=2)

# Two-column layout
def left_column():
    st.write('Left column content')

def right_column():
    st.write('Right column content')

two_column_layout(left_column, right_column)

# Three-column layout
def middle_column():
    st.write('Middle column content')

three_column_layout(left_column, middle_column, right_column)

# Card
def card_content():
    st.write('Card content')

card('Sample Card', card_content)

# Tabs layout
def tab1_content():
    st.write('Tab 1 content')

def tab2_content():
    st.write('Tab 2 content')

tabs_layout({
    'Tab 1': tab1_content,
    'Tab 2': tab2_content
})
```