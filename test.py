import streamlit as st
import os
from PIL import Image
from langchain_community.document_loaders import TextLoader,PyPDFLoader,Docx2txtLoader, UnstructuredPowerPointLoader,AssemblyAIAudioTranscriptLoader
import google.generativeai as genai
import mimetypes



# Configure the Google API key
genai.configure(api_key=st.secrets.GOOGLE_API_KEY)
# model = genai.GenerativeModel(model_name="gemini-1.5-flash")

# Assemblyai API key
api_key=st.secrets.ASSEMBLYAI_API_KEY


# Title of the app
st.title("📂 FileSence.AI")
st.subheader(" ",divider='rainbow')

# Sidebar instructions
st.write("### Upload your files")
st.write("Simply drag and drop your files (PDF, Docx, PPTx, Txt, JPG, JPEG, PNG, MP3, video) into the box below.")

def get_mime_type(filename):
    mime_type, _ = mimetypes.guess_type(filename)
    return mime_type

def renamer(uploaded_file,doc_data):
    prompt = f"Generate a compelling title for the document by summarizing it in no more than 3 words. Replace spaces with underscores and avoid any breaks between words. Document: {doc_data}"

    model = genai.GenerativeModel(model_name="gemini-1.5-flash")
    response = model.generate_content([prompt])

    file_extension = os.path.splitext(uploaded_file.name)[1]

    # Construct the filename using the response and file extension
    name = f"{response.text.strip().replace(' ', '_')}{file_extension}"

    # Read the file content as bytes
    file_content = uploaded_file.read()

    return name, file_content



# File uploader widget
uploaded_file = st.file_uploader("Upload Files", type=["pdf", "doc", "docx", "txt", "jpg", "jpeg", "png", "MP3", "video-mp4","pptx"])

# st.write(uploaded_file.type)

if uploaded_file is not None:
    st.write(uploaded_file.type)
    try:
        if uploaded_file.type in ["text/plain"]:
            # Save the uploaded file to a temporary location
            temp_file_path = "./temp/temp_uploaded.txt"
            with open(temp_file_path, "wb") as f:
                f.write(uploaded_file.getbuffer())
            
            # Load the file using TextLoader
            loader = TextLoader(temp_file_path)
            loaded_data = loader.load()
        
            # Display the content
            # for doc in loaded_data:
            #     st.write(doc)

            name, file_content = renamer(uploaded_file,loaded_data)

            # Provide a download button
            st.download_button(label=f"Download {name}", data=file_content, file_name=name, mime=get_mime_type(name))


        elif uploaded_file.type in ["application/pdf"]:

            temp_file_path = "temp_uploaded.pdf"
            with open(temp_file_path, "wb") as f:
                f.write(uploaded_file.getbuffer())

            loader = PyPDFLoader(temp_file_path)
            pages = loader.load_and_split()

            # for page in pages:
            #     st.write(page)

            name, file_content = renamer(uploaded_file,pages)

            st.download_button(label=f"Download {name}", data=file_content, file_name=name, mime=get_mime_type(name))

            
        elif uploaded_file.type in ['application/vnd.openxmlformats-officedocument.wordprocessingml.document']:

            temp_file_path = "temp_uploaded.docx"
            with open(temp_file_path, "wb") as f:
                f.write(uploaded_file.getbuffer())

            loader = Docx2txtLoader(temp_file_path)
            data = loader.load()

            # for doc in data:
            #     st.write(doc)

            name, file_content = renamer(uploaded_file,data)

            st.download_button(label=f"Download {name}", data=file_content, file_name=name, mime=get_mime_type(name))

        
        elif uploaded_file.type in ['application/vnd.openxmlformats-officedocument.presentationml.presentation']:

            temp_file_path = "temp_uploaded.pptx"
            with open(temp_file_path, "wb") as f:
                f.write(uploaded_file.getbuffer())

            loader = UnstructuredPowerPointLoader(temp_file_path)
            data = loader.load()

            # st.write(data)

            name, file_content = renamer(uploaded_file,data)

            st.download_button(label=f"Download {name}", data=file_content, file_name=name, mime=get_mime_type(name))


        elif uploaded_file.type in ['audio/mpeg']:

            temp_file_path = "temp_uploaded.mp3"
            with open(temp_file_path, "wb") as f:
                f.write(uploaded_file.getbuffer())

            loader = AssemblyAIAudioTranscriptLoader(temp_file_path,api_key=api_key)

            docs = loader.load()

            st.write(docs[0].page_content)

            # st.write(data)

            name, file_content = renamer(uploaded_file,docs[0].page_content)

            st.download_button(label=f"Download {name}", data=file_content, file_name=name, mime=get_mime_type(name))


        elif uploaded_file.type in ["image/jpeg", "image/png","image/jpg"]:
            # Extract the file extension
            file_extension = os.path.splitext(uploaded_file.name)[1]

            # Load and display the image
            image = Image.open(uploaded_file)
            st.image(image, caption='Uploaded Image', use_column_width=True)

            # Generate a prompt for the generative model
            prompt = f"Your task is to give a short title for the image related to the content in the image having at most 3 words. There should not be any break between words, use '_' instead of blank spaces."

            # Initialize and use the generative model for the image
            model = genai.GenerativeModel(model_name="gemini-1.5-flash")
            response = model.generate_content([prompt, image])

            # Construct the filename using the response and file extension
            name = f"{response.text.strip().replace(' ', '_')}{file_extension}"
            # name = f"{response.text}{file_extension}"

            # Read the file content as bytes
            file_content = uploaded_file.read()

            # Provide a download button
            st.download_button(label=f"Download {name}", data=file_content, file_name=name, mime=get_mime_type(name))

        else:
            st.warning("File not supprted")


    except Exception as e:
        st.error(f"Error loading file: {e}")










