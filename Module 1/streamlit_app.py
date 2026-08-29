import os
import json
import streamlit as st


# Connect to Snowflake
conn = st.connection(
    "snowflake",
    ttl=os.getenv("SNOWFLAKE_CONNECTION_TTL")
)

session = conn.session()


def summarize():

    st.header("Call Transcript JSON Summary")

    entered_text = st.text_area(
        "Enter text",
        label_visibility="hidden",
        height=400,
        placeholder="Enter a call transcript to summarize."
    )

    btn_summarize = st.button(
        "Summarize",
        type="primary"
    )

    if entered_text and btn_summarize:

        with st.spinner("Summarizing..."):

            # Prompt for Cortex
            prompt = (
                "Summarize this transcript in less than 200 words. "
                "Return ONLY valid JSON. "
                "Do not include any explanation, introduction, or markdown. "
                "Use exactly these keys: "
                "product_name, defect, summary. "
                "Transcript: "
                + entered_text
            )

            # Call Snowflake Cortex
            cortex_response = session.sql(
                "SELECT SNOWFLAKE.CORTEX.COMPLETE(?, ?) AS response",
                params=["llama3.1-8b", prompt],
            ).collect()[0]["RESPONSE"]

        # Extract and parse JSON
        try:

            start = cortex_response.find("{")
            end = cortex_response.rfind("}") + 1

            if start == -1 or end == 0:
                raise ValueError("No JSON object found")

            json_text = cortex_response[start:end]

            result = json.loads(json_text)

            st.subheader("Summary")
            st.json(result)

        except (json.JSONDecodeError, ValueError):

            st.error("Could not parse the model response as JSON.")

            st.subheader("Raw Cortex Response")
            st.code(cortex_response)


# Sidebar navigation
page_names_to_funcs = {
    "JSON Summary": summarize
}

selected_page = st.sidebar.selectbox(
    "Select",
    page_names_to_funcs.keys()
)

page_names_to_funcs[selected_page]()