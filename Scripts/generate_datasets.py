import json
import os
from pathlib import Path

DATA_RAW = Path("data/raw")
DATA_PROCESSED = Path("data/processed")
DATA_RAW.mkdir(parents=True, exist_ok=True)
DATA_PROCESSED.mkdir(parents=True, exist_ok=True)

# 1. Government Schemes Data (myScheme standard)
SCHEMES = [
    {
        "id": "SCH-PM-KISAN",
        "title_en": "Pradhan Mantri Kisan Samman Nidhi (PM-KISAN)",
        "title_hi": "प्रधानमंत्री किसान सम्मान निधि (पीएम-किसान)",
        "category": "Agriculture & Farming",
        "summary_en": "Provides financial assistance of Rs 6,000 per year in three equal installments of Rs 2,000 to all landholding farmer families across India.",
        "summary_hi": "सभी पात्र भूमिधारक किसान परिवारों को प्रति वर्ष ₹6,000 की वित्तीय सहायता तीन समान किस्तों (₹2,000 प्रत्येक) में सीधे बैंक खाते में दी जाती है।",
        "eligibility": {
            "min_age": 18,
            "max_age": 75,
            "gender": "All",
            "min_qualification": "None",
            "max_annual_income": None,
            "caste_category": ["All"],
            "state": "All India",
            "occupation": "Farmer"
        },
        "benefits_en": "Rs 6,000 annually credited directly to beneficiary bank account via DBT.",
        "benefits_hi": "वार्षिक ₹6,000 सीधे डीबीटी के माध्यम से लाभार्थी के बैंक खाते में जमा।",
        "documents_required": ["Aadhaar Card", "Land Ownership Documents (Khasra/Khatauni)", "Bank Account Details", "Mobile Number"],
        "application_url": "https://pmkisan.gov.in",
        "tags": ["farmer", "kisan", "agriculture", "financial aid", "crop", "paisa", "खेती", "किसान"]
    },
    {
        "id": "SCH-PMJAY",
        "title_en": "Ayushman Bharat - PM Jan Arogya Yojana (AB-PMJAY)",
        "title_hi": "आयुष्मान भारत - प्रधानमंत्री जन आरोग्य योजना (एबी-पीएमजेएवाई)",
        "category": "Healthcare & Wellness",
        "summary_en": "World's largest health insurance scheme providing cashless secondary and tertiary hospitalization cover up to Rs 5 Lakh per family per year.",
        "summary_hi": "प्रति परिवार प्रति वर्ष ₹5 लाख तक का कैशलेस स्वास्थ्य बीमा कवर, जिसके तहत सरकारी और सूचीबद्ध निजी अस्पतालों में मुफ्त इलाज मिलता है।",
        "eligibility": {
            "min_age": 0,
            "max_age": 100,
            "gender": "All",
            "min_qualification": "None",
            "max_annual_income": 250000,
            "caste_category": ["All"],
            "state": "All India",
            "occupation": "Any"
        },
        "benefits_en": "Free medical treatment and surgery up to Rs 5,00,000 per year per family at empanelled hospitals.",
        "benefits_hi": "प्रति वर्ष ₹5 लाख तक का मुफ्त इलाज और ऑपरेशन किसी भी पैनलबद्ध अस्पताल में।",
        "documents_required": ["Aadhaar Card", "Ration Card", "SECC verification proof", "Family ID"],
        "application_url": "https://pmjay.gov.in",
        "tags": ["health", "hospital", "insurance", "ayushman card", "medical treatment", "इलाज", "अस्पताल", "बीमा"]
    },
    {
        "id": "SCH-PMAWAS-U",
        "title_en": "Pradhan Mantri Awas Yojana - Urban & Gramin (PMAY)",
        "title_hi": "प्रधानमंत्री आवास योजना (पीएमएवाई)",
        "category": "Housing & Shelter",
        "summary_en": "Provides financial subsidy and assistance to low and middle-income families to construct or purchase a pucca house.",
        "summary_hi": "गरीब और मध्यम वर्ग के परिवारों को पक्का मकान बनाने या खरीदने के लिए सरकार द्वारा सीधी आर्थिक सहायता व ब्याज सब्सिडी दी जाती है।",
        "eligibility": {
            "min_age": 21,
            "max_age": 70,
            "gender": "All",
            "min_qualification": "None",
            "max_annual_income": 300000,
            "caste_category": ["All"],
            "state": "All India",
            "occupation": "Any"
        },
        "benefits_en": "Financial assistance of Rs 1.2 Lakh to 2.5 Lakh for house construction or credit-linked subsidy.",
        "benefits_hi": "पक्के घर के निर्माण हेतु ₹1.2 लाख से ₹2.5 लाख तक की सीधी सरकारी आर्थिक सहायता।",
        "documents_required": ["Aadhaar Card", "Income Certificate", "Caste Certificate (if applicable)", "BPL/Ration Card", "Bank Details"],
        "application_url": "https://pmaymis.gov.in",
        "tags": ["house", "housing", "pucca makan", "home loan subsidy", "मकान", "घर", "आवास"]
    },
    {
        "id": "SCH-POST-MATRIC-SCHOLARSHIP",
        "title_en": "Post-Matric Scholarship Scheme for SC/ST/OBC Students",
        "title_hi": "अनुसूचित जाति/जनजाति/अन्य पिछड़ा वर्ग हेतु पोस्ट-मैट्रिक छात्रवृत्ति",
        "category": "Education & Scholarships",
        "summary_en": "Provides full tuition fee waiver, maintenance allowance, and academic support for students pursuing Class 11, 12, ITI, Diploma, Undergraduate, or Postgraduate studies.",
        "summary_hi": "10वीं के बाद (11वीं, 12वीं, आईटीआई, डिप्लोमा, कॉलेज डिग्री या पीजी) की पढ़ाई करने वाले छात्रों को पूरी ट्यूशन फीस प्रतिपूर्ति और मासिक भत्ता प्रदान किया जाता है।",
        "eligibility": {
            "min_age": 15,
            "max_age": 30,
            "gender": "All",
            "min_qualification": "10th",
            "max_annual_income": 250000,
            "caste_category": ["SC", "ST", "OBC"],
            "state": "All India",
            "occupation": "Student"
        },
        "benefits_en": "100% course fee reimbursement plus monthly study allowance up to Rs 13,500/year.",
        "benefits_hi": "कॉलेज/स्कूल की पूरी फीस वापसी और ₹13,500 प्रति वर्ष तक का पढ़ाई भत्ता।",
        "documents_required": ["10th/12th Marksheet", "Caste Certificate", "Income Certificate", "College Admission Receipt", "Aadhaar Card"],
        "application_url": "https://scholarships.gov.in",
        "tags": ["scholarship", "college fee", "students", "sc st obc", "higher education", "छात्रवृत्ति", "पढ़ाई"]
    },
    {
        "id": "SCH-SUKANYA",
        "title_en": "Sukanya Samriddhi Yojana (SSY)",
        "title_hi": "सुकन्या समृद्धि योजना",
        "category": "Women & Child Development",
        "summary_en": "Government-backed high-interest savings scheme for girl children to secure funds for higher education and marriage.",
        "summary_hi": "बालिकाओं के उज्ज्वल भविष्य और उच्च शिक्षा के लिए सबसे अधिक ब्याज देने वाली सरकारी बचत योजना।",
        "eligibility": {
            "min_age": 0,
            "max_age": 10,
            "gender": "Female",
            "min_qualification": "None",
            "max_annual_income": None,
            "caste_category": ["All"],
            "state": "All India",
            "occupation": "Any"
        },
        "benefits_en": "Guaranteed attractive interest rate (8.2%+) with triple tax exemption under Section 80C.",
        "benefits_hi": "8.2% से अधिक सरकारी गारंटीकृत ब्याज दर और पूर्ण आयकर छूट।",
        "documents_required": ["Girl Child Birth Certificate", "Parent Aadhaar Card", "Address Proof", "Passport Size Photos"],
        "application_url": "https://www.indiapost.gov.in",
        "tags": ["girl child", "daughter", "savings", "tax free", "education fund", "बेटी", "सुकन्या"]
    },
    {
        "id": "SCH-PM-MUDRA",
        "title_en": "Pradhan Mantri MUDRA Yojana (PMMY)",
        "title_hi": "प्रधानमंत्री मुद्रा योजना",
        "category": "Banking, Financial Services & Business",
        "summary_en": "Provides collateral-free business loans up to Rs 10 Lakh (Shishu, Kishore, Tarun) to small entrepreneurs, shopkeepers, and micro-enterprises.",
        "summary_hi": "छोटे कारोबारियों, दुकानदारों और नए उद्यमियों को बिना किसी गारंटी के ₹50,000 से लेकर ₹10 लाख तक का आसान व्यावसायिक ऋण।",
        "eligibility": {
            "min_age": 18,
            "max_age": 65,
            "gender": "All",
            "min_qualification": "None",
            "max_annual_income": None,
            "caste_category": ["All"],
            "state": "All India",
            "occupation": "Self-employed"
        },
        "benefits_en": "Collateral-free loans: Shishu (up to 50k), Kishore (up to 5 Lakh), Tarun (up to 10 Lakh) with low interest rates.",
        "benefits_hi": "बिना किसी जमानत (collateral) के ₹10 लाख तक का बिजनेस लोन।",
        "documents_required": ["Aadhaar Card", "PAN Card", "Business Address Proof", "Quotation of Machinery / Project Report", "Bank Statement"],
        "application_url": "https://www.mudra.org.in",
        "tags": ["business loan", "mudra", "startup", "shop loan", "msme", "कर्ज", "व्यापार", "लोन"]
    },
    {
        "id": "SCH-PM-SVANIDHI",
        "title_en": "PM Street Vendor's AtmaNirbhar Nidhi (PM SVANidhi)",
        "title_hi": "पीएम स्वनिधि योजना (स्ट्रीट वेंडर्स के लिए)",
        "category": "Employment & Livelihood",
        "summary_en": "Special micro-credit facility providing collateral-free working capital loan up to Rs 50,000 with 7% interest subsidy for street vendors and hawkers.",
        "summary_hi": "रेहड़ी-पटरी वालों और ठेले वालों को अपना काम बढ़ाने के लिए ₹10,000 से ₹50,000 तक का सस्ता सरकारी कार्यशील ऋण।",
        "eligibility": {
            "min_age": 18,
            "max_age": 65,
            "gender": "All",
            "min_qualification": "None",
            "max_annual_income": 180000,
            "caste_category": ["All"],
            "state": "All India",
            "occupation": "Self-employed"
        },
        "benefits_en": "Affordable working capital loans with 7% interest subsidy and cashback on digital transactions.",
        "benefits_hi": "बिना गारंटी ₹50,000 तक का लोन, 7% ब्याज सब्सिडी और डिजिटल लेन-देन पर कैशबैक।",
        "documents_required": ["Vending Certificate / Letter of Recommendation (ULB)", "Aadhaar Card", "Bank Account Details"],
        "application_url": "https://pmsvanidhi.mohua.gov.in",
        "tags": ["street vendor", "hawker", "thela", "micro loan", "svanidhi", "रेहड़ी", "पटरी"]
    },
    {
        "id": "SCH-PM-VISHWAKARMA",
        "title_en": "PM Vishwakarma Kaushal Samman Yojana",
        "title_hi": "प्रधानमंत्री विश्वकर्मा योजना",
        "category": "Skill Development & Artisan Support",
        "summary_en": "Holistic support for traditional artisans and craftspeople including Rs 15,000 toolkit incentive, free training with Rs 500/day stipend, and loans up to Rs 3 Lakh at 5% interest.",
        "summary_hi": "पारंपरिक कारीगरों और शिल्पकारों (बढ़ई, लोहार, दर्जी, राजमिस्त्री आदि) को मुफ्त कौशल प्रशिक्षण, ₹500/दिन स्टाइपेंड, ₹15,000 टूलकिट और 5% पर ₹3 लाख का लोन।",
        "eligibility": {
            "min_age": 18,
            "max_age": 60,
            "gender": "All",
            "min_qualification": "None",
            "max_annual_income": 250000,
            "caste_category": ["All"],
            "state": "All India",
            "occupation": "Artisan"
        },
        "benefits_en": "Free 5-7 days skill training, Rs 500/day stipend, Rs 15,000 modern toolkit grant, and 5% concessional credit.",
        "benefits_hi": "प्रशिक्षण के दौरान ₹500 दैनिक भत्ता, ₹15,000 की टूलकिट और मात्र 5% ब्याज पर व्यवसायिक ऋण।",
        "documents_required": ["Aadhaar Card", "Mobile Number", "Ration Card", "Artisan Trade Skill Declaration", "Bank Account Details"],
        "application_url": "https://pmvishwakarma.gov.in",
        "tags": ["artisan", "carpenter", "tailor", "blacksmith", "craftsman", "vishwakarma", "कारीगर", "विश्वकर्मा"]
    },
    {
        "id": "SCH-NAPS-APPRENTICE",
        "title_en": "National Apprenticeship Promotion Scheme (NAPS)",
        "title_hi": "राष्ट्रीय शिक्षुता प्रोत्साहन योजना (एनएपीएस)",
        "category": "Skill Development & Employment",
        "summary_en": "Industry apprenticeship training with monthly stipend support for 10th, 12th, ITI, and Diploma holders to gain hands-on industrial job experience.",
        "summary_hi": "10वीं, 12वीं, आईटीआई और डिप्लोमा धारकों के लिए उद्योगों में व्यावहारिक ट्रेनिंग और साथ में मासिक स्टाइपेंड (वेतन)।",
        "eligibility": {
            "min_age": 18,
            "max_age": 28,
            "gender": "All",
            "min_qualification": "10th",
            "max_annual_income": None,
            "caste_category": ["All"],
            "state": "All India",
            "occupation": "Unemployed"
        },
        "benefits_en": "Hands-on company training + monthly stipend of Rs 7,000 to Rs 12,000 + National Apprenticeship Certificate.",
        "benefits_hi": "प्रतिष्ठित कंपनियों में ऑन-द-जॉब ट्रेनिंग, ₹7,000 से ₹12,000 मासिक स्टाइपेंड और सरकारी प्रमाण पत्र।",
        "documents_required": ["10th/12th/ITI/Diploma Marksheet", "Aadhaar Card", "Bank Passbook", "Resume"],
        "application_url": "https://www.apprenticeshipindia.gov.in",
        "tags": ["apprentice", "iti", "training", "stipend", "first job", "शिक्षुता", "ट्रेनिंग", "नौकरी"]
    },
    {
        "id": "SCH-LADLI-BEHNA",
        "title_en": "Mukhyamantri Ladli Behna Yojana",
        "title_hi": "मुख्यमंत्री लाड़ली बहना योजना",
        "category": "Women Welfare & Social Security",
        "summary_en": "Direct financial cash transfer of Rs 1,250 every month to eligible married and unmarried women to empower their financial independence.",
        "summary_hi": "21 से 60 वर्ष की पात्र महिलाओं के बैंक खाते में प्रतिमाह ₹1,250 की सीधी आर्थिक सहायता।",
        "eligibility": {
            "min_age": 21,
            "max_age": 60,
            "gender": "Female",
            "min_qualification": "None",
            "max_annual_income": 250000,
            "caste_category": ["All"],
            "state": "Madhya Pradesh",
            "occupation": "Any"
        },
        "benefits_en": "Rs 1,250 transferred directly to bank account every month.",
        "benefits_hi": "हर महीने ₹1,250 सीधे डीबीटी बैंक खाते में।",
        "documents_required": ["Samagra ID / State ID", "Aadhaar Card", "Active Bank Account with DBT", "Mobile Number"],
        "application_url": "https://cmladlibehna.mp.gov.in",
        "tags": ["women empowerment", "monthly allowance", "ladli behna", "dbt", "महिला सहायता", "लाड़ली बहना"]
    }
]

# 2. Government Job & Recent Recruitment Notifications
JOBS = [
    {
        "job_id": "JOB-SSC-GD-2026",
        "title_en": "SSC General Duty (GD) Constable Recruitment",
        "title_hi": "एसएससी जीडी कांस्टेबल भर्ती (बीएसएफ, सीआईएसएफ, सीआरपीएफ)",
        "organization": "Staff Selection Commission (SSC)",
        "category": "Defence & Police Services",
        "qualification_required": "10th",
        "min_age": 18,
        "max_age": 23,
        "vacancies": "39,481 Posts",
        "application_deadline": "2026-10-15",
        "official_portal": "https://ssc.gov.in",
        "summary_en": "Mega recruitment for 10th pass candidates across Central Armed Police Forces (CAPFs) including BSF, CISF, CRPF, and Assam Rifles. Basic pay Rs 21,700 - 69,100.",
        "summary_hi": "10वीं पास युवाओं के लिए सीमा सुरक्षा बल (BSF), CISF, CRPF में कांस्टेबल पदों पर बंपर भर्ती। प्रारंभिक वेतन ₹21,700 से ₹69,100।",
        "location": "All India"
    },
    {
        "job_id": "JOB-SSC-CHSL-2026",
        "title_en": "SSC Combined Higher Secondary Level (CHSL) Exam",
        "title_hi": "एसएससी सीएचएसएल (12वीं पास) भर्ती",
        "organization": "Staff Selection Commission (SSC)",
        "category": "Central Government Clerical & Administration",
        "qualification_required": "12th",
        "min_age": 18,
        "max_age": 27,
        "vacancies": "3,712 Posts",
        "application_deadline": "2026-11-10",
        "official_portal": "https://ssc.gov.in",
        "summary_en": "Recruitment for Lower Division Clerk (LDC), Junior Secretariat Assistant (JSA), and Data Entry Operator (DEO) in Central Government Ministries. Requires 12th pass standard.",
        "summary_hi": "12वीं पास छात्रों के लिए केंद्रीय मंत्रालयों में क्लर्क और डाटा एंट्री ऑपरेटर के पदों पर सीधी भर्ती।",
        "location": "All India"
    },
    {
        "job_id": "JOB-RRB-ALP-2026",
        "title_en": "Railway Recruitment Board (RRB) Assistant Loco Pilot & Technician",
        "title_hi": "रेलवे भर्ती बोर्ड (आरआरबी) सहायक लोको पायलट व तकनीशियन भर्ती",
        "organization": "Railway Recruitment Board (RRB)",
        "category": "Railways & Technical",
        "qualification_required": "10th",
        "min_age": 18,
        "max_age": 30,
        "vacancies": "18,799 Posts",
        "application_deadline": "2026-10-30",
        "official_portal": "https://indianrailways.gov.in",
        "summary_en": "Recruitment of Assistant Loco Pilot (Train Driver) and Technicians across Indian Railways divisions. Qualification: 10th pass + ITI trade certificate or Diploma in Engineering.",
        "summary_hi": "भारतीय रेलवे में ट्रेन ड्राइवर (असिस्टेंट लोको पायलट) और तकनीशियन के पदों पर भर्ती। 10वीं पास + आईटीआई या इंजीनियरिंग डिप्लोमा वाले पात्र हैं।",
        "location": "All India"
    },
    {
        "job_id": "JOB-IBPS-PO-2026",
        "title_en": "IBPS Probationary Officer (PO) & Management Trainee",
        "title_hi": "आईबीपीएस बैंक पीओ (प्रोबेशनरी ऑफिसर) भर्ती",
        "organization": "Institute of Banking Personnel Selection (IBPS)",
        "category": "Banking & Financial Services",
        "qualification_required": "Graduate",
        "min_age": 20,
        "max_age": 30,
        "vacancies": "4,455 Posts",
        "application_deadline": "2026-10-25",
        "official_portal": "https://ibps.in",
        "summary_en": "Recruitment of Officer scale-1 in 11 Public Sector Nationalized Banks (PNB, Bank of Baroda, Canara Bank, etc.). Minimum qualification: Bachelor's degree in any discipline.",
        "summary_hi": "राष्ट्रीयकृत बैंकों में प्रोबेशनरी ऑफिसर (बैंक अफसर) के पदों पर भर्ती। किसी भी विषय में स्नातक (Graduate) डिग्री उत्तीर्ण छात्र आवेदन कर सकते हैं।",
        "location": "All India"
    },
    {
        "job_id": "JOB-UPSC-CSE-2026",
        "title_en": "UPSC Civil Services Examination (IAS / IPS / IFS)",
        "title_hi": "संघ लोक सेवा आयोग सिविल सेवा परीक्षा (आईएएस / आईपीएस)",
        "organization": "Union Public Service Commission (UPSC)",
        "category": "Civil Services & Administration",
        "qualification_required": "Graduate",
        "min_age": 21,
        "max_age": 32,
        "vacancies": "1,056 Posts",
        "application_deadline": "2026-11-20",
        "official_portal": "https://upsc.gov.in",
        "summary_en": "Premier national examination for recruitment to Indian Administrative Service (IAS), Indian Police Service (IPS), Indian Foreign Service (IFS) and allied Central Group-A services.",
        "summary_hi": "देश की सर्वोच्च प्रशासनिक सेवा (आईएएस, आईपीएस, आईएफएस) परीक्षा। न्यूनतम योग्यता: किसी भी मान्यता प्राप्त विश्वविद्यालय से स्नातक।",
        "location": "All India"
    },
    {
        "job_id": "JOB-STATE-POLICE-2026",
        "title_en": "State Police Constable & Sub-Inspector (SI) Recruitment",
        "title_hi": "राज्य पुलिस कांस्टेबल एवं उप-निरीक्षक भर्ती",
        "organization": "State Police Recruitment Board",
        "category": "Police & Law Enforcement",
        "qualification_required": "12th",
        "min_age": 18,
        "max_age": 25,
        "vacancies": "12,500 Posts",
        "application_deadline": "2026-10-18",
        "official_portal": "https://police.gov.in",
        "summary_en": "Recruitment of Constable (Civil Police and Armed Police) for 12th pass candidates with physical fitness standards.",
        "summary_hi": "12वीं पास युवाओं के लिए राज्य पुलिस में कांस्टेबल पद हेतु सीधी भर्ती परीक्षा। शारीरिक दक्षता एवं लिखित परीक्षा के आधार पर चयन।",
        "location": "State Level"
    },
    {
        "job_id": "JOB-POSTAL-GDS-2026",
        "title_en": "India Post Gramin Dak Sevak (GDS) Recruitment",
        "title_hi": "भारतीय डाक विभाग ग्रामीण डाक सेवक (जीडीएस) भर्ती",
        "organization": "Department of Posts (India Post)",
        "category": "Postal & Communications",
        "qualification_required": "10th",
        "min_age": 18,
        "max_age": 40,
        "vacancies": "44,228 Posts",
        "application_deadline": "2026-10-12",
        "official_portal": "https://indiapostgdsonline.gov.in",
        "summary_en": "No written exam recruitment for Branch Postmaster (BPM) and Assistant Branch Postmaster (ABPM) based directly on 10th class marks merit list.",
        "summary_hi": "बिना किसी लिखित परीक्षा के 10वीं के अंकों की मेरिट के आधार पर डाक विभाग में ग्रामीण डाक सेवक की सीधी भर्ती।",
        "location": "All India"
    },
    {
        "job_id": "JOB-CTET-TEACHER-2026",
        "title_en": "Central Teacher Eligibility Test (CTET) / KVS-NVS Teacher Recruitment",
        "title_hi": "केंद्रीय शिक्षक पात्रता परीक्षा (सीटेट) एवं शिक्षक भर्ती",
        "organization": "Central Board of Secondary Education (CBSE) / KVS",
        "category": "Education & Teaching",
        "qualification_required": "Graduate",
        "min_age": 18,
        "max_age": 35,
        "vacancies": "8,200 Posts",
        "application_deadline": "2026-11-05",
        "official_portal": "https://ctet.nic.in",
        "summary_en": "Recruitment for Primary Teacher (PRT), Trained Graduate Teacher (TGT), and Post Graduate Teacher (PGT) in Kendriya Vidyalayas and Navodaya Vidyalayas. Requires Graduation + B.Ed/D.El.Ed.",
        "summary_hi": "केंद्रीय विद्यालयों एवं नवोदय विद्यालयों में सरकारी शिक्षक पदों के लिए भर्ती। स्नातक + बी.एड या डी.एल.एड डिग्री आवश्यक।",
        "location": "All India"
    }
]

# 3. IndicNLP Multilingual Benchmark Query Corpus (English & Hindi)
INDIC_QUERIES = [
    {
        "query_en": "What government schemes provide financial help to poor farmers?",
        "query_hi": "गरीब किसानों को आर्थिक सहायता देने वाली सरकारी योजना कौन सी है?",
        "target_scheme_id": "SCH-PM-KISAN",
        "category": "Agriculture"
    },
    {
        "query_en": "How to get free hospital treatment up to 5 lakh rupees?",
        "query_hi": "5 लाख तक का मुफ्त अस्पताल इलाज और आयुष्मान कार्ड कैसे बनवाएं?",
        "target_scheme_id": "SCH-PMJAY",
        "category": "Healthcare"
    },
    {
        "query_en": "I passed 10th class, which government jobs can I apply for right now?",
        "query_hi": "मैंने 10वीं पास की है, मुझे कौन सी सरकारी नौकरी मिल सकती है?",
        "target_job_id": "JOB-SSC-GD-2026",
        "category": "Jobs-10th"
    },
    {
        "query_en": "I have completed 12th standard, what are the latest vacancy notifications?",
        "query_hi": "12वीं पास के लिए कौन सी नई सरकारी भर्तियां निकली हैं?",
        "target_job_id": "JOB-SSC-CHSL-2026",
        "category": "Jobs-12th"
    },
    {
        "query_en": "I am a graduate looking for government bank officer jobs",
        "query_hi": "मैं ग्रेजुएट हूँ और सरकारी बैंक पीओ नौकरी के लिए आवेदन करना चाहता हूँ",
        "target_job_id": "JOB-IBPS-PO-2026",
        "category": "Jobs-Graduate"
    },
    {
        "query_en": "Government loan scheme to start small business without mortgage or collateral",
        "query_hi": "बिना गारंटी छोटा व्यापार या दुकान शुरू करने के लिए सरकारी मुद्रा लोन कैसे मिलेगा?",
        "target_scheme_id": "SCH-PM-MUDRA",
        "category": "Business Loan"
    },
    {
        "query_en": "What schemes exist for girl child savings and education?",
        "query_hi": "बेटी की पढ़ाई और भविष्य के लिए सुकन्या समृद्धि योजना क्या है?",
        "target_scheme_id": "SCH-SUKANYA",
        "category": "Women & Child"
    },
    {
        "query_en": "Scholarship for SC ST OBC college students to pay tuition fees",
        "query_hi": "कॉलेज फीस भरने के लिए एससी एसटी ओबीसी छात्रों की छात्रवृत्ति योजना",
        "target_scheme_id": "SCH-POST-MATRIC-SCHOLARSHIP",
        "category": "Scholarship"
    },
    {
        "query_en": "How can artisans like carpenters or tailors get tools and training loan?",
        "query_hi": "बढ़ई या दर्जी जैसे कारीगरों को टूलकिट और 5% पर लोन किस योजना से मिलेगा?",
        "target_scheme_id": "SCH-PM-VISHWAKARMA",
        "category": "Artisans"
    },
    {
        "query_en": "Are there government jobs with no written exam based only on 10th marks?",
        "query_hi": "बिना परीक्षा सिर्फ 10वीं के नंबर पर डाक विभाग जीडीएस भर्ती कैसे होती है?",
        "target_job_id": "JOB-POSTAL-GDS-2026",
        "category": "Jobs-10th"
    }
]

def preprocess_and_save():
    # Save raw data
    with open(DATA_RAW / "schemes_myscheme.json", "w", encoding="utf-8") as f:
        json.dump(SCHEMES, f, ensure_ascii=False, indent=2)
    
    with open(DATA_RAW / "government_jobs.json", "w", encoding="utf-8") as f:
        json.dump(JOBS, f, ensure_ascii=False, indent=2)

    with open(DATA_RAW / "indic_nlp_pairs.json", "w", encoding="utf-8") as f:
        json.dump(INDIC_QUERIES, f, ensure_ascii=False, indent=2)

    # Process schemes for RAG indexing
    processed_schemes = []
    for s in SCHEMES:
        # Searchable multilingual text block
        search_text = (
            f"Scheme Title: {s['title_en']} | {s['title_hi']}\n"
            f"Category: {s['category']}\n"
            f"Summary (English): {s['summary_en']}\n"
            f"Summary (Hindi): {s['summary_hi']}\n"
            f"Benefits: {s['benefits_en']} | {s['benefits_hi']}\n"
            f"Eligibility: Min Age {s['eligibility']['min_age']}, Max Age {s['eligibility']['max_age']}, "
            f"Gender {s['eligibility']['gender']}, Qualification {s['eligibility']['min_qualification']}, "
            f"State {s['eligibility']['state']}, Occupation {s['eligibility']['occupation']}\n"
            f"Documents Required: {', '.join(s['documents_required'])}\n"
            f"Tags: {', '.join(s['tags'])}"
        )
        item = dict(s)
        item["search_text"] = search_text
        processed_schemes.append(item)

    with open(DATA_PROCESSED / "schemes_processed.json", "w", encoding="utf-8") as f:
        json.dump(processed_schemes, f, ensure_ascii=False, indent=2)

    # Process jobs for qualification indexing & RAG
    processed_jobs = []
    for j in JOBS:
        search_text = (
            f"Job Title: {j['title_en']} | {j['title_hi']}\n"
            f"Organization: {j['organization']}\n"
            f"Category: {j['category']}\n"
            f"Qualification Required: {j['qualification_required']}\n"
            f"Age Limit: {j['min_age']} to {j['max_age']} years\n"
            f"Vacancies: {j['vacancies']}\n"
            f"Deadline: {j['application_deadline']}\n"
            f"Summary (English): {j['summary_en']}\n"
            f"Summary (Hindi): {j['summary_hi']}\n"
            f"Official Link: {j['official_portal']}"
        )
        item = dict(j)
        item["search_text"] = search_text
        processed_jobs.append(item)

    with open(DATA_PROCESSED / "jobs_processed.json", "w", encoding="utf-8") as f:
        json.dump(processed_jobs, f, ensure_ascii=False, indent=2)

    # Process Indic Queries
    with open(DATA_PROCESSED / "indic_corpus.json", "w", encoding="utf-8") as f:
        json.dump(INDIC_QUERIES, f, ensure_ascii=False, indent=2)

    print(f"[OK] Generated {len(processed_schemes)} processed schemes.")
    print(f"[OK] Generated {len(processed_jobs)} processed job recruitment notifications.")
    print(f"[OK] Generated {len(INDIC_QUERIES)} IndicNLP multilingual evaluation pairs.")

if __name__ == "__main__":
    preprocess_and_save()
