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

my_dataframe = session.table("smoothies.public.fruit_options").select(col('FRUIT_NAME'), col('SEARCH_ON'))
#st.dataframe(data=my_dataframe, use_container_width=True)
#st.stop()

#convert the snowpark dataframe to a pandas dataframe so we use the loc function
pd_df=my_dataframe.to_pandas()
st.dataframe(pd_df)
st.stop

# Convert Snowpark DataFrame to Pandas DataFrame so we can use loc
pd_df = my_dataframe.to_pandas()

ingredients_list = st.multiselect(
    'Choose up to 5 ingredients:',
    pd_df['FRUIT_NAME']
)

if ingredients_list:
    ingredients_string = ''

    for fruit_chosen in ingredients_list:
        ingredients_string += fruit_chosen + ' '
        
        # SEARCH_ON column se search value nikalna
        search_on = pd_df.loc[pd_df['FRUIT_NAME'] == fruit_chosen, 'SEARCH_ON'].iloc[0]
        st.write(f'The search value for {fruit_chosen} is {search_on}.')
        
        # Display nutrition information safely for each selected fruit
        st.subheader(fruit_chosen + ' Nutrition Information')
        smoothiefroot_response = requests.get(f"https://my.smoothiefroot.com/api/fruit/{search_on}")
        
        if smoothiefroot_response.status_code == 200:
            try:
                st.dataframe(data=smoothiefroot_response.json(), use_container_width=True)
            except requests.exceptions.JSONDecodeError:
                st.error(f"Could not load nutrition data for {fruit_chosen} (Invalid JSON format).")
        else:
            st.warning(f"Could not fetch data for {fruit_chosen}. API status code: {smoothiefroot_response.status_code}")

    safe_ingredients = ingredients_string.replace("'", "''")
    safe_name = name_on_order.replace("'", "''")

    my_insert_stmt = f"""INSERT INTO smoothies.public.orders (ingredients, name_on_order) 
                        VALUES ('{safe_ingredients}', '{safe_name}')"""

    time_to_insert = st.button('Submit Order')

    if time_to_insert:
        session.sql(my_insert_stmt).collect()
        st.success('Your Smoothie is ordered! ✅')
