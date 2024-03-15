import os
from platform import processor
from flask import Flask,request,jsonify,render_template,redirect,url_for,session
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash,check_password_hash
import openai
import secrets
import logging
from datetime import datetime
from flask import flash
from difflib import SequenceMatcher
import time

app = Flask(__name__)
app.secret_key = secrets.token_hex(16)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

openai.api_key = "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"

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(128), nullable=False)
    role = db.Column(db.String(20), nullable=False)

@app.route('/')
def home():
    return render_template('login.html')
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        data = request.form
        username = data.get('username')
        password = data.get('password')

        user = User.query.filter_by(username=username).first()
        if user and check_password_hash(user.password, password):
            session['username'] = username
            return redirect(url_for('chatbot'))
        else:
            flash('Invalid username or password', 'error')
            return render_template('login.html')

    else:
        return render_template('login.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if 'username' not in session:
        return redirect(url_for('login'))
    if request.method == 'GET':
        return render_template('signup.html')
    elif request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        role = request.form['role']

        if not username or not password:
            flash('Username and password cannot be empty', 'error')
            return render_template('signup.html')

        if User.query.filter_by(username=username).first():
         flash('Username already exists', 'error')
         return render_template('signup.html')


        hashed_password = generate_password_hash(password)
        new_user = User(username=username, password=hashed_password, role=role)
        db.session.add(new_user)
        db.session.commit()
        flash('User created successfully', 'success')
        return redirect(url_for('login'))

@app.route('/chatbot', methods=['GET', 'POST'])
def chatbot():
    if request.method == 'GET':
        username = session.get('username')
        if not username:
            return redirect(url_for('login'))
        return render_template('chatbot.html', username=username)
    
    elif request.method == 'POST':
        data = request.json
        message = data.get('message')
        if not message:
            return jsonify({'error': 'Message is missing'}), 400
        
        try:
            chatbot_response = call_chatgpt_api(message)
            
            return jsonify({'chat_message': chatbot_response}), 200
        except Exception as e:
            logging.error(f'Error calling chatbot API: {str(e)}')  # Log the error
            return jsonify({'error': str(e)}), 500
    else:
        return jsonify({'error': 'Method not allowed'}), 405



def call_chatgpt_api(message):
    try:
        match_threshold = 0.70
        
        responses = {
    "kgisl institute of technology": "KGiSL Institute of Technology (KiTE) is a private engineering college started in 2008 by G. Bakthavathsalam, Founder-Chairman of KG Hospital. It is located at Saravanampatti in Coimbatore, Tamil Nadu, India. The college is affiliated to Anna University. It offers various undergraduate and postgraduate courses leading to the Degree of Bachelor of Engineering (B.E).",
    "details about kgisl institute of technology": "KGiSL Institute of Technology (KiTE) is a private engineering college started in 2008 by G. Bakthavathsalam, Founder-Chairman of KG Hospital. It is located at Saravanampatti in Coimbatore, Tamil Nadu, India. The college is affiliated to Anna University. It offers various undergraduate and postgraduate courses leading to the Degree of Bachelor of Engineering (B.E).",

    "who is the founder of kgisl institute of technology credentials": "The founder of KGiSL Institute of Technology is Dr. G. Bakthavathsalam, who holds credentials including MS, FICS, FCCP, FAMS, FMMC, and is also the Founder-Chairman of KG Hospital.",
    "where is kite located?": "KiTE Address: 365, Kgisl Campus, near Thudiyalur Road, Saravanampatti, Coimbatore, Tamil Nadu 641035",
    "main objective of kgisl institute of technology?": "The main objective of KGiSL Institute of Technology is to provide industry-embedded education, mold students for leadership in various sectors, and influence the future of engineering education and practice.",
    "can you tell me about the infrastructure at kite?": "KiTE boasts a 40-acre campus integrating institute-industry infrastructure.",
    "quality policy of kgisl institute of technology?": "The quality policy of KGiSL Institute of Technology is centered on pursuing global standards of excellence in all endeavors encompassing teaching, research, consultancy, entrepreneurship, and continuing education, with accountability to stakeholders through periodic evaluation and continual improvement.",
    "vision of kgisl institute of technology?": "The vision of KGiSL Institute of Technology is to be recognized as a renowned technical institution for transforming young minds into competent professionals to serve the industry and society.",
    "key administrators at kgisl institute of technology?": "The key administrators at KGiSL Institute of Technology include Dr. Ashok Bakthavathsalam as the Managing Trustee, Dr. P. Shankar as the Director of Academics & Administration, Dr. N. Rajkumar as the Secretary, and Dr. S. Suresh Kumar as the Principal.",
    "Who is the priciple of kite":"Dr. S. Suresh Kumar – Accomplished, Professor, Ph.D., C. Eng., MIEEE., MIET., MIETE, MIE., MIAENG, MSESI, MBMESI, MAEMP, MSEEM, MAES., MISCA., MACCS., MSSI., MCSI., MISTE., with over 31 years of Experience in Education, Research and Development in a range of areas such as Power Electronics & Drives, Power Quality, Renewable Energy (RE) Technologies, Signal & Image Processing, Embedded Systems and IoT.",
    "Who is the priciple of kgisl institute of technology":"Dr. S. Suresh Kumar is the priciple of kgisl institute of technology, Who has – Accomplished, Professor, Ph.D., C. Eng., MIEEE., MIET., MIETE, MIE., MIAENG, MSESI, MBMESI, MAEMP, MSEEM, MAES., MISCA., MACCS., MSSI., MCSI., MISTE., with over 31 years of Experience in Education, Research and Development in a range of areas such as Power Electronics & Drives, Power Quality, Renewable Energy (RE) Technologies, Signal & Image Processing, Embedded Systems and IoT.",
    "Director of Academics & Administration":"Dr P.Shankar is presently Director (Academics & Administration) at KGISL Institute of Technology, Saravanampatti, Coimbatore. He was formerly the Founding Principal at Amrita School of Engineering, Chennai campus from 2019 to 2022. He was also associated with Saveetha University as the Principal of School of Engineering from 2010 to 2016.",
    "Director of kgisl institute of technology":"Dr P.Shankar is presently Director (Academics & Administration) at KGISL Institute of Technology, Saravanampatti, Coimbatore. He was formerly the Founding Principal at Amrita School of Engineering, Chennai campus from 2019 to 2022. He was also associated with Saveetha University as the Principal of School of Engineering from 2010 to 2016.",
    # Programs Section
    "departments offered by kgisl institute of technology":"We offer various undergraduate programs including B.E. Computer Science and Engineering, B.E. Electronics and Communication Engineering, B.E. Mechanical Engineering, B.Tech. Artificial Intelligence and Data Science, B.Tech. Computer Science and Business Systems, and B.Tech. Information Technology. Our postgraduate programs include M.E. Applied Electronics, M.E. Computer Science and Engineering, and Masters in Business Administration (MBA)",

    "Undergraduate Programs" : "We offer various undergraduate programs including B.E. Computer Science and Engineering, B.E. Electronics and Communication Engineering, B.E. Mechanical Engineering, B.Tech. Artificial Intelligence and Data Science, B.Tech. Computer Science and Business Systems, and B.Tech Information Technology. ",
    "Postgraduate Programs": "Our postgraduate programs include M.E. Applied Electronics, M.E. Computer Science and Engineering, and Masters in Business Administration (MBA).",
    "Courses offered by kgisl institute of technology":"We offer various undergraduate programs including B.E. Computer Science and Engineering, B.E. Electronics and Communication Engineering, B.E. Mechanical Engineering, B.Tech. Artificial Intelligence and Data Science, B.Tech. Computer Science and Business Systems, and B.Tech. Information Technology. Our postgraduate programs include M.E. Applied Electronics, M.E. Computer Science and Engineering, and Masters in Business Administration (MBA)",
    "Undergraduate courses offered by kgisl institute of technology": "We offer various undergraduate programs including B.E. Computer Science and Engineering, B.E. Electronics and Communication Engineering, B.E. Mechanical Engineering, B.Tech. Artificial Intelligence and Data Science, B.Tech. Computer Science and Business Systems, and B.Tech. Information Technology.",
    "Postgraduate courses offered by kgisl institute of technology": "Our postgraduate programs include M.E. Applied Electronics, M.E. Computer Science and Engineering, and Masters in Business Administration (MBA).",
    "Ug courses offered by kgisl institute of technology": "We offer various undergraduate programs including B.E. Computer Science and Engineering, B.E. Electronics and Communication Engineering, B.E. Mechanical Engineering, B.Tech. Artificial Intelligence and Data Science, B.Tech. Computer Science and Business Systems, and B.Tech. Information Technology.",
    "Pg courses offered by kgisl institute of technology": "Our postgraduate programs include M.E. Applied Electronics, M.E. Computer Science and Engineering, and Masters in Business Administration (MBA).",
    "Undergraduate programs offered by kgisl institute of technology": "We offer various undergraduate programs including B.E. Computer Science and Engineering, B.E. Electronics and Communication Engineering, B.E. Mechanical Engineering, B.Tech. Artificial Intelligence and Data Science, B.Tech. Computer Science and Business Systems, and B.Tech. Information Technology.",
    "Postgraduate programs offered by kgisl institute of technology": "Our postgraduate programs include M.E. Applied Electronics, M.E. Computer Science and Engineering, and Masters in Business Administration (MBA).",
    "Ug programs offered by kgisl institute of technology": "We offer various undergraduate programs including B.E. Computer Science and Engineering, B.E. Electronics and Communication Engineering, B.E. Mechanical Engineering, B.Tech. Artificial Intelligence and Data Science, B.Tech. Computer Science and Business Systems, and B.Tech. Information Technology.",
    "Pg programs offered by kgisl institute of technology": "Our postgraduate programs include M.E. Applied Electronics, M.E. Computer Science and Engineering, and Masters in Business Administration (MBA).",

    # Ph.D Programs
    "PhD Programs offered by Kite": "We offer Ph.D programs in Computer Science and Engineering, and Electronics and Communication Engineering.",

    # Admissions Section
    "Admission Contact Number": "For admissions, you can contact us at +91-90952 44488 / +91-89399 26761 / +91-90809 27613.",
    "Admission Email": "For any admission-related queries, you can email us at admission@kgkite.ac.in.",
    "Admission Address": "Our address is KGiSL Institute of Technology, KG Information Systems Private Limited KGiSL Campus, 365, Thudiyalur Road, Saravanampatti, Coimbatore – 641035.",
    "Admission AdmissionEnquiryFormLink": "You can fill out the admission enquiry form by visiting the link: [Admission Enquiry Form](Link for admission enquiry form).",
    # Requirements Section
    "EntryRequirements_BE_BTech_OtherCommunities": "To qualify for admission, candidates from other communities must pass the 12th standard or equivalent with an aggregate of at least 50% marks in Mathematics, Physics & Chemistry.",
    "EntryRequirements_BE_BTech_BackwardClassCommunity": "Candidates from backward class communities must pass the 12th standard or equivalent with an aggregate of at least 45% marks in Mathematics, Physics & Chemistry. The candidate should produce the Community Certificate duly signed by the Tahsildar.",
    # Admission Documents Required
    "AdmissionRequirements_UndergraduateAdmission_DocumentsRequired": "The documents required for undergraduate admission include Statement of marks of the qualifying examinations, Transfer Certificate, Conduct Certificate, Community Certificate, Migration Certificate (for candidates passed other than HSC of Tamil Nadu), Diploma Mark statements (for Lateral Entry Only), SSLC Mark Statement (for Lateral Entry Only), and Passport size Photographs.",
    "AdmissionRequirements_PostgraduateAdmission_DocumentsRequired": "The documents required for postgraduate admission include Transfer Certificate, Provisional / Degree Certificate, UG Mark Statements, TANCET / CET score card, Conduct Certificate, Community Certificate, Migration Certificate (for candidates passed HSC / +2 of other than Tamil Nadu State), and Passport size Photographs.",
    # Certificate Verification
    "EquivalenceCertificate": "An Equivalency Certificate issued by the DOTE (Directorate of Technical Education); Chennai – 25 should be provided for the students who studied HSC (or) Equivalent abroad and other Private Bodies of any state.",
    "CertificateVerification_UndergraduateAdmission_DocumentsRequired": "The documents required for undergraduate admission verification include SSLC/ 10th Mark Statement, HSC / +2 Mark Statement, Diploma Certificate (For Lateral Entry), Diploma All Semester Marksheet (For Lateral Entry), Transfer Certificate, Community Certificate, and Recent Passport Size Photographs.",
    "CertificateVerification_PostgraduateAdmission_DocumentsRequired": "The documents required for postgraduate admission verification include SSLC/ 10th Mark Statement, HSC / +2 Mark Statement, UG Degree / Provisional Certificate, Consolidated Grade Sheet/ All semester Grade Sheet, Transfer Certificate, Community Certificate, and Recent Passport Size Photographs.",
    "Information Technology": "The IT department, led by Dr. N. SANKAR RAM, focuses on a broad range of career options in software development, computer programming, business analysis, data modeling, systems integration, and network management.",
    "Computer Science and Engineering": "The CSE department offers programs like B.E in CSE, M.E in CSE, and Ph.D in CSE, under the leadership of Dr. Thenmozhi T. The department is dedicated to the theory, development, and application of software and systems.",
    "Computer Science and Business Systems": "Headed by Dr. P. Rajkumar, the CSBS department merges technology with strategic business insights, preparing students for the multidisciplinary demands of the digital era.",
    "Science & Humanities": "The Department of Science and Humanities is an essential department offering entry-level courses in Mathematics, Physics, Chemistry, and English, laying the foundation for fundamental science knowledge for all engineering disciplines. The department always strives hard to provide holistic education to students. The laboratory under the Department of Science & Humanities includes Engineering Physics Laboratory, Engineering Chemistry Laboratory, and Language Laboratory. Salient features of the department include experienced faculty members, well-equipped laboratories, ICT-enabled classrooms, peer learning teaching strategies, remedial coaching classes, availability of resources in MOODLE for better learning, digital learning facility using Coursera certification, skill enhancement opportunities, motivation for participation in technical and non-technical events, and a strong student support system.",
    "Artificial Intelligence & Data Science": "The AI&DS department, offering a B.Tech in AI and Data Science and led by Dr. S. Kalpana, is dedicated to exploring and advancing the frontiers of artificial intelligence and data science.",
    "Electronics and Communication Engineering": "The Department of Electronics and Communication Engineering was established in 2008 with a vision to develop competent professionals to meet the global challenges in modern engineering society. It offers a 4-year B.E. Electronics and Communication Engineering program with a sanctioned intake of 120 students, M.E Applied Electronics program with a sanctioned intake of 9 students, and Ph.D program. The Laboratories are equipped with the latest technology in fields such as Electronic Devices and Circuits, Digital Electronics, Linear Integrated Circuits, Microprocessors and Microcontrollers, Digital Signal Processing, Communication System, VLSI, Embedded Systems, Optical & Microwave, offering opportunities on a wide range of hardware and advanced software packages. The Department has a committed team of faculty members with expertise in areas such as Applied Electronics, Communication systems, VLSI, Embedded Systems, Signal processing, and Networking. It encompasses professional technical associations such as IEEE, IETE, and ISTE chapters, providing students with platforms to learn professional and soft skills.",
    # Department Heads Section
    "who all are the hods of kgisl institute of technology":"The Heads of Departments (HODs) at KGISL Institute of Technology are:  1. Dr. Kathiravan N - Head of the Science & Humanities department  2. Dr. B. Shoba - Head of the Electronics and Communication Engineering (ECE) department  3. Dr. T. Venugopal - Head of the Mechanical Engineering department  4. Dr. N. Sankar Ram - Head of the Information Technology (IT) department  5. Dr. P. Rajkumar - Head of the Computer Science and Business Systems (CSBS) department  6. Dr. S. Kalpana - Head of the Artificial Intelligence & Data Science (AI&DS) department  7. Dr. K.G. Senthilkumar - Head of the Master of Business Administration (MBA) department",
    "who all are the hods of kite":"The Heads of Departments (HODs) at KGISL Institute of Technology are:  1. Dr. Kathiravan N - Head of the Science & Humanities department  2. Dr. B. Shoba - Head of the Electronics and Communication Engineering (ECE) department  3. Dr. T. Venugopal - Head of the Mechanical Engineering department  4. Dr. N. Sankar Ram - Head of the Information Technology (IT) department  5. Dr. P. Rajkumar - Head of the Computer Science and Business Systems (CSBS) department  6. Dr. S. Kalpana - Head of the Artificial Intelligence & Data Science (AI&DS) department  7. Dr. K.G. Senthilkumar - Head of the Master of Business Administration (MBA) department",
    "name all the hods of kgisl institute of technology":"The Heads of Departments (HODs) at KGISL Institute of Technology are:  1. Dr. Kathiravan N - Head of the Science & Humanities department  2. Dr. B. Shoba - Head of the Electronics and Communication Engineering (ECE) department  3. Dr. T. Venugopal - Head of the Mechanical Engineering department  4. Dr. N. Sankar Ram - Head of the Information Technology (IT) department  5. Dr. P. Rajkumar - Head of the Computer Science and Business Systems (CSBS) department  6. Dr. S. Kalpana - Head of the Artificial Intelligence & Data Science (AI&DS) department  7. Dr. K.G. Senthilkumar - Head of the Master of Business Administration (MBA) department",
    "name all the hods of kite":"The Heads of Departments (HODs) at KGISL Institute of Technology are:  1. Dr. Kathiravan N - Head of the Science & Humanities department 2. Dr. B. Shoba - Head of the Electronics and Communication Engineering (ECE) department 3. Dr. T. Venugopal - Head of the Mechanical Engineering department 4. Dr. N. Sankar Ram - Head of the Information Technology (IT) department  5. Dr. P. Rajkumar - Head of the Computer Science and Business Systems (CSBS) department  6. Dr. S. Kalpana - Head of the Artificial Intelligence & Data Science (AI&DS) department  7. Dr. K.G. Senthilkumar - Head of the Master of Business Administration (MBA) department",
    
    "Head of Department of Science & Humanities": "Dr. Kathiravan N, M.E., Ph.D., is a Professor & Dean of the Science & Humanities department. He received his Ph.D. in Mechanical Engineering from Bharathiar University, Coimbatore. He completed his Masters in Industrial Engineering from PSG College of Technology, Coimbatore. His research areas include Automation, TQM, and Manufacturing Process. With about 10 years of industrial and 25 years of academic experience, he has 10 international publications to his credit. Dr. Kathiravan is a subject expert in Engineering Drawing and a recognized supervisor under Anna University, Chennai. He is a member of IE, ISTE, and a certified Chartered Engineer. Additionally, he serves as a 'Special Invitee' of the Managing Committee of Indian Red Cross Society, Coimbatore District branch.",
    "Head of Department of ECE": "DDr.B.Shoba, M.Tech.,M.B.A.,Ph.D., M.I.S.T.E, ASSOCIATE PROFESSOR & HEAD OF THE DEPARTMENT- ECE Dr.B.Shoba completed her B.Tech degree in Electronics and Communication Engineering from Pondicherry Engineering College, Pondicherry Central University in 2002 and M.Tech degree with gold medal in Electronics and Communication Engineering from Pondicherry Central University in 2008. She has also completed MBA in Operations Management from IGNOU, New Delhi. She got her doctorate in Electronics and Communication Engineering from Pondicherry Central University in April 2019. She is having 18 years of experience in teaching and administration. She has published 40 research papers in various International and national Journals and Conferences. She is the recipient of 5 Best paper awards in International and national conferences. She received “Best working women award” from CII and IWN in 2014. She also received “Best Leadership Award” in 2017. She has organized several workshops, seminars, national level symposiums etc., She has acted as reviewer for international conferences and has given guest lectures and webinars. She is also an active life member in ISTE. Her areas of interest include wireless communication, signal processing and biomedical applications.",
    "Head of Department of Mechanical Engineering": "Dr. T. Venugopal M.E., Ph.D., ASSOCIATE PROFESSOR & HEAD. Dr. T. Venugopal graduated in Mechanical Engineering from Bharathiar University, Coimbatore in 2002 and obtained his Master’s Degree in CAD/CAM from Anna University Chennai in 2004. He earned his Doctoral degree in Mechanical Engineering from Anna University, Chennai in 2019. With 19 years of academic and research experience, he has published 15 research articles in various peer-reviewed international journals and conferences at the national and international levels. Dr. T. Venugopal has also published two patents in the area of Natural Fibre Products and serves as a reviewer for prestigious Springer and Elsevier Journals. He received a Seminar Grant OF Rs.20,000/- from CSIR, New Delhi and a Project Grant of Rs.7500 from TNSCST (SPS), Chennai. He is a life member of ISTE and ISNT.",
    "Head of Department of IT": "Dr.N.SANKAR RAM, B.E.,M.E.,Ph.D.,FIE PROFESSOR & HEAD OF THE DEPARTMENT An incisive professional, currently working as a Professor and Head in the department of IT, KGISL Institute of Technology,Coimbatore. Completed his B.E., and M.E., from M.K.University, Madurai and Ph.D. from Anna University, Chennai, with over 25 years of experience in teaching operations. Produced good results and facilitating students by using interactive discussions and guide students to learn and apply concepts in subjects. More interested in doing research activities, as a part of it guiding Ph.D scholars under Anna University and other Universities and produced 11 Ph.D candidates as on date. Received fund from reputed research funding agencies to a tune of Rs 13 Lakhs to his credit and published more than 50 papers in referred journals and conferences. Active Life Member of ISTE, CSI, IEI and organized many Conferences, Symposia, Workshops, FDPs, Science Expo etc .. in national and international level .Having a positive professional attitude and a strong commitment to do excellence in academic activities. A keen communicator with the ability to understand the competitive situation and needs of the students. Received “Best Researcher Award” from Integrated Intelligent Research Group in the year 2017, “Best Teacher Award” from IEAE, Bangalore in the year 2018 and received “Best Professional Icon Award” from IEI in the same year.",
    "Head of Department of CSE":"Dr. Thenmozhi T PROFESSOR & HEAD OF THE DEPARTMENT - CSE Dr.Thenmozhi T completed her Bachelors Degree in Computer Science and Engineering from Madurai Kamaraj University in the year 1996 and has completed her Master’s in Business Administration by 1998, specializing in Marketing and Finance from The American college , Madurai. She has her Master’s degree in Computer science Engineering from Avinashilingam University in the year 2009. She has received her Doctorate in Information and Communication Engineering, from Anna University, Chennai. She has nearly 24 years of experience in teaching and research. Her research areas include Vehicular Networks and Blockchain Technologies. She has nearly ten of her papers published in International Journals. She has been serving as Head of Department in Engineering Colleges in TamilNadu. She is a member in Professional bodies like CSI and ISTE",
    "Research Advisory Committee (RAC)": "The Research Advisory Committee (RAC) consists of distinguished members from various departments who provide guidance and oversight for research activities at the institution. The committee members are as follows: \n1. Dr. S. Suresh Kumar - Principal, ECE (Chairperson) \n2. Dr. N. Rajkumar - Professor, CSE (Director of Research) \n3. Dr. N. Kathiravan - Professor, Mech (Member) \n4. Dr. T. Thenmozhi - Professor, CSE (Member) \n5. Dr. N. Sankar Ram - Professor, IT (Member) \n6. Dr. C. Venkatesh - Professor, ECE (Member) \n7. Dr. P. Vigneshkumar - Professor, S&H (Member)",
    "Research Ethics Committee (REC)": "The Research Ethics Committee (REC) is responsible for ensuring ethical conduct in research activities undertaken at the institution. The committee members are as follows: \n1. Dr. S. Sureshkumar - Professor, ECE (Principal) \n2. Dr. N. Rajkumar - Professor, CSE (Convenor) \n3. Dr. N. Kathiravan - Professor, Mech (Member) \n4. Dr. P. Rajkumar - Professor, CSE (Member) \n5. Dr. S. Kalpana - Associate Professor, CSE (Member) \n6. Dr. T. Venugopal - Associate Professor, Mech (Member)",
    "Head of the department of  Master of Business Administration of kgisl institute of technology":"Dr. K.G. Senthilkumar, MBA.M.Phill.,Ph.D",

    "Head of Department of CSE at kgisl Institute of Technology":"Dr. Thenmozhi T PROFESSOR & HEAD OF THE DEPARTMENT - CSE Dr.Thenmozhi T completed her Bachelors Degree in Computer Science and Engineering from Madurai Kamaraj University in the year 1996 and has completed her Master’s in Business Administration by 1998, specializing in Marketing and Finance from The American college , Madurai. She has her Master’s degree in Computer science Engineering from Avinashilingam University in the year 2009. She has received her Doctorate in Information and Communication Engineering, from Anna University, Chennai. She has nearly 24 years of experience in teaching and research. Her research areas include Vehicular Networks and Blockchain Technologies. She has nearly ten of her papers published in International Journals. She has been serving as Head of Department in Engineering Colleges in TamilNadu. She is a member in Professional bodies like CSI and ISTE",
    "HOD of CSE at kgisl Institute of Technology":"Dr. Thenmozhi T PROFESSOR & HEAD OF THE DEPARTMENT - CSE Dr.Thenmozhi T completed her Bachelors Degree in Computer Science and Engineering from Madurai Kamaraj University in the year 1996 and has completed her Master’s in Business Administration by 1998, specializing in Marketing and Finance from The American college , Madurai. She has her Master’s degree in Computer science Engineering from Avinashilingam University in the year 2009. She has received her Doctorate in Information and Communication Engineering, from Anna University, Chennai. She has nearly 24 years of experience in teaching and research. Her research areas include Vehicular Networks and Blockchain Technologies. She has nearly ten of her papers published in International Journals. She has been serving as Head of Department in Engineering Colleges in TamilNadu. She is a member in Professional bodies like CSI and ISTE",
    "Head of Department of Computer Scince and engineering at kgisl Institute of Technology":"Dr. Thenmozhi T PROFESSOR & HEAD OF THE DEPARTMENT - CSE Dr.Thenmozhi T completed her Bachelors Degree in Computer Science and Engineering from Madurai Kamaraj University in the year 1996 and has completed her Master’s in Business Administration by 1998, specializing in Marketing and Finance from The American college , Madurai. She has her Master’s degree in Computer science Engineering from Avinashilingam University in the year 2009. She has received her Doctorate in Information and Communication Engineering, from Anna University, Chennai. She has nearly 24 years of experience in teaching and research. Her research areas include Vehicular Networks and Blockchain Technologies. She has nearly ten of her papers published in International Journals. She has been serving as Head of Department in Engineering Colleges in TamilNadu. She is a member in Professional bodies like CSI and ISTE",
    "HOD of Computer Scince and engineering at kgisl Institute of Technology":"Dr. Thenmozhi T PROFESSOR & HEAD OF THE DEPARTMENT - CSE Dr.Thenmozhi T completed her Bachelors Degree in Computer Science and Engineering from Madurai Kamaraj University in the year 1996 and has completed her Master’s in Business Administration by 1998, specializing in Marketing and Finance from The American college , Madurai. She has her Master’s degree in Computer science Engineering from Avinashilingam University in the year 2009. She has received her Doctorate in Information and Communication Engineering, from Anna University, Chennai. She has nearly 24 years of experience in teaching and research. Her research areas include Vehicular Networks and Blockchain Technologies. She has nearly ten of her papers published in International Journals. She has been serving as Head of Department in Engineering Colleges in TamilNadu. She is a member in Professional bodies like CSI and ISTE",

    "HOD of Science & Humanities at kgisl Institute of Technology": "Dr. Kathiravan N, M.E., Ph.D., is a Professor & Dean of the Science & Humanities department. He received his Ph.D. in Mechanical Engineering from Bharathiar University, Coimbatore. He completed his Masters in Industrial Engineering from PSG College of Technology, Coimbatore. His research areas include Automation, TQM, and Manufacturing Process. With about 10 years of industrial and 25 years of academic experience, he has 10 international publications to his credit. Dr. Kathiravan is a subject expert in Engineering Drawing and a recognized supervisor under Anna University, Chennai. He is a member of IE, ISTE, and a certified Chartered Engineer. Additionally, he serves as a 'Special Invitee' of the Managing Committee of Indian Red Cross Society, Coimbatore District branch.",
    "HOD of ECE at kgisl Institute of Technology": "Dr.B.Shoba, M.Tech.,M.B.A.,Ph.D., M.I.S.T.E, ASSOCIATE PROFESSOR & HEAD OF THE DEPARTMENT- ECE Dr.B.Shoba completed her B.Tech degree in Electronics and Communication Engineering from Pondicherry Engineering College, Pondicherry Central University in 2002 and M.Tech degree with gold medal in Electronics and Communication Engineering from Pondicherry Central University in 2008. She has also completed MBA in Operations Management from IGNOU, New Delhi. She got her doctorate in Electronics and Communication Engineering from Pondicherry Central University in April 2019. She is having 18 years of experience in teaching and administration. She has published 40 research papers in various International and national Journals and Conferences. She is the recipient of 5 Best paper awards in International and national conferences. She received “Best working women award” from CII and IWN in 2014. She also received “Best Leadership Award” in 2017. She has organized several workshops, seminars, national level symposiums etc., She has acted as reviewer for international conferences and has given guest lectures and webinars. She is also an active life member in ISTE. Her areas of interest include wireless communication, signal processing and biomedical applications.",
    "HOD of electrical and comunication engineering at kgisl Institute of Technology": "Dr.B.Shoba, M.Tech.,M.B.A.,Ph.D., M.I.S.T.E, ASSOCIATE PROFESSOR & HEAD OF THE DEPARTMENT- ECE Dr.B.Shoba completed her B.Tech degree in Electronics and Communication Engineering from Pondicherry Engineering College, Pondicherry Central University in 2002 and M.Tech degree with gold medal in Electronics and Communication Engineering from Pondicherry Central University in 2008. She has also completed MBA in Operations Management from IGNOU, New Delhi. She got her doctorate in Electronics and Communication Engineering from Pondicherry Central University in April 2019. She is having 18 years of experience in teaching and administration. She has published 40 research papers in various International and national Journals and Conferences. She is the recipient of 5 Best paper awards in International and national conferences. She received “Best working women award” from CII and IWN in 2014. She also received “Best Leadership Award” in 2017. She has organized several workshops, seminars, national level symposiums etc., She has acted as reviewer for international conferences and has given guest lectures and webinars. She is also an active life member in ISTE. Her areas of interest include wireless communication, signal processing and biomedical applications.",

            
    "HOD of Mechanical Engineering at kgisl Institute of Technology": "Dr. T. Venugopal M.E., Ph.D., ASSOCIATE PROFESSOR & HEAD. Dr. T. Venugopal graduated in Mechanical Engineering from Bharathiar University, Coimbatore in 2002 and obtained his Master’s Degree in CAD/CAM from Anna University Chennai in 2004. He earned his Doctoral degree in Mechanical Engineering from Anna University, Chennai in 2019. With 19 years of academic and research experience, he has published 15 research articles in various peer-reviewed international journals and conferences at the national and international levels. Dr. T. Venugopal has also published two patents in the area of Natural Fibre Products and serves as a reviewer for prestigious Springer and Elsevier Journals. He received a Seminar Grant OF Rs.20,000/- from CSIR, New Delhi and a Project Grant of Rs.7500 from TNSCST (SPS), Chennai. He is a life member of ISTE and ISNT.",
    "HOD of mech at kgisl Institute of Technology": "Dr. T. Venugopal M.E., Ph.D., ASSOCIATE PROFESSOR & HEAD. Dr. T. Venugopal graduated in Mechanical Engineering from Bharathiar University, Coimbatore in 2002 and obtained his Master’s Degree in CAD/CAM from Anna University Chennai in 2004. He earned his Doctoral degree in Mechanical Engineering from Anna University, Chennai in 2019. With 19 years of academic and research experience, he has published 15 research articles in various peer-reviewed international journals and conferences at the national and international levels. Dr. T. Venugopal has also published two patents in the area of Natural Fibre Products and serves as a reviewer for prestigious Springer and Elsevier Journals. He received a Seminar Grant OF Rs.20,000/- from CSIR, New Delhi and a Project Grant of Rs.7500 from TNSCST (SPS), Chennai. He is a life member of ISTE and ISNT.",
    
    "HOD of IT at kgisl Institute of Technology": "Dr.N.SANKAR RAM, B.E.,M.E.,Ph.D.,FIE PROFESSOR & HEAD OF THE DEPARTMENT An incisive professional, currently working as a Professor and Head in the department of IT, KGISL Institute of Technology,Coimbatore. Completed his B.E., and M.E., from M.K.University, Madurai and Ph.D. from Anna University, Chennai, with over 25 years of experience in teaching operations. Produced good results and facilitating students by using interactive discussions and guide students to learn and apply concepts in subjects. More interested in doing research activities, as a part of it guiding Ph.D scholars under Anna University and other Universities and produced 11 Ph.D candidates as on date. Received fund from reputed research funding agencies to a tune of Rs 13 Lakhs to his credit and published more than 50 papers in referred journals and conferences. Active Life Member of ISTE, CSI, IEI and organized many Conferences, Symposia, Workshops, FDPs, Science Expo etc .. in national and international level .Having a positive professional attitude and a strong commitment to do excellence in academic activities. A keen communicator with the ability to understand the competitive situation and needs of the students. Received “Best Researcher Award” from Integrated Intelligent Research Group in the year 2017, “Best Teacher Award” from IEAE, Bangalore in the year 2018 and received “Best Professional Icon Award” from IEI in the same year.",
    "HOD of Information Technology at kgisl Institute of Technology": "Dr.N.SANKAR RAM, B.E.,M.E.,Ph.D.,FIE PROFESSOR & HEAD OF THE DEPARTMENT An incisive professional, currently working as a Professor and Head in the department of IT, KGISL Institute of Technology,Coimbatore. Completed his B.E., and M.E., from M.K.University, Madurai and Ph.D. from Anna University, Chennai, with over 25 years of experience in teaching operations. Produced good results and facilitating students by using interactive discussions and guide students to learn and apply concepts in subjects. More interested in doing research activities, as a part of it guiding Ph.D scholars under Anna University and other Universities and produced 11 Ph.D candidates as on date. Received fund from reputed research funding agencies to a tune of Rs 13 Lakhs to his credit and published more than 50 papers in referred journals and conferences. Active Life Member of ISTE, CSI, IEI and organized many Conferences, Symposia, Workshops, FDPs, Science Expo etc .. in national and international level .Having a positive professional attitude and a strong commitment to do excellence in academic activities. A keen communicator with the ability to understand the competitive situation and needs of the students. Received “Best Researcher Award” from Integrated Intelligent Research Group in the year 2017, “Best Teacher Award” from IEAE, Bangalore in the year 2018 and received “Best Professional Icon Award” from IEI in the same year.",

    "HOD of CSBS at kgisl Institute of Technology": "Dr.P.Rajkumar, currently working as a professor and Head in the department of Computer Science and Business Systems. Completed his Bachelor's Degree from Bharathiar University in 2005 and has completed his Master’s degree in Computer science engineering from Anna University in 2008. He has received his Ph.D. in Information and Communication Engineering, from Anna University in 2013. He is having 17 years of experience in teaching and administration. He has published as many as 30 papers in reputed International Journals, International and National Conferences. He also has published 3 patents. He is active reviewer for 3 international journals and he received Rs.1, 00,000 from IBNC for the conduct of Seven days workshop “IBNC- India’s Biggest Networking Championship” jointly organized by IIT Delhi. He received Rs.45, 000 from NNSC for the conduct of two days workshop “National Network Security Championship” jointly organized by IIT Delhi. He is also an active life member in CSI and ISTE. His research areas include Network Security, Cloud Computing.",
    "HOD of Computer Science and Business Systems at kgisl Institute of Technology": "Dr.P.Rajkumar, currently working as a professor and Head in the department of Computer Science and Business Systems. Completed his Bachelor's Degree from Bharathiar University in 2005 and has completed his Master’s degree in Computer science engineering from Anna University in 2008. He has received his Ph.D. in Information and Communication Engineering, from Anna University in 2013. He is having 17 years of experience in teaching and administration. He has published as many as 30 papers in reputed International Journals, International and National Conferences. He also has published 3 patents. He is active reviewer for 3 international journals and he received Rs.1, 00,000 from IBNC for the conduct of Seven days workshop “IBNC- India’s Biggest Networking Championship” jointly organized by IIT Delhi. He received Rs.45, 000 from NNSC for the conduct of two days workshop “National Network Security Championship” jointly organized by IIT Delhi. He is also an active life member in CSI and ISTE. His research areas include Network Security, Cloud Computing.",
 
    "HOD of AI&DS at kgisl Institute of Technology": "Dr. S. Kalpana, has received her B.E in Information Technology from Bharathiar University, Coimbatore in 2003 and Master’s in Computer Science and Engineering from Anna University, Chennai in 2006. She completed her Ph.D(ICE) from Anna University, Chennai in 2019. She has about 17 years of teaching experience and 3 years of Industry and EDUTech Experience. Her area of interest includes Artificial Intelligence, Machine Learning, Deep Learning Cyber Security, and Networking. She has authored several research papers in refereed International Journals and IEEE conferences and also got sanction of around INR 7.7 million from DST, Govt of India for her research project. She had led large scale operations teams, SMEs and academicians to deliver skilling PAN India effectively. She also had led teams for many national level initiatives including MHRD NBA, NIRF, Swachhta, Smart India Hackathon, SIRO of DSIR. She is the INTEL certified instructor in OneAPI. Her passion in learning made her complete international certifications like Harvard CS50p and CS50x, Coursera, Google, Intel etc. She is actively involved in several open source projects, organized Hackathons, Project expo and guided several projects. She is the lifetime member of ISTE and also the member of CSI and IAENG.",
    "Head of the department of  MBA of kgisl institute of technology":"Dr. K.G. Senthilkumar, MBA.M.Phill.,Ph.D",
    "HOD of MBA at kgisl Institute of Technology": "Dr. K.G. Senthilkumar, MBA.M.Phill.,Ph.D",
    "HOD of Master of Business Administration at kgisl Institute of Technology": "Dr. K.G. Senthilkumar, MBA.M.Phill.,Ph.D",

   "Skill Labs at kgisl institute of technology": "The Skill Labs at KGiSL Institute of Technology encompass various cutting-edge technologies such as Augmented Reality (AR), Virtual Reality (VR), and Robotic Process Automation (RPA). These labs provide students with hands-on experience and practical training in these emerging fields, preparing them for the challenges of the future.",
    "Learning Management System at kgisl institute of technology": "KGiSL Institute of Technology utilizes Moodle, a globally recognized open-source Learning Management System (LMS), to facilitate online learning. Moodle offers a collaborative platform for both students and teachers, delivering course materials and enabling interactive learning experiences. It includes features such as discussion forums, quizzes, and assignment tracking, enhancing the overall learning journey.",
    "Infrastructure at kgisl institute of technology": "The infrastructure at KGiSL Institute of Technology is state-of-the-art, designed to provide students with a conducive learning environment. The campus spans 11 acres and includes three blocks: Admin Block, Academic Block, and Lab Block. It features smart classrooms, well-equipped laboratories, a digital library, an auditorium, a gym, a food court, yoga facilities, and a health center. Additionally, the hostel provides comfortable accommodation with Wi-Fi connectivity.",
    "Class Room at kgisl institute of technology": "KGiSL Institute of Technology boasts 42 classrooms and 3 seminar halls equipped with ICT facilities such as LCD projectors, Wi-Fi/LAN connectivity, and green boards. The seminar halls are utilized for department meetings, workshops, and club activities.",
    "Laboratories at kgisl institute of technology": "The institute's teaching-learning laboratories are fully equipped with state-of-the-art facilities, meeting the norms and standards prescribed by regulatory authorities such as AICTE and the affiliating university. The laboratories cover various disciplines and are instrumental in providing practical exposure to students.",
    "Library at kgisl institute of technology": "The central library at KGiSL Institute of Technology is fully automated and houses a vast collection of books and journals. It subscribes to numerous online journals and provides access to digital resources. Additionally, departmental libraries are available for immediate reference by staff and students.",
    "Fitness Centre at kgisl institute of technology": "The KGiSL Fitness Centre focuses on maintaining physical fitness and offers modern equipment for various exercises. It operates from early morning to late evening, providing students and staff with opportunities for physical activity.",
    "Amenities at  kgisl institute of technology": "The college campus is self-sufficient, with amenities such as a cafeteria, restaurant, hospital, pharmacy, and banking facilities. It also provides 24x7 security and transportation services for students.",
    "Physical Education at kgisl institute of technology": "KGiSL Institute of Technology emphasizes physical education as an integral part of student development. The campus provides facilities for various sports and fitness activities to promote a healthy lifestyle among students.",
    "Transport at kgisl institute of technology": "The college offers transportation services for students residing outside the campus, facilitating easy commute to and from the college.",
    "Pharmacy  at kgisl institute of technology": "A pharmacy located on the campus provides essential medical supplies and services to students and staff, ensuring their healthcare needs are met.",
    "Cafeteria at kgisl institute of technology": "The 24-hour cafeteria at KGiSL Institute of Technology offers a variety of food and snacks, providing students with a space for relaxation and professional interaction.",
    "Hospital at kgisl institute of technology": "The campus hospital offers medical facilities to students, ensuring prompt medical attention in case of any health issues.",
    "Bank  at kgisl institute of technology": "A Canara Bank facility with ATMs is available on campus, providing banking services to students and staff.",
    "Security  at kgisl institute of technology": "The college campus is equipped with 24-hour security personnel to ensure the safety and security of students and staff.",
    

    "Hostel at kgisl institute of technology": "At KGiSL Institute of Technology, we prioritize providing safe, comfortable, and well-equipped hostels for both male and female students, ensuring a conducive living environment conducive to academic success and personal growth. Here's an overview of our exceptional hostel facilities:",
    "Hostel at kite ": "At KGiSL Institute of Technology, we prioritize providing safe, comfortable, and well-equipped hostels for both male and female students, ensuring a conducive living environment conducive to academic success and personal growth. Here's an overview of our exceptional hostel facilities:",

    "Hostel Facilities  at kgisl institute of technology": "Our hostel premises are equipped with round-the-clock security personnel and surveillance cameras, ensuring a safe and secure living environment for all students.",
    "Hostel Facilities  at kite": "Our hostel premises are equipped with round-the-clock security personnel and surveillance cameras, ensuring a safe and secure living environment for all students.",


    "Accommodation at kgisl institute of technology": "Our hostel rooms are designed to provide maximum comfort and convenience, with amenities such as comfortable beds, study desks, storage units, and adequate lighting.",
    "Accommodation at kite": "Our hostel rooms are designed to provide maximum comfort and convenience, with amenities such as comfortable beds, study desks, storage units, and adequate lighting.",

    "Dining Facilities at kgisl institute of technology": "The hostel mess serves nutritious and delicious meals, catering to diverse dietary preferences, while maintaining hygiene and quality standards.",
    "Dining Facilities a tkite": "The hostel mess serves nutritious and delicious meals, catering to diverse dietary preferences, while maintaining hygiene and quality standards.",

    "Wi-Fi Connectivity  at kgisl institute of technology": "High-speed Wi-Fi connectivity is available throughout the hostel, allowing students to stay connected with family and friends and access online resources.",

    "Study and Recreational Areas": "Designated study areas and recreational spaces are provided, encouraging focused study and social interactions among students.",

    "Laundry Services kgisl institute of technology": "On-site laundry services are available, eliminating the hassle of finding external laundry facilities for students.",

    "Guidance and Support kgisl institute of technology": "Experienced hostel wardens offer guidance and support to students, creating a nurturing environment where students can thrive.",

    "Transport details at kgisl institute of technology": "At KGiSL Institute of Technology, we ensure seamless transportation for students from various parts of Coimbatore and beyond, prioritizing safety and punctuality. Here are the details of our college bus routes  Transport
    We ferry students from all parts of Coimbatore and beyond. We are on time, every time. We facilitate connectivity to student homes and drive them safe.COLLEGE BUS ROUTE AND FEE DETAILS
Route No : 1 - Sirumugai - Reyon Nagar to KGiSL Campus
Route No : 2 - CTC METTUPALAYAM to KGiSL Campus
Route No : 3 - Batharakaliamman Temple to KGiSL Campus
Route No : 4 - Jothipuram to KGiSL Campus
Route No : 5 - Bharathiar University to KGiSL Campus
Route No : 6 - Kannappan Nagar to KGiSL Campus
Route No : 7 - Kuniyamuthoor to KGiSL Campus
Route No : 8 - Sulur to KGiSL Campus
Route No : 9 - Tirupur to KGiSL Campus
Route No : 10 - Alanthurai to KGiSL Campus
Route No : 11 - Bhavanisagar to KGiSL Campus
Route No : 12 - Annur to KGiSL Campus
Route No : 13 - Thadagam to KGiSL Campus",

    
    "Bus Routes at kgisl institute of technology": "Our college buses operate on various routes, covering key areas in and around Coimbatore, ensuring convenient transportation for students.",
    
    "Fee Structure at kgisl institute of technology": "The college bus fee structure is designed to be affordable and transparent, providing students with a cost-effective mode of transportation.",
    
    "Bus Facilities at kgisl institute of technology": "Our college buses are equipped with modern facilities, ensuring a comfortable and safe travel experience for students.",
    
    "Safety Measures at kgisl institute of technology": "We prioritize the safety and security of students during transportation, implementing stringent safety measures and guidelines.",
    
    "Bus Timings at kgisl institute of technology": "The college bus timings are scheduled to align with the college's academic schedule, ensuring punctual arrival and departure for students.",
    
    "Bus Rules at kgisl institute of technology": "We have established clear and comprehensive rules for college bus usage, ensuring discipline and safety among students during transportation.",
    
    "Bus Staff at kgisl institute of technology": "Our college buses are managed by experienced and professional staff, ensuring a smooth and reliable transportation experience for students.",
    
    
    "Placement details at kgisl institute of technology": "At KGiSL Institute of Technology, we are committed to providing students with exceptional placement opportunities, ensuring their successful transition from academia to industry. Here's an overview of our placement process and achievements:",
    
    "Placement Process at kgisl institute of technology": "Our comprehensive placement process is designed to equip students with the necessary skills and resources to secure rewarding career opportunities.",
    
    "Placement Achievements at kgisl institute of technology": "We have a strong track record of successful placements, with students securing positions in leading companies across diverse industries.",
    
    "Placement Training at kgisl institute of technology": "We offer specialized training programs to prepare students for the recruitment process, enhancing their employability and confidence.",
    
    "Recruitment Partners at kgisl institute of technology": "We have established strong partnerships with leading companies, facilitating regular recruitment drives and internship opportunities for students.",
    
    "Placement Support at kgisl institute of technology": "Our dedicated placement cell provides students with guidance and support throughout the placement process, ensuring a seamless experience.",
    
    "Internship Opportunities at kgisl institute of technology": "We offer students access to valuable internship opportunities, enabling them to gain practical experience and industry exposure.",
    
    "Placement Statistics at kgisl institute of technology": "Our placement statistics reflect the success of our students, with a high percentage of students securing placements in top companies.",
    
    "Placement Highlights at kgisl institute of technology": "Our placement highlights showcase the diverse roles and industries in which our students have secured rewarding career opportunities.",
    
    "Placement Testimonials at kgisl institute of technology": "We have received positive testimonials from both students and recruiters, reflecting the quality and impact of our placement initiatives.",
    
    "Placement FAQs at kgisl institute of technology": "Our placement FAQs provide students with comprehensive information on the placement process, ensuring clarity and transparency.",
    
    "Placement Contact at kgisl institute of technology": "For any placement-related queries, students can contact our placement cell for guidance and support.",
    
    "Alumni details at kgisl institute of technology": "At KGiSL Institute of Technology, we take pride in our vibrant alumni community, comprising successful professionals across diverse industries. Here's an overview of our alumni network and initiatives:",
    
    "Alumni Network at kgisl institute of technology": "Our alumni network spans various industries and geographies, providing students with valuable connections and mentorship opportunities.",
    
    "Alumni Achievements at kgisl institute of technology": "Our alumni have achieved significant success in their respective careers, serving as role models and mentors for current students.",
    
    "Alumni Initiatives at kgisl institute of technology": "We offer various initiatives and programs to engage and support our alumni, fostering a strong sense of community and collaboration.",
    
    "Alumni Testimonials at kgisl institute of technology": "We have received positive testimonials from our alumni, reflecting the transformative impact of their educational experience at our institution.",
    
    "Alumni Events at kgisl institute of technology": "We organize regular alumni events and reunions, providing opportunities for networking, knowledge sharing, and professional development.",
    
    "Alumni Contact at kgisl institute of technology": "For any alumni-related queries or collaborations, students and alumni can contact our alumni cell for support and guidance.",
    
    "Alumni FAQs at kgisl institute of technology": "Our alumni FAQs provide students with comprehensive information on alumni initiatives and engagement opportunities.",
    
    "Alumni Registration at kgisl institute of technology": "Students and alumni can register with our alumni network to access exclusive benefits and stay connected with our institution and throut E-Campus.",

    
    #LABS 
    " People in AIES lab": "Technical Manager-Mr. Navaneeth Malligan,Ms. Bhuvaneshwari Kanagaraj; Project Manager-Dr. Krishnapriya; Industry Mentos/PoP-MR. dinesh Tantri; Faculty Mentor-Mr.Sathish Ramanujam,Ms.Leena Bojaraj,Mr. Rahul Poopathi,Mr. Antony Pradeesh",
   
    " Vision of AIES lab":"Our vision for the AIES Innovation Lab is to make KITE (KGiSL Institute of Technology and Engineering) an industry-leading applied research organization that is not only aligned with current technological needs but also contributes significantly to the future of the computing industry. We aim to achieve this by fostering a learn by doing philosophy and focusing on the intersections of Artificial Intelligence and Embedded Systems.",
    " POP'S professor of practices": "Processor of Practices (POPs) Mr. Dinesh Tantri- Lead Mentor Mr. Ramesh Gopal- Founder, Blokxlab- WEB 3.0 Mr. Raghav, Microsoft, Blokxlab - Cyber", # type: ignore
    "people in Cloud and DevOps Lab":"Cloud and DevOpsPeopleTechnical Manager - Mrs. Pavithra RagunathanProject Manager - Dr. Sankar RamIndustry Mentos/PoP - Mr.Dinesh TantriFaculty Mentor -Ms. Amrin ZameerDr. Rajesekaran SMr. Vivekanandhan VMr. Manikandan SMs. Suriya ADr.Ajitha PMs.Dhanusha CMs. Mahalakshmi MMs.Anitha EMs.Gomathi R",
    " vision of Cloud and DevOps Lab":"The Cloud-DevOps COE will be focused on upskilling KITE faculty and graduates with the latest industry best practices as regards to DevOps. Modern websites and software apps have become a complex affair. They are powered by a chain of dependent services residing inside the cloud provider. Customers have come to expect high availability and reliability from the Apps that they use. As a result, DevOps engineers have come to play a critical role in ensuring that the deployed software continues to deliver despite intermittent failures.",
    "people in Web 3.0 Lab ":"Web 3.0PeopleTechnical Manager - Mrs. Pavithra RagunathanProject Manager - Mrs. ThenmozhiIndustry Mentos/PoP -Mr.Dinesh TantriMr. Ramesh GopalFaculty Mentor -Mr. Jeeva Padmanaban V,Mr. Sureshkumar R,Mr. Mani deepak C,Ms.Nithya K,Ms.Yemunarane K,Mr. Boopalan S,Mr. Omprakash S,Mr. Deepan kumar S",
    " Vision of Web 3.0 Lab":"The Web 3.0 Innovation Lab exists to drive transformative learning experiences and enable learner transformation in the Web 3.0 space. The primary goal is to equip learners with the knowledge, skills, and mindset required to understand Web 3.0 deeply and build innovative products and solutions. We believe doing this will automatically improve chances of starting up, finding employment or pursuing higher education in the Web 3.0 area.",
    "people in Cyber Security Lab ":"Technical Manager – Mr.Joel Anandraj.E, AP/ITProject Manager - Dr.S.Vidhya, Vice Principal, KG College of Arts and Science.Industry Mentors/PoP – Mr. Raghav Ellur, Principal Security Group Manager at MicrosoftFaculty Mentor –Ms.Shirley Josephine Mary AP/IT,Ms. Krishna Kala AP/CSBS,Mr.Anbarasan R AP/IT,Ms.Nithya AP/CSE,Ms.Aruna AP/CSE",
    "vision of Cyber Security Lab":"To attain the foremost position in the Cyber Security domain, ensuring a secure digital future through excellence in education, research, and collaborative initiatives.",
    "Innovation Labs at kgisl institute of technology":"KGiSL Institute Of Technology  has 4 innovation labs 1. AI&ES Lab (Artificial intelligence and Embedded systems ) 2. Cloud and DevOps Lab  3. Web 3.0 4. Cyber Security Lab ",
    "Innovation Labs at kite":"KGiSL Institute Of Technology  has 4 innovation labs 1. AI&ES Lab (Artificial intelligence and Embedded systems ) 2. Cloud and DevOps Lab  3. Web 3.0 4. Cyber Security Lab ",

    
    
    
    "Tech Community": {
        "Objectives": [
            "Create technical awareness among students and improve their quality through learning.",
            "Promote interest and innovation among the students.",
            "Provide opportunities to interact with industry mentors and acquire knowledge for live projects."
        ],
        "Communities": {
            "COMPYLE – Python Community": {},
            "BRAIN – AI Community": {},
            "ML Community": {},
            "WARPATH – RPA Community": {},
            "IoT, Robotics, Drones Community": {}
        }
    }
}


        



        max_similarity = 0
        matched_question = None
        
        for question in responses:
            similarity = SequenceMatcher(None, message.lower(), question.lower()).ratio()
            if similarity > max_similarity:
                max_similarity = similarity
                matched_question = question
        
        if max_similarity >= match_threshold:
            time.sleep(1.1) 
            return responses[matched_question]
        else:
            messages=[{"role":"system","content":"You are a helpful assistant."}, {"role":"user","content":message}]

            response = openai.ChatCompletion.create(model="gpt-3.5-turbo", messages=messages)
            answer = response['choices'][0]['message']['content'].replace('\n', '<br>')
            return answer
        
    except Exception as e:
        return 'Oops, something went wrong: ' + str(e)


if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
