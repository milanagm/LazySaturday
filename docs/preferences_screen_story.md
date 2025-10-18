# Preferences Setup Screen Blueprint

## User Story
**As** an immigrant user who wants to eat healthily while staying connected to my culture  
**I want** to configure my dietary, cultural, and lifestyle preferences in one guided experience  
**So that** the system can generate weekly meal plans and recipes rooted in my traditions and adaptable to my current home.

## Acceptance Criteria
- **UX & Flow:** Collect diet type, cultural cuisines (multi-select), dietary goals, allergies/intolerances, disliked ingredients, location, household size, meal cadence, and cooking time limit.
- **UI Behaviour:** Auto-save each section with inline confirmation (`Saved ✓`) and show wizard progress.
- **Validation:** Diet, primary culture, and country required; all other fields optional but encouraged.
- **Accessibility:** Full keyboard navigation, ARIA-labelled controls, localisation-ready copy, metric preferences auto-selected by country.
- **Persistence:** Preferences persist to the backend, linked to the authenticated user profile.
- **Integration:** Successful submission triggers `diet-plan-start` n8n workflow.
- **Feedback:** Display blocking state “Creating your personalized plan…” until redirect to plan overview or fallback message on timeout.

## UI Flow
1. **Entry Point (`/preferences`):** Post-login welcome message explaining personalisation benefit.
   - Primary CTA on landing page (“Start Your Cultural Plan”) links directly here.
2. **Diet Section:** Card grid (Vegan, Halal, Low-Carb, etc.) with tooltips; “Avoid specific foods” modal for dislikes.
3. **Culture Section:** Two-level selector (region → culture) with iconography; allow “Mixed background” for multi-select.
4. **Goals Section:** Icon chips for health, weight, muscle, sustainability, and time-saving.
5. **Location Section:** Geolocation detection with manual country dropdown and optional city input.
6. **Portion & Schedule Section:** Numeric inputs for household size, meals/day, slider for cooking time.
7. **Allergies Section:** Checkbox list plus free-text “Other”.
8. **Submission:** Primary action “Generate My First Week”; transition to loading screen followed by success redirect or graceful failure message.

## Frontend Technical Considerations
- **Form orchestration:** `react-hook-form` + Zod schema per step; integrate with MUI Stepper for wizard UX.
- **State:** Use Zustand to persist partial progress between steps; leverage TanStack Query mutation with optimistic cache update.
- **Internationalisation:** Bootstrap `i18next` for copy and unit toggles; derive measurement defaults from country.
- **Feedback:** MUI Snackbar for save confirmations; full-screen `Backdrop` during plan generation.

## API & Data Model
- **Endpoint:** `POST /user/preferences` returns `202 Accepted` with `{ status, workflow_id, message }`.
- **Payload additions:** `dietary_goals`, `disliked_ingredients`, `country`, `city`, `household_size`, `meals_per_day`, `cooking_time_limit`, and `additional_cultures` for mixed-background users.
- **Persistence:** Store data in `user_preferences` table with JSONB arrays for goals, allergies, dislikes, secondary cultures, and timestamps for auditing.
- **Follow-up retrieval:** Provide `GET /user/preferences` to hydrate the form on repeat visits.

## n8n Integration Trigger
1. Backend validates and stores preferences, then invokes `N8NClient.trigger_workflow("diet-plan-start", payload)` including user ID, locale, and preferences snapshot.
2. n8n orchestrates LLM meal plan generation, renders shopping list PDF, and POSTs results to `/workflows/plan-complete`.
3. Backend updates `meal_plans` record status and surfaces plan ID via polling or WebSocket event to the frontend.

## QA Scenarios
- Vegan + Turkish + Germany → workflow returns culturally aligned vegetarian plan with local ingredient substitutes.
- Multiple goals selected → verify payload passes all goals and n8n honours composite objectives.
- Optional sections skipped → defaults applied (balanced diet, 3 meals/day, 30 min cook time) without validation errors.
- Workflow failure → user sees reassurance toast and email notification remains queued.
