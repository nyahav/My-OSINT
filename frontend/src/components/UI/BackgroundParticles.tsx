// components/BackgroundParticles.tsx
import React from 'react';
import Particles from 'react-tsparticles';
import { loadFull } from 'tsparticles';

const BackgroundParticles = () => {
  const particlesInit = async (main: any) => {
    await loadFull(main);
  };

  return (
    <Particles
      id="tsparticles"
      init={particlesInit}
      options={{
        background: {
          color: '#0f0f1a',
        },
        fpsLimit: 60,
        particles: {
          number: { value: 60 },
          color: { value: '#9B59B6' },
          shape: { type: 'circle' },
          opacity: {
            value: 0.3,
          },
          size: {
            value: 6,
            random: true,
          },
          move: {
            direction: 'none',
            enable: true,
            speed: 0.6,
            random: true,
            outModes: {
              default: 'bounce',
            },
          },
        },
        detectRetina: true,
      }}
    />
  );
};

export default BackgroundParticles;
