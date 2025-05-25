import React, { useEffect, useRef } from 'react';

interface ParticleProps {
  x: number;
  y: number;
  vx: number;
  vy: number;
  size: number;
  opacity: number;
  color: string;
  direction: 'diagonal' | 'vertical' | 'horizontal' | 'circular' | 'random';
  angle?: number;
  radius?: number;
  centerX?: number;
  centerY?: number;
}

const BackgroundParticles: React.FC = () => {
  const canvasRef = useRef<HTMLCanvasElement>(null);

  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;

    const ctx = canvas.getContext('2d');
    if (!ctx) return;

    let animationId: number;

    // Set canvas size
    const resizeCanvas = (): void => {
      if (!canvas) return;
      canvas.width = window.innerWidth;
      canvas.height = window.innerHeight;
    };
    
    resizeCanvas();
    window.addEventListener('resize', resizeCanvas);

    // Particle class
    class Particle implements ParticleProps {
      x: number;
      y: number;
      vx: number = 0;
      vy: number = 0;
      size: number;
      opacity: number;
      color: string;
      direction: 'diagonal' | 'vertical' | 'horizontal' | 'circular' | 'random';
      angle?: number;
      radius?: number;
      centerX?: number;
      centerY?: number;
      time: number;

      constructor(direction: ParticleProps['direction']) {
        // Initialize all properties with default values first
        this.vx = 0;
        this.vy = 0;
        this.size = Math.random() * 5 + 2;
        this.opacity = Math.random() * 0.4 + 0.2;
        this.time = Math.random() * Math.PI * 2;
        this.direction = direction;
        
        if (!canvas) {
          // Fallback values if canvas is not available
          this.x = 0;
          this.y = 0;
        } else {
          this.x = Math.random() * canvas.width;
          this.y = Math.random() * canvas.height;
        }
        
        // Color variations
        const colors = ['#9B59B6', '#3498DB', '#E74C3C', '#2ECC71', '#F39C12', '#1ABC9C'];
        this.color = colors[Math.floor(Math.random() * colors.length)];

        this.initializeMovement();
      }

      initializeMovement(): void {
        if (!canvas) return;
        
        const speed = Math.random() * 1.5 + 0.5;
        
        switch (this.direction) {
          case 'diagonal':
            // Diagonal movement (4 directions)
            const diagonalDirections = [
              { vx: speed, vy: speed },     // bottom-right
              { vx: -speed, vy: speed },    // bottom-left
              { vx: speed, vy: -speed },    // top-right
              { vx: -speed, vy: -speed }    // top-left
            ];
            const diagonal = diagonalDirections[Math.floor(Math.random() * 4)];
            this.vx = diagonal.vx;
            this.vy = diagonal.vy;
            break;

          case 'vertical':
            // Pure vertical movement
            this.vx = 0;
            this.vy = Math.random() > 0.5 ? speed : -speed;
            break;

          case 'horizontal':
            // Pure horizontal movement
            this.vx = Math.random() > 0.5 ? speed : -speed;
            this.vy = 0;
            break;

          case 'circular':
            // Circular movement
            this.centerX = this.x;
            this.centerY = this.y;
            this.radius = Math.random() * 50 + 30;
            this.angle = Math.random() * Math.PI * 2;
            this.vx = speed * 0.02; // Angular velocity
            this.vy = 0;
            break;

          case 'random':
          default:
            // Random movement
            this.vx = (Math.random() - 0.5) * speed * 2;
            this.vy = (Math.random() - 0.5) * speed * 2;
            break;
        }
      }

      update(): void {
        if (!canvas) return;
        
        this.time += 0.02;

        switch (this.direction) {
          case 'circular':
            if (this.centerX !== undefined && this.centerY !== undefined && this.radius !== undefined && this.angle !== undefined) {
              this.angle += this.vx;
              this.x = this.centerX + Math.cos(this.angle) * this.radius;
              this.y = this.centerY + Math.sin(this.angle) * this.radius;
              
              // Slowly drift the center
              this.centerX += Math.sin(this.time) * 0.1;
              this.centerY += Math.cos(this.time) * 0.1;
              
              // Keep center in bounds
              if (this.centerX < -this.radius) this.centerX = canvas.width + this.radius;
              if (this.centerX > canvas.width + this.radius) this.centerX = -this.radius;
              if (this.centerY < -this.radius) this.centerY = canvas.height + this.radius;
              if (this.centerY > canvas.height + this.radius) this.centerY = -this.radius;
            }
            break;

          default:
            this.x += this.vx;
            this.y += this.vy;

            // Bounce off edges for non-circular particles
            if (this.x <= 0 || this.x >= canvas.width) {
              this.vx *= -1;
              this.x = Math.max(0, Math.min(canvas.width, this.x));
            }
            if (this.y <= 0 || this.y >= canvas.height) {
              this.vy *= -1;
              this.y = Math.max(0, Math.min(canvas.height, this.y));
            }
            break;
        }

        // Add slight opacity pulsing
        this.opacity = 0.3 + Math.sin(this.time) * 0.2;
      }

      draw(): void {
        if (!ctx) return;
        
        ctx.save();
        ctx.globalAlpha = Math.max(0.1, this.opacity);
        
        // Add glow effect
        ctx.shadowColor = this.color;
        ctx.shadowBlur = 10;
        
        ctx.fillStyle = this.color;
        ctx.beginPath();
        ctx.arc(this.x, this.y, this.size, 0, Math.PI * 2);
        ctx.fill();
        
        // Add inner bright core
        ctx.shadowBlur = 0;
        ctx.globalAlpha = Math.max(0.3, this.opacity);
        ctx.fillStyle = '#ffffff';
        ctx.beginPath();
        ctx.arc(this.x, this.y, this.size * 0.3, 0, Math.PI * 2);
        ctx.fill();
        
        ctx.restore();
      }
    }

    // Create particles with different movement patterns
    const particles: Particle[] = [];
    const directions: ParticleProps['direction'][] = ['diagonal', 'vertical', 'horizontal', 'circular', 'random'];
    
    // Create 15 particles of each type (75 total)
    directions.forEach(direction => {
      for (let i = 0; i < 15; i++) {
        particles.push(new Particle(direction));
      }
    });

    // Animation loop
    const animate = (): void => {
      if (!ctx || !canvas) return;
      
      // Clear canvas with gradient background
      const gradient = ctx.createLinearGradient(0, 0, 0, canvas.height);
      gradient.addColorStop(0, '#0f0f1a');
      gradient.addColorStop(0.5, '#1a1a2e');
      gradient.addColorStop(1, '#16213e');
      
      ctx.fillStyle = gradient;
      ctx.fillRect(0, 0, canvas.width, canvas.height);

      // Draw connecting lines between nearby particles
      particles.forEach((particle, i) => {
        particles.slice(i + 1).forEach(otherParticle => {
          const dx = particle.x - otherParticle.x;
          const dy = particle.y - otherParticle.y;
          const distance = Math.sqrt(dx * dx + dy * dy);
          
          if (distance < 100) {
            ctx.save();
            ctx.globalAlpha = (100 - distance) / 100 * 0.1;
            ctx.strokeStyle = '#9B59B6';
            ctx.lineWidth = 1;
            ctx.beginPath();
            ctx.moveTo(particle.x, particle.y);
            ctx.lineTo(otherParticle.x, otherParticle.y);
            ctx.stroke();
            ctx.restore();
          }
        });
      });

      // Update and draw particles
      particles.forEach(particle => {
        particle.update();
        particle.draw();
      });

      animationId = requestAnimationFrame(animate);
    };

    animate();

    return () => {
      window.removeEventListener('resize', resizeCanvas);
      if (animationId) {
        cancelAnimationFrame(animationId);
      }
    };
  }, []);

  return (
    <canvas
      ref={canvasRef}
      className="fixed inset-0 pointer-events-none"
      style={{ 
        zIndex: 0,
        width: '100vw',
        height: '100vh',
        position: 'fixed',
        top: 0,
        left: 0,
        right: 0,
        bottom: 0
      }}
    />
  );
};

export default BackgroundParticles;