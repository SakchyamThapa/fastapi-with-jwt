import streamlit as st


st.write("DEBUG: Streamlit is running!")
st.write("DEBUG: Session state:", st.session_state)

st.title("Test Page")
st.success("If you can see this, Streamlit is working!")

if st.button("Test Button"):
    st.balloons()
    st.write("Button clicked!")