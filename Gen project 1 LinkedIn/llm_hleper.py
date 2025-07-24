from dotenv import load_dotenv
from langchain_groq import ChatGroq
import os

load_dotenv()

# Initialize the model
llm = ChatGroq(groq_api_key=os.getenv("GROQ_API_KEY"), model_name="llama-3.3-70b-versatile")

if __name__ == "__main__":
    # Invoke the model
    response = llm.invoke("What are the two main ingredients in samosa")
    
    # Print the response content
    print(response.content)  # Adjust this based on the structure of the `invoke` method's return

