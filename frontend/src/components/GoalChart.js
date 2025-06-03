import React, { useState, useEffect } from "react";
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
  BarChart,
  Bar,
} from "recharts";
import { goalsAPI } from "../api";

const GoalChart = ({ projectId }) => {
  const [goals, setGoals] = useState([]);
  const [chartData, setChartData] = useState([]);
  const [newGoal, setNewGoal] = useState({ description: "", week_start: "" });
  const [showAddGoal, setShowAddGoal] = useState(false);

  useEffect(() => {
    // Mock data for goals progress
    const mockData = [
      {
        week: "Week 1",
        target: 100,
        achieved: 85,
        goalCount: 5,
        completedGoals: 4,
      },
      {
        week: "Week 2",
        target: 120,
        achieved: 110,
        goalCount: 6,
        completedGoals: 5,
      },
      {
        week: "Week 3",
        target: 150,
        achieved: 140,
        goalCount: 7,
        completedGoals: 6,
      },
      {
        week: "Week 4",
        target: 180,
        achieved: 175,
        goalCount: 8,
        completedGoals: 7,
      },
    ];
    setChartData(mockData);

    // Mock goals list
    setGoals([
      {
        id: 1,
        description: "Complete 5 client calls",
        week_start: "2024-01-01",
        achieved: true,
      },
      {
        id: 2,
        description: "Close 2 deals",
        week_start: "2024-01-01",
        achieved: true,
      },
      {
        id: 3,
        description: "Generate 10 leads",
        week_start: "2024-01-08",
        achieved: false,
      },
      {
        id: 4,
        description: "Follow up with prospects",
        week_start: "2024-01-08",
        achieved: true,
      },
    ]);
  }, [projectId]);

  const handleAddGoal = async () => {
    if (newGoal.description.trim() && newGoal.week_start) {
      try {
        // const response = await goalsAPI.create(newGoal, projectId);
        const goal = {
          id: Date.now(),
          description: newGoal.description,
          week_start: newGoal.week_start,
          achieved: false,
        };
        setGoals((prev) => [...prev, goal]);
        setNewGoal({ description: "", week_start: "" });
        setShowAddGoal(false);
      } catch (error) {
        console.error("Error creating goal:", error);
      }
    }
  };

  const toggleGoalAchievement = (goalId) => {
    setGoals((prev) =>
      prev.map((goal) =>
        goal.id === goalId ? { ...goal, achieved: !goal.achieved } : goal
      )
    );
  };

  const getCurrentWeekGoals = () => {
    const currentWeek = new Date().toISOString().split("T")[0];
    return goals.filter((goal) => {
      const goalWeek = new Date(goal.week_start);
      const current = new Date(currentWeek);
      const weekDiff = Math.abs(current - goalWeek) / (1000 * 60 * 60 * 24 * 7);
      return weekDiff < 1;
    });
  };

  return (
    <div className="p-6">
      <div className="flex justify-between items-center mb-6">
        <h2 className="text-2xl font-bold text-gray-800">Goal Progress</h2>
        <button
          onClick={() => setShowAddGoal(true)}
          className="bg-green-600 hover:bg-green-700 text-white px-4 py-2 rounded-lg"
        >
          + Add Goal
        </button>
      </div>

      {showAddGoal && (
        <div className="bg-white p-4 rounded-lg shadow-md mb-6 border">
          <h3 className="font-semibold mb-3">Add New Goal</h3>
          <input
            type="text"
            placeholder="Goal description"
            value={newGoal.description}
            onChange={(e) =>
              setNewGoal((prev) => ({ ...prev, description: e.target.value }))
            }
            className="w-full p-2 border border-gray-300 rounded mb-3"
          />
          <input
            type="date"
            value={newGoal.week_start}
            onChange={(e) =>
              setNewGoal((prev) => ({ ...prev, week_start: e.target.value }))
            }
            className="w-full p-2 border border-gray-300 rounded mb-3"
          />
          <div className="flex gap-2">
            <button
              onClick={handleAddGoal}
              className="bg-green-600 hover:bg-green-700 text-white px-4 py-2 rounded"
            >
              Add Goal
            </button>
            <button
              onClick={() => setShowAddGoal(false)}
              className="bg-gray-500 hover:bg-gray-600 text-white px-4 py-2 rounded"
            >
              Cancel
            </button>
          </div>
        </div>
      )}

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-6">
        {/* Progress Line Chart */}
        <div className="bg-white p-6 rounded-lg shadow-md">
          <h3 className="text-lg font-semibold mb-4">Weekly Progress Trend</h3>
          <ResponsiveContainer width="100%" height={300}>
            <LineChart data={chartData}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="week" />
              <YAxis />
              <Tooltip />
              <Legend />
              <Line
                type="monotone"
                dataKey="target"
                stroke="#ef4444"
                strokeWidth={2}
                name="Target"
              />
              <Line
                type="monotone"
                dataKey="achieved"
                stroke="#22c55e"
                strokeWidth={2}
                name="Achieved"
              />
            </LineChart>
          </ResponsiveContainer>
        </div>

        {/* Goals Completion Bar Chart */}
        <div className="bg-white p-6 rounded-lg shadow-md">
          <h3 className="text-lg font-semibold mb-4">Goals Completion</h3>
          <ResponsiveContainer width="100%" height={300}>
            <BarChart data={chartData}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="week" />
              <YAxis />
              <Tooltip />
              <Legend />
              <Bar dataKey="goalCount" fill="#3b82f6" name="Total Goals" />
              <Bar
                dataKey="completedGoals"
                fill="#22c55e"
                name="Completed Goals"
              />
            </BarChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* Current Week Goals */}
      <div className="bg-white p-6 rounded-lg shadow-md">
        <h3 className="text-lg font-semibold mb-4">This Week's Goals</h3>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {getCurrentWeekGoals().map((goal) => (
            <div
              key={goal.id}
              className={`p-4 rounded-lg border-2 cursor-pointer transition-colors ${
                goal.achieved
                  ? "border-green-500 bg-green-50"
                  : "border-gray-300 bg-white hover:border-blue-500"
              }`}
              onClick={() => toggleGoalAchievement(goal.id)}
            >
              <div className="flex items-center justify-between">
                <p
                  className={`font-medium ${
                    goal.achieved ? "text-green-800" : "text-gray-800"
                  }`}
                >
                  {goal.description}
                </p>
                <div
                  className={`w-6 h-6 rounded-full border-2 flex items-center justify-center ${
                    goal.achieved
                      ? "border-green-500 bg-green-500"
                      : "border-gray-300"
                  }`}
                >
                  {goal.achieved && (
                    <svg
                      className="w-4 h-4 text-white"
                      fill="currentColor"
                      viewBox="0 0 20 20"
                    >
                      <path
                        fillRule="evenodd"
                        d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z"
                        clipRule="evenodd"
                      />
                    </svg>
                  )}
                </div>
              </div>
              <p className="text-sm text-gray-500 mt-2">
                Week of {new Date(goal.week_start).toLocaleDateString()}
              </p>
            </div>
          ))}
        </div>
      </div>

      {/* All Goals List */}
      <div className="bg-white p-6 rounded-lg shadow-md mt-6">
        <h3 className="text-lg font-semibold mb-4">All Goals</h3>
        <div className="space-y-3">
          {goals.map((goal) => (
            <div
              key={goal.id}
              className={`p-3 rounded border flex items-center justify-between ${
                goal.achieved
                  ? "bg-green-50 border-green-200"
                  : "bg-gray-50 border-gray-200"
              }`}
            >
              <div>
                <p
                  className={`font-medium ${
                    goal.achieved
                      ? "text-green-800 line-through"
                      : "text-gray-800"
                  }`}
                >
                  {goal.description}
                </p>
                <p className="text-sm text-gray-500">
                  Week of {new Date(goal.week_start).toLocaleDateString()}
                </p>
              </div>
              <button
                onClick={() => toggleGoalAchievement(goal.id)}
                className={`px-3 py-1 rounded text-sm ${
                  goal.achieved
                    ? "bg-green-600 text-white hover:bg-green-700"
                    : "bg-gray-600 text-white hover:bg-gray-700"
                }`}
              >
                {goal.achieved ? "Achieved" : "Mark Complete"}
              </button>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};

export default GoalChart;
