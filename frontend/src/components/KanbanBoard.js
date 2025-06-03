import React, { useState, useEffect } from "react";
import { tasksAPI } from "../api";

const KanbanBoard = ({ projectId }) => {
  const [tasks, setTasks] = useState({
    todo: [],
    inProgress: [],
    done: [],
  });

  const [newTask, setNewTask] = useState({ title: "", description: "" });
  const [showAddTask, setShowAddTask] = useState(false);

  useEffect(() => {
    // In a real app, you'd fetch tasks by project ID
    // For now, we'll use mock data
    setTasks({
      todo: [
        {
          id: 1,
          title: "Design UI mockups",
          description: "Create wireframes for dashboard",
          completed: false,
        },
        {
          id: 2,
          title: "Set up database",
          description: "Configure PostgreSQL",
          completed: false,
        },
      ],
      inProgress: [
        {
          id: 3,
          title: "Implement API endpoints",
          description: "Build FastAPI routes",
          completed: false,
        },
      ],
      done: [
        {
          id: 4,
          title: "Project setup",
          description: "Initialize repository",
          completed: true,
        },
      ],
    });
  }, [projectId]);

  const handleAddTask = async () => {
    if (newTask.title.trim()) {
      try {
        // const response = await tasksAPI.create(newTask, projectId);
        // For now, add to todo column
        const task = {
          id: Date.now(),
          title: newTask.title,
          description: newTask.description,
          completed: false,
        };
        setTasks((prev) => ({
          ...prev,
          todo: [...prev.todo, task],
        }));
        setNewTask({ title: "", description: "" });
        setShowAddTask(false);
      } catch (error) {
        console.error("Error creating task:", error);
      }
    }
  };

  const moveTask = (taskId, fromColumn, toColumn) => {
    setTasks((prev) => {
      const task = prev[fromColumn].find((t) => t.id === taskId);
      return {
        ...prev,
        [fromColumn]: prev[fromColumn].filter((t) => t.id !== taskId),
        [toColumn]: [...prev[toColumn], task],
      };
    });
  };

  const TaskCard = ({ task, column }) => (
    <div className="bg-white p-4 rounded-lg shadow-sm border border-gray-200 mb-3">
      <h4 className="font-semibold text-gray-800 mb-2">{task.title}</h4>
      <p className="text-gray-600 text-sm mb-3">{task.description}</p>
      <div className="flex gap-2">
        {column !== "todo" && (
          <button
            onClick={() =>
              moveTask(
                task.id,
                column,
                column === "inProgress" ? "todo" : "inProgress"
              )
            }
            className="text-xs bg-gray-100 hover:bg-gray-200 px-2 py-1 rounded"
          >
            ← Move Back
          </button>
        )}
        {column !== "done" && (
          <button
            onClick={() =>
              moveTask(
                task.id,
                column,
                column === "todo" ? "inProgress" : "done"
              )
            }
            className="text-xs bg-blue-100 hover:bg-blue-200 text-blue-700 px-2 py-1 rounded"
          >
            Move Forward →
          </button>
        )}
      </div>
    </div>
  );

  const Column = ({ title, tasks, column, bgColor }) => (
    <div className="flex-1 bg-gray-50 rounded-lg p-4">
      <div
        className={`${bgColor} text-white px-3 py-2 rounded-lg mb-4 text-center font-semibold`}
      >
        {title} ({tasks.length})
      </div>
      <div className="space-y-3">
        {tasks.map((task) => (
          <TaskCard key={task.id} task={task} column={column} />
        ))}
      </div>
    </div>
  );

  return (
    <div className="p-6">
      <div className="flex justify-between items-center mb-6">
        <h2 className="text-2xl font-bold text-gray-800">Project Tasks</h2>
        <button
          onClick={() => setShowAddTask(true)}
          className="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-lg"
        >
          + Add Task
        </button>
      </div>

      {showAddTask && (
        <div className="bg-white p-4 rounded-lg shadow-md mb-6 border">
          <h3 className="font-semibold mb-3">Add New Task</h3>
          <input
            type="text"
            placeholder="Task title"
            value={newTask.title}
            onChange={(e) =>
              setNewTask((prev) => ({ ...prev, title: e.target.value }))
            }
            className="w-full p-2 border border-gray-300 rounded mb-3"
          />
          <textarea
            placeholder="Task description"
            value={newTask.description}
            onChange={(e) =>
              setNewTask((prev) => ({ ...prev, description: e.target.value }))
            }
            className="w-full p-2 border border-gray-300 rounded mb-3"
            rows="3"
          />
          <div className="flex gap-2">
            <button
              onClick={handleAddTask}
              className="bg-green-600 hover:bg-green-700 text-white px-4 py-2 rounded"
            >
              Add Task
            </button>
            <button
              onClick={() => setShowAddTask(false)}
              className="bg-gray-500 hover:bg-gray-600 text-white px-4 py-2 rounded"
            >
              Cancel
            </button>
          </div>
        </div>
      )}

      <div className="flex gap-6">
        <Column
          title="To Do"
          tasks={tasks.todo}
          column="todo"
          bgColor="bg-red-500"
        />
        <Column
          title="In Progress"
          tasks={tasks.inProgress}
          column="inProgress"
          bgColor="bg-yellow-500"
        />
        <Column
          title="Done"
          tasks={tasks.done}
          column="done"
          bgColor="bg-green-500"
        />
      </div>
    </div>
  );
};

export default KanbanBoard;
