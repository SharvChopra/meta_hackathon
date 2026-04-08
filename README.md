# 🤖 GitGuard AI — Open-Source Repository Maintainer Agent

> **Scalar Meta OpenEnv Hackathon Submission**
> An AI agent that navigates a mock GitHub web UI to triage issues, detect duplicates, and catch logic bugs in pull requests — trained end-to-end with GRPO reinforcement learning.

---

## 📌 Table of Contents

- [Overview](#overview)
- [Demo](#demo)
- [Architecture](#architecture)
- [The Three Challenges](#the-three-challenges)
- [Reward Function](#reward-function)
- [How GRPO Training Works](#how-grpo-training-works)
- [Project Structure](#project-structure)
- [Setup & Installation](#setup--installation)
- [Running the Agent](#running-the-agent)
- [Deployment on Hugging Face Spaces](#deployment-on-hugging-face-spaces)
- [Tech Stack](#tech-stack)
- [Team](#team)

---

## 🧠 Overview

**GitGuard AI** is a web-browsing AI agent trained to act like a senior software engineer managing a busy open-source repository. Instead of operating via direct API calls, the agent **visually navigates a custom-built mock GitHub interface**, reads issue descriptions and code diffs, and performs actions by clicking real UI buttons — exactly the way a human maintainer would.

This environment tests three core competencies of an intelligent software agent:

| Competency | Task | Difficulty |
|---|---|---|
| Text Classification | Applying correct issue labels | 🟢 Easy |
| Semantic Reasoning | Detecting duplicate issues | 🟡 Medium |
| Code Understanding | Spotting logic bugs in PRs | 🔴 Hard |

The agent is trained using **GRPO (Group Relative Policy Optimization)** — a reinforcement learning algorithm that refines the LLM's behavior purely from numeric reward signals, with no human feedback labels required.

---

## 🎥 Demo

> 🔗 **Live Environment:** [Hugging Face Space — GitGuard AI](#) *(link after deployment)*
> 🔗 **Demo Video:** [Watch on YouTube](#) *(link after recording)*

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                        TRAINING PHASE                       │
│                                                             │
│   LLM Policy ──► BrowserGym Agent ──► Mock GitHub UI       │
│       ▲                                      │              │
│       │           GRPO Update                │              │
│       └──────── Reward Signal ◄── Grader ◄──┘              │
└─────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│                        TESTING PHASE                        │
│                                                             │
│  Issue/PR Inbox ──► Issues List Page ──► Issue Detail Page  │
│                                               │             │
│                              ┌────────────────┘             │
│                              ▼                              │
│                   Dropdown: Bug / Enhancement /             │
│                   Documentation / Duplicate                 │
│                              │                              │
│                   Backend DB ◄── Grader validates action    │
└─────────────────────────────────────────────────────────────┘
```

**Three core components work together:**

1. **The Environment** — A lightweight mock GitHub site (FastAPI + SQLite + React) with real clickable UI: Issues tab, Pull Requests tab, label dropdowns, merge buttons, and comment boxes.

2. **The Agent** — A BrowserGym-powered LLM that receives visual observations of the webpage and outputs browser actions (`click`, `type`, `select`).

3. **The Grader** — A Python evaluation script that queries the backend database after each episode and computes a structured reward score.

---

## 🎯 The Three Challenges

### 🟢 Easy — Automated Issue Triage

**Scenario:** Five new issues arrive in the inbox. Each describes a different kind of problem.

**What the agent does:**
1. Navigates to the Issues list page
2. Opens each issue and reads the description
3. Clicks the Labels dropdown
4. Selects the correct label (`bug`, `enhancement`, or `documentation`)
5. Saves the label

**Example:**
- *"The app crashes when I click the login button"* → `bug`
- *"Add dark mode support"* → `enhancement`
- *"The README doesn't mention environment setup"* → `documentation`

**Grader check:** Label field in DB matches expected label for that issue ID.

---

### 🟡 Medium — Duplicate Issue Detection

**Scenario:** A new issue is submitted. It describes the exact same problem as an older, already-open issue.

**What the agent does:**
1. Reads the new issue carefully
2. Recognizes it matches an existing open issue (e.g., Issue #12)
3. Types the duplicate issue ID in the "Linked Issue" field
4. Clicks "Close as Duplicate"

**Example:**
- New issue: *"Submit button is completely blue instead of red"*
- Matches Issue #12: *"Primary button color rendering incorrectly"*

**Grader check:** Issue status is `closed`, `duplicate_of` field is set to the correct issue ID.

---

### 🔴 Hard — Code Review Trap

**Scenario:** A Pull Request is submitted with a deliberate, injected logic error (e.g., an off-by-one error in array traversal, or an unhandled null exception).

**What the agent does:**
1. Navigates to the Pull Requests tab
2. Opens the PR and reads the code diff
3. **Identifies the specific injected bug**
4. Clicks "Review Changes" → selects "Request Changes"
5. Types a comment describing exactly what the bug is
6. Submits the review — **without** clicking "Merge"

**Example injected bug:**
```cpp
// Off-by-one: should be i < n-1, not i < n
for (int i = 0; i < n; i++) {
    if (intervals[i][1] >= intervals[i+1][0]) { // Index out of bounds!
        merge(intervals[i], intervals[i+1]);
    }
}
```

**Grader check:**
- ✅ PR status = `changes_requested` → Score: **1.0**
- ❌ PR status = `merged` → Score: **0.0** + massive penalty

---

## 🏆 Reward Function

The reward system provides **partial credit** for intermediate correct steps, not just final outcomes:

```
Action                                          Reward
──────────────────────────────────────────────────────
Navigate to correct issue/PR page             + 0.20
Interact with correct UI elements             + 0.30
Finalize the correct action                   + 0.50
──────────────────────────────────────────────────────
SUBTOTAL (per task, max)                        1.00
──────────────────────────────────────────────────────
Merge a PR containing injected bug            - 1.00
Close a non-duplicate issue as duplicate      - 1.00
──────────────────────────────────────────────────────
```

This partial-credit structure ensures the agent learns from partial successes rather than receiving only binary pass/fail signals — which is critical for stable GRPO convergence.

---

## 📐 How GRPO Training Works

**GRPO (Group Relative Policy Optimization)** trains the LLM agent by comparing groups of rollouts on the same task:

```
1. Sample N attempts of the same task (e.g., N=8 episodes of the bug-labeling task)
2. Score each attempt with the reward function above
3. Compute relative advantage: how much better/worse was each attempt vs the group mean?
4. Update LLM weights to make high-reward actions more likely
5. Repeat for 1000+ training loops
```

**Why GRPO fits this project perfectly:**
- The reward signal is deterministic (DB state is ground truth — no ambiguity)
- No human preference labels needed
- Works well with sparse rewards (the -1.0 penalty for merging bad code is a strong training signal)
- Each task episode is short enough to fit within the LLM's context window

---

## 📁 Project Structure

```
gitguard-ai/
│
├── Dockerfile                    # Container definition for HF Spaces deployment
├── requirements.txt              # Python dependencies
├── README.md                     # This file
│
├── environment/                  # Mock GitHub Web App
│   ├── app.py                    # FastAPI backend (issues, PRs, labels API)
│   ├── database.py               # SQLite schema and seed data
│   ├── seed_data.json            # Pre-loaded issues, PRs, injected bugs
│   └── frontend/                 # React UI
│       ├── src/
│       │   ├── pages/
│       │   │   ├── IssuesList.jsx
│       │   │   ├── IssueDetail.jsx
│       │   │   ├── PRList.jsx
│       │   │   └── PRDetail.jsx
│       │   └── components/
│       │       ├── LabelDropdown.jsx
│       │       ├── CodeDiffViewer.jsx
│       │       └── ReviewPanel.jsx
│       └── package.json
│
├── agent/
│   └── inference.py              # BrowserGym agent entry point (runs during eval)
│
├── grader/
│   └── evaluate.py               # Reward computation + score reporting
│
└── scripts/
    ├── validate-submission.sh    # OpenEnv pre-validation script
    └── train_grpo.py             # GRPO training loop (offline, GPU required)
```

---

## ⚙️ Setup & Installation

### Prerequisites

- Python 3.10+
- Node.js 18+
- Docker (for deployment)
- GPU with 16GB+ VRAM (for GRPO training only)

### 1. Clone the Repository

```bash
git clone https://github.com/your-username/gitguard-ai.git
cd gitguard-ai
```

### 2. Install Python Dependencies

```bash
pip install -r requirements.txt
```

### 3. Install & Build the Frontend

```bash
cd environment/frontend
npm install
npm run build
cd ../..
```

### 4. Seed the Database

```bash
python environment/database.py --seed
```

### 5. Start the Environment Locally

```bash
uvicorn environment.app:app --host 0.0.0.0 --port 8000
```

The mock GitHub UI will be live at `http://localhost:8000`

---

## 🤖 Running the Agent

### Inference (Evaluation Mode)

```bash
python agent/inference.py \
  --env-url http://localhost:8000 \
  --model claude-sonnet-4-20250514 \
  --task all
```

**Task options:** `easy`, `medium`, `hard`, `all`

### Grading

```bash
python grader/evaluate.py --db-path environment/gitguard.db
```

Output:
```
Task           Score    Notes
─────────────────────────────────────────
Easy Triage    0.85     4/5 labels correct
Medium Dupes   0.70     Correct link, slow navigation
Hard PR Review 1.00     Bug identified, merge blocked
─────────────────────────────────────────
TOTAL          2.55 / 3.00
```

---

## 🚀 Deployment on Hugging Face Spaces

### Step 1: Build and Test Docker Container Locally

```bash
docker build -t gitguard-ai .
docker run -p 7860:7860 gitguard-ai
```

Verify the environment loads at `http://localhost:7860`

### Step 2: Push to Hugging Face

```bash
# Install HF CLI
pip install huggingface_hub

# Login
huggingface-cli login

# Push to Spaces
git remote add space https://huggingface.co/spaces/your-username/gitguard-ai
git push space main
```

### Step 3: Run Pre-validation

```bash
bash scripts/validate-submission.sh
```

All checks must pass before submission.

---

## 🛠️ Tech Stack

| Layer | Technology |
|---|---|
| AI Agent Framework | BrowserGym |
| LLM | Claude Sonnet / GPT-4o |
| RL Training Algorithm | GRPO |
| Backend | FastAPI + SQLite |
| Frontend | React + Tailwind CSS |
| Containerization | Docker |
| Deployment | Hugging Face Spaces |
| Validation | OpenEnv CLI |

---

## 👥 Team

| Name | Role |
|---|---|
| [Your Name] | Agent Training & GRPO Implementation |
| [Teammate] | Frontend UI & Environment Design |
| [Teammate] | Grader & Reward Function Engineering |

---

## 📄 License

MIT License — see [LICENSE](./LICENSE) for details.

---

## 🙏 Acknowledgements

- [Scalar Meta](https://scalar.com) for organizing the OpenEnv Hackathon
- [BrowserGym](https://github.com/ServiceNow/BrowserGym) for the web agent framework
- [Hugging Face](https://huggingface.co) for free Spaces hosting

---

> *"The best code review is one where the reviewer catches the bug before it ships — even if that reviewer is an AI."*
