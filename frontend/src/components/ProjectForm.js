import React, { useState, useEffect } from "react";
import { projectsAPI } from "../api";

const ProjectForm = ({ onProjectCreated }) => {
  const [projects, setProjects] = useState([]);
  const [newProject, setNewProject] = useState({ name: "", description: "" });
  const [showForm, setShowForm] = useState(false);
  const [editingProject, setEditingProject] = useState(null);

  useEffect(() => {
    // Mock projects data
    setProjects([
      {
        id: 1,
        name: "Sales Dashboard",
        description: "Build a comprehensive sales tracking dashboard",
        owner_id: 1,
      },
      {
        id: 2,
        name: "Client Onboarding",
        description: "Streamline the client onboarding process",
        owner_id: 1,
      },
      {
        id: 3,
        name: "Marketing Campaign",
        description: "Q1 marketing campaign for new product launch",
        owner_id: 1,
      },
    ]);
  }, []);

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (newProject.name.trim()) {
      try {
        if (editingProject) {
          // Update existing project
          setProjects((prev) =>
            prev.map((p) =>
              p.id === editingProject.id
                ? {
                    ...p,
                    name: newProject.name,
                    description: newProject.description,
                  }
                : p
            )
          );
        } else {
          // Create new project
          // const response = await projectsAPI.create(newProject, 1); // owner_id = 1 for demo
          const project = {
            id: Date.now(),
            name: newProject.name,
            description: newProject.description,
            owner_id: 1,
          };
          setProjects((prev) => [...prev, project]);
          if (onProjectCreated) onProjectCreated(project);
        }

        setNewProject({ name: "", description: "" });
        setShowForm(false);
        setEditingProject(null);
      } catch (error) {
        console.error("Error saving project:", error);
      }
    }
  };

  const handleEdit = (project) => {
    setNewProject({ name: project.name, description: project.description });
    setEditingProject(project);
    setShowForm(true);
  };

  const handleDelete = (projectId) => {
    if (window.confirm("Are you sure you want to delete this project?")) {
      setProjects((prev) => prev.filter((p) => p.id !== projectId));
    }
  };

  const handleCancel = () => {
    setNewProject({ name: "", description: "" });
    setEditingProject(null);
    setShowForm(false);
  };

  return (
    <div className="p-6">
      <div className="flex justify-between items-center mb-6">
        <h2 className="text-2xl font-bold text-gray-800">Project Management</h2>
        <button
          onClick={() => setShowForm(true)}
          className="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-lg"
        >
          + New Project
        </button>
      </div>

      {showForm && (
        <div className="bg-white p-6 rounded-lg shadow-md mb-6 border">
          <h3 className="text-lg font-semibold mb-4">
            {editingProject ? "Edit Project" : "Create New Project"}
          </h3>
          <form onSubmit={handleSubmit}>
            <div className="mb-4">
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Project Name
              </label>
              <input
                type="text"
                value={newProject.name}
                onChange={(e) =>
                  setNewProject((prev) => ({ ...prev, name: e.target.value }))
                }
                className="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                placeholder="Enter project name"
                required
              />
            </div>
            <div className="mb-6">
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Description
              </label>
              <textarea
                value={newProject.description}
                onChange={(e) =>
                  setNewProject((prev) => ({
                    ...prev,
                    description: e.target.value,
                  }))
                }
                className="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                placeholder="Enter project description"
                rows="4"
              />
            </div>
            <div className="flex gap-3">
              <button
                type="submit"
                className="bg-green-600 hover:bg-green-700 text-white px-6 py-2 rounded-lg"
              >
                {editingProject ? "Update Project" : "Create Project"}
              </button>
              <button
                type="button"
                onClick={handleCancel}
                className="bg-gray-500 hover:bg-gray-600 text-white px-6 py-2 rounded-lg"
              >
                Cancel
              </button>
            </div>
          </form>
        </div>
      )}

      {/* Projects Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {projects.map((project) => (
          <div
            key={project.id}
            className="bg-white rounded-lg shadow-md border border-gray-200 overflow-hidden"
          >
            <div className="p-6">
              <div className="flex justify-between items-start mb-3">
                <h3 className="text-lg font-semibold text-gray-800">
                  {project.name}
                </h3>
                <div className="flex gap-2">
                  <button
                    onClick={() => handleEdit(project)}
                    className="text-blue-600 hover:text-blue-800 p-1"
                    title="Edit project"
                  >
                    <svg
                      className="w-4 h-4"
                      fill="currentColor"
                      viewBox="0 0 20 20"
                    >
                      <path d="M13.586 3.586a2 2 0 112.828 2.828l-.793.793-2.828-2.828.793-.793zM11.379 5.793L3 14.172V17h2.828l8.38-8.379-2.83-2.828z" />
                    </svg>
                  </button>
                  <button
                    onClick={() => handleDelete(project.id)}
                    className="text-red-600 hover:text-red-800 p-1"
                    title="Delete project"
                  >
                    <svg
                      className="w-4 h-4"
                      fill="currentColor"
                      viewBox="0 0 20 20"
                    >
                      <path
                        fillRule="evenodd"
                        d="M9 2a1 1 0 000 2h2a1 1 0 100-2H9zM4 5a2 2 0 012-2h8a2 2 0 012 2v6a2 2 0 01-2 2H6a2 2 0 01-2-2V5zm3 4a1 1 0 102 0v3a1 1 0 11-2 0V9zm4 0a1 1 0 10-2 0v3a1 1 0 102 0V9z"
                        clipRule="evenodd"
                      />
                    </svg>
                  </button>
                </div>
              </div>
              <p className="text-gray-600 text-sm mb-4">
                {project.description}
              </p>
              <div className="flex justify-between items-center">
                <span className="text-xs text-gray-500">
                  Owner ID: {project.owner_id}
                </span>
                <button
                  onClick={() => onProjectCreated && onProjectCreated(project)}
                  className="bg-blue-100 hover:bg-blue-200 text-blue-700 px-3 py-1 rounded text-sm"
                >
                  View Details
                </button>
              </div>
            </div>
          </div>
        ))}
      </div>

      {projects.length === 0 && (
        <div className="text-center py-12">
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
            No projects yet
          </h3>
          <p className="text-gray-500 mb-4">
            Get started by creating your first project.
          </p>
          <button
            onClick={() => setShowForm(true)}
            className="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-lg"
          >
            Create Project
          </button>
        </div>
      )}
    </div>
  );
};

export default ProjectForm;
