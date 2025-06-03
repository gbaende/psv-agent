import React, { useState } from "react";
import KanbanBoard from "../components/KanbanBoard";
import GoalChart from "../components/GoalChart";
import ProjectForm from "../components/ProjectForm";

const Dashboard = () => {
  const [activeTab, setActiveTab] = useState("projects");
  const [selectedProject, setSelectedProject] = useState(null);

  const tabs = [
    { id: "projects", name: "Projects", icon: "📋" },
    { id: "kanban", name: "Tasks", icon: "📝" },
    { id: "goals", name: "Goals", icon: "🎯" },
  ];

  const handleProjectSelect = (project) => {
    setSelectedProject(project);
    setActiveTab("kanban");
  };

  return (
    <div className="min-h-screen bg-gray-100">
      {/* Header */}
      <header className="bg-white shadow-sm border-b border-gray-200">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center py-6">
            <div className="flex items-center">
              <h1 className="text-3xl font-bold text-gray-900">DealTracker</h1>
              <span className="ml-3 px-3 py-1 bg-blue-100 text-blue-800 text-sm font-medium rounded-full">
                Dashboard
              </span>
            </div>
            <div className="flex items-center space-x-4">
              <div className="text-sm text-gray-500">Welcome back, User!</div>
              <div className="w-8 h-8 bg-blue-600 rounded-full flex items-center justify-center">
                <span className="text-white text-sm font-medium">U</span>
              </div>
            </div>
          </div>
        </div>
      </header>

      {/* Navigation Tabs */}
      <nav className="bg-white shadow-sm">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex space-x-8">
            {tabs.map((tab) => (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id)}
                className={`py-4 px-1 border-b-2 font-medium text-sm flex items-center space-x-2 ${
                  activeTab === tab.id
                    ? "border-blue-500 text-blue-600"
                    : "border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300"
                }`}
              >
                <span>{tab.icon}</span>
                <span>{tab.name}</span>
              </button>
            ))}
          </div>
        </div>
      </nav>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto py-6 sm:px-6 lg:px-8">
        {/* Project Selection Info */}
        {selectedProject && activeTab !== "projects" && (
          <div className="mb-6 bg-blue-50 border border-blue-200 rounded-lg p-4">
            <div className="flex items-center justify-between">
              <div>
                <h3 className="text-lg font-medium text-blue-900">
                  Current Project: {selectedProject.name}
                </h3>
                <p className="text-blue-700">{selectedProject.description}</p>
              </div>
              <button
                onClick={() => setActiveTab("projects")}
                className="text-blue-600 hover:text-blue-800 text-sm font-medium"
              >
                Change Project →
              </button>
            </div>
          </div>
        )}

        {/* Tab Content */}
        <div className="bg-white rounded-lg shadow">
          {activeTab === "projects" && (
            <ProjectForm onProjectCreated={handleProjectSelect} />
          )}

          {activeTab === "kanban" && (
            <div>
              {selectedProject ? (
                <KanbanBoard projectId={selectedProject.id} />
              ) : (
                <div className="p-12 text-center">
                  <div className="text-gray-400 mb-4">
                    <svg
                      className="w-16 h-16 mx-auto"
                      fill="currentColor"
                      viewBox="0 0 20 20"
                    >
                      <path
                        fillRule="evenodd"
                        d="M3 4a1 1 0 011-1h12a1 1 0 110 2H4a1 1 0 01-1-1zm0 4a1 1 0 011-1h12a1 1 0 110 2H4a1 1 0 01-1-1zm0 4a1 1 0 011-1h12a1 1 0 110 2H4a1 1 0 01-1-1z"
                        clipRule="evenodd"
                      />
                    </svg>
                  </div>
                  <h3 className="text-lg font-medium text-gray-900 mb-2">
                    No project selected
                  </h3>
                  <p className="text-gray-500 mb-4">
                    Please select a project to view its tasks.
                  </p>
                  <button
                    onClick={() => setActiveTab("projects")}
                    className="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-lg"
                  >
                    Go to Projects
                  </button>
                </div>
              )}
            </div>
          )}

          {activeTab === "goals" && (
            <div>
              {selectedProject ? (
                <GoalChart projectId={selectedProject.id} />
              ) : (
                <div className="p-12 text-center">
                  <div className="text-gray-400 mb-4">
                    <svg
                      className="w-16 h-16 mx-auto"
                      fill="currentColor"
                      viewBox="0 0 20 20"
                    >
                      <path
                        fillRule="evenodd"
                        d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-8.293l-3-3a1 1 0 00-1.414 1.414L10.586 9.5 9.293 10.793a1 1 0 101.414 1.414l3-3a1 1 0 000-1.414z"
                        clipRule="evenodd"
                      />
                    </svg>
                  </div>
                  <h3 className="text-lg font-medium text-gray-900 mb-2">
                    No project selected
                  </h3>
                  <p className="text-gray-500 mb-4">
                    Please select a project to view its goals.
                  </p>
                  <button
                    onClick={() => setActiveTab("projects")}
                    className="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-lg"
                  >
                    Go to Projects
                  </button>
                </div>
              )}
            </div>
          )}
        </div>
      </main>

      {/* Footer */}
      <footer className="bg-white border-t border-gray-200 mt-12">
        <div className="max-w-7xl mx-auto py-6 px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center">
            <p className="text-gray-500 text-sm">
              © 2024 DealTracker. Built with FastAPI + React.
            </p>
            <div className="flex space-x-6">
              <span className="text-green-500 text-sm">
                ● Frontend Connected
              </span>
              <span className="text-yellow-500 text-sm">● Backend Pending</span>
            </div>
          </div>
        </div>
      </footer>
    </div>
  );
};

export default Dashboard;
