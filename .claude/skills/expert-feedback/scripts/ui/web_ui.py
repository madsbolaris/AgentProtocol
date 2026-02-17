#!/usr/bin/env python3
"""
Local web UI for expert-feedback skill.

Provides:
- Real-time progress tracking
- Question answering interface
- Recommendation approval/rejection
- User can add context/thoughts during Q&A

Usage:
    python3 scripts/web_ui.py --workspace /path/to/workspace --port 8765

Opens browser to http://localhost:8765
"""
import asyncio
import json
from pathlib import Path
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, asdict
from datetime import datetime
import webbrowser
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import parse_qs, urlparse
import time
import sys

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))

try:
    from state.manager import StateManager, WorkspaceState as StateManagerWorkspaceState
except ImportError:
    # Fallback if import fails
    StateManager = None
    StateManagerWorkspaceState = None


@dataclass
class WorkspaceState:
    """Workspace state for UI."""
    topic: str
    mode: str
    experts: List[str]
    iteration: int
    convergence_percent: float
    consensus_reached: bool
    phase: str  # 'spawning_experts', 'synthesizing', 'questions', 'finalizing', 'reviewing'
    expert_progress: Dict[str, Dict[str, Any]]  # {expert: {status, duration, tokens, ...}}
    questions: List[Dict[str, Any]]
    recommendations: List[Dict[str, Any]]
    # ADD THESE:
    total_tokens: int = 0
    total_cost: float = 0.0
    start_time: Optional[str] = None
    complete_time: Optional[str] = None
    artifact_review: Optional[Dict[str, Any]] = None  # artifact-review-result.json data
    synthesized_concerns: Optional[Dict[str, Any]] = None  # synthesized-concerns.json
    concerns_feedback: Optional[Dict[str, Any]] = None  # concerns-feedback.json (user responses)
    # Token metrics
    total_input_tokens: int = 0
    total_output_tokens: int = 0


class WorkspaceWatcher:
    """Watch workspace for file changes and update UI.

    Uses centralized state management from state.json (single source of truth).
    """

    def __init__(self, workspace: Path):
        self.workspace = workspace
        self.state_file = workspace / "state.json"
        self.last_modified = {}

    def load_state(self) -> Optional[WorkspaceState]:
        """Load current workspace state using centralized state.json (Phase 4.4).

        Prioritizes 'phase' field from state.json as the single source of truth.
        Falls back to file-based phase detection only if 'phase' field is missing.
        """
        if not self.state_file.exists():
            return None

        try:
            data = json.loads(self.state_file.read_text())
        except Exception as e:
            print(f"⚠️ Error loading state: {e}")
            return None

        # Get phase from state.json (centralized source of truth)
        phase = data.get('phase', 'unknown')

        # Require phase field to be set in state.json
        if phase == 'unknown':
            raise ValueError("state.json must have 'phase' field set")

        # Load expert progress (required field)
        expert_progress = data['expert_progress']
        expert_results = data.get('expert_results', {})

        if not expert_progress:
            # Fallback: compute from expert_results (old behavior)
            expert_progress = {}
            for expert in data.get('experts', []):
                result = expert_results.get(expert, {})
                if result:
                    # Expert has results - include all data
                    expert_progress[expert] = result
                else:
                    # Expert not started yet
                    expert_progress[expert] = {'status': 'pending'}
        else:
            # Ensure all experts have an entry
            # Check both expert_progress and expert_results (experts may be in results but not progress)
            for expert in data.get('experts', []):
                if expert not in expert_progress:
                    # Check if expert has results (completed) but missing from progress
                    result = expert_results.get(expert, {})
                    if result:
                        # Expert completed - use result data
                        expert_progress[expert] = result
                    else:
                        # Expert not started yet
                        expert_progress[expert] = {'status': 'pending'}

        # Load questions
        questions = []
        iteration = data.get('iteration', 1)
        questions_file = self.workspace / f"iteration-{iteration}/questions.json"
        if questions_file.exists():
            try:
                questions = json.loads(questions_file.read_text())
            except Exception:
                pass

        # Load recommendations from consolidated feedback
        recommendations = []
        synthesized_file = self.workspace / f"iteration-{iteration}/synthesized.md"
        if synthesized_file.exists():
            # Try to extract recommendations from state
            iteration_state_file = self.workspace / f"iteration-{iteration}/state.json"
            if iteration_state_file.exists():
                try:
                    iter_data = json.loads(iteration_state_file.read_text())
                    recommendations = iter_data.get('recommendations', [])
                except Exception:
                    pass

        # Load artifact review result from iteration folder (if reviewing phase)
        artifact_review = None
        synthesized_concerns = None
        concerns_feedback = None

        # Artifact review is in current iteration
        review_iteration_dir = self.workspace / f"iteration-{iteration}"

        artifact_review_file = review_iteration_dir / "artifact-review-result.json"
        if artifact_review_file.exists():
            try:
                artifact_review = json.loads(artifact_review_file.read_text())
            except Exception:
                pass

        # Load synthesized concerns from iteration folder (if consolidation ran)
        synthesized_concerns_file = review_iteration_dir / "synthesized-concerns.json"
        if synthesized_concerns_file.exists():
            try:
                synthesized_concerns = json.loads(synthesized_concerns_file.read_text())
            except Exception:
                pass

        # Load concerns feedback from iteration folder (user responses to concerns)
        concerns_feedback_file = review_iteration_dir / "concerns-feedback.json"
        if concerns_feedback_file.exists():
            try:
                concerns_feedback = json.loads(concerns_feedback_file.read_text())
            except Exception:
                pass

        return WorkspaceState(
            topic=data.get('topic', ''),
            mode=data.get('mode', 'review'),
            experts=data.get('experts', []),
            iteration=iteration,
            convergence_percent=data.get('convergence_percent', 0),
            consensus_reached=data.get('consensus_reached', False),
            phase=phase,
            expert_progress=expert_progress,
            questions=questions,
            recommendations=recommendations,
            # ADD THESE:
            total_tokens=data.get('total_tokens', 0),
            total_cost=data.get('total_cost', 0.0),
            start_time=data.get('start_time'),
            complete_time=data.get('complete_time'),
            artifact_review=artifact_review,
            synthesized_concerns=synthesized_concerns,
            concerns_feedback=concerns_feedback,
            # Token metrics
            total_input_tokens=data.get('total_input_tokens', 0),
            total_output_tokens=data.get('total_output_tokens', 0)
        )


class WebUIHandler(BaseHTTPRequestHandler):
    """HTTP request handler for web UI."""

    workspace = None  # Set by server

    def log_message(self, format, *args):
        """Suppress default logging."""
        pass

    def do_GET(self):
        """Handle GET requests."""
        parsed = urlparse(self.path)
        path = parsed.path

        if path == '/':
            self.serve_index()
        elif path == '/api/state':
            self.serve_state()
        else:
            self.send_error(404)

    def do_POST(self):
        """Handle POST requests (answers, approvals, concern feedback)."""
        parsed = urlparse(self.path)
        path = parsed.path

        if path == '/api/answer':
            self.handle_answer()
        elif path == '/api/approve':
            self.handle_approve()
        elif path == '/api/reject':
            self.handle_reject()
        elif path == '/api/concern-feedback':
            self.handle_concern_feedback()
        elif path == '/api/restart-iteration':
            self.handle_restart_iteration()
        elif path == '/api/regenerate-artifact':
            self.handle_regenerate_artifact()
        elif path == '/api/approve-plan':
            self.handle_approve_plan()
        else:
            self.send_error(404)

    def serve_index(self):
        """Serve main UI HTML."""
        html = """<!DOCTYPE html>
<html>
<head>
    <title>Expert Feedback Session</title>
    <meta charset="UTF-8">
    <style>
        * { box-sizing: border-box; }
        body {
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
            background: #f5f5f5;
        }
        h1 { color: #333; margin-bottom: 10px; }
        .status {
            background: white;
            padding: 15px;
            border-radius: 8px;
            margin: 20px 0;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }
        .status-item {
            display: inline-block;
            margin-right: 20px;
            font-size: 14px;
        }
        .status-label { font-weight: 600; color: #666; }
        .progress { margin: 20px 0; }
        .expert {
            padding: 12px;
            margin: 8px 0;
            border-radius: 6px;
            display: flex;
            align-items: center;
            justify-content: space-between;
            font-size: 14px;
        }
        .expert.pending { background: #f0f0f0; color: #666; }
        .expert.running { background: #fff3cd; color: #856404; }
        .expert.complete { background: #d4edda; color: #155724; }
        .expert.error { background: #f8d7da; color: #721c24; }
        .expert-name { font-weight: 600; }
        .expert-status { font-size: 12px; text-transform: uppercase; }
        .expert-duration {
            margin-left: 8px;
            font-size: 11px;
            opacity: 0.8;
            font-weight: normal;
            text-transform: none;
        }
        .section {
            background: white;
            padding: 20px;
            border-radius: 8px;
            margin: 20px 0;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            display: none;
        }
        .section.visible { display: block; }
        .section h2 { margin-top: 0; color: #333; }
        .question {
            margin: 20px 0;
            padding: 20px;
            border: 2px solid #e0e0e0;
            border-radius: 8px;
            background: #fafafa;
        }
        .question h3 { margin-top: 0; color: #333; }
        .question-meta {
            font-size: 13px;
            color: #666;
            margin: 10px 0;
        }
        .question-meta span {
            display: inline-block;
            margin-right: 15px;
        }
        .references {
            background: #f8f9fa;
            border-left: 3px solid #007bff;
            padding: 10px 15px;
            margin: 10px 0;
            font-size: 13px;
        }
        .references ul {
            margin: 5px 0;
            padding-left: 20px;
        }
        .references li {
            margin: 5px 0;
        }
        .vscode-link {
            color: #007bff;
            text-decoration: none;
            font-size: 12px;
            margin-left: 10px;
        }
        .vscode-link:hover {
            text-decoration: underline;
        }
        .option-label {
            display: block;
            padding: 8px 12px;
            margin: 5px 0;
            background: white;
            border: 2px solid #ddd;
            border-radius: 6px;
            cursor: pointer;
            transition: all 0.2s;
        }
        .option-label:hover {
            background: #f8f9fa;
            border-color: #007bff;
        }
        .option-label input[type="radio"],
        .option-label input[type="checkbox"] {
            margin-right: 8px;
            cursor: pointer;
        }
        .option-label input[type="radio"]:checked ~ *,
        .option-label input[type="checkbox"]:checked ~ * {
            font-weight: 600;
        }
        .other-input {
            width: 100%;
            padding: 8px;
            margin-top: 5px;
            border: 1px solid #ddd;
            border-radius: 4px;
            font-family: inherit;
        }
        .additional-context {
            margin-top: 30px;
            padding: 20px;
            background: #f8f9fa;
            border-radius: 8px;
            border: 2px solid #dee2e6;
        }
        .additional-context h3 {
            margin-top: 0;
            color: #495057;
        }
        .recommendation {
            margin: 20px 0;
            padding: 20px;
            border-left: 4px solid #007bff;
            background: white;
            border-radius: 0 8px 8px 0;
            box-shadow: 0 2px 4px rgba(0,0,0,0.05);
        }
        .recommendation h3 { margin-top: 0; color: #333; }
        .recommendation-meta {
            font-size: 13px;
            color: #666;
            margin: 10px 0;
        }
        .recommendation-meta span {
            display: inline-block;
            margin-right: 15px;
            padding: 4px 8px;
            border-radius: 4px;
            background: #f0f0f0;
        }
        textarea {
            width: 100%;
            min-height: 100px;
            padding: 10px;
            border: 1px solid #ddd;
            border-radius: 6px;
            font-family: inherit;
            font-size: 14px;
            margin: 10px 0;
            resize: vertical;
        }
        textarea:focus {
            outline: none;
            border-color: #007bff;
            box-shadow: 0 0 0 3px rgba(0,123,255,0.1);
        }
        button {
            padding: 12px 24px;
            margin: 10px 5px 0 0;
            cursor: pointer;
            border: none;
            border-radius: 6px;
            font-size: 14px;
            font-weight: 600;
            transition: all 0.2s;
        }
        button:hover { transform: translateY(-1px); box-shadow: 0 2px 8px rgba(0,0,0,0.15); }
        button:active { transform: translateY(0); }
        .btn-primary {
            background: #007bff;
            color: white;
        }
        .btn-primary:hover { background: #0056b3; }
        .btn-secondary {
            background: #6c757d;
            color: white;
        }
        .btn-secondary:hover { background: #545b62; }
        .approve {
            background: #28a745;
            color: white;
        }
        .approve:hover { background: #218838; }
        .reject {
            background: #dc3545;
            color: white;
        }
        .reject:hover { background: #c82333; }
        .approved {
            opacity: 0.6;
            border-left-color: #28a745;
        }
        .rejected {
            opacity: 0.6;
            border-left-color: #dc3545;
        }
        .spinner {
            display: inline-block;
            width: 14px;
            height: 14px;
            border: 2px solid #f3f3f3;
            border-top: 2px solid #007bff;
            border-radius: 50%;
            animation: spin 1s linear infinite;
        }
        @keyframes spin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
        }
        .empty-state {
            text-align: center;
            padding: 40px;
            color: #999;
        }
    </style>
</head>
<body>
    <h1 id="topic">Expert Feedback Session</h1>
    <div class="status">
        <div class="status-item">
            <span class="status-label">Phase:</span>
            <span id="phase">Loading...</span>
        </div>
        <div class="status-item">
            <span class="status-label">Iteration:</span>
            <span id="iteration">-</span>
        </div>
        <div class="status-item">
            <span class="status-label">Convergence:</span>
            <span id="convergence">-</span>%
        </div>
        <div class="status-item">
            <span class="status-label">Duration:</span>
            <span id="duration">-</span>
        </div>
        <div class="status-item">
            <span class="status-label">Tokens:</span>
            <span id="total-tokens">-</span>
        </div>
        <div class="status-item">
            <span class="status-label">Cost:</span>
            <span id="total-cost">$-</span>
        </div>
    </div>

    <div class="progress" id="progress"></div>

    <div id="questions" class="section">
        <h2>❓ Questions from Experts</h2>
        <p>Please answer these questions to help refine the recommendations:</p>
        <div id="question-list"></div>

        <!-- Additional context section moved to end -->
        <div class="additional-context">
            <h3>💭 Additional Context (Optional)</h3>
            <p>Any additional thoughts, constraints, or context that applies to all questions:</p>
            <textarea id="additional-context"
                      placeholder="E.g., 'Tight 2-week deadline' or 'Team has limited TypeScript experience'..."
                      style="min-height: 150px; width: 100%;"></textarea>
        </div>

        <button class="btn-primary" onclick="submitAnswers()">Submit Answers & Continue Iteration</button>
        <button class="btn-secondary" onclick="skipIteration()">Skip Iteration & Proceed to Finalization</button>
    </div>

    <div id="recommendations" class="section">
        <h2>💡 Review Recommendations</h2>
        <p>Approve or reject each recommendation individually:</p>
        <div id="recommendation-list"></div>
    </div>

    <script>
        let currentState = null;
        let approvals = {};
        let questionsRendered = false;

        async function loadState() {
            try {
                const response = await fetch('/api/state');
                const state = await response.json();
                currentState = state;
                updateUI(state);
            } catch (error) {
                console.error('Failed to load state:', error);
            }
        }

        function updateUI(state) {
            if (!state || !state.topic) return;

            // Update header
            document.getElementById('topic').innerText = state.topic;
            document.getElementById('phase').innerText = state.phase.replace('_', ' ');
            document.getElementById('iteration').innerText = state.iteration;
            document.getElementById('convergence').innerText = state.convergence_percent.toFixed(1);

            // ADD THESE: Calculate and display duration
            if (state.start_time) {
                const start = new Date(state.start_time);
                const now = state.complete_time ? new Date(state.complete_time) : new Date();
                const durationMs = now - start;
                const minutes = Math.floor(durationMs / 60000);
                const seconds = Math.floor((durationMs % 60000) / 1000);
                document.getElementById('duration').innerText = `${minutes}m ${seconds}s`;
            }

            // Display total tokens and cost
            document.getElementById('total-tokens').innerText = state.total_tokens.toLocaleString();
            document.getElementById('total-cost').innerText = `$${state.total_cost.toFixed(4)}`;

            // Update expert progress or finalization status
            let progressHTML = '';
            if (state.phase === 'finalizing') {
                progressHTML = `<div class="status-message">
                    <h3>🎯 Generating Implementation Plan</h3>
                    <p>Synthesizing expert feedback and your Q&A responses into actionable plan...</p>
                    <p style="color: #666; font-size: 0.9em;">This may take 2-3 minutes.</p>
                </div>`;
            } else if (state.phase === 'reviewing') {
                // Show synthesized concerns if available
                if (state.synthesized_concerns && state.synthesized_concerns.concerns) {
                    const concerns = state.synthesized_concerns.concerns;
                    const summary = state.synthesized_concerns.summary || {};
                    const feedback = state.concerns_feedback || {};

                    // Count priority levels
                    const highPriority = concerns.filter(c => c.priority === 'high').length;
                    const mediumPriority = concerns.filter(c => c.priority === 'medium').length;
                    const lowPriority = concerns.filter(c => c.priority === 'low').length;

                    progressHTML = `
                        <div class="status-message">
                            <h3>🔍 Expert Feedback Consolidated</h3>
                            <p>Experts have reviewed the draft artifact. Please review their synthesized concerns below.</p>
                            <div style="margin-top: 15px; font-size: 0.9em;">
                                <div><strong>Total Experts:</strong> ${summary.total_experts || 0}</div>
                                <div><strong>Total Concerns:</strong> ${concerns.length}</div>
                                <div style="margin-left: 20px;">
                                    <span style="color: #dc3545;">⬆ High: ${highPriority}</span> |
                                    <span style="color: #ffc107;">➡ Medium: ${mediumPriority}</span> |
                                    <span style="color: #28a745;">⬇ Low: ${lowPriority}</span>
                                </div>
                            </div>
                        </div>

                        <div style="margin-top: 20px;">
                            <h3>Review Consolidated Concerns</h3>
                            <p style="color: #666; font-size: 0.9em;">For each concern, indicate whether you agree and optionally add a comment.</p>

                            ${concerns.map((concern, i) => {
                                const concernFeedback = feedback[i] || {};
                                const response = concernFeedback.response || '';
                                const comment = concernFeedback.comment || '';

                                // Priority styling
                                let priorityColor = '#28a745';
                                if (concern.priority === 'high') priorityColor = '#dc3545';
                                else if (concern.priority === 'medium') priorityColor = '#ffc107';

                                return `
                                <div class="concern-card" style="margin: 20px 0; padding: 15px; background: white; border-left: 4px solid ${priorityColor}; border-radius: 4px; box-shadow: 0 2px 4px rgba(0,0,0,0.1);">
                                    <div style="display: flex; justify-content: space-between; align-items: start; margin-bottom: 10px;">
                                        <h4 style="margin: 0; flex: 1;">${concern.title}</h4>
                                        <span style="background: ${priorityColor}; color: white; padding: 2px 8px; border-radius: 3px; font-size: 0.8em; text-transform: uppercase;">
                                            ${concern.priority}
                                        </span>
                                    </div>

                                    <div style="margin: 10px 0; font-size: 0.9em; color: #666;">
                                        <strong>Category:</strong> ${concern.category} |
                                        <strong>Raised by:</strong> ${concern.raised_by.join(', ')}
                                    </div>

                                    <div style="margin: 10px 0;">
                                        <strong>Description:</strong>
                                        <p style="margin: 5px 0;">${concern.description}</p>
                                    </div>

                                    <div style="margin: 10px 0; padding: 10px; background: #f8f9fa; border-radius: 3px;">
                                        <strong>Recommendation:</strong>
                                        <p style="margin: 5px 0;">${concern.recommendation}</p>
                                    </div>

                                    ${concern.impact_if_ignored ? `
                                    <div style="margin: 10px 0; padding: 10px; background: #fff3cd; border-radius: 3px;">
                                        <strong>⚠️ Impact if Ignored:</strong>
                                        <p style="margin: 5px 0;">${concern.impact_if_ignored}</p>
                                    </div>
                                    ` : ''}

                                    <!-- Feedback UI -->
                                    <div style="margin-top: 15px; padding-top: 15px; border-top: 1px solid #dee2e6;">
                                        <div style="margin-bottom: 10px;">
                                            <strong>Your Response:</strong>
                                        </div>
                                        <div style="display: flex; gap: 10px; margin-bottom: 10px;">
                                            <button class="concern-btn ${response === 'agree' ? 'active' : ''}"
                                                    onclick="setConcernResponse(${i}, 'agree')"
                                                    style="flex: 1; padding: 8px; border: 2px solid #28a745; background: ${response === 'agree' ? '#28a745' : 'white'}; color: ${response === 'agree' ? 'white' : '#28a745'}; border-radius: 4px; cursor: pointer; font-weight: 600;">
                                                ✓ Agree
                                            </button>
                                            <button class="concern-btn ${response === 'disagree' ? 'active' : ''}"
                                                    onclick="setConcernResponse(${i}, 'disagree')"
                                                    style="flex: 1; padding: 8px; border: 2px solid #dc3545; background: ${response === 'disagree' ? '#dc3545' : 'white'}; color: ${response === 'disagree' ? 'white' : '#dc3545'}; border-radius: 4px; cursor: pointer; font-weight: 600;">
                                                ✗ Disagree
                                            </button>
                                        </div>
                                        <textarea
                                            id="concern-comment-${i}"
                                            placeholder="Optional: Add your comment or clarification..."
                                            style="width: 100%; padding: 8px; border: 1px solid #ced4da; border-radius: 4px; font-family: inherit; resize: vertical;"
                                            rows="2"
                                            onchange="setConcernComment(${i}, this.value)"
                                        >${comment}</textarea>
                                    </div>
                                </div>
                                `;
                            }).join('')}
                        </div>

                        <!-- Action Buttons -->
                        <div style="margin-top: 30px; padding: 20px; background: #f8f9fa; border-radius: 4px; text-align: center;">
                            <h4>Next Steps</h4>
                            <p style="color: #666; margin-bottom: 20px;">Based on the concerns, what would you like to do?</p>
                            <div style="display: flex; gap: 15px; justify-content: center; flex-wrap: wrap;">
                                <button onclick="restartIteration()"
                                        style="padding: 12px 24px; background: #17a2b8; color: white; border: none; border-radius: 4px; cursor: pointer; font-weight: 600;">
                                    🔄 Restart Expert Iteration
                                </button>
                                <button onclick="regenerateArtifact()"
                                        style="padding: 12px 24px; background: #ffc107; color: #333; border: none; border-radius: 4px; cursor: pointer; font-weight: 600;">
                                    🔧 Regenerate Artifact
                                </button>
                                <button onclick="approvePlan()"
                                        style="padding: 12px 24px; background: #28a745; color: white; border: none; border-radius: 4px; cursor: pointer; font-weight: 600;">
                                    ✓ Approve Plan
                                </button>
                            </div>
                        </div>
                    `;
                } else if (state.artifact_review) {
                    // Fallback to old display if consolidation hasn't run yet
                    progressHTML = `<div class="status-message">
                        <h3>⏳ Consolidating Expert Feedback</h3>
                        <p>Processing expert reviews...</p>
                    </div>`;
                } else {
                    // No artifact review data yet
                    progressHTML = `<div class="status-message">
                        <h3>📄 Experts Reviewing Draft Artifact</h3>
                        <p>Experts are reviewing the draft for critical issues...</p>
                    </div>`;
                }
            } else {
                progressHTML = state.experts.map(expert => {
                    const result = state.expert_progress[expert] || {status: 'pending'};
                    const status = result.status || 'pending';

                    // Format metadata (duration, tokens, cost, cache) if available
                    let metadataText = '';
                    const duration = result.duration_seconds || result.duration || 0;
                    const tokens = result.total_tokens || 0;
                    const cost = result.cost || 0;

                    if (status === 'complete' && (duration > 0 || tokens > 0)) {
                        const parts = [];

                        if (duration > 0) {
                            const minutes = Math.floor(duration / 60);
                            const seconds = duration % 60;
                            if (minutes > 0) {
                                parts.push(`${minutes}m ${seconds}s`);
                            } else {
                                parts.push(`${seconds}s`);
                            }
                        }

                        if (tokens > 0) {
                            parts.push(`${tokens.toLocaleString()} tokens`);
                        }

                        if (cost > 0) {
                            parts.push(`$${cost.toFixed(4)}`);
                        }

                        if (parts.length > 0) {
                            metadataText = `<span class="expert-duration">(${parts.join(', ')})</span>`;
                        }
                    }

                    return `<div class="expert ${status}">
                        <span class="expert-name">${expert}</span>
                        <span class="expert-status">${status} ${metadataText}</span>
                    </div>`;
                }).join('');
            }
            document.getElementById('progress').innerHTML = progressHTML || '<div class="empty-state">No experts yet</div>';

            // Show questions if available (only render once to preserve focus)
            const questionsSection = document.getElementById('questions');
            const questionList = state.questions?.questions || [];
            if (state.phase === 'questions' && questionList.length > 0) {
                if (!questionsRendered) {
                    questionsSection.classList.add('visible');
                    const questionsHTML = questionList.map((q, i) => {
                        // Render input based on question type
                        let inputHTML = '';
                        const questionType = q.question_type || 'textarea';

                        if (questionType === 'radio' && q.options) {
                            inputHTML = q.options.map((opt, j) => `
                                <label class="option-label">
                                    <input type="radio" name="answer-${i}" value="${opt}">
                                    <span>${opt}</span>
                                </label>
                            `).join('');

                            // Always include "Other" option
                            if (q.allow_other !== false) {
                                inputHTML += `
                                    <label class="option-label">
                                        <input type="radio" name="answer-${i}" value="__other__">
                                        <span>Other:</span>
                                    </label>
                                    <input type="text" id="answer-${i}-other" class="other-input"
                                           placeholder="Please specify...">
                                `;
                            }
                        } else if (questionType === 'checkbox' && q.options) {
                            inputHTML = q.options.map((opt, j) => `
                                <label class="option-label">
                                    <input type="checkbox" class="answer-${i}" value="${opt}">
                                    <span>${opt}</span>
                                </label>
                            `).join('');

                            if (q.allow_other !== false) {
                                inputHTML += `
                                    <label class="option-label">
                                        <input type="checkbox" class="answer-${i}" value="__other__">
                                        <span>Other:</span>
                                    </label>
                                    <input type="text" id="answer-${i}-other" class="other-input"
                                           placeholder="Please specify...">
                                `;
                            }
                        } else {
                            // Default: textarea
                            inputHTML = `<textarea id="answer-${i}" placeholder="Your answer..."></textarea>`;
                        }

                        // Render references if available
                        let referencesHTML = '';
                        if (q.references && q.references.length > 0) {
                            const workspacePath = '${self.server.workspace if hasattr(self, "server") else ""}';
                            referencesHTML = `
                                <div class="references">
                                    <strong>📚 Referenced by:</strong>
                                    <ul>
                                        ${q.references.map(ref => `
                                            <li>
                                                <strong>${ref.expert}</strong>: "${ref.excerpt}"
                                                <a href="vscode://file${workspacePath}/iteration-1/experts/${ref.file}"
                                                   class="vscode-link">
                                                    📂 Open in VS Code
                                                </a>
                                            </li>
                                        `).join('')}
                                    </ul>
                                </div>
                            `;
                        }

                        return `
                            <div class="question">
                                <h3>${q.question}</h3>
                                <div class="question-meta">
                                    <span><strong>Context:</strong> ${q.context || 'N/A'}</span>
                                    <span><strong>Importance:</strong> ${q.importance || 'medium'}</span>
                                </div>
                                ${referencesHTML}
                                ${inputHTML}
                            </div>
                        `;
                    }).join('');
                    document.getElementById('question-list').innerHTML = questionsHTML;
                    questionsRendered = true;
                }
            } else {
                questionsSection.classList.remove('visible');
                questionsRendered = false;
            }

            // Show recommendations if available
            const recsSection = document.getElementById('recommendations');
            if (state.phase === 'reviewing' && state.recommendations && state.recommendations.length > 0) {
                recsSection.classList.add('visible');
                const recsHTML = state.recommendations.map((rec, i) => {
                    const approval = approvals[i];
                    const statusClass = approval ? (approval === 'approved' ? 'approved' : 'rejected') : '';
                    const buttons = approval
                        ? `<span style="color: ${approval === 'approved' ? '#28a745' : '#dc3545'}; font-weight: 600;">
                             ${approval === 'approved' ? '✓ Approved' : '✗ Rejected'}
                           </span>`
                        : `<button class="approve" onclick="approveRec(${i})">✓ Approve</button>
                           <button class="reject" onclick="rejectRec(${i})">✗ Reject</button>`;

                    return `<div class="recommendation ${statusClass}">
                        <h3>${rec.title}</h3>
                        <div class="recommendation-meta">
                            <span><strong>Priority:</strong> ${rec.priority || 'N/A'}</span>
                            <span><strong>Complexity:</strong> ${rec.complexity || 'N/A'}</span>
                            <span><strong>DX Impact:</strong> ${rec.dx_impact || 'N/A'}</span>
                        </div>
                        <p>${rec.description || ''}</p>
                        ${buttons}
                    </div>`;
                }).join('');
                document.getElementById('recommendation-list').innerHTML = recsHTML;
            } else {
                recsSection.classList.remove('visible');
            }
        }

        async function submitAnswers() {
            const questionList = currentState?.questions?.questions || [];
            const answers = [];

            questionList.forEach((q, i) => {
                const questionType = q.question_type || 'textarea';
                let answer = '';

                if (questionType === 'radio') {
                    // Get selected radio button
                    const radioInputs = document.querySelectorAll(`input[name="answer-${i}"]`);
                    for (const input of radioInputs) {
                        if (input.checked) {
                            if (input.value === '__other__') {
                                // Use "other" text field
                                const otherInput = document.getElementById(`answer-${i}-other`);
                                answer = otherInput?.value || '';
                            } else {
                                answer = input.value;
                            }
                            break;
                        }
                    }
                } else if (questionType === 'checkbox') {
                    // Get all checked checkboxes
                    const checkboxes = document.querySelectorAll(`.answer-${i}:checked`);
                    const selected = [];
                    for (const checkbox of checkboxes) {
                        if (checkbox.value === '__other__') {
                            const otherInput = document.getElementById(`answer-${i}-other`);
                            if (otherInput?.value) {
                                selected.push(otherInput.value);
                            }
                        } else {
                            selected.push(checkbox.value);
                        }
                    }
                    answer = selected.join(', ');
                } else {
                    // Textarea
                    const answerEl = document.getElementById(`answer-${i}`);
                    answer = answerEl?.value || '';
                }

                answers.push({
                    question_id: q.id,
                    question: q.question,
                    answer: answer
                });
            });

            // Get additional context
            const additionalContext = document.getElementById('additional-context')?.value || '';

            console.log('Submitting answers:', answers);
            console.log('Additional context:', additionalContext);

            try {
                const response = await fetch('/api/answer', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({
                        answers: answers,
                        additional_context: additionalContext,
                        skip_iteration: false
                    })
                });

                if (response.ok) {
                    alert('✅ Answers submitted! Experts will refine their recommendations.');
                    document.getElementById('questions').classList.remove('visible');
                    questionsRendered = false;
                } else {
                    alert('❌ Failed to submit answers. Please try again.');
                }
            } catch (error) {
                console.error('Error submitting answers:', error);
                alert('❌ Failed to submit answers. Please try again.');
            }
        }

        async function skipIteration() {
            if (!confirm('Skip iteration and proceed to finalization? This will generate the final artifact with current feedback.')) {
                return;
            }

            try {
                const response = await fetch('/api/answer', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({answers: [], skip_iteration: true})
                });

                if (response.ok) {
                    alert('✅ Skipping iteration. Proceeding to finalization...');
                    document.getElementById('questions').classList.remove('visible');
                } else {
                    alert('❌ Failed to skip iteration. Please try again.');
                }
            } catch (error) {
                console.error('Error skipping iteration:', error);
                alert('❌ Failed to skip iteration. Please try again.');
            }
        }

        async function approveRec(index) {
            try {
                const response = await fetch('/api/approve', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({index})
                });

                if (response.ok) {
                    approvals[index] = 'approved';
                    updateUI(currentState);
                }
            } catch (error) {
                console.error('Error approving recommendation:', error);
            }
        }

        async function rejectRec(index) {
            const reason = prompt('Why are you rejecting this recommendation?');
            if (!reason) return;

            try {
                const response = await fetch('/api/reject', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({index, reason})
                });

                if (response.ok) {
                    approvals[index] = 'rejected';
                    updateUI(currentState);
                }
            } catch (error) {
                console.error('Error rejecting recommendation:', error);
            }
        }

        // Concern feedback functions
        const concernFeedback = {};

        async function setConcernResponse(index, response) {
            concernFeedback[index] = concernFeedback[index] || {};
            concernFeedback[index].response = response;
            await saveConcernFeedback();
            loadState(); // Refresh UI
        }

        async function setConcernComment(index, comment) {
            concernFeedback[index] = concernFeedback[index] || {};
            concernFeedback[index].comment = comment;
            await saveConcernFeedback();
        }

        async function saveConcernFeedback() {
            try {
                const response = await fetch('/api/concern-feedback', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({feedback: concernFeedback})
                });
                if (!response.ok) {
                    console.error('Failed to save concern feedback');
                }
            } catch (error) {
                console.error('Error saving concern feedback:', error);
            }
        }

        async function restartIteration() {
            if (!confirm('This will restart the expert iteration process with a new round of reviews. Continue?')) {
                return;
            }

            try {
                const response = await fetch('/api/restart-iteration', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'}
                });

                if (response.ok) {
                    alert('Expert iteration restarted. Experts will begin a new round of reviews.');
                    loadState();
                } else {
                    alert('Failed to restart iteration. Check console for errors.');
                }
            } catch (error) {
                console.error('Error restarting iteration:', error);
                alert('Error restarting iteration. Check console for details.');
            }
        }

        async function regenerateArtifact() {
            if (!confirm('This will regenerate the artifact based on your concern feedback. Continue?')) {
                return;
            }

            try {
                const response = await fetch('/api/regenerate-artifact', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({feedback: concernFeedback})
                });

                if (response.ok) {
                    alert('Artifact regeneration started. Experts will review the new version.');
                    loadState();
                } else {
                    alert('Failed to regenerate artifact. Check console for errors.');
                }
            } catch (error) {
                console.error('Error regenerating artifact:', error);
                alert('Error regenerating artifact. Check console for details.');
            }
        }

        async function approvePlan() {
            if (!confirm('This will mark the plan as approved and complete the review process. Continue?')) {
                return;
            }

            try {
                const response = await fetch('/api/approve-plan', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({feedback: concernFeedback})
                });

                if (response.ok) {
                    alert('Plan approved! The workflow is complete.');
                    loadState();
                } else {
                    alert('Failed to approve plan. Check console for errors.');
                }
            } catch (error) {
                console.error('Error approving plan:', error);
                alert('Error approving plan. Check console for details.');
            }
        }

        // Auto-refresh every 2 seconds
        setInterval(loadState, 2000);
        loadState();
    </script>
</body>
</html>"""

        self.send_response(200)
        self.send_header('Content-type', 'text/html; charset=utf-8')
        self.send_header('Cache-Control', 'no-store')
        self.end_headers()
        self.wfile.write(html.encode('utf-8'))

    def serve_state(self):
        """Serve current workspace state as JSON."""
        workspace = Path(self.server.workspace)
        watcher = WorkspaceWatcher(workspace)
        state = watcher.load_state()

        if state:
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.send_header('Cache-Control', 'no-store')
            self.end_headers()
            self.wfile.write(json.dumps(asdict(state)).encode('utf-8'))
        else:
            # Return proper error response
            self.send_response(503)
            self.send_header('Content-type', 'application/json')
            self.send_header('Cache-Control', 'no-store')
            self.end_headers()
            error_response = {
                'error': 'State not available',
                'message': 'Workspace state has not been initialized yet. Please wait for the session to start.'
            }
            self.wfile.write(json.dumps(error_response).encode('utf-8'))

    def handle_answer(self):
        """Handle question answers."""
        try:
            content_length = int(self.headers.get('Content-Length', 0))
            post_data = self.rfile.read(content_length)
            data = json.loads(post_data.decode('utf-8'))

            # Save answers to iteration-N/qa-answers.json
            workspace = Path(self.server.workspace)

            # Load existing state to get iteration
            state_file = workspace / "state.json"
            iteration = 1
            if state_file.exists():
                try:
                    state_data = json.loads(state_file.read_text())
                    iteration = state_data.get('iteration', 1)
                except Exception:
                    pass

            # Save to iteration folder
            iteration_dir = workspace / f"iteration-{iteration}"
            iteration_dir.mkdir(parents=True, exist_ok=True)
            answers_file = iteration_dir / "qa-answers.json"

            answers_file.write_text(json.dumps({
                'iteration': iteration,
                'answers': data.get('answers', []),
                'additional_context': data.get('additional_context', ''),
                'skip_iteration': data.get('skip_iteration', False),
                'timestamp': datetime.now().astimezone().isoformat()
            }, indent=2))

            print(f"✅ Received {len(data.get('answers', []))} answers")

            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(b'{"status": "ok"}')
        except Exception as e:
            print(f"⚠️ Error handling answer: {e}")
            self.send_error(500, str(e))

    def handle_approve(self):
        """Handle recommendation approval."""
        try:
            content_length = int(self.headers.get('Content-Length', 0))
            post_data = self.rfile.read(content_length)
            data = json.loads(post_data.decode('utf-8'))

            # Save approval to approvals.json
            workspace = Path(self.server.workspace)
            approvals_file = workspace / "approvals.json"

            approvals = []
            if approvals_file.exists():
                try:
                    approvals = json.loads(approvals_file.read_text())
                except Exception:
                    pass

            approvals.append({
                'index': data.get('index'),
                'status': 'approved',
                'timestamp': datetime.now().astimezone().isoformat()
            })

            approvals_file.write_text(json.dumps(approvals, indent=2))

            print(f"✅ Recommendation {data.get('index')} approved")

            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(b'{"status": "ok"}')
        except Exception as e:
            print(f"⚠️ Error handling approval: {e}")
            self.send_error(500, str(e))

    def handle_reject(self):
        """Handle recommendation rejection."""
        try:
            content_length = int(self.headers.get('Content-Length', 0))
            post_data = self.rfile.read(content_length)
            data = json.loads(post_data.decode('utf-8'))

            # Save rejection to approvals.json
            workspace = Path(self.server.workspace)
            approvals_file = workspace / "approvals.json"

            approvals = []
            if approvals_file.exists():
                try:
                    approvals = json.loads(approvals_file.read_text())
                except Exception:
                    pass

            approvals.append({
                'index': data.get('index'),
                'status': 'rejected',
                'reason': data.get('reason', ''),
                'timestamp': datetime.now().astimezone().isoformat()
            })

            approvals_file.write_text(json.dumps(approvals, indent=2))

            print(f"❌ Recommendation {data.get('index')} rejected: {data.get('reason', 'No reason')}")

            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(b'{"status": "ok"}')
        except Exception as e:
            print(f"⚠️ Error handling rejection: {e}")
            self.send_error(500, str(e))

    def handle_concern_feedback(self):
        """Handle concern feedback (agree/disagree/comment)."""
        try:
            content_length = int(self.headers.get('Content-Length', 0))
            post_data = self.rfile.read(content_length)
            data = json.loads(post_data.decode('utf-8'))

            # Get current iteration from state
            workspace = Path(self.server.workspace)
            from state.manager import StateManager
            state_mgr = StateManager(workspace)
            state = state_mgr.load()
            review_iteration = state.iteration

            # Save feedback to iteration folder
            iteration_dir = workspace / f"iteration-{review_iteration}"
            iteration_dir.mkdir(parents=True, exist_ok=True)
            feedback_file = iteration_dir / "concerns-feedback.json"

            feedback_file.write_text(json.dumps({
                'feedback': data.get('feedback', {}),
                'timestamp': datetime.now().astimezone().isoformat()
            }, indent=2))

            print(f"💬 Concern feedback saved ({len(data.get('feedback', {}))} concerns)")

            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(b'{"status": "ok"}')
        except Exception as e:
            print(f"⚠️ Error saving concern feedback: {e}")
            self.send_error(500, str(e))

    def handle_restart_iteration(self):
        """Handle request to restart expert iteration."""
        try:
            workspace = Path(self.server.workspace)

            # Update phase to trigger expert spawning again
            state_manager = StateManager(workspace)
            state = state_manager.load()

            # Increment iteration
            new_iteration = state.iteration + 1
            state_manager.set_iteration(new_iteration)
            state_manager.set_phase("spawning")

            print(f"🔄 Restarting expert iteration (iteration {new_iteration})")

            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({
                'status': 'ok',
                'iteration': new_iteration
            }).encode())
        except Exception as e:
            print(f"⚠️ Error restarting iteration: {e}")
            self.send_error(500, str(e))

    def handle_regenerate_artifact(self):
        """Handle request to regenerate artifact."""
        try:
            workspace = Path(self.server.workspace)

            # Update phase to trigger finalization again
            state_manager = StateManager(workspace)
            state_manager.set_phase("finalizing")

            print(f"🔧 Regenerating artifact")

            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(b'{"status": "ok"}')
        except Exception as e:
            print(f"⚠️ Error regenerating artifact: {e}")
            self.send_error(500, str(e))

    def handle_approve_plan(self):
        """Handle plan approval."""
        try:
            workspace = Path(self.server.workspace)

            # Mark as complete
            state_manager = StateManager(workspace)
            state_manager.set_phase("complete")

            # Save approval timestamp
            approval_file = workspace / "plan-approved.json"
            approval_file.write_text(json.dumps({
                'approved': True,
                'timestamp': datetime.now().astimezone().isoformat()
            }, indent=2))

            print(f"✅ Plan approved!")

            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(b'{"status": "ok"}')
        except Exception as e:
            print(f"⚠️ Error approving plan: {e}")
            self.send_error(500, str(e))


def start_server(workspace: Path, port: int = 8765, open_browser: bool = True):
    """Start local web UI server."""
    # Create server
    handler = WebUIHandler
    server = HTTPServer(("", port), handler)
    server.workspace = str(workspace)

    url = f"http://localhost:{port}"
    print(f"\n🌐 Expert Feedback UI: {url}")
    print(f"📁 Workspace: {workspace}")

    # Open browser in separate thread
    if open_browser:
        def open_browser_delayed():
            time.sleep(1)
            webbrowser.open(url)

        browser_thread = threading.Thread(target=open_browser_delayed, daemon=True)
        browser_thread.start()

    print("\n✅ Server running. Press Ctrl+C to stop.\n")

    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n🛑 Server stopped")
    finally:
        server.shutdown()


def main():
    import argparse
    parser = argparse.ArgumentParser(description="Local web UI for expert-feedback")
    parser.add_argument("--workspace", type=Path, required=True, help="Workspace path")
    parser.add_argument("--port", type=int, default=8765, help="Server port")
    parser.add_argument("--no-browser", action="store_true", help="Don't open browser")

    args = parser.parse_args()

    if not args.workspace.exists():
        print(f"❌ Workspace does not exist: {args.workspace}")
        return 1

    start_server(args.workspace, args.port, not args.no_browser)
    return 0


if __name__ == "__main__":
    exit(main())
