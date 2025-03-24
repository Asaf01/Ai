import streamlit as st
import boto3
import json

# AWS Bedrock Config
AWS_REGION_BEDROCK = "us-west-2"
KNOWLEDGE_BASE_ID = "*****************"
MODEL_ARN = "arn:aws:bedrock:us-west-2::foundation-model/anthropic.claude-v2"

client = boto3.client("bedrock-agent-runtime", region_name=AWS_REGION_BEDROCK)

# Streamlit UI
st.title("AWS Knowledge Base Chatbot")
st.write("Ask a question based on the uploaded documents.")

question = st.text_input("Enter your question:")
if st.button("Ask"):
    if question:
        response = client.retrieve_and_generate(
            input={"text": question},
            retrieveAndGenerateConfiguration={
                "type": "KNOWLEDGE_BASE",
                "knowledgeBaseConfiguration": {
                    "knowledgeBaseId": KNOWLEDGE_BASE_ID,
                    "modelArn": MODEL_ARN,
                },
            },
        )
        answer = response.get("output", {}).get("text", "No answer found.")
        st.write("### Answer:")
        st.success(answer)
    else:
        st.warning("Please enter a question.")
