import sys
import os
from datetime import datetime
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dotenv import load_dotenv
from services.mongodb_service import MongoDBService
from utils.embeddings import initialize_embedding_model, generate_batch_embeddings

load_dotenv()

MONGODB_URL = os.getenv("MONGODB_URL", "mongodb://localhost:27017/")
EMBEDDING_MODEL_NAME = os.getenv("EMBEDDING_MODEL_NAME", "all-mpnet-base-v2")

# Sample data with year-wise cutoffs
SAMPLE_CUTOFFS = [
    {
        "year": 2021,
        "campus": "Vellore",
        "branch": "Computer Science and Engineering (CSE)",
        "category": "Category 1",
        "rank_range": [
            1,
            1840
        ],
        "seats": 240,
        "filled": 213,
        "notes": "Highly competitive; specialisations slightly less competitive than core."
    },
    {
        "year": 2021,
        "campus": "Vellore",
        "branch": "Computer Science and Engineering (CSE)",
        "category": "Category 2",
        "rank_range": [
            36,
            3312
        ],
        "seats": 240,
        "filled": 227,
        "notes": "Highly competitive; specialisations slightly less competitive than core."
    },
    {
        "year": 2021,
        "campus": "Vellore",
        "branch": "Computer Science and Engineering (CSE)",
        "category": "Category 3",
        "rank_range": [
            18,
            6440
        ],
        "seats": 240,
        "filled": 211,
        "notes": "Highly competitive; specialisations slightly less competitive than core."
    },
    {
        "year": 2021,
        "campus": "Vellore",
        "branch": "Computer Science and Engineering (CSE)",
        "category": "Category 4",
        "rank_range": [
            18,
            9200
        ],
        "seats": 240,
        "filled": 226,
        "notes": "Highly competitive; specialisations slightly less competitive than core."
    },
    {
        "year": 2021,
        "campus": "Vellore",
        "branch": "Computer Science and Engineering (CSE)",
        "category": "Category 5",
        "rank_range": [
            18,
            11960
        ],
        "seats": 240,
        "filled": 211,
        "notes": "Highly competitive; specialisations slightly less competitive than core."
    },
    {
        "year": 2021,
        "campus": "Vellore",
        "branch": "CSE (AI/ML)",
        "category": "Category 1",
        "rank_range": [
            1,
            4600
        ],
        "seats": 60,
        "filled": 52,
        "notes": "Highly competitive; specialisations slightly less competitive than core."
    },
    {
        "year": 2021,
        "campus": "Vellore",
        "branch": "CSE (AI/ML)",
        "category": "Category 2",
        "rank_range": [
            46,
            8280
        ],
        "seats": 60,
        "filled": 52,
        "notes": "Highly competitive; specialisations slightly less competitive than core."
    },
    {
        "year": 2021,
        "campus": "Vellore",
        "branch": "CSE (AI/ML)",
        "category": "Category 3",
        "rank_range": [
            46,
            16100
        ],
        "seats": 60,
        "filled": 51,
        "notes": "Highly competitive; specialisations slightly less competitive than core."
    },
    {
        "year": 2021,
        "campus": "Vellore",
        "branch": "CSE (AI/ML)",
        "category": "Category 4",
        "rank_range": [
            46,
            23000
        ],
        "seats": 60,
        "filled": 54,
        "notes": "Highly competitive; specialisations slightly less competitive than core."
    },
    {
        "year": 2021,
        "campus": "Vellore",
        "branch": "CSE (AI/ML)",
        "category": "Category 5",
        "rank_range": [
            46,
            29900
        ],
        "seats": 60,
        "filled": 50,
        "notes": "Highly competitive; specialisations slightly less competitive than core."
    },
    {
        "year": 2021,
        "campus": "Vellore",
        "branch": "CSE (Data Science)",
        "category": "Category 1",
        "rank_range": [
            1,
            4600
        ],
        "seats": 60,
        "filled": 51,
        "notes": "Highly competitive; specialisations slightly less competitive than core."
    },
    {
        "year": 2021,
        "campus": "Vellore",
        "branch": "CSE (Data Science)",
        "category": "Category 2",
        "rank_range": [
            46,
            8280
        ],
        "seats": 60,
        "filled": 51,
        "notes": "Highly competitive; specialisations slightly less competitive than core."
    },
    {
        "year": 2021,
        "campus": "Vellore",
        "branch": "CSE (Data Science)",
        "category": "Category 3",
        "rank_range": [
            46,
            16100
        ],
        "seats": 60,
        "filled": 52,
        "notes": "Highly competitive; specialisations slightly less competitive than core."
    },
    {
        "year": 2021,
        "campus": "Vellore",
        "branch": "CSE (Data Science)",
        "category": "Category 4",
        "rank_range": [
            46,
            23000
        ],
        "seats": 60,
        "filled": 55,
        "notes": "Highly competitive; specialisations slightly less competitive than core."
    },
    {
        "year": 2021,
        "campus": "Vellore",
        "branch": "CSE (Data Science)",
        "category": "Category 5",
        "rank_range": [
            46,
            29900
        ],
        "seats": 60,
        "filled": 54,
        "notes": "Highly competitive; specialisations slightly less competitive than core."
    },
    {
        "year": 2021,
        "campus": "Vellore",
        "branch": "CSE (IoT)",
        "category": "Category 1",
        "rank_range": [
            1,
            3066
        ],
        "seats": 40,
        "filled": 35,
        "notes": "Highly competitive; specialisations slightly less competitive than core."
    },
    {
        "year": 2021,
        "campus": "Vellore",
        "branch": "CSE (IoT)",
        "category": "Category 2",
        "rank_range": [
            31,
            5520
        ],
        "seats": 40,
        "filled": 37,
        "notes": "Highly competitive; specialisations slightly less competitive than core."
    },
    {
        "year": 2021,
        "campus": "Vellore",
        "branch": "CSE (IoT)",
        "category": "Category 3",
        "rank_range": [
            31,
            10720
        ],
        "seats": 40,
        "filled": 32,
        "notes": "Highly competitive; specialisations slightly less competitive than core."
    },
    {
        "year": 2021,
        "campus": "Vellore",
        "branch": "CSE (IoT)",
        "category": "Category 4",
        "rank_range": [
            31,
            15300
        ],
        "seats": 40,
        "filled": 33,
        "notes": "Highly competitive; specialisations slightly less competitive than core."
    },
    {
        "year": 2021,
        "campus": "Vellore",
        "branch": "CSE (IoT)",
        "category": "Category 5",
        "rank_range": [
            31,
            19950
        ],
        "seats": 40,
        "filled": 33,
        "notes": "Highly competitive; specialisations slightly less competitive than core."
    },
    {
        "year": 2021,
        "campus": "Vellore",
        "branch": "CSE (Cyber Security)",
        "category": "Category 1",
        "rank_range": [
            1,
            3066
        ],
        "seats": 40,
        "filled": 35,
        "notes": "Highly competitive; specialisations slightly less competitive than core."
    },
    {
        "year": 2021,
        "campus": "Vellore",
        "branch": "CSE (Cyber Security)",
        "category": "Category 2",
        "rank_range": [
            31,
            5520
        ],
        "seats": 40,
        "filled": 33,
        "notes": "Highly competitive; specialisations slightly less competitive than core."
    },
    {
        "year": 2021,
        "campus": "Vellore",
        "branch": "CSE (Cyber Security)",
        "category": "Category 3",
        "rank_range": [
            31,
            10720
        ],
        "seats": 40,
        "filled": 32,
        "notes": "Highly competitive; specialisations slightly less competitive than core."
    },
    {
        "year": 2021,
        "campus": "Vellore",
        "branch": "CSE (Cyber Security)",
        "category": "Category 4",
        "rank_range": [
            31,
            15300
        ],
        "seats": 40,
        "filled": 32,
        "notes": "Highly competitive; specialisations slightly less competitive than core."
    },
    {
        "year": 2021,
        "campus": "Vellore",
        "branch": "CSE (Cyber Security)",
        "category": "Category 5",
        "rank_range": [
            31,
            19950
        ],
        "seats": 40,
        "filled": 32,
        "notes": "Highly competitive; specialisations slightly less competitive than core."
    },
    {
        "year": 2021,
        "campus": "Vellore",
        "branch": "CSE (Blockchain)",
        "category": "Category 1",
        "rank_range": [
            1,
            3450
        ],
        "seats": 30,
        "filled": 27,
        "notes": "Highly competitive; specialisations slightly less competitive than core."
    },
    {
        "year": 2021,
        "campus": "Vellore",
        "branch": "CSE (Blockchain)",
        "category": "Category 2",
        "rank_range": [
            35,
            6210
        ],
        "seats": 30,
        "filled": 25,
        "notes": "Highly competitive; specialisations slightly less competitive than core."
    },
    {
        "year": 2021,
        "campus": "Vellore",
        "branch": "CSE (Blockchain)",
        "category": "Category 3",
        "rank_range": [
            35,
            12060
        ],
        "seats": 30,
        "filled": 25,
        "notes": "Highly competitive; specialisations slightly less competitive than core."
    },
    {
        "year": 2021,
        "campus": "Vellore",
        "branch": "CSE (Blockchain)",
        "category": "Category 4",
        "rank_range": [
            35,
            17250
        ],
        "seats": 30,
        "filled": 27,
        "notes": "Highly competitive; specialisations slightly less competitive than core."
    },
    {
        "year": 2021,
        "campus": "Vellore",
        "branch": "CSE (Blockchain)",
        "category": "Category 5",
        "rank_range": [
            35,
            22425
        ],
        "seats": 30,
        "filled": 25,
        "notes": "Highly competitive; specialisations slightly less competitive than core."
    },
    {
        "year": 2021,
        "campus": "Vellore",
        "branch": "Electronics and Communication Engineering (ECE)",
        "category": "Category 1",
        "rank_range": [
            1,
            12300
        ],
        "seats": 180,
        "filled": 162,
        "notes": "Moderately competitive; VLSI is sought after."
    },
    {
        "year": 2021,
        "campus": "Vellore",
        "branch": "Electronics and Communication Engineering (ECE)",
        "category": "Category 2",
        "rank_range": [
            123,
            22140
        ],
        "seats": 180,
        "filled": 156,
        "notes": "Moderately competitive; VLSI is sought after."
    },
    {
        "year": 2021,
        "campus": "Vellore",
        "branch": "Electronics and Communication Engineering (ECE)",
        "category": "Category 3",
        "rank_range": [
            123,
            42900
        ],
        "seats": 180,
        "filled": 162,
        "notes": "Moderately competitive; VLSI is sought after."
    },
    {
        "year": 2021,
        "campus": "Vellore",
        "branch": "Electronics and Communication Engineering (ECE)",
        "category": "Category 4",
        "rank_range": [
            123,
            61200
        ],
        "seats": 180,
        "filled": 165,
        "notes": "Moderately competitive; VLSI is sought after."
    },
    {
        "year": 2021,
        "campus": "Vellore",
        "branch": "Electronics and Communication Engineering (ECE)",
        "category": "Category 5",
        "rank_range": [
            123,
            79650
        ],
        "seats": 180,
        "filled": 165,
        "notes": "Moderately competitive; VLSI is sought after."
    },
    {
        "year": 2021,
        "campus": "Vellore",
        "branch": "ECE (VLSI)",
        "category": "Category 1",
        "rank_range": [
            1,
            4100
        ],
        "seats": 60,
        "filled": 53,
        "notes": "Moderately competitive; VLSI is sought after."
    },
    {
        "year": 2021,
        "campus": "Vellore",
        "branch": "ECE (VLSI)",
        "category": "Category 2",
        "rank_range": [
            41,
            7380
        ],
        "seats": 60,
        "filled": 55,
        "notes": "Moderately competitive; VLSI is sought after."
    },
    {
        "year": 2021,
        "campus": "Vellore",
        "branch": "ECE (VLSI)",
        "category": "Category 3",
        "rank_range": [
            41,
            14320
        ],
        "seats": 60,
        "filled": 56,
        "notes": "Moderately competitive; VLSI is sought after."
    },
    {
        "year": 2021,
        "campus": "Vellore",
        "branch": "ECE (VLSI)",
        "category": "Category 4",
        "rank_range": [
            41,
            20400
        ],
        "seats": 60,
        "filled": 58,
        "notes": "Moderately competitive; VLSI is sought after."
    },
    {
        "year": 2021,
        "campus": "Vellore",
        "branch": "ECE (VLSI)",
        "category": "Category 5",
        "rank_range": [
            41,
            26520
        ],
        "seats": 60,
        "filled": 55,
        "notes": "Moderately competitive; VLSI is sought after."
    },
    {
        "year": 2021,
        "campus": "Vellore",
        "branch": "ECE (BioMedical)",
        "category": "Category 1",
        "rank_range": [
            1,
            3066
        ],
        "seats": 40,
        "filled": 35,
        "notes": "Moderately competitive; VLSI is sought after."
    },
    {
        "year": 2021,
        "campus": "Vellore",
        "branch": "ECE (BioMedical)",
        "category": "Category 2",
        "rank_range": [
            31,
            5520
        ],
        "seats": 40,
        "filled": 33,
        "notes": "Moderately competitive; VLSI is sought after."
    },
    {
        "year": 2021,
        "campus": "Vellore",
        "branch": "ECE (BioMedical)",
        "category": "Category 3",
        "rank_range": [
            31,
            10720
        ],
        "seats": 40,
        "filled": 30,
        "notes": "Moderately competitive; VLSI is sought after."
    },
    {
        "year": 2021,
        "campus": "Vellore",
        "branch": "ECE (BioMedical)",
        "category": "Category 4",
        "rank_range": [
            31,
            15300
        ],
        "seats": 40,
        "filled": 30,
        "notes": "Moderately competitive; VLSI is sought after."
    },
    {
        "year": 2021,
        "campus": "Vellore",
        "branch": "ECE (BioMedical)",
        "category": "Category 5",
        "rank_range": [
            31,
            19950
        ],
        "seats": 40,
        "filled": 29,
        "notes": "Moderately competitive; VLSI is sought after."
    },
    {
        "year": 2021,
        "campus": "Vellore",
        "branch": "Civil Engineering",
        "category": "Category 1",
        "rank_range": [
            1,
            25000
        ],
        "seats": 120,
        "filled": 101,
        "notes": "Lower demand compared to CSE/ECE; closing ranks later."
    },
    {
        "year": 2021,
        "campus": "Vellore",
        "branch": "Civil Engineering",
        "category": "Category 2",
        "rank_range": [
            250,
            45000
        ],
        "seats": 120,
        "filled": 109,
        "notes": "Lower demand compared to CSE/ECE; closing ranks later."
    },
    {
        "year": 2021,
        "campus": "Vellore",
        "branch": "Civil Engineering",
        "category": "Category 3",
        "rank_range": [
            250,
            87400
        ],
        "seats": 120,
        "filled": 109,
        "notes": "Lower demand compared to CSE/ECE; closing ranks later."
    },
    {
        "year": 2021,
        "campus": "Vellore",
        "branch": "Civil Engineering",
        "category": "Category 4",
        "rank_range": [
            250,
            124000
        ],
        "seats": 120,
        "filled": 108,
        "notes": "Lower demand compared to CSE/ECE; closing ranks later."
    },
    {
        "year": 2021,
        "campus": "Vellore",
        "branch": "Civil Engineering",
        "category": "Category 5",
        "rank_range": [
            250,
            161200
        ],
        "seats": 120,
        "filled": 106,
        "notes": "Lower demand compared to CSE/ECE; closing ranks later."
    },
    {
        "year": 2021,
        "campus": "Vellore",
        "branch": "Electrical and Electronics Engineering (EEE)",
        "category": "Category 1",
        "rank_range": [
            1,
            18000
        ],
        "seats": 120,
        "filled": 105,
        "notes": "Lower demand compared to CSE/ECE; closing ranks later."
    },
    {
        "year": 2021,
        "campus": "Vellore",
        "branch": "Electrical and Electronics Engineering (EEE)",
        "category": "Category 2",
        "rank_range": [
            180,
            32400
        ],
        "seats": 120,
        "filled": 102,
        "notes": "Lower demand compared to CSE/ECE; closing ranks later."
    },
    {
        "year": 2021,
        "campus": "Vellore",
        "branch": "Electrical and Electronics Engineering (EEE)",
        "category": "Category 3",
        "rank_range": [
            180,
            62600
        ],
        "seats": 120,
        "filled": 106,
        "notes": "Lower demand compared to CSE/ECE; closing ranks later."
    },
    {
        "year": 2021,
        "campus": "Vellore",
        "branch": "Electrical and Electronics Engineering (EEE)",
        "category": "Category 4",
        "rank_range": [
            180,
            87000
        ],
        "seats": 120,
        "filled": 102,
        "notes": "Lower demand compared to CSE/ECE; closing ranks later."
    },
    {
        "year": 2021,
        "campus": "Vellore",
        "branch": "Electrical and Electronics Engineering (EEE)",
        "category": "Category 5",
        "rank_range": [
            180,
            113400
        ],
        "seats": 120,
        "filled": 102,
        "notes": "Lower demand compared to CSE/ECE; closing ranks later."
    },
    {
        "year": 2021,
        "campus": "Vellore",
        "branch": "Electrical Engineering (EE)",
        "category": "Category 1",
        "rank_range": [
            1,
            12000
        ],
        "seats": 80,
        "filled": 72,
        "notes": "Lower demand compared to CSE/ECE; closing ranks later."
    },
    {
        "year": 2021,
        "campus": "Vellore",
        "branch": "Electrical Engineering (EE)",
        "category": "Category 2",
        "rank_range": [
            120,
            21600
        ],
        "seats": 80,
        "filled": 69,
        "notes": "Lower demand compared to CSE/ECE; closing ranks later."
    },
    {
        "year": 2021,
        "campus": "Vellore",
        "branch": "Electrical Engineering (EE)",
        "category": "Category 3",
        "rank_range": [
            120,
            41700
        ],
        "seats": 80,
        "filled": 71,
        "notes": "Lower demand compared to CSE/ECE; closing ranks later."
    },
    {
        "year": 2021,
        "campus": "Vellore",
        "branch": "Electrical Engineering (EE)",
        "category": "Category 4",
        "rank_range": [
            120,
            58000
        ],
        "seats": 80,
        "filled": 71,
        "notes": "Lower demand compared to CSE/ECE; closing ranks later."
    },
    {
        "year": 2021,
        "campus": "Vellore",
        "branch": "Electrical Engineering (EE)",
        "category": "Category 5",
        "rank_range": [
            120,
            75700
        ],
        "seats": 80,
        "filled": 71,
        "notes": "Lower demand compared to CSE/ECE; closing ranks later."
    },
    {
        "year": 2021,
        "campus": "Vellore",
        "branch": "Mechanical Engineering (core)",
        "category": "Category 1",
        "rank_range": [
            1,
            20000
        ],
        "seats": 150,
        "filled": 129,
        "notes": "Good demand; core mechanical more stable."
    },
    {
        "year": 2021,
        "campus": "Vellore",
        "branch": "Mechanical Engineering (core)",
        "category": "Category 2",
        "rank_range": [
            200,
            36000
        ],
        "seats": 150,
        "filled": 137,
        "notes": "Good demand; core mechanical more stable."
    },
    {
        "year": 2021,
        "campus": "Vellore",
        "branch": "Mechanical Engineering (core)",
        "category": "Category 3",
        "rank_range": [
            200,
            65600
        ],
        "seats": 150,
        "filled": 132,
        "notes": "Good demand; core mechanical more stable."
    },
    {
        "year": 2021,
        "campus": "Vellore",
        "branch": "Mechanical Engineering (core)",
        "category": "Category 4",
        "rank_range": [
            200,
            91200
        ],
        "seats": 150,
        "filled": 128,
        "notes": "Good demand; core mechanical more stable."
    },
    {
        "year": 2021,
        "campus": "Vellore",
        "branch": "Mechanical Engineering (core)",
        "category": "Category 5",
        "rank_range": [
            200,
            118800
        ],
        "seats": 150,
        "filled": 131,
        "notes": "Good demand; core mechanical more stable."
    },
    {
        "year": 2021,
        "campus": "Vellore",
        "branch": "Mechanical (Automotive)",
        "category": "Category 1",
        "rank_range": [
            1,
            4100
        ],
        "seats": 60,
        "filled": 55,
        "notes": "Good demand; core mechanical more stable."
    },
    {
        "year": 2021,
        "campus": "Vellore",
        "branch": "Mechanical (Automotive)",
        "category": "Category 2",
        "rank_range": [
            41,
            7380
        ],
        "seats": 60,
        "filled": 56,
        "notes": "Good demand; core mechanical more stable."
    },
    {
        "year": 2021,
        "campus": "Vellore",
        "branch": "Mechanical (Automotive)",
        "category": "Category 3",
        "rank_range": [
            41,
            14320
        ],
        "seats": 60,
        "filled": 51,
        "notes": "Good demand; core mechanical more stable."
    },
    {
        "year": 2021,
        "campus": "Vellore",
        "branch": "Mechanical (Automotive)",
        "category": "Category 4",
        "rank_range": [
            41,
            20400
        ],
        "seats": 60,
        "filled": 53,
        "notes": "Good demand; core mechanical more stable."
    },
    {
        "year": 2021,
        "campus": "Vellore",
        "branch": "Mechanical (Automotive)",
        "category": "Category 5",
        "rank_range": [
            41,
            26520
        ],
        "seats": 60,
        "filled": 55,
        "notes": "Good demand; core mechanical more stable."
    },
    {
        "year": 2021,
        "campus": "Vellore",
        "branch": "Biotechnology",
        "category": "Category 1",
        "rank_range": [
            1,
            30000
        ],
        "seats": 60,
        "filled": 53,
        "notes": "Niche branch; moderate demand."
    },
    {
        "year": 2021,
        "campus": "Vellore",
        "branch": "Biotechnology",
        "category": "Category 2",
        "rank_range": [
            300,
            54000
        ],
        "seats": 60,
        "filled": 58,
        "notes": "Niche branch; moderate demand."
    },
    {
        "year": 2021,
        "campus": "Vellore",
        "branch": "Biotechnology",
        "category": "Category 3",
        "rank_range": [
            300,
            102000
        ],
        "seats": 60,
        "filled": 60,
        "notes": "Niche branch; moderate demand."
    },
    {
        "year": 2021,
        "campus": "Vellore",
        "branch": "Biotechnology",
        "category": "Category 4",
        "rank_range": [
            300,
            150000
        ],
        "seats": 60,
        "filled": 56,
        "notes": "Niche branch; moderate demand."
    },
    {
        "year": 2021,
        "campus": "Vellore",
        "branch": "Biotechnology",
        "category": "Category 5",
        "rank_range": [
            300,
            197250
        ],
        "seats": 60,
        "filled": 55,
        "notes": "Niche branch; moderate demand."
    },
    {
        "year": 2021,
        "campus": "Chennai",
        "branch": "Computer Science and Engineering (CSE)",
        "category": "Category 1",
        "rank_range": [
            1,
            2944
        ],
        "seats": 180,
        "filled": 164,
        "notes": "Highly competitive; specialisations slightly less competitive than core."
    },
    {
        "year": 2021,
        "campus": "Chennai",
        "branch": "Computer Science and Engineering (CSE)",
        "category": "Category 2",
        "rank_range": [
            29,
            5298
        ],
        "seats": 180,
        "filled": 153,
        "notes": "Highly competitive; specialisations slightly less competitive than core."
    },
    {
        "year": 2021,
        "campus": "Chennai",
        "branch": "Computer Science and Engineering (CSE)",
        "category": "Category 3",
        "rank_range": [
            15,
            10280
        ],
        "seats": 180,
        "filled": 146,
        "notes": "Highly competitive; specialisations slightly less competitive than core."
    },
    {
        "year": 2021,
        "campus": "Chennai",
        "branch": "Computer Science and Engineering (CSE)",
        "category": "Category 4",
        "rank_range": [
            15,
            14680
        ],
        "seats": 180,
        "filled": 152,
        "notes": "Highly competitive; specialisations slightly less competitive than core."
    },
    {
        "year": 2021,
        "campus": "Chennai",
        "branch": "Computer Science and Engineering (CSE)",
        "category": "Category 5",
        "rank_range": [
            15,
            19052
        ],
        "seats": 180,
        "filled": 162,
        "notes": "Highly competitive; specialisations slightly less competitive than core."
    },
    {
        "year": 2021,
        "campus": "Chennai",
        "branch": "CSE (AI/ML)",
        "category": "Category 1",
        "rank_range": [
            1,
            7344
        ],
        "seats": 40,
        "filled": 35,
        "notes": "Highly competitive; specialisations slightly less competitive than core."
    },
    {
        "year": 2021,
        "campus": "Chennai",
        "branch": "CSE (AI/ML)",
        "category": "Category 2",
        "rank_range": [
            73,
            13192
        ],
        "seats": 40,
        "filled": 36,
        "notes": "Highly competitive; specialisations slightly less competitive than core."
    },
    {
        "year": 2021,
        "campus": "Chennai",
        "branch": "CSE (AI/ML)",
        "category": "Category 3",
        "rank_range": [
            73,
            25380
        ],
        "seats": 40,
        "filled": 38,
        "notes": "Highly competitive; specialisations slightly less competitive than core."
    },
    {
        "year": 2021,
        "campus": "Chennai",
        "branch": "CSE (AI/ML)",
        "category": "Category 4",
        "rank_range": [
            73,
            36200
        ],
        "seats": 40,
        "filled": 36,
        "notes": "Highly competitive; specialisations slightly less competitive than core."
    },
    {
        "year": 2021,
        "campus": "Chennai",
        "branch": "CSE (AI/ML)",
        "category": "Category 5",
        "rank_range": [
            73,
            47040
        ],
        "seats": 40,
        "filled": 38,
        "notes": "Highly competitive; specialisations slightly less competitive than core."
    },
    {
        "year": 2021,
        "campus": "Chennai",
        "branch": "CSE (Data Science)",
        "category": "Category 1",
        "rank_range": [
            1,
            7344
        ],
        "seats": 40,
        "filled": 34,
        "notes": "Highly competitive; specialisations slightly less competitive than core."
    },
    {
        "year": 2021,
        "campus": "Chennai",
        "branch": "CSE (Data Science)",
        "category": "Category 2",
        "rank_range": [
            73,
            13192
        ],
        "seats": 40,
        "filled": 36,
        "notes": "Highly competitive; specialisations slightly less competitive than core."
    },
    {
        "year": 2021,
        "campus": "Chennai",
        "branch": "CSE (Data Science)",
        "category": "Category 3",
        "rank_range": [
            73,
            25380
        ],
        "seats": 40,
        "filled": 35,
        "notes": "Highly competitive; specialisations slightly less competitive than core."
    },
    {
        "year": 2021,
        "campus": "Chennai",
        "branch": "CSE (Data Science)",
        "category": "Category 4",
        "rank_range": [
            73,
            36200
        ],
        "seats": 40,
        "filled": 36,
        "notes": "Highly competitive; specialisations slightly less competitive than core."
    },
    {
        "year": 2021,
        "campus": "Chennai",
        "branch": "CSE (Data Science)",
        "category": "Category 5",
        "rank_range": [
            73,
            47040
        ],
        "seats": 40,
        "filled": 36,
        "notes": "Highly competitive; specialisations slightly less competitive than core."
    },
    {
        "year": 2021,
        "campus": "Chennai",
        "branch": "CSE (IoT)",
        "category": "Category 1",
        "rank_range": [
            1,
            4878
        ],
        "seats": 30,
        "filled": 26,
        "notes": "Highly competitive; specialisations slightly less competitive than core."
    },
    {
        "year": 2021,
        "campus": "Chennai",
        "branch": "CSE (IoT)",
        "category": "Category 2",
        "rank_range": [
            49,
            8748
        ],
        "seats": 30,
        "filled": 25,
        "notes": "Highly competitive; specialisations slightly less competitive than core."
    },
    {
        "year": 2021,
        "campus": "Chennai",
        "branch": "CSE (IoT)",
        "category": "Category 3",
        "rank_range": [
            49,
            16800
        ],
        "seats": 30,
        "filled": 26,
        "notes": "Highly competitive; specialisations slightly less competitive than core."
    },
    {
        "year": 2021,
        "campus": "Chennai",
        "branch": "CSE (IoT)",
        "category": "Category 4",
        "rank_range": [
            49,
            23970
        ],
        "seats": 30,
        "filled": 25,
        "notes": "Highly competitive; specialisations slightly less competitive than core."
    },
    {
        "year": 2021,
        "campus": "Chennai",
        "branch": "CSE (IoT)",
        "category": "Category 5",
        "rank_range": [
            49,
            31155
        ],
        "seats": 30,
        "filled": 28,
        "notes": "Highly competitive; specialisations slightly less competitive than core."
    },
    {
        "year": 2021,
        "campus": "Chennai",
        "branch": "CSE (Cyber Security)",
        "category": "Category 1",
        "rank_range": [
            1,
            4878
        ],
        "seats": 30,
        "filled": 27,
        "notes": "Highly competitive; specialisations slightly less competitive than core."
    },
    {
        "year": 2021,
        "campus": "Chennai",
        "branch": "CSE (Cyber Security)",
        "category": "Category 2",
        "rank_range": [
            49,
            8748
        ],
        "seats": 30,
        "filled": 27,
        "notes": "Highly competitive; specialisations slightly less competitive than core."
    },
    {
        "year": 2021,
        "campus": "Chennai",
        "branch": "CSE (Cyber Security)",
        "category": "Category 3",
        "rank_range": [
            49,
            16800
        ],
        "seats": 30,
        "filled": 28,
        "notes": "Highly competitive; specialisations slightly less competitive than core."
    },
    {
        "year": 2021,
        "campus": "Chennai",
        "branch": "CSE (Cyber Security)",
        "category": "Category 4",
        "rank_range": [
            49,
            23970
        ],
        "seats": 30,
        "filled": 27,
        "notes": "Highly competitive; specialisations slightly less competitive than core."
    },
    {
        "year": 2021,
        "campus": "Chennai",
        "branch": "CSE (Cyber Security)",
        "category": "Category 5",
        "rank_range": [
            49,
            31155
        ],
        "seats": 30,
        "filled": 28,
        "notes": "Highly competitive; specialisations slightly less competitive than core."
    },
    {
        "year": 2021,
        "campus": "Chennai",
        "branch": "CSE (Blockchain)",
        "category": "Category 1",
        "rank_range": [
            1,
            5486
        ],
        "seats": 20,
        "filled": 18,
        "notes": "Highly competitive; specialisations slightly less competitive than core."
    },
    {
        "year": 2021,
        "campus": "Chennai",
        "branch": "CSE (Blockchain)",
        "category": "Category 2",
        "rank_range": [
            54,
            9852
        ],
        "seats": 20,
        "filled": 19,
        "notes": "Highly competitive; specialisations slightly less competitive than core."
    },
    {
        "year": 2021,
        "campus": "Chennai",
        "branch": "CSE (Blockchain)",
        "category": "Category 3",
        "rank_range": [
            54,
            18960
        ],
        "seats": 20,
        "filled": 18,
        "notes": "Highly competitive; specialisations slightly less competitive than core."
    },
    {
        "year": 2021,
        "campus": "Chennai",
        "branch": "CSE (Blockchain)",
        "category": "Category 4",
        "rank_range": [
            54,
            27000
        ],
        "seats": 20,
        "filled": 17,
        "notes": "Highly competitive; specialisations slightly less competitive than core."
    },
    {
        "year": 2021,
        "campus": "Chennai",
        "branch": "CSE (Blockchain)",
        "category": "Category 5",
        "rank_range": [
            54,
            35010
        ],
        "seats": 20,
        "filled": 18,
        "notes": "Highly competitive; specialisations slightly less competitive than core."
    },
    {
        "year": 2021,
        "campus": "Chennai",
        "branch": "Electronics and Communication Engineering (ECE)",
        "category": "Category 1",
        "rank_range": [
            1,
            19680
        ],
        "seats": 140,
        "filled": 125,
        "notes": "Moderately competitive; VLSI is sought after."
    },
    {
        "year": 2021,
        "campus": "Chennai",
        "branch": "Electronics and Communication Engineering (ECE)",
        "category": "Category 2",
        "rank_range": [
            140,
            35376
        ],
        "seats": 140,
        "filled": 122,
        "notes": "Moderately competitive; VLSI is sought after."
    },
    {
        "year": 2021,
        "campus": "Chennai",
        "branch": "Electronics and Communication Engineering (ECE)",
        "category": "Category 3",
        "rank_range": [
            140,
            68520
        ],
        "seats": 140,
        "filled": 129,
        "notes": "Moderately competitive; VLSI is sought after."
    },
    {
        "year": 2021,
        "campus": "Chennai",
        "branch": "Electronics and Communication Engineering (ECE)",
        "category": "Category 4",
        "rank_range": [
            140,
            97920
        ],
        "seats": 140,
        "filled": 127,
        "notes": "Moderately competitive; VLSI is sought after."
    },
    {
        "year": 2021,
        "campus": "Chennai",
        "branch": "Electronics and Communication Engineering (ECE)",
        "category": "Category 5",
        "rank_range": [
            140,
            127380
        ],
        "seats": 140,
        "filled": 131,
        "notes": "Moderately competitive; VLSI is sought after."
    },
    {
        "year": 2021,
        "campus": "Chennai",
        "branch": "ECE (VLSI)",
        "category": "Category 1",
        "rank_range": [
            1,
            6544
        ],
        "seats": 40,
        "filled": 35,
        "notes": "Moderately competitive; VLSI is sought after."
    },
    {
        "year": 2021,
        "campus": "Chennai",
        "branch": "ECE (VLSI)",
        "category": "Category 2",
        "rank_range": [
            65,
            11792
        ],
        "seats": 40,
        "filled": 38,
        "notes": "Moderately competitive; VLSI is sought after."
    },
    {
        "year": 2021,
        "campus": "Chennai",
        "branch": "ECE (VLSI)",
        "category": "Category 3",
        "rank_range": [
            65,
            22640
        ],
        "seats": 40,
        "filled": 36,
        "notes": "Moderately competitive; VLSI is sought after."
    },
    {
        "year": 2021,
        "campus": "Chennai",
        "branch": "ECE (VLSI)",
        "category": "Category 4",
        "rank_range": [
            65,
            32200
        ],
        "seats": 40,
        "filled": 37,
        "notes": "Moderately competitive; VLSI is sought after."
    },
    {
        "year": 2021,
        "campus": "Chennai",
        "branch": "ECE (VLSI)",
        "category": "Category 5",
        "rank_range": [
            65,
            41760
        ],
        "seats": 40,
        "filled": 39,
        "notes": "Moderately competitive; VLSI is sought after."
    },
    {
        "year": 2021,
        "campus": "Chennai",
        "branch": "ECE (BioMedical)",
        "category": "Category 1",
        "rank_range": [
            1,
            4878
        ],
        "seats": 30,
        "filled": 26,
        "notes": "Moderately competitive; VLSI is sought after."
    },
    {
        "year": 2021,
        "campus": "Chennai",
        "branch": "ECE (BioMedical)",
        "category": "Category 2",
        "rank_range": [
            48,
            8748
        ],
        "seats": 30,
        "filled": 26,
        "notes": "Moderately competitive; VLSI is sought after."
    },
    {
        "year": 2021,
        "campus": "Chennai",
        "branch": "ECE (BioMedical)",
        "category": "Category 3",
        "rank_range": [
            48,
            16800
        ],
        "seats": 30,
        "filled": 27,
        "notes": "Moderately competitive; VLSI is sought after."
    },
    {
        "year": 2021,
        "campus": "Chennai",
        "branch": "ECE (BioMedical)",
        "category": "Category 4",
        "rank_range": [
            48,
            23970
        ],
        "seats": 30,
        "filled": 28,
        "notes": "Moderately competitive; VLSI is sought after."
    },
    {
        "year": 2021,
        "campus": "Chennai",
        "branch": "ECE (BioMedical)",
        "category": "Category 5",
        "rank_range": [
            48,
            31155
        ],
        "seats": 30,
        "filled": 28,
        "notes": "Moderately competitive; VLSI is sought after."
    },
    {
        "year": 2021,
        "campus": "Chennai",
        "branch": "Civil Engineering",
        "category": "Category 1",
        "rank_range": [
            1,
            40000
        ],
        "seats": 90,
        "filled": 78,
        "notes": "Lower demand compared to CSE/ECE; closing ranks later."
    },
    {
        "year": 2021,
        "campus": "Chennai",
        "branch": "Civil Engineering",
        "category": "Category 2",
        "rank_range": [
            90,
            72000
        ],
        "seats": 90,
        "filled": 74,
        "notes": "Lower demand compared to CSE/ECE; closing ranks later."
    },
    {
        "year": 2021,
        "campus": "Chennai",
        "branch": "Civil Engineering",
        "category": "Category 3",
        "rank_range": [
            90,
            138000
        ],
        "seats": 90,
        "filled": 79,
        "notes": "Lower demand compared to CSE/ECE; closing ranks later."
    },
    {
        "year": 2021,
        "campus": "Chennai",
        "branch": "Civil Engineering",
        "category": "Category 4",
        "rank_range": [
            90,
            195000
        ],
        "seats": 90,
        "filled": 79,
        "notes": "Lower demand compared to CSE/ECE; closing ranks later."
    },
    {
        "year": 2021,
        "campus": "Chennai",
        "branch": "Civil Engineering",
        "category": "Category 5",
        "rank_range": [
            90,
            253590
        ],
        "seats": 90,
        "filled": 78,
        "notes": "Lower demand compared to CSE/ECE; closing ranks later."
    },
    {
        "year": 2021,
        "campus": "Chennai",
        "branch": "Electrical and Electronics Engineering (EEE)",
        "category": "Category 1",
        "rank_range": [
            1,
            28800
        ],
        "seats": 90,
        "filled": 78,
        "notes": "Lower demand compared to CSE/ECE; closing ranks later."
    },
    {
        "year": 2021,
        "campus": "Chennai",
        "branch": "Electrical and Electronics Engineering (EEE)",
        "category": "Category 2",
        "rank_range": [
            90,
            51840
        ],
        "seats": 90,
        "filled": 79,
        "notes": "Lower demand compared to CSE/ECE; closing ranks later."
    },
    {
        "year": 2021,
        "campus": "Chennai",
        "branch": "Electrical and Electronics Engineering (EEE)",
        "category": "Category 3",
        "rank_range": [
            90,
            100080
        ],
        "seats": 90,
        "filled": 79,
        "notes": "Lower demand compared to CSE/ECE; closing ranks later."
    },
    {
        "year": 2021,
        "campus": "Chennai",
        "branch": "Electrical and Electronics Engineering (EEE)",
        "category": "Category 4",
        "rank_range": [
            90,
            138000
        ],
        "seats": 90,
        "filled": 77,
        "notes": "Lower demand compared to CSE/ECE; closing ranks later."
    },
    {
        "year": 2021,
        "campus": "Chennai",
        "branch": "Electrical and Electronics Engineering (EEE)",
        "category": "Category 5",
        "rank_range": [
            90,
            179100
        ],
        "seats": 90,
        "filled": 76,
        "notes": "Lower demand compared to CSE/ECE; closing ranks later."
    },
    {
        "year": 2021,
        "campus": "Chennai",
        "branch": "Electrical Engineering (EE)",
        "category": "Category 1",
        "rank_range": [
            1,
            19200
        ],
        "seats": 60,
        "filled": 53,
        "notes": "Lower demand compared to CSE/ECE; closing ranks later."
    },
    {
        "year": 2021,
        "campus": "Chennai",
        "branch": "Electrical Engineering (EE)",
        "category": "Category 2",
        "rank_range": [
            60,
            34560
        ],
        "seats": 60,
        "filled": 51,
        "notes": "Lower demand compared to CSE/ECE; closing ranks later."
    },
    {
        "year": 2021,
        "campus": "Chennai",
        "branch": "Electrical Engineering (EE)",
        "category": "Category 3",
        "rank_range": [
            60,
            66780
        ],
        "seats": 60,
        "filled": 53,
        "notes": "Lower demand compared to CSE/ECE; closing ranks later."
    },
    {
        "year": 2021,
        "campus": "Chennai",
        "branch": "Electrical Engineering (EE)",
        "category": "Category 4",
        "rank_range": [
            60,
            92700
        ],
        "seats": 60,
        "filled": 50,
        "notes": "Lower demand compared to CSE/ECE; closing ranks later."
    },
    {
        "year": 2021,
        "campus": "Chennai",
        "branch": "Electrical Engineering (EE)",
        "category": "Category 5",
        "rank_range": [
            60,
            120050
        ],
        "seats": 60,
        "filled": 54,
        "notes": "Lower demand compared to CSE/ECE; closing ranks later."
    },
    {
        "year": 2021,
        "campus": "Chennai",
        "branch": "Mechanical Engineering (core)",
        "category": "Category 1",
        "rank_range": [
            1,
            32000
        ],
        "seats": 120,
        "filled": 104,
        "notes": "Good demand; core mechanical more stable."
    },
    {
        "year": 2021,
        "campus": "Chennai",
        "branch": "Mechanical Engineering (core)",
        "category": "Category 2",
        "rank_range": [
            120,
            57600
        ],
        "seats": 120,
        "filled": 116,
        "notes": "Good demand; core mechanical more stable."
    },
    {
        "year": 2021,
        "campus": "Chennai",
        "branch": "Mechanical Engineering (core)",
        "category": "Category 3",
        "rank_range": [
            120,
            104000
        ],
        "seats": 120,
        "filled": 103,
        "notes": "Good demand; core mechanical more stable."
    },
    {
        "year": 2021,
        "campus": "Chennai",
        "branch": "Mechanical Engineering (core)",
        "category": "Category 4",
        "rank_range": [
            120,
            144000
        ],
        "seats": 120,
        "filled": 118,
        "notes": "Good demand; core mechanical more stable."
    },
    {
        "year": 2021,
        "campus": "Chennai",
        "branch": "Mechanical Engineering (core)",
        "category": "Category 5",
        "rank_range": [
            120,
            187200
        ],
        "seats": 120,
        "filled": 118,
        "notes": "Good demand; core mechanical more stable."
    },
    {
        "year": 2021,
        "campus": "Chennai",
        "branch": "Mechanical (Automotive)",
        "category": "Category 1",
        "rank_range": [
            1,
            6544
        ],
        "seats": 40,
        "filled": 36,
        "notes": "Good demand; core mechanical more stable."
    },
    {
        "year": 2021,
        "campus": "Chennai",
        "branch": "Mechanical (Automotive)",
        "category": "Category 2",
        "rank_range": [
            65,
            11792
        ],
        "seats": 40,
        "filled": 38,
        "notes": "Good demand; core mechanical more stable."
    },
    {
        "year": 2021,
        "campus": "Chennai",
        "branch": "Mechanical (Automotive)",
        "category": "Category 3",
        "rank_range": [
            65,
            22640
        ],
        "seats": 40,
        "filled": 35,
        "notes": "Good demand; core mechanical more stable."
    },
    {
        "year": 2021,
        "campus": "Chennai",
        "branch": "Mechanical (Automotive)",
        "category": "Category 4",
        "rank_range": [
            65,
            32200
        ],
        "seats": 40,
        "filled": 36,
        "notes": "Good demand; core mechanical more stable."
    },
    {
        "year": 2021,
        "campus": "Chennai",
        "branch": "Mechanical (Automotive)",
        "category": "Category 5",
        "rank_range": [
            65,
            41760
        ],
        "seats": 40,
        "filled": 36,
        "notes": "Good demand; core mechanical more stable."
    },
    {
        "year": 2021,
        "campus": "Chennai",
        "branch": "Biotechnology",
        "category": "Category 1",
        "rank_range": [
            1,
            60000
        ],
        "seats": 45,
        "filled": 40,
        "notes": "Niche branch; moderate demand."
    },
    {
        "year": 2021,
        "campus": "Chennai",
        "branch": "Biotechnology",
        "category": "Category 2",
        "rank_range": [
            45,
            108000
        ],
        "seats": 45,
        "filled": 42,
        "notes": "Niche branch; moderate demand."
    },
    {
        "year": 2021,
        "campus": "Chennai",
        "branch": "Biotechnology",
        "category": "Category 3",
        "rank_range": [
            45,
            204000
        ],
        "seats": 45,
        "filled": 42,
        "notes": "Niche branch; moderate demand."
    },
    {
        "year": 2021,
        "campus": "Chennai",
        "branch": "Biotechnology",
        "category": "Category 4",
        "rank_range": [
            45,
            300000
        ],
        "seats": 45,
        "filled": 43,
        "notes": "Niche branch; moderate demand."
    },
    {
        "year": 2021,
        "campus": "Chennai",
        "branch": "Biotechnology",
        "category": "Category 5",
        "rank_range": [
            45,
            390150
        ],
        "seats": 45,
        "filled": 43,
        "notes": "Niche branch; moderate demand."
    },
    {
        "year": 2021,
        "campus": "VIT-AP",
        "branch": "Computer Science and Engineering (CSE)",
        "category": "Category 1",
        "rank_range": [
            1,
            4088
        ],
        "seats": 180,
        "filled": 157,
        "notes": "Highly competitive; specialisations slightly less competitive than core."
    },
    {
        "year": 2021,
        "campus": "VIT-AP",
        "branch": "Computer Science and Engineering (CSE)",
        "category": "Category 2",
        "rank_range": [
            40,
            7368
        ],
        "seats": 180,
        "filled": 154,
        "notes": "Highly competitive; specialisations slightly less competitive than core."
    },
    {
        "year": 2021,
        "campus": "VIT-AP",
        "branch": "Computer Science and Engineering (CSE)",
        "category": "Category 3",
        "rank_range": [
            20,
            14200
        ],
        "seats": 180,
        "filled": 160,
        "notes": "Highly competitive; specialisations slightly less competitive than core."
    },
    {
        "year": 2021,
        "campus": "VIT-AP",
        "branch": "Computer Science and Engineering (CSE)",
        "category": "Category 4",
        "rank_range": [
            20,
            20360
        ],
        "seats": 180,
        "filled": 149,
        "notes": "Highly competitive; specialisations slightly less competitive than core."
    },
    {
        "year": 2021,
        "campus": "VIT-AP",
        "branch": "Computer Science and Engineering (CSE)",
        "category": "Category 5",
        "rank_range": [
            20,
            26472
        ],
        "seats": 180,
        "filled": 157,
        "notes": "Highly competitive; specialisations slightly less competitive than core."
    },
    {
        "year": 2021,
        "campus": "VIT-AP",
        "branch": "CSE (AI/ML)",
        "category": "Category 1",
        "rank_range": [
            1,
            10188
        ],
        "seats": 40,
        "filled": 36,
        "notes": "Highly competitive; specialisations slightly less competitive than core."
    },
    {
        "year": 2021,
        "campus": "VIT-AP",
        "branch": "CSE (AI/ML)",
        "category": "Category 2",
        "rank_range": [
            101,
            18444
        ],
        "seats": 40,
        "filled": 38,
        "notes": "Highly competitive; specialisations slightly less competitive than core."
    },
    {
        "year": 2021,
        "campus": "VIT-AP",
        "branch": "CSE (AI/ML)",
        "category": "Category 3",
        "rank_range": [
            101,
            35400
        ],
        "seats": 40,
        "filled": 37,
        "notes": "Highly competitive; specialisations slightly less competitive than core."
    },
    {
        "year": 2021,
        "campus": "VIT-AP",
        "branch": "CSE (AI/ML)",
        "category": "Category 4",
        "rank_range": [
            101,
            50400
        ],
        "seats": 40,
        "filled": 37,
        "notes": "Highly competitive; specialisations slightly less competitive than core."
    },
    {
        "year": 2021,
        "campus": "VIT-AP",
        "branch": "CSE (AI/ML)",
        "category": "Category 5",
        "rank_range": [
            101,
            65400
        ],
        "seats": 40,
        "filled": 40,
        "notes": "Highly competitive; specialisations slightly less competitive than core."
    },
    {
        "year": 2021,
        "campus": "VIT-AP",
        "branch": "CSE (Data Science)",
        "category": "Category 1",
        "rank_range": [
            1,
            10188
        ],
        "seats": 40,
        "filled": 36,
        "notes": "Highly competitive; specialisations slightly less competitive than core."
    },
    {
        "year": 2021,
        "campus": "VIT-AP",
        "branch": "CSE (Data Science)",
        "category": "Category 2",
        "rank_range": [
            101,
            18444
        ],
        "seats": 40,
        "filled": 35,
        "notes": "Highly competitive; specialisations slightly less competitive than core."
    },
    {
        "year": 2021,
        "campus": "VIT-AP",
        "branch": "CSE (Data Science)",
        "category": "Category 3",
        "rank_range": [
            101,
            35400
        ],
        "seats": 40,
        "filled": 36,
        "notes": "Highly competitive; specialisations slightly less competitive than core."
    },
    {
        "year": 2021,
        "campus": "VIT-AP",
        "branch": "CSE (Data Science)",
        "category": "Category 4",
        "rank_range": [
            101,
            50400
        ],
        "seats": 40,
        "filled": 39,
        "notes": "Highly competitive; specialisations slightly less competitive than core."
    },
    {
        "year": 2021,
        "campus": "VIT-AP",
        "branch": "CSE (Data Science)",
        "category": "Category 5",
        "rank_range": [
            101,
            65400
        ],
        "seats": 40,
        "filled": 39,
        "notes": "Highly competitive; specialisations slightly less competitive than core."
    },
    {
        "year": 2021,
        "campus": "VIT-AP",
        "branch": "CSE (IoT)",
        "category": "Category 1",
        "rank_range": [
            1,
            6812
        ],
        "seats": 30,
        "filled": 27,
        "notes": "Highly competitive; specialisations slightly less competitive than core."
    },
    {
        "year": 2021,
        "campus": "VIT-AP",
        "branch": "CSE (IoT)",
        "category": "Category 2",
        "rank_range": [
            68,
            12240
        ],
        "seats": 30,
        "filled": 26,
        "notes": "Highly competitive; specialisations slightly less competitive than core."
    },
    {
        "year": 2021,
        "campus": "VIT-AP",
        "branch": "CSE (IoT)",
        "category": "Category 3",
        "rank_range": [
            68,
            22360
        ],
        "seats": 30,
        "filled": 26,
        "notes": "Highly competitive; specialisations slightly less competitive than core."
    },
    {
        "year": 2021,
        "campus": "VIT-AP",
        "branch": "CSE (IoT)",
        "category": "Category 4",
        "rank_range": [
            68,
            31800
        ],
        "seats": 30,
        "filled": 28,
        "notes": "Highly competitive; specialisations slightly less competitive than core."
    },
    {
        "year": 2021,
        "campus": "VIT-AP",
        "branch": "CSE (IoT)",
        "category": "Category 5",
        "rank_range": [
            68,
            41220
        ],
        "seats": 30,
        "filled": 26,
        "notes": "Highly competitive; specialisations slightly less competitive than core."
    },
    {
        "year": 2021,
        "campus": "VIT-AP",
        "branch": "CSE (Cyber Security)",
        "category": "Category 1",
        "rank_range": [
            1,
            6812
        ],
        "seats": 30,
        "filled": 27,
        "notes": "Highly competitive; specialisations slightly less competitive than core."
    },
    {
        "year": 2021,
        "campus": "VIT-AP",
        "branch": "CSE (Cyber Security)",
        "category": "Category 2",
        "rank_range": [
            68,
            12240
        ],
        "seats": 30,
        "filled": 28,
        "notes": "Highly competitive; specialisations slightly less competitive than core."
    },
    {
        "year": 2021,
        "campus": "VIT-AP",
        "branch": "CSE (Cyber Security)",
        "category": "Category 3",
        "rank_range": [
            68,
            22360
        ],
        "seats": 30,
        "filled": 25,
        "notes": "Highly competitive; specialisations slightly less competitive than core."
    },
    {
        "year": 2021,
        "campus": "VIT-AP",
        "branch": "CSE (Cyber Security)",
        "category": "Category 4",
        "rank_range": [
            68,
            31800
        ],
        "seats": 30,
        "filled": 28,
        "notes": "Highly competitive; specialisations slightly less competitive than core."
    },
    {
        "year": 2021,
        "campus": "VIT-AP",
        "branch": "CSE (Cyber Security)",
        "category": "Category 5",
        "rank_range": [
            68,
            41220
        ],
        "seats": 30,
        "filled": 27,
        "notes": "Highly competitive; specialisations slightly less competitive than core."
    },
    {
        "year": 2021,
        "campus": "VIT-AP",
        "branch": "CSE (Blockchain)",
        "category": "Category 1",
        "rank_range": [
            1,
            7604
        ],
        "seats": 20,
        "filled": 18,
        "notes": "Highly competitive; specialisations slightly less competitive than core."
    },
    {
        "year": 2021,
        "campus": "VIT-AP",
        "branch": "CSE (Blockchain)",
        "category": "Category 2",
        "rank_range": [
            76,
            13704
        ],
        "seats": 20,
        "filled": 18,
        "notes": "Highly competitive; specialisations slightly less competitive than core."
    },
    {
        "year": 2021,
        "campus": "VIT-AP",
        "branch": "CSE (Blockchain)",
        "category": "Category 3",
        "rank_range": [
            76,
            26360
        ],
        "seats": 20,
        "filled": 17,
        "notes": "Highly competitive; specialisations slightly less competitive than core."
    },
    {
        "year": 2021,
        "campus": "VIT-AP",
        "branch": "CSE (Blockchain)",
        "category": "Category 4",
        "rank_range": [
            76,
            37500
        ],
        "seats": 20,
        "filled": 18,
        "notes": "Highly competitive; specialisations slightly less competitive than core."
    },
    {
        "year": 2021,
        "campus": "VIT-AP",
        "branch": "CSE (Blockchain)",
        "category": "Category 5",
        "rank_range": [
            76,
            48630
        ],
        "seats": 20,
        "filled": 19,
        "notes": "Highly competitive; specialisations slightly less competitive than core."
    },
    {
        "year": 2021,
        "campus": "VIT-AP",
        "branch": "Electronics and Communication Engineering (ECE)",
        "category": "Category 1",
        "rank_range": [
            1,
            24600
        ],
        "seats": 140,
        "filled": 120,
        "notes": "Moderately competitive; VLSI is sought after."
    },
    {
        "year": 2021,
        "campus": "VIT-AP",
        "branch": "Electronics and Communication Engineering (ECE)",
        "category": "Category 2",
        "rank_range": [
            140,
            44280
        ],
        "seats": 140,
        "filled": 119,
        "notes": "Moderately competitive; VLSI is sought after."
    },
    {
        "year": 2021,
        "campus": "VIT-AP",
        "branch": "Electronics and Communication Engineering (ECE)",
        "category": "Category 3",
        "rank_range": [
            140,
            85560
        ],
        "seats": 140,
        "filled": 121,
        "notes": "Moderately competitive; VLSI is sought after."
    },
    {
        "year": 2021,
        "campus": "VIT-AP",
        "branch": "Electronics and Communication Engineering (ECE)",
        "category": "Category 4",
        "rank_range": [
            140,
            122400
        ],
        "seats": 140,
        "filled": 119,
        "notes": "Moderately competitive; VLSI is sought after."
    },
    {
        "year": 2021,
        "campus": "VIT-AP",
        "branch": "Electronics and Communication Engineering (ECE)",
        "category": "Category 5",
        "rank_range": [
            140,
            159300
        ],
        "seats": 140,
        "filled": 121,
        "notes": "Moderately competitive; VLSI is sought after."
    },
    {
        "year": 2021,
        "campus": "VIT-AP",
        "branch": "ECE (VLSI)",
        "category": "Category 1",
        "rank_range": [
            1,
            8200
        ],
        "seats": 40,
        "filled": 36,
        "notes": "Moderately competitive; VLSI is sought after."
    },
    {
        "year": 2021,
        "campus": "VIT-AP",
        "branch": "ECE (VLSI)",
        "category": "Category 2",
        "rank_range": [
            82,
            14792
        ],
        "seats": 40,
        "filled": 36,
        "notes": "Moderately competitive; VLSI is sought after."
    },
    {
        "year": 2021,
        "campus": "VIT-AP",
        "branch": "ECE (VLSI)",
        "category": "Category 3",
        "rank_range": [
            82,
            28320
        ],
        "seats": 40,
        "filled": 39,
        "notes": "Moderately competitive; VLSI is sought after."
    },
    {
        "year": 2021,
        "campus": "VIT-AP",
        "branch": "ECE (VLSI)",
        "category": "Category 4",
        "rank_range": [
            82,
            40200
        ],
        "seats": 40,
        "filled": 38,
        "notes": "Moderately competitive; VLSI is sought after."
    },
    {
        "year": 2021,
        "campus": "VIT-AP",
        "branch": "ECE (VLSI)",
        "category": "Category 5",
        "rank_range": [
            82,
            52160
        ],
        "seats": 40,
        "filled": 37,
        "notes": "Moderately competitive; VLSI is sought after."
    },
    {
        "year": 2021,
        "campus": "VIT-AP",
        "branch": "ECE (BioMedical)",
        "category": "Category 1",
        "rank_range": [
            1,
            6120
        ],
        "seats": 30,
        "filled": 27,
        "notes": "Moderately competitive; VLSI is sought after."
    },
    {
        "year": 2021,
        "campus": "VIT-AP",
        "branch": "ECE (BioMedical)",
        "category": "Category 2",
        "rank_range": [
            61,
            11040
        ],
        "seats": 30,
        "filled": 26,
        "notes": "Moderately competitive; VLSI is sought after."
    },
    {
        "year": 2021,
        "campus": "VIT-AP",
        "branch": "ECE (BioMedical)",
        "category": "Category 3",
        "rank_range": [
            61,
            21120
        ],
        "seats": 30,
        "filled": 27,
        "notes": "Moderately competitive; VLSI is sought after."
    },
    {
        "year": 2021,
        "campus": "VIT-AP",
        "branch": "ECE (BioMedical)",
        "category": "Category 4",
        "rank_range": [
            61,
            30300
        ],
        "seats": 30,
        "filled": 27,
        "notes": "Moderately competitive; VLSI is sought after."
    },
    {
        "year": 2021,
        "campus": "VIT-AP",
        "branch": "ECE (BioMedical)",
        "category": "Category 5",
        "rank_range": [
            61,
            39530
        ],
        "seats": 30,
        "filled": 29,
        "notes": "Moderately competitive; VLSI is sought after."
    },
    {
        "year": 2021,
        "campus": "VIT-AP",
        "branch": "Civil Engineering",
        "category": "Category 1",
        "rank_range": [
            1,
            50000
        ],
        "seats": 80,
        "filled": 70,
        "notes": "Lower demand compared to CSE/ECE; closing ranks later."
    },
    {
        "year": 2021,
        "campus": "VIT-AP",
        "branch": "Civil Engineering",
        "category": "Category 2",
        "rank_range": [
            80,
            90000
        ],
        "seats": 80,
        "filled": 71,
        "notes": "Lower demand compared to CSE/ECE; closing ranks later."
    },
    {
        "year": 2021,
        "campus": "VIT-AP",
        "branch": "Civil Engineering",
        "category": "Category 3",
        "rank_range": [
            80,
            173600
        ],
        "seats": 80,
        "filled": 73,
        "notes": "Lower demand compared to CSE/ECE; closing ranks later."
    },
    {
        "year": 2021,
        "campus": "VIT-AP",
        "branch": "Civil Engineering",
        "category": "Category 4",
        "rank_range": [
            80,
            245600
        ],
        "seats": 80,
        "filled": 68,
        "notes": "Lower demand compared to CSE/ECE; closing ranks later."
    },
    {
        "year": 2021,
        "campus": "VIT-AP",
        "branch": "Civil Engineering",
        "category": "Category 5",
        "rank_range": [
            80,
            319440
        ],
        "seats": 80,
        "filled": 69,
        "notes": "Lower demand compared to CSE/ECE; closing ranks later."
    },
    {
        "year": 2021,
        "campus": "VIT-AP",
        "branch": "Electrical and Electronics Engineering (EEE)",
        "category": "Category 1",
        "rank_range": [
            1,
            36000
        ],
        "seats": 80,
        "filled": 70,
        "notes": "Lower demand compared to CSE/ECE; closing ranks later."
    },
    {
        "year": 2021,
        "campus": "VIT-AP",
        "branch": "Electrical and Electronics Engineering (EEE)",
        "category": "Category 2",
        "rank_range": [
            80,
            64800
        ],
        "seats": 80,
        "filled": 68,
        "notes": "Lower demand compared to CSE/ECE; closing ranks later."
    },
    {
        "year": 2021,
        "campus": "VIT-AP",
        "branch": "Electrical and Electronics Engineering (EEE)",
        "category": "Category 3",
        "rank_range": [
            80,
            125200
        ],
        "seats": 80,
        "filled": 71,
        "notes": "Lower demand compared to CSE/ECE; closing ranks later."
    },
    {
        "year": 2021,
        "campus": "VIT-AP",
        "branch": "Electrical and Electronics Engineering (EEE)",
        "category": "Category 4",
        "rank_range": [
            80,
            173600
        ],
        "seats": 80,
        "filled": 67,
        "notes": "Lower demand compared to CSE/ECE; closing ranks later."
    },
    {
        "year": 2021,
        "campus": "VIT-AP",
        "branch": "Electrical and Electronics Engineering (EEE)",
        "category": "Category 5",
        "rank_range": [
            80,
            225600
        ],
        "seats": 80,
        "filled": 68,
        "notes": "Lower demand compared to CSE/ECE; closing ranks later."
    },
    {
        "year": 2021,
        "campus": "VIT-AP",
        "branch": "Electrical Engineering (EE)",
        "category": "Category 1",
        "rank_range": [
            1,
            24000
        ],
        "seats": 60,
        "filled": 55,
        "notes": "Lower demand compared to CSE/ECE; closing ranks later."
    },
    {
        "year": 2021,
        "campus": "VIT-AP",
        "branch": "Electrical Engineering (EE)",
        "category": "Category 2",
        "rank_range": [
            60,
            43200
        ],
        "seats": 60,
        "filled": 53,
        "notes": "Lower demand compared to CSE/ECE; closing ranks later."
    },
    {
        "year": 2021,
        "campus": "VIT-AP",
        "branch": "Electrical Engineering (EE)",
        "category": "Category 3",
        "rank_range": [
            60,
            83400
        ],
        "seats": 60,
        "filled": 51,
        "notes": "Lower demand compared to CSE/ECE; closing ranks later."
    },
    {
        "year": 2021,
        "campus": "VIT-AP",
        "branch": "Electrical Engineering (EE)",
        "category": "Category 4",
        "rank_range": [
            60,
            115000
        ],
        "seats": 60,
        "filled": 47,
        "notes": "Lower demand compared to CSE/ECE; closing ranks later."
    },
    {
        "year": 2021,
        "campus": "VIT-AP",
        "branch": "Electrical Engineering (EE)",
        "category": "Category 5",
        "rank_range": [
            60,
            149450
        ],
        "seats": 60,
        "filled": 48,
        "notes": "Lower demand compared to CSE/ECE; closing ranks later."
    },
    {
        "year": 2021,
        "campus": "VIT-AP",
        "branch": "Mechanical Engineering (core)",
        "category": "Category 1",
        "rank_range": [
            1,
            40000
        ],
        "seats": 120,
        "filled": 108,
        "notes": "Good demand; core mechanical more stable."
    },
    {
        "year": 2021,
        "campus": "VIT-AP",
        "branch": "Mechanical Engineering (core)",
        "category": "Category 2",
        "rank_range": [
            120,
            72000
        ],
        "seats": 120,
        "filled": 113,
        "notes": "Good demand; core mechanical more stable."
    },
    {
        "year": 2021,
        "campus": "VIT-AP",
        "branch": "Mechanical Engineering (core)",
        "category": "Category 3",
        "rank_range": [
            120,
            130400
        ],
        "seats": 120,
        "filled": 109,
        "notes": "Good demand; core mechanical more stable."
    },
    {
        "year": 2021,
        "campus": "VIT-AP",
        "branch": "Mechanical Engineering (core)",
        "category": "Category 4",
        "rank_range": [
            120,
            180000
        ],
        "seats": 120,
        "filled": 104,
        "notes": "Good demand; core mechanical more stable."
    },
    {
        "year": 2021,
        "campus": "VIT-AP",
        "branch": "Mechanical Engineering (core)",
        "category": "Category 5",
        "rank_range": [
            120,
            234000
        ],
        "seats": 120,
        "filled": 103,
        "notes": "Good demand; core mechanical more stable."
    },
    {
        "year": 2021,
        "campus": "VIT-AP",
        "branch": "Mechanical (Automotive)",
        "category": "Category 1",
        "rank_range": [
            1,
            8200
        ],
        "seats": 40,
        "filled": 34,
        "notes": "Good demand; core mechanical more stable."
    },
    {
        "year": 2021,
        "campus": "VIT-AP",
        "branch": "Mechanical (Automotive)",
        "category": "Category 2",
        "rank_range": [
            82,
            14792
        ],
        "seats": 40,
        "filled": 36,
        "notes": "Good demand; core mechanical more stable."
    },
    {
        "year": 2021,
        "campus": "VIT-AP",
        "branch": "Mechanical (Automotive)",
        "category": "Category 3",
        "rank_range": [
            82,
            28320
        ],
        "seats": 40,
        "filled": 35,
        "notes": "Good demand; core mechanical more stable."
    },
    {
        "year": 2021,
        "campus": "VIT-AP",
        "branch": "Mechanical (Automotive)",
        "category": "Category 4",
        "rank_range": [
            82,
            40200
        ],
        "seats": 40,
        "filled": 37,
        "notes": "Good demand; core mechanical more stable."
    },
    {
        "year": 2021,
        "campus": "VIT-AP",
        "branch": "Mechanical (Automotive)",
        "category": "Category 5",
        "rank_range": [
            82,
            52160
        ],
        "seats": 40,
        "filled": 36,
        "notes": "Good demand; core mechanical more stable."
    },
    {
        "year": 2021,
        "campus": "VIT-AP",
        "branch": "Biotechnology",
        "category": "Category 1",
        "rank_range": [
            1,
            90000
        ],
        "seats": 40,
        "filled": 35,
        "notes": "Niche branch; moderate demand."
    },
    {
        "year": 2021,
        "campus": "VIT-AP",
        "branch": "Biotechnology",
        "category": "Category 2",
        "rank_range": [
            40,
            162000
        ],
        "seats": 40,
        "filled": 37,
        "notes": "Niche branch; moderate demand."
    },
    {
        "year": 2021,
        "campus": "VIT-AP",
        "branch": "Biotechnology",
        "category": "Category 3",
        "rank_range": [
            40,
            306000
        ],
        "seats": 40,
        "filled": 37,
        "notes": "Niche branch; moderate demand."
    },
    {
        "year": 2021,
        "campus": "VIT-AP",
        "branch": "Biotechnology",
        "category": "Category 4",
        "rank_range": [
            40,
            450000
        ],
        "seats": 40,
        "filled": 38,
        "notes": "Niche branch; moderate demand."
    },
    {
        "year": 2021,
        "campus": "VIT-AP",
        "branch": "Biotechnology",
        "category": "Category 5",
        "rank_range": [
            40,
            585300
        ],
        "seats": 40,
        "filled": 36,
        "notes": "Niche branch; moderate demand."
    },
    {
        "year": 2021,
        "campus": "Bhopal",
        "branch": "Computer Science and Engineering (CSE)",
        "category": "Category 1",
        "rank_range": [
            1,
            5152
        ],
        "seats": 120,
        "filled": 103,
        "notes": "Highly competitive; specialisations slightly less competitive than core."
    },
    {
        "year": 2021,
        "campus": "Bhopal",
        "branch": "Computer Science and Engineering (CSE)",
        "category": "Category 2",
        "rank_range": [
            51,
            9280
        ],
        "seats": 120,
        "filled": 111,
        "notes": "Highly competitive; specialisations slightly less competitive than core."
    },
    {
        "year": 2021,
        "campus": "Bhopal",
        "branch": "Computer Science and Engineering (CSE)",
        "category": "Category 3",
        "rank_range": [
            25,
            17900
        ],
        "seats": 120,
        "filled": 101,
        "notes": "Highly competitive; specialisations slightly less competitive than core."
    },
    {
        "year": 2021,
        "campus": "Bhopal",
        "branch": "Computer Science and Engineering (CSE)",
        "category": "Category 4",
        "rank_range": [
            25,
            25616
        ],
        "seats": 120,
        "filled": 110,
        "notes": "Highly competitive; specialisations slightly less competitive than core."
    },
    {
        "year": 2021,
        "campus": "Bhopal",
        "branch": "Computer Science and Engineering (CSE)",
        "category": "Category 5",
        "rank_range": [
            25,
            33168
        ],
        "seats": 120,
        "filled": 112,
        "notes": "Highly competitive; specialisations slightly less competitive than core."
    },
    {
        "year": 2021,
        "campus": "Bhopal",
        "branch": "CSE (AI/ML)",
        "category": "Category 1",
        "rank_range": [
            1,
            12880
        ],
        "seats": 30,
        "filled": 27,
        "notes": "Highly competitive; specialisations slightly less competitive than core."
    },
    {
        "year": 2021,
        "campus": "Bhopal",
        "branch": "CSE (AI/ML)",
        "category": "Category 2",
        "rank_range": [
            128,
            23344
        ],
        "seats": 30,
        "filled": 26,
        "notes": "Highly competitive; specialisations slightly less competitive than core."
    },
    {
        "year": 2021,
        "campus": "Bhopal",
        "branch": "CSE (AI/ML)",
        "category": "Category 3",
        "rank_range": [
            128,
            44800
        ],
        "seats": 30,
        "filled": 27,
        "notes": "Highly competitive; specialisations slightly less competitive than core."
    },
    {
        "year": 2021,
        "campus": "Bhopal",
        "branch": "CSE (AI/ML)",
        "category": "Category 4",
        "rank_range": [
            128,
            63840
        ],
        "seats": 30,
        "filled": 29,
        "notes": "Highly competitive; specialisations slightly less competitive than core."
    },
    {
        "year": 2021,
        "campus": "Bhopal",
        "branch": "CSE (AI/ML)",
        "category": "Category 5",
        "rank_range": [
            128,
            82800
        ],
        "seats": 30,
        "filled": 30,
        "notes": "Highly competitive; specialisations slightly less competitive than core."
    },
    {
        "year": 2021,
        "campus": "Bhopal",
        "branch": "CSE (Data Science)",
        "category": "Category 1",
        "rank_range": [
            1,
            12880
        ],
        "seats": 30,
        "filled": 26,
        "notes": "Highly competitive; specialisations slightly less competitive than core."
    },
    {
        "year": 2021,
        "campus": "Bhopal",
        "branch": "CSE (Data Science)",
        "category": "Category 2",
        "rank_range": [
            128,
            23344
        ],
        "seats": 30,
        "filled": 27,
        "notes": "Highly competitive; specialisations slightly less competitive than core."
    },
    {
        "year": 2021,
        "campus": "Bhopal",
        "branch": "CSE (Data Science)",
        "category": "Category 3",
        "rank_range": [
            128,
            44800
        ],
        "seats": 30,
        "filled": 28,
        "notes": "Highly competitive; specialisations slightly less competitive than core."
    },
    {
        "year": 2021,
        "campus": "Bhopal",
        "branch": "CSE (Data Science)",
        "category": "Category 4",
        "rank_range": [
            128,
            63840
        ],
        "seats": 30,
        "filled": 28,
        "notes": "Highly competitive; specialisations slightly less competitive than core."
    },
    {
        "year": 2021,
        "campus": "Bhopal",
        "branch": "CSE (Data Science)",
        "category": "Category 5",
        "rank_range": [
            128,
            82800
        ],
        "seats": 30,
        "filled": 27,
        "notes": "Highly competitive; specialisations slightly less competitive than core."
    },
    {
        "year": 2021,
        "campus": "Bhopal",
        "branch": "CSE (IoT)",
        "category": "Category 1",
        "rank_range": [
            1,
            8600
        ],
        "seats": 20,
        "filled": 18,
        "notes": "Highly competitive; specialisations slightly less competitive than core."
    },
    {
        "year": 2021,
        "campus": "Bhopal",
        "branch": "CSE (IoT)",
        "category": "Category 2",
        "rank_range": [
            86,
            15480
        ],
        "seats": 20,
        "filled": 17,
        "notes": "Highly competitive; specialisations slightly less competitive than core."
    },
    {
        "year": 2021,
        "campus": "Bhopal",
        "branch": "CSE (IoT)",
        "category": "Category 3",
        "rank_range": [
            86,
            28160
        ],
        "seats": 20,
        "filled": 18,
        "notes": "Highly competitive; specialisations slightly less competitive than core."
    },
    {
        "year": 2021,
        "campus": "Bhopal",
        "branch": "CSE (IoT)",
        "category": "Category 4",
        "rank_range": [
            86,
            39900
        ],
        "seats": 20,
        "filled": 16,
        "notes": "Highly competitive; specialisations slightly less competitive than core."
    },
    {
        "year": 2021,
        "campus": "Bhopal",
        "branch": "CSE (IoT)",
        "category": "Category 5",
        "rank_range": [
            86,
            51660
        ],
        "seats": 20,
        "filled": 16,
        "notes": "Highly competitive; specialisations slightly less competitive than core."
    },
    {
        "year": 2021,
        "campus": "Bhopal",
        "branch": "CSE (Cyber Security)",
        "category": "Category 1",
        "rank_range": [
            1,
            8600
        ],
        "seats": 20,
        "filled": 17,
        "notes": "Highly competitive; specialisations slightly less competitive than core."
    },
    {
        "year": 2021,
        "campus": "Bhopal",
        "branch": "CSE (Cyber Security)",
        "category": "Category 2",
        "rank_range": [
            86,
            15480
        ],
        "seats": 20,
        "filled": 18,
        "notes": "Highly competitive; specialisations slightly less competitive than core."
    },
    {
        "year": 2021,
        "campus": "Bhopal",
        "branch": "CSE (Cyber Security)",
        "category": "Category 3",
        "rank_range": [
            86,
            28160
        ],
        "seats": 20,
        "filled": 16,
        "notes": "Highly competitive; specialisations slightly less competitive than core."
    },
    {
        "year": 2021,
        "campus": "Bhopal",
        "branch": "CSE (Cyber Security)",
        "category": "Category 4",
        "rank_range": [
            86,
            39900
        ],
        "seats": 20,
        "filled": 17,
        "notes": "Highly competitive; specialisations slightly less competitive than core."
    },
    {
        "year": 2021,
        "campus": "Bhopal",
        "branch": "CSE (Cyber Security)",
        "category": "Category 5",
        "rank_range": [
            86,
            51660
        ],
        "seats": 20,
        "filled": 16,
        "notes": "Highly competitive; specialisations slightly less competitive than core."
    },
    {
        "year": 2021,
        "campus": "Bhopal",
        "branch": "CSE (Blockchain)",
        "category": "Category 1",
        "rank_range": [
            1,
            9608
        ],
        "seats": 10,
        "filled": 9,
        "notes": "Highly competitive; specialisations slightly less competitive than core."
    }
    # // ... the dataset continues with the same structure for all campuses, branches, categories for years 2021 through 2025 (total ~1500 records)
]


def seed_database(db_service: MongoDBService):
    print("\n" + "="*60)
    print("SEEDING YEAR-WISE CUTOFF DATA")
    print("="*60)
    
    # Initialize embedding model for vector search
    initialize_embedding_model(EMBEDDING_MODEL_NAME)
    
    # Generate embeddings for the cutoff descriptions
    descriptions = [
        f"{c['branch']} at {c['campus']} campus, {c['category']} - Year {c['year']}"
        for c in SAMPLE_CUTOFFS
    ]
    print(f"\nGenerating embeddings for {len(descriptions)} cutoff entries...")
    embeddings = generate_batch_embeddings(descriptions)
    
    # Add embeddings to cutoff data
    for cutoff, embedding in zip(SAMPLE_CUTOFFS, embeddings):
        cutoff_data = {
            **cutoff,
            "embedding": embedding,
            "last_updated": datetime.utcnow()
        }
        
        doc_id = db_service.add_cutoff(cutoff_data)
        if doc_id:
            print(f"✅ Added {cutoff['year']} cutoff: {cutoff['branch']} - {cutoff['campus']}")
        else:
            print(f"❌ Failed to add {cutoff['year']} cutoff: {cutoff['branch']} - {cutoff['campus']}")
    
    print("\n✅ Database seeding complete!")

def main():
    print("\n" + "="*70)
    print("VIT COUNSELING ASSISTANT - YEAR-WISE DATABASE SEEDING")
    print("="*70)
    
    db_service = MongoDBService(MONGODB_URL)
    
    if not db_service.is_connected():
        print("\n❌ Error: Could not connect to MongoDB.")
        print("Please make sure MongoDB is running locally and try again.")
        return
    
    print("\nThis script will add year-wise cutoff data to MongoDB.")
    print("This includes data from 2023-2025 for trend analysis.")
    response = input("Do you want to proceed? (yes/no): ")
    
    if response.lower() != 'yes':
        print("Seeding cancelled.")
        return
    
    seed_database(db_service)
    
    # Display sample trend analysis
    print("\nTesting trend analysis...")
    trends = db_service.get_year_wise_trends(
        branch="Computer Science and Engineering (CSE)",
        campus="Vellore",
        category="Category 1"
    )
    
    if trends:
        print("\nSample Trend Analysis for CSE at Vellore:")
        for trend in trends.get("trends", []):
            print(f"Year {trend['year']}: Range {trend['min_rank']}-{trend['max_rank']}")
            if "yoy_change" in trend:
                print(f"Year-over-year change: {trend['yoy_change']}%")
    
    # Test prediction
    prediction = db_service.predict_rank_range(
        branch="Computer Science and Engineering (CSE)",
        campus="Vellore",
        category="Category 1"
    )
    
    if prediction:
        print(f"\nPredicted 2026 Rank Range:")
        print(f"Min Rank: {prediction['predicted_min_rank']}")
        print(f"Max Rank: {prediction['predicted_max_rank']}")
        print(f"Confidence: {prediction['confidence']}")
        print(f"Trend: {prediction['trend']} ({prediction['avg_yearly_change']}% per year)")
    
    print("\n" + "="*70)
    print("SEEDING AND TESTING COMPLETE!")
    print("="*70)

if __name__ == "__main__":
    main()