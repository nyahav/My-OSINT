import { useState } from 'react';
import { Link } from 'react-router-dom';
import { Menu, X } from 'lucide-react'; // Optional: use Heroicons/lucide

const Navbar = () => {
  const [menuOpen, setMenuOpen] = useState(false);

  const toggleMenu = () => setMenuOpen(prev => !prev);

  return (
    <nav className="bg-slate-900 text-white shadow-md sticky top-0 z-50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between items-center h-16">
          {/* Logo */}
          <div className="flex-shrink-0">
            <Link to="/" className="text-xl font-bold text-white hover:text-purple-400 transition">
              MyOSINT
            </Link>
          </div>

          {/* Desktop Navigation */}
          <div className="hidden md:flex space-x-6 items-center">
            <Link
              to="/dashboard"
              className="hover:text-purple-400 transition-colors"
            >
              Dashboard
            </Link>
            <Link
              to="/scandomain"
              className="hover:text-purple-400 transition-colors"
            >
              Scan Domain
            </Link>
            <Link
              to="/"
              className="px-3 py-1 bg-red-700 hover:bg-red-800 text-white hover:text-black rounded-lg transition"
            >
              Logout
            </Link>
          </div>

          {/* Mobile Menu Button */}
          <div className="md:hidden">
            <button
              onClick={toggleMenu}
              className="text-gray-300 hover:text-white focus:outline-none"
              aria-label="Toggle menu"
            >
              {menuOpen ? <X className="w-6 h-6" /> : <Menu className="w-6 h-6" />}
            </button>
          </div>
        </div>
      </div>

      {/* Mobile Menu */}
      {menuOpen && (
        <div className="md:hidden bg-slate-800 px-4 pt-4 pb-6 space-y-3 transition-all duration-300">
          <Link
            to="/dashboard"
            className="block text-gray-300 hover:text-white hover:bg-slate-700 px-3 py-2 rounded-md transition"
            onClick={() => setMenuOpen(false)}
          >
            Dashboard
          </Link>
          <Link
            to="/scandomain"
            className="block text-gray-300 hover:text-white hover:bg-slate-700 px-3 py-2 rounded-md transition"
            onClick={() => setMenuOpen(false)}
          >
            Scan Domain
          </Link>
          <Link
            to="/"
            className="block text-gray-300 hover:text-white hover:bg-red-600 px-3 py-2 rounded-md transition"
            onClick={() => setMenuOpen(false)}
          >
            Logout
          </Link>
        </div>
      )}
    </nav>
  );
};

export default Navbar;
