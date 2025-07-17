import React, { useState, useRef, useEffect } from 'react';
import './App.css';
import ChatInput from './components/ChatInput';
import ChatMessage from './components/ChatMessage';
import { ChatOutput, Step } from './types';
import { IncompleteJsonParser } from 'incomplete-json-parser';

function App() {
  const [message, setMessage] = useState('');
  const [chatHistory, setChatHistory] = useState<ChatOutput[]>([]);

  useEffect(() => {
    const fetchInitialHistory = async () => {
      try {
        const response = await fetch(`${process.env.REACT_APP_API_URL}/api/initial_history`);
        if (!response.ok) {
          throw new Error(`HTTP error! status: ${response.status}`);
        }
        const data = await response.json();
        const initialBotMessage = data.chat_history.find((msg: any) => msg.type === 'ai');
        if (initialBotMessage) {
          setChatHistory([
            {
              question: '',
              steps: [],
              result: {
                answer: initialBotMessage.content,
                tools_used: [],
              },
            },
          ]);
        }
      } catch (error) {
        console.error("Error fetching initial chat history:", error);
      }
    };

    fetchInitialHistory();
  }, []);
  const chatHistoryRef = useRef<HTMLDivElement>(null);
  const [isGenerating, setIsGenerating] = useState(false);

  const sendMessage = async () => {
    if (!message) return;

    const userMessage = message;
    const newOutputs: ChatOutput[] = [
      ...chatHistory,
      {
        question: userMessage,
        steps: [],
        result: {
          answer: "",
          tools_used: [],
        },
      },
    ];
    setChatHistory(newOutputs);
    setMessage('');
    setIsGenerating(true);

    try {
      const res = await fetch(`${process.env.REACT_APP_API_URL}/api/chat`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ message: userMessage }),
      });

      if (!res.ok) {
        throw new Error("Error");
      }

      const data = res.body;
      if (!data) {
        setIsGenerating(false);
        return;
      }

      const reader = data.getReader();
      const decoder = new TextDecoder();
      let done = false;
      let answer = { answer: "", tools_used: [] };
      let currentSteps: Step[] = [];
      let buffer = "";
      const parser = new IncompleteJsonParser();

      // Process streaming response chunks and parse steps/results
      while (!done) {
        const { value, done: doneReading } = await reader.read();
        done = doneReading;
        let chunkValue = decoder.decode(value);
        if (!chunkValue) continue;

        buffer += chunkValue;

        // Handle different types of steps in the response stream - regular steps and final answer
        if (buffer.includes("</step_name>")) {
          const stepNameMatch = buffer.match(/<step_name>([^<]*)<\/step_name>/);
          if (stepNameMatch) {
            const [_, stepName] = stepNameMatch;
            try {
              if (stepName !== "final_answer") {
                const fullStepPattern =
                  /<step><step_name>([^<]*)<\/step_name>([^<]*?)(?=<step>|<\/step>|$)/g;
                const matches = [...buffer.matchAll(fullStepPattern)];

                for (const match of matches) {
                  const [fullMatch, matchStepName, jsonStr] = match;
                  if (jsonStr) {
                    try {
                      const result = JSON.parse(jsonStr);
                      currentSteps.push({ name: matchStepName, result });
                      buffer = buffer.replace(fullMatch, "");
                    } catch (error) {
                    }
                  }
                }
              } else {
                // If it's the final answer step, parse the streaming JSON using incomplete-json-parser
                const jsonMatch = buffer.match(
                  /(?<=<step><step_name>final_answer<\/step_name>)(.*)/
                );
                if (jsonMatch) {
                  const [_, jsonStr] = jsonMatch;
                  parser.write(jsonStr);
                  const result = parser.getObjects();
                  answer = result;
                  parser.reset();
                }
              }
            } catch (e) {
              console.log("Failed to parse step:", e);
            }
          }
        }

        // Update output with current content and steps
        setChatHistory((prevState) => {
          const lastOutput = prevState[prevState.length - 1];
          return [
            ...prevState.slice(0, -1),
            {
              ...lastOutput,
              steps: currentSteps,
              result: answer,
            },
          ];
        });
      }
    } catch (error) {
      console.error(error);
    } finally {
      setIsGenerating(false);
    }
  };

  useEffect(() => {
    if (chatHistoryRef.current) {
      chatHistoryRef.current.scrollTop = chatHistoryRef.current.scrollHeight;
    }
  }, [chatHistory]);

  return (
    <div className="App">
      <header className="App-header">
        <h1>BiteBot</h1>
        <div className="chat-history" ref={chatHistoryRef}>
          {chatHistory.map((output, index) => (
            <ChatMessage key={index} output={output} />
          ))}
        </div>
        <ChatInput message={message} setMessage={setMessage} sendMessage={sendMessage} />
      </header>
    </div>
  );
}

export default App;
