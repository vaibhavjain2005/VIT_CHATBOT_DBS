import React from "react";
import RankPredictionCard from "./intents/RankPredictionCard";
import CutoffCard from "./intents/CutoffCard";
import FAQCard from "./intents/FAQCard";
import { Card } from "@heroui/react";

export default function ResponseCard({ data }) {
  if (!data.intent)
    return (
      <Card className="bg-default-100 p-3">
        {data.text || "No response"}
      </Card>
    );

  switch (data.intent) {
    case "rank_prediction":
      return <RankPredictionCard data={data} />;
    case "cutoff":
      return <CutoffCard data={data} />;
    case "faq":
      return <FAQCard data={data} />;
    default:
      return <Card className="bg-default-100 p-3">{data.answer}</Card>;
  }
}
