import mixpanel from "mixpanel-browser";

const TOKEN = process.env.NEXT_PUBLIC_MIXPANEL_TOKEN ?? "";
const ENABLED = Boolean(TOKEN) && TOKEN !== "PLACEHOLDER_REPLACE_BEFORE_DEPLOY";

export function initAnalytics() {
  if (!ENABLED) return;
  mixpanel.init(TOKEN, {
    track_pageview: true,
    persistence: "localStorage",
    ignore_dnt: false,
  });
}

export const track = {
  onboardingStart: () =>
    ENABLED && mixpanel.track("Onboarding Started"),

  onboardingComplete: (evolutionStage: string) =>
    ENABLED && mixpanel.track("Onboarding Completed", { evolution_stage: evolutionStage }),

  truthQuerySent: (props: {
    dimensions: string[];
    mode: "mentor" | "mirror" | "challenge";
    depth: "light" | "standard" | "deep";
  }) => ENABLED && mixpanel.track("Truth Query Sent", props),

  truthQueryReceived: (props: {
    grounded_score: number;
    dimension_primary: string;
    puzzle_count: number;
    response_ms: number;
  }) => ENABLED && mixpanel.track("Truth Query Received", props),

  beliefShiftLogged: (props: {
    dimension: string;
    tag: string;
    had_evidence: boolean;
  }) => ENABLED && mixpanel.track("Belief Shift Logged", props),

  blindSpotFlagged: (triggerPattern: string) =>
    ENABLED && mixpanel.track("Blind Spot Flagged", { trigger_pattern: triggerPattern }),

  sessionStart: (userId: string, evolutionStage: string) => {
    if (!ENABLED) return;
    mixpanel.identify(userId);
    mixpanel.people.set({ evolution_stage: evolutionStage });
    mixpanel.track("Session Started");
  },

  sessionEnd: (durationSeconds: number) =>
    ENABLED && mixpanel.track("Session Ended", { duration_s: durationSeconds }),

  soulMapViewed: () =>
    ENABLED && mixpanel.track("Soul Map Viewed"),

  coachReviewTriggered: (caseId: string) =>
    ENABLED && mixpanel.track("Coach Review Triggered", { case_id: caseId }),
};
