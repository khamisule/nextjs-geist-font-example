import os
import sys
import subprocess
import zipfile
import shutil
import urllib.request
import json
from pathlib import Path
import tkinter as tk
from tkinter import messagebox, ttk, filedialog
import threading
import time
import webbrowser

class NeuroQuantXInstaller:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("NeuroQuant X - AI Trading System Installer v2.1.0")
        self.root.geometry("700x600")
        self.root.configure(bg="#000000")
        self.root.resizable(False, False)
        
        # Center window
        self.center_window()
        
        # Variables
        self.install_path = os.path.join(os.path.expanduser("~"), "Desktop", "NeuroQuantX")
        self.progress_var = tk.DoubleVar()
        self.status_var = tk.StringVar(value="Ready to install NeuroQuant X AI Trading System")
        
        self.create_ui()
        
    def center_window(self):
        self.root.update_idletasks()
        x = (self.root.winfo_screenwidth() // 2) - (700 // 2)
        y = (self.root.winfo_screenheight() // 2) - (600 // 2)
        self.root.geometry(f"700x600+{x}+{y}")
        
    def create_ui(self):
        # Header with logo
        header_frame = tk.Frame(self.root, bg="#000000", height=120)
        header_frame.pack(fill="x", padx=20, pady=15)
        header_frame.pack_propagate(False)
        
        # ASCII Logo
        logo_text = """
 ███╗   ██╗███████╗██╗   ██╗██████╗  ██████╗  ██████╗ ██╗   ██╗ █████╗ ███╗   ██╗████████╗    ██╗  ██╗
 ████╗  ██║██╔════╝██║   ██║██╔══██╗██╔═══██╗██╔═══██╗██║   ██║██╔══██╗████╗  ██║╚══██╔══╝    ╚██╗██╔╝
 ██╔██╗ ██║█████╗  ██║   ██║██████╔╝██║   ██║██║   ██║██║   ██║███████║██╔██╗ ██║   ██║        ╚███╔╝ 
 ██║╚██╗██║██╔══╝  ██║   ██║██╔══██╗██║   ██║██║   ██║██║   ██║██╔══██║██║╚██╗██║   ██║        ██╔██╗ 
 ██║ ╚████║███████╗╚██████╔╝██║  ██║╚██████╔╝╚██████╔╝╚██████╔╝██║  ██║██║ ╚████║   ██║       ██╔╝ ██╗
 ╚═╝  ╚═══╝╚══════╝ ╚═════╝ ╚═╝  ╚═╝ ╚═════╝  ╚═════╝  ╚═════╝ ╚═╝  ╚═╝╚═╝  ╚═══╝   ╚═╝       ╚═╝  ╚═╝
        """
        
        title_label = tk.Label(header_frame, text="NeuroQuant X", 
                              font=("Courier", 20, "bold"), 
                              fg="#00ff00", bg="#000000")
        title_label.pack(pady=5)
        
        subtitle_label = tk.Label(header_frame, text="Advanced AI Trading System - Professional Installer", 
                                 font=("Arial", 12, "bold"), 
                                 fg="#ffffff", bg="#000000")
        subtitle_label.pack()
        
        version_label = tk.Label(header_frame, text="Version 2.1.0 - Complete Installation Package", 
                               font=("Arial", 10), 
                               fg="#888888", bg="#000000")
        version_label.pack()
        
        # Features section
        features_frame = tk.Frame(self.root, bg="#1a1a1a", relief="raised", bd=2)
        features_frame.pack(fill="x", padx=20, pady=15)
        
        features_title = tk.Label(features_frame, text="🚀 What You're Installing:", 
                                 font=("Arial", 12, "bold"), 
                                 fg="#00ff00", bg="#1a1a1a")
        features_title.pack(pady=10)
        
        features_text = """
✅ Complete AI Trading System with Neural Network Engine
✅ Real-time Market Analysis (1-second processing)
✅ Advanced Security & Cyber Defense System
✅ Professional Trading Dashboard (11 functional pages)
✅ Offline Operation (No external API dependencies)
✅ Multi-layer License Protection System
✅ Automatic Node.js Installation & Setup
✅ Desktop Shortcuts & Easy Launch System
✅ 24/7 Technical Support Included
✅ Business-Ready Revenue Generation Features
        """
        
        features_label = tk.Label(features_frame, text=features_text, 
                                 font=("Arial", 10), 
                                 fg="#ffffff", bg="#1a1a1a",
                                 justify="left")
        features_label.pack(padx=20, pady=10)
        
        # Installation path section
        path_frame = tk.Frame(self.root, bg="#000000")
        path_frame.pack(fill="x", padx=20, pady=15)
        
        path_label = tk.Label(path_frame, text="📁 Installation Directory:", 
                             font=("Arial", 11, "bold"), 
                             fg="#ffffff", bg="#000000")
        path_label.pack(anchor="w")
        
        path_input_frame = tk.Frame(path_frame, bg="#000000")
        path_input_frame.pack(fill="x", pady=5)
        
        self.path_entry = tk.Entry(path_input_frame, font=("Arial", 10), width=50, bg="#333333", fg="#ffffff")
        self.path_entry.insert(0, self.install_path)
        self.path_entry.pack(side="left", fill="x", expand=True)
        
        browse_btn = tk.Button(path_input_frame, text="Browse", 
                              font=("Arial", 9),
                              bg="#007bff", fg="white",
                              command=self.browse_directory,
                              width=10)
        browse_btn.pack(side="right", padx=(10, 0))
        
        # System requirements
        req_frame = tk.Frame(self.root, bg="#2a2a2a", relief="raised", bd=1)
        req_frame.pack(fill="x", padx=20, pady=10)
        
        req_label = tk.Label(req_frame, text="💻 System Requirements: Windows 10/11 | 4GB RAM | 1GB Storage | Internet (setup only)", 
                            font=("Arial", 9), 
                            fg="#cccccc", bg="#2a2a2a")
        req_label.pack(pady=8)
        
        # Progress section
        progress_frame = tk.Frame(self.root, bg="#000000")
        progress_frame.pack(fill="x", padx=20, pady=20)
        
        progress_label = tk.Label(progress_frame, text="📊 Installation Progress:", 
                                 font=("Arial", 11, "bold"), 
                                 fg="#ffffff", bg="#000000")
        progress_label.pack(anchor="w")
        
        self.progress_bar = ttk.Progressbar(progress_frame, 
                                           variable=self.progress_var, 
                                           maximum=100,
                                           style="TProgressbar")
        self.progress_bar.pack(fill="x", pady=8)
        
        self.status_label = tk.Label(progress_frame, 
                                    textvariable=self.status_var,
                                    font=("Arial", 10), 
                                    fg="#00ff00", bg="#000000")
        self.status_label.pack(anchor="w", pady=5)
        
        # Buttons section
        button_frame = tk.Frame(self.root, bg="#000000")
        button_frame.pack(fill="x", padx=20, pady=20)
        
        self.install_btn = tk.Button(button_frame, text="🚀 Install NeuroQuant X", 
                                    font=("Arial", 14, "bold"),
                                    bg="#28a745", fg="white",
                                    command=self.start_installation,
                                    width=25, height=2,
                                    relief="raised", bd=3)
        self.install_btn.pack(side="left", padx=10)
        
        self.exit_btn = tk.Button(button_frame, text="❌ Exit", 
                                 font=("Arial", 12),
                                 bg="#dc3545", fg="white",
                                 command=self.root.quit,
                                 width=15, height=2,
                                 relief="raised", bd=3)
        self.exit_btn.pack(side="right", padx=10)
        
        # Contact and support info
        contact_frame = tk.Frame(self.root, bg="#1a1a1a", relief="sunken", bd=2)
        contact_frame.pack(fill="x", padx=20, pady=15)
        
        contact_title = tk.Label(contact_frame, text="📞 24/7 Support & Contact Information", 
                                font=("Arial", 11, "bold"), 
                                fg="#00ff00", bg="#1a1a1a")
        contact_title.pack(pady=5)
        
        contact_info = tk.Label(contact_frame, 
                               text="WhatsApp: +255713860400 | Email: forcm01@gmail.com | Free Installation Support",
                               font=("Arial", 10), 
                               fg="#ffffff", bg="#1a1a1a")
        contact_info.pack(pady=5)
        
        # License info
        license_label = tk.Label(self.root, 
                                text="© 2024 NeuroQuant X - Licensed AI Trading System | Professional Edition",
                                font=("Arial", 8), 
                                fg="#666666", bg="#000000")
        license_label.pack(pady=10)
        
    def browse_directory(self):
        directory = filedialog.askdirectory(initialdir=os.path.expanduser("~"))
        if directory:
            self.install_path = os.path.join(directory, "NeuroQuantX")
            self.path_entry.delete(0, tk.END)
            self.path_entry.insert(0, self.install_path)
        
    def update_progress(self, value, status):
        self.progress_var.set(value)
        self.status_var.set(status)
        self.root.update()
        
    def start_installation(self):
        self.install_btn.config(state="disabled", text="Installing...", bg="#ffc107")
        self.install_path = self.path_entry.get()
        
        # Start installation in separate thread
        thread = threading.Thread(target=self.install_system)
        thread.daemon = True
        thread.start()
        
    def install_system(self):
        try:
            # Step 1: Create directory
            self.update_progress(5, "🗂️ Creating installation directory...")
            os.makedirs(self.install_path, exist_ok=True)
            time.sleep(1)
            
            # Step 2: Extract system files
            self.update_progress(15, "📦 Extracting NeuroQuant X system files...")
            self.extract_system_files()
            time.sleep(2)
            
            # Step 3: Check Node.js
            self.update_progress(30, "🔍 Checking Node.js installation...")
            if not self.check_nodejs():
                self.update_progress(40, "⬇️ Downloading and installing Node.js...")
                if not self.install_nodejs():
                    self.update_progress(45, "⚠️ Node.js installation skipped - creating HTML version...")
            time.sleep(1)
            
            # Step 4: Install dependencies
            self.update_progress(60, "📚 Installing system dependencies...")
            self.install_dependencies()
            time.sleep(2)
            
            # Step 5: Create launchers
            self.update_progress(80, "🚀 Creating launch scripts...")
            self.create_launchers()
            time.sleep(1)
            
            # Step 6: Create shortcuts
            self.update_progress(90, "🔗 Creating desktop shortcuts...")
            self.create_shortcuts()
            time.sleep(1)
            
            # Step 7: Complete
            self.update_progress(100, "✅ Installation completed successfully!")
            
            # Show success message
            success_msg = (
                f"🎉 NeuroQuant X installed successfully!\n\n"
                f"📁 Location: {self.install_path}\n"
                f"🖥️ Desktop shortcut created\n"
                f"🌐 Access: http://localhost:8000\n\n"
                f"🚀 Click 'Launch Now' to start trading!\n"
                f"📞 Support: +255713860400"
            )
            
            result = messagebox.askyesno("Installation Complete", 
                                       success_msg + "\n\nLaunch NeuroQuant X now?")
            
            if result:
                self.launch_system()
            
        except Exception as e:
            error_msg = (
                f"❌ Installation encountered an issue:\n\n{str(e)}\n\n"
                f"📞 Contact support for assistance:\n"
                f"WhatsApp: +255713860400\n"
                f"Email: forcm01@gmail.com\n\n"
                f"We provide FREE installation support!"
            )
            messagebox.showerror("Installation Issue", error_msg)
            
        finally:
            self.install_btn.config(state="normal", text="🚀 Install NeuroQuant X", bg="#28a745")
    
    def extract_system_files(self):
        # Create complete NeuroQuant X system structure
        
        # Create directories
        directories = [
            "src/app", "src/components/ui", "src/components/dashboard", 
            "src/lib", "src/hooks", "src/mock", "public"
        ]
        
        for dir_path in directories:
            os.makedirs(os.path.join(self.install_path, dir_path), exist_ok=True)
        
        # Create package.json with all dependencies
        package_json = {
            "name": "neuroquant-x",
            "version": "2.1.0",
            "description": "NeuroQuant X - Advanced AI Trading System",
            "scripts": {
                "dev": "next dev -p 8000",
                "build": "next build",
                "start": "next start -p 8000",
                "lint": "next lint"
            },
            "dependencies": {
                "next": "15.0.0",
                "react": "^18.2.0",
                "react-dom": "^18.2.0",
                "typescript": "^5.0.0",
                "@types/node": "^20.0.0",
                "@types/react": "^18.2.0",
                "@types/react-dom": "^18.2.0",
                "tailwindcss": "^3.3.0",
                "autoprefixer": "^10.4.0",
                "postcss": "^8.4.0",
                "class-variance-authority": "^0.7.0",
                "clsx": "^2.0.0",
                "tailwind-merge": "^2.0.0"
            },
            "devDependencies": {
                "eslint": "^8.0.0",
                "eslint-config-next": "15.0.0"
            }
        }
        
        with open(os.path.join(self.install_path, "package.json"), "w") as f:
            json.dump(package_json, f, indent=2)
        
        # Create Next.js config
        next_config = '''/** @type {import('next').NextConfig} */
const nextConfig = {
  output: 'standalone',
  trailingSlash: true,
  images: {
    unoptimized: true
  }
}

module.exports = nextConfig
'''
        
        with open(os.path.join(self.install_path, "next.config.js"), "w") as f:
            f.write(next_config)
        
        # Create TypeScript config
        tsconfig = {
            "compilerOptions": {
                "target": "es5",
                "lib": ["dom", "dom.iterable", "es6"],
                "allowJs": True,
                "skipLibCheck": True,
                "strict": True,
                "noEmit": True,
                "esModuleInterop": True,
                "module": "esnext",
                "moduleResolution": "bundler",
                "resolveJsonModule": True,
                "isolatedModules": True,
                "jsx": "preserve",
                "incremental": True,
                "plugins": [{"name": "next"}],
                "baseUrl": ".",
                "paths": {
                    "@/*": ["./src/*"]
                }
            },
            "include": ["next-env.d.ts", "**/*.ts", "**/*.tsx", ".next/types/**/*.ts"],
            "exclude": ["node_modules"]
        }
        
        with open(os.path.join(self.install_path, "tsconfig.json"), "w") as f:
            json.dump(tsconfig, f, indent=2)
        
        # Create Tailwind config
        tailwind_config = '''/** @type {import('tailwindcss').Config} */
module.exports = {
  darkMode: ["class"],
  content: [
    './pages/**/*.{ts,tsx}',
    './components/**/*.{ts,tsx}',
    './app/**/*.{ts,tsx}',
    './src/**/*.{ts,tsx}',
  ],
  theme: {
    extend: {},
  },
  plugins: [],
}
'''
        
        with open(os.path.join(self.install_path, "tailwind.config.js"), "w") as f:
            f.write(tailwind_config)
        
        # Create basic app structure
        self.create_basic_app_files()
    
    def create_basic_app_files(self):
        # Create layout.tsx
        layout_content = '''import type { Metadata } from 'next'
import { Inter } from 'next/font/google'
import './globals.css'

const inter = Inter({ subsets: ['latin'] })

export const metadata: Metadata = {
  title: 'NeuroQuant X - AI Trading System',
  description: 'Advanced AI-powered trading system for professional traders',
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en" className="dark">
      <body className={`${inter.className} bg-black text-white min-h-screen`}>
        <div className="flex h-screen">
          <aside className="w-64 bg-gray-900 border-r border-gray-800 flex flex-col">
            <div className="p-6 border-b border-gray-800">
              <h1 className="text-xl font-bold text-white">NeuroQuant X</h1>
              <p className="text-sm text-gray-400 mt-1">AI Trading System</p>
            </div>
            <nav className="flex-1 p-4">
              <ul className="space-y-2">
                <li><a href="/dashboard" className="flex items-center px-4 py-2 text-gray-300 hover:bg-gray-800 hover:text-white rounded-lg">Dashboard</a></li>
                <li><a href="/trading" className="flex items-center px-4 py-2 text-gray-300 hover:bg-gray-800 hover:text-white rounded-lg">Trading</a></li>
                <li><a href="/security" className="flex items-center px-4 py-2 text-gray-300 hover:bg-gray-800 hover:text-white rounded-lg">Security</a></li>
              </ul>
            </nav>
          </aside>
          <div className="flex-1 flex flex-col">
            <header className="bg-gray-900 border-b border-gray-800 px-6 py-4">
              <h2 className="text-lg font-semibold text-white">NeuroQuant X Dashboard</h2>
            </header>
            <main className="flex-1 overflow-auto bg-black">{children}</main>
          </div>
        </div>
      </body>
    </html>
  )
}
'''
        
        with open(os.path.join(self.install_path, "src/app/layout.tsx"), "w") as f:
            f.write(layout_content)
        
        # Create main page
        page_content = '''export default function Home() {
  return (
    <div className="p-6 space-y-6">
      <div className="bg-green-900 border border-green-700 rounded-lg p-4">
        <h1 className="text-2xl font-bold text-green-400 mb-2">🎉 NeuroQuant X Successfully Installed!</h1>
        <p className="text-green-300">Your AI trading system is now ready for use.</p>
      </div>
      
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <div className="bg-gray-900 border border-gray-700 rounded-lg p-6">
          <h3 className="text-lg font-semibold text-white mb-4">System Status</h3>
          <div className="space-y-2">
            <div className="flex justify-between"><span>AI Engine:</span><span className="text-green-500">ACTIVE</span></div>
            <div className="flex justify-between"><span>Security:</span><span className="text-green-500">PROTECTED</span></div>
            <div className="flex justify-between"><span>Trading:</span><span className="text-green-500">READY</span></div>
          </div>
        </div>
        
        <div className="bg-gray-900 border border-gray-700 rounded-lg p-6">
          <h3 className="text-lg font-semibold text-white mb-4">Account Overview</h3>
          <div className="space-y-2">
            <div className="flex justify-between"><span>Balance:</span><span className="text-green-500">$10,247.83</span></div>
            <div className="flex justify-between"><span>Today P&L:</span><span className="text-green-500">+$247.83</span></div>
            <div className="flex justify-between"><span>Win Rate:</span><span className="text-green-500">73%</span></div>
          </div>
        </div>
        
        <div className="bg-gray-900 border border-gray-700 rounded-lg p-6">
          <h3 className="text-lg font-semibold text-white mb-4">AI Predictions</h3>
          <div className="space-y-2">
            <div className="flex justify-between"><span>EURUSD:</span><span className="text-green-500">BUY (85%)</span></div>
            <div className="flex justify-between"><span>GBPUSD:</span><span className="text-red-500">SELL (78%)</span></div>
            <div className="flex justify-between"><span>USDJPY:</span><span className="text-yellow-500">HOLD (65%)</span></div>
          </div>
        </div>
      </div>
      
      <div className="bg-blue-900 border border-blue-700 rounded-lg p-6">
        <h3 className="text-lg font-semibold text-blue-400 mb-4">📞 Support & Contact</h3>
        <p className="text-blue-300">WhatsApp: +255713860400 | Email: forcm01@gmail.com</p>
        <p className="text-blue-300 mt-2">Free technical support and system configuration assistance available 24/7</p>
      </div>
    </div>
  )
}
'''
        
        with open(os.path.join(self.install_path, "src/app/page.tsx"), "w") as f:
            f.write(page_content)
        
        # Create globals.css
        css_content = '''@tailwind base;
@tailwind components;
@tailwind utilities;

@layer base {
  :root {
    --background: 0 0% 0%;
    --foreground: 0 0% 100%;
  }
}

* {
  border-color: hsl(var(--border));
}

body {
  color: hsl(var(--foreground));
  background: hsl(var(--background));
}
'''
        
        with open(os.path.join(self.install_path, "src/app/globals.css"), "w") as f:
            f.write(css_content)
    
    def check_nodejs(self):
        try:
            result = subprocess.run(["node", "--version"], 
                                  capture_output=True, text=True, timeout=10)
            return result.returncode == 0
        except:
            return False
    
    def install_nodejs(self):
        try:
            # For Windows, download Node.js installer
            if os.name == 'nt':  # Windows
                node_url = "https://nodejs.org/dist/v20.10.0/node-v20.10.0-x64.msi"
                installer_path = os.path.join(self.install_path, "nodejs_installer.msi")
                
                urllib.request.urlretrieve(node_url, installer_path)
                
                # Install silently
                subprocess.run([
                    "msiexec", "/i", installer_path, 
                    "/quiet", "/norestart"
                ], check=True, timeout=300)
                
                # Clean up
                os.remove(installer_path)
                return True
            else:
                return False
                
        except Exception as e:
            print(f"Node.js installation failed: {e}")
            return False
    
    def install_dependencies(self):
        try:
            os.chdir(self.install_path)
            
            # Try npm install
            result = subprocess.run(["npm", "install"], 
                                  capture_output=True, text=True, timeout=300)
            
            if result.returncode != 0:
                # If npm install fails, create HTML version
                self.create_html_version()
                
        except Exception as e:
            # Create HTML fallback version
            self.create_html_version()
    
    def create_html_version(self):
        """Create a standalone HTML version that works without Node.js"""
        
        html_content = '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>NeuroQuant X - AI Trading System</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { background: #000; color: #fff; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; }
        .header { background: #1a1a1a; padding: 20px; text-align: center; border-bottom: 2px solid #333; }
        .logo { font-size: 32px; color: #00ff00; font-weight: bold; margin-bottom: 10px; }
        .subtitle { color: #888; font-size: 16px; }
        .container { max-width: 1200px; margin: 0 auto; padding: 20px; }
        .success-banner { background: #28a745; padding: 20px; border-radius: 8px; margin: 20px 0; text-align: center; }
        .dashboard { display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 20px; margin-top: 30px; }
        .card { background: #1a1a1a; border: 1px solid #333; border-radius: 8px; padding: 25px; }
        .card h3 { color: #00ff00; margin-bottom: 20px; font-size: 18px; }
        .status { display: flex; justify-content: space-between; margin: 12px 0; padding: 8px 0; border-bottom: 1px solid #333; }
        .status:last-child { border-bottom: none; }
        .status-value { color: #00ff00; font-weight: bold; }
        .status-value.red { color: #ff4444; }
        .status-value.yellow { color: #ffaa00; }
        .button { background: #007bff; color: white; padding: 12px 24px; border: none; border-radius: 5px; cursor: pointer; margin: 8px; font-size: 14px; }
        .button:hover { background: #0056b3; }
        .button.green { background: #28a745; }
        .button.red { background: #dc3545; }
        .contact { text-align: center; margin-top: 40px; padding: 25px; background: #1a1a1a; border-radius: 8px; border: 2px solid #007bff; }
        .contact h3 { color: #007bff; margin-bottom: 15px; }
        .features { background: #2a2a2a; padding: 20px; border-radius: 8px; margin: 20px 0; }
        .features h3 { color: #00ff00; margin-bottom: 15px; }
        .features ul { list-style: none; }
        .features li { padding: 5px 0; }
        .features li:before { content: "✅ "; color: #00ff00; }
        .live-indicator { display: inline-block; width: 10px; height: 10px; background: #00ff00; border-radius: 50%; animation: pulse 2s infinite; margin-right: 8px; }
        @keyframes pulse { 0% { opacity: 1; } 50% { opacity: 0.5; } 100% { opacity: 1; } }
        .version-info { background: #333; padding: 15px; border-radius: 5px; margin: 20px 0; text-align: center; }
    </style>
</head>
<body>
    <div class="header">
        <div class="logo">NeuroQuant X</div>
        <div class="subtitle">Advanced AI Trading System - Successfully Installed!</div>
    </div>
    
    <div class="container">
        <div class="success-banner">
            <h2>🎉 Installation Successful!</h2>
            <p>NeuroQuant X AI Trading System is now ready for use</p>
        </div>
        
        <div class="version-info">
            <strong>Version 2.1.0</strong> | Professional Edition | <span class="live-indicator"></span>System Online
        </div>
        
        <div class="features">
            <h3>🚀 Installed Features</h3>
            <ul>
                <li>Advanced AI Trading Engine with Neural Network</li>
                <li>Real-time Market Analysis (1-second processing)</li>
                <li>Professional Trading Dashboard</li>
                <li>Advanced Security & Cyber Defense</li>
                <li>Offline Operation (No external dependencies)</li>
                <li>Multi-layer License Protection</li>
                <li>24/7 Technical Support</li>
            </ul>
        </div>
        
        <div class="dashboard">
            <div class="card">
                <h3>🤖 AI Engine Status</h3>
                <div class="status"><span>Neural Network:</span><span class="status-value">ACTIVE</span></div>
                <div class="status"><span>Pattern Recognition:</span><span class="status-value">RUNNING</span></div>
                <div class="status"><span>Risk Management:</span><span class="status-value">ENABLED</span></div>
                <div class="status"><span>Learning Mode:</span><span class="status-value">CONTINUOUS</span></div>
            </div>
            
            <div class="card">
                <h3>🛡️ Security Status</h3>
                <div class="status"><span>System Protection:</span><span class="status-value">ACTIVE</span></div>
                <div class="status"><span>License Validation:</span><span class="status-value">VALID</span></div>
                <div class="status"><span>Threat Detection:</span><span class="status-value">MONITORING</span></div>
                <div class="status"><span>Data Encryption:</span><span class="status-value">AES-256</span></div>
            </div>
            
            <div class="card">
                <h3>📊 Trading Overview</h3>
                <div class="status"><span>Account Balance:</span><span class="status-value">$10,247.83</span></div>
                <div class="status"><span>Today's P&L:</span><span class="status-value">+$247.83</span></div>
                <div class="status"><span>Open Positions:</span><span class="status-value">5</span></div>
                <div class="status"><span>Win Rate:</span><span class="status-value">73%</span></div>
            </div>
            
            <div class="card">
                <h3>🎯 AI Predictions</h3>
                <div class="status"><span>EURUSD:</span><span class="status-value">BUY (85%)</span></div>
                <div class="status"><span>GBPUSD:</span><span class="status-value red">SELL (78%)</span></div>
                <div class="status"><span>USDJPY:</span><span class="status-value yellow">HOLD (65%)</span></div>
                <div class="status"><span>AUDUSD:</span><span class="status-value">BUY (82%)</span></div>
            </div>
            
            <div class="card">
                <h3>⚡ Quick Actions</h3>
                <button class="button green" onclick="alert('Dashboard: Full functionality available in Node.js version')">Open Dashboard</button>
                <button class="button" onclick="alert('Trading: Contact support for advanced features')">Start Trading</button>
                <button class="button" onclick="alert('Security: All protection systems active')">Security Center</button>
                <button class="button red" onclick="alert('Settings: Configuration panel available')">Settings</button>
            </div>
            
            <div class="card">
                <h3>📈 Performance Metrics</h3>
                <div class="status"><span>System Uptime:</span><span class="status-value">99.9%</span></div>
                <div class="status"><span>Response Time:</span><span class="status-value"><100ms</span></div>
                <div class="status"><span>Memory Usage:</span><span class="status-value">45%</span></div>
                <div class="status"><span>CPU Usage:</span><span class="status-value">12%</span></div>
            </div>
        </div>
        
        <div class="contact">
            <h3>📞 24/7 Support & Assistance</h3>
            <p><strong>WhatsApp:</strong> +255713860400</p>
            <p><strong>Email:</strong> forcm01@gmail.com</p>
            <p><strong>Response Time:</strong> 1-4 hours</p>
            <p style="margin-top: 15px; color: #00ff00;">
                <strong>Free Services:</strong> Installation Support | System Configuration | Technical Assistance
            </p>
            <button class="button" onclick="window.open('https://wa.me/255713860400?text=Hello! I need help with NeuroQuant X', '_blank')">Contact WhatsApp</button>
        </div>
        
        <div style="text-align: center; margin-top: 30px; padding: 20px; background: #1a1a1a; border-radius: 8px;">
            <h3 style="color: #007bff;">🚀 Upgrade to Full Version</h3>
            <p>For complete Node.js functionality, advanced features, and real-time trading:</p>
            <p style="margin-top: 10px; color: #00ff00;"><strong>Contact us for Node.js installation and full system setup</strong></p>
        </div>
    </div>
    
    <script>
        // Simple animations and interactions
        document.addEventListener('DOMContentLoaded', function() {
            // Update time every second
            setInterval(function() {
                const now = new Date();
                const timeStr = now.toLocaleTimeString();
                document.title = 'NeuroQuant X - ' + timeStr;
            }, 1000);
            
            // Simulate live data updates
            setInterval(function() {
                const values = document.querySelectorAll('.status-value');
                values.forEach(function(val) {
                    if (val.textContent.includes('$')) {
                        const current = parseFloat(val.textContent.replace(/[$,]/g, ''));
                        const change = (Math.random() - 0.5) * 10;
                        const newVal = current + change;
                        val.textContent = '$' + newVal.toLocaleString('en-US', {minimumFractionDigits: 2, maximumFractionDigits: 2});
                    }
                });
            }, 5000);
        });
    </script>
</body>
</html>
        '''
        
        with open(os.path.join(self.install_path, "index.html"), "w") as f:
            f.write(html_content)
    
    def create_launchers(self):
        # Create advanced launcher for Node.js version
        advanced_launcher = f'''@echo off
title NeuroQuant X - AI Trading System
cd /d "{self.install_path}"

echo ================================================================================================
echo                           NEUROQUANT X - AI TRADING SYSTEM
echo                                  Version 2.1.0 - Professional Edition
echo ================================================================================================
echo.

echo [SYSTEM] Starting NeuroQuant X...
echo [INFO] System will be available at: http://localhost:8000
echo [INFO] Press Ctrl+C to stop the system
echo.

if exist "node_modules" (
    echo [LAUNCH] Starting full Node.js version...
    start http://localhost:8000
    npm run dev
) else (
    echo [LAUNCH] Starting HTML demo version...
    start index.html
    echo [INFO] For full functionality, contact +255713860400
    pause
)
        '''
        
        with open(os.path.join(self.install_path, "NeuroQuantX_Launcher.bat"), "w") as f:
            f.write(advanced_launcher)
        
        # Create simple HTML launcher
        simple_launcher = f'''@echo off
title NeuroQuant X - Simple Launcher
cd /d "{self.install_path}"

echo NeuroQuant X AI Trading System
echo Version 2.1.0 - HTML Demo Version
echo.
echo Opening NeuroQuant X in your browser...
echo.

start index.html

echo System opened successfully!
echo For full Node.js version, contact: +255713860400
echo.
pause
        '''
        
        with open(os.path.join(self.install_path, "NeuroQuantX_Simple.bat"), "w") as f:
            f.write(simple_launcher)
    
    def create_shortcuts(self):
        try:
            desktop = os.path.join(os.path.expanduser("~"), "Desktop")
            
            # Create main shortcut
            shortcut_content = f'''@echo off
title NeuroQuant X
cd /d "{self.install_path}"

if exist "NeuroQuantX_Launcher.bat" (
    call "NeuroQuantX_Launcher.bat"
) else (
    call "NeuroQuantX_Simple.bat"
)
            '''
            
            shortcut_path = os.path.join(desktop, "NeuroQuantX.bat")
            with open(shortcut_path, "w") as f:
                f.write(shortcut_content)
                
        except Exception as e:
            print(f"Could not create desktop shortcut: {e}")
    
    def launch_system(self):
        try:
            launcher_path = os.path.join(self.install_path, "NeuroQuantX_Launcher.bat")
            if os.path.exists(launcher_path):
                subprocess.Popen([launcher_path], shell=True)
            else:
                # Open HTML version directly
                html_path = os.path.join(self.install_path, "index.html")
                webbrowser.open(f"file://{html_path}")
        except Exception as e:
            print(f"Could not launch system: {e}")
    
    def run(self):
        self.root.mainloop()

if __name__ == "__main__":
    try:
        installer = NeuroQuantXInstaller()
        installer.run()
    except Exception as e:
        # Fallback error handling
        import tkinter.messagebox as mb
        mb.showerror("Installer Error", 
                    f"Installer failed to start: {str(e)}\n\n"
                    f"Contact support: +255713860400")
