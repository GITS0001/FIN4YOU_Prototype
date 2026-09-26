# UI/UX Documentation
**FIN4YOU — Financial Health Copilot**

## 1. Design Principles
The FIN4YOU interface is designed as a modern, clean, and highly responsive SaaS application. Its primary goal is to demystify complex financial data by strictly separating observed facts from simulated futures, while establishing trust through complete mathematical transparency.

**Key Principles:**
- **Clarity Over Complexity:** Present high-level insights first, offering drill-down capabilities for detailed metrics.
- **Visual Segregation of Time:** Clear visual cues to distinguish between past (Observed), present (State), and future (Projected/Simulated).
- **Transparent AI:** The Artha AI Copilot must always expose its "Decision Trace" so users understand exactly how conclusions were reached.

## 2. Component Hierarchy & Navigation
The application utilizes a robust layout wrapper comprising a left-aligned `Sidebar` and a top-aligned `Topbar`.
- **Dashboard (`/dashboard`):** The central hub providing a holistic view of the user's financial state, expense ratios, detected anomalies, upcoming obligations, and quick-access Copilot prompts.
- **Artha AI / Copilot (`/copilot`):** A conversational interface for natural language financial queries.
- **Insights (`/insights`):** Visual breakdowns of spending categories and trends.
- **Forecast (`/forecast`):** A forward-looking analysis of cash flow health, contrasting observed history against next month's projection.
- **What-If (`/what-if`):** An interactive scenario builder for modeling spending modifications.
- **Affordability (`/affordability`):** A dedicated tool to check if specific purchases are viable and view installment options.
- **Profile (`/profile`):** User configuration for adjusting the minimum balance buffer and financial priorities.

## 3. Communication of State
To prevent user confusion, the UI strictly categorizes data using visual markers:
- **Observed:** Displayed in standard, solid colors. Represents historical, factual aggregations.
- **Prediction:** Displayed with dashed lines on charts or with a "Projected" badge. Represents the deterministic forecast for the upcoming month.
- **Scenario / Expected Impact:** Highlighted using comparative UI elements (e.g., baseline vs. modified state). Positive impacts are colored green, negative impacts are colored amber or red.
- **Confidence Indicators:** Provides contextual text detailing if predictions are based on highly consistent or highly variable historical spending patterns.

## 4. Key UI Components

### 4.1 Dashboard
- **KPI Cards:** Top-level metrics summarizing income, expenses, and savings over the observed period.
- **"What Needs Attention":** An alert-driven card prioritizing urgent cash-flow gaps or negative savings trends. Automatically collapses if finances are perfectly stable.
- **Obligations:** A concise list of recurring subscriptions and fixed costs expected in the next month.

### 4.2 Artha AI (CopilotChat)
- **Chat Interface:** Standard conversational flow with distinct user and AI message bubbles.
- **Structured Responses:** The AI does not just return raw text. It returns structured JSON that the UI maps into interactive tables, charts, and metric comparison cards.
- **Decision Trace:** A dedicated expandable accordion appended to AI responses detailing the exact numbers and rules the engine used to derive the answer.

### 4.3 What-If & Affordability Simulators
- **Input Controls:** Quick-select suggestion buttons (e.g., "10% reduction", "₹5,000 purchase") alongside manual input fields.
- **Comparative Visuals:** Side-by-side metric cards showing "Current Projected Cash Flow" vs "New Projected Cash Flow".

## 5. Responsive Behavior & Accessibility
- **Responsive Layout:** The application uses Tailwind CSS grid systems that gracefully degrade from complex multi-column dashboards on desktop to single-column, scrollable views on mobile devices. 
- **Navigation:** The Sidebar collapses into a hamburger menu on smaller screens, accessible via the Topbar.
- **Typography & Spacing:** Standardized font scales and padding ensure readability. Redundant whitespace is actively minimized to ensure high data density without clutter.

## 6. Error & Loading States
- **Skeletons:** Loading phases display animated skeleton placeholders matching the target component's dimensions to prevent layout shift.
- **Error States:** Failed API calls trigger contextual error boundaries with "Retry" capabilities rather than crashing the entire application. Empty states (e.g., no upcoming obligations) are explicitly labeled to confirm the lack of data rather than appearing broken.
- **Client-Side Validation:** Form inputs disable submit buttons until valid numbers are provided to prevent malformed API requests.
