import React, { useState } from 'react';
import './App.css';

function App() {
  const [message, setMessage] = useState('');
  const [chatHistory, setChatHistory] = useState<{ user: string; bot: string }[]>([]);

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

  return (
    <div className="App">
      <header className="App-header">
        <h1>Chatbot</h1>
        <div className="chat-history">
          {chatHistory.map((chat, index) => (
            <div key={index}>
              <p><strong>You:</strong> {chat.user}</p>
              <p><strong>Bot:</strong> {chat.bot}</p>
            </div>
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
