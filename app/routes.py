from flask import render_template, redirect, url_for, session, request, json, make_response
from app import app, db
from app.forms import RegistrationForm, LoginForm, fileUpload, AskAI
from app.models import User, UserResponse, Image
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
import cv2
import numpy as np
import tensorflow as tf
import time
import os
import re
import datetime
# import openai

# openai.api_key = ""


@app.route("/")
def homepage():
    if 'user_id' in session:
        user_row = User.query.get(session['user_id'])
        if user_row.questionaire_filled:
            return redirect(url_for('dashboard'))
        return redirect(url_for('questions'))
    user = User.query.filter_by(id=session['user_id']).first() if 'user_id' in session else None
    return render_template("index.html", user=user)

@app.route("/signup", methods=['GET', 'POST'])
def signup():
    if 'user_id' in session:
        user_row = User.query.get(session['user_id'])
        if user_row.questionaire_filled:
            return redirect(url_for('dashboard'))
        return redirect(url_for('questions'))
    form = RegistrationForm()
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        confirm_password = request.form['confirm_password']
        name = request.form['name']
        
        # Check if the username is already taken
        if User.query.filter_by(email=email).first():
            return render_template('signup.html', error='Email already exists', form=form)
        if password != confirm_password:
            return render_template('signup.html', error='Password not same as confirm password. Try again!', form=form)
        
        # Create a new user
        new_user = User(name=name ,email=email, password=generate_password_hash(password))
        db.session.add(new_user)
        db.session.commit()
        print("User created successfully")

        sanitized_email = re.sub(r'[^a-zA-Z0-9]', '_', email)
        os.makedirs("app/static/assets/uploads/" + sanitized_email)
        print("Directory created successfully")


        # Find the user by username
        user = User.query.filter_by(email=email).first()
        session['user_id'] = user.id
        print("Login successful")

        return redirect(url_for('questions'))
    return render_template("signup.html", form=form)

@app.route("/login", methods=['GET', 'POST'])
def login():
    if 'user_id' in session:
        user_row = User.query.get(session['user_id'])
        if user_row.questionaire_filled:
            return redirect(url_for('dashboard'))
        return redirect(url_for('questions'))
    form = LoginForm()
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        
        # Find the user by username
        user = User.query.filter_by(email=email).first()
        
        # Check if the user exists and the password is correct
        if user and check_password_hash(user.password, password):
            session['user_id'] = user.id
            user_row = User.query.get(user.id)
            if user_row.questionaire_filled:
                return redirect(url_for('dashboard'))
            return redirect(url_for('questions'))
        else:
            return render_template('login.html', error='Invalid email or password', form=form)
    if request.args.get('message'):
        message = request.args.get('message')
        print(message)
        return render_template('login.html', form=form, message=message)
    return render_template('login.html', form=form)

@app.route("/questions", methods=['GET', 'POST'])
def questions():
    if 'user_id' not in session:
        return redirect(url_for('login', message='Please login to continue'))
    user_row = User.query.get(session['user_id'])
    if user_row.questionaire_filled:
        return redirect(url_for('dashboard'))
    user = User.query.filter_by(id=session['user_id']).first()
    return render_template("questions.html", user=user)

@app.route("/submitform", methods=['POST'])
def submitform():
    # Get the form data
    data = request.json
    print(data)
    q_1 = data['q_1']
    q_2 = data['q_2']
    q_3 = data['q_3']

    try:
        q_4 = data['q_4']
    except:
        q_4 = "None"
    try:
        q_5_breathing = data['q_5_breathing']
    except:
        q_5_breathing = "No"

    try:
        q_5_chest = data['q_5_chest']
    except:
        q_5_chest = "No"

    try:
        q_5_speech = data['q_5_speech']
    except:
        q_5_speech = "No"

    try:
        q_5_pale = data['q_5_pale']
    except:
        q_5_pale = "No"
    try:
        q_5_none = data['q_5_none']
    except:
        q_5_none = "No"

    print("Form submitted successfully")
    print(q_1, q_2, q_3, q_4, q_5_breathing, q_5_chest, q_5_speech, q_5_pale, q_5_none)
    user_id = session['user_id']

    # Add date to the UserResponse table
    date = datetime.datetime.now()

    # Create a new response
    new_response = UserResponse(user_id=user_id, q_1=q_1, q_2=q_2, q_3=q_3, q_4=q_4, q_5_breathing=q_5_breathing, q_5_chest=q_5_chest, q_5_speech=q_5_speech, q_5_pale=q_5_pale, q_5_none=q_5_none, date_created=date)
    user_row = User.query.get(user_id)
    user_row.questionaire_filled = True
    db.session.add(new_response)
    db.session.commit()

    # Return a response if needed
    response = {'message': 'Form submitted successfully'}
    return json.dumps(response)
    
    
@app.route('/logout')
def logout():
    session.pop('user_id', None)
    print("Logout successful")
    return redirect(url_for('homepage'))

@app.route('/dashboard')
def dashboard():
    form = fileUpload()
    if 'user_id' not in session:
        return redirect(url_for('login', message='Please login to continue'))
    user_row = User.query.get(session['user_id'])
    if user_row.questionaire_filled == False:
        return redirect(url_for('questions'))
    user = User.query.filter_by(id=session['user_id']).first()

    # Fetching all the images of the current user
    images = Image.query.filter_by(user_id=session['user_id']).all()
    image_paths = []
    image_results = []
    dates = []
    gptResponses = []
    for image in images:
        image_path = image.image_path
        image_path = image_path.replace("app/static/", "")
        image_result = image.result
        date = image.date
        image_paths.append(image_path)
        image_results.append(image_result)
        dates.append(date)
        gptResponses.append((image.gptResponse))
    print("Image paths")
    print(image_paths)

    if len(image_paths) == 0:
        return render_template('dashboard.html', user=user, form=form)
    return render_template('dashboard.html', user=user, form=form, image_paths = image_paths, image_results=image_results, dates=dates, gptResponses=gptResponses)

def preprocess(image):
  image = cv2.imread(image)
  image = image / 255.0
  image = cv2.resize(image,(100,100))
  return image

@app.route('/dashboard/upload', methods=['GET', 'POST'])
def image_processing():
    form = fileUpload()
    if 'user_id' not in session:
        return redirect(url_for('login', message='Please login to continue'))
    user_row = User.query.get(session['user_id'])
    if user_row.questionaire_filled == False:
        return redirect(url_for('questions'))
    
    # Get date_created from UserResponse table
    date_created = UserResponse.query.filter_by(user_id=session['user_id']).first().date_created

    # Get the current date
    current_date = datetime.datetime.now()

    # Get the difference between the current date and date_created
    difference = current_date - date_created
    print("Difference: ")
    print(difference.days)

    # If the difference is less than 7 days, then redirect to dashboard. Else redirect to questions
    if difference.days > 7:
        user_row.questionaire_filled = False
        db.session.commit()
        return redirect(url_for('questions'))
    
    user = User.query.filter_by(id=session['user_id']).first()
    user_id = session['user_id']

    if request.method == "POST":
        model = tf.keras.models.load_model('app/saved_model')
        print("Model loaded successfully")
        print(model)
        uploaded_file = request.files["file"]
        # uploaded_file.save(uploaded_file.filename)
        sanitized_email = re.sub(r'[^a-zA-Z0-9]', '_', user.email)
        file_directory = "app/static/assets/uploads/" + sanitized_email + "/" + uploaded_file.filename
        print(file_directory)
        uploaded_file.save(file_directory)
        print("File saved successfully")
        print(uploaded_file.filename)

        preprocessed_input = preprocess(str(file_directory))
        preprocessed_input = np.expand_dims(preprocessed_input, axis=0)
        predictions = model.predict(preprocessed_input)
        print(predictions)
        # Assuming 'predictions' is the output from your model
        predicted_prob_class_1 = predictions[0][0]

        # Calculate the complementary probability for class 0
        predicted_prob_class_0 = 1.0 - predicted_prob_class_1

        # Define the class labels
        class_labels = [0, 1]

        # Apply a threshold (0.5) to make the final prediction
        threshold = 0.5

        if predicted_prob_class_1 >= threshold:
            predicted_class = class_labels[1]  # Class 1
            result = "Positive"
        else:
            predicted_class = class_labels[0]  # Class 0
            result = "Negative"

        print("Predicted Class:", result)

        date = datetime.datetime.now()
        saved_image = Image(image_path=file_directory, result=result, user_id=user_id, date=date)
        db.session.add(saved_image)
        db.session.commit()

        # Fetching all the images of the current user
        images = Image.query.filter_by(user_id=session['user_id']).all()
        image_paths = []
        image_results = []
        dates = []
        gptResponses = []
        for image in images:
            image_path = image.image_path
            image_path = image_path.replace("app/static/", "")
            image_result = image.result
            date = image.date
            image_paths.append(image_path)
            image_results.append(image_result)
            dates.append(date)

        # Getting answers from User Response model for the current user
        user_response = UserResponse.query.filter_by(user_id=session['user_id']).first()
        q_1 = user_response.q_1
        q_2 = user_response.q_2
        q_3 = user_response.q_3
        q_4 = user_response.q_4
        q_5_breathing = user_response.q_5_breathing
        q_5_chest = user_response.q_5_chest
        q_5_speech = user_response.q_5_speech
        q_5_pale = user_response.q_5_pale
        q_5_none = user_response.q_5_none
        print(q_1, q_2, q_3, q_4, q_5_breathing, q_5_chest, q_5_speech, q_5_pale, q_5_none)

        print(q_5_none)
        if q_5_none == "None":
            message = [ {"role": "system", "content": "I'll give you answer to five questions. First question is 'Have you recently been in close contact with someone who has COVID-19?', Second question is 'Are you experiencing a high fever, dry cough, tiredness and loss of taste or smell?', third question is 'Are you having diarrhoea, stomach pain, conjunctivitis, vomiting and headache?', fourth questions is 'Have you traveled to any of these countries with the highest number of COVID-19 cases in the world for the past 2 weeks?' For this question, depending on the country I have travelled, tell me what variant I might have, and the last question is 'Are you experiencing any of these serious  symptoms of COVID-19 below? (there are 5 options to this questions and user can select multiple options)'. The five options for the last question are Difficulty breathing or shortness of breath, Chest pain or pressure, Loss of speech or movement, and Pale, gray or blue-colored skin, lips or nail beds. For the last question, the user can select multiple options. Based on each answer, what is the likelihood of me being in a very critical condition and why. Also mention what I can do to feel better, heal quickly, and protect the people around me from getting the disease from me. Give your response as bullet points. If I'm covid negative, in the start of the message, mention that there is not much to worry because the report looks good."},
                    {"role": "user", "content": 'I am COVID ' + result + '. My answer to the first question is:' + q_1 + '. My answer to the second question is '+ q_2 + '. My answer to the third question is ' + q_3+ '. I have travelled to ' + q_4 + '. The answer to "Do I have any Difficulty breathing or shortness of breath"? is ' + q_5_breathing + '. The answer to "Do I have any Chest pain or pressure?" is ' + q_5_chest + '. The answer to "Do I have any Loss of speech or movement?" is ' + q_5_speech + '. The answer to "Do I have Pale, gray or blue-colored skin, lips or nail beds?" is ' + q_5_pale + '. '}
                    ]
            print(message)
        else:
            message = [ {"role": "system", "content": " I'll give you answer to five questions. First question is 'Have you recently been in close contact with someone who has COVID-19?', Second question is 'Are you experiencing a high fever, dry cough, tiredness and loss of taste or smell?', third question is 'Are you having diarrhoea, stomach pain, conjunctivitis, vomiting and headache?', fourth questions is 'Have you traveled to any of these countries with the highest number of COVID-19 cases in the world for the past 2 weeks?' and the last question is 'Are you experiencing any of these serious  symptoms of COVID-19 below? (there are 5 options to this questions and user can select multiple options)'. The five options for the last question are Difficulty breathing or shortness of breath, Chest pain or pressure, Loss of speech or movement, and Pale, gray or blue-colored skin, lips or nail beds. For the last question, the user can select multiple options. Based on each answer, what is the likelihood of me being in a very critical condition and why. Also mention what I can do to feel better, heal quickly, and protect the people around me from getting the disease from me. Give your response as bullet points. If I'm covid negative, in the start of the message, mention that there is not much to worry because the report looks good."},
                    {"role": "user", "content": 'I am COVID ' + result + '. My answer to the first question is:' + q_1 + '. My answer to the second question is '+ q_2 + '. My answer to the third question is ' + q_3+ '. I have travelled to ' + q_4 + '. Tell me which COVID variant was viral in '+ q_4 +'. The answer to "Do I have any Difficulty breathing or shortness of breath"? is ' + q_5_breathing + '. The answer to "Do I have any Chest pain or pressure?" is ' + q_5_chest + '. The answer to "Do I have any Loss of speech or movement?" is ' + q_5_speech + '. The answer to "Do I have Pale, gray or blue-colored skin, lips or nail beds?" is ' + q_5_pale + '. '}
                    ]
            print(message)
        
        chat = openai.ChatCompletion.create(
            model="gpt-3.5-turbo-16k", messages=message
        )

        reply = chat.choices[0].message.content
        reply = reply.replace("\n", "")
        print(reply)

        # Savt the reply to gptResponse column in Image table
        image = Image.query.filter_by(image_path=file_directory).first()
        image.gptResponse = reply
        db.session.commit()

        for image in images:
            gptResponses.append(image.gptResponse)


        # sleep for 10 seconds
        time.sleep(1)
        return render_template('dashboard.html', user=user, form=form, result=result, image_paths = image_paths, image_results=image_results, dates=dates, reply=reply, some_text=reply, gptResponses=gptResponses)
    return render_template('dashboard.html', user=user, form=form)

@app.route('/chat', methods=['GET', 'POST'])
def chat():
    form = AskAI()
    user = User.query.filter_by(id=session['user_id']).first()

    # Get URL parameters
    current_image_path = request.args.get('image_paths')

    return render_template('chatbot.html', form=form, user=user, current_image_path=current_image_path)

@app.route("/api/askai", methods=['GET', 'POST'])
def api():
    form = AskAI()
    user = User.query.filter_by(id=session['user_id']).first()
    if request.method == 'POST':
        question = request.form['text']
        print("We are here")
        # Get URL parameters
        current_image_path = request.args.get('current_image')

        # Fetch the image description using the current_image
        current_image = Image.query.filter_by(image_path=current_image_path).first()

        # Fetch the gptResponse from the current_image
        gptResponse = current_image.gptResponse

        message = [ {"role": "system", "content": "I want you to act as a doctor who can give some home remedies to me. The next message will have two parts. The first part is a response generated by you based on some answers that I gave previosly. The second part is the question that I have asked. Generate upto 3 advices and make it consice and short."},
                    {"role": "user", "content": " The description of the image is " + gptResponse + ". The question that I have asked is " + question + "."}
                    ]
        
        chat = openai.ChatCompletion.create(
            model="gpt-3.5-turbo-16k", messages=message
        )

        advice = chat.choices[0].message.content

        return render_template('chatbot.html', user=user, form=form, advice=advice, current_image=current_image_path)