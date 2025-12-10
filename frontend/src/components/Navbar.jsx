import { Activity, FileText, Home, LogIn } from "lucide-react";

const navItemClass = (currentPage, page) =>
  `flex items-center gap-2 px-4 py-1.5 text-sm transition-all duration-200 border border-transparent ${
    currentPage === page
      ? "text-white bg-zinc-900 border-zinc-800"
      : "text-zinc-500 hover:text-zinc-300 hover:bg-zinc-900/50"
  }`;

const Navbar = ({ currentPage, onNavigate }) => {
  return (
    <nav className="sticky top-0 z-50 w-full nav-tint bg-black/60 backdrop-blur-md border-b border-zinc-900">
      <div className="max-w-7xl mx-auto px-6">
        <div className="flex justify-between items-center h-16">
          <button
            type="button"
            className="flex items-center gap-3 cursor-pointer group"
            onClick={() => onNavigate("home")}
          >
            <div className="w-8 h-8 flex items-center justify-center text-white">
              <svg
                xmlns="http://www.w3.org/2000/svg"
                viewBox="0 0 512 512"
                className="w-6 h-6"
                fill="currentColor"
              >
                <path d="M447.1 112c-34.2.5-62.3 28.4-63 62.6-.5 24.3 12.5 45.6 32 56.8V344c0 57.3-50.2 104-112 104-60 0-109.2-44.1-111.9-99.2C265 333.8 320 269.2 320 192V36.6c0-11.4-8.1-21.3-19.3-23.5L237.8.5c-13-2.6-25.6 5.8-28.2 18.8L206.4 35c-2.6 13 5.8 25.6 18.8 28.2l30.7 6.1v121.4c0 52.9-42.2 96.7-95.1 97.2-53.4.5-96.9-42.7-96.9-96V69.4l30.7-6.1c13-2.6 21.4-15.2 18.8-28.2l-3.1-15.7C107.7 6.4 95.1-2 82.1.6L19.3 13C8.1 15.3 0 25.1 0 36.6V192c0 77.3 55.1 142 128.1 156.8C130.7 439.2 208.6 512 304 512c97 0 176-75.4 176-168V231.4c19.1-11.1 32-31.7 32-55.4 0-35.7-29.2-64.5-64.9-64zm.9 80c-8.8 0-16-7.2-16-16s7.2-16 16-16 16 7.2 16 16-7.2 16-16 16z"></path>
              </svg>
            </div>
            <span className="text-lg font-bold tracking-tight text-white group-hover:text-zinc-300 transition-colors">
              MediAI
            </span>
          </button>

          <div className="hidden md:flex items-center gap-6">
            <button
              onClick={() => onNavigate("home")}
              className={navItemClass(currentPage, "home")}
            >
              <Home className="w-3.5 h-3.5" />
              <span>Home</span>
            </button>
            <button
              onClick={() => onNavigate("reports")}
              className={navItemClass(currentPage, "reports")}
            >
              <FileText className="w-3.5 h-3.5" />
              <span>Reports</span>
            </button>
            <button
              onClick={() => onNavigate("recommendations")}
              className={navItemClass(currentPage, "recommendations")}
            >
              <Activity className="w-3.5 h-3.5" />
              <span>Recommendations</span>
            </button>
          </div>

          <button
            onClick={() => onNavigate("login")}
            className="hidden md:flex items-center gap-2 text-zinc-400 hover:text-white font-medium text-xs uppercase tracking-wide px-4 py-2 border border-zinc-800 hover:border-zinc-600 transition-all bg-zinc-950"
          >
            <span>Login</span>
            <span className="bg-zinc-800 text-zinc-400 px-1.5 py-0.5 rounded-[1px] text-[10px]">
              L
            </span>
          </button>

          <div className="md:hidden">
            <button
              onClick={() => onNavigate("home")}
              className="p-2 text-zinc-400 border border-zinc-800 bg-zinc-900"
            >
              <Home className="w-5 h-5" />
            </button>
          </div>
        </div>
      </div>
    </nav>
  );
};

export default Navbar;