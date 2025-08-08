import streamlit as st
import requests
import json
import pandas as pd
import time

# --- API Functions ---

def get_message_templates(token, waba_id):
    """
    Fetches message templates from the WhatsApp Business Account.

    Args:
        token (str): Your WhatsApp Business API token.
        waba_id (str): Your WhatsApp Business Account ID.

    Returns:
        list: A list of template names, or an empty list if an error occurs.
    """
    url = f"https://graph.facebook.com/v23.0/{waba_id}/message_templates"
    headers = {"Authorization": f"Bearer {token}"}
    params = {'fields': 'name,status'}
    try:
        response = requests.get(url, headers=headers, params=params)
        response.raise_for_status()
        templates = response.json().get("data", [])
        # Filter for templates that are approved
        approved_templates = [t['name'] for t in templates if t.get('status') == 'APPROVED']
        return approved_templates
    except requests.exceptions.RequestException as e:
        st.error(f"Error fetching templates: {e}")
        return []
    except Exception as e:
        st.error(f"An unexpected error occurred: {e}")
        st.json(response.json()) # Show the raw error from Meta
        return []


def send_template_message(token, phone_id, to_phone_number, template_name, variables):
    """
    Sends a WhatsApp template message using the Meta Graph API.

    Args:
        token (str): Your WhatsApp Business API token.
        phone_id (str): Your WhatsApp Business phone number ID.
        to_phone_number (str): The recipient's phone number.
        template_name (str): The name of the template to send.
        variables (list): A list of strings for the template's variables.

    Returns:
        dict: The JSON response from the API.
    """
    url = f"https://graph.facebook.com/v19.0/{phone_id}/messages"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
    }
    
    components = []
    if variables:
        parameters = [{"type": "text", "text": var} for var in variables]
        components.append({"type": "body", "parameters": parameters})

    data = {
        "messaging_product": "whatsapp",
        "to": to_phone_number,
        "type": "template",
        "template": {
            "name": template_name,
            "language": {"code": "en_US"}, # Assuming en_US, can be made dynamic
            "components": components
        },
    }
    try:
        response = requests.post(url, headers=headers, data=json.dumps(data))
        response.raise_for_status()
        return {"success": True, "data": response.json()}
    except requests.exceptions.RequestException as e:
        return {"success": False, "error": str(e), "details": response.json()}


# --- Streamlit App UI ---
st.set_page_config(page_title="WhatsApp Bulk Sender", layout="wide")

st.title("📱 WhatsApp Business API Bulk Sender")
st.markdown(
    "This app allows you to send approved message templates to a list of contacts from a CSV file."
)

# --- Sidebar for Credentials ---
st.sidebar.header("API Credentials")
st.sidebar.markdown(
    "Enter your WhatsApp Business API credentials from your Meta for Developers account."
)

api_token = st.sidebar.text_input(
    "API Token", type="password", help="Your temporary or permanent access token."
)
phone_number_id = st.sidebar.text_input(
    "Phone Number ID", help="The ID of the phone number you are sending from."
)
waba_id = st.sidebar.text_input(
    "WhatsApp Business Account ID (WABA ID)", help="The ID of your WhatsApp Business Account."
)

# Initialize session state
if 'templates' not in st.session_state:
    st.session_state.templates = []
if 'df_for_editing' not in st.session_state:
    st.session_state.df_for_editing = pd.DataFrame()


# --- Main App Layout ---
col1, col2 = st.columns(2)

with col1:
    st.header("1. Select Template")
    if st.button("Fetch Approved Templates"):
        if api_token and waba_id:
            with st.spinner("Fetching templates..."):
                st.session_state.templates = get_message_templates(api_token, waba_id)
            if not st.session_state.templates:
                st.warning("No approved templates found or there was an error.")
        else:
            st.error("Please provide API Token and WABA ID in the sidebar to fetch templates.")

    if st.session_state.templates:
        selected_template = st.selectbox(
            "Choose a template", options=st.session_state.templates
        )

        st.subheader("Template Variables")
        st.info("Enter each variable on a new line. These variables will be the same for all selected recipients.")
        template_variables_input = st.text_area(
            "Body Variables (one per line)", 
            height=100,
            placeholder="Variable 1\nVariable 2\n..."
        )
    else:
        st.info("Click 'Fetch Approved Templates' to load your message templates.")

with col2:
    st.header("2. Select Recipients")
    uploaded_file = st.file_uploader("Upload a CSV file with contacts", type="csv")

    if uploaded_file:
        try:
            # If a new file is uploaded, read it and add the 'Send' column
            if st.session_state.get('uploaded_filename') != uploaded_file.name:
                df = pd.read_csv(uploaded_file)
                st.session_state.uploaded_filename = uploaded_file.name
                df.insert(0, 'Send', True) # Insert 'Send' column at the beginning
                st.session_state.df_for_editing = df
        except Exception as e:
            st.error(f"Error reading CSV file: {e}")
            # Clear state on error
            st.session_state.df_for_editing = pd.DataFrame()

    if not st.session_state.df_for_editing.empty:
        df_to_edit = st.session_state.df_for_editing
        st.subheader("Confirm Recipients")
        
        # Let user select the phone number column from the uploaded file's columns
        phone_col = st.selectbox(
            "Which column has the phone numbers?",
            [col for col in df_to_edit.columns if col != 'Send'] # Exclude 'Send' column
        )

        st.info("Uncheck the 'Send' box for any contacts you want to exclude.")
        # The data editor shows the full dataframe with the 'Send' checkbox column
        edited_df = st.data_editor(
            df_to_edit,
            key="editor",
            use_container_width=True,
            hide_index=True,
        )
        
        # Add the visual warning for selection limit
        num_selected = edited_df['Send'].sum()
        if num_selected > 250:
            st.warning(f"⚠️ You have selected {num_selected} recipients. The maximum allowed is 250.")


# --- Send Button and Logic ---
st.header("3. Send Messages")
if st.button("Send to Selected Recipients", type="primary"):
    if 'selected_template' not in locals():
        st.warning("Please select a template first.")
    elif 'edited_df' not in locals() or edited_df.empty:
        st.warning("Please upload a CSV and select recipients.")
    elif 'phone_col' not in locals() or not phone_col:
         st.warning("Please select the column containing phone numbers.")
    else:
        # Filter the dataframe for rows where 'Send' is True
        recipients_to_send = edited_df[edited_df['Send'] == True]
        
        # Add the restriction check before sending
        if len(recipients_to_send) > 250:
            st.error(f"Message not sent. You have selected {len(recipients_to_send)} recipients, but the maximum is 250. Please deselect some recipients and try again.")
        else:
            # Get the phone numbers from the user-specified column
            phone_numbers = recipients_to_send[phone_col].tolist()
            
            variables = [var.strip() for var in template_variables_input.split('\n') if var.strip()]
            
            if not phone_numbers:
                st.warning("No recipients selected. Please check the 'Send' box for at least one contact.")
            else:
                total_recipients = len(phone_numbers)
                st.info(f"Preparing to send '{selected_template}' to {total_recipients} recipient(s)...")
                
                progress_bar = st.progress(0)
                results = []
                
                for i, number in enumerate(phone_numbers):
                    with st.spinner(f"Sending to {number}... ({i+1}/{total_recipients})"):
                        response = send_template_message(
                            api_token, phone_number_id, str(number), selected_template, variables
                        )
                        results.append({"phone_number": number, "response": response})
                    progress_bar.progress((i + 1) / total_recipients)
                
                st.header("Sending Complete: Results")
                
                success_count = sum(1 for r in results if r['response']['success'])
                st.success(f"Successfully sent messages: {success_count}/{total_recipients}")
                
                failed_messages = [r for r in results if not r['response']['success']]
                if failed_messages:
                    st.error(f"Failed to send messages: {len(failed_messages)}/{total_recipients}")
                    with st.expander("View Failed Message Details"):
                        for failed in failed_messages:
                            st.write(f"**Phone:** {failed['phone_number']}")
                            st.json(failed['response'])

st.markdown(
    """
---
**Disclaimer:** This is a simple UI wrapper and is not affiliated with Meta.
Ensure you comply with WhatsApp's Business Messaging Policy.
"""
)