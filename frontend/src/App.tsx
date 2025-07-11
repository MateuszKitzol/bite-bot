import React, { useState, useRef, useEffect } from 'react';
import './App.css';

function App() {
  const [message, setMessage] = useState('');
  const [chatHistory, setChatHistory] = useState<{ user: string; bot: string }[]>([]);
  const chatHistoryRef = useRef<HTMLDivElement>(null);

  const sendMessage = async () => {
    if (!message) return;

    const response = await fetch('http://localhost:8000/api/chat', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ message }),
    });

    const data = await response.json();
    setChatHistory([...chatHistory, { user: message, bot: data.response }]);
    setMessage('');
  };

  useEffect(() => {
    if (chatHistoryRef.current) {
      chatHistoryRef.current.scrollTop = chatHistoryRef.current.scrollHeight;
    }
  }, [chatHistory]);

  return (
    <div className="App">
      <header className="App-header">
        <h1>Chatbot</h1>
        <div className="chat-history" ref={chatHistoryRef}>
          {chatHistory.map((chat, index) => (
            <React.Fragment key={index}>
              <div className="message-container user-message">
                <p>{chat.user}</p>
              </div>
              <div className="message-container bot-message">
                <p>{chat.bot}</p>
              </div>
            </React.Fragment>
          ))}
        </div>
        <div className="chat-input">
          <input
            type="text"
            value={message}
            onChange={(e) => setMessage(e.target.value)}
            onKeyPress={(e) => e.key === 'Enter' && sendMessage()}
          />
          <button onClick={sendMessage}>Send</button>
        </div>
      </header>
    </div>
  );
}

export default App;
