import React, { useState } from 'react';
import './App.css';

function App() {
  const [userInput, setUserInput] = useState('');
  const [responseText, setResponseText] = useState('');
  const [messages, setMessages] = useState([
    {
      message: "Hello i am chatbot",
      sender: "ChatBot",
    },
  ]);
  const handleUserInput = (event) => {
    setUserInput(event.target.value);
  };
  
  const handleSubmit = async () => {
    const inputMessage = document.getElementById("message").value;

    const newMessage = {
      message: inputMessage,
      sender: "user",
    };

    const newMessages = [...messages, newMessage];
    await setMessages(newMessages);
    console.log("messages: ", newMessages);
    console.log(messages);
    await processMessage(newMessage);
  };
  async function processMessage(newMesages) {
    const jsonMessage = JSON.stringify([
      {
        role: newMesages.sender === "ChatBot" ? "assistant" : "user",
        content: newMesages.message,
      },
    ]);
    console.log("0", jsonMessage);

    const response = await fetch("http://127.0.0.1:8000/chat", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: jsonMessage,
    });
    console.log("1");
    if (!response.ok) {
      throw new Error("Failed to fetch");
    }
    const data = await response.json();

    const newMessage = {
      message: data[0].response,
      sender: "ChatBot",
      // direction: "incoming",
    };
    console.log("newMesages1: ", newMessage);

    setMessages((prevMessages) => [...prevMessages, newMessage]);
    console.log("newMesages2: ", messages);
    
  }

  return (
    <div className="App">
      <h1>Chatbot</h1>
      <div className="chat-history">
        {messages.map((chat, index) => (
          <div key={index} className="chat-entry">
            <div className="user-message">{chat.message}</div>
            {/* <div className="bot-message">{chat.answer}</div> */}
          </div>
        ))}
        <div className="response">{responseText}</div>
      </div>
      <div className="input-section">
        <input
          id="message"
          type="text"
          value={userInput}
          onChange={handleUserInput}
          placeholder="Enter your message"
        />
        <button onClick={handleSubmit}>Send</button>
      </div>
    </div>
  );
}

export default App;
