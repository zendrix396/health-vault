import { motion, AnimatePresence } from "framer-motion";
import { useState, useEffect } from "react";
import { 
  FaStethoscope, 
  FaUserMd, 
  FaFileMedical, 
  FaPills,
  FaMoon,
  FaSun,
  FaUserCircle
} from "react-icons/fa";

// Update the BlurryBackground component
const BlurryBackground = () => {
    return (
      <div className="fixed inset-0 -z-10 overflow-hidden">
        {/* Dark gradient background */}
        <div className="absolute inset-0 bg-gradient-to-br from-[#0A0F1C] via-[#0A0F1C] to-[#0A0F1C]"></div>
        
        {/* Animated blurry shapes with reduced blur */}
        <motion.div
          animate={{
            scale: [1, 1.2, 1],
            rotate: [0, 180, 360],
            x: [0, 100, 0],
            y: [0, -50, 0],
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
            x: [0, -100, 0],
            y: [0, 50, 0],
          }}
          transition={{
            duration: 15,
            repeat: Infinity,
            ease: "linear"
          }}
          className="absolute top-1/3 right-1/4 w-96 h-96 rounded-full bg-purple-500/5 blur-[80px]"
        />
        <motion.div
          animate={{
            scale: [1, 1.3, 1],
            rotate: [0, 90, 360],
            x: [0, 50, 0],
            y: [0, 100, 0],
          }}
          transition={{
            duration: 18,
            repeat: Infinity,
            ease: "linear"
          }}
          className="absolute bottom-1/4 left-1/3 w-96 h-96 rounded-full bg-green-500/5 blur-[80px]"
        />
      </div>
    );
  };
const GlassCard = ({ children, className = "" }) => (
    <div className={`bg-[#0A0F1C]/80 border border-white/10 rounded-xl shadow-lg ${className}`}>
      {children}
    </div>
  );
  

const HomePage = ({ setCurrentPage }) => {
  const [isDark, setIsDark] = useState(true);
  const [showLogin, setShowLogin] = useState(false);
  const [mousePosition, setMousePosition] = useState({ x: 0, y: 0 });

  useEffect(() => {
    const handleMouseMove = (e) => {
      setMousePosition({ x: e.clientX, y: e.clientY });
    };

    window.addEventListener('mousemove', handleMouseMove);
    return () => window.removeEventListener('mousemove', handleMouseMove);
  }, []);

  const features = [
    {
      icon: <FaFileMedical className="text-4xl text-blue-400" />,
      title: "Medical Report Analysis",
      description: "Upload and analyze medical reports with AI-powered insights"
    },
    {
      icon: <FaPills className="text-4xl text-green-400" />,
      title: "Medicine Recommendations",
      description: "Get personalized medicine suggestions based on symptoms"
    },
    {
      icon: <FaUserMd className="text-4xl text-purple-400" />,
      title: "Doctor Portal",
      description: "Specialized tools and insights for healthcare professionals"
    },
    {
      icon: <FaStethoscope className="text-4xl text-red-400" />,
      title: "Patient Care",
      description: "Comprehensive patient care and monitoring tools"
    }
  ];


  return (
    <div className="min-h-screen text-white relative overflow-hidden">
      <BlurryBackground />

      {/* Hero Section */}
      <div className="pt-24 pb-20">
        <motion.div 
          className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8"
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.8 }}
        >
          <motion.h1 
            className="text-6xl font-bold text-center mb-6 bg-clip-text text-transparent bg-gradient-to-r from-blue-400 to-purple-400"
          >
            Welcome to MediAI
          </motion.h1>
          <motion.p 
            className="text-xl text-center mb-12 text-gray-300"
          >
            Your AI-powered medical assistant for smarter healthcare decisions
          </motion.p>

          {/* Features Grid */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-8 mt-16">
            {features.map((feature, index) => (
              <motion.div
                key={index}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: index * 0.1 }}
                whileHover={{ scale: 1.05 }}
                className="cursor-pointer"
                onClick={() => setCurrentPage(feature.title)}
              >
                <GlassCard className="p-6 h-full transition-all duration-300 hover:bg-white/20">
                  <div className="flex items-center mb-4">
                    {feature.icon}
                    <h3 className="text-xl font-semibold ml-4">{feature.title}</h3>
                  </div>
                  <p className="text-gray-300">{feature.description}</p>
                </GlassCard>
              </motion.div>
            ))}
          </div>
        </motion.div>
      </div>

      {/* Login Modal */}
      <AnimatePresence>
        {showLogin && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="fixed inset-0 bg-black/50 backdrop-blur-sm flex items-center justify-center p-4 z-50"
          >
            <motion.div
              initial={{ scale: 0.9, opacity: 0 }}
              animate={{ scale: 1, opacity: 1 }}
              exit={{ scale: 0.9, opacity: 0 }}
              className="relative"
            >
              <GlassCard className="p-8 max-w-md w-full">
                <h2 className="text-2xl font-bold mb-6">Login to MediAI</h2>
                <input
                  type="email"
                  placeholder="Email"
                  className="w-full p-3 rounded mb-4 bg-white/10 backdrop-blur-lg border border-white/20 focus:border-blue-400 outline-none"
                />
                <input
                  type="password"
                  placeholder="Password"
                  className="w-full p-3 rounded mb-6 bg-white/10 backdrop-blur-lg border border-white/20 focus:border-blue-400 outline-none"
                />
                <div className="flex justify-between">
                  <motion.button
                    whileHover={{ scale: 1.05 }}
                    whileTap={{ scale: 0.95 }}
                    className="bg-blue-500/80 backdrop-blur-sm text-white px-6 py-2 rounded"
                  >
                    Login
                  </motion.button>
                  <motion.button
                    whileHover={{ scale: 1.05 }}
                    whileTap={{ scale: 0.95 }}
                    onClick={() => setShowLogin(false)}
                    className="bg-white/10 backdrop-blur-sm px-6 py-2 rounded"
                  >
                    Cancel
                  </motion.button>
                </div>
              </GlassCard>
            </motion.div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
};

export default HomePage;