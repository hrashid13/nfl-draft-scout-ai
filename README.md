# NFL Draft Scout AI

An AI-powered scouting assistant for the 2026 NFL Draft, combining semantic search with advanced analytics to provide comprehensive prospect evaluations through natural language queries.

## Overview

NFL Draft Scout AI is a RAG (Retrieval-Augmented Generation) system that enables users to query over 500 NFL draft prospects using conversational language. The system combines vector database search with AI-powered analysis to deliver contextual insights based on player statistics, consensus rankings, and performance metrics.

[![Live Demo](https://img.shields.io/badge/Demo-nfldraftscoutai.org-green)](https://www.nfldraftscoutai.org)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](license)

## Features

- **Natural Language Queries**: Ask questions about prospects in plain English
- **Comprehensive Database**: 500 prospects from the 2026 NFL Draft class with 80.4% statistical coverage
- **Consensus Rankings**: Integrated data from five major draft services (NFL Mock Draft Database, PFF, CBS Sports, Tankathon, Fantasy Pros)
- **Team Intelligence**: Complete NFL team profiles including draft capital, positional needs, and roster analysis
- **Hybrid Search**: Combines semantic search with statistical re-ranking for optimal accuracy
- **Real-time Analysis**: Claude AI provides contextual analysis and comparisons
- **Temporal Tracking**: Monitor prospect momentum through all-star games and NFL combine

## Technology Stack

### Frontend
- React with Tailwind CSS
- Custom green-dominant color scheme
- Responsive design for desktop and mobile

### Backend
- Flask (Python 3.11)
- RESTful API architecture
- Serves both static files and API endpoints

### AI/ML
- ChromaDB vector database with sentence-transformer embeddings (all-MiniLM-L6-v2)
- Claude API (Haiku model) for natural language processing
- Hybrid query strategy: semantic search + statistical re-ranking

### Deployment
- Railway platform
- Custom domain via Squarespace DNS
- Git-based continuous deployment

## Dataset

### Prospect Coverage
- 500 total prospects in the 2026 NFL Draft class
- 402 players with complete statistical profiles
- 230 prospects with consensus rankings
- Temporal snapshots tracking pre/post all-star games and combine

### Data Sources
- Sports Reference for player statistics
- NFL Mock Draft Database, PFF, CBS Sports, Tankathon, Fantasy Pros for rankings
- Manual data collection for comprehensive skill position coverage

### Team Information
- All 32 NFL teams across 8 divisions
- Draft capital analysis
- Positional needs assessment
- Roster strengths and weaknesses
- Coaching staff details
- Scouting context

## Architecture

The system operates as a RAG application where:
1. User submits natural language query
2. ChromaDB performs semantic search across prospect database
3. Statistical re-ranking optimizes result relevance
4. Claude Haiku formats and presents retrieved data with contextual analysis
5. Response includes player statistics, rankings, and comparisons

### Key Design Decisions

- **Haiku over Sonnet**: 12x cost savings with improved accuracy and speed
- **Hybrid Search**: Combines semantic understanding with statistical precision
- **JSON for Team Data**: Resolves metadata size limitations while maintaining performance
- **Performance-Contextualized Embeddings**: Uses descriptive language ("elite production") over raw stats
- **Strict Database Adherence**: Eliminates hallucinations by constraining AI to retrieved data

## Project Structure

```
nfl-draft-scout-ai/
├── frontend/                 # React application
├── chroma_db/               # Vector database (gitignored)
├── draft_chatbot.py         # Main chatbot logic
├── flask_backend.py         # Flask API server
├── draft_prospects_POST_SENIOR_BOWL.json
├── nfl_team_needs_2026_ALL_TEAMS.json
├── requirements.txt         # Python dependencies
├── runtime.txt             # Python version
├── Procfile                # Railway deployment config
└── package.json            # Node.js configuration
```

## Installation

### Prerequisites
- Python 3.11
- Node.js and npm
- Anthropic API key

### Setup

1. Clone the repository
```bash
git clone https://github.com/yourusername/nfl-draft-scout-ai.git
cd nfl-draft-scout-ai
```

2. Create virtual environment
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install Python dependencies
```bash
pip install -r requirements.txt
```

4. Install frontend dependencies
```bash
cd frontend
npm install
cd ..
```

5. Set up environment variables
```bash
echo "ANTHROPIC_API_KEY=your_api_key_here" > .env
```

6. Build frontend
```bash
cd frontend
npm run build
cd ..
```

7. Run the application
```bash
python flask_backend.py
```

Visit `http://localhost:5000` to use the application.

## Deployment

The project is configured for Railway deployment:

1. Connect your GitHub repository to Railway
2. Set environment variable: `ANTHROPIC_API_KEY`
3. Railway will automatically detect and use the Procfile
4. Custom domain configuration available through Railway dashboard

## Usage Examples

**Query by position:**
"Show me the top edge rushers in this draft"

**Compare prospects:**
"Compare the top 3 quarterbacks and their strengths"

**Team-specific queries:**
"Which prospects would fit the Kansas City Chiefs' needs?"

**Statistical queries:**
"Find cornerbacks with elite coverage stats"

**Draft position analysis:**
"Who are the best prospects available in the late first round?"

## Performance

- **Cost**: 12x reduction using Claude Haiku vs Sonnet
- **Accuracy**: Improved through hybrid search and statistical re-ranking
- **Speed**: Faster response times with Haiku model
- **Database Coverage**: 86% statistical coverage for top 300 prospects

## Development Approach

This project follows an iterative development methodology:
1. Comprehensive dataset creation first
2. Layer AI capabilities incrementally
3. Systematic testing and optimization
4. Manual verification of automated processes
5. Clean project organization and version control

## Future Enhancements

- Real-time draft board tracking
- Advanced player comparison visualizations
- Historical draft class comparisons
- Mock draft simulator integration
- Enhanced mobile experience

## Contributing

This is a portfolio project, but feedback and suggestions are welcome. Please open an issue to discuss potential improvements.

## License

This project is for educational and portfolio purposes.

## Contact

Hesham
- Portfolio: https://www.heshamrashid.org/
- LinkedIn: https://www.linkedin.com/in/hesham-rashid/ 
- Email: h.f.rashid@gmail.com

Master's in AI and Business Analytics - University of South Florida

## Acknowledgments

- Data sourced from Sports Reference, NFL Mock Draft Database, PFF, CBS Sports, Tankathon, and Fantasy Pros
- Built with Anthropic's Claude API
- Vector search powered by ChromaDB
