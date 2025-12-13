import { motion } from "framer-motion";
import clsx from "clsx";

interface TimelineEvent {
  id: string;
  timestamp: string;
  title: string;
  description?: string;
  significance?: "low" | "medium" | "high" | "critical";
}

interface TimelineStreamProps {
  events: TimelineEvent[];
  accent?: "sun" | "saturn" | "mars";
}

export function TimelineStream({ events, accent = "saturn" }: TimelineStreamProps) {
  const getSignificanceGlow = (significance?: string) => {
    switch (significance) {
      case "critical":
        return "shadow-[0_0_24px_rgba(239,68,68,0.8)] scale-125";
      case "high":
        return "shadow-[0_0_20px_rgba(251,191,36,0.7)] scale-110";
      case "medium":
        return "shadow-[0_0_16px_rgba(96,165,250,0.6)]";
      default:
        return "shadow-[0_0_12px_rgba(148,163,184,0.5)]";
    }
  };

  const getLineColor = () => {
    switch (accent) {
      case "sun":
        return "bg-gradient-to-b from-sun-300/40 via-sun-400/20 to-sun-300/40";
      case "mars":
        return "bg-gradient-to-b from-mars-300/40 via-mars-400/20 to-mars-300/40";
      default:
        return "bg-gradient-to-b from-saturn-300/40 via-saturn-400/20 to-saturn-300/40";
    }
  };

  return (
    <div className="relative py-8">
      {/* Timeline line */}
      <div className={clsx(
        "absolute left-6 top-0 bottom-0 w-0.5",
        getLineColor()
      )} />

      {/* Events */}
      <div className="space-y-8">
        {events.map((event, idx) => (
          <motion.div
            key={event.id}
            initial={{ opacity: 0, x: -20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ delay: idx * 0.1, type: "spring", stiffness: 200, damping: 20 }}
            className="relative pl-16"
          >
            {/* Timeline dot */}
            <div className={clsx(
              "absolute left-3.5 top-2 w-5 h-5 rounded-full",
              "bg-space-700 border-2",
              accent === "sun" && "border-sun-400",
              accent === "mars" && "border-mars-400",
              accent === "saturn" && "border-saturn-400",
              getSignificanceGlow(event.significance)
            )} />

            {/* Event content */}
            <div className="bg-space-700/60 backdrop-blur-sm rounded-lg p-4 border border-pearl-500/10">
              <div className="flex items-start justify-between gap-4">
                <div className="flex-1">
                  <h4 className="text-pearl-100 font-medium mb-1">{event.title}</h4>
                  {event.description && (
                    <p className="text-pearl-400 text-sm">{event.description}</p>
                  )}
                </div>
                <span className="text-xs text-pearl-500 whitespace-nowrap">{event.timestamp}</span>
              </div>
            </div>
          </motion.div>
        ))}
      </div>
    </div>
  );
}
