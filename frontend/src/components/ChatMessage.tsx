import React, { useState, useEffect } from 'react';
import './ChatMessage.css';
import MarkdownRenderer from './MarkdownRenderer';
import { Step, ChatOutput } from '../types';

interface ChatMessageProps {
  output: ChatOutput;
}

const ChatMessage: React.FC<ChatMessageProps> = ({ output }) => {
  const detailsHidden = !!output.result?.answer;
  return (
    <React.Fragment>
      <div className="message-container user-message">
        <p>{output.question}</p>
      </div>
      <div className="message-container bot-message">
        {output.steps.length > 0 && (
          <GenerationSteps steps={output.steps} done={detailsHidden} />
        )}
        <MarkdownRenderer content={output.result?.answer || ""} />
      </div>
    </React.Fragment>
  );
};

const GenerationSteps = ({ steps, done }: { steps: Step[]; done: boolean }) => {
  const [hidden, setHidden] = useState(done);

  return (
    <div className="generation-steps-container">
      <button
        className="steps-toggle-button"
        onClick={() => setHidden(!hidden)}
      >
        Steps {hidden ? <ChevronDown /> : <ChevronUp />}
      </button>

      {!hidden && (
        <div className="generation-steps-content">
          <div className="generation-steps-line-container">
            <span
              className={`generation-steps-pulse-dot ${
                !done ? "animate-pulse" : "bg-gray-500"}
              }`}
            ></span>

            <div className="generation-steps-vertical-line"></div>
          </div>

          <div className="generation-steps-item-container">
            {steps.map((step, j) => {
              return (
                <div key={j}>
                  <p>{step.name}</p>

                  <div className="generation-steps-tool-results">
                    {Object.entries(step.result).map(([key, value]) => (
                      <p
                        key={key}
                        className="generation-steps-tool-item"
                      >
                        {`${key}: ${value}`}
                      </p>
                    ))}
                  </div>
                </div>
              );
            })}
          </div>
        </div>
      )}
    </div>
  );
};

const ChevronDown = () => (
  <svg
    xmlns="http://www.w3.org/2000/svg"
    width="18"
    height="18"
    viewBox="0 0 24 24"
    fill="none"
    stroke="currentColor"
    strokeWidth="2"
    strokeLinecap="round"
    strokeLinejoin="round"
    className="lucide lucide-chevron-down"
  >
    <path d="m6 9 6 6 6-6" />
  </svg>
);

const ChevronUp = () => (
  <svg
    xmlns="http://www.w3.org/2000/svg"
    width="18"
    height="18"
    viewBox="0 0 24 24"
    fill="none"
    stroke="currentColor"
    strokeWidth="2"
    strokeLinecap="round"
    strokeLinejoin="round"
    className="lucide lucide-chevron-up"
  >
    <path d="m18 15-6-6-6 6" />
  </svg>
);

export default ChatMessage;