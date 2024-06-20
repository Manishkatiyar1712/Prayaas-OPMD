from fastapi import FastAPI, UploadFile, File
from pydantic import BaseModel
import numpy as np
from PIL import Image
import io
import tensorflow as tf
from tensorflow.keras.preprocessing.image import img_to_array
from tensorflow.keras.models import model_from_json
from tensorflow.keras.applications.mobilenet_v2 import preprocess_input
import base64


app = FastAPI()

class ImageInput(BaseModel):
    file: str

# Load the model architecture from JSON
with open('model.json', 'r') as json_file:
    model_json = json_file.read()

# Load the model weights
lm = model_from_json(model_json)
lm.load_weights('model_weights.keras')
lm.compile(optimizer=tf.keras.optimizers.Adam(learning_rate=0.0001),
           loss='categorical_crossentropy',
           metrics=['accuracy'])

@app.post("/predict")
async def predict(image_data: ImageInput):
    # Decode base64 image data to bytes
    img_bytes = base64.b64decode(image_data.file)
    
    # Open the image using PIL
    img_stream = io.BytesIO(img_bytes)
    img = Image.open(img_stream)
    
    # Resize the image to match the input size of the model
    img_resized = img.resize((224, 224))
    
    # Convert the image to a NumPy array
    img_array = img_to_array(img_resized)
    img_array = np.expand_dims(img_array, axis=0)  # Add batch dimension
    
    # Normalize the image array if needed (based on your training preprocessing)
    img_array = img_array / 255.0

    # Make prediction
    pred = lm.predict(img_array)

    # Convert probabilities to percentages
    pred_percent = pred * 100
    results=pred_percent.tolist()
    results = [item for sublist in results for item in sublist]
   
    
    return results

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8080)
