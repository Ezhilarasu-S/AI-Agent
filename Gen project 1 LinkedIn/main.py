import streamlit as st
from few_shot import FewShotPosts
from post_generator import generate_post

# How to run this come mean open terminal type streamlit run main.py

length_options = ["Short", "Medium", "Long"]
language_options = ["English"]

def main():
    st.title("LinkedIn Post Generator")

    # Instantiate the FewShotPosts class
    fs = FewShotPosts()

    col1, col2, col3 = st.columns(3)
    with col1:
        select_language= st.selectbox("Title", options=list(fs.get_tags()))  # Properly call get_tags()
    with col2:
        select_length = st.selectbox("Length", options=length_options)
    with col3:
        select_language = st.selectbox("Language", options=language_options)

    if st.button("Generate"):
        post = generate_post(select_length, select_language, select_language)
        # Simulate generating a post
        st.write(post)

if __name__ == "__main__":
    main()
