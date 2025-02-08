import { motion } from "framer-motion";
import { AnimatePresence } from "framer-motion";
import { 
  FaStethoscope, 
  FaSun, 
  FaMoon, 
  FaUserCircle,
  FaHome,
  FaFileMedical,
  FaPills,
  FaUserMd,
  FaTimes
} from "react-icons/fa";
import { useState } from "react";
const GlassCard = ({ children, className = "" }) => (
    <div className={`bg-[#0A0F1C]/95 border-b border-white/10 shadow-lg ${className}`}>
      {children}
    </div>
  );
  
  const NavLink = ({ icon, text, isActive, onClick }) => (
    <motion.button
      whileHover={{ scale: 1.05 }}
      whileTap={{ scale: 0.95 }}
      onClick={onClick}
      className={`flex items-center px-4 py-2 rounded-lg transition-all duration-300
                  ${isActive 
                    ? 'bg-blue-600/20 text-blue-400' 
                    : 'hover:bg-white/5 text-gray-400 hover:text-white'}`}
    >
      {icon}
      <span className="ml-2">{text}</span>
    </motion.button>
  );

  const LoginModal = ({ isOpen, onClose }) => (
    <AnimatePresence>
      {isOpen && (
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
            className="relative w-full max-w-md"
          >
            <GlassCard className="p-8">
              <div className="flex justify-between items-center mb-6">
                <h2 className="text-2xl font-bold text-white">Login to MediAI</h2>
                <motion.button
                  whileHover={{ scale: 1.1 }}
                  whileTap={{ scale: 0.9 }}
                  onClick={onClose}
                  className="text-gray-400 hover:text-white"
                >
                  <FaTimes className="text-xl" />
                </motion.button>
              </div>
  
              <form className="space-y-4">
                <div>
                  <label className="block text-gray-300 mb-2">Email</label>
                  <input
                    type="email"
                    className="w-full p-3 rounded-lg bg-black/30 border border-gray-700 
                             text-white placeholder-gray-500 focus:border-blue-500 
                             focus:ring-2 focus:ring-blue-500/20 outline-none"
                    placeholder="Enter your email"
                  />
                </div>
  
                <div>
                  <label className="block text-gray-300 mb-2">Password</label>
                  <input
                    type="password"
                    className="w-full p-3 rounded-lg bg-black/30 border border-gray-700 
                             text-white placeholder-gray-500 focus:border-blue-500 
                             focus:ring-2 focus:ring-blue-500/20 outline-none"
                    placeholder="Enter your password"
                  />
                </div>
  
                <div className="flex items-center justify-between">
                  <label className="flex items-center">
                    <input
                      type="checkbox"
                      className="w-4 h-4 rounded border-gray-700 bg-black/30 
                               text-blue-500 focus:ring-blue-500/20"
                    />
                    <span className="ml-2 text-gray-300">Remember me</span>
                  </label>
                  <a href="#" className="text-blue-400 hover:text-blue-300">
                    Forgot password?
                  </a>
                </div>
  
                <motion.button
                  whileHover={{ scale: 1.02 }}
                  whileTap={{ scale: 0.98 }}
                  className="w-full py-3 bg-blue-500 hover:bg-blue-600 
                           text-white rounded-lg font-semibold transition-colors"
                >
                  Login
                </motion.button>
  
                <div className="text-center text-gray-400">
                  Don't have an account?{" "}
                  <a href="#" className="text-blue-400 hover:text-blue-300">
                    Sign up
                  </a>
                </div>
              </form>
            </GlassCard>
          </motion.div>
        </motion.div>
      )}
    </AnimatePresence>
  );
const Navbar = ({ currentPage, setCurrentPage, isDarkMode, setIsDarkMode }) => {
  const [showLogin, setShowLogin] = useState(false);

  const navItems = [
    { id: 'home', text: 'Home', icon: <FaHome /> },
    { id: 'Medical Report Analysis', text: 'Medical Reports', icon: <FaFileMedical /> },
    { id: 'Medicine Recommendations', text: 'Recommendations', icon: <FaPills /> },
    { id: 'Doctor Portal', text: 'Doctor Portal', icon: <FaUserMd /> },
  ];

  return (
    <>
    <GlassCard className="fixed top-0 w-full z-50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between h-16">
          {/* Logo */}
          <motion.div 
            className="flex items-center cursor-pointer"
            whileHover={{ scale: 1.05 }}
            onClick={() => setCurrentPage('home')}
          >
            <FaStethoscope className="text-blue-400 text-3xl" />
            <span className="ml-2 text-xl font-bold text-white">MediAI</span>
          </motion.div>

          {/* Navigation Links */}
          <div className="hidden md:flex items-center space-x-2">
            {navItems.map((item) => (
              <NavLink
                key={item.id}
                icon={item.icon}
                text={item.text}
                isActive={currentPage === item.id}
                onClick={() => setCurrentPage(item.id)}
              />
            ))}
          </div>

          {/* Right Side Controls */}
          <div className="flex items-center space-x-4">
            <motion.button
              whileHover={{ scale: 1.1 }}
              whileTap={{ scale: 0.95 }}
              onClick={() => setIsDarkMode(!isDarkMode)}
              className="p-2 rounded-full hover:bg-white/5"
            >
              {isDarkMode ? 
                <FaSun className="text-yellow-400" /> : 
                <FaMoon className="text-gray-300" />
              }
            </motion.button>

            <motion.button
              whileHover={{ scale: 1.1 }}
              whileTap={{ scale: 0.95 }}
              onClick={() => setShowLogin(true)}
              className="flex items-center px-4 py-2 rounded-lg bg-blue-500/80 hover:bg-blue-600/80 text-white"
            >
              <FaUserCircle className="mr-2" />
              Login
            </motion.button>
          </div>
        </div>
      </div>
    </GlassCard>
    <LoginModal 
    isOpen={showLogin} 
    onClose={() => setShowLogin(false)} 
  />
</>
);
};

export default Navbar;