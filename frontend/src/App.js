import React, { useState, useEffect, useRef } from 'react';
import Footer from './Footer';

const DraftScoutingWebApp = () => {
  // Use relative URL - works for both local and Railway
  // When deployed, it will use the same domain as the frontend
  const API_URL = window.location.origin;
  
  const [messages, setMessages] = useState([]);
  const [inputMessage, setInputMessage] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [systemStatus, setSystemStatus] = useState({
    backend: 'checking',
    chromadb: 'checking',
    claude: 'checking'
  });
  const messagesEndRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  // Check system status on mount
  useEffect(() => {
    checkSystemStatus();
  }, []);

  const checkSystemStatus = async () => {
    try {
      const response = await fetch(`${API_URL}/api/health`);
      const data = await response.json();
      
      setSystemStatus({
        backend: data.status === 'healthy' ? 'online' : 'offline',
        chromadb: data.chromadb === 'connected' ? 'online' : 'offline',
        claude: data.anthropic_api_key === 'configured' ? 'online' : 'offline'
      });
    } catch (error) {
      console.error('Health check failed:', error);
      setSystemStatus({
        backend: 'offline',
        chromadb: 'offline',
        claude: 'offline'
      });
    }
  };

  const suggestedQuestions = [
    "Who are the top 5 quarterback prospects?",
    "Show me the best edge rushers with elite sack production",
    "Find cornerbacks with the best ball production",
    "Compare the top 3 wide receivers",
    "Who are consensus first round talents at safety?",
    "Show me offensive tackles ranked in the top 50"
  ];

  const handleSendMessage = async (messageText = null) => {
    const message = messageText || inputMessage.trim();
    
    if (!message) return;

    const userMessage = { role: 'user', content: message };
    setMessages(prev => [...prev, userMessage]);
    setInputMessage('');
    setIsLoading(true);

    try {
      const response = await fetch(`${API_URL}/api/chat`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ message: message }),
      });

      const data = await response.json();
      
      if (response.ok) {
        const assistantMessage = { role: 'assistant', content: data.response };
        setMessages(prev => [...prev, assistantMessage]);
      } else {
        throw new Error(data.error || 'Failed to get response');
      }
    } catch (error) {
      console.error('Error:', error);
      const errorMessage = { 
        role: 'assistant', 
        content: `Error: ${error.message}. Please try again or check if the backend is running.` 
      };
      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleReset = async () => {
    try {
      await fetch(`${API_URL}/api/reset`, { method: 'POST' });
      setMessages([]);
    } catch (error) {
      console.error('Error resetting conversation:', error);
    }
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSendMessage();
    }
  };

  return (
    <div className="flex flex-col min-h-screen">
      <div className="flex-grow bg-gradient-dark">
        <div className="container mx-auto px-4 py-8 max-w-7xl">
        {/* Header */}
        <div className="text-center mb-8">
          <h1 className="text-5xl font-bold text-wheat mb-2 text-shadow">
            NFL Draft Scout AI
          </h1>
          <p className="text-wheat opacity-80 text-lg">
            2026 Draft Class Analysis - Powered by AI
          </p>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
          {/* Sidebar */}
          <div className="lg:col-span-1 space-y-6">
            {/* Stats Card */}
            <div className="card p-6">
              <h3 className="text-xl font-semibold text-wheat mb-4">Database Stats</h3>
              <div className="space-y-3">
                <div className="flex justify-between items-center">
                  <span className="text-wheat opacity-80">Total Prospects</span>
                  <span className="text-wheat font-bold">500</span>
                </div>
                <div className="flex justify-between items-center">
                  <span className="text-wheat opacity-80">With Statistics</span>
                  <span className="text-wheat font-bold">377</span>
                </div>
                <div className="flex justify-between items-center">
                  <span className="text-wheat opacity-80">Coverage</span>
                  <span className="text-green-400 font-bold">75.4%</span>
                </div>
                <div className="flex justify-between items-center">
                  <span className="text-wheat opacity-80">Ranking Sources</span>
                  <span className="text-wheat font-bold">5</span>
                </div>
              </div>
            </div>

            {/* System Status */}
            <div className="card p-6">
              <h3 className="text-xl font-semibold text-wheat mb-4">System Status</h3>
              <div className="space-y-3">
                <div className="flex justify-between items-center">
                  <span className="text-wheat opacity-80">Backend</span>
                  <span className={`px-2 py-1 rounded text-xs font-semibold ${
                    systemStatus.backend === 'online' ? 'bg-green-500/20 text-green-400' : 'bg-red-500/20 text-red-400'
                  }`}>
                    {systemStatus.backend}
                  </span>
                </div>
                <div className="flex justify-between items-center">
                  <span className="text-wheat opacity-80">ChromaDB</span>
                  <span className={`px-2 py-1 rounded text-xs font-semibold ${
                    systemStatus.chromadb === 'online' ? 'bg-green-500/20 text-green-400' : 'bg-red-500/20 text-red-400'
                  }`}>
                    {systemStatus.chromadb}
                  </span>
                </div>
                <div className="flex justify-between items-center">
                  <span className="text-wheat opacity-80">Claude API</span>
                  <span className={`px-2 py-1 rounded text-xs font-semibold ${
                    systemStatus.claude === 'online' ? 'bg-green-500/20 text-green-400' : 'bg-red-500/20 text-red-400'
                  }`}>
                    {systemStatus.claude}
                  </span>
                </div>
              </div>
            </div>

            {/* Suggested Questions */}
            <div className="card p-6">
              <h3 className="text-xl font-semibold text-wheat mb-4">Suggested Questions</h3>
              <div className="space-y-2">
                {suggestedQuestions.map((question, index) => (
                  <button
                    key={index}
                    onClick={() => handleSendMessage(question)}
                    className="w-full text-left px-3 py-2 rounded bg-blue-slate-500 bg-opacity-20 hover:bg-opacity-35 text-wheat text-sm transition-all border border-wheat border-opacity-25 hover:border-blue-slate-500 hover-translate"
                  >
                    {question}
                  </button>
                ))}
              </div>
            </div>

            {/* Features */}
            <div className="card p-6">
              <h3 className="text-xl font-semibold text-wheat mb-4">Features</h3>
              <ul className="space-y-2 text-wheat opacity-80 text-sm">
                <li className="flex items-start">
                  <span className="text-green-400 mr-2">✓</span>
                  <span>Semantic search across 500 prospects</span>
                </li>
                <li className="flex items-start">
                  <span className="text-green-400 mr-2">✓</span>
                  <span>Statistical analysis & rankings</span>
                </li>
                <li className="flex items-start">
                  <span className="text-green-400 mr-2">✓</span>
                  <span>Position-specific queries</span>
                </li>
                <li className="flex items-start">
                  <span className="text-green-400 mr-2">✓</span>
                  <span>Multi-source consensus rankings</span>
                </li>
                <li className="flex items-start">
                  <span className="text-green-400 mr-2">✓</span>
                  <span>Natural language interface</span>
                </li>
              </ul>
            </div>
          </div>

          {/* Main Chat Area */}
          <div className="lg:col-span-3">
            <div className="card flex flex-col h-[calc(100vh-200px)]">
              {/* Chat Header */}
              <div className="p-4 border-b border-wheat border-opacity-20 flex justify-between items-center">
                <h2 className="text-xl font-semibold text-wheat">Chat with Scout AI</h2>
                <button
                  onClick={handleReset}
                  className="btn-secondary"
                >
                  Reset Conversation
                </button>
              </div>

              {/* Messages */}
              <div className="flex-1 overflow-y-auto p-6 space-y-4">
                {messages.length === 0 ? (
                  <div className="text-center text-wheat opacity-70 mt-20">
                    <p className="text-lg mb-2">Welcome to NFL Draft Scout AI!</p>
                    <p className="text-sm">Ask me anything about the 2026 draft class.</p>
                  </div>
                ) : (
                  messages.map((message, index) => (
                    <div
                      key={index}
                      className={`flex ${message.role === 'user' ? 'justify-end' : 'justify-start'}`}
                    >
                      <div
                        className={`max-w-3xl px-4 py-3 rounded-lg ${
                          message.role === 'user'
                            ? 'message-user'
                            : 'message-assistant'
                        }`}
                      >
                        <p className="whitespace-pre-wrap">{message.content}</p>
                      </div>
                    </div>
                  ))
                )}
                {isLoading && (
                  <div className="flex justify-start">
                    <div className="bg-evergreen-500 bg-opacity-50 px-4 py-3 rounded-lg border border-wheat border-opacity-20">
                      <div className="flex space-x-2">
                        <div className="w-2 h-2 bg-blue-slate-400 rounded-full animate-bounce"></div>
                        <div className="w-2 h-2 bg-blue-slate-400 rounded-full animate-bounce" style={{ animationDelay: '0.1s' }}></div>
                        <div className="w-2 h-2 bg-blue-slate-400 rounded-full animate-bounce" style={{ animationDelay: '0.2s' }}></div>
                      </div>
                    </div>
                  </div>
                )}
                <div ref={messagesEndRef} />
              </div>

              {/* Input Area */}
              <div className="p-4 border-t border-wheat border-opacity-20">
                <div className="flex space-x-2">
                  <input
                    type="text"
                    value={inputMessage}
                    onChange={(e) => setInputMessage(e.target.value)}
                    onKeyPress={handleKeyPress}
                    placeholder="Ask about draft prospects..."
                    className="input-field"
                    disabled={isLoading}
                  />
                  <button
                    onClick={() => handleSendMessage()}
                    disabled={isLoading || !inputMessage.trim()}
                    className="btn-primary disabled:opacity-50 disabled:cursor-not-allowed"
                  >
                    Send
                  </button>
                </div>
              </div>
            </div>
          </div>
        </div>
        </div>
      </div>
      <Footer />
    </div>
  );
};

export default DraftScoutingWebApp;