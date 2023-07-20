import streamlit as st
from PIL import Image
import pytesseract
from spam_u import spam_detection

# Set the Tesseract executable path
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

def extract_text_from_image(image):
    # Convert the image to grayscale
    image = image.convert("L")

    # Use Tesseract to perform OCR and extract text
    text = pytesseract.image_to_string(image)

    # Return the extracted text
    return text

def main():
    st.title("Image Text Extraction and Spam Detection")
    st.text("you can either past your text or join an image and we will process it")
    his_email=st.text_area("enter your email:")
    if st.button("submit your email"):
        prediction = spam_detection(his_email)
        if prediction == 1:
            st.write("The extracted text is classified as spam.")
        else:
            st.write("The extracted text is not classified as spam.")
    
    # Image uploader
    uploaded_image = st.file_uploader("Upload an image", type=["jpg", "jpeg", "png"])
    
    # Process button
    if st.button("Process Image") and uploaded_image is not None:
        # Open the uploaded image
        image = Image.open(uploaded_image)
        
        # Perform OCR and extract text
        extracted_text = extract_text_from_image(image)
        
        # Display the extracted text
        st.write("Extracted Text:")
        st.write(extracted_text)
        st.write("okay i will check it for you")
        prediction = spam_detection(extracted_text)
            
            # Display the result
        if prediction == 1:
            st.write("The extracted text is classified as spam.")
        elif prediction == 0:
            st.write("The extracted text is not classified as spam.")

    
if __name__ == "__main__":
    main()
