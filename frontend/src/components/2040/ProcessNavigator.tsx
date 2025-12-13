import { motion } from 'framer-motion';

interface Step {
  id: string;
  name: string;
  status: 'pending' | 'active' | 'done' | 'error';
}

interface Props {
  steps: Step[];
}

export function ProcessNavigator({ steps }: Readonly<Props>) {
  return (
    <div className="flex items-center space-x-4">
      {steps.map((s, idx) => (
        <div key={s.id} className="flex items-center">
          <motion.div
                className={(() => {
                  const base = 'px-3 py-2 rounded-lg text-sm ';
                  let statusClass = 'bg-space-500/10';
                  if (s.status === 'active') statusClass = 'bg-saturn-500/10 shadow-holo';
                  else if (s.status === 'done') statusClass = 'bg-pearl-50/5';
                  else if (s.status === 'error') statusClass = 'bg-mars-500/10';
                  return base + statusClass;
                })()}
            initial={{ opacity: 0, y: 4 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.25 }}
          >
            <span className="text-pearl-100 text-sm">{s.name}</span>
          </motion.div>
          {idx < steps.length - 1 && (
            <div className="mx-4 w-8 h-px bg-gradient-to-r from-saturn-500/30 to-sun-500/30" />
          )}
        </div>
      ))}
    </div>
  );
}

export default ProcessNavigator;