# VIT Chatbot with Database System (DBS)

An intelligent chatbot system designed to assist prospective students with VIT (Vellore Institute of Technology) admission queries, powered by a robust database backend.

## 📋 Overview

This project implements an AI-powered chatbot that helps students navigate the VIT admission process by providing accurate, real-time information about courses, eligibility criteria, admission procedures, campus facilities, and more. The system integrates with a database to store and retrieve structured information efficiently.

## ✨ Features

- **Intelligent Query Handling**: Natural language processing to understand and respond to student queries
- **Database Integration**: Persistent storage for admission data, FAQs, and user interactions
- **Multi-topic Support**: Handles queries about:
  - Admission procedures and eligibility
  - Course details and specializations
  - Fee structure and scholarships
  - Campus facilities and infrastructure
  - Placement statistics and opportunities
  - Hostel and accommodation information
- **24/7 Availability**: Automated responses without human intervention
- **Scalable Architecture**: Modular design for easy maintenance and updates

## 🏗️ Project Structure

```
VIT_CHATBOT_DBS/
├── admission-chatbot/      # Core chatbot implementation
├── models/                 # ML models and training data
├── services/               # Backend services and APIs
├── scripts/                # Utility scripts for deployment and maintenance
├── utils/                  # Helper functions and utilities
├── main.py                 # Application entry point
├── requirements.txt        # Python dependencies
└── .gitignore             # Git ignore rules
```

## 🚀 Getting Started

### Prerequisites

- Python 3.8 or higher
- pip (Python package manager)
- Database system (SQLite/PostgreSQL/MySQL)

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/vaibhavjain2005/VIT_CHATBOT_DBS.git
   cd VIT_CHATBOT_DBS
   ```

2. **Switch to the main branch**
   ```bash
   git checkout v3
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables**
   Create a `.env` file in the root directory with necessary configurations:
   ```env
   DATABASE_URL=your_database_url
   API_KEY=your_api_key
   SECRET_KEY=your_secret_key
   ```

5. **Initialize the database**
   ```bash
   python scripts/init_db.py
   ```

6. **Run the application**
   ```bash
   python main.py
   ```

## 💻 Usage

### Starting the Chatbot

```bash
python main.py
```

The chatbot will start and be ready to accept queries through the configured interface (web, CLI, or API).

### Example Queries

- "What is the eligibility criteria for B.Tech admission?"
- "Tell me about the Computer Science program"
- "What are the fee details for the academic year?"
- "How can I apply for scholarships?"
- "What are the placement statistics?"

## 🗄️ Database Schema

The system uses a relational database with the following key tables:

- **courses**: Course information, eligibility, and details
- **admissions**: Admission procedures and requirements
- **faqs**: Frequently asked questions and answers
- **chat_logs**: User interaction history
- **feedback**: User feedback and ratings

## 🛠️ Technology Stack

- **Backend**: Python
- **NLP/ML**: Natural Language Processing libraries
- **Database**: SQL-based DBMS
- **Framework**: (Flask/FastAPI - based on implementation)
- **Version Control**: Git

## 🤝 Contributing

Contributions are welcome! Please follow these steps:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

### Contributors

- [vaibhavjain2005](https://github.com/vaibhavjain2005) - Vaibhav Jain
- [ADRIVID-MISHRA](https://github.com/ADRIVID-MISHRA) - Ghost

## 📝 Development Roadmap

- [ ] Enhanced NLP capabilities with transformer models
- [ ] Multi-language support
- [ ] Voice interaction feature
- [ ] Mobile application integration
- [ ] Advanced analytics dashboard
- [ ] Integration with VIT admission portal API

## 🐛 Known Issues

Please check the [Issues](https://github.com/vaibhavjain2005/VIT_CHATBOT_DBS/issues) page for current bugs and feature requests.

## 📄 License

This project is available for educational and non-commercial use. Please contact the maintainers for commercial licensing.

## 📧 Contact

For questions, suggestions, or support:

- **Project Link**: [https://github.com/vaibhavjain2005/VIT_CHATBOT_DBS](https://github.com/vaibhavjain2005/VIT_CHATBOT_DBS)
- **Report Issues**: [GitHub Issues](https://github.com/vaibhavjain2005/VIT_CHATBOT_DBS/issues)

## 🙏 Acknowledgments

- VIT for inspiration and context
- Open-source NLP libraries and frameworks
- All contributors and testers

---

**Note**: This project is for educational purposes and is not officially affiliated with Vellore Institute of Technology (VIT).
