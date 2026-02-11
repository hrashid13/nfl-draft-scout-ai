"""
Flask Backend for NFL Draft Scouting Web App - Single Service Deployment
Serves both the React frontend and API endpoints
"""

from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import os
import sys

# Import your chatbot
from draft_chatbot import GuidedRAGDraftScout

# Initialize Flask app with static folder for React build
app = Flask(__name__, static_folder='frontend/build', static_url_path='')

# Configure CORS for API endpoints only
CORS(app, resources={
    r"/api/*": {
        "origins": "*",
        "methods": ["GET", "POST", "OPTIONS"],
        "allow_headers": ["Content-Type"]
    }
})

# Global chatbot instance
chatbot = None

def initialize_chatbot():
    """Initialize the chatbot on startup"""
    global chatbot
    
    try:
        print("="*80)
        print("Initializing NFL Draft Scouting Chatbot...")
        print("="*80)
        
        # Get API key from environment variable (set in Railway)
        api_key = os.environ.get('ANTHROPIC_API_KEY')
        if not api_key:
            print("WARNING: ANTHROPIC_API_KEY not found in environment variables!")
            print("Set it in Railway dashboard: Settings > Variables")
        
        # Initialize chatbot
        chatbot = GuidedRAGDraftScout(
            api_key=api_key,
            chroma_path="./chroma_db"
        )
        
        print(" Chatbot initialized successfully!")
        print(f" Collection loaded: {chatbot.collection.count()} prospects")
        print("="*80)
        
        return True
        
    except Exception as e:
        print(f" Error initializing chatbot: {e}")
        return False

# Initialize on startup
with app.app_context():
    initialize_chatbot()

# ============================================================================
# FRONTEND ROUTES - Serve React App
# ============================================================================

@app.route('/')
def serve_react_app():
    """Serve the React frontend"""
    try:
        return send_from_directory(app.static_folder, 'index.html')
    except Exception as e:
        return jsonify({
            'error': 'Frontend not found. Make sure frontend/build/ folder exists.',
            'details': str(e)
        }), 404

@app.route('/<path:path>')
def serve_static_files(path):
    """Serve React static files (JS, CSS, images, etc.)"""
    try:
        # Check if file exists in build folder
        if path != "" and os.path.exists(os.path.join(app.static_folder, path)):
            return send_from_directory(app.static_folder, path)
        else:
            # For client-side routing, return index.html
            return send_from_directory(app.static_folder, 'index.html')
    except Exception as e:
        return jsonify({
            'error': 'File not found',
            'details': str(e)
        }), 404

# ============================================================================
# API ROUTES - Backend Endpoints
# ============================================================================

@app.route('/api/status')
def api_status():
    """API status page - JSON response"""
    if chatbot is None:
        return jsonify({
            'status': 'error',
            'message': 'Chatbot not initialized'
        }), 500
    
    try:
        prospect_count = chatbot.collection.count()
        return jsonify({
            'status': 'online',
            'service': 'NFL Draft Scout API',
            'version': '2.0',
            'prospects_loaded': prospect_count,
            'chatbot_initialized': True,
            'endpoints': {
                'GET /': 'React frontend',
                'POST /api/chat': 'Send a question about draft prospects',
                'POST /api/reset': 'Reset conversation history',
                'GET /api/health': 'Health check',
                'GET /api/status': 'API status (this endpoint)'
            }
        })
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

@app.route('/api/chat', methods=['POST'])
def chat():
    """Handle chat requests from frontend"""
    if chatbot is None:
        return jsonify({
            'error': 'Chatbot not initialized. Please contact administrator.'
        }), 500
    
    try:
        data = request.get_json()
        
        if not data or 'message' not in data:
            return jsonify({
                'error': 'Missing "message" field in request body'
            }), 400
        
        user_message = data['message']
        
        print(f"\n[API] User query: {user_message}")
        
        # Get response from chatbot
        response = chatbot.chat(user_message)
        
        print(f"[API] Response length: {len(response)} characters")
        
        return jsonify({
            'response': response
        })
        
    except Exception as e:
        print(f"[API] Error in /api/chat: {e}")
        return jsonify({
            'error': f'An error occurred: {str(e)}'
        }), 500

@app.route('/api/reset', methods=['POST'])
def reset():
    """Reset conversation history"""
    if chatbot is None:
        return jsonify({
            'error': 'Chatbot not initialized'
        }), 500
    
    try:
        chatbot.reset_conversation()
        print("[API] Conversation reset")
        return jsonify({
            'message': 'Conversation history reset successfully'
        })
    except Exception as e:
        print(f"[API] Error resetting conversation: {e}")
        return jsonify({
            'error': f'Error resetting conversation: {str(e)}'
        }), 500

@app.route('/api/health', methods=['GET'])
def health():
    """Health check endpoint for monitoring"""
    try:
        if chatbot is None:
            return jsonify({
                'status': 'unhealthy',
                'chatbot': 'not_initialized',
                'timestamp': os.environ.get('RAILWAY_DEPLOYMENT_ID', 'local')
            }), 500
        
        # Check ChromaDB
        prospect_count = chatbot.collection.count()
        
        # Check API key
        has_api_key = bool(os.environ.get('ANTHROPIC_API_KEY'))
        
        return jsonify({
            'status': 'healthy',
            'chatbot': 'initialized',
            'chromadb': 'connected',
            'prospects': prospect_count,
            'anthropic_api_key': 'configured' if has_api_key else 'missing',
            'environment': 'railway' if os.environ.get('RAILWAY_ENVIRONMENT') else 'local',
            'timestamp': os.environ.get('RAILWAY_DEPLOYMENT_ID', 'local')
        })
        
    except Exception as e:
        return jsonify({
            'status': 'unhealthy',
            'error': str(e)
        }), 500

# ============================================================================
# ERROR HANDLERS
# ============================================================================

@app.errorhandler(404)
def not_found(e):
    """Handle 404 errors"""
    # If it's an API request, return JSON
    if request.path.startswith('/api/'):
        return jsonify({'error': 'API endpoint not found'}), 404
    # Otherwise, serve React app (for client-side routing)
    return send_from_directory(app.static_folder, 'index.html')

@app.errorhandler(500)
def internal_error(e):
    """Handle 500 errors"""
    return jsonify({
        'error': 'Internal server error',
        'details': str(e)
    }), 500

# ============================================================================
# STARTUP
# ============================================================================

if __name__ == '__main__':
    # For local development
    port = int(os.environ.get('PORT', 5000))
    
    print("\n" + "="*80)
    print("NFL DRAFT SCOUTING APP - SINGLE SERVICE MODE")
    print("="*80)
    print(f"\n Server starting on http://localhost:{port}")
    print(f" Frontend: http://localhost:{port}/")
    print(f" API: http://localhost:{port}/api/chat")
    print(f"  Health: http://localhost:{port}/api/health")
    print("\nPress Ctrl+C to stop the server")
    print("="*80 + "\n")
    
    app.run(
        host='0.0.0.0',
        port=port,
        debug=False  # Set to False for production
    )