# InfraChat

**Natural Language Interface for Manufacturing Infrastructure**

InfraChat is an industrial management platform that bridges the gap between manufacturing data and human operators. By utilizing Natural Language Processing (NLP) and Predictive Maintenance Intelligence, users can interact with factory infrastructure via plain English commands.

## Features

- **Query by Product ID**: Query machine status using standard Product IDs (e.g., `L47181`).
- **Command Library**: Supports over 30 natural language commands for infrastructure management.
- **Analytics Dashboard**: Real-time charts, KPIs, and gauges for system monitoring.
- **Risk Scoring**: Categorizes machine health into four tiers: Safe, Elevated, High Warning, and Critical.
- **Fuzzy String Matching**: Uses Rapidfuzz to handle variations and typos in user input.
- **User Interface**: Includes a typing indicator and quick reply chips.

## Technical Stack

- **Backend**: Python, Flask
- **Data & NLP**: Pandas, Rapidfuzz
- **Frontend**: HTML5, CSS3, JavaScript, Chart.js

## Dataset

This project utilizes the [Machine Predictive Maintenance Classification](https://www.kaggle.com/) dataset from Kaggle to simulate industrial equipment health and failure modes.

## Installation

### Prerequisites

- Python 3.8+
- pip

### Setup Instructions

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/manufacturing-infrastructure-chatbot.git
   cd manufacturing-infrastructure-chatbot
   ```

2. Create and activate a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows use: venv\Scripts\activate
   ```

3. Install required dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Start the application:
   ```bash
   flask run
   ```

5. Access the application at `http://localhost:5000`.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.
