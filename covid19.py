import COVID19Py
import pandas as pd
import streamlit as st
import json
import numpy as np
import altair as alt

@st.cache
def get_covid19data():
    covid19 = COVID19Py.COVID19()
    locations = covid19.getLocations()
    
    dfItem = pd.DataFrame.from_records(locations)
    df_1 = pd.json_normalize(dfItem.latest).add_prefix('latest')
    df_2 = pd.json_normalize(dfItem.coordinates).add_prefix('Coordinates.')
    
    result = pd.concat([dfItem, df_1,df_2], axis=1)
    result.sort_values(['latestconfirmed'], inplace=True, ascending=False)
    
    return result
    


st.title('COVID19 data using JHU/covid19py')

# Create a text element and let the reader know the data is loading.
data_load_state = st.text('Loading data...')
# Load data into the dataframe.
data = get_covid19data()

# Notify the reader that the data was successfully loaded.
data_load_state.text("Done! (using st.cache)")


#st.subheader('raw data by country')

#st.write(data)

if st.checkbox('Show raw data'):
    st.subheader('Raw data by country')
    st.write(data)

st.subheader('Population chart by country')

st.write(alt.Chart(data).mark_bar().encode(
    x=alt.X('country', sort=None),
    y='country_population',
))

st.subheader('Latest Confirmed cases chart by country')

st.write(alt.Chart(data).mark_bar().encode(
    x=alt.X('country', sort=None),
    y='latestconfirmed',
))

# Create a list of possible values and multiselect menu with them in it.
COUNTRIES = data['country'].unique()
COUNTRIES_SELECTED = st.multiselect('Select countries', COUNTRIES)

# Mask to filter dataframe
mask_countries = data['country'].isin(COUNTRIES_SELECTED)

data = data[mask_countries]

st.write(alt.Chart(data).mark_bar().encode(
    x=alt.X('country', sort=None),
    y='latestconfirmed',
))