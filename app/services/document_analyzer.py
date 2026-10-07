import re
from typing import Dict, Any, List, Optional
from app.ml.rag_engine import MultilingualRAGEngine
from app.core.i18n import t

DOCUMENT_TEMPLATES = {
    "tender": {
        "en": {
            "title": "Official E-Tender & Procurement Notice (NIT)",
            "meaning": "This document is an official government tender or Notice Inviting Tender (NIT) for public works, equipment supply, or services contract.",
            "action": "Contractors/vendors must register their Digital Signature Certificate (DSC Token) on the e-Procurement portal, verify BOQ specifications, deposit the EMD or submit MSME exemption, and upload technical & financial bids before the closing deadline.",
            "safety": "Always submit bids strictly through official government e-procurement portals (eprocure.gov.in / gem.gov.in). Never transfer EMD or processing fees to personal bank accounts."
        },
        "hi": {
            "title": "आधिकारिक ई-निविदा एवं अधिप्राप्ति सूचना (NIT)",
            "meaning": "यह दस्तावेज सरकारी कार्य, उपकरण आपूर्ति अथवा सेवा अनुबंध हेतु जारी की गई आधिकारिक ई-निविदा (टेंडर सूचना) है।",
            "action": "ठेकेदार अथवा विक्रेता आधिकारिक ई-प्रोक्योरमेंट पोर्टल पर अपना डिजिटल सिग्नेचर (DSC) पंजीकृत करें, धरोहर राशि (EMD) जमा करें या एमएसएमई छूट प्रमाण पत्र संलग्न करें और समयसीमा से पहले तकनीकी व वित्तीय बोली जमा करें।",
            "safety": "निविदा बोली केवल आधिकारिक सरकारी पोर्टल (eprocure.gov.in / gem.gov.in) पर ही जमा करें। किसी भी व्यक्ति के व्यक्तिगत खाते में धरोहर राशि या शुल्क न भेजें।"
        },
        "bn": {
            "title": "অফিসিয়াল ই-টেন্ডার ও ক্রয় বিজ্ঞপ্তি (NIT)",
            "meaning": "এই নথিটি সরকারি নির্মাণ কাজ, সরঞ্জাম সরবরাহ বা পরিষেবা চুক্তির জন্য প্রকাশিত একটি অফিসিয়াল ই-টেন্ডার বিজ্ঞপ্তি।",
            "action": "ঠিকাদার বা বিক্রেতাদের অফিসিয়াল ই-প্রোকিউরমেন্ট পোর্টালে ডিজিটাল স্বাক্ষর নিবন্ধন করতে হবে, ইএমডি জমা দিতে হবে এবং নির্ধারিত সময়ের পূর্বে কারিগরি ও আর্থিক দরপত্র জমা দিতে হবে।",
            "safety": "শুধুমাত্র অফিসিয়াল সরকারি পোর্টালে (eprocure.gov.in) দরপত্র জমা দিন। ব্যক্তিগত অ্যাকাউন্টে কোনো ফি প্রদান করবেন না।"
        },
        "te": {
            "title": "అధికారిక ఈ-టెండర్ మరియు సేకరణ నోటీసు (NIT)",
            "meaning": "ఈ పత్రం ప్రభుత్వ పనులు, పరికరాల సరఫరా లేదా సేవా కాంట్రాక్టు కోసం విడుదల చేసిన అధికారిక ఈ-టెండర్ ఆహ్వాన నోటీసు.",
            "action": "కాంట్రాక్టర్లు ఈ-ప్రొక్యూర్మెంట్ పోర్టల్‌లో డిజిటల్ సంతకం నమోదు చేసుకోవాలి, ఈఎండి చెల్లించాలి మరియు గడువు ముగిసేలోగా బిడ్లను సమర్పించాలి.",
            "safety": "కేవలం అధికారిక ప్రభుత్వ పోర్టల్ ద్వారా మాత్రమే టెండర్లలో పాల్గొనండి. వ్యక్తిగత ఖాతాలకు ఎటువంటి రుసుము చెల్లించవద్దు."
        },
        "gu": {
            "title": "સત્તાવાર ઇ-ટેન્ડર અને પ્રાપ્તિ સૂચના (NIT)",
            "meaning": "આ દસ્તાવેજ સરકારી કામકાજ, સાધન સામગ્રી સપ્લાય અથવા સર્વિસ કોન્ટ્રાક્ટ માટે બહાર પાડવામાં આવેલ સત્તાવાર ટેન્ડર નોટિસ છે.",
            "action": "કોન્ટ્રાક્ટરોએ ઇ-પ્રોક્યોરમેન્ટ પોર્ટલ પર ડિજિટલ સહી રજીસ્ટર કરવી, ઇએમડી જમા કરવી અને છેલ્લી તારીખ પહેલાં બિડ સબમિટ કરવી.",
            "safety": "માત્ર સત્તાવાર સરકારી પોર્ટલ દ્વારા જ ટેન્ડર પ્રક્રિયા પૂર્ણ કરો. અજાણ્યા વ્યક્તિઓને કોઈ નાણાં ચૂકવશો નહીં."
        },
        "ur": {
            "title": "سرکاری ای ٹینڈر اور پروکیورمنٹ نوٹس (NIT)",
            "meaning": "یہ دستاویز سرکاری تعمیراتی کاموں، سامان کی فراہمی یا سروس کنٹریکٹ کے لیے جاری کردہ سرکاری ای ٹینڈر نوٹس ہے۔",
            "action": "ٹھیکیداروں کو ای پروکیورمنٹ پورٹل پر ڈیجیٹل دستخط رجسٹر کرنا، ای ایم ڈی جمع کرانا اور مقررہ تاریخ سے پہلے بولی داخل کرنا لازمی ہے۔",
            "safety": "ہمیشہ سرکاری ای پروکیورمنٹ پورٹل کے ذریعے ہی ٹینڈر جمع کرائیں۔ کسی بھی ذاتی اکاؤنٹ میں رقم منتقل نہ کریں۔"
        }
    },
    "newspaper": {
        "en": {
            "title": "Newspaper Notice & Public Announcement",
            "meaning": "This document is a public notice, administrative circular, or news announcement issued for the information and compliance of citizens.",
            "action": "Carefully review the guidelines, verify whether your locality or family category is affected, and keep relevant certificates/identities ready for verification at the designated government office or portal.",
            "safety": "Verify all newspaper notices on the concerned department's official website (.gov.in / .nic.in) before acting on instructions."
        },
        "hi": {
            "title": "समाचार पत्र सूचना एवं सार्वजनिक विज्ञप्ति",
            "meaning": "यह दस्तावेज आम नागरिकों की जानकारी, अनुपालन एवं सार्वजनिक हित हेतु प्रकाशित सरकारी विज्ञप्ति अथवा समाचार सूचना है।",
            "action": "दिशानिर्देशों को ध्यानपूर्वक पढ़ें, सुनिश्चित करें कि आपका क्षेत्र या वर्ग इससे संबंधित है या नहीं, तथा निर्धारित तिथि से पूर्व आवश्यक दस्तावेज तैयार रखें।",
            "safety": "समाचार पत्र में प्रकाशित सूचना को संबंधित विभाग की आधिकारिक वेबसाइट (.gov.in / .nic.in) पर अवश्य सत्यापित करें।"
        },
        "bn": {
            "title": "সংবাদপত্রের বিজ্ঞপ্তি ও গণবিজ্ঞপ্তি",
            "meaning": "এই নথিটি সাধারণ নাগরিকদের অবগতি ও নির্দেশনার জন্য সংবাদপত্রে প্রকাশিত একটি সরকারি গণবিজ্ঞপ্তি।",
            "action": "বিজ্ঞপ্তির নির্দেশাবলী সতর্কতার সাথে পড়ুন এবং প্রয়োজনীয় প্রমাণপত্র প্রস্তুত রাখুন।",
            "safety": "যে কোনো পদক্ষেপ নেওয়ার আগে সংশ্লিষ্ট সরকারি ওয়েবসাইটে বিজ্ঞপ্তিটি যাচাই করুন।"
        },
        "te": {
            "title": "వార్తాపత్రిక ప్రకటన & ప్రజా నోటీసు",
            "meaning": "ఈ పత్రం పౌరుల సమాచారం మరియు అవగాహన కొరకు వార్తాపత్రికలో విడుదల చేయబడిన అధికారిక ప్రభుత్వ ప్రకటన.",
            "action": "సూచనలను శ్రద్ధగా చదివి, నిర్దేశిత గడువులోగా తగిన పత్రాలను సిద్ధం చేసుకోండి.",
            "safety": "అధికారిక ప్రభుత్వ వెబ్‌సైట్ ద్వారా ప్రకటనను ధృవీకరించుకోండి."
        },
        "gu": {
            "title": "સમાચાર પત્ર જાહેરાત અને જાહેર નોટિસ",
            "meaning": "આ દસ્તાવેજ સામાન્ય નાગરિકોની જાણકારી અને માર્ગદર્શન માટે સમાચાર પત્રમાં પ્રકાશિત સત્તાવાર સરકારી જાહેરાત છે.",
            "action": "માર્ગદર્શિકા ધ્યાનથી વાંચો અને છેલ્લી તારીખ પહેલાં જરૂરી પ્રક્રિયા પૂર્ણ કરો.",
            "safety": "સત્તાવાર સરકારી વેબસાઇટ પરથી વિગતોની ખરાઈ અવશ્ય કરો."
        },
        "ur": {
            "title": "اخبار کا اشتہار اور عوامی اطلاع",
            "meaning": "یہ دستاویز عام شہریوں کی آگاہی اور معلومات کے لیے اخبار میں شائع کردہ سرکاری نوٹس ہے۔",
            "action": "ہدایات کو غور سے پڑھیں اور آخری تاریخ سے پہلے ضروری دستاویزات تیار رکھیں۔",
            "safety": "کوئی بھی اقدام کرنے سے پہلے متعلقہ سرکاری ویب سائٹ سے تصدیق کر لیں۔"
        }
    },
    "job": {
        "en": {
            "title": "Official Government Job Recruitment Notice",
            "meaning": "This document is an official recruitment notification for vacant government positions announcing eligibility, exam schedule, and vacancies.",
            "action": "Verify age limit and educational qualification, register on the commission/department recruitment portal, upload photo and signature, pay the exam fee, and submit before the application deadline.",
            "safety": "Recruitments in government are conducted strictly through merit and official portals. Beware of unauthorized agents demanding bribes."
        },
        "hi": {
            "title": "सरकारी भर्ती एवं आवेदन सूचना",
            "meaning": "यह दस्तावेज सरकारी विभाग में रिक्त पदों पर चयन हेतु जारी की गई आधिकारिक भर्ती अधिसूचना है।",
            "action": "अपनी आयु सीमा एवं शैक्षणिक योग्यता की जांच करें, आयोग की आधिकारिक वेबसाइट पर पंजीकरण करें, फोटो व हस्ताक्षर अपलोड करें और अंतिम तिथि से पूर्व आवेदन शुल्क जमा कर फॉर्म सबमिट करें।",
            "safety": "सरकारी नौकरियां केवल योग्यता व आधिकारिक परीक्षा से मिलती हैं। फर्जी नौकरी रैकेट एवं बिचौलियों से सावधान रहें।"
        },
        "bn": {
            "title": "সরকারি নিয়োগ ও আবেদন বিজ্ঞপ্তি",
            "meaning": "এই নথিটি সরকারি দপ্তরে শূন্যপদে নিয়োগের জন্য প্রকাশিত একটি আনুষ্ঠানিক বিজ্ঞপ্তি।",
            "action": "শিক্ষাগত যোগ্যতা ও বয়স যাচাই করে নির্ধারিত সময়ের মধ্যে অনলাইনে আবেদনপত্র জমা দিন।",
            "safety": "চাকরির জন্য দালাল বা প্রতারকদের প্রলোভনে পা দেবেন না, সর্বদা অফিসিয়াল পোর্টালে আবেদন করুন।"
        },
        "te": {
            "title": "ప్రభుత్వ ఉద్యోగ నియామక ప్రకటన",
            "meaning": "ఈ పత్రం ప్రభుత్వ విభాగంలో ఖాళీగా ఉన్న పోస్టుల భర్తీ కోసం విడుదల చేసిన అధికారిక నోటిఫికేషన్.",
            "action": "విద్యార్హతలు మరియు వయోపరిమితిని సరిచూసుకొని, అధికారిక వెబ్‌సైట్‌లో గడువు ముగిసేలోగా దరఖాస్తు చేసుకోండి.",
            "safety": "ఉద్యోగాల పేరిట మోసం చేసే దళారులను నమ్మవద్దు. అధికారిక ప్రక్రియను మాత్రమే అనుసరించండి."
        },
        "gu": {
            "title": "સરકારી ભરતી અને અરજી જાહેરાત",
            "meaning": "આ દસ્તાવેજ સરકારી વિભાગમાં ખાલી જગ્યાઓ ભરવા માટે બહાર પાડવામાં આવેલ સત્તાવાર ભરતી જાહેરાત છે.",
            "action": "શૈક્ષણિક લાયકાત અને વયમર્યાદા ચકાસીને સત્તાવાર પોર્ટલ પર સમયસર ઓનલાઇન અરજી કરો.",
            "safety": "નોકરી અપાવવાના બહાને નાણાં પડાવતા લેભાગુ તત્વોથી સાવચેત રહો."
        },
        "ur": {
            "title": "سرکاری ملازمت اور درخواست کا نوٹس",
            "meaning": "یہ دستاویز سرکاری محکمے میں خالی آسامیوں پر بھرتی کے لیے جاری کردہ سرکاری نوٹیفکیشن ہے۔",
            "action": "تعلیمی قابلیت اور عمر کی حد چیک کریں اور سرکاری پورٹل پر آخری تاریخ سے پہلے آن لائن درخواست دیں۔",
            "safety": "نوکری دلانے کے نام پر رشوت مانگنے والے جعلسازوں سے ہوشیار رہیں۔"
        }
    },
    "scheme": {
        "en": {
            "title": "Government Welfare Scheme & Citizen Subsidy Circular",
            "meaning": "This official circular provides direct financial benefits, subsidies, agricultural grants, or social security support to eligible citizens.",
            "action": "Ensure your bank account is seeded with Aadhaar for Direct Benefit Transfer (DBT), complete biometric or OTP e-KYC on the portal, and track status with your registered mobile number.",
            "safety": "All welfare schemes under Digital India are 100% free of charge. No government official will ask you for your ATM PIN, OTP, or UPI MPIN."
        },
        "hi": {
            "title": "सरकारी जनकल्याणकारी योजना परिपत्र",
            "meaning": "यह परिपत्र पात्र नागरिकों को प्रत्यक्ष वित्तीय सहायता, कृषि अनुदान, पेंशन अथवा सामाजिक सुरक्षा लाभ प्रदान करने वाली आधिकारिक योजना से संबंधित है।",
            "action": "प्रत्यक्ष लाभ अंतरण (DBT) हेतु बैंक खाते को आधार से लिंक कराएं, पोर्टल पर ई-केवाईसी (e-KYC) पूर्ण करें तथा आवेदन स्थिति की जांच करें।",
            "safety": "सरकारी योजनाएं पूर्णतः निःशुल्क हैं। किसी को भी अपना बैंक ओटीपी (OTP), एटीएम पिन या यूपीआई पिन साझा न करें।"
        },
        "bn": {
            "title": "সরকারি কল্যাণমূলক প্রকল্প নির্দেশিকা",
            "meaning": "এই বিজ্ঞপ্তিটি যোগ্য নাগরিকদের জন্য আর্থিক অনুদান, ভর্তুকি বা সামাজিক নিরাপত্তা সুবিধা প্রদানকারী একটি সরকারি প্রকল্প।",
            "action": "ব্যাঙ্ক অ্যাকাউন্টে আধার সংযুক্ত করুন (DBT), ই-কেওয়াইসি সম্পন্ন করুন এবং পোর্টালে আবেদন করুন।",
            "safety": "সরকারি প্রকল্প সম্পূর্ণ বিনামূল্যে। কাউকে ওটিপি বা পিন নম্বর শেয়ার করবেন না।"
        },
        "te": {
            "title": "ప్రభుత్వ సంక్షేమ పథక మార్గదర్శకాలు",
            "meaning": "ఈ పత్రం అర్హులైన పౌరులకు ఆర్థిక సహాయం, సబ్సిడీ లేదా పింఛను అందించే అధికారిక సంక్షేమ పథకానికి సంబంధించినది.",
            "action": "బ్యాంకు ఖాతాకు ఆధార్ అనుసంధానం చేయించుకోండి (DBT), ఈ-కేవైసీ పూర్తి చేసి దరఖాస్తును సమర్పించండి.",
            "safety": "ప్రభుత్వ పథకాలు పూర్తిగా ఉచితం. ఓటీపీ లేదా బ్యాంకు వివరాలను ఎవరికీ చెప్పవద్దు."
        },
        "gu": {
            "title": "સરકારી કલ્યાણકારી યોજના પરિપત્ર",
            "meaning": "આ પરિપત્ર પાત્ર નાગરિકોને સીધી આર્થિક સહાય, સબસિડી કે સામાજિક સુરક્ષા પૂરી પાડતી સત્તાવાર યોજના સાથે સંબંધિત છે.",
            "action": "બેંક ખાતા સાથે આધાર લિંક કરાવો (DBT), ઈ-કેવાયસી પૂર્ણ કરો અને સત્તાવાર પોર્ટલ પરથી લાભ મેળવો.",
            "safety": "સરકારી યોજનાઓ મફત છે. કોઈની પણ સાથે તમારો ઓટીપી કે પિન શેર કરશો નહીં."
        },
        "ur": {
            "title": "سرکاری فلاحی اسکیم کا سرکلر",
            "meaning": "یہ سرکلر اہل شہریوں کو مالی امداد، سبسڈی یا پنشن فراہم کرنے والی سرکاری فلاحی اسکیم سے متعلق ہے۔",
            "action": "بینک اکاؤنٹ کے ساتھ آدھار لنک کروائیں (DBT)، ای کے وائی سی مکمل کریں اور سرکاری پورٹل پر اندراج کریں۔",
            "safety": "تمام سرکاری اسکیمیں مفت ہیں۔ اپنا او ٹی پی یا پن کسی کے ساتھ شیئر نہ کریں۔"
        }
    },
    "general": {
        "en": {
            "title": "Official Government Circular & Administrative Order",
            "meaning": "This document contains official directives, statutory rules, or policy guidelines issued by the government administration.",
            "action": "Review the relevant clauses that pertain to your district, institution, or category and comply with the mentioned instructions.",
            "safety": "Verify circular authenticity through the National Portal of India (india.gov.in) or the State Gazette portal."
        },
        "hi": {
            "title": "आधिकारिक सरकारी आदेश / प्रशासनिक परिपत्र",
            "meaning": "यह दस्तावेज सरकारी प्रशासन द्वारा जारी आधिकारिक दिशा-निर्देश, नीतिगत निर्णय अथवा वैधानिक आदेश है।",
            "action": "दस्तावेज में दिए गए नियमों का अध्ययन करें तथा संबंधित विभाग द्वारा दिए गए निर्देशों का पालन करें।",
            "safety": "संदेह होने पर आदेश की प्रमाणिकता राज्य के आधिकारिक गजट अथवा india.gov.in से सत्यापित करें।"
        },
        "bn": {
            "title": "সরকারি নির্দেশনামা ও প্রশাসনিক সার্কুলার",
            "meaning": "এই নথিটি প্রশাসনিক নির্দেশাবলী ও সরকারি নীতিমালা সম্বলিত একটি সরকারি আদেশ।",
            "action": "নথির নিয়মাবলী অনুসরণ করুন এবং প্রয়োজনীয় নির্দেশ পালন করুন।",
            "safety": "অফিসিয়াল গ্যাজেট বা সরকারি পোর্টাল থেকে সত্যতা যাচাই করুন।"
        },
        "te": {
            "title": "అధికారిక ప్రభుత్వ ఉత్తర్వు / పరిపాలనా పత్రం",
            "meaning": "ఈ పత్రం ప్రభుత్వ పరిపాలన విడుదల చేసిన అధికారిక మార్గదర్శకాలు లేదా ఉత్తర్వులు.",
            "action": "నిబంధనలను పరిశీలించి సంబంధిత విభాగ ఆదేశాలను పాటించండి.",
            "safety": "ప్రభుత్వ పోర్టల్ ద్వారా ఉత్తర్వును ధృవీకరించుకోండి."
        },
        "gu": {
            "title": "સત્તાવાર સરકારી પરિપત્ર / વહીવટી આદેશ",
            "meaning": "આ દસ્તાવેજ સરકારી વહીવટ દ્વારા બહાર પાડવામાં આવેલ સત્તાવાર માર્ગદર્શિકા કે નીતિ વિષયક આદેશ છે.",
            "action": "નિયમોનું પાલન કરો અને સૂચવેલ પગલાં લો.",
            "safety": "સરકારી પોર્ટલ પરથી આદેશની સત્યતા તપાસો."
        },
        "ur": {
            "title": "سرکاری حکم نامہ اور انتظامی سرکلر",
            "meaning": "یہ دستاویز سرکاری انتظامیہ کی جانب سے جاری کردہ باضابطہ ہدایات یا پالیسی سے متعلق ہے۔",
            "action": "دی گئی ہدایات پر عمل کریں اور مجاز افسران سے رابطہ کریں۔",
            "safety": "حکم نامے کی تصدیق سرکاری گزیٹ یا پورٹل سے کریں۔"
        }
    }
}

class DocumentAnalyzer:
    _instance = None

    def __init__(self):
        self.rag = MultilingualRAGEngine.get_instance()

    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def classify_document(self, text: str) -> str:
        """Classifies document into: tender, newspaper, job, scheme, or general."""
        t_low = text.lower()

        # 1. Tender Keywords
        tender_signals = [
            "tender", "notice inviting tender", "nit no", "e-tender", "etender", "procurement",
            "earnest money", "emd", "rfp", "request for proposal", "contractor", "bidder",
            "bidding", "boq", "bill of quantities", "work order", "corrigendum", "tender fee",
            "estimated cost", "bid opening", "eprocure", "gem.gov.in", "cppp",
            "निविदा", "ई-निविदा", "धरोहर राशि", "अनुमानित लागत", "ठेकेदार", "कार्य का नाम", "बोली"
        ]
        tender_score = sum(2 if sig in ["notice inviting tender", "nit no", "e-tender", "धरोहर राशि", "निविदा आमंत्रण"] else 1
                           for sig in tender_signals if sig in t_low)

        # 2. Newspaper / Public Announcement Signals
        newspaper_signals = [
            "newspaper", "press release", "press note", "public notice", "advertisement",
            "vigyapti", "gazette", "dainik", "patrika", "amar ujala", "bhaskar", "times of india",
            "the hindu", "hindustan", "samachar", "circular no",
            "दैनिक", "विज्ञप्ति", "प्रेस नोट", "सार्वजनिक विज्ञप्ति", "आम सूचना", "सर्वसाधारण को सूचित",
            "सर्वसाधारण", "अखबार", "समाचार पत्र"
        ]
        newspaper_score = sum(2 if sig in ["press release", "public notice", "सर्वसाधारण को सूचित", "आम सूचना", "विज्ञप्ति"] else 1
                              for sig in newspaper_signals if sig in t_low)

        # 3. Job / Recruitment Signals
        job_signals = [
            "recruitment", "vacancy", "vacancies", "advt no", "advertisement no", "post of",
            "apply online", "eligibility criteria", "educational qualification", "age limit",
            "written exam", "admit card", "hall ticket", "selection procedure", "tier-1",
            "ssc", "upsc", "ibps", "rrb", "pay scale", "grade pay",
            "भर्ती", "रिक्तियां", "पद", "विज्ञापन संख्या", "ऑनलाइन आवेदन", "शैक्षणिक योग्यता",
            "आयु सीमा", "प्रवेश पत्र", "चयन प्रक्रिया"
        ]
        job_score = sum(2 if sig in ["recruitment", "advt no", "apply online", "भर्ती", "विज्ञापन संख्या"] else 1
                        for sig in job_signals if sig in t_low)

        # 4. Welfare Scheme Signals
        scheme_signals = [
            "scheme", "yojana", "subsidy", "financial assistance", "dbt", "direct benefit transfer",
            "beneficiary", "kalyan", "pension", "pradhan mantri", "pm-kisan", "ayushman",
            "awas yojana", "scholarship", "aadhaar seeding", "ration card", "kisan",
            "योजना", "कल्याण", "सब्सिडी", "अनुदान", "वित्तीय सहायता", "डीबीटी", "लाभार्थी", "पेंशन", "किसान", "आवास"
        ]
        scheme_score = sum(2 if sig in ["dbt", "direct benefit transfer", "pm-kisan", "yojana", "योजना", "सब्सिडी"] else 1
                           for sig in scheme_signals if sig in t_low)

        # Weighted decision
        scores = {
            "tender": tender_score,
            "newspaper": newspaper_score,
            "job": job_score,
            "scheme": scheme_score
        }
        best_cat = max(scores, key=scores.get)
        if scores[best_cat] > 0:
            return best_cat
        return "general"

    def extract_rich_entities(self, text: str) -> Dict[str, Any]:
        """Extracts crucial fields: authority, reference/NIT numbers, dates, financials, eligibility."""
        
        # 1. Authority / Department
        authority = "Government Authority / Competent Department"
        dept_patterns = [
            r"(?:जिलाधिकारी\s*कार्यालय[^\n\r,.]*|कलेक्ट्रेट[^\n\r,.]*|नगर\s*निगम[^\n\r,.]*|विकास\s*प्राधिकरण[^\n\r,.]*|महानिदेशालय[^\n\r,.]*)",
            r"(?:Central Public Works Department|CPWD|NHAI|Staff Selection Commission|SSC|UPSC|Railway Recruitment Board|RRB|State Public Works Department|PWD|Indian Railways)",
            r"(?:Ministry of\s+[A-Za-z\s]{3,40}|Department of\s+[A-Za-z\s]{3,40}|Government of\s+[A-Za-z\s]{3,40}|[A-Za-z\s]{3,30}\s+Corporation|[A-Za-z\s]{3,30}\s+Commission)"
        ]
        for dp in dept_patterns:
            dm = re.search(dp, text, re.IGNORECASE)
            if dm:
                authority = dm.group(0).strip()
                break

        # 2. Reference / NIT / Advt Number
        ref_no = "N/A"
        ref_patterns = [
            r"(?:NIT\s*(?:No\.?|Number)|Tender\s*(?:No\.?|ID)|Advt\.?\s*No\.?|Notification\s*No\.?|Notice\s*No\.?|Ref\s*No\.?|विज्ञापन\s*संख्या|निविदा\s*संख्या|पत्रांक)\s*[:=-]?\s*([A-Za-z0-9\/\-_]+(?:\s*[A-Za-z0-9\/\-_]+)?)",
            r"\b(?:Tender\s*ID\s*[:=-]?\s*(\d{4}_[A-Za-z0-9_]+))\b"
        ]
        for pat in ref_patterns:
            m = re.search(pat, text, re.IGNORECASE)
            if m:
                ref_no = m.group(1).strip()
                break

        # 3. Dates & Deadlines
        dates = re.findall(r"\b\d{1,2}[/-]\d{1,2}[/-]\d{2,4}\b|\b\d{4}-\d{2}-\d{2}\b|\b\d{1,2}(?:st|nd|rd|th)?\s+(?:January|February|March|April|May|June|July|August|September|October|November|December|Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\s*,?\s*\d{2,4}\b", text, re.IGNORECASE)
        
        # Look specifically for deadline date following keywords
        deadline_text = "Refer to notice for closing date"
        deadline_match = re.search(r"(?:Last\s*Date|Closing\s*Date|Submission\s*Deadline|Due\s*Date|अंतिम\s*तिथि|समाप्ति\s*तिथि)[^\d\n\r]*(\d{1,2}[/-]\d{1,2}[/-]\d{2,4}|\d{1,2}(?:st|nd|rd|th)?\s+[A-Za-z]+\s+\d{2,4})", text, re.IGNORECASE)
        if deadline_match:
            deadline_text = deadline_match.group(1).strip()
        elif dates:
            deadline_text = dates[-1]

        # 4. Financials / Cost / EMD / Benefit
        financials = []
        money_matches = re.findall(r"(?:₹|Rs\.?|INR)\s*[\d,]+(?:\.\d+)?|\b\d+(?:,\d+)*(?:\.\d+)?\s*(?:Lakh|Crore|Lakhs|Crores|हजार|लाख|करोड़)\b", text, re.IGNORECASE)
        if money_matches:
            financials.extend(money_matches[:4])
        
        emd_info = "Refer to notice document"
        emd_match = re.search(r"(?:EMD|Earnest\s*Money(?:\s*Deposit)?|धरोहर\s*राशि)[^\d\n\r₹RsINR]*((?:₹|Rs\.?|INR)\s*[\d,]+(?:\.\d+)?|\d+\s*(?:Lakh|Crore|हजार|लाख))", text, re.IGNORECASE)
        if emd_match:
            emd_info = emd_match.group(1).strip()
        elif "tender" not in text.lower():
            emd_info = "Direct Benefit Transfer / Government Grant"

        # 5. Qualifications & Eligibility Mentions
        quals = [q for q in ["8th", "10th", "12th", "Diploma", "ITI", "Graduate", "Post Graduate", "B.Tech", "BE", "Any Degree"] if re.search(rf"\b{re.escape(q)}\b", text, re.IGNORECASE)]
        contractor_cats = re.findall(r"\b(?:Class\s*[-A-Z0-9]+|Category\s*[-A-Z0-9]+|Registered Contractor|GSTIN|PAN)\b", text, re.IGNORECASE)
        age_mentions = re.findall(r"(?:age|आयु)\s*[:=-]?\s*(\d{1,2}\s*(?:to|-)\s*\d{1,2}|\d{1,2})", text, re.IGNORECASE)

        return {
            "issuing_authority": authority,
            "reference_number": ref_no,
            "dates_found": dates[:6],
            "submission_deadline": deadline_text,
            "financial_amounts": financials,
            "emd_or_grant": emd_info,
            "qualifications": quals,
            "contractor_categories": contractor_cats[:3],
            "age_mentions": age_mentions
        }

    def analyze_document(self, text: str, user_profile: dict = None, preferred_language: str = "en") -> Dict[str, Any]:
        """Comprehensive document explanation for newspaper clippings, tenders, job circulars, and schemes."""
        if not text.strip():
            return {
                "success": False,
                "message": "No text could be extracted from the document."
            }

        lang = preferred_language if preferred_language in ["en", "hi", "bn", "te", "gu", "ur"] else "en"
        doc_category = self.classify_document(text)
        entities = self.extract_rich_entities(text)

        # Semantic check against RAG database for specific scheme or job match
        sample_query = text[:350]
        scheme_matches = self.rag.search_schemes(sample_query, top_k=2)
        job_matches = self.rag.search_jobs(sample_query, top_k=2)

        top_scheme_score = scheme_matches[0]["similarity_score"] if scheme_matches else 0.0
        top_job_score = job_matches[0]["similarity_score"] if job_matches else 0.0

        # Refine doc_category if RAG has very high confidence
        best_rag_match = None
        if doc_category == "scheme" and top_scheme_score >= 0.38:
            best_rag_match = scheme_matches[0]
        elif doc_category == "job" and top_job_score >= 0.38:
            best_rag_match = job_matches[0]

        tpl = DOCUMENT_TEMPLATES.get(doc_category, DOCUMENT_TEMPLATES["general"]).get(lang, DOCUMENT_TEMPLATES["general"]["en"])

        # Construct customized, highly articulate explanation
        authority_name = entities["issuing_authority"]
        ref_no_str = entities["reference_number"]
        deadline_val = entities["submission_deadline"]
        
        # Build category-specific outputs
        if doc_category == "tender":
            doc_type_label = t("doc_type_tender", lang)
            official_url = "https://eprocure.gov.in"
            portal_name = "Central Public Procurement Portal (eprocure.gov.in) & GeM"
            
            # Meaning text
            tender_val_str = ", ".join(entities["financial_amounts"]) if entities["financial_amounts"] else "As per Notice specifications"
            meaning_text = (
                f"{tpl['meaning']}\n\n"
                f"• **Issuing Authority / Client:** {authority_name}\n"
                f"• **Tender / NIT Reference:** {ref_no_str}\n"
                f"• **Estimated Cost / Value:** {tender_val_str}\n"
                f"• **Earnest Money Deposit (EMD):** {entities['emd_or_grant']}\n"
                f"• **Submission Closing Date:** {deadline_val}"
            )
            who_is_it_for = (
                f"Registered Government Contractors and Vendors"
                if lang == "en" else "पंजीकृत ठेकेदार, आपूर्तिकर्ता एवं अधिकृत वेंडर"
            )
            if entities["contractor_categories"]:
                who_is_it_for += f" ({', '.join(entities['contractor_categories'])})"

            action_steps = [
                "1. Download complete Tender Document and Bill of Quantities (BOQ) from the official portal." if lang == "en" else "1. आधिकारिक पोर्टल से पूर्ण निविदा दस्तावेज एवं बीओक्यू (BOQ) एक्सेल शीट डाउनलोड करें।",
                "2. Ensure active Class-3 Digital Signature Certificate (DSC) and contractor enlistment." if lang == "en" else "2. सुनिश्चित करें कि आपका क्लास-3 डिजिटल सिग्नेचर (DSC) सक्रिय एवं पोर्टल पर मैप है।",
                "3. Deposit the required EMD or upload valid MSME/Udyam exemption certificate." if lang == "en" else "3. निर्धारित धरोहर राशि (EMD) ऑनलाइन जमा करें अथवा वैध एमएसएमई छूट प्रमाण पत्र संलग्न करें।",
                "4. Upload Technical Packet and Financial Bid before the closing deadline." if lang == "en" else "4. निर्धारित अंतिम समयसीमा से पहले तकनीकी दस्तावेज व वित्तीय बोली पोर्टल पर अपलोड करें।"
            ]
            key_benefits_str = f"Estimated Contract Budget: {tender_val_str} | EMD: {entities['emd_or_grant']}"

        elif doc_category == "newspaper":
            doc_type_label = t("doc_type_newspaper", lang)
            official_url = "https://india.gov.in"
            portal_name = "National Portal of India & Concerned State Gazette"
            
            meaning_text = (
                f"{tpl['meaning']}\n\n"
                f"• **Published By:** {authority_name}\n"
                f"• **Notice Reference / Order No:** {ref_no_str}\n"
                f"• **Effective / Closing Timeline:** {deadline_val}\n"
                f"• **Public Announcement Summary:** The published circular informs citizens regarding official administrative guidelines, deadline extensions, or statutory public compliance."
            )
            who_is_it_for = (
                "General Public, Affected Residents & Beneficiary Citizens"
                if lang == "en" else "सर्वसाधारण नागरिक, संबंधित क्षेत्रवासी एवं लाभार्थी परिवार"
            )
            action_steps = [
                "1. Read the published circular terms carefully to verify if your family or property is affected." if lang == "en" else "1. समाचार पत्र विज्ञप्ति को ध्यानपूर्वक पढ़ें और देखें कि आपका क्षेत्र या परिवार इससे संबंधित है या नहीं।",
                "2. Prepare supporting identity proofs (Aadhaar, Land Records, Ration Card, Certificates)." if lang == "en" else "2. संबंधित आवश्यक पहचान पत्र एवं आवश्यक अभिलेख (आधार, खतौनी, प्रमाण पत्र) तैयार रखें।",
                "3. Contact the local district office, official helpline, or visit the official government website." if lang == "en" else "3. निकटतम जिला कार्यालय, संबंधित हेल्पलाइन अथवा आधिकारिक पोर्टल से विवरण प्राप्त करें।",
                "4. Beware of unauthorized intermediaries; verify all circular details on official .gov.in websites." if lang == "en" else "4. किसी भी अनाधिकृत बिचौलिए या अफवाह पर विश्वास न करें; आधिकारिक .gov.in वेबसाइट से पुष्टि करें।"
            ]
            key_benefits_str = f"Public Compliance & Administrative Directives (Deadline: {deadline_val})"

        elif doc_category == "job":
            doc_type_label = t("doc_type_job", lang)
            official_url = best_rag_match.get("official_portal", "https://ssc.gov.in") if best_rag_match else "https://ssc.gov.in"
            portal_name = best_rag_match.get("organization", authority_name) if best_rag_match else authority_name
            
            job_title = best_rag_match.get("title_en" if lang == "en" else "title_hi", "Government Recruitment") if best_rag_match else "Government Vacancy Notice"
            vacancies_info = best_rag_match.get("vacancies", "Refer to detailed notice") if best_rag_match else "As per vacancy roster"
            qual_req = ", ".join(entities["qualifications"]) if entities["qualifications"] else (best_rag_match.get("qualification_required", "10th / 12th / Graduate") if best_rag_match else "Prescribed Educational Qualification")

            meaning_text = (
                f"{tpl['meaning']}\n\n"
                f"• **Designation / Post:** {job_title}\n"
                f"• **Recruitment Body:** {authority_name}\n"
                f"• **Advertisement / Notice No:** {ref_no_str}\n"
                f"• **Minimum Qualification:** {qual_req}\n"
                f"• **Application Last Date:** {deadline_val}"
            )
            who_is_it_for = f"Job Seekers meeting {qual_req}" if lang == "en" else f"{qual_req} योग्यता रखने वाले सभी योग्य अभ्यर्थी"
            action_steps = [
                "1. Review minimum educational qualification, age limits, and category reservation criteria." if lang == "en" else "1. न्यूनतम शैक्षणिक योग्यता, आयु सीमा एवं वर्गवार आरक्षण नियमों की जांच करें।",
                "2. Complete One-Time Registration (OTR) on the official recruitment commission portal." if lang == "en" else "2. आधिकारिक भर्ती आयोग के पोर्टल पर वन-टाइम रजिस्ट्रेशन (OTR) पूर्ण करें।",
                "3. Upload scanned photograph and signature in accordance with official notification dimensions." if lang == "en" else "3. निर्धारित माप व आकार में अपना पासपोर्ट फोटो एवं हस्ताक्षर अपलोड करें।",
                "4. Submit online application fee and download final confirmation application receipt." if lang == "en" else "4. ऑनलाइन परीक्षा शुल्क जमा कर भरे हुए आवेदन पत्र की पावती सुरक्षित डाउनलोड करें।"
            ]
            key_benefits_str = f"Total Vacancies: {vacancies_info} | Educational Qualification: {qual_req}"

        elif doc_category == "scheme":
            doc_type_label = t("doc_type_scheme", lang)
            official_url = best_rag_match.get("application_url", "https://myscheme.gov.in") if best_rag_match else "https://myscheme.gov.in"
            portal_name = "myScheme Central Portal / Official State Welfare Portal"
            
            scheme_title = best_rag_match.get("title_en" if lang == "en" else "title_hi", "Government Welfare Scheme") if best_rag_match else "National Welfare Assistance Scheme"
            benefits_info = best_rag_match.get("benefits_en" if lang == "en" else "benefits_hi", ", ".join(entities["financial_amounts"]) if entities["financial_amounts"] else "Direct Financial Benefit Transfer & Subsidies") if best_rag_match else ("Direct Benefit Transfer & Subsidies" if lang == "en" else "प्रत्यक्ष वित्तीय लाभ एवं सरकारी अनुदान")

            meaning_text = (
                f"{tpl['meaning']}\n\n"
                f"• **Scheme Name:** {scheme_title}\n"
                f"• **Sponsoring Authority:** {authority_name}\n"
                f"• **Circular / Scheme Ref:** {ref_no_str}\n"
                f"• **Key Benefits:** {benefits_info}\n"
                f"• **Active Timeline:** {deadline_val}"
            )
            who_is_it_for = (
                "Eligible Citizens, Farmers, Women, Students & Economically Weaker Families"
                if lang == "en" else "पात्र किसान, महिलाएं, छात्र, मजदूर एवं आर्थिक रूप से कमजोर परिवार"
            )
            action_steps = [
                "1. Ensure bank account has active NPCI Aadhaar Seeding for Direct Benefit Transfer (DBT)." if lang == "en" else "1. सुनिश्चित करें कि आपका बैंक खाता एनपीसीआई आधार सीडिंग (DBT) से जुड़ा हुआ है।",
                "2. Complete mandatory biometric or mobile OTP e-KYC on the official scheme portal." if lang == "en" else "2. योजना के आधिकारिक पोर्टल अथवा सीएससी केंद्र पर जाकर ई-केवाईसी (e-KYC) पूर्ण करें।",
                "3. Keep income certificate, caste certificate, ration card, and bank passbook handy." if lang == "en" else "3. आय प्रमाण पत्र, जाति प्रमाण पत्र, राशन कार्ड एवं बैंक पासबुक तैयार रखें।",
                "4. Submit application online on myScheme.gov.in or at the nearest Common Service Centre (CSC)." if lang == "en" else "4. myScheme.gov.in पोर्टल अथवा नजदीकी जन सेवा केंद्र (CSC) से ऑनलाइन आवेदन करें।"
            ]
            key_benefits_str = f"Benefit Details: {benefits_info}"

        else: # general
            doc_type_label = t("doc_type_general", lang)
            official_url = "https://india.gov.in"
            portal_name = "National Portal of India"
            meaning_text = (
                f"{tpl['meaning']}\n\n"
                f"• **Issuing Authority:** {authority_name}\n"
                f"• **Order / Circular No:** {ref_no_str}\n"
                f"• **Timeline / Deadline:** {deadline_val}"
            )
            who_is_it_for = "Concerned Citizens, Institutions & Administrative Personnel" if lang == "en" else "संबंधित नागरिक, संस्थाएं एवं विभागीय अधिकारी"
            action_steps = [
                "1. Examine the circular directives and notes of compliance." if lang == "en" else "1. परिपत्र के मुख्य बिंदुओं एवं निर्देशों का अवलोकन करें।",
                "2. Visit the parent department website for official verification." if lang == "en" else "2. आधिकारिक सत्यापन के लिए संबंधित विभाग की वेबसाइट देखें।",
                "3. Submit required representations or compliance within stated deadlines." if lang == "en" else "3. निर्धारित समयसीमा में अपनी रिपोर्ट या आवेदन प्रस्तुत करें।"
            ]
            key_benefits_str = f"Administrative Compliance & Statutory Guidelines"

        return {
            "success": True,
            "document_category": doc_category,
            "document_type": doc_type_label,
            "issuing_authority": authority_name,
            "reference_number": ref_no_str,
            "deadline": deadline_val,
            "what_it_means_first": meaning_text,
            "who_is_it_for": who_is_it_for,
            "key_benefits": key_benefits_str,
            "action_steps": action_steps,
            "safety_guidance": tpl["safety"],
            "official_url": official_url,
            "official_portal_name": portal_name,
            "extracted_entities": entities,
            "matched_scheme": best_rag_match if doc_category == "scheme" else None,
            "matched_job": best_rag_match if doc_category == "job" else None,
            "top_scheme_matches": scheme_matches,
            "top_job_matches": job_matches
        }
