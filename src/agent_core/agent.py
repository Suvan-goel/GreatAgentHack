import os
from fastapi import FastAPI, UploadFile

app = FastAPI()

@app.post("/uploadfile/")
async def create_upload_file(file: UploadFile):
    return {"filename": file.filename}





# import os
# from dotenv import load_dotenv
# from holistic_ai_bedrock import HolisticAIBedrockChat, get_chat_model
# from strands_tools import file_read
# from strands import agent







# load_dotenv()
#
# HOLISTIC_AI_TEAM_ID = os.getenv("HOLISTIC_AI_TEAM_ID")
# HOLISTIC_AI_KEY = os.getenv("HOLISTIC_AI_API_TOKEN")
#
# llm = get_chat_model("claude-3-5-sonnet")  # Uses Holistic AI Bedrock (recommended)
#
# question = "What is quantum computing?"
#
# response = llm.invoke(question)