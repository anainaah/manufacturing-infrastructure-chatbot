# manufacturing-infrastructure-chatbot
InfraChat: Natural Language Interface for Manufacturing Infrastructure
InfraChat is a state-of-the-art industrial management platform that bridges the gap between complex manufacturing data and human operators. By leveraging Natural Language Processing (NLP) and Predictive Maintenance Intelligence, users can interact with their factory infrastructure using plain English commands.

🚀 Key Features
Natural Language Interface (NLI): Ask complex questions like "What is the RPM of Machine L47181?" and get instant, specific data retrieval.

Intelligent Logic: Implements rapidfuzz for typo-tolerant command recognition and multi-variable extraction from single sentences.

Predictive Maintenance Dashboard: Real-time visualization of machine health, failure distributions, and operational KPIs (RPM, Torque, Tool Wear).

Industrial Robustness: Advanced error handling with pattern-based Machine ID validation and technical record auditing.
Cinematic UI/UX: High-end industrial aesthetic with "Breathing Glow" interactive elements and a fully responsive layout.
🛠️ Technical Stack
Backend: Python / Flask
Data Intelligence: Pandas (Data analysis), RapidFuzz (String matching logic)
Frontend: HTML5, CSS3, JavaScript
Icons/Styling: FontAwesome, Google Fonts (Inter/Orbitron)
Dataset: AI4I 2020 Predictive Maintenance Dataset
🧠 Smart Chatbot Logic
The chatbot uses a multi-layer heuristic approach to understand user intent:
Fuzzy String Matching: Map various human phrases to core system commands.
Product ID Pattern Matching: Detects serialized machine codes (L/M/H) across the dataset.
Contextual Awareness: Remembers conversation state to handle follow-up questions intelligently.
