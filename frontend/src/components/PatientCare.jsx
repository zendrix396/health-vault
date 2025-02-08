import { motion } from "framer-motion";
import { FaStethoscope } from "react-icons/fa";

const PatientCare = () => {
  return (
    <div className="min-h-screen bg-[#0A0F1C] text-white relative overflow-hidden">
      {/* Background with reduced blur */}
      <div className="fixed inset-0 -z-10 overflow-hidden">
        <div className="absolute inset-0 bg-gradient-to-br from-[#0A0F1C] via-[#0A0F1C] to-[#0A0F1C]"></div>
        <motion.div
          animate={{
            scale: [1, 1.2, 1],
            rotate: [0, 180, 360],
          }}
          transition={{
            duration: 20,
            repeat: Infinity,
            ease: "linear"
          }}
          className="absolute top-1/4 left-1/4 w-96 h-96 rounded-full bg-blue-500/5 blur-[80px]"
        />
        <motion.div
          animate={{
            scale: [1.2, 1, 1.2],
            rotate: [0, -180, -360],
          }}
          transition={{
            duration: 15,
            repeat: Infinity,
            ease: "linear"
          }}
          className="absolute bottom-1/4 right-1/4 w-96 h-96 rounded-full bg-purple-500/5 blur-[80px]"
        />
      </div>

      {/* Content */}
      <div className="relative z-10 flex flex-col items-center justify-center min-h-screen p-6">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.8 }}
          className="text-center"
        >
          <div className="flex items-center justify-center mb-6">
            <FaStethoscope className="text-6xl text-blue-400 mr-4" />
            <h1 className="text-4xl font-bold bg-clip-text text-transparent bg-gradient-to-r from-blue-400 to-purple-400">
              Patient Care
            </h1>
          </div>
          
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ delay: 0.3 }}
            className="bg-[#0A0F1C]/80 border border-white/10 rounded-xl p-8 shadow-lg max-w-2xl mx-auto"
          >
            <h2 className="text-2xl font-semibold mb-4 text-blue-400">
              Coming Soon
            </h2>
            <p className="text-gray-300 text-lg">
              We're working hard to bring you comprehensive patient care and monitoring tools. 
              Stay tuned for updates!
            </p>
          </motion.div>
        </motion.div>
      </div>
    </div>
  );
};

export default PatientCare;