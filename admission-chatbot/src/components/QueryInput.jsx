import React, { useState } from "react";
import { Input, Button } from "@heroui/react";

export default function QueryInput({ onSubmit }) {
  const [query, setQuery] = useState("");

  const handleSubmit = (e) => {
    e.preventDefault();
    if (!query.trim()) return;
    onSubmit(query);
    setQuery("");
  };

  return (
    <form
      onSubmit={handleSubmit}
      className="fixed bottom-0 left-0 w-full p-4 bg-background border-t border-divider flex items-center gap-2"
    >
      <Input
        fullWidth
        placeholder="Ask something about VIT..."
        value={query}
        onChange={(e) => setQuery(e.target.value)}
        size="lg"
        variant="bordered"
      />
      <Button color="primary" size="lg" type="submit">
        Send
      </Button>
    </form>
  );
}
