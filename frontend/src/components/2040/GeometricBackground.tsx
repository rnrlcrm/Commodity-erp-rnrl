import { motion } from "framer-motion";

export function GeometricBackground() {
  return (
    <div className="fixed inset-0 pointer-events-none overflow-hidden opacity-10">
      <svg className="absolute inset-0 w-full h-full" xmlns="http://www.w3.org/2000/svg">
        <defs>
          <linearGradient id="geo-gradient-1" x1="0%" y1="0%" x2="100%" y2="100%">
            <stop offset="0%" stopColor="#3b82f6" stopOpacity="0.3" />
            <stop offset="50%" stopColor="#2563eb" stopOpacity="0.2" />
            <stop offset="100%" stopColor="#60a5fa" stopOpacity="0.3" />
          </linearGradient>
          <linearGradient id="geo-gradient-2" x1="100%" y1="0%" x2="0%" y2="100%">
            <stop offset="0%" stopColor="#fbbf24" stopOpacity="0.25" />
            <stop offset="100%" stopColor="#3b82f6" stopOpacity="0.25" />
          </linearGradient>
        </defs>
        
        {/* Animated geometric shapes */}
        <motion.polygon
          points="0,0 200,100 0,200"
          fill="url(#geo-gradient-1)"
          initial={{ opacity: 0 }}
          animate={{ opacity: [0.3, 0.5, 0.3] }}
          transition={{ duration: 8, repeat: Infinity, ease: "easeInOut" }}
        />
        <motion.polygon
          points="200,100 400,0 400,200"
          fill="url(#geo-gradient-2)"
          initial={{ opacity: 0 }}
          animate={{ opacity: [0.25, 0.4, 0.25] }}
          transition={{ duration: 10, repeat: Infinity, ease: "easeInOut", delay: 1 }}
        />
        <motion.polygon
          points="400,0 600,150 400,200"
          fill="url(#geo-gradient-1)"
          initial={{ opacity: 0 }}
          animate={{ opacity: [0.35, 0.45, 0.35] }}
          transition={{ duration: 12, repeat: Infinity, ease: "easeInOut", delay: 2 }}
        />
        <motion.polygon
          points="600,150 800,50 800,250"
          fill="url(#geo-gradient-2)"
          initial={{ opacity: 0 }}
          animate={{ opacity: [0.3, 0.5, 0.3] }}
          transition={{ duration: 9, repeat: Infinity, ease: "easeInOut", delay: 0.5 }}
        />
        
        {/* Bottom layer */}
        <motion.polygon
          points="0,400 300,300 0,600"
          fill="url(#geo-gradient-1)"
          initial={{ opacity: 0 }}
          animate={{ opacity: [0.25, 0.4, 0.25] }}
          transition={{ duration: 11, repeat: Infinity, ease: "easeInOut", delay: 1.5 }}
        />
        <motion.polygon
          points="300,300 600,400 300,600"
          fill="url(#geo-gradient-2)"
          initial={{ opacity: 0 }}
          animate={{ opacity: [0.3, 0.45, 0.3] }}
          transition={{ duration: 13, repeat: Infinity, ease: "easeInOut", delay: 2.5 }}
        />
        
        {/* Right side */}
        <motion.polygon
          points="1200,0 1400,200 1200,400"
          fill="url(#geo-gradient-1)"
          initial={{ opacity: 0 }}
          animate={{ opacity: [0.35, 0.5, 0.35] }}
          transition={{ duration: 10, repeat: Infinity, ease: "easeInOut", delay: 0.8 }}
        />
        <motion.polygon
          points="1400,200 1600,100 1600,300"
          fill="url(#geo-gradient-2)"
          initial={{ opacity: 0 }}
          animate={{ opacity: [0.28, 0.42, 0.28] }}
          transition={{ duration: 14, repeat: Infinity, ease: "easeInOut", delay: 3 }}
        />
      </svg>
    </div>
  );
}
