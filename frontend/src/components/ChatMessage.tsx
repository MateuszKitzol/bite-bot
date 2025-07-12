import React from 'react';

interface ChatMessageProps {
  chat: { user: string; bot: string };
}

const ChatMessage: React.FC<ChatMessageProps> = ({ chat }) => {
  return (
    <React.Fragment>
      <div className="message-container user-message">
        <p>{chat.user}</p>
      </div>
      <div className="message-container bot-message">
        <p>{chat.bot}</p>
      </div>
    </React.Fragment>
  );
};

export default ChatMessage;
