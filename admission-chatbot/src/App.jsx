// // import { useState } from 'react'
// // import reactLogo from './assets/react.svg'
// // import viteLogo from '/vite.svg'
// // import './App.css'
// // import {Button, ButtonGroup} from "@heroui/button";

// // function App() {
// //   const [count, setCount] = useState(0)

// //   return (
// //     <>
// //       <Button color="primary">Button</Button>
// //     </>
// //   )
// // }

// // export default App


// import React, { useState } from "react";
// import ChatBox from "./components/ChatBox";
// import QueryInput from "./components/QueryInput";
// import { Card } from "@heroui/react";
// import ThemeToggle from "./components/ThemeToggle";

// export default function App() {
//   const [messages, setMessages] = useState([]);

//   const handleQuery = async (query) => {
//     const userMsg = { role: "user", text: query };
//     setMessages((prev) => [...prev, userMsg]);

//     try {
//       const res = await fetch("http://localhost:5000/api/query", {
//         method: "POST",
//         headers: { "Content-Type": "application/json" },
//         body: JSON.stringify({
//           query,
//           user_id: "user123",
//           year: 2025,
//         }),
//       });
//       const data = await res.json();
//       setMessages((prev) => [...prev, { role: "bot", data }]);
//     } catch (err) {
//       setMessages((prev) => [
//         ...prev,
//         { role: "bot", text: "⚠️ Server error. Please try again." },
//       ]);
//     }
//   };

//   return (
//     <div className="min-h-screen flex flex-col bg-default-50">
//       <ThemeToggle />
//       <Card className="flex-1 overflow-y-auto p-4 bg-background">
//         <ChatBox messages={messages} />
//       </Card>
//       <QueryInput onSubmit={handleQuery} />
//     </div>
//   );
// }
// src/App.jsx
import React, { useState } from "react";
import ChatBox from "./components/ChatBox";
import QueryInput from "./components/QueryInput";
import ThemeToggle from "./components/ThemeToggle";
import { Navbar, NavbarBrand, NavbarContent, Card } from "@heroui/react";

export default function App() {
  const [messages, setMessages] = useState([]);

  const handleQuery = async (query) => {
    const userMsg = { role: "user", text: query };
    setMessages((prev) => [...prev, userMsg]);

    try {
      const res = await fetch("http://localhost:5000/api/query", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          query,
          user_id: "user123",
          year: 2025,
        }),
      });
      const data = await res.json();
      setMessages((prev) => [...prev, { role: "bot", data }]);
    } catch (err) {
      setMessages((prev) => [
        ...prev,
        { role: "bot", text: "⚠️ Server error. Please try again." },
      ]);
    }
  };

  return (
    <div className="min-h-screen flex flex-col bg-default-50 dark:bg-default-900 transition-colors duration-300">
      {/* 🔹 Navbar */}
      <Navbar isBordered className="bg-background">
        <NavbarBrand>
          <h1 className="text-lg font-semibold text-primary-600">
            VIT Chatbot
          </h1>
        </NavbarBrand>

        <NavbarContent justify="end">
          <ThemeToggle />
        </NavbarContent>
      </Navbar>

      {/* 🔹 Chat Section */}
      <Card radius="none" className="flex-1 overflow-y-auto  pb-24 bg-background">
        <ChatBox className="" messages={messages} />
      </Card>

      {/* 🔹 Input Section */}
      <QueryInput className="" onSubmit={handleQuery} />
    </div>
  );
}
