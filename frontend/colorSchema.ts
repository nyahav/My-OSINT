interface ColorSchema {
  background: string;
  primary: string;
  accent: string;
  text: string;
  danger: string;
  secondary: string;
}

const colors: Readonly<ColorSchema> = {
  background: '#0f0f1a',
  primary: '#9B59B6',
  accent: '#00FFFF',
  text: '#E5E7EB',
  danger: '#EF4444',
  secondary: '#6B7280',
};

export default colors;

// Use animated glows, neon borders, and subtle hover transitions.

// Pair fonts like Orbitron, Share Tech Mono, or Fira Code with your UI.

// Add terminal-style cards for scan results/logs.