import React from "react";
import { Card, Divider } from "@heroui/react";

export default function CutoffCard({ data }) {
  return (
    <Card className="p-4 bg-primary-50 border border-primary-100 max-w-[80%]">
      <h3 className="font-semibold text-primary-700 text-lg">📊 Cutoff Info</h3>
      <Divider className="my-2" />
      <p className="whitespace-pre-line text-sm text-foreground">
        {data.answer}
      </p>
    </Card>
  );
}
