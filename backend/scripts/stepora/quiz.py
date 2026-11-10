"""
The 'Find my path' quiz: (question_en, question_te, weight, [(option_en, option_te, course slugs)]).

Each chosen option adds the question's weight to its courses. Interests weigh more than
practical limits, and each course has an option that points to it above its neighbours. The student's Intermediate group is
asked first and is a hard filter, so options can safely list courses from every group.
"""

_BTECH = ["btech-cse", "btech-ece", "btech-mech", "btech-civil", "btech-eee"]

INTEREST = 3
PRACTICAL = 1

QUIZ = [
    ("Which subject do you enjoy most?", "మీకు ఏ సబ్జెక్ట్ అంటే ఎక్కువ ఇష్టం?", INTEREST, [
        ("Maths and solving problems", "మ్యాథ్స్, సమస్యలను పరిష్కరించడం", _BTECH + ["bsc-cs", "ca"]),
        ("Computers and coding", "కంప్యూటర్లు, కోడింగ్", ["btech-cse", "bca", "bsc-cs"]),
        ("Electronics and gadgets", "ఎలక్ట్రానిక్స్, గాడ్జెట్లు", ["btech-ece", "btech-eee"]),
        ("Machines and how things move", "యంత్రాలు, వస్తువులు ఎలా కదులుతాయి", ["btech-mech", "btech-civil", "cpl"]),
        ("Drawing, art and design", "డ్రాయింగ్, ఆర్ట్, డిజైన్", ["b-des", "b-arch", "bfa"]),
        ("Biology and the human body", "బయాలజీ, మానవ శరీరం", ["mbbs", "bsc-nursing", "bpt", "bsc-mlt", "bvsc", "bpharm", "bsc-agri", "bs-ms"]),
        ("Accounts, business and economics", "అకౌంట్స్, వ్యాపారం, ఎకనామిక్స్", ["bcom", "bba", "ca", "cs", "cma"]),
        ("History, society and languages", "చరిత్ర, సమాజం, భాషలు", ["ba", "ba-llb", "bsw"]),
    ]),
    ("What kind of work sounds exciting to you?", "ఏ రకమైన పని మీకు ఆసక్తిగా అనిపిస్తుంది?", INTEREST, [
        ("Building apps and websites", "యాప్‌లు, వెబ్‌సైట్లు తయారు చేయడం", ["btech-cse", "bca", "btech-it"]),
        ("Artificial intelligence and machine learning", "కృత్రిమ మేధస్సు, మెషిన్ లెర్నింగ్", ["btech-aiml", "btech-ai-ds"]),
        ("Protecting systems from hackers", "హ్యాకర్ల నుండి వ్యవస్థలను కాపాడటం", ["btech-cse-cyber"]),
        ("Finding patterns in data", "డేటాలో నమూనాలు కనుగొనడం", ["btech-cse-ds"]),
        ("Running computer systems and networks", "కంప్యూటర్ వ్యవస్థలు, నెట్‌వర్క్‌లు నడపడం", ["btech-it"]),
        ("Designing electronics and chips", "ఎలక్ట్రానిక్స్, చిప్స్ డిజైన్ చేయడం", ["btech-ece"]),
        # One clear answer for each newer B.Tech branch, added on 10 November 2026 (English only)
        ("Making computers think and decide on their own", "", ["btech-ai"]),
        ("Software for businesses and banks", "", ["btech-csbs"]),
        ("Designing apps that people enjoy using", "", ["btech-cs-design"]),
        ("Smart devices that talk to the internet", "", ["btech-cse-iot"]),
        ("Measuring and controlling machines in factories", "", ["btech-eie"]),
        ("Building robots", "", ["btech-robotics"]),
        ("Cars, bikes and electric vehicles", "", ["btech-automobile"]),
        ("Aircraft and how they fly", "", ["btech-aeronautical"]),
        ("Chemicals, plants and how products are made", "", ["btech-chemical"]),
        ("Designing and building machines", "యంత్రాలు డిజైన్ చేసి నిర్మించడం", ["btech-mech", "btech-civil", "btech-eee"]),
        ("Working with data, science and research", "డేటా, సైన్స్, రీసెర్చ్‌తో పనిచేయడం", ["bsc-cs", "btech-cse", "bs-ms"]),
        ("Treating and caring for patients", "రోగులకు చికిత్స, సేవ చేయడం", ["mbbs", "bsc-nursing", "bpt", "bnys", "bsc-allied"]),
        ("Ayurveda, homeopathy and traditional medicine", "ఆయుర్వేదం, హోమియోపతి, సంప్రదాయ వైద్యం", ["bams", "bhms", "bums"]),
        ("Teeth and dental care", "దంతాలు, దంత సంరక్షణ", ["bds"]),
        ("Working with medicines", "మందులతో పనిచేయడం", ["bpharm", "pharm-d"]),
        ("Farming, food and the land", "వ్యవసాయం, ఆహారం, భూమి", ["bsc-agri", "bsc-horti", "bvsc", "bfsc"]),
        ("Handling accounts, tax and money", "అకౌంట్స్, టాక్స్, డబ్బు వ్యవహారాలు చూడటం", ["bcom", "ca", "cma"]),
        ("Advising companies on law and rules", "చట్టం, నియమాలపై కంపెనీలకు సలహా ఇవ్వడం", ["cs"]),
        ("Leading people and running a business", "మనుషులను నడిపించడం, వ్యాపారం నిర్వహించడం", ["bba"]),
        ("Working in government or public service", "ప్రభుత్వం లేదా ప్రజా సేవలో పనిచేయడం", ["ba", "ssc-chsl"]),
        ("Serving in the armed forces", "సాయుధ దళాల్లో సేవ చేయడం", ["nda"]),
        ("Flying aircraft", "విమానాలు నడపడం", ["cpl"]),
        ("Designing buildings and spaces", "భవనాలు, స్థలాలు డిజైన్ చేయడం", ["b-arch"]),
        ("Creating products, fashion or digital designs", "ఉత్పత్తులు, ఫ్యాషన్ లేదా డిజిటల్ డిజైన్లు సృష్టించడం", ["b-des"]),
        ("Hotels, food and looking after guests", "హోటళ్ళు, ఆహారం, అతిథులను చూసుకోవడం", ["bsc-hha"]),
        ("Learning a trade and starting work early", "ఒక వృత్తి నేర్చుకుని త్వరగా పని ప్రారంభించడం", ["b-voc", "ssc-chsl", "dped"]),
        ("Law, courts and justice", "చట్టం, కోర్టులు, న్యాయం", ["ba-llb"]),
    ]),
    ("How many years would you like to study for your first qualification?", "మీ మొదటి అర్హత కోసం ఎన్ని సంవత్సరాలు చదవాలనుకుంటున్నారు?", PRACTICAL, [
        ("3 years, so I can start working or study further sooner", "3 సంవత్సరాలు, త్వరగా ఉద్యోగం లేదా ఉన్నత చదువులు ప్రారంభించడానికి", ["bca", "bsc-cs", "bcom", "bba", "ba", "bsc-hha", "b-voc"]),
        ("4 years is fine for a professional degree", "ప్రొఫెషనల్ డిగ్రీ కోసం 4 సంవత్సరాలు పర్వాలేదు", _BTECH + ["bpharm", "bsc-nursing", "bsc-agri", "b-des"]),
        ("5 years or more is fine if the goal is worth it", "లక్ష్యం విలువైనదైతే 5 సంవత్సరాలు లేదా ఎక్కువైనా పర్వాలేదు", ["mbbs", "ba-llb", "ca", "b-arch", "bs-ms"]),
    ]),
    ("Are you ready to prepare for a big entrance exam (like AP EAPCET, NEET or CLAT)?", "పెద్ద ప్రవేశ పరీక్ష (AP EAPCET, NEET లేదా CLAT వంటివి) కోసం సిద్ధం కావడానికి మీరు రెడీగా ఉన్నారా?", PRACTICAL, [
        ("Yes, I am ready for an entrance exam", "అవును, ప్రవేశ పరీక్షకు నేను సిద్ధంగా ఉన్నాను", _BTECH + ["mbbs", "bsc-nursing", "bpharm", "bsc-agri", "ba-llb", "ca", "b-arch", "b-des", "bs-ms", "bsc-hha", "nda", "cs", "ssc-chsl"]),
        ("I prefer admission without a big entrance exam", "పెద్ద ప్రవేశ పరీక్ష లేకుండా అడ్మిషన్ కావాలి", ["bca", "bsc-cs", "bcom", "bba", "ba", "b-voc", "cma"]),
    ]),
    ("What matters more for your family right now?", "ప్రస్తుతం మీ కుటుంబానికి ఏది ఎక్కువ ముఖ్యం?", PRACTICAL, [
        ("Lower fees", "తక్కువ ఫీజు", ["bca", "bsc-cs", "bcom", "ba", "ca"]),
        ("We can manage professional course fees (or scholarships/reimbursement)", "ప్రొఫెషనల్ కోర్సు ఫీజు మేనేజ్ చేయగలం (లేదా స్కాలర్‌షిప్/రీయింబర్స్‌మెంట్)", _BTECH + ["mbbs", "bsc-nursing", "bpharm", "bsc-agri", "bba", "ba-llb", "b-arch", "b-des", "bs-ms", "bsc-hha", "cpl"]),
    ]),
    ("How do you like to learn?", "మీరు ఎలా నేర్చుకోవడానికి ఇష్టపడతారు?", PRACTICAL, [
        ("By building projects", "ప్రాజెక్ట్‌లు నిర్మిస్తూ", ["btech-cse", "btech-ece", "btech-mech", "bca", "b-arch", "b-des"]),
        ("By hands-on work in labs, hospitals or fields", "ల్యాబ్‌లు, ఆసుపత్రులు లేదా పొలాల్లో ప్రత్యక్షంగా పనిచేస్తూ", ["btech-ece", "mbbs", "bsc-nursing", "bpharm", "bsc-agri", "b-voc", "bsc-hha", "nda", "cpl"]),
        ("By reading and understanding ideas deeply", "చదివి, ఆలోచనలను లోతుగా అర్థం చేసుకుంటూ", ["bsc-cs", "ba", "ba-llb", "bs-ms", "ssc-chsl"]),
        ("By working with numbers and real business cases", "సంఖ్యలు, నిజమైన వ్యాపార ఉదాహరణలతో పనిచేస్తూ", ["bcom", "bba", "ca", "cs", "cma"]),
    ]),
]
