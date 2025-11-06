import React from "react";
import ResponseCard from "./ResponseCard";
import { Card } from "@heroui/react";

export default function ChatBox({ messages }) {
  return (
    <div className="flex flex-col gap-4 p-8">
      {messages.map((msg, idx) =>
        msg.role === "user" ? (
          <div key={idx} className="flex justify-end">
            <Card radius="lg" className="bg-primary-100 text-primary-900 p-3 max-w-[75%]">
              {msg.text}
            </Card>
          </div>
        ) : (
          <div key={idx} className="flex justify-start">
            <ResponseCard data={msg.data || msg} />
          </div>
        )
      )}
    </div>
  );
}
