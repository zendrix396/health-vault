import { motion } from "framer-motion";
import { FaUserMd, FaLock, FaClock, FaTools } from "react-icons/fa";

const FeatureCard = ({ icon, title, description }) => (
  <motion.div
    initial={{ opacity: 0, y: 20 }}
    animate={{ opacity: 1, y: 0 }}
    className="bg-[#0A0F1C]/80 border border-white/10 rounded-xl p-6 shadow-lg"
  >
    <div className="flex items-center mb-4">
      {icon}
      <h3 className="text-xl font-semibold ml-3 text-gray-200">{title}</h3>
    </div>
    <p className="text-gray-400">{description}</p>
  </motion.div>
);

const DoctorPortal = () => {
  const features = [
    {
      icon: <FaLock className="text-3xl text-purple-400" />,
      title: "Secure Access",
      description: "Protected healthcare professional portal with encrypted data transmission"
    },
    {
      icon: <FaTools className="text-3xl text-blue-400" />,
      title: "Advanced Tools",
      description: "Specialized diagnostic and analysis tools for medical professionals"
    },
    {
      icon: <FaClock className="text-3xl text-green-400" />,
      title: "Coming Soon",
      description: "We're working on bringing you more powerful features for patient care"
    }
  ];

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
          className="absolute top-1/4 left-1/4 w-96 h-96 rounded-full bg-purple-500/5 blur-[80px]"
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
          className="absolute bottom-1/4 right-1/4 w-96 h-96 rounded-full bg-blue-500/5 blur-[80px]"
        />
      </div>

      {/* Content */}
      <div className="relative z-10 container mx-auto px-4 py-16">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.8 }}
          className="text-center mb-16"
        >
          <div className="flex items-center justify-center mb-6">
            <FaUserMd className="text-6xl text-purple-400 mr-4" />
            <h1 className="text-4xl font-bold bg-clip-text text-transparent bg-gradient-to-r from-purple-400 to-blue-400">
              Doctor Portal
            </h1>
          </div>
          
          <p className="text-xl text-gray-300 max-w-2xl mx-auto">
            A specialized platform for healthcare professionals with advanced tools and insights
          </p>
        </motion.div>

        {/* Coming Soon Message */}
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.3 }}
          className="bg-[#0A0F1C]/80 border border-white/10 rounded-xl p-8 shadow-lg max-w-3xl mx-auto mb-16"
        >
          <h2 className="text-2xl font-semibold mb-4 text-purple-400">
            Portal Access Coming Soon
          </h2>
          <p className="text-gray-300 text-lg">
            We're currently developing a comprehensive suite of tools for medical professionals. 
            Register your interest to be notified when we launch.
          </p>
        </motion.div>

        {/* Feature Grid */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-8 max-w-5xl mx-auto">
          {features.map((feature, index) => (
            <motion.div
              key={index}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: index * 0.2 }}
            >
              <FeatureCard {...feature} />
            </motion.div>
          ))}
        </div>

        {/* Registration Interest Form */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.6 }}
          className="mt-16 max-w-md mx-auto"
        >
          <div className="bg-[#0A0F1C]/80 border border-white/10 rounded-xl p-8 shadow-lg">
            <h3 className="text-xl font-semibold mb-6 text-center text-gray-200">
              Register Your Interest
            </h3>
            <form className="space-y-4">
              <input
                type="email"
                placeholder="Professional Email"
                className="w-full p-3 rounded-lg bg-black/20 border border-white/10 text-white placeholder-gray-500 focus:outline-none focus:border-purple-400"
              />
              <select className="w-full p-3 rounded-lg bg-black/20 border border-white/10 text-gray-400 focus:outline-none focus:border-purple-400">
                <option value="">Select Specialization</option>
                <option value="general">General Practice</option>
                <option value="cardiology">Cardiology</option>
                <option value="neurology">Neurology</option>
                <option value="other">Other</option>
              </select>
              <motion.button
                whileHover={{ scale: 1.02 }}
                whileTap={{ scale: 0.98 }}
                className="w-full py-3 rounded-lg bg-gradient-to-r from-purple-500 to-blue-500 text-white font-semibold hover:from-purple-600 hover:to-blue-600 transition-all duration-300"
              >
                Notify Me
              </motion.button>
            </form>
          </div>
        </motion.div>
      </div>
    </div>
  );
};

export default DoctorPortal;