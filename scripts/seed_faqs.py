import sys
import os
from datetime import datetime

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dotenv import load_dotenv
from services.mongodb_service import MongoDBService
from utils.embeddings import initialize_embedding_model, generate_batch_embeddings

# Load environment variables
load_dotenv()

MONGODB_URL = os.getenv("MONGODB_URL", "mongodb://localhost:27017/")
EMBEDDING_MODEL_NAME = os.getenv("EMBEDDING_MODEL_NAME", "all-mpnet-base-v2")

# ============================================================
# SAMPLE FAQ DATA
# ============================================================
SAMPLE_FAQS = [
    {
        "question": "What is VITEEE?",
        "answer": "VITEEE stands for Vellore Institute of Technology Engineering Entrance Examination, which is the entrance test for admission to B.Tech programs at all VIT campuses.",
        "category": "General"
    },
    {
        "question": "How many categories of fees are there at VIT?",
        "answer": "VIT has five categories (Category 1 to Category 5) with varying tuition fees. Category 1 has the lowest fees and highest merit requirement.",
        "category": "Admissions"
    },
    {
        "question": "What is the exam pattern of VITEEE?",
        "answer": "The exam has 125 questions divided into Physics, Chemistry, Mathematics or Biology, English, and Aptitude sections. Each question carries one mark and there is no negative marking.",
        "category": "Exam Pattern"
    },
    {
        "question": "Is there any negative marking in VITEEE?",
        "answer": "Yes, there is negative marking in the VITEEE examination. It will be implemented from 2026 onwards. Earlier there used to be no negative marking.",
        "category": "Exam Pattern"
    },
    {
        "question": "When does VITEEE usually take place?",
        "answer": "VITEEE is typically conducted in April every year, and the application process usually begins in November of the previous year.",
        "category": "Timeline"
    },
    {
        "question": "Can I change my campus after admission?",
        "answer": "No, inter-campus transfers are not allowed once admission has been confirmed at a specific VIT campus.",
        "category": "Policies"
    },
    {
        "question": "How are seats allotted in VIT?",
        "answer": "Seat allotment is based on your VITEEE rank and the availability of seats in your preferred branch and campus during the counselling process.",
        "category": "Counselling"
    },
    {
        "question": "Does VIT offer AI and Data Science programs?",
        "answer": "Yes, VIT offers B.Tech programs in Artificial Intelligence, AI & Data Science, and AI & Robotics across multiple campuses.",
        "category": "Programs"
    },
    {
        "question": "What is Vellore Institute of Technology (VIT)?",
        "answer": "VIT (Vellore Institute of Technology) is a private deemed-to-be university in India, founded in 1984 by Dr. G. Viswanathan, and has multiple campuses (Vellore, Chennai, VIT-AP, VIT-Bhopal, and newer ones in Bangalore and Mauritius under development).",
        "category": "General"
    },
    {
        "question": "Which campuses does VIT have?",
        "answer": "VIT currently has four fully operational campuses: Vellore (Tamil Nadu), Chennai (Tamil Nadu), VIT-AP (Andhra Pradesh) and VIT-Bhopal (Madhya Pradesh). Additionally, two new campuses are in early-stage development (Bangalore and Mauritius), which are not yet admitting undergraduate students.",
        "category": "General"
    },
    {
        "question": "What accreditations and rankings does VIT hold?",
        "answer": "VIT is accredited by NAAC with ‘A++’ and has NBA-accredited programmes. According to QS and NIRF, VIT is among India’s top private universities (e.g., NIRF 2024 placed VIT 19th overall, 10th among universities, 11th among engineering). :contentReference[oaicite:1]{index=1}",
        "category": "General"
    },
    {
        "question": "What is the Fully Flexible Credit System (FFCS) at VIT?",
        "answer": "VIT follows the Fully Flexible Credit System (FFCS) which lets students choose their subjects (electives/minors), semester schedule (within bounds), and sometimes class timings, giving more flexibility in academics. :contentReference[oaicite:2]{index=2}",
        "category": "Academics"
    },
    {
        "question": "What undergraduate programmes are offered by VIT?",
        "answer": "VIT offers B.Tech programmes in traditional branches (Mechanical, Electrical, Civil, Electronics) as well as modern fields such as Artificial Intelligence, AI & Data Science, AI & Robotics, CSE, etc across its campuses.",
        "category": "Programs"
    },
    {
        "question": "What is the eligibility criterion for the VITEEE (VIT Engineering Entrance Examination)?",
        "answer": "To be eligible for VITEEE, a candidate must have passed 10 + 2 (or equivalent) with a minimum of ~60% in aggregate in Physics, Chemistry and Mathematics/Biology, though eligibility may vary by category and campus.",
        "category": "Admissions"
    },
    {
        "question": "How many fee-categories does VIT use for undergraduate admission and what do they mean?",
        "answer": "VIT uses five fee categories (Category 1 to Category 5) for undergraduate admissions. Category 1 is the lowest fee (highest merit) and subsequent categories reflect lower merit or gap years. Fees vary accordingly.",
        "category": "Admissions"
    },
    {
        "question": "What is the approximate tuition fee structure for B.Tech at VIT across campuses?",
        "answer": "For Indian category undergraduate students, tuition fees approximate: Category 1 ~ ₹1.2 lakh/year, Category 2 ~ ₹1.9 lakh/year, Category 3 ~ ₹2.3 lakh/year, Category 4 ~ ₹2.75 lakh/year, Category 5 ~ ₹2.95 lakh/year (varies by campus and year).",
        "category": "Fees"
    },
    {
        "question": "What is the hostel + mess fee structure for first-year students at VIT Vellore (men)?",
        "answer": "For first-year male students at VIT Vellore (Indian category) in 2024-25: e.g., 6NAC+Veg Mess: ~₹1,33,700; 6AC+Special Mess: ~₹1,76,400. Fees vary by room type + mess type. You need to check official sheet for current year. (Figures from hostel information sheet) ",
        "category": "Fees"
    },
    {
        "question": "Is laundry included in the hostel fees at VIT Vellore?",
        "answer": "Yes — laundry service (the so-called 'Chota Dhobi' free laundry) is included in the hostel fees at VIT Vellore for hostel students. ",
        "category": "Fees"
    },
    {
        "question": "What is the exam pattern of VITEEE?",
        "answer": "The VITEEE exam consists of 125 questions from Physics, Chemistry, Mathematics/Biology, English, and Aptitude. Each question carries one mark. Negative marking is introduced from 2026 onwards. :contentReference[oaicite:3]{index=3}",
        "category": "Exam Pattern"
    },
    {
        "question": "When is VITEEE usually held and when does application begin?",
        "answer": "Typically, VITEEE is held in April every year. The application window usually opens in November of the previous year. Students are advised to check the official site for exact dates. :contentReference[oaicite:4]{index=4}",
        "category": "Timeline"
    },
    {
        "question": "How are seats allotted at VIT after VITEEE?",
        "answer": "Seat allotment is based on VITEEE rank, candidate’s fee category, campus + branch choices, availability of seats and counselling rounds. Students select choices online during counselling and seats are allotted in phases.",
        "category": "Counselling"
    },
    {
        "question": "Are inter-campus transfers allowed after admission at VIT?",
        "answer": "Once admission is confirmed at a specific campus and branch, transfers to another campus are generally **not** allowed under normal policy at VIT.",
        "category": "Policies"
    },
    {
        "question": "What is the minimum attendance required at VIT for end-semester exams?",
        "answer": "At VIT the minimum attendance requirement is 75% in each semester for students to be eligible for end-semester examinations. :contentReference[oaicite:5]{index=5}",
        "category": "Academics"
    },
    {
        "question": "What is the mobile phone policy inside class at VIT?",
        "answer": "Mobile phone use in class at VIT depends on the individual professor — some allow use for notes/references, others may restrict phones during class to avoid distractions.",
        "category": "Policies"
    },
    {
        "question": "What kinds of hostel rooms are available at VIT Vellore?",
        "answer": "At VIT Vellore there are AC and Non-AC shared rooms (2-bed, 3-bed, 4-bed, 6-bed), deluxe options, and apartment-style hostel blocks (‘R’ block) with lounge and attached bathrooms. Students choose room/mess combinations when applying. :contentReference[oaicite:6]{index=6}",
        "category": "Campus Life"
    },
    {
        "question": "What mess food options are there in VIT hostels?",
        "answer": "In VIT hostels there are vegetarian mess, non-vegetarian mess, and special mess (premium menu) options. Students may change mess monthly, but downgrades do not usually result in refund of paid mess fee.",
        "category": "Campus Life"
    },
    {
        "question": "What is the laundry service facility in hostel at VIT?",
        "answer": "The hostel provides a laundry service (‘Chota Dhobi’) included in hostel fee; students get a specified number of washes per year (for example 44 washes). Additional wash counts beyond limit may incur charges. (As per hostel rules) ",
        "category": "Campus Life"
    },
    {
        "question": "What are the night-time library access and activity rules at VIT?",
        "answer": "At VIT Vellore, the night library stays open till around 12:30 AM. If students go out after 9 PM for campus activities (until about 11 PM), they must obtain a ‘night slip’ from hostel/activities office to maintain security and tracking.",
        "category": "Campus Life"
    },
    {
        "question": "What are some of the major student clubs and technical chapters at VIT?",
        "answer": "VIT hosts numerous clubs and chapters in domains like robotics, coding, entrepreneurship, cultural arts, music, dance, theatre, sports, aero/automobile, hackathons, start-ups. Top clubs include VIT Robotics Club, E-Cell (Entrepreneurship Cell), Aero & Automobile Society, Music & Cultural Club, Sports Club etc.",
        "category": "Campus Life"
    },
    {
        "question": "How are student cultural festivals at VIT organised?",
        "answer": "At VIT Vellore, the flagship cultural-sports fest is “Riviera” — 4-day event with thousands of participants, pro-shows, competitions, sports and cultural events. :contentReference[oaicite:7]{index=7} Similar fests exist at other campuses under different names.",
        "category": "Campus Life"
    },
    {
        "question": "What is the placement performance at VIT Vellore in recent years?",
        "answer": "For VIT Vellore (2024 batch): highest package ~₹88 LPA, average ~₹9.9 LPA, ~867 recruiters visited, ~7,526 students placed. These are approximate figures and change year to year. :contentReference[oaicite:8]{index=8}",
        "category": "Placements"
    },
    {
        "question": "Which big companies recruit from VIT?",
        "answer": "Prominent recruiters at VIT include Microsoft, Amazon, Google, TCS, Cognizant, Infosys, Deloitte, PayPal, Nvidia, Qualcomm among many others. These companies participate in the on-campus placement drives. :contentReference[oaicite:9]{index=9}",
        "category": "Placements"
    },
    {
        "question": "What international student exchange or semester abroad programs are available at VIT?",
        "answer": "VIT has MoUs and partnerships with international universities for student exchange programmes, semester abroad options, research collaborations and internships overseas. Such opportunities are available for eligible students. :contentReference[oaicite:10]{index=10}",
        "category": "Research & International"
    },
    {
        "question": "What campus facilities does VIT provide?",
        "answer": "Facilities at VIT include modern labs, high-speed Wi-Fi across campus, large library (including night access), sports complex (indoor/outdoor), paid gym (e.g., at Vellore: Fitty, Indoor Gym, Trendset for boys), mini-hospital (Narayani Hospital & Research Centre) open 24/7, free ambulance service to the hospital and to CMC Vellore in emergencies, paid bus transport, hostel amenities, guest houses and guest accommodation. :contentReference[oaicite:11]{index=11}",
        "category": "Facilities"
    },
    {
        "question": "Does VIT have medical facilities on campus?",
        "answer": "Yes — At VIT Vellore, there is the on-campus Narayani Hospital & Research Centre which operates 24/7 with visiting specialists at scheduled times, and provides free ambulance service from hostel blocks and to Christian Medical College (CMC) Vellore in serious cases.",
        "category": "Facilities"
    },
    {
        "question": "What is the alumni network like at VIT?",
        "answer": "VIT has a large, active alumni network across India and abroad, engaging in industry, academia and entrepreneurship. The alumni cell organises events, mentoring programmes and networking opportunities for current students.",
        "category": "Miscellaneous"
    },
    {
        "question": "When is the academic calendar for VIT released?",
        "answer": "The academic calendar — containing semester start dates, registration, mid-sem exam dates and end-sem exam dates — is typically released about 2-3 months before the semester begins. VIT follows Fall and Winter semesters under its FFCS system.",
        "category": "Timeline"
    },
    {
        "question": "What transport options are available for students at VIT?",
        "answer": "VIT offers paid bus services for students from nearby towns/cities to the campus. Routes, schedules and fares are published each semester by the transport office for each campus.",
        "category": "Facilities"
    },
    {
        "question": "What happens if a student fails to meet the attendance requirement at VIT?",
        "answer": "If a student’s attendance falls below the required 75% in a semester, they may be declared ineligible to appear for end-semester examination or may have to repeat the semester as per VIT’s academic regulations and Student Code of Conduct. :contentReference[oaicite:12]{index=12}",
        "category": "Policies"
    },
    {
        "question": "What is the Student Code of Conduct at VIT?",
        "answer": "VIT has a Student Code of Conduct which outlines expected behaviours relating to academics, campus life, hostels, discipline, attendance, dress code, mobile usage, anti-ragging etc. Students are required to adhere to it throughout their stay.",
        "category": "Policies"
    },
    {
        "question": "Can students bring their own vehicle to VIT campus and hostels?",
        "answer": "Yes — Students may bring their vehicles (two-wheelers) to the campus subject to registration with the transport office, payment of parking/permit charges and compliance with safety rules. (Check campus-specific rules) ",
        "category": "Campus Life"
    },
    {
        "question": "Are students required to stay in hostels at VIT in the first year?",
        "answer": "At most VIT campuses, first-year undergraduate students (especially those from outside the city/state) are required to take hostel accommodation. Local students sometimes may be exempt but must check campus policy.",
        "category": "Campus Life"
    },
    {
        "question": "Does VIT have a dress code for hostels and campus events?",
        "answer": "While VIT has a liberal dress code on campus, students are expected to dress appropriately in common areas and comply with the guidelines under the Student Code of Conduct. Hostels may have specific rules for night-outs, visitors, and curfew. ",
        "category": "Campus Life"
    },
    {
        "question": "What is the student to faculty ratio at VIT?",
        "answer": "VIT publishes that it has a large number of faculty across its campuses and aims for a good student-faculty ratio, but the exact value varies by campus and programme. For latest ratio, refer to the annual mandatory disclosure on the VIT website. :contentReference[oaicite:13]{index=13}",
        "category": "Academics"
    },
    {
        "question": "Does VIT allow back-log clearance and how is it managed?",
        "answer": "Yes — under FFCS, students who fail a course may re-register in a later semester or in special weeks/sessions. VIT allows summer or weekend semesters for backlog clearance. Grades ‘F’ or ‘N’ have specified re-registration rules. :contentReference[oaicite:14]{index=14}",
        "category": "Academics"
    },
    {
        "question": "What is the minimum age or attempt criteria for VITEEE?",
        "answer": "There is no formal fixed number of attempts for VITEEE; candidates can appear as many times as they qualify the eligibility criteria. For VITEEE 2026, the candidate should be born on or after July 1, 2004. :contentReference[oaicite:15]{index=15}",
        "category": "Admissions"
    },
    {
        "question": "What is the process for PhD admissions at VIT (VITREE)?",
        "answer": "VIT conducts the VIT Research Entrance Examination (VITREE) for admission to full-time/part-time PhD programmes across campuses. The examination has MCQs on technical subjects, communication skills, and for external part-time candidates. :contentReference[oaicite:16]{index=16}",
        "category": "Admissions"
    },
    {
        "question": "Are scholarships available at VIT and who is eligible?",
        "answer": "Yes — VIT offers merit-based scholarships (for top ranks, board toppers), need-based grants, sports quotas, rural student support (STARS scheme) and special awards for research/internships abroad. :contentReference[oaicite:17]{index=17}",
        "category": "Fees"
    },
    {
        "question": "Can students change their mess or hostel room type mid-year at VIT?",
        "answer": "Yes — within policy, students may upgrade mess/hostel room categories (e.g., Non-Veg to Special Mess) by paying differential fee. Downgrades generally do not result in refund. Monthly changes in mess options may be allowed. ",
        "category": "Campus Life"
    },
    {
        "question": "What is the minimum duration of the B.Tech programme at VIT and is there an honours/dual degree option?",
        "answer": "The standard B.Tech programme at VIT is 4 years (8 semesters). Additionally, honours/minor/dual-degree options may extend beyond the typical duration, allowing specialisation or integrated masters (depending on programme and campus).",
        "category": "Programs"
    },
    {
        "question": "How often does VIT change or update its fee structure and categories?",
        "answer": "VIT typically revises the fee structure and categories annually, based on campus, inflation, programmes etc. Students should refer to the official fee-structure published each admission cycle for accurate values.",
        "category": "Fees"
    },
    {
        "question": "What is the guest-house facility at VIT for visiting parents/guests?",
        "answer": "VIT Vellore has guest-house facilities with rooms (Executive A/C & Premium A/C) for visitors. Booking should be made at least 1 week in advance and meals can be arranged via the guest-house office. :contentReference[oaicite:18]{index=18}",
        "category": "Facilities"
    },
    {
        "question": "What is the process for branch change or specialization switch during the course at VIT?",
        "answer": "At VIT, branch change is possible (depending on availability) after the second semester or as per campus policy, but eligibility criteria such as CGPA threshold (for example >9.0) may apply. Students should check the latest rules for the relevant campus.",
        "category": "Academics"
    },
    {
        "question": "Does VIT offer weekend or online courses or part-time programmes?",
        "answer": "Yes — VIT offers part-time/external programmes in research (PhD) and some continuing education courses; however regular B.Tech programmes are full-time. Weekend/online options depend on campus and programme. :contentReference[oaicite:19]{index=19}",
        "category": "Programs"
    },
    {
        "question": "What is the timeline for counselling and seat allotment at VIT?",
        "answer": "After VITEEE results are declared (usually May), VIT conducts counselling rounds starting in June where candidates fill choices, seats are allotted in phases and students have to confirm admission by paying fee and reporting to campus. Dates vary by year. :contentReference[oaicite:20]{index=20}",
        "category": "Counselling"
    },
    {
        "question": "What IDs and documents are required for admission and hostel at VIT?",
        "answer": "For admission to VIT and hostel registration, students must submit 10th/12th mark sheets, category certificate (if applicable), VITEEE scorecard, passport-size photos, identity proof (Aadhar/Passport), and in hostel cases, medical form and parental consent. Always check the current admission brochure for details.",
        "category": "Admissions"
    },
    {
        "question": "Are students allowed to go out of campus in evenings at VIT Vellore?",
        "answer": "At VIT Vellore, students can go out for campus activities until around 11 pm with a night slip. Exiting the campus after curfew or without permission may lead to disciplinary action. Local city visits may require permission based on hostel rules.",
        "category": "Campus Life"
    },
    {
        "question": "Does VIT accept scores from other entrance exams like JEE Main for B.Tech admission?",
        "answer": "No — for B.Tech admission via VITEEE, VIT currently does *not* accept JEE Main scores for domestic candidates at most campuses. Foreign/NRI quotas may have alternate criteria. :contentReference[oaicite:21]{index=21}",
        "category": "Admissions"
    },
    {
        "question": "How many seats are available at each campus of VIT for B.Tech annually?",
        "answer": "The number of seats varies each year and by campus & programme; for example, VIT Vellore may allocate several thousand seats for B.Tech across disciplines. Check the official “Intake” table for the current year per campus and branch.",
        "category": "Admissions"
    },
    {
        "question": "Is there any minimum CGPA requirement for students to continue at VIT?",
        "answer": "Yes — students may be required to maintain a minimum CGPA (for example >4.0 or as specified) to progress. If CGPA falls below the threshold, they may have to reduce credit load or could face academic warning/suspension. :contentReference[oaicite:22]{index=22}",
        "category": "Academics"
    },
    {
        "question": "Does VIT allow drop of a subject after registration (Add/Drop) and what are the rules?",
        "answer": "Yes — at VIT, students can usually add or drop subjects within the first few instructional days of a semester (for full semester courses) under FFCS. Withdrawal from courses mid-semester may lead to a ‘W’ grade and may not impact CGPA. :contentReference[oaicite:23]{index=23}",
        "category": "Academics"
    },
    {
        "question": "How is attendance tracked for students at VIT?",
        "answer": "Attendance at VIT is tracked per subject and overall; students must maintain at least 75% attendance in each subject/semester. Biometric/ID-card scanning or class registers are used depending on campus policy.",
        "category": "Policies"
    },
    {
        "question": "What is the refund policy if a student withdraws admission from VIT after paying fees?",
        "answer": "The refund policy varies by campus and year; generally if a student withdraws before a specified date, a portion of the fee may be refunded after deduction of processing charges. It's advisable to check the official admission brochure for the year.",
        "category": "Policies"
    },
    {
        "question": "Is there a dress code for pro-shows, cultural events and hostel common areas at VIT?",
        "answer": "Yes — while everyday dress is liberal on campus, for pro-shows, guest events and hostel common areas there may be guidelines (e.g., no offensive slogans, no swimwear in common spaces, etc.). Students should follow instructions given by club/event organisers and hostel wardens.",
        "category": "Campus Life"
    },
    {
        "question": "What is the procedure if a student wants to access counselling or mental-health services at VIT?",
        "answer": "VIT campuses have counselling & wellness centres. Students may book sessions with trained counsellors for emotional/academic issues. Contact details are available on the campus website under “Counselling Division”. :contentReference[oaicite:24]{index=24}",
        "category": "Facilities"
    },
    {
        "question": "What is the estimated average package for non-CSE students at VIT?",
        "answer": "Average package varies by branch. For non-CSE/IT branches the average may be lower than CSE; as per some sources the overall average across placements was ~₹8-10 LPA in recent years. Prospective students should check current placement reports.",
        "category": "Placements"
    },
    {
        "question": "Does VIT provide internship opportunities and industrial training to students?",
        "answer": "Yes — VIT through its Career Development Centre (CDC) and departmental partnerships helps students secure internships, industrial training, summer research projects, and international internship options. These often complement academic curriculum and improve employability.",
        "category": "Research & International"
    },
    {
        "question": "Are sports and outdoor facilities available at VIT campuses?",
        "answer": "Yes — VIT has extensive sports facilities such as cricket, football, basketball, badminton courts, swimming pool (some campuses), indoor gyms, athletics track, and annual sports meet events. Students may join teams/clubs and participate in inter-collegiate competitions.",
        "category": "Campus Life"
    },
    {
        "question": "How does VIT support entrepreneurship and start-ups among students?",
        "answer": "VIT has an Entrepreneurship Cell (E-Cell) and incubation facilities where students can work on start-ups, get mentorship, access seed funding/scholarships, use lab spaces, participate in hackathons and connect with alumni/start-up community.",
        "category": "Research & International"
    },
    {
        "question": "What is the frequency of hostel review committee meetings at VIT Vellore?",
        "answer": "At VIT Vellore hostels the hostel review committee meetings are conducted every 15 days by hostel administrators to address student queries, upkeep services and update on upgrades. :contentReference[oaicite:25]{index=25}",
        "category": "Campus Life"
    },
    {
        "question": "Are there any special facilities for differently-abled students at VIT?",
        "answer": "Yes — VIT provides support infrastructure for differently-abled students, including accessible hostel rooms, ramps, lifts, and counselling services. Students should contact the Admissions Office for specific facility details at the campus of interest.",
        "category": "Facilities"
    },
    {
        "question": "Is there a system for student feedback on faculty and courses at VIT?",
        "answer": "Yes — VIT regularly collects student feedback on courses, faculty and campus services via online portals or feedback forms. This feedback helps in academic improvement and quality assurance under the IQAC/quality cell.",
        "category": "Academics"
    },
    {
        "question": "Can VIT students avail semester abroad or exchange programmes?",
        "answer": "Yes — eligible students at VIT may apply for Semester Abroad Programmes (SAP) and exchange programmes with partner international universities under MoUs. Such programmes may require meeting CGPA, language and application deadlines. :contentReference[oaicite:26]{index=26}",
        "category": "Research & International"
    },
    {
        "question": "What is the procedure to register for clubs and chapters at VIT?",
        "answer": "Students typically register for clubs/chapters during orientation or within the first few weeks of semester, attend club-fair events, fill online membership forms and pay nominal fees (if any). Leadership roles are usually filled by elections or selection by club coordinators.",
        "category": "Campus Life"
    },
    {
        "question": "Does VIT publish a mandatory disclosure document and what does it contain?",
        "answer": "Yes — VIT publishes an ‘AICTE Mandatory Disclosure’ document for each campus detailing intake, faculty, student-faculty ratio, facilities, scholarship, hostel info etc. :contentReference[oaicite:27]{index=27}",
        "category": "General"
    },
    {
        "question": "Are part-time job or on-campus job opportunities available at VIT for students?",
        "answer": "Yes — Some campuses offer on-campus job opportunities (such as library assistance, lab assistance, tutoring) and part-time roles during semester breaks. Students should check bulletin boards or CDC postings for opportunities.",
        "category": "Campus Life"
    },
    {
        "question": "What is the duration of the summer/winter recess at VIT campuses?",
        "answer": "The exact recess duration varies by semester and campus, but typically VIT provides breaks after each semester (around 3-4 weeks) and may have short summer/winter vacations. The calendar is published ahead of time.",
        "category": "Timeline"
    },
    {
        "question": "Does VIT provide gym and fitness centre facilities? Are they free or paid?",
        "answer": "Yes — VIT Vellore (and some other campuses) provide gym/fitness centres (e.g., Fitty, Indoor Gym, Trendset) which are **paid** services for students. Membership terms and fees vary by centre. ",
        "category": "Campus Life"
    },
    {
        "question": "What is the dress code for internships and placements at VIT?",
        "answer": "For internships and placements at VIT, students are typically required to dress in formal corporate attire (shirt, tie, trousers for men; formal business attire for women) as per CDC guidelines. Failure to adhere may affect eligibility for interviews.",
        "category": "Placements"
    },
    {
        "question": "Do students have to attend orientation programmes when they join VIT?",
        "answer": "Yes — On joining, VIT conducts orientation programs for freshers (first-year students) at each campus to familiarise them with academic system, campus facilities, rules, clubs, hostel life and student welfare. Attendance is typically mandatory.",
        "category": "Admissions"
    },
    {
        "question": "Is ragging strictly prohibited at VIT? What are the anti-ragging measures?",
        "answer": "Yes — VIT has a zero-tolerance policy on ragging. Anti-ragging committees, helplines, CCTV, hostel wardens and disciplinary actions are in place. Students must comply with guidelines and report any incident immediately.",
        "category": "Policies"
    },
    {
        "question": "What scholarship is given to rural students under the STARS initiative at VIT?",
        "answer": "Under the STARS (Support for Talent Advancement and Retaining Students) initiative, rural students and students from under-privileged backgrounds may receive fee exemptions or reductions, support for projects abroad and other academic support. :contentReference[oaicite:28]{index=28}",
        "category": "Fees"
    },
    {
        "question": "How many hostel blocks and capacity does the VIT Vellore campus have?",
        "answer": "VIT Vellore campus has approximately 24 hostel blocks (18 for boys, rest for girls) and accommodates over 22,000 resident students annually. :contentReference[oaicite:29]{index=29}",
        "category": "Campus Life"
    },
    {
        "question": "What is the minimum CGPA required for honours/minor specialisation at VIT?",
        "answer": "To opt for honours/minor specialisation at VIT, students usually need to meet a minimum CGPA threshold (for example >8.0) and fulfil other prerequisites such as cumulative credits and departmental approval. Students should check the latest campus policy.",
        "category": "Programs"
    },
    {
        "question": "Does VIT provide mid-sem, end-sem and other exams schedule ahead of time?",
        "answer": "Yes — VIT publishes semester exam schedules (mid-sem, CAT-I, CAT-II, FAT/end-sem) ahead of time (usually in the academic calendar) so students can plan their study and project timelines accordingly.",
        "category": "Timeline"
    },
    {
        "question": "Are students allowed to keep pets/animals in hostels at VIT?",
        "answer": "No — Generally, pets/animals are not allowed in hostel rooms or campus residences at VIT unless specific permission is granted (e.g., service animals). Hostel rules should be checked for each campus.",
        "category": "Policies"
    },
    {
        "question": "Does VIT allow foreign nationals to apply and what are the criteria?",
        "answer": "Yes — VIT allows foreign nationals (and NRI students) to apply under a separate quota with distinct fee structure, admission criteria and seats. Students should refer to the campus-specific foreign admission brochure for details.",
        "category": "Admissions"
    },
    {
        "question": "What is the role of the Career Development Centre (CDC) at VIT?",
        "answer": "The CDC at VIT manages internships, placement drives, industry tie-ups, training programmes, career workshops, and tracks placement statistics. It acts as a bridge between students and recruiters.",
        "category": "Placements"
    },
    {
        "question": "Is drinking, smoking or consumption of tobacco allowed in campus or hostels at VIT?",
        "answer": "No — Consumption of alcohol, smoking, or any form of tobacco is strictly prohibited in VIT campus and hostels. Violation of rules may lead to disciplinary action under the Student Code of Conduct.",
        "category": "Policies"
    },
    {
        "question": "What is the procedure if a student wants to change to a higher fee-category at VIT (for example from Cat 3 to Cat 2)?",
        "answer": "If a student meets the higher category merit criteria (for example post board results or re-assessment) and the campus allows category upgration, they may apply for change. The fee difference will apply; however availability is subject to policy and is not guaranteed. ",
        "category": "Admissions"
    },
    {
        "question": "Does VIT have its own fleet of buses for daily commute or does it partner external transporters?",
        "answer": "VIT partners or operates its own paid bus service for students commuting from nearby towns and cities. The transport office publishes route maps, fare details and timings each semester. Some campuses may have shuttle services within campus.",
        "category": "Facilities"
    },
    {
        "question": "Can students apply for semester/weekend courses to clear backlogs at VIT?",
        "answer": "Yes — VIT offers summer or weekend sessions (depending on campus) where students can take additional/failed courses to clear backlogs and graduate on time. Students must register and pay applicable fees for these sessions. :contentReference[oaicite:30]{index=30}",
        "category": "Academics"
    },
    {
        "question": "What is the general climate at VIT Vellore campus and should students from different regions prepare accordingly?",
        "answer": "Vellore region typically has a hot tropical climate; summer months may be warm, monsoon season humid, winters mild. Students from cooler regions may consider bringing light jackets and check hostel amenities (AC/Non-AC).",
        "category": "Campus Life"
    },
    {
        "question": "How is the mess hygiene and food quality at VIT hostels?",
        "answer": "Hostel mess at VIT undergoes regular inspections, student feedback is collected via the hostel review committee (every ~15 days) and suggestions for improvement are accommodated. Students may rate food quality and cleanliness. :contentReference[oaicite:31]{index=31}",
        "category": "Campus Life"
    },
    {
        "question": "Can a student fail and repeat a semester at VIT? What is the procedure?",
        "answer": "Yes — If a student fails to meet CGPA/credit requirements or attendance thresholds, they may be required to repeat a semester or register for backlog courses. Repeating may incur additional fees and delay graduation.",
        "category": "Academics"
    },
    {
        "question": "Are there medical insurance or health-care facilities included in hostel fees at VIT?",
        "answer": "Yes — Health-care facilities (first-aid, medical centre, on-campus hospital in Vellore) are available. Some campuses may include basic medical cover or tie-ups, but students are advised to check additional insurance requirements or coverage for serious cases.",
        "category": "Facilities"
    },
    {
        "question": "Does VIT provide Wi-Fi and computing resources in hostels and campus?",
        "answer": "Yes — VIT campuses are equipped with high-speed campus-wide Wi-Fi, computer labs, printing/photocopy services, study lounges in hostels and dedicated research computing infrastructure for eligible students.",
        "category": "Facilities"
    },
    {
        "question": "Are women’s hostels and safety arrangements adequate at VIT?",
        "answer": "Yes — VIT has dedicated women’s hostels with wardens, security, CCTV coverage, visitor logs, curfew enforcement and the Student Welfare/Grievance cell. Students are encouraged to report any safety concerns promptly.",
        "category": "Policies"
    },
    {
        "question": "What are the key contact numbers and emails for admissions and placements at VIT Vellore?",
        "answer": "For VIT Vellore: Admissions Office (UG) – +91-416-220 2020; Placement CDC – +91-416-220 2846; Emails: ugadmission@vit.ac.in, placement@vit.ac.in. :contentReference[oaicite:32]{index=32}",
        "category": "Miscellaneous"
    },
    {
        "question": "Is attendance in club activities or sports counted toward minimum attendance requirements at VIT?",
        "answer": "Attendance in club/sports activities may count as extra-curricular credits but does **not** replace the required minimum attendance in academic/theory classes. Students must still maintain 75% in each subject unless exemptions apply.",
        "category": "Campus Life"
    },
    {
        "question": "How does VIT handle academic dishonesty, plagiarism or cheating during exams?",
        "answer": "VIT’s Student Code of Conduct prohibits academic dishonesty. Penalties for cheating or plagiarism may include grade ‘F’, suspension, expulsion or revocation of degree depending on severity and repeat offence.",
        "category": "Policies"
    },
    {
        "question": "What is the typical batch strength and student-population at VIT Vellore?",
        "answer": "VIT Vellore has a large student population (over 30,000 across UG/PG). Estimates vary; hostel capacity and campus-wide figures are published in mandatory disclosure documents. :contentReference[oaicite:33]{index=33}",
        "category": "General"
    },
    {
        "question": "Does VIT hold summer training programmes or certificate courses for students?",
        "answer": "Yes — VIT organises summer training programmes, certificate courses in emerging technologies (AI, Data Science, IoT, Robotics) and workshops in collaboration with industry and research organisations. Students can enrol for additional credits/external certification.",
        "category": "Research & International"
    },
    {
        "question": "What is the procedure to apply for a hostel room at VIT and how are room types allotted?",
        "answer": "After admission, students apply for hostel accommodation via online/printed form. Room types (AC/Non-AC, bed-sharing type) are allotted on first-come/merit basis, fee category, and availability. Students must pay hostel fees and caution deposit by deadline.",
        "category": "Campus Life"
    },
    {
        "question": "Are extra-curricular credits required for graduation at VIT?",
        "answer": "Yes — Under FFCS some programmes at VIT require students to complete extra-curricular/ co-curricular credits (club participation, sports, social service) to graduate. The exact requirement depends on branch/semester/campus.",
        "category": "Academics"
    },
    {
        "question": "What is the role of the parent/guardian portal at VIT?",
        "answer": "VIT provides an online parent/guardian portal where academic progress, attendance, fee status, hostel/transport details are visible. Parents can view updates and student performance. Students/parents should fetch login credentials during orientation.",
        "category": "Facilities"
    },
    {
        "question": "Does VIT allow students to switch mess from veg to non-veg or vice versa during the year?",
        "answer": "Yes — VIT hostels typically allow change of mess menu option (veg/non-veg) monthly or as per policy. But payment for new mess must be done; downgrading may not be refunded.",
        "category": "Campus Life"
    },
    {
        "question": "What is the policy for campus visits by guardians/parents at VIT?",
        "answer": "Parents/guardians may visit the campus during specified hours. Hostels may require visitor registration, entry-pass and curfew check. Some campuses hold scheduled parent-teacher meetings and orientation days for parents.",
        "category": "Campus Life"
    },
    {
        "question": "Are there any annual alumni meets or networks at VIT?",
        "answer": "Yes — VIT hosts alumni meets (for example ‘Crystal Connexions’ at Chennai campus) where alumni from batches meet, network, mentor students, and share experiences. Alumni networks help students with internships, jobs and start-ups.",
        "category": "Miscellaneous"
    },
    {
        "question": "Does VIT have any MOUs with international universities for research and student exchange?",
        "answer": "Yes — VIT has MoUs with international universities and research institutes for collaboration in emerging tech (AI, semiconductors), student/faculty exchange, joint research and publication. :contentReference[oaicite:34]{index=34}",
        "category": "Research & International"
    },
    {
        "question": "What are the curfew timings in hostels at VIT Vellore?",
        "answer": "Though timings may vary by hostel block and year, at VIT Vellore there are restrictions on student movement after 9 pm (for general outings), and fully returning to hostel may be required by certain curfew hours (e.g., midnight). Specific hostel handbook lists curfew for each block.",
        "category": "Campus Life"
    },
    {
        "question": "What is the policy for rooms/hostels if a student opts not to stay but is eligible for hostel?",
        "answer": "If a student eligible for hostel accommodation opts not to stay (for example local student), they must submit relevant forms and the hostel fee may be exempted or adjusted as per campus policy. Permanent outside staying might need permission and proof of local residence.",
        "category": "Campus Life"
    },
    {
        "question": "Are there health check-ups or medical screening for students at VIT?",
        "answer": "Yes — On joining, students may undergo medical screening, submit health/fitness certificate, and periodic health check-ups or vaccination drives may be organised on campus. The campus medical centre (or hospital) manages student health records.",
        "category": "Facilities"
    },
    {
        "question": "What is the situation for international students at VIT — orientation, visa support, accommodation?",
        "answer": "International students at VIT receive orientation, visa/admission support, special accommodation options, mentors/guides, buddy-systems, and may pay fees in foreign currency or special brackets. They should refer to the International Office of the campus.",
        "category": "Admissions"
    },
    {
        "question": "Is photography, drone usage or filming allowed on VIT campus?",
        "answer": "Photography/filming by students on VIT campus is allowed in public/common areas during events/fests, subject to permission. Use of drones or commercial filming generally requires prior approval from the campus administration/security.",
        "category": "Campus Life"
    },
    {
        "question": "Does VIT allow students to bring laptops/tablets and what is the recommended specification?",
        "answer": "Yes — Students are encouraged to bring laptops/tablets for academic work. Recommended specifications (not mandatory) include ≥8 GB RAM, SSD, latest OS, good battery life. The campus IT department may recommend configurations at orientation.",
        "category": "Facilities"
    },
    {
        "question": "What is the process for re-examination or supplementary exams at VIT if a student fails?",
        "answer": "VIT offers re-exams or supplementary exams for failed subjects as per campus academic regulations. Students may apply within deadlines, pay applicable fees, and register for the exam; failure to register may force course repeat or extra semester.",
        "category": "Academics"
    },
    {
        "question": "How does VIT handle hostel room repairs, maintenance and student complaints?",
        "answer": "Hostel administrators and wardens oversee maintenance; students may register complaints online or via hostel review committee meetings (held every ~15 days at Vellore). Common complaints (fixtures, plumbing, Wi-Fi) are logged and addressed. :contentReference[oaicite:35]{index=35}",
        "category": "Campus Life"
    },
    {
        "question": "What are the options for paid food outlets, cafes or convenience stores inside VIT campus?",
        "answer": "VIT campuses have food courts, cafés, kiosks, convenience stores, stationary shops and beverage outlets within or near hostels/campus. Students may pay via cash/card/QR depending on outlet. Some hostels may restrict outside food delivery during curfew hours.",
        "category": "Campus Life"
    },
    {
        "question": "Can students form new clubs or chapters at VIT if none currently exist for their interest area?",
        "answer": "Yes — VIT allows students to propose new club/chapter formation. They must submit a proposal, list faculty sponsor, objectives, membership plan and get approval from the Student Activities/Dean’s office. The club must adhere to campus norms and register each year.",
        "category": "Campus Life"
    },
    {
        "question": "What is the process for withdrawing from a semester or taking a break/year off at VIT?",
        "answer": "If a student wishes to take a break or sit out a semester/year, they must apply for leave of absence as per campus policy, pay any applicable fees, submit reasons and guardian consent. On return they may need to follow re-registration procedures and meet CGPA criteria.",
        "category": "Policies"
    },
    {
        "question": "Does VIT allow women to stay with family/vocational stay off-campus during semesters?",
        "answer": "Some campuses of VIT may allow local women students (residing nearby) to live with their families and commute rather than stay in hostel, subject to parent/guardian consent and campus policies. Hostels may remain mandatory for out-station students.",
        "category": "Campus Life"
    },
    {
        "question": "What are the key steps for freshers arriving at VIT Vellore during orientation week?",
        "answer": "First year students arriving at VIT Vellore during orientation week must complete document verification, hostel allotment/check-in, ID card issuance, participate in induction programme, attend briefings on academic system, club fair, transport registration and attend the welcome event.",
        "category": "Admissions"
    },
    {
        "question": "Is there a code of ethics or value system emphasised at VIT during student life?",
        "answer": "Yes — VIT emphasises ethical values, integrity, professional behaviour and character building. For instance, during convocation older speakers have emphasized ethics alongside technical competence. :contentReference[oaicite:36]{index=36}",
        "category": "Miscellaneous"
    },
    {
        "question": "How are electives and minor specialisations chosen under FFCS at VIT?",
        "answer": "Under FFCS at VIT, students pick electives/minors based on their credits, branch prerequisites and seat availability. The registration process opens each semester, and students must clear required number of credits for their branch and minor/honours programmes.",
        "category": "Academics"
    }
]

# ============================================================
# FUNCTION TO SEED FAQ DATA
# ============================================================

def seed_faqs(db_service: MongoDBService):
    print("\n" + "="*60)
    print("SEEDING FAQ DATA")
    print("="*60)
    
    initialize_embedding_model(EMBEDDING_MODEL_NAME)

    # Create embedding inputs (use both question + answer)
    texts = [f"Q: {faq['question']} A: {faq['answer']}" for faq in SAMPLE_FAQS]
    print(f"\nGenerating embeddings for {len(texts)} FAQs...")
    embeddings = generate_batch_embeddings(texts)

    for faq, embedding in zip(SAMPLE_FAQS, embeddings):
        faq_data = {
            **faq,
            "embedding": embedding,
            "created_at": datetime.utcnow()
        }

        doc_id = db_service.add_faq(faq_data)
        if doc_id:
            print(f"✅ Added FAQ: {faq['question'][:60]}...")
        else:
            print(f"❌ Failed to add FAQ: {faq['question'][:60]}...")

    print("\n✅ FAQ seeding complete!")

# ============================================================
# MAIN ENTRY POINT
# ============================================================

def main():
    print("\n" + "="*70)
    print("VIT COUNSELING ASSISTANT - FAQ DATABASE SEEDING")
    print("="*70)
    
    db_service = MongoDBService(MONGODB_URL)
    if not db_service.is_connected():
        print("\n❌ Error: Could not connect to MongoDB.")
        return

    response = input("\nThis will add FAQ data to MongoDB. Proceed? (yes/no): ")
    if response.lower() != 'yes':
        print("Seeding cancelled.")
        return

    seed_faqs(db_service)
    
    print("\n" + "="*70)
    print("FAQ SEEDING COMPLETE!")
    print("="*70)

if __name__ == "__main__":
    main()
