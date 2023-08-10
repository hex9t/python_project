
import streamlit as st
from PIL import Image
import pytesseract
import numpy as np
from email_system import get_text_plain_part
from email_system import format_email_headers
from email_system import read_email_content_by_uid
from email_system import get_last_email_uid
from email_system import delete_email_by_uid
import re
import time
import joblib
from sklearn.feature_extraction.text import CountVectorizer
import json
import requests
from streamlit_lottie import st_lottie
import matplotlib.pyplot as plt
import seaborn as sns
import tensorflow as tf
import pickle
from tensorflow.keras.preprocessing.sequence import pad_sequences
import plotly.express as px

if "number_of_users" not in st.session_state:
    st.session_state["number_of_users"] = 50
if "number_of_safe_emails" not in st.session_state:
    st.session_state["number_of_safe_emails"] = 30
if "number_of_spam_emails" not in st.session_state:
    st.session_state["number_of_spam_emails"] = 20       

d_model = tf.keras.models.load_model('deep_learning_model.h5')
with open('d_tokenizer.pickle', 'rb') as handle:
    tokenizer = pickle.load(handle)

def d_prediction(text):
    test_tokens = tokenizer.texts_to_sequences([text])
    test_paded =  pad_sequences(test_tokens, maxlen=20, padding="post", truncating="post")
    if d_model.predict(test_paded) > 0.5:
        return 1
    else:
        return 0    
def spam_detection(text):
    model = joblib.load('spam_detection.joblib')
    cv = joblib.load('vectorizer.joblib')
    text_vector = cv.transform([text])
    prediction = model.predict(text_vector)
    return prediction[0]





def read_variables_from_file(file_path):
    with open(file_path, 'r') as file:
        lines = file.readlines()

    variable_dict = {}
    for line in lines:
        parts = line.strip().split("=")
        if len(parts) == 2:
            name = parts[0].strip()
            value = int(parts[1].strip())
            variable_dict[name] = value

    return variable_dict

def write_variables_to_file(file_path, variable_dict):
    with open(file_path, 'w') as file:
        for name, value in variable_dict.items():
            file.write(f"{name} = {value}\n")


def extract_money_sentences(text):
    # Define the regex pattern to match money values
    pattern = r'\$\s?\d+(?:,\d{3})*(?:\.\d{2})?'

    # Find all occurrences of the pattern in the text
    money_sentences = re.findall(pattern, text)

    if not money_sentences:
        return None
    else:
        return money_sentences

def find_words_in_string(input_string):
    words_to_find = ["mother", "father", "uncle", "son", "brother"]
    found_words = []

    for word in words_to_find:
        if word in input_string.lower():
            found_words.append(word)

    return found_words

#

def extract_links(text):
    # Define the regex pattern to match URLs
    pattern = r'https?://\S+|www\.\S+'

    # Find all occurrences of the pattern in the text
    links = re.findall(pattern, text)

    if not links:  # If links list is empty
        return None  # You can also return False, an empty list, or any other custom value
    else:
        return links



def get_color(score):
    if 6<=score <=10:
        # Calculate the RGB values for red color (255, 0, 0)
        color_hex = "#FF0000"
    elif 3<=score < 6:
        # Calculate the RGB values for orange color (255, 165, 0)
        color_hex = "#FFA500"
    else:
        # Calculate the RGB values for green color (0, 128, 0)
        color_hex = "#008000"

    return color_hex
#calculer un score de risk
def risk(text):
    counter = [0,0] 
    text_v=text.split()
    for word in text_v:
        if spam_detection(word)==1:
            counter[0] = counter[0] + 1 
        elif spam_detection(word)==0 : 
            counter[1] = counter[1] + 1   
    medium = round(counter[0]/len(text_v) * 10,2 )
    return medium
def d_risk(text):
    counter = [0,0] 
    text_v=text.split()
    for word in text_v:
        if d_prediction(word)==1:
            counter[0] = counter[0] + 1 
        elif d_prediction(word)==0 : 
            counter[1] = counter[1] + 1   
    medium = round(counter[0]/len(text_v) * 10,2 )
    return medium    
        
words_to_remove = ['for', 'as', 'to', 'with','is']
def highlight_spam_words(text):
    words = text.split()
    highlighted_text = ""

    for word in words:
        if word in words_to_remove:
            highlighted_text += f"{word} "
        else:    

            if spam_detection(word):
                highlighted_text += f'<span style="color:red">{word}</span> '
            else:
                highlighted_text += f"{word} "

    return highlighted_text.strip()

# c'est un scan avancé des motes de l'email
def advanced(text,id):
    if id == 0:
     score = risk(text)
    else:
        score = d_risk(text) 
                  
    if extract_links(text)==None:
        st.write("no links...")
    else:
        st.warning(f"the email provided a link: {extract_links(text)}")   
        score +=1   
    if extract_money_sentences(text)==None:
        st.write("no money is mentionned")
    else:
        st.warning(f"money declared:{extract_money_sentences(text)}")
        score +=1
    if find_words_in_string(text)==[]:
        st.write("no family mentionned")
    else:
        st.warning(f"family members who got mentionned: {find_words_in_string(text)}")  
        score +=len(find_words_in_string(text))
    color = get_color(score)
    st.markdown(f'<h1 style="color: {color}; font-size: 48px; text-align: center;">Score: {score}/10</h1>', unsafe_allow_html=True)
    if 6<=score <=10:
        st.write("this is still too suspicious be aware !")
    if 3<= score <6:
        st.write("this is a bit suspicious so be aware !")
    elif score < 3 :
        st.write("it looks like this email is safe")                  
    highlighted_text = highlight_spam_words(text)
    st.write("words we find suspicious in your email such dates, threatening messages...etc will be highlited in red:")

    st.markdown(highlighted_text, unsafe_allow_html=True)
    
    
    





# design du homepage
def design():
    # Set page title and icon
    
    # Header with Lottie animation
    st.markdown('<h1 style="color: #FF8080;">HOMEPAGE:</h1>', unsafe_allow_html=True)
    url = requests.get("https://lottie.host/c2534cf0-83c9-4822-b017-e5d637ec1dd2/RGqASbFpMF.json")
    url_json = url.json()    
    st_lottie(url_json, width=800, height=600)

    # Title and subtitle
    st.markdown("<div class='title'>Welcome to The HOMEPAGE</div>", unsafe_allow_html=True)
    st.markdown("<div class='subtitle'>Use my app with care please :)</div>", unsafe_allow_html=True)

    # Create a smaller box for the feature section
    with st.markdown("<div class='feature' style='border: 2px solid #FF8080; padding: 20px;'>", unsafe_allow_html=True):
        st.markdown("## Spam Detection")
        
        file_path = 'number_of_users.txt'
        data = read_variables_from_file(file_path)
        data = dict()
        data["number_of_uses"] = st.session_state.number_of_users
        data["detection_times"] = st.session_state.number_of_spam_emails
        data["safe_emails"] = st.session_state.number_of_safe_emails
        
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric(label="Uses", value=data['number_of_uses'], delta="Total Uses")
        with col2:
            st.metric(label="Spam Detections", value=data['detection_times'], delta="New Detections")
        with col3:
            st.metric(label="Safe Emails", value=data['safe_emails'], delta="New Safe Emails")
    
    detection_times_percentage = (data['detection_times'] / data['number_of_uses']) * 100
    safe_emails_percentage = (data['safe_emails'] / data['number_of_uses']) * 100

    # Create and display pie chart using Plotly
    fig = px.pie(
        values=[detection_times_percentage, safe_emails_percentage],
        names=["Spam Emails", "Safe Emails"],
        title="Spam Detection Percentage",
    )
    fig.update_traces(textinfo='percent+label')
    
    st.plotly_chart(fig, use_container_width=True)
    st.write(st.session_state.number_of_users)


def extract_text_from_image(image):
 
    image = image.convert("L")

    
    text = pytesseract.image_to_string(image)

   
    return text

def main():
    
    st.set_page_config(page_title="spam filter", page_icon=":gear:")
  

    st.title("spam detection using ai ")
    st.markdown("This is a project of mine to filter spam emails using various methods.")

 
    st.sidebar.title("Navigation")
    app_mode = st.sidebar.radio(
        "Select an option:",
        ["💒:Home Page","📜:Text Input", "🖼️ :Image Upload", "📬:Gmail Spam Scan", "🤷‍♀️ lost ❔"]
    )

   


    if app_mode == "📜:Text Input":
        st.header("Text Input")
        st.subheader("Enter your text:")

        his_email = st.text_area("Enter your email:")

        if st.button("scan with the machine learning model 🤖"):
        
  
            prediction = spam_detection(his_email)
            st.session_state.number_of_users +=1
            if prediction == 1:
                st.warning("The text is classified as spam.")
                st.session_state.number_of_spam_emails+=1
            elif prediction == 0:
                st.success("The text is not classified as spam.")
                advanced(his_email,0)
                st.session_state.number_of_safe_emails+=1
        if st.button("scan with deep learning model 🛸"):
            prediction = d_prediction(his_email)
            st.session_state.number_of_users +=1
            if prediction == 1:
                st.warning("The text is classified as spam.")
                st.session_state.number_of_spam_emails+=1
            elif prediction == 0:
                st.success("The text is not classified as spam.")
                advanced(his_email,1)
                st.session_state.number_of_safe_emails+=1

            


    elif app_mode == "💒:Home Page":
        design()
        
        

        
        

    elif app_mode == "📬:Gmail Spam Scan":
        st.header("Gmail Spam Scan")
        st.subheader("Enter your Gmail credentials:")

        username = st.text_input("Username (Gmail email)")
        password = st.text_input("Password", type="password")
        imap_server = 'imap.gmail.com'

        if st.button("Analyze Gmail Inbox"):
            st.session_state.number_of_users +=1
            

            last_email_uid = get_last_email_uid(imap_server, username, password)
            if last_email_uid:
                st.write("Latest Email Content:")
                input = read_email_content_by_uid(imap_server, username, password, last_email_uid)
                st.code(input, language="plaintext")
                
                prediction = spam_detection(input)
                if prediction == 1:
                    st.session_state.number_of_spam_emails+=1
                    st.error("The email is classified as spam.")
                    st.warning("The email has been deleted from your inbox.")
                    delete_email_by_uid(imap_server, username, password, last_email_uid)
                else:
                    st.success("The email is not classified as spam.")
                    st.session_state.number_of_safe_emails+=1
                    advanced(input)
            else:
                st.error("No emails found in the mailbox.")
        st.header("you should know:")
        st.write("in order for the gmail analyze to work you need to enable 'less secure apps' in your gmail!")
        st.write("and use the password provided by google the 'app password'")        
        

    elif app_mode == "🤷‍♀️ lost ❔":
        st.title("Simple Tutorial")
        st.write("This tutorial guides you through options for spam detection using both deep learning and naive Bayes scans. If the AI predicts that your email is spam, it will perform an 'advanced scan' for further analysis.")
        st.write("Results are categorized into levels of safety:")

        # Safety Levels
        st.success("0 - 3: Your email is totally safe.")
        st.warning("3 - 6: Your email is suspicious.")
        st.error("6 - 10: Your email is dangerous.")

        # Text Input Section
        st.header("Text Input:")
        st.info("Simply write or paste your message into the text input box, and then scan to see the results!")

        # Image Scan Section
        st.header("Image Scan:")
        st.info("For those who want to scan a screenshot of their email:")
        st.header("gmail scan")
        st.warning("you must enable 'less secure apps' in your google account first and log in with the password provided by google. it takes this form :'XXXX XXXX XXXX XXXX' ")
        st.write("if you click 'analyse gmail inbox' the ai will read your last email and analyse it")
        st.write("it will automatily deletet it if it was a spam")

        

        if st.button("understood"):
            st.balloons()
            

       
        
                
            

            


                     
                  
             
             

    elif app_mode == "🖼️ :Image Upload":
        st.header("Image Upload")
        st.subheader("Upload an image:")
        uploaded_image = st.file_uploader("Choose an image", type=["jpg", "jpeg", "png"])

        if st.button("Process Image with machine learning model 🤖") and uploaded_image is not None:
            st.session_state.number_of_users +=1
            image = Image.open(uploaded_image)
            extracted_text = extract_text_from_image(image)

            st.write("Checking for spam...")
            prediction = spam_detection(extracted_text)

            if prediction == 1:
                st.warning("The extracted text is classified as spam.")
                st.session_state.number_of_spam_emails+=1
                
                
            elif prediction == 0:
                st.success("The extracted text is not classified as spam.")
                with st.spinner("Running advanced scanning..."):
                 
                 advanced(extracted_text,0)
                 st.session_state.number_of_safe_emails+=1
        if st.button("process image with deep machine learning model 🛸"):
            st.session_state.number_of_users +=1
            image = Image.open(uploaded_image)
            extracted_text = extract_text_from_image(image)

            st.write("Checking for spam...")
            prediction = d_prediction(extracted_text)

            if prediction == 1:
                st.warning("The extracted text is classified as spam.")
                st.session_state.number_of_spam_emails+=1
                
                
            elif prediction == 0:
                st.success("The extracted text is not classified as spam.")
                with st.spinner("Running advanced scanning..."):
                 st.session_state.number_of_safe_emails+=1
                 
                 advanced(extracted_text,1)
                  

                    


                 
                 
                                

   
         
              
             
      

if __name__ == "__main__":
    main()

