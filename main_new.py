import streamlit as st 
from openai import OpenAI
from google.cloud import firestore
import plotly.graph_objects as go 
import fitz 
import os 
import json 
import pandas as pd
from datetime import datetime


client = OpenAI(api_key=os.environ['OPENAI_SECRET'])
db = firestore.Client.from_service_account_json("firestore-key.json")
posts_ref = db.collection("posts")


# Adding CSS for styling
st.markdown("""
    <style>
        .title {
            font-size: 40px;
            color: #4CAF50;
            text-align: center;
            font-weight: bold;
        }
        .header {
            font-size: 24px;
            color: #000000;
            font-weight: bold;
        }
        .subheader {
            font-size: 20px;
            color: #333;
        }
        .question {
            font-size: 18px;
            color: #000;
        }
        .footer {
            font-size: 14px;
            color: #666;
        }
    </style>
    """, unsafe_allow_html=True)

# Main title
st.markdown("<div class='title'>Finance Service Advisor</div>", unsafe_allow_html=True)

st.markdown("""
    <p style="text-align: left;">Welcome to the Student Finance Planner! This platform is a comprehensive tool designed to help students manage their finances effectively. 

    With this planner, you can allocate your monthly budget, plan your savings, and get personalized investment advice based on your financial goals and preferences. Utilize the power of OpenAI's advanced algorithms to make informed decisions and achieve financial stability during your studies.</p>
    """, unsafe_allow_html=True)


# Function to generate expense plan
def expense_planner(income, state, current_savings, monthly_expenses, saving_goal, necessary_spending, comment):
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": """
                You are a financial planner bot. You will receive income, living state, current_savings, monthly expenses, saving goal, and necessary spending
                for the next month. Your task is to evaluate the spending and saving patterns and provide insights and recommendations to optimize the user's budget.
                Include the Pros, Cons, Effects, and Measures for the user's financial habits. Lastly, provide an overall analysis of the user's entire budget allocation.
            """},
            {"role": "user", "content": f"""
                Here are my details: 
                Current income: RM{income}
                Current state of living: {state}
                Current savings: RM{current_savings}
                Monthly expenses: RM{monthly_expenses}
                Saving goal: RM{saving_goal}
                Necessary spending next month: RM{necessary_spending}

                Here are some of my extra comments: {comment}
            """}
        ],
        max_tokens=4000,
        temperature=0
    )
    return response.choices[0].message.content


def check(income, state, current_savings, monthly_expenses, saving_goal, necessary_spending, comment):
    return f"""
        Here are my details: 
        Current income: RM{income} monthly
        Current state of living: {state} 
        Current savings: RM{current_savings}
        Monthly expenses: RM{monthly_expenses}
        Saving goal: RM{saving_goal}
        Already decided spending next month: RM{necessary_spending}

        Additional comments: {comment}
    """

def chatbot_response(user_input, additional_context):
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": """
                    You are a general AI chatbot. You will receive user input along with some additional context of the user.
                    Your task is to understand the user's question or statement and provide a relevant and helpful response.
                    Ensure that the response is engaging and informative based on the input and context provided. React as a normal AI Chatbot that normally speaks in a casual manner. If a user asks a question that is not related to finance, you can provide a different response for a casual talk. Ensure to personalize the experience based on the fascilities, development and economy of the state
            """},
            {"role": "user", "content": f"""
                User input: {user_input}
                Additional context: {additional_context}
            """}
        ],
        max_tokens=1500,
        temperature=0.7
    )
    # st.write(response.choices[0].message.content)
    return response.choices[0].message.content



# Collecting all inputs in a dictionary
inputs = {}


tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs(
    ["Upload Receipt", "Personal Q&A", "Upload Bills",  "FinTechy (Beta 💸)", "Contact Us", "Rate Us",])

with tab1:
    def initialize(): 
        doc_ref = db.collection("posts").document("food")
        doc_ref.set({
          "title": "food",
          "value": 0
        })

        doc_ref = db.collection("posts").document("entertainment")
        doc_ref.set({
          "title": "entertainment",
          "value": 0
        })

        doc_ref = db.collection("posts").document("travel")
        doc_ref.set({
          "title": "travel",
          "value": 0
        })

        doc_ref = db.collection("posts").document("shopping")
        doc_ref.set({
          "title": "shopping",
          "value": 0
        })

        doc_ref = db.collection("posts").document("personal_care")
        doc_ref.set({
          "title": "personal_care",
          "value": 0
        })

        doc_ref = db.collection("posts").document("family")
        doc_ref.set({
          "title": "family",
          "value": 0
        })

        doc_ref = db.collection("posts").document("others")
        doc_ref.set({
          "title": "others",
          "value": 0
        })

    def save_database(title, new_value): 
        doc_ref = db.collection("posts").document(title)
        doc = doc_ref.get()

        if doc.exists: 
            current_value = doc.to_dict().get("value", 0)
            updated_value = current_value + new_value
        else: 
            updated_value = new_value

        doc_ref.set({
          "title": title,
          "value": updated_value
        })

    def pdf_to_text(pdf_bytes):
        try:
            document = fitz.open(stream=pdf_bytes, filetype="pdf")
            text = ""
            for page_num in range(len(document)):
                page = document.load_page(page_num)
                text += page.get_text()
            return text
        except Exception as e:
            st.error(f"Error extracting text: {e}")
            return ""

    def categorize(prompt):
      response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
          {"role": "system", "content": """
          You are a receipt categorizer bot. You will receive a prompt which is the contents of a receipt. Your task is to categorize the receipt and the total 
          amount into one of the following categories: "food", "entertainment", "travel", "shopping", "personal_care", "family", and "others", where "others" include utility bills such as electricity, water, rent, taxes, etc. 
          """},
          {"role": "user", "content": """
          Touch N Go Receipt Date: 18/7/2024 Touch N Go card topup amount: RM50.00 Touch N Go card topup amount: RM25.00 Total: RM75.00
          """},
          {"role": "assistant", "content": """
          { "category": "travel", "value": 75 } 
          """},
          {"role": "user", "content": f"""
          {prompt}
          """}
        ],
        max_tokens = 50,
        temperature = 0
      )
      return response.choices[0].message.content

    def get_total(): 
        total = 0 
        keys = ['food', 'entertainment', 'travel', 'shopping', 'personal_care', 'family', 'others']
        for key in keys: 
            doc_ref = db.collection("posts").document(key)
            doc = doc_ref.get() 

            if doc.exists:
                value = doc.to_dict().get("value", 0)
                total += value

        return total 

    def get_pecentages(): 
        keys = ['food', 'entertainment', 'travel', 'shopping', 'personal_care', 'family', 'others']
        output = []

        total = 0 
        for key in keys: 
            doc_ref = db.collection("posts").document(key)
            doc = doc_ref.get() 

            if doc.exists:
                value = doc.to_dict().get("value", 0)
                total += value

        for key in keys: 
            doc_ref = db.collection("posts").document(key)
            doc = doc_ref.get() 

            value = 0
            if doc.exists:
                value = doc.to_dict().get("value", 0)

            percentage = (value / total) * 100
            output.append(percentage)

        return output

    st.write("Please upload your expenses recipt")


    with st.form("my_form", clear_on_submit=True):
        # income = st.number_input("Fixed income (RM)", min_value=0.00, step=0.01) 
        # current_savings = st.number_input("Current Savings (RM)", min_value=0.00, step=0.01)
        # expenses = st.number_input("Monthly Expenses (RM)", min_value=0.00, step=0.01)
        # target_savings = st.number_input("Target Savings (RM)", min_value=0.00, step=0.01)

        uploaded_files = st.file_uploader("Choose a PDF file", accept_multiple_files=True)
        submitted = st.form_submit_button("Submit")

        if submitted and uploaded_files:
            for uploaded_file in uploaded_files:
                pdf_bytes = uploaded_file.read()
                st.write("Filename:", uploaded_file.name)
                extracted_text = pdf_to_text(pdf_bytes)

                if extracted_text:
                    with st.spinner('Saving to Database'):
                        output = json.loads(categorize(extracted_text))
                        category = output["category"] 
                        value = output["value"]
                        save_database(category, value)
                        st.write(output)
                        
                else:
                    st.warning("No text extracted or error occurred.")

    ### PIE CHART 
    try:
        labels = ['Food', 'Entertainment', 'Travel', 'Shopping', 'Personal Care', 'Family', 'Others']
        values = get_pecentages()

        fig = go.Figure(data=[go.Pie(
            labels=labels,
            values=values,
            hole=0.5,
            textinfo='percent',
            hoverinfo='none', 
            textposition='inside',
        )])

        fig.update_traces(hovertemplate='%{label} %{value}%')

        fig.update_layout(
            title='Expenses Pie Chart',
            margin=dict(l=20, r=20, t=50, b=20),  # Adjust margins as needed
        )

        st.plotly_chart(fig)
    except:
       st.write("Please upload your recipts to view your expense chart") 

    ### READ DATABASE (TEMPORARY DELETE)
    # for doc in posts_ref.stream():
    #   st.write("The id is: ", doc.id)
    #   st.write("The contents are: ", doc.to_dict())


    if st.button('Clear'):
        initialize()
        st.rerun()

with tab2: 
    with st.form(key='finance_form'):
        # Question 1: Fixed Income
        fixed_income = st.number_input("How much is your fixed income? (RM)", min_value=100, step=50)
        inputs['Fixed Income'] = fixed_income

        # Question 2: State of Living
        state = st.selectbox(
            "Select a state",
            ("None", "Johor", "Kedah", "Kelantan", "Malacca", "Negeri Sembilan", "Pahang", "Penang", "Perak", "Perlis", "Selangor", "Sarawak", "Sabah", "Terengganu")
        )
        inputs['State'] = state

        # Question 3: Savings
        savings = st.number_input("How much do you have in your savings? (RM)", min_value=100, step=1)
        inputs['Savings'] = savings

        # Question 4: Monthly Expenses
        monthly_expenses = st.number_input("How much do you spend every month? (RM)", min_value=100, step=1)
        inputs['Monthly Expenses'] = monthly_expenses

        # Question 5: Saving Goal
        saving_goal = st.number_input("How much do you want to save? (RM)", min_value=100, step=1)
        inputs['Saving Goal'] = saving_goal

        # Question 7: Necessary Spending Next Month
        necessary_spending = st.number_input("How much do you must spend for next month first? (RM)", min_value=0, step=1)
        inputs['Necessary Spending'] = necessary_spending

        comment = st.text_area("Additional comments", value="Nothing")

        # Validate inputs before showing the final message
        if st.form_submit_button("Submit"):
            if state == "None":
                st.warning("Please select a state.")
            elif necessary_spending > fixed_income:
                st.warning("Necessary spending cannot exceed fixed income. Please adjust your necessary spending or fixed income.")
            else:
                advice = expense_planner(fixed_income, state, savings, monthly_expenses, saving_goal, necessary_spending, comment)
                st.success("Thank you for your responses! Your personalized financial advice is generated based on these inputs.")
                st.markdown(advice)

with tab3:
    def clear_collection_sar(collection_name):
        collection_ref = db.collection(collection_name)
        docs = collection_ref.stream()
        for doc in docs:
            doc.reference.delete()


    def initialize_sar(): 
        doc_ref = db.collection("to_pay").document("electricity")
        doc_ref.set({
          "cost": 30,
          "priority_level": "high",  # Example priority level
          "current_day": 0,  # Example current day
          "return_day": 90  # Example return day
        })

        doc_ref = db.collection("to_pay").document("credit_card")
        doc_ref.set({
          "cost": 30,
          "priority_level": "medium",  # Example priority level
          "current_day": 0,  # Example current day
          "return_day": 20  # Example return day
        })

    # streamlit run main.py --server.enableXsrfProtection false

    def save_database_sar(title, new_value, priority, current_day, cutoff_days):

        doc_ref = db.collection("to_pay").document(title)
        doc = doc_ref.get()

        if doc.exists:
            data = doc.to_dict()
            current_cost = data.get("cost", 0)
            updated_cost = current_cost + new_value
            data["cost"] = updated_cost
            data["priority_level"] = priority
            data["current_day"] = current_day
            data["return_day"] = cutoff_days

        else:
            data = {
                "cost": new_value,
                "priority_level": "high",  # Default priority level if not existing
                "current_day": current_day,  # Default current day if not existing
                "return_day": cutoff_days  # Default return day if not existing
            }

        doc_ref.set(data)



    def pdf_to_text_sar(pdf_bytes):
        try:
            document = fitz.open(stream=pdf_bytes, filetype="pdf")
            text = ""
            for page_num in range(len(document)):
                page = document.load_page(page_num)
                text += page.get_text()
            return text
        except Exception as e:
            st.error(f"Error extracting text: {e}")
            return ""



    def categorize_sar(prompt):
        # Define the instruction strings
        cut_date_str = (
            f'You are a receipt categorizer bot. You will receive a prompt which is the contents of a receipt. '
            f'Your task is to categorize the receipt and the total amount into one of their respective categories, '
            f'such as electricity bill in the electric category. If there is no default date, assume the receipt is for the current day. '
            f'The output must be in the following format of 4 values in the form of {{ "category": "electricity", "cost": 600, "priority_level": "medium", "current_day": 4, "cutoff_days": 20 }} where '
            f'the category is the category of the bill, cost total cost to pay, priority level is the priority level (considering the timeframe from the current day and the cutoff_days, where if it is more closer to the cutoff day it should be high, if it is in middle it should be medium and low if there is a longer time frame ), '
            f'the current_day is to Identify the receipt issued date from the receipt and calculate the number of days since the receipt issued date (identified from the receipt) and today: {datetime.today().date()}, '
            f'and the cutoff_days is the general time taken before the receipt is due to be paid before an additional interest or additional cost will be issued or unforeseen circumstances like electric cut,i.e. , an electricity bill has a cutoff day of 90 days, so the cutoff date is 90 days after the receipt was issued.'
        )
        # cut_date_str_2 = "current_day is set to the number of days since the receipt was issued."

        st.write(prompt)

        # Construct the chat completion request
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": cut_date_str},
                {"role": "user", "content": """
                    Credit Card Receipt Issued Date: 15/7/2024 Cost to pay: RM600.00 amount: RM25.00 
                """},
                {"role": "assistant", "content": """
                    { "category": "electricity", "cost": 600, "priority_level": "medium", "current_day": 4, "cutoff_days": 20 } 
                """},
                {"role": "user", "content": f"{prompt}"}
            ],
            max_tokens=100,
            temperature=0
        )

        st.write(response.choices[0].message.content)

        # Return the response
        return response.choices[0].message.content

    # Streamlit app code
    # st.header("Financial Garbage I REALLY REALLY want to die")
    with st.form("my_form_2"):
        uploaded_files = st.file_uploader("Choose a PDF file", accept_multiple_files=True)
        submitted = st.form_submit_button("Submit")

        if submitted and uploaded_files:
            for uploaded_file in uploaded_files:
                pdf_bytes = uploaded_file.read()
                st.write("Filename:", uploaded_file.name)
                extracted_text = pdf_to_text_sar(pdf_bytes)

                if extracted_text:
                    with st.spinner('Saving to Database'):
                        # st.write(extracted_text)

                        output = json.loads(categorize_sar(extracted_text))
                        category = output["category"]
                        value = output["cost"]
                        priority_level = output["priority_level"]
                        current_day = output["current_day"]
                        return_day = output["cutoff_days"]



                        save_database_sar(category, value, priority_level, current_day, return_day)


                    st.write("Done")
                else:
                    st.warning("No text extracted or error occurred.")


    def check_cutoff_dates_sar():
        collection_ref = db.collection("to_pay")
        docs = collection_ref.stream()

        notifications = []
        data_list = []
        # today = datetime.today()

        for doc in docs:
            data = doc.to_dict()
            title = doc.id
            current_day = data.get("current_day", 0)
            return_day = data.get("return_day", 0)
            priority_level = data.get("priority_level", 0)


            # Add data to the list for table representation
            data_list.append({
                "Payment to Make": title,
                "Priority": priority_level,
                "Days Since Last Payment": current_day,
                "Cut-off Date before Consequence": return_day
            })

            st.write(f"Title: {title}", current_day, return_day)

            if current_day + 5 > return_day:
                notifications.append(f"{title} payment has exceeded cutoff date! Time since last payment is {current_day}. Please pay latest in {return_day - current_day} days!")

        return notifications, data_list

    st.header("Financial Notification System")


    notifications, data_list = check_cutoff_dates_sar()

    # Convert the data list to a DataFrame
    df = pd.DataFrame(data_list)

    # Display the data as a table
    st.table(df)

    if notifications:
        for notification in notifications:
            st.warning(notification)
    else:
        st.success("No payments have exceeded the cutoff date.")


    if st.button('Delete'):
        clear_collection_sar("to_pay")
        st.rerun()




# Tab4 설정
with tab5:
    st.header("Contact Us")
    st.subheader("Send us an email if you have any questions or feedback!")

    # 이메일 관련 입력 필드
    email_categories = ["Error Report", "Additional Question", "Feedback", "Improvement Suggestion", "Others"]
    email_subject = st.selectbox("Subject:", email_categories)
    email_content = st.text_area("Message:", height=200)

    # 이메일 전송 버튼
    if st.button("Send Email"):
        if email_subject and email_content:
            # 이메일 전송 로직 추가
            st.success("Your email has been sent successfully!")
        else:
            st.warning("Please fill in both the subject and message before sending.")


# Tab5 설정
with tab6:
    st.header("Rating and Comment")

    # 별점 설정 슬라이더
    st.subheader("Rate your experience:")
    rating = st.slider("Rate from 0 to 5:", 0.0, 5.0, step=0.5)

    # 선택된 별점 표시
    st.write(f"Selected rating: {rating}")

    # 코멘트 입력 텍스트 영역
    st.subheader("Add your comment:")
    comment = st.text_area("Enter your comment here:", height=200)

    # 전송 버튼
    if st.button("Submit Rating and Comment"):
        if comment:
            st.success("Thank you for your feedback!")
        else:
            st.warning("Please enter your comment before submitting.")


with tab4:
    st.subheader("Chatbot")

    # Create a container for the chat messages
    chat_container = st.container()

    # Create a container for the input box
    input_container = st.container()

    st.markdown(
      """
      <style>
      .stApp {
          height: 100vh;
          display: flex;
          flex-direction: column;
      }
      .main {
          flex-grow: 1;
          overflow: auto;
      }
      .chat-input {
          position: fixed;
          bottom: 0;
          left: 0;
          right: 0;
          background-color: white;
          padding: 1rem;
          z-index: 1000;
      }
      .chat-messages {
          padding-bottom: 70px;
      }
      </style>
      """,
      unsafe_allow_html=True
    )

    # Function to clear chat history
    def clear_chat():
        st.session_state.messages = []

    # Display clear chat button
    if st.button("Clear Chat History"):
        clear_chat()


    with chat_container:
        if "messages" not in st.session_state:
            st.session_state.messages = []

        for message in st.session_state.messages:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])

        if len(st.session_state.messages) == 0:
            with st.chat_message("assistant"):
                st.markdown("Hi! I'm FinTechy, your virtual financial advisor. How can I help you today?")
            st.session_state.messages.append({"role": "assistant", "content": "Hi! I'm FinTechy, your virtual financial advisor. How can I help you today?"})

        with input_container:
            prompt = st.chat_input("Ask a question!")
            if prompt:
                  with chat_container:
                      with st.chat_message("user"):
                          st.markdown(prompt)

                      st.session_state.messages.append({"role": "user", "content": prompt})

                      response_content = chatbot_response(st.session_state.messages, check(fixed_income, state, savings, monthly_expenses, saving_goal, necessary_spending, comment))
                      with st.chat_message("assistant"):
                          st.markdown(response_content)
                      st.session_state.messages.append({"role": "assistant", "content": response_content})

                  # Rerun to update the chat container
                  st.rerun()



