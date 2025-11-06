import React from "react";
import { Card, Divider } from "@heroui/react";

export default function RankPredictionCard({ data }) {
  // Get top 5 predictions sorted by confidence score
  const predictions = (data.rank_prediction?.predictions || [])
    .sort((a, b) => b.confidence_score - a.confidence_score)
    .slice(0, 5);
  const userRank = data.rank_prediction?.rank;

  const getConfidenceColor = (confidence) => {
    switch (confidence) {
      case "High": return "bg-success-100 text-success-700";
      case "Good": return "bg-warning-100 text-warning-700";
      default: return "bg-error-100 text-error-700";
    }
  };

  return (
    <Card className="p-6 bg-gradient-to-br from-success-50 to-success-100 border border-success-200 max-w-[80%] shadow-lg">
      <div className="flex items-center justify-between mb-4">
        <h3 className="font-bold text-success-800 text-xl">
          🎯 Rank Prediction Analysis
        </h3>
        <span className="bg-success-200 text-success-800 px-3 py-1 rounded-full text-sm font-medium">
          Rank: {userRank}
        </span>
      </div>
      
      <Divider className="mb-4" />

      {predictions.length > 0 && (
        <div className="space-y-4">
          {predictions.map((prediction, index) => (
            <div 
              key={index} 
              className="bg-white rounded-xl border border-success-200 overflow-hidden shadow-sm hover:shadow-md transition-shadow duration-200"
            >
              <div className="p-4">
                <div className="flex justify-between items-start mb-3">
                  <div className="flex-1">
                    <h4 className="font-semibold text-gray-800 text-lg mb-1">
                      {prediction.branch}
                    </h4>
                    <p className="text-gray-600 text-sm">
                      {prediction.campus} • {prediction.category}
                    </p>
                  </div>
                  <span className={`px-3 py-1 rounded-full text-sm font-medium ${getConfidenceColor(prediction.confidence)}`}>
                    {(prediction.confidence_score * 100).toFixed(0)}% Confidence
                  </span>
                </div>

                <div className="grid grid-cols-2 gap-4 mt-4">
                  <div className="bg-gray-50 p-3 rounded-lg">
                    <p className="text-sm text-gray-600 mb-1">2025 Predicted Range</p>
                    <p className="font-mono font-medium text-gray-800">
                      {prediction.rank_range[0].toLocaleString()} - {prediction.rank_range[1].toLocaleString()}
                    </p>
                  </div>
                  
                  <div className="bg-gray-50 p-3 rounded-lg">
                    <p className="text-sm text-gray-600 mb-1">Historical Data</p>
                    <div className="space-y-1 font-mono text-sm">
                      {Object.entries(prediction.historical_data).map(([year, range]) => (
                        <p key={year} className="text-gray-700">
                          {year}: {range[0].toLocaleString()} - {range[1].toLocaleString()}
                        </p>
                      ))}
                    </div>
                  </div>
                </div>

                {prediction.notes && (
                  <div className="mt-3 text-sm text-gray-500 italic bg-gray-50 p-2 rounded">
                    📝 {prediction.notes}
                  </div>
                )}
              </div>
            </div>
          ))}
        </div>
      )}
      
      <div className="mt-4 text-sm text-gray-600 bg-white p-3 rounded-lg">
        {data.answer}
      </div>
    </Card>
  );
}