import React from 'react';
import { Toaster } from 'react-hot-toast';


const ToastProvider: React.FC = () => {
  return (
    <Toaster
      position="bottom-right" 
      reverseOrder={false} 
      toastOptions={{
        className: 'font-inter', 
        duration: 3000, 
        style: {
          background: '#363636',
          color: '#fff', 
          borderRadius: '8px', 
        },
        
        success: {
          iconTheme: {
            primary: '#10B981', 
            secondary: '#fff', 
          },
        },
        
        error: {
          iconTheme: {
            primary: '#EF4444', 
            secondary: '#fff', 
          },
        },
      }}
    />
  );
};

export default ToastProvider;
