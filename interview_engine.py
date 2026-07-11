import os
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain_core.prompts import PromptTemplate
from langchain_community.document_loaders import CSVLoader
from langchain_core.tools import tool

load_dotenv()

# 🚀 1. Initialize LangChain Groq Model (Llama 3)
# =========================================================================
llm = ChatGroq(
    model="llama-3.3-70b-versatile",
    groq_api_key=os.environ.get("GROQ_API_KEY"),
    temperature=0.3  
)


# 🛠️ 2. Advanced Tools (Dataset Stats & Forecasting)
# =========================================================================
@tool
def calculate_dataset_stats(metric_name: str) -> str:
    """Useful to calculate averages or stats from the car dataset. Accepts 'price' or 'mileage'."""
    import pandas as pd
    try:
        df = pd.read_csv("sri_lankan_car_dataset.csv")
        if "price" in metric_name.lower():
            avg_price = df["Price"].mean()
            return f"[Tool Output] Actual average price is {avg_price:.2f} million LKR."
        elif "mileage" in metric_name.lower() or "millage" in metric_name.lower():
            avg_mileage = df["Millage(KM)"].mean()
            return f"[Tool Output] Actual average mileage is {avg_mileage:.2f} KM."
        return "[Tool Output] Metric not recognized."
    except Exception as e:
        return f"[Tool Output] Error: {e}"

@tool
def forecast_future_car_prices(years_into_future: int) -> str:
    """Useful to predict future car market trends in Sri Lanka based on an 8% annual baseline."""
    import pandas as pd
    try:
        df = pd.read_csv("sri_lankan_car_dataset.csv")
        current_avg_price = df["Price"].mean()
        predicted_future_price = current_avg_price * ((1 + 0.08) ** years_into_future)
        return f"[Forecasting Tool Output] Predicted average price in {years_into_future} year(s): {predicted_future_price:.2f} million LKR."
    except Exception as e:
        return f"[Forecasting Tool Output] Error: {e}"

llm_with_tools = llm.bind_tools([calculate_dataset_stats, forecast_future_car_prices])

# =========================================================================
# 📂 3. Dynamic Context Loaders

def load_csv_data(csv_file_path=None):
    # Pass the CSV path to the loader; if None (no file uploaded), it will return "No extra dataset" to the model.
    if not csv_file_path:
        return "No specific dataset provided by the candidate."
    try:
        loader = CSVLoader(file_path=csv_file_path)
        documents = loader.load()
        return "\n".join([doc.page_content for doc in documents[:10]])
    except:
        return "Failed to load the dataset."

def load_resume():
    try:
        with open("student_resume.txt", "r", encoding="utf-8") as file:
            return file.read()
    except FileNotFoundError:
        return "Resume context is missing. Please ensure 'student_resume.txt' exists."

# =========================================================================
# 🧠 4. Dynamic Master Prompt (All Rules, English Corrections & Report Included)


interview_prompt_template = PromptTemplate(
    input_variables=["resume_context", "csv_data", "chat_history", "user_message", "user_name", "job_title", "level"],
    template="""You are an expert Lead Data Scientist and Corporate Recruiter conducting a strict mock technical interview for {user_name}. 

Your tone must be professional, analytical, and supportive, yet critical like a real tech lead evaluating data skills.
You are an expert Interviewer. Conduct a {level} level technical interview for {user_name} for the position of {job_title}. Adjust your technical questions and evaluation strictness based on the {level} level. 

STRICT RULES & OBJECTIVES:
1. If the user message is "exit", stop asking technical questions. Instantly generate a comprehensive, professional **FINAL INTERVIEW PERFORMANCE REPORT** in Markdown format.
    The report must cover:
   - Technical Strengths
   - Coding & Logic Gaps
   - English Communication & Grammar Improvements
   - Overall Hiring Decision Status (e.g., Highly Recommended / Needs Improvement)

2. welcome {user_name} professionally and challenge her with ONE sharp technical or behavioral question based on her resume and the target role: {job_title}.

3. Keep intermediate conversation rounds lively and concise (under 4 sentences).

4. CRITICAL - English Communication Guardrail: If {user_name} makes grammatical mistakes, spelling errors, or poor sentence structures in English, gently correct her grammar/communication in your feedback to help her look professional.

5. CRITICAL - CONVERSATION FLOW GUARDRAIL: Greet, welcome, or introduce the interview to {user_name} ONLY in the very first message (when user says 'start'). For all subsequent interview questions, DO NOT say "Welcome", "Welcome back", "Good day", or use any introductory greetings. Start your response directly with the feedback on her answer and the next question.

6. ONE QUESTION RULE: Ask exactly ONE sharp technical or behavioral question per turn. Never combine multiple interview questions into a single response, as it overwhelms the candidate.

7. DRILL-DOWN APPROACH: Act like a real interviewer. Instead of jumping to a completely new topic in every turn, listen to {user_name}'s answer carefully. Ask follow-up questions based on her specific response to test the depth of her knowledge (e.g., "Why did you choose that specific method?", "What were the challenges with that approach?"). Spend at least 2-3 turns on a single major topic before moving to the next.

8. LANGUAGE STICKINESS: The interview must be conducted ENTIRELY in English. Even if {user_name} responds in another language (like Sinhala), you must gently encourage her to try in English and continue your response strictly in English.

Context 1 - Resume Data:
\"\"\"{resume_context}\"\"\"

Context 2 - Car Dataset Context:
\"\"\"{csv_data}\"\"\"

Chat History:
\"\"\"{chat_history}\"\"\"

Current User Message: "{user_message}"

Provide your direct professional response:"""
)

# =========================================================================
# 🌟 5. Main Function Called by Streamlit UI (`app.py`)
# =========================================================================
def handle_interview_chat(user_message, chat_history, uploaded_resume_text=None, difficulty_level="Intern", csv_path=None, user_name="Candidate", job_title="Candidate", level="Intern"):
    resume_content = uploaded_resume_text if uploaded_resume_text else load_resume()
    csv_data = load_csv_data(csv_path)
    
    # 1. Exit පණිවිඩය සඳහා විශේෂ Prompt එක
    if user_message.lower() == "exit":
        prompt_to_use = f"""
        Analyze the provided chat history. 
        
        CRITICAL RULE: 
        1. If the chat history is empty or contains NO answers to technical questions, explicitly state: "The interview was terminated before any technical questions were answered. Cannot generate a performance report."
        2. If the chat history contains answers, generate a detailed Markdown report for {user_name}.
        
        Structure the report as follows:
        1. UNDER '💪 Technical Strengths': Analyze only the answers given during the chat.
        2. UNDER '🔍 Coding & Logic Gaps': Analyze only the logic demonstrated in the answers.
        3. UNDER '🗣️ English Communication & Grammar Improvements': Analyze the language used in the chat.
        4. UNDER '🎯 Overall Hiring Decision Status': Give a recommendation based on the *interview performance*, not just the resume.
        
        Chat History:
        {chat_history}
        """
        # 🌟 මෙතනදී කෙලින්ම මෙම Prompt එක invoke කරන්න
        try:
            response = llm.invoke(prompt_to_use) # llm_with_tools වෙනුවට කෙලින්ම llm භාවිතා කරන්න (Tools අවශ්‍ය නැති නිසා)
            return response.content
        except Exception as e:
            return f"Report Generation Error: {e}"

    # 2. සාමාන්‍ය ප්‍රශ්න සඳහා පවතින Logic එක
    else:
        formatted_prompt = interview_prompt_template.format(
            resume_context=resume_content,
            csv_data=csv_data,
            chat_history=chat_history,
            user_message=user_message,
            difficulty_level=difficulty_level,
            user_name=user_name,
            job_title=job_title,
            level=level
        )
        try:
            response = llm_with_tools.invoke(formatted_prompt)
            return response.content
        except Exception as e:
            return f"Agent Guardrail Error: {e}"

# =========================================================================
# 🏃‍♂️ 6. Runtime Interactive Terminal Loop (Fixed Positional Arguments)
# =========================================================================
if __name__ == "__main__":
    print("--- 🛡️ Milestone 4: Intelligent Groq Llama 3 Agent Interviewer is Live ---")
    print("(Type 'start' to begin the smart data science panel. Type 'exit' to quit)\n")
    
    history = ""
    is_active = False
    
    while True:
        user_input = input("Student: ").strip()
        
        if user_input.lower() == "exit":
            print("\n[Interview Board]: Concluding the interview. Generating your performance report...")
            # 🌟 Terminal එකෙන් exit වෙද්දී මෙතනට වැරදෙන්නේ නැති වෙන්න None එකක් පාස් කළා
            final_report = handle_interview_chat("exit", history, None)
            print(f"\n{final_report}\n")
            break
            
        if user_input.lower() == "start":
            is_active = True
            
        if not is_active:
            print("[Interview Board]: Please type 'start' to begin the panel interview.")
            continue
            
        # # Terminal-based chat: explicitly passing None for csv_path to prevent errors
        bot_response = handle_interview_chat(user_input, history, None)
        print(f"\n[Interview Board]:\n{bot_response}\n")
        
        history += f"\nStudent: {user_input}\nInterviewer: {bot_response}"


        