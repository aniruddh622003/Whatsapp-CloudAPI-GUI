# Whatsapp-CloudAPI-GUI 📱

A simple, user-friendly web GUI for the WhatsApp Business Cloud API, built with Streamlit. This tool allows you to send approved template messages in bulk to your contacts by simply uploading a CSV file.

![App Screenshot](https://i.imgur.com/your-screenshot-url.png)
_Replace the URL above with a real screenshot of your application._

---

## ✨ Key Features

- **No Code Required:** Interact with the WhatsApp Cloud API through an easy-to-use graphical interface.
- **Send Template Messages:** Fetch and select from your approved WhatsApp message templates.
- **Bulk Sending via CSV:** Upload a list of contacts in a CSV file to send messages in bulk.
- **Interactive Recipient Selection:** A built-in table with checkboxes lets you easily select and deselect recipients from your uploaded list.
- **Dynamic Variable Support:** Input variables for your templates that will be applied to all outgoing messages.
- **Safe & Secure:** Your API credentials are required for each session and are not stored.
- **Rate Limiting:** A safeguard prevents sending to more than 250 recipients at a time.
- **Real-time Feedback:** View the status of your sent messages with a progress bar and a final report of successes and failures.

---

## 🚀 Getting Started

Follow these instructions to get a copy of the project up and running on your local machine.

### Prerequisites

- Python 3.8+
- A [Meta for Developers](https://developers.facebook.com/) account.
- A WhatsApp Business App set up with access to the Cloud API.

### Installation & Setup

1.  **Clone the repository:**

    ```bash
    git clone [https://github.com/your-username/Whatsapp-CloudAPI-GUI.git](https://github.com/your-username/Whatsapp-CloudAPI-GUI.git)
    cd Whatsapp-CloudAPI-GUI
    ```

2.  **Install the required dependencies:**

    ```bash
    pip install -r requirements.txt
    ```

    _(You will need to create a `requirements.txt` file. See below.)_

3.  **Run the Streamlit app:**
    ```bash
    streamlit run app.py
    ```
    The application will open in a new tab in your default web browser.

### Configuration

To use the application, you will need three credentials from your Meta for Developers App Dashboard:

1.  **API Token:** A temporary or permanent access token.
2.  **Phone Number ID:** The ID for the phone number you are sending messages from.
3.  **WhatsApp Business Account ID (WABA ID):** The ID of your main WhatsApp Business Account.

You can find these in your app's dashboard under **WhatsApp > API Setup**.

---

## 🤝 Contributing

Contributions are what make the open-source community such an amazing place to learn, inspire, and create. Any contributions you make are **greatly appreciated**.

1.  Fork the Project
2.  Create your Feature Branch (`git checkout -b feature/AmazingFeature`)
3.  Commit your Changes (`git commit -m 'Add some AmazingFeature'`)
4.  Push to the Branch (`git push origin feature/AmazingFeature`)
5.  Open a Pull Request

---

## 📄 License

Distributed under the MIT License. See `LICENSE` file for more information.
