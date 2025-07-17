import React from 'react';
import './InfoPanel.css';

interface InfoPanelProps {
  onClose: () => void;
}

const InfoPanel: React.FC<InfoPanelProps> = ({ onClose }) => {
  return (
    <div className="info-panel">
      <button className="close-button" onClick={onClose}>
        <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className="feather feather-x"><line x1="18" y1="6" x2="6" y2="18"></line><line x1="6" y1="6" x2="18" y2="18"></line></svg>
      </button>
      <div className="info-content">
        <h2>BiteBot - Your Personal Recipe Health Assistant</h2>
        <p>BiteBot is a full-stack chatbot application designed to help you make your favorite recipes healthier. Simply provide a recipe, and BiteBot will suggest three minor modifications to improve its nutritional value. It can also provide detailed nutritional information for individual ingredients and entire meals.</p>
        <h3>Tech Stack</h3>
        <h4>Backend</h4>
        <ul>
          <li>Python</li>
          <li>FastAPI: For building the REST API.</li>
          <li>LangChain: To power the conversational agent.</li>
          <li>OpenAI GPT-4o-mini: The language model used by the agent.</li>
          <li>USDA FoodData Central API: For fetching nutritional information.</li>
        </ul>
        <h4>Frontend</h4>
        <ul>
          <li>React</li>
          <li>TypeScript</li>
          <li>Create React App</li>
          <li>React Markdown: For rendering Markdown content.</li>
        </ul>
        <h3>How It Works</h3>
        <p>The application consists of a React frontend and a FastAPI backend. The frontend provides a user-friendly chat interface, while the backend handles the business logic.</p>
        <p>When a user sends a message, the frontend sends a POST request to the /api/chat endpoint on the backend. The backend then uses a LangChain agent to process the message. The agent has access to a set of tools that allow it to perform various tasks, such as fetching nutritional information or scraping movie listings. The agent's response is streamed back to the frontend and displayed to the user.</p>
      </div>
    </div>
  );
};

export default InfoPanel;