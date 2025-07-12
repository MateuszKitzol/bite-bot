import React, { useState } from 'react';

interface ChatInputProps {
  message: string;
  setMessage: (message: string) => void;
  sendMessage: () => void;
}

const ChatInput: React.FC<ChatInputProps> = ({ message, setMessage, sendMessage }) => {
  return (
    <div className="chat-input">
      <input
        type="text"
        value={message}
        onChange={(e) => setMessage(e.target.value)}
        onKeyPress={(e) => e.key === 'Enter' && sendMessage()}
      />
      <button onClick={sendMessage}><svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className="feather feather-send"><line x1="22" y1="2" x2="11" y2="13"></line><polygon points="22 2 15 22 11 13 2 9 22 2"></polygon></svg></button>
    </div>
  );
};

export default ChatInput;
