import React from "react";
import { Card, Divider } from "@heroui/react";

export default function RankPredictionCard({ data }) {
  const prediction = data.rank_prediction?.predictions?.[0];

  return (
    <Card className="p-4 bg-success-50 border border-success-100 max-w-[80%]">
      <h3 className="font-semibold text-success-700 text-lg">
        🎯 Rank Prediction Result
      </h3>
      <Divider className="my-2" />
      <p className="whitespace-pre-line text-sm text-foreground">
        {data.answer}
      </p>

      {prediction && (
        <div className="mt-3 text-sm text-foreground-600 space-y-1">
          <p>
            <strong>Campus:</strong> {prediction.campus}
          </p>
          <p>
            <strong>Branch:</strong> {prediction.branch}
          </p>

          {/* ✅ Added this new line */}
          <p>
            <strong>Category:</strong> {prediction.category}
          </p>

          <p>
            <strong>Confidence:</strong>{" "}
            {(prediction.confidence_score * 100).toFixed(0)}%
          </p>
          <Divider className="my-2" />
          <p className="font-medium">
            Predicted 2025 Rank Range:{" "}
            {prediction.prediction.predicted_min_rank} -{" "}
            {prediction.prediction.predicted_max_rank}
          </p>
          <p>
            📈 Trend: {prediction.prediction.trend_direction} (
            {prediction.prediction.avg_yearly_change}% avg yearly change)
          </p>
        </div>
      )}
    </Card>
  );
}
