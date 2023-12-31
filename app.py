import streamlit as st
import numpy as np
import pandas as pd
import keras
from keras.utils.np_utils import to_categorical
from keras.models import Sequential, load_model
from keras import backend as K
import os
import time
import io
from PIL import Image
import plotly.express as px


MODELSPATH = './models/'
DATAPATH = './data/'


st.set_page_config(page_title='Skin Cancer Analysis')  
@st.cache(suppress_st_warning=True)
def load_mekd():
    img = Image.open(DATAPATH + '/ISIC_0024312.jpg')
    return img


@st.cache
def data_gen(x):
    img = np.asarray(Image.open(x).resize((100, 75)))
    x_test = np.asarray(img.tolist())
    x_test_mean = np.mean(x_test)
    x_test_std = np.std(x_test)
    x_test = (x_test - x_test_mean) / x_test_std
    x_validate = x_test.reshape(1, 75, 100, 3)

    return x_validate


@st.cache()
def data_gen_(img):
    img = img.reshape(100, 75)
    x_test = np.asarray(img.tolist())
    x_test_mean = np.mean(x_test)
    x_test_std = np.std(x_test)
    x_test = (x_test - x_test_mean) / x_test_std
    x_validate = x_test.reshape(1, 75, 100, 3)

    return x_validate


def load_models():

    model = load_model(MODELSPATH + 'model.h5')
    return model


@st.cache()
def predict(x_test, model):
    Y_pred = model.predict(x_test)
    ynew = model.predict(x_test)
    K.clear_session()
    ynew = np.round(ynew, 2)
    ynew = ynew*100
    y_new = ynew[0].tolist()
    Y_pred_classes = np.argmax(Y_pred, axis=1)
    K.clear_session()
    return y_new, Y_pred_classes


@st.cache()
def display_prediction(y_new):
    """Display image and preditions from model"""

    result = pd.DataFrame({'Probability': y_new}, index=np.arange(7))
    result = result.reset_index()
    result.columns = ['Classes', 'Probability']
    lesion_type_dict = {2: 'Benign keratosis-like lesions', 4: 'Normal Human Skin', 3: 'Dermatofibroma',
                        5: 'Melanoma', 6: 'Vascular lesions', 1: 'Basal cell carcinoma', 0: 'Actinic keratoses'}
    result["Classes"] = result["Classes"].map(lesion_type_dict)
    return result


def main():
    st.sidebar.header('Skin Cancer Analysis Image Recognition')
    st.sidebar.subheader('Skin Lesions Detectable:')
    st.sidebar.text('1. Normal Human Skin')
    st.sidebar.text('2. Melanoma')
    st.sidebar.text('3. Benign keratosis-like lesions')
    st.sidebar.text('4. Basal cell carcinoma')
    st.sidebar.text('5. Actinic keratoses')
    st.sidebar.text('6. Vascular lesions')
    st.sidebar.text('7. Dermatofibroma')        
      
                
option = st.selectbox(
     'How would you like to detect a disease?',
     ('Camera', 'Upload an Image'))
if option == 'Camera':
    picture = st.camera_input("Take a picture")
    
    if picture:
        x_test = data_gen(picture)
        image = Image.open(picture)
        img_array = np.array(image)
        st.success('File Upload Success!!')
        if st.button('Run Image Recognition'):
            import time

            my_bar = st.progress(0)

            for percent_complete in range(100):
                my_bar.progress(percent_complete + 1)
            st.image(picture)
            st.subheader("Loading Algorithm!")
            model = load_models()
            st.success("Hooray !! Keras Model Loaded!")
            st.subheader("Prediction Probability for Uploaded Image")
            y_new, Y_pred_classes = predict(x_test, model)
            result = display_prediction(y_new)
            st.write(result)
            st.subheader("Probability Graph")
            fig = px.bar(result, x="Classes",
            y="Probability", color='Classes')
            st.plotly_chart(fig, use_container_width=True)

    
else:
    file_path = st.file_uploader('Upload an image', type=['png', 'jpg'])
    if file_path is not None:
            x_test = data_gen(file_path)
            image = Image.open(file_path)
            img_array = np.array(image)

            st.success('File Upload Success!!')
            if st.button('Run Image Recognition'):
                import time
                my_bar = st.progress(0)
                for percent_complete in range(100):
                    my_bar.progress(percent_complete + 1)
                st.info("Showing Uploaded Image ---->>>")
                st.image(img_array, caption='Uploaded Image',
                     use_column_width=True)
                st.subheader("Loading Algorithm!")
                model = load_models()
                st.success("Hooray !! Keras Model Loaded!")
                st.subheader("Prediction Probability for Uploaded Image")
                y_new, Y_pred_classes = predict(x_test, model)
                result = display_prediction(y_new)
                st.write(result)
                st.subheader("Probability Graph")
                fig = px.bar(result, x="Classes",
                y="Probability", color='Classes')
                st.plotly_chart(fig, use_container_width=True)
        
            else:
                 st.info("Click the button to continue")
    else:
            st.info('Please upload Image file')

    

if __name__ == "__main__":
    main()
