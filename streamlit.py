import streamlit as st
import requests
import json

# Base API URL
BASE_URL = "http://127.0.0.1:8000/api/v1"

def add_new_user():
    st.header("Add New User")
    with st.form("new_user_form"):
        user_id = st.text_input("User ID")
        interests_str = st.text_input("Interests (comma separated)")
        preferences_str = st.text_area("Preferences (JSON format)", value="{}")
        demographics_str = st.text_area("Demographics (JSON format)", value="{}")
        submit_button = st.form_submit_button("Submit")
    
    if submit_button:
        try:
            interests = [i.strip() for i in interests_str.split(",")] if interests_str else []
            preferences = json.loads(preferences_str)
            demographics = json.loads(demographics_str)
            
            payload = {
                "user_id": user_id,
                "interests": interests,
                "preferences": preferences,
                "demographics": demographics
            }
            
            response = requests.post(f"{BASE_URL}/user/user-details", json=payload)
            if response.status_code in [200, 201]:
                st.success("User added successfully!")
                st.json(response.json())
            else:
                st.error(f"Error: {response.status_code} - {response.text}")
        except Exception as e:
            st.error(f"An error occurred: {e}")

def get_recommendation():
    st.header("Get Recommendation")
    user_id = st.text_input("Enter User ID for Recommendation", key="rec_user_id")
    if st.button("Get Recommendation"):
        try:
            response = requests.get(f"{BASE_URL}/recommendation/recommendations/?user_id={user_id}")
            if response.status_code == 200:
                data = response.json()
                
                # Display Jobs simply as text
                st.subheader("Jobs")
                jobs = data.get("Jobs", {})
                if jobs:
                    for job_key, job in jobs.items():
                        st.write(f"Job Title: {job['job_title']}")
                        st.write(f"Company: {job['company_name']}")
                        st.write(f"Posted Date: {job['posted_date']}")
                        st.write(f"Industry: {job['industry']}")
                        st.write(f"Final Score: {job['final_score']}")
                        st.write("---")
                else:
                    st.write("No jobs available.")

                # Display News simply as text
                st.subheader("News")
                news = data.get("News", {})
                if news:
                    for news_key, item in news.items():
                        st.write(f"Title: {item['title']}")
                        st.write(f"Published Date: {item['published_date']}")
                        st.write(f"Source: {item['source']}")
                        st.write(f"Score: {item['final_score']}")
                        st.write(f"URL: {item['url']}")
                        st.write("---")
                else:
                    st.write("No news available.")
            else:
                st.error(f"Error: {response.status_code} - {response.text}")
        except Exception as e:
            st.error(f"An error occurred: {e}")

def main():
    st.title("User and Recommendation App")
    tab1, tab2 = st.tabs(["Add New User", "Get Recommendation"])
    
    with tab1:
        add_new_user()
    with tab2:
        get_recommendation()

if __name__ == "__main__":
    main()
