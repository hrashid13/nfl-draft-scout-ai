import React from 'react';

const Footer = () => {
  return (
    <footer 
      className="bg-gray-900 border-t border-gray-800 mt-auto py-6"
      style={{
        backgroundColor: '#111827',
        borderTop: '1px solid rgba(31, 41, 55, 0.5)',
        marginTop: 'auto',
        padding: '1.5rem 0'
      }}
    >
      <div 
        className="max-w-7xl mx-auto px-4 text-center"
        style={{
          maxWidth: '80rem',
          margin: '0 auto',
          padding: '0 1rem',
          textAlign: 'center'
        }}
      >
        <p 
          className="text-gray-400 text-sm"
          style={{
            color: '#9CA3AF',
            fontSize: '0.875rem'
          }}
        >
          © 2026 - NFL Draft Scout AI - Hesham Rashid - Check out some of my other work at my{' '}
          <a 
            href="https://www.heshamrashid.org/" 
            target="_blank" 
            rel="noopener noreferrer"
            className="text-green-400 hover:text-green-300 underline transition-colors"
            style={{
              color: '#4ade80',
              textDecoration: 'underline',
              transition: 'color 0.2s'
            }}
            onMouseEnter={(e) => e.target.style.color = '#86efac'}
            onMouseLeave={(e) => e.target.style.color = '#4ade80'}
          >
            Personal Portfolio
          </a>
        </p>
      </div>
    </footer>
  );
};

export default Footer;