# AI Chat Assistant

A stateless and secure chat interface with LLM capabilities and file upload functionality, deployed as a Databricks App. The model serving endpoint can connect to a variety of LLM providers.

## 🎯 Overview

This application provides:
- Document upload and analysis (PDF, DOCX, TXT, MD)
- AI-powered chat interface for document Q&A
- Stateless design - no data persistence
- Secure processing within Databricks environment

## ✨ Key Features

- **Document Upload**: Support for PDF, DOCX, TXT, and Markdown files
- **Text Extraction**: Automatic processing of document content
- **AI Chat Interface**: Real-time responses based on uploaded documents
- **Stateless Design**: No data persistence between sessions
- **Secure Processing**: All processing within Databricks environment

## 🏗️ Technical Architecture

- **Databricks Model Serving**: Uses Databricks LLM endpoints
- **Streamlit Frontend**: Modern web interface
- **Stateless Design**: Scalable architecture

## 🚀 Deployment Options

### Databricks-Native Deployment
- Deploy directly within Databricks workspace
- Leverage existing Databricks infrastructure
- Integrated with Databricks security and governance

### On-Premises Deployment
- Self-hosted solution for maximum security
- Complete control over data and infrastructure
- Integration with existing enterprise systems

## 📋 Prerequisites

### System Requirements
- Python 3.8+
- Databricks workspace with model serving capabilities
- Azure Active Directory for authentication

### Dependencies
```
mlflow>=2.21.2
streamlit==1.44.1
databricks-sdk
PyMuPDF
python-docx
```

## 🚀 Getting Started

### Develop and run the Databricks app locally

See documentation [here](https://docs.databricks.com/aws/en/generative-ai/agent-framework/chat-app)

1. **Clone this repository:**
   ```bash
   git clone https://github.com/ashwinpo/databricks-chat-app
   cd databricks-chat-app
   ```

2. **Install the required libraries:**
   ```bash
   pip install -r requirements.txt
   ```

3. To make calls to the agent endpoint, you must **authenticate to your Databricks workspace.** Generate a personal access token and save the token value.

4. **Configure the Databricks CLI:**
   ```bash
   databricks configure
   ```
5. Provide the **Databricks host** url for your workspace: https://hostname.cloud.databricks.com and the **Personal access token** from earlier.

6. Specify the model serving endpoint name and run the app. To find the model serving endpoint name, go to your workspace and select **Serving** to see a list of model serving endpoints:
   ```bash
   export SERVING_ENDPOINT=databricks-llama-4-maverick
   streamlit run app.py
   ```

### Deploy the Databricks app programmatically

Deploy the example as a Databricks app to share it with others.

1. **Create the Databricks App:**
   Run `databricks app create` to create the Databricks App. The following snippet assumes `SERVING_ENDPOINT` is still set - if not, replace it with your serving endpoint name:

   ```bash
   databricks apps create --json '{
     "name": "my-agent-chatbot",
     "resources": [
       {
         "name": "serving-endpoint",
         "serving_endpoint": {
           "name": "'"$SERVING_ENDPOINT"'",
           "permission": "CAN_QUERY"
         }
       }
     ]
   }'
   ```

2. **Upload source code and deploy:**
   Upload the source code to Databricks and deploy the app by running the following commands from the `databricks-chat-app` directory:

   ```bash
   DATABRICKS_USERNAME=$(databricks current-user me | jq -r .userName)
   databricks sync . "/Users/$DATABRICKS_USERNAME/databricks-chat-app"
   databricks apps deploy my-agent-chatbot --source-code-path "/Workspace/Users/$DATABRICKS_USERNAME/databricks-chat-app"
   ```

3. **Get the app URL:**
   Get the URL of your app and test the app:

   ```bash
   databricks apps get my-agent-chatbot | jq -r '.url'
   ```

### Deploying in Databricks via UI

1. **Setup your Databricks Environment**
- Git clone in Databricks
   - Workspace > Create > Git folder > copy & paste Git repository URL: https://github.com/ashwinpo/databricks-chat-app
   - Create Git Folder

- Create the app via Databricks UI
   - Click **Compute** in the sidebar
   - Go to the **Apps** tab > select **Create app** in top right corner
   - Select **Streamlit tab** under Create new app > **Chatbot**
   - Select **Serving endpoint: databricks-llama-4-maverick** > Install

   <img src="images/serving_endpoint.png" alt="Selecting serving endpoint" width="800" style="max-width: 100%; height: auto;">

2. **Deploy the app using Databricks UI**
   - Toggle the **Deploy** button > Select **Deploy using different source code path**

   <img src="images/deploy_sourcecode.png" alt="Deploying new sourcecode" width="800" style="max-width: 100%; height: auto;">

   - Select file with sourcecode
   - **Deploy**
   - Click on the link next to **Running** to access the deployed app



