import React from "react";
import { Card, Divider } from "@heroui/react";

export default function FAQCard({ data }) {
  return (
    <Card className="p-4 bg-warning-50 border border-warning-100 max-w-[80%]">
      <h3 className="font-semibold text-warning-700 text-lg">💡 FAQ</h3>
      <Divider className="my-2" />
      <p className="whitespace-pre-line text-sm text-foreground">
        {data.answer}
      </p>
    </Card>
  );
}
