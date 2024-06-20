import streamlit as st
from pymongo import MongoClient
import matplotlib.pyplot as plt
from PIL import Image
from bson import ObjectId
import os
from dotenv import load_dotenv
import numpy as np
import io
import bson.binary
from matplotlib.backends.backend_pdf import PdfPages

# Example list of users (in a real application, use a secure method to store passwords)
users = {
    "man": "123",
    "shriya": "iihmrb",
    "akash": "prabhune"
}

def check_credentials(username, password):
    if username in users and users[username] == password:
        return True
    return False

# Streamlit app
def main():
    # Initialize session state for login
    if "logged_in" not in st.session_state:
        st.session_state.logged_in = False
        st.session_state.username = ""

    # Placeholder for the logout button
    logout_placeholder = st.empty()

    # If authenticated, show the logout button at the top right
    if st.session_state.logged_in:
        st.sidebar.success("Login successful")
        with logout_placeholder.container():
            col1, col2 = st.columns([30, 4])
            with col2:
                if st.button("Logout"):
                    st.session_state.logged_in = False
                    st.experimental_rerun()
        st.title("Welcome Admin, {}".format(st.session_state.username))

    

    # Show login form if not authenticated
    if not st.session_state.logged_in:
        st.sidebar.title("Login")
        username = st.sidebar.text_input("Username")
        password = st.sidebar.text_input("Password", type="password")
        if st.sidebar.button("Login"):
            if check_credentials(username, password):
                st.session_state.logged_in = True
                st.session_state.username = username
                # st.sidebar.success("Login successful")
                st.rerun()
            else:
                st.sidebar.error("Invalid username or password")

    # If authenticated, show the main content
    if st.session_state.logged_in:
        load_dotenv()
        os.environ['MONGO_URI'] = 'mongodb+srv://interns:iihmr123@cluster0.gzuy93a.mongodb.net/'

        MONGO_URI = os.getenv("MONGO_URI")

        if not MONGO_URI:
            raise ValueError("No MONGO_URI found. Please set the MONGO_URI environment variable.")
        client = MongoClient(MONGO_URI)
        db = client['iihmr']
        ic = db['patientinfo']
        cursor = ic.find()

        # Initialize lists to store information
        names = []
        genders = []
        ages = []
        dates = []
        times = []
        cancers = []
        normals = []
        opmds = []
        images = []

        # Iterate over the documents
        for document in cursor:
            # Retrieve information from the document
            names.append(document["name"])
            genders.append(document["gender"])
            ages.append(document["age"])
            dates.append(document["date"])
            times.append(document["time"])
            cancers.append(round(document["cancer"], 2))  
            normals.append(round(document["normal"], 2))  
            opmds.append(round(document["OPMD"], 2))
            
            # Convert binary data into an image
            image_data = document["image_data"]
            image = Image.open(io.BytesIO(image_data))
            images.append(image)

        # Create a table using matplotlib
        num_rows = len(names)
        fig, ax = plt.subplots(num_rows, 9, figsize=(20, num_rows * 3))

        # Set column titles
        columns = ['Name', 'Gender', 'Age', 'Date', 'Time', 'Cancer', 'Normal', 'OPMD', 'Image']
        for i, column in enumerate(columns):
            if num_rows == 1:
                ax[i].set_title(column)
            else:
                ax[0, i].set_title(column)

        # Iterate over the rows of the table
        for i in range(num_rows):
            if num_rows == 1:
                # Plot name
                ax[0].text(0.5, 0.5, f"{names[i]}", ha='center', va='center', fontsize=12)
                ax[0].axis('off')
                
                # Plot gender
                ax[1].text(0.5, 0.5, f"{genders[i]}", ha='center', va='center', fontsize=12)
                ax[1].axis('off')
                
                # Plot age
                ax[2].text(0.5, 0.5, f"{ages[i]}", ha='center', va='center', fontsize=12)
                ax[2].axis('off')
                
                # Plot date
                ax[3].text(0.5, 0.5, f"{dates[i]}", ha='center', va='center', fontsize=12)
                ax[3].axis('off')
                
                # Plot time
                ax[4].text(0.5, 0.5, f"{times[i]}", ha='center', va='center', fontsize=12)
                ax[4].axis('off')
                
                # Plot cancer
                ax[5].text(0.5, 0.5, f"{cancers[i]}", ha='center', va='center', fontsize=12)
                ax[5].axis('off')
                
                # Plot normal
                ax[6].text(0.5, 0.5, f"{normals[i]}", ha='center', va='center', fontsize=12)
                ax[6].axis('off')
                
                # Plot OPMD
                ax[7].text(0.5, 0.5, f"{opmds[i]}", ha='center', va='center', fontsize=12)
                ax[7].axis('off')
                
                # Plot image
                ax[8].imshow(images[i])
                ax[8].axis('off')
            else:
                # Plot name
                ax[i, 0].text(0.5, 0.5, f"{names[i]}", ha='center', va='center', fontsize=12)
                ax[i, 0].axis('off')
                
                # Plot gender
                ax[i, 1].text(0.5, 0.5, f"{genders[i]}", ha='center', va='center', fontsize=12)
                ax[i, 1].axis('off')
                
                # Plot age
                ax[i, 2].text(0.5, 0.5, f"{ages[i]}", ha='center', va='center', fontsize=12)
                ax[i, 2].axis('off')
                
                # Plot date
                ax[i, 3].text(0.5, 0.5, f"{dates[i]}", ha='center', va='center', fontsize=12)
                ax[i, 3].axis('off')
                
                # Plot time
                ax[i, 4].text(0.5, 0.5, f"{times[i]}", ha='center', va='center', fontsize=12)
                ax[i, 4].axis('off')
                
                # Plot cancer
                ax[i, 5].text(0.5, 0.5, f"{cancers[i]}", ha='center', va='center', fontsize=12)
                ax[i, 5].axis('off')
                
                # Plot normal
                ax[i, 6].text(0.5, 0.5, f"{normals[i]}", ha='center', va='center', fontsize=12)
                ax[i, 6].axis('off')
                
                # Plot OPMD
                ax[i, 7].text(0.5, 0.5, f"{opmds[i]}", ha='center', va='center', fontsize=12)
                ax[i, 7].axis('off')
                
                # Plot image
                ax[i, 8].imshow(images[i])
                ax[i, 8].axis('off')

        plt.tight_layout()
        st.pyplot(fig)
        pdf_buffer = io.BytesIO()
        with PdfPages(pdf_buffer) as pdf:
            pdf.savefig(fig)
            plt.close(fig)
        pdf_buffer.seek(0)

        # Streamlit app
        st.title("Data Table with Downloadable PDF")

        st.write("The table has been generated. You can view it below and download it as a PDF file.")

        # Display the DataFrame
        # st.dataframe(df)

        # Provide download button
        st.download_button(
            label="Download PDF",
            data=pdf_buffer,
            file_name="alldata.pdf",
            mime="application/pdf"
        )

if __name__ == "__main__":
    main()