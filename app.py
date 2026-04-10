"""
AI Chat Application - Flask Backend
Features: Login, Chat History, Auto-Reply, Context Understanding
Deploy on Render, Railway, or any Python hosting platform
"""

from flask import Flask, render_template, request, jsonify, session, redirect, url_for
from flask_cors import CORS
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
import os
import json
import re
import random

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'your-super-secret-key-change-in-production')
CORS(app)

# ============================================
# DATABASE SIMULATION (Replace with real DB in production)
# Use SQLite, PostgreSQL, or MongoDB for production
# ============================================

users_db = {}  # {username: {password_hash, email, created_at}}
chat_history_db = {}  # {username: [{role, content, timestamp, conversation_id}]}
conversations_db = {}  # {username: [{id, title, created_at}]}

# ============================================
# AI RESPONSE ENGINE
# Replace with OpenAI, Gemini, or other AI APIs
# ============================================

class AIEngine:
    """
    Smart AI Response Engine with Context Understanding
    Replace generate_response with actual AI API calls for production
    """
    
    def __init__(self):
        self.context_memory = {}  # Store conversation context per user
        
        # Knowledge base for demo responses
        self.knowledge_base = {
            "greeting": [
                "Hello! How can I assist you today?",
                "Hi there! I'm ready to help you with anything.",
                "Welcome! What would you like to know?",
                "Hey! Great to see you. What's on your mind?"
            ],
            "farewell": [
                "Goodbye! Have a wonderful day!",
                "See you later! Don't hesitate to come back if you need help.",
                "Take care! It was nice chatting with you.",
                "Bye for now! Feel free to return anytime."
            ],
            "thanks": [
                "You're welcome! Is there anything else I can help with?",
                "Happy to help! Let me know if you need more assistance.",
                "My pleasure! Feel free to ask more questions.",
                "Anytime! I'm here whenever you need me."
            ],
            "help": [
                "I can help you with various tasks:\n\n• **Answer questions** on many topics\n• **Write code** in multiple languages\n• **Explain concepts** in simple terms\n• **Help with writing** and editing\n• **Solve problems** step by step\n\nJust ask me anything!",
            ],
            "code_python": [
                "Here's an example Python code:\n\n```python\ndef greet(name):\n    return f'Hello, {name}!'\n\nprint(greet('World'))\n```\n\nWould you like me to explain or modify this?",
            ],
            "code_javascript": [
                "Here's an example JavaScript code:\n\n```javascript\nconst greet = (name) => {\n    return `Hello, ${name}!`;\n};\n\nconsole.log(greet('World'));\n```\n\nNeed any modifications?",
            ],
        }
    
    def understand_intent(self, message: str) -> str:
        """Analyze user message to understand intent"""
        message_lower = message.lower().strip()
        
        # Greeting detection
        greetings = ['hello', 'hi', 'hey', 'good morning', 'good afternoon', 'good evening', 'howdy']
        if any(g in message_lower for g in greetings):
            return "greeting"
        
        # Farewell detection
        farewells = ['bye', 'goodbye', 'see you', 'later', 'take care', 'good night']
        if any(f in message_lower for f in farewells):
            return "farewell"
        
        # Thanks detection
        thanks = ['thank', 'thanks', 'appreciate', 'grateful']
        if any(t in message_lower for t in thanks):
            return "thanks"
        
        # Help request
        if 'help' in message_lower or 'what can you do' in message_lower:
            return "help"
        
        # Code requests
        if 'python' in message_lower and ('code' in message_lower or 'example' in message_lower or 'write' in message_lower):
            return "code_python"
        if 'javascript' in message_lower and ('code' in message_lower or 'example' in message_lower or 'write' in message_lower):
            return "code_javascript"
        
        return "general"
    
    def extract_context(self, user_id: str, message: str, history: list) -> dict:
        """Extract and maintain conversation context"""
        context = self.context_memory.get(user_id, {
            "topics": [],
            "user_preferences": {},
            "last_question": None,
            "conversation_mood": "neutral"
        })
        
        # Update context based on current message
        words = message.lower().split()
        
        # Track topics discussed
        topic_keywords = ['python', 'javascript', 'coding', 'programming', 'ai', 'machine learning', 
                         'web', 'database', 'api', 'frontend', 'backend']
        for keyword in topic_keywords:
            if keyword in words and keyword not in context["topics"]:
                context["topics"].append(keyword)
        
        # Detect mood
        positive_words = ['great', 'awesome', 'love', 'happy', 'excellent', 'amazing']
        negative_words = ['bad', 'hate', 'terrible', 'awful', 'frustrated', 'confused']
        
        if any(w in words for w in positive_words):
            context["conversation_mood"] = "positive"
        elif any(w in words for w in negative_words):
            context["conversation_mood"] = "needs_support"
        
        # Store question if it's a question
        if '?' in message:
            context["last_question"] = message
        
        self.context_memory[user_id] = context
        return context
    
    def generate_response(self, user_id: str, message: str, history: list = None) -> str:
        """
        Generate intelligent response based on context
        
        For production, replace this with actual AI API calls:
        - OpenAI: openai.ChatCompletion.create(...)
        - Google Gemini: genai.GenerativeModel('gemini-pro').generate_content(...)
        - Anthropic Claude: anthropic.messages.create(...)
        """
        if history is None:
            history = []
        
        # Extract context from conversation
        context = self.extract_context(user_id, message, history)
        
        # Understand intent
        intent = self.understand_intent(message)
        
        # Generate response based on intent
        if intent in self.knowledge_base:
            base_response = random.choice(self.knowledge_base[intent])
        else:
            # Generate contextual response for general queries
            base_response = self._generate_contextual_response(message, context, history)
        
        return base_response
    
    def _generate_contextual_response(self, message: str, context: dict, history: list) -> str:
        """Generate context-aware responses"""
        message_lower = message.lower()
        
        # Check for follow-up questions
        if history and ('it' in message_lower or 'that' in message_lower or 'this' in message_lower):
            last_topic = context.get("topics", [])[-1] if context.get("topics") else None
            if last_topic:
                return f"Regarding {last_topic}, I can provide more details. What specific aspect would you like to explore?"
        
        # Handle coding questions
        if any(word in message_lower for word in ['code', 'program', 'function', 'write', 'create']):
            return self._handle_code_request(message)
        
        # Handle explanations
        if any(word in message_lower for word in ['explain', 'what is', 'what are', 'how does', 'how do']):
            return self._handle_explanation(message)
        
        # Handle opinion/advice questions
        if any(word in message_lower for word in ['should', 'recommend', 'best', 'advice', 'suggest']):
            return self._handle_advice(message)
        
        # Default intelligent response
        return self._default_response(message, context)
    
    def _handle_code_request(self, message: str) -> str:
        """Handle code-related requests"""
        responses = [
            "I'd be happy to help you with coding! Could you provide more details about:\n\n• What programming language?\n• What functionality do you need?\n• Any specific requirements?\n\nThe more details you share, the better I can assist!",
            "Let's write some code together! Please tell me:\n\n1. **Language**: Which programming language?\n2. **Goal**: What should the code accomplish?\n3. **Context**: Any existing code or constraints?\n\nI'll create something tailored to your needs!"
        ]
        return random.choice(responses)
    
    def _handle_explanation(self, message: str) -> str:
        """Handle explanation requests"""
        # Extract the topic being asked about
        words = message.lower().replace('?', '').split()
        topic_words = [w for w in words if w not in ['explain', 'what', 'is', 'are', 'how', 'does', 'do', 'the', 'a', 'an', 'to', 'me']]
        topic = ' '.join(topic_words[-3:]) if topic_words else 'that concept'
        
        return f"Great question about **{topic}**! Let me explain:\n\n{topic.title()} is a concept that involves multiple aspects. To give you the most relevant explanation, could you tell me:\n\n• Your current understanding level?\n• The specific context you're working in?\n• Any particular aspects you're curious about?\n\nThis helps me tailor my explanation to your needs!"
    
    def _handle_advice(self, message: str) -> str:
        """Handle advice requests"""
        return "That's a thoughtful question! To give you the best advice, I'd like to understand:\n\n• **Your current situation**: What are you working with?\n• **Your goals**: What outcome are you hoping for?\n• **Constraints**: Any limitations or requirements?\n\nWith this context, I can provide more targeted recommendations!"
    
    def _default_response(self, message: str, context: dict) -> str:
        """Generate default contextual response"""
        mood = context.get("conversation_mood", "neutral")
        topics = context.get("topics", [])
        
        if mood == "needs_support":
            return "I understand this might be frustrating. Let me help you work through this step by step. What specific challenge are you facing?"
        
        if topics:
            recent_topic = topics[-1]
            return f"I see we've been discussing {recent_topic}. I'm here to help! Could you elaborate on what you'd like to know or accomplish? The more details you provide, the better I can assist you."
        
        return "I'm here to help! Could you provide more details about what you're looking for? I can assist with:\n\n• **Questions**: General knowledge or specific topics\n• **Coding**: Write, explain, or debug code\n• **Writing**: Help draft or edit content\n• **Problem-solving**: Work through challenges step by step\n\nWhat would you like to explore?"


# Initialize AI Engine
ai_engine = AIEngine()

# ============================================
# HELPER FUNCTIONS
# ============================================

def get_user_history(username: str) -> list:
    """Get chat history for a user"""
    return chat_history_db.get(username, [])

def save_message(username: str, role: str, content: str, conversation_id: str = "default"):
    """Save a message to chat history"""
    if username not in chat_history_db:
        chat_history_db[username] = []
    
    chat_history_db[username].append({
        "role": role,
        "content": content,
        "timestamp": datetime.now().isoformat(),
        "conversation_id": conversation_id
    })

def generate_conversation_title(first_message: str) -> str:
    """Generate a title from the first message"""
    # Take first 30 characters or first sentence
    title = first_message[:50].split('.')[0].split('?')[0].split('!')[0]
    return title.strip() + "..." if len(first_message) > 50 else title.strip()

# ============================================
# ROUTES
# ============================================

@app.route('/')
def index():
    """Serve the main chat interface"""
    if 'username' not in session:
        return redirect(url_for('login_page'))
    return render_template('index.html', username=session['username'])

@app.route('/login')
def login_page():
    """Serve the login page"""
    if 'username' in session:
        return redirect(url_for('index'))
    return render_template('login.html')

@app.route('/api/register', methods=['POST'])
def register():
    """Register a new user"""
    data = request.get_json()
    username = data.get('username', '').strip().lower()
    password = data.get('password', '')
    email = data.get('email', '').strip().lower()
    
    # Validation
    if not username or not password:
        return jsonify({"success": False, "error": "Username and password are required"}), 400
    
    if len(username) < 3:
        return jsonify({"success": False, "error": "Username must be at least 3 characters"}), 400
    
    if len(password) < 6:
        return jsonify({"success": False, "error": "Password must be at least 6 characters"}), 400
    
    if username in users_db:
        return jsonify({"success": False, "error": "Username already exists"}), 400
    
    # Create user
    users_db[username] = {
        "password_hash": generate_password_hash(password),
        "email": email,
        "created_at": datetime.now().isoformat()
    }
    
    # Initialize user data
    chat_history_db[username] = []
    conversations_db[username] = []
    
    # Auto login
    session['username'] = username
    
    return jsonify({"success": True, "message": "Registration successful", "username": username})

@app.route('/api/login', methods=['POST'])
def login():
    """Login a user"""
    data = request.get_json()
    username = data.get('username', '').strip().lower()
    password = data.get('password', '')
    
    if not username or not password:
        return jsonify({"success": False, "error": "Username and password are required"}), 400
    
    user = users_db.get(username)
    if not user or not check_password_hash(user['password_hash'], password):
        return jsonify({"success": False, "error": "Invalid username or password"}), 401
    
    session['username'] = username
    return jsonify({"success": True, "message": "Login successful", "username": username})

@app.route('/api/logout', methods=['POST'])
def logout():
    """Logout the current user"""
    session.pop('username', None)
    return jsonify({"success": True, "message": "Logged out successfully"})

@app.route('/api/chat', methods=['POST'])
def chat():
    """Process chat messages and return AI response"""
    if 'username' not in session:
        return jsonify({"success": False, "error": "Please login first"}), 401
    
    username = session['username']
    data = request.get_json()
    user_message = data.get('message', '').strip()
    conversation_id = data.get('conversation_id', 'default')
    
    if not user_message:
        return jsonify({"success": False, "error": "Message cannot be empty"}), 400
    
    # Get conversation history for context
    history = [msg for msg in get_user_history(username) if msg.get('conversation_id') == conversation_id]
    
    # Save user message
    save_message(username, "user", user_message, conversation_id)
    
    # Generate AI response
    ai_response = ai_engine.generate_response(username, user_message, history)
    
    # Save AI response
    save_message(username, "assistant", ai_response, conversation_id)
    
    # Update or create conversation
    if username not in conversations_db:
        conversations_db[username] = []
    
    # Check if this is a new conversation
    existing_conv = next((c for c in conversations_db[username] if c['id'] == conversation_id), None)
    if not existing_conv:
        conversations_db[username].insert(0, {
            "id": conversation_id,
            "title": generate_conversation_title(user_message),
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat()
        })
    else:
        existing_conv['updated_at'] = datetime.now().isoformat()
    
    return jsonify({
        "success": True,
        "response": ai_response,
        "timestamp": datetime.now().isoformat()
    })

@app.route('/api/history', methods=['GET'])
def get_history():
    """Get chat history for the current user"""
    if 'username' not in session:
        return jsonify({"success": False, "error": "Please login first"}), 401
    
    username = session['username']
    conversation_id = request.args.get('conversation_id', 'default')
    
    history = [msg for msg in get_user_history(username) if msg.get('conversation_id') == conversation_id]
    
    return jsonify({
        "success": True,
        "history": history
    })

@app.route('/api/conversations', methods=['GET'])
def get_conversations():
    """Get all conversations for the current user"""
    if 'username' not in session:
        return jsonify({"success": False, "error": "Please login first"}), 401
    
    username = session['username']
    conversations = conversations_db.get(username, [])
    
    return jsonify({
        "success": True,
        "conversations": conversations
    })

@app.route('/api/conversations/new', methods=['POST'])
def new_conversation():
    """Create a new conversation"""
    if 'username' not in session:
        return jsonify({"success": False, "error": "Please login first"}), 401
    
    conversation_id = f"conv_{datetime.now().timestamp()}"
    
    return jsonify({
        "success": True,
        "conversation_id": conversation_id
    })

@app.route('/api/conversations/<conversation_id>', methods=['DELETE'])
def delete_conversation(conversation_id):
    """Delete a conversation"""
    if 'username' not in session:
        return jsonify({"success": False, "error": "Please login first"}), 401
    
    username = session['username']
    
    # Remove conversation
    if username in conversations_db:
        conversations_db[username] = [c for c in conversations_db[username] if c['id'] != conversation_id]
    
    # Remove messages
    if username in chat_history_db:
        chat_history_db[username] = [m for m in chat_history_db[username] if m.get('conversation_id') != conversation_id]
    
    return jsonify({"success": True, "message": "Conversation deleted"})

@app.route('/api/search', methods=['GET'])
def search_history():
    """Search through chat history"""
    if 'username' not in session:
        return jsonify({"success": False, "error": "Please login first"}), 401
    
    username = session['username']
    query = request.args.get('q', '').lower().strip()
    
    if not query:
        return jsonify({"success": True, "results": []})
    
    history = get_user_history(username)
    results = [msg for msg in history if query in msg['content'].lower()]
    
    return jsonify({
        "success": True,
        "results": results[:20]  # Limit results
    })

@app.route('/api/user', methods=['GET'])
def get_user():
    """Get current user info"""
    if 'username' not in session:
        return jsonify({"success": False, "error": "Not logged in"}), 401
    
    return jsonify({
        "success": True,
        "username": session['username']
    })

# ============================================
# ERROR HANDLERS
# ============================================

@app.errorhandler(404)
def not_found(e):
    return jsonify({"success": False, "error": "Not found"}), 404

@app.errorhandler(500)
def server_error(e):
    return jsonify({"success": False, "error": "Internal server error"}), 500

# ============================================
# RUN APPLICATION
# ============================================

if __name__ == '__main__':
    # Create templates folder if it doesn't exist
    os.makedirs('templates', exist_ok=True)
    os.makedirs('static', exist_ok=True)
    
    # Run the app
    port = int(os.environ.get('PORT', 5000))
    debug = os.environ.get('FLASK_ENV') == 'development'
    app.run(host='0.0.0.0', port=port, debug=debug)
