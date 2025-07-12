import React, { useState, useRef, useEffect } from 'react';
import './App.css';
import ChatInput from './components/ChatInput';
import ChatMessage from './components/ChatMessage';

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
            <ChatMessage key={index} chat={chat} />
          ))}
        </div>
        <ChatInput message={message} setMessage={setMessage} sendMessage={sendMessage} />
      </header>
    </div>
  );
}

export default App;
