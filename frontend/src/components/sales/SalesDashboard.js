import React, { useState, useEffect } from "react";
import {
  Trophy,
  Target,
  TrendingUp,
  Users,
  Calendar,
  MessageCircle,
  BarChart3,
  Clock,
  CheckCircle,
  Zap,
  Award,
  Star,
  Phone,
  Video,
  FileText,
  X,
  Send,
} from "lucide-react";

const SalesDashboard = () => {
  const [teamProgress, setTeamProgress] = useState([]);
  const [leaderboard, setLeaderboard] = useState([]);
  const [schedulerStatus, setSchedulerStatus] = useState([]);
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState("team");

  // New state for modals
  const [showCoachingModal, setShowCoachingModal] = useState(false);
  const [showMessageModal, setShowMessageModal] = useState(false);
  const [selectedUser, setSelectedUser] = useState(null);
  const [coachingTips, setCoachingTips] = useState([]);
  const [customMessage, setCustomMessage] = useState("");
  const [loadingTips, setLoadingTips] = useState(false);
  const [sendingMessage, setSendingMessage] = useState(false);

  useEffect(() => {
    fetchDashboardData();
    const interval = setInterval(fetchDashboardData, 30000); // Refresh every 30 seconds
    return () => clearInterval(interval);
  }, []);

  const fetchDashboardData = async () => {
    try {
      const [progressResponse, leaderboardResponse, schedulerResponse] =
        await Promise.all([
          fetch("/api/sales/progress/team"),
          fetch("/api/sales/leaderboard/current"),
          fetch("/api/sales/scheduler/status"),
        ]);

      if (progressResponse.ok) {
        setTeamProgress(await progressResponse.json());
      }
      if (leaderboardResponse.ok) {
        setLeaderboard(await leaderboardResponse.json());
      }
      if (schedulerResponse.ok) {
        const schedulerData = await schedulerResponse.json();
        setSchedulerStatus(schedulerData.data?.jobs || []);
      }
    } catch (error) {
      console.error("Error fetching dashboard data:", error);
    } finally {
      setLoading(false);
    }
  };

  const fetchCoachingTips = async (userId) => {
    setLoadingTips(true);
    try {
      const response = await fetch(`/api/sales/coaching/${userId}/tips`);
      if (response.ok) {
        const data = await response.json();
        let tips = data.data.tips || [];

        // Handle both string and array responses
        if (typeof tips === "string") {
          // Split string response into individual tips
          tips = tips.split("\n").filter((tip) => tip.trim().length > 0);
        }

        setCoachingTips(tips);
      } else {
        console.error("Failed to fetch coaching tips");
        setCoachingTips(["Unable to load coaching tips at this time."]);
      }
    } catch (error) {
      console.error("Error fetching coaching tips:", error);
      setCoachingTips(["Error loading coaching tips. Please try again."]);
    } finally {
      setLoadingTips(false);
    }
  };

  const sendCustomMessage = async () => {
    if (!customMessage.trim() || !selectedUser) return;

    setSendingMessage(true);
    try {
      const response = await fetch(
        `/api/sales/coaching/${selectedUser.user_id}/send`,
        {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({ message: customMessage }),
        }
      );

      if (response.ok) {
        alert(`Message sent successfully to ${selectedUser.user_name}!`);
        setCustomMessage("");
        setShowMessageModal(false);
      } else {
        const errorData = await response.json();
        alert(`Failed to send message: ${errorData.detail || "Unknown error"}`);
      }
    } catch (error) {
      console.error("Error sending message:", error);
      alert("Error sending message. Please try again.");
    } finally {
      setSendingMessage(false);
    }
  };

  const openCoachingModal = (user) => {
    setSelectedUser(user);
    setShowCoachingModal(true);
    fetchCoachingTips(user.user_id);
  };

  const openMessageModal = (user) => {
    setSelectedUser(user);
    setShowMessageModal(true);
    setCustomMessage(`Hi ${user.user_name}! `);
  };

  const triggerSchedulerJob = async (jobType) => {
    try {
      const response = await fetch(`/api/sales/triggers/${jobType}`, {
        method: "POST",
      });

      if (response.ok) {
        alert(`${jobType} triggered successfully!`);
        fetchDashboardData();
      } else {
        alert(`Failed to trigger ${jobType}`);
      }
    } catch (error) {
      console.error("Error triggering job:", error);
      alert("Error triggering job");
    }
  };

  const getPerformanceColor = (percentage) => {
    if (percentage >= 100) return "text-green-600 bg-green-100";
    if (percentage >= 80) return "text-blue-600 bg-blue-100";
    if (percentage >= 60) return "text-yellow-600 bg-yellow-100";
    return "text-red-600 bg-red-100";
  };

  const getRankIcon = (rank) => {
    switch (rank) {
      case 1:
        return <Trophy className="w-5 h-5 text-yellow-500" />;
      case 2:
        return <Award className="w-5 h-5 text-gray-400" />;
      case 3:
        return <Star className="w-5 h-5 text-orange-400" />;
      default:
        return (
          <span className="w-5 h-5 text-gray-600 font-semibold">{rank}</span>
        );
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto"></div>
          <p className="mt-4 text-gray-600">Loading sales dashboard...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <div className="bg-white shadow-sm border-b">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between h-16">
            <div className="flex items-center space-x-4">
              <Zap className="w-8 h-8 text-blue-600" />
              <h1 className="text-2xl font-bold text-gray-900">
                SalesPM Dashboard
              </h1>
              <span className="px-3 py-1 bg-green-100 text-green-800 rounded-full text-sm font-medium">
                🤖 AI Agent Active
              </span>
            </div>
            <div className="flex items-center space-x-4">
              <Clock className="w-5 h-5 text-gray-400" />
              <span className="text-sm text-gray-600">
                Last updated: {new Date().toLocaleTimeString()}
              </span>
            </div>
          </div>
        </div>
      </div>

      {/* Navigation Tabs */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 pt-6">
        <div className="border-b border-gray-200">
          <nav className="-mb-px flex space-x-8">
            {[
              { id: "team", label: "Team Progress", icon: Users },
              { id: "leaderboard", label: "Leaderboard", icon: Trophy },
              { id: "automation", label: "AI Automation", icon: Zap },
              { id: "analytics", label: "Analytics", icon: BarChart3 },
            ].map(({ id, label, icon: Icon }) => (
              <button
                key={id}
                onClick={() => setActiveTab(id)}
                className={`flex items-center space-x-2 py-2 px-1 border-b-2 font-medium text-sm ${
                  activeTab === id
                    ? "border-blue-500 text-blue-600"
                    : "border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300"
                }`}
              >
                <Icon className="w-4 h-4" />
                <span>{label}</span>
              </button>
            ))}
          </nav>
        </div>
      </div>

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Team Progress Tab */}
        {activeTab === "team" && (
          <div className="space-y-6">
            {/* Quick Stats */}
            <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
              <div className="bg-white p-6 rounded-lg shadow-sm border">
                <div className="flex items-center">
                  <Users className="w-8 h-8 text-blue-600" />
                  <div className="ml-4">
                    <p className="text-sm text-gray-600">Team Size</p>
                    <p className="text-2xl font-bold text-gray-900">
                      {teamProgress.length}
                    </p>
                  </div>
                </div>
              </div>
              <div className="bg-white p-6 rounded-lg shadow-sm border">
                <div className="flex items-center">
                  <Target className="w-8 h-8 text-green-600" />
                  <div className="ml-4">
                    <p className="text-sm text-gray-600">Avg Progress</p>
                    <p className="text-2xl font-bold text-gray-900">
                      {teamProgress.length > 0
                        ? Math.round(
                            teamProgress.reduce(
                              (sum, member) => sum + member.overall_percentage,
                              0
                            ) / teamProgress.length
                          )
                        : 0}
                      %
                    </p>
                  </div>
                </div>
              </div>
              <div className="bg-white p-6 rounded-lg shadow-sm border">
                <div className="flex items-center">
                  <CheckCircle className="w-8 h-8 text-purple-600" />
                  <div className="ml-4">
                    <p className="text-sm text-gray-600">On Target</p>
                    <p className="text-2xl font-bold text-gray-900">
                      {
                        teamProgress.filter(
                          (member) => member.overall_percentage >= 80
                        ).length
                      }
                    </p>
                  </div>
                </div>
              </div>
              <div className="bg-white p-6 rounded-lg shadow-sm border">
                <div className="flex items-center">
                  <TrendingUp className="w-8 h-8 text-orange-600" />
                  <div className="ml-4">
                    <p className="text-sm text-gray-600">Exceeding</p>
                    <p className="text-2xl font-bold text-gray-900">
                      {
                        teamProgress.filter(
                          (member) => member.overall_percentage > 100
                        ).length
                      }
                    </p>
                  </div>
                </div>
              </div>
            </div>

            {/* Team Progress Cards */}
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              {teamProgress.map((member) => (
                <div
                  key={member.user_id}
                  className="bg-white rounded-lg shadow-sm border overflow-hidden"
                >
                  <div className="p-6">
                    <div className="flex items-center justify-between mb-4">
                      <div className="flex items-center space-x-3">
                        {getRankIcon(member.rank)}
                        <h3 className="text-lg font-semibold text-gray-900">
                          {member.user_name}
                        </h3>
                      </div>
                      <span
                        className={`px-3 py-1 rounded-full text-sm font-medium ${getPerformanceColor(
                          member.overall_percentage
                        )}`}
                      >
                        {member.overall_percentage}% Complete
                      </span>
                    </div>

                    {/* Progress Bars */}
                    <div className="space-y-4">
                      <div>
                        <div className="flex items-center justify-between mb-2">
                          <div className="flex items-center space-x-2">
                            <Phone className="w-4 h-4 text-blue-600" />
                            <span className="text-sm font-medium text-gray-700">
                              Calls
                            </span>
                          </div>
                          <span className="text-sm text-gray-600">
                            {member.calls_completed}/{member.calls_target}
                          </span>
                        </div>
                        <div className="w-full bg-gray-200 rounded-full h-2">
                          <div
                            className="bg-blue-600 h-2 rounded-full"
                            style={{
                              width: `${Math.min(
                                member.calls_percentage,
                                100
                              )}%`,
                            }}
                          ></div>
                        </div>
                      </div>

                      <div>
                        <div className="flex items-center justify-between mb-2">
                          <div className="flex items-center space-x-2">
                            <Video className="w-4 h-4 text-green-600" />
                            <span className="text-sm font-medium text-gray-700">
                              Demos
                            </span>
                          </div>
                          <span className="text-sm text-gray-600">
                            {member.demos_completed}/{member.demos_target}
                          </span>
                        </div>
                        <div className="w-full bg-gray-200 rounded-full h-2">
                          <div
                            className="bg-green-600 h-2 rounded-full"
                            style={{
                              width: `${Math.min(
                                member.demos_percentage,
                                100
                              )}%`,
                            }}
                          ></div>
                        </div>
                      </div>

                      <div>
                        <div className="flex items-center justify-between mb-2">
                          <div className="flex items-center space-x-2">
                            <FileText className="w-4 h-4 text-purple-600" />
                            <span className="text-sm font-medium text-gray-700">
                              Proposals
                            </span>
                          </div>
                          <span className="text-sm text-gray-600">
                            {member.proposals_completed}/
                            {member.proposals_target}
                          </span>
                        </div>
                        <div className="w-full bg-gray-200 rounded-full h-2">
                          <div
                            className="bg-purple-600 h-2 rounded-full"
                            style={{
                              width: `${Math.min(
                                member.proposals_percentage,
                                100
                              )}%`,
                            }}
                          ></div>
                        </div>
                      </div>
                    </div>

                    {/* Action Buttons */}
                    <div className="mt-4 flex space-x-2">
                      <button
                        onClick={() => openCoachingModal(member)}
                        className="flex-1 bg-blue-50 text-blue-700 px-3 py-2 rounded-md text-sm font-medium hover:bg-blue-100 transition-colors"
                      >
                        View Coaching Tips
                      </button>
                      <button
                        onClick={() => openMessageModal(member)}
                        className="flex-1 bg-green-50 text-green-700 px-3 py-2 rounded-md text-sm font-medium hover:bg-green-100 transition-colors"
                      >
                        Send Message
                      </button>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Leaderboard Tab */}
        {activeTab === "leaderboard" && (
          <div className="space-y-6">
            <div className="bg-white rounded-lg shadow-sm border">
              <div className="p-6 border-b border-gray-200">
                <h2 className="text-xl font-semibold text-gray-900 flex items-center space-x-2">
                  <Trophy className="w-6 h-6 text-yellow-500" />
                  <span>Weekly Leaderboard</span>
                </h2>
              </div>
              <div className="overflow-x-auto">
                <table className="min-w-full divide-y divide-gray-200">
                  <thead className="bg-gray-50">
                    <tr>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        Rank
                      </th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        Sales Rep
                      </th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        Overall
                      </th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        Calls
                      </th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        Demos
                      </th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        Proposals
                      </th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        Score
                      </th>
                    </tr>
                  </thead>
                  <tbody className="bg-white divide-y divide-gray-200">
                    {leaderboard.map((entry, index) => (
                      <tr
                        key={entry.user_id}
                        className={index < 3 ? "bg-yellow-50" : ""}
                      >
                        <td className="px-6 py-4 whitespace-nowrap">
                          <div className="flex items-center">
                            {getRankIcon(index + 1)}
                          </div>
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap">
                          <div className="text-sm font-medium text-gray-900">
                            {entry.name}
                          </div>
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap">
                          <span
                            className={`inline-flex px-2 py-1 text-xs font-semibold rounded-full ${getPerformanceColor(
                              entry.overall_pct
                            )}`}
                          >
                            {entry.overall_pct}%
                          </span>
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                          {entry.calls_pct}%
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                          {entry.demos_pct}%
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                          {entry.proposals_pct}%
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap">
                          <div className="text-sm font-semibold text-gray-900">
                            {entry.total_score}
                          </div>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          </div>
        )}

        {/* AI Automation Tab */}
        {activeTab === "automation" && (
          <div className="space-y-6">
            <div className="bg-white rounded-lg shadow-sm border">
              <div className="p-6 border-b border-gray-200">
                <h2 className="text-xl font-semibold text-gray-900 flex items-center space-x-2">
                  <Zap className="w-6 h-6 text-blue-600" />
                  <span>Sales Agent Automation</span>
                </h2>
                <p className="mt-2 text-sm text-gray-600">
                  Monitor and control the autonomous sales management system
                </p>
              </div>

              <div className="p-6">
                {/* Manual Triggers */}
                <div className="mb-8">
                  <h3 className="text-lg font-medium text-gray-900 mb-4">
                    Manual Triggers
                  </h3>
                  <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
                    <button
                      onClick={() => triggerSchedulerJob("monday-prompts")}
                      className="bg-blue-600 text-white px-4 py-3 rounded-lg hover:bg-blue-700 transition-colors flex items-center space-x-2"
                    >
                      <Calendar className="w-5 h-5" />
                      <span>Monday Prompts</span>
                    </button>
                    <button
                      onClick={() => triggerSchedulerJob("wednesday-nudges")}
                      className="bg-green-600 text-white px-4 py-3 rounded-lg hover:bg-green-700 transition-colors flex items-center space-x-2"
                    >
                      <MessageCircle className="w-5 h-5" />
                      <span>Wednesday Nudges</span>
                    </button>
                    <button
                      onClick={() => triggerSchedulerJob("friday-summaries")}
                      className="bg-purple-600 text-white px-4 py-3 rounded-lg hover:bg-purple-700 transition-colors flex items-center space-x-2"
                    >
                      <BarChart3 className="w-5 h-5" />
                      <span>Friday Summaries</span>
                    </button>
                    <button
                      onClick={() => triggerSchedulerJob("milestone-check")}
                      className="bg-orange-600 text-white px-4 py-3 rounded-lg hover:bg-orange-700 transition-colors flex items-center space-x-2"
                    >
                      <Trophy className="w-5 h-5" />
                      <span>Milestone Check</span>
                    </button>
                  </div>
                </div>

                {/* Scheduled Jobs Status */}
                <div>
                  <h3 className="text-lg font-medium text-gray-900 mb-4">
                    Scheduled Jobs Status
                  </h3>
                  <div className="overflow-x-auto">
                    <table className="min-w-full divide-y divide-gray-200">
                      <thead className="bg-gray-50">
                        <tr>
                          <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                            Job Name
                          </th>
                          <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                            Next Run
                          </th>
                          <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                            Schedule
                          </th>
                          <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                            Status
                          </th>
                        </tr>
                      </thead>
                      <tbody className="bg-white divide-y divide-gray-200">
                        {schedulerStatus.map((job) => (
                          <tr key={job.id}>
                            <td className="px-6 py-4 whitespace-nowrap">
                              <div className="text-sm font-medium text-gray-900">
                                {job.name}
                              </div>
                            </td>
                            <td className="px-6 py-4 whitespace-nowrap">
                              <div className="text-sm text-gray-900">
                                {job.next_run}
                              </div>
                            </td>
                            <td className="px-6 py-4 whitespace-nowrap">
                              <div className="text-sm text-gray-600">
                                {job.trigger}
                              </div>
                            </td>
                            <td className="px-6 py-4 whitespace-nowrap">
                              <span className="inline-flex px-2 py-1 text-xs font-semibold rounded-full bg-green-100 text-green-800">
                                Active
                              </span>
                            </td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                </div>
              </div>
            </div>
          </div>
        )}

        {/* Analytics Tab */}
        {activeTab === "analytics" && (
          <div className="space-y-6">
            <div className="bg-white rounded-lg shadow-sm border p-6">
              <h2 className="text-xl font-semibold text-gray-900 mb-4 flex items-center space-x-2">
                <BarChart3 className="w-6 h-6 text-blue-600" />
                <span>Team Analytics</span>
              </h2>
              <div className="text-center py-12">
                <BarChart3 className="w-16 h-16 text-gray-400 mx-auto mb-4" />
                <p className="text-gray-600">
                  Advanced analytics coming soon...
                </p>
                <p className="text-sm text-gray-500 mt-2">
                  This will include historical trends, performance insights, and
                  predictive analytics.
                </p>
              </div>
            </div>
          </div>
        )}
      </div>

      {/* Coaching Modal */}
      {showCoachingModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
          <div className="bg-white p-6 rounded-lg shadow-xl max-w-2xl w-full max-h-[80vh] overflow-y-auto">
            <div className="flex justify-between items-center mb-4">
              <h2 className="text-xl font-semibold text-gray-900">
                🎯 Coaching Tips for {selectedUser?.user_name}
              </h2>
              <button
                onClick={() => setShowCoachingModal(false)}
                className="text-gray-400 hover:text-gray-600"
              >
                <X className="w-6 h-6" />
              </button>
            </div>

            {loadingTips ? (
              <div className="text-center py-12">
                <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto"></div>
                <p className="mt-4 text-gray-600">Loading coaching tips...</p>
              </div>
            ) : (
              <div className="space-y-4">
                {coachingTips.map((tip, index) => (
                  <div
                    key={index}
                    className="bg-blue-50 p-4 rounded-lg border-l-4 border-blue-500"
                  >
                    <p className="text-sm text-gray-800 leading-relaxed">
                      {tip}
                    </p>
                  </div>
                ))}
                {coachingTips.length === 0 && (
                  <div className="text-center py-8">
                    <p className="text-gray-500">
                      No coaching tips available at this time.
                    </p>
                  </div>
                )}
              </div>
            )}

            <div className="mt-6 flex justify-end">
              <button
                onClick={() => setShowCoachingModal(false)}
                className="bg-blue-600 text-white px-4 py-2 rounded-md text-sm font-medium hover:bg-blue-700 transition-colors"
              >
                Close
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Message Modal */}
      {showMessageModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
          <div className="bg-white p-6 rounded-lg shadow-xl max-w-lg w-full">
            <div className="flex justify-between items-center mb-4">
              <h2 className="text-xl font-semibold text-gray-900">
                💬 Send Message to {selectedUser?.user_name}
              </h2>
              <button
                onClick={() => setShowMessageModal(false)}
                className="text-gray-400 hover:text-gray-600"
              >
                <X className="w-6 h-6" />
              </button>
            </div>

            <div className="mb-4">
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Message
              </label>
              <textarea
                value={customMessage}
                onChange={(e) => setCustomMessage(e.target.value)}
                className="w-full h-32 p-3 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                placeholder="Type your message here..."
              />
            </div>

            <div className="flex space-x-3 justify-end">
              <button
                onClick={() => setShowMessageModal(false)}
                className="px-4 py-2 text-sm font-medium text-gray-700 bg-gray-100 rounded-md hover:bg-gray-200 transition-colors"
              >
                Cancel
              </button>
              <button
                onClick={sendCustomMessage}
                disabled={!customMessage.trim() || sendingMessage}
                className="px-4 py-2 text-sm font-medium text-white bg-green-600 rounded-md hover:bg-green-700 disabled:bg-gray-400 disabled:cursor-not-allowed transition-colors flex items-center space-x-2"
              >
                {sendingMessage ? (
                  <>
                    <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white"></div>
                    <span>Sending...</span>
                  </>
                ) : (
                  <>
                    <Send className="w-4 h-4" />
                    <span>Send Message</span>
                  </>
                )}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default SalesDashboard;
