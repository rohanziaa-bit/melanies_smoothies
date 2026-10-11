# Import python packages
import streamlit as st
from snowflake.snowpark.functions import col
import requests

# Write directly to the app
st.title(f"Customize Your smoothie :balloon: {st.__version__}")
st.write(
    """Replace this example with your own code!
    **And if you're new to Streamlit,** check
    out our easy-to-follow guides at
    [docs.streamlit.io](https://docs.streamlit.io).
    """
)

name_on_order = st.text_input('Name on Smoothies')
st.write('The name on your Smoothies will be', name_on_order)

# Connect to Snowflake using standard Streamlit connection
cnx = st.connection("snowflake")
session = cnx.session()

my_dataframe = session.table("smoothies.public.fruit_options").select(col('FRUIT_NAME'))
#st.dataframe(data=my_dataframe, use_container_width=True)

ingredients_list = st.multiselect(
    'Choose up to 5 ingredients:',
    my_dataframe
)

if ingredients_list:
    ingredients_string = ''

    for fruit_chosen in ingredients_list:
        ingredients_string += fruit_chosen + ' '
        st.subheader(fruit_chosen + 'Nutrition information')
        # Display nutrition information safely for each selected fruit
        st.subheader(fruit_chosen + ' Nutrition Information')
        smoothiefroot_response = requests.get(f"https://my.smoothiefroot.com/api/fruit/{fruit_chosen}")
        
        if smoothiefroot_response.status_code == 200:
            try:
                st.dataframe(data=smoothiefroot_response.json(), use_container_width=True)
            except requests.exceptions.JSONDecodeError:
                st.error(f"Could not load nutrition data for {fruit_chosen} (Invalid JSON format).")
        else:
            st.warning(f"Could not fetch data for {fruit_chosen}. API status code: {smoothiefroot_response.status_code}")

    my_insert_stmt = """INSERT INTO smoothies.public.orders
                        (ingredients, name_on_order)
                        VALUES ('""" + ingredients_string + """', '""" + name_on_order + """')"""

    # st.write(my_insert_stmt)

    time_to_insert = st.button('Submit Order')

    if time_to_insert:
        session.sql(my_insert_stmt).collect()
        st.success('Your Smoothie is ordered! ✅')
