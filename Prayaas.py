import streamlit as st
from PIL import Image
from pymongo import MongoClient
import os
from io import BytesIO
from dotenv import load_dotenv
import numpy as np
import warnings
import requests
import cv2
import io
import bson.binary
import base64
import requests
warnings.filterwarnings("ignore")


load_dotenv()
os.environ['MONGO_URI'] = 'mongodb+srv://interns:iihmr123@cluster0.gzuy93a.mongodb.net/'

MONGO_URI = os.getenv("MONGO_URI")

if not MONGO_URI:
    raise ValueError("No MONGO_URI found. Please set the MONGO_URI environment variable.")

# Create a MongoClient instance
client = MongoClient(MONGO_URI)

db = client['iihmr']
ic = db['patientinfo']

def get_current_date():
    response = requests.get("http://worldtimeapi.org/api/ip")
    if response.status_code == 200:
        data = response.json()
        datetime_str = data["datetime"]
        date, time = datetime_str.split("T")
        time = time.split(".")[0]  # Remove milliseconds
        return date, time
    else:
        return "Error fetching date and time", ""


def process_image(image):
    # Convert to RGB (if not already in RGB format)
    image = image.convert("RGB")
    # Resize image to 224x224
    image = image.resize((224, 224))
    # Convert the image to a NumPy array
    image_np = np.array(image)
    # Convert RGB to BGR for OpenCV
    image_np = cv2.cvtColor(image_np, cv2.COLOR_RGB2BGR)
    # Split the channels
    b, g, r = cv2.split(image_np)
    # Apply CLAHE to each channel
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
    clahe_b = clahe.apply(b)
    clahe_g = clahe.apply(g)
    clahe_r = clahe.apply(r)

    # Merge the CLAHE enhanced channels back
    image_clahe = cv2.merge((clahe_b, clahe_g, clahe_r))

    # Convert BGR back to RGB
    image_clahe = cv2.cvtColor(image_clahe, cv2.COLOR_BGR2RGB)
    return image, image_clahe


def work(img):
    image = Image.fromarray(img)
    buffer = io.BytesIO()
    image.save(buffer, format='PNG')
    buffer.seek(0)

    # Encode the image data as base64
    img_data = base64.b64encode(buffer.read()).decode("utf-8")
    response = requests.post("http://127.0.0.1:8080/predict", json={"file": img_data})
    res = response.json()

    label = ['Oral Cancer', 'No Abnormality detected', 'Oral premalignant lesion']

    # Convert probabilities to percentages
    for i in range(0,3):
        st.subheader(f"Probability of class {label[i]}: {res[i]:.2f}%")
    
    return res





def main():
    image_url = "https://i.imgur.com/7ppJJP4.jpeg"  # Replace with your actual direct image URL from Imgur

# Centered content using HTML/CSS
    st.markdown(f"""
        <style>
            .center {{
                display: flex;
                justify-content: center;
                align-items: center;
                height: 100;
            }}
            .image-container {{
                text-align: center;
            }}
        </style>
        <div class="center">
            <div class="image-container">
                <img src="{image_url}" style="width: 200px;">
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    # <h1 style='font-size: 5em;'>PRAYAAS</h1>
    st.markdown("""
    <div style='text-align: center;'>
        <h2 style='font-size: 2em;'>Primary Referral and AI-based Screening for Assessing Oral Health</h2>
    </div>
    """, unsafe_allow_html=True)

    name = st.text_input(label="Enter Patient's name:\n:red[*]")
    gender = st.selectbox(label="Select gender:\n:red[*]", options=("None", "Male", "Female", "Other"))
    age = st.number_input(label="Enter age:\n:red[*]", min_value=0, max_value=120, step=1)
    d,t = get_current_date()
    abha = st.text_input("Enter ABHA ID:")
    
    sub=False
    
    
    
    # st.title("Image Upload or Capture")
    st.markdown("<h2 style='font-size: 2em;'>Image Upload or Capture</h2>", unsafe_allow_html=True)
    # Let the user choose between uploading an image or taking a photo
    option = st.selectbox(
        'Choose an option:',
        ('Upload an image', 'Take a photo with your camera')
    )

    image = None

    if option == 'Upload an image':
        uploaded_file = st.file_uploader("Choose an image...", type=["jpg", "jpeg", "png"])
        if uploaded_file is not None:
            image = Image.open(uploaded_file)
    
    elif option == 'Take a photo with your camera':
        img_file_buffer = st.camera_input("Capture an image")
        if img_file_buffer is not None:
            image = Image.open(img_file_buffer)
    if st.button("Submit"):
        if not name:
            st.error("Patient's name is required.")
        if gender=="None":
            st.error("Patient's gender can't be None")
        if age is None or age <= 0:
            st.error("Patient's age is required.")
        else:
            sub=True
        if sub==False:
            st.error("Patient's details not filled")

    if image is not None and sub==True :
        original_image, processed_image = process_image(image)

        # Display the original and processed images
        st.image(processed_image, caption='Enhanced Image', use_column_width=True)
        if abha==None:
            abha="None"
        a=work(processed_image)
                    # ic.insert_one({'name': name,'gender': gender,'age': age,'date': d,'time': t,'cancer': a[0][0],'normal': a[0][1],'OPMD': a[0][2], 'file_id': file_id})
        oi = image.resize((224, 224))
        img_byte_arr = BytesIO()
        oi.save(img_byte_arr, format='PNG') 
        image_binary = bson.Binary(img_byte_arr.getvalue())

        document = {'name': name,'gender': gender,'age': age,'abha': abha,'date': d,'time': t,'cancer': a[0],'normal': a[1],'OPMD': a[2],"image_data": image_binary}
        ic.insert_one(document)
        st.subheader(f"Details uploaded")            



if __name__ == "__main__":
    main()
