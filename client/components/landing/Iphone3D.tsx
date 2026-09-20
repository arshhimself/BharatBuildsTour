'use client';

import React, { useRef } from 'react';
import { motion, useMotionValue, useSpring, useTransform } from 'framer-motion';

type Iphone3DProps = {
  children: React.ReactNode;
  className?: string;
  rotateZ?: number;
  glowColor?: string;
};

export function Iphone3D({
  children,
  className = '',
  rotateZ = 0,
  glowColor = 'rgba(91, 92, 240, 0.18)',
}: Iphone3DProps) {
  const ref = useRef<HTMLDivElement>(null);

  const mouseX = useMotionValue(0);
  const mouseY = useMotionValue(0);

  const rotateY = useSpring(useTransform(mouseX, [-0.5, 0.5], [9, -9]), {
    stiffness: 180,
    damping: 24,
  });

  const rotateX = useSpring(useTransform(mouseY, [-0.5, 0.5], [-8, 8]), {
    stiffness: 180,
    damping: 24,
  });

  function handleMouseMove(e: React.MouseEvent<HTMLDivElement>) {
    if (!ref.current) return;
    const rect = ref.current.getBoundingClientRect();
    const x = (e.clientX - rect.left) / rect.width - 0.5;
    const y = (e.clientY - rect.top) / rect.height - 0.5;
    mouseX.set(x);
    mouseY.set(y);
  }

  function handleMouseLeave() {
    mouseX.set(0);
    mouseY.set(0);
  }

  return (
    <div
      ref={ref}
      className={`relative [perspective:1400px] select-none ${className}`}
      onMouseMove={handleMouseMove}
      onMouseLeave={handleMouseLeave}
    >
      <motion.div
        style={{
          rotateX,
          rotateY,
          rotateZ,
          transformStyle: 'preserve-3d',
        }}
        className="relative mx-auto aspect-[433/882] w-full max-w-[340px]"
        whileHover={{ scale: 1.02 }}
        transition={{ type: 'spring', stiffness: 200, damping: 22 }}
      >
        {/* Ambient Color Glow behind device */}
        <div
          className="absolute -inset-10 -z-10 rounded-[35%] blur-3xl pointer-events-none transition-opacity duration-500"
          style={{ background: `radial-gradient(circle, ${glowColor} 0%, transparent 70%)` }}
        />

        {/* Contact Shadow under phone */}
        <div className="absolute -bottom-10 left-1/2 h-14 w-[76%] -translate-x-1/2 rounded-full bg-slate-900/15 blur-2xl pointer-events-none" />

        {/* Outer Metallic iPhone Edge Frame */}
        <div className="relative h-full w-full rounded-[48px] bg-gradient-to-b from-slate-700 via-slate-950 to-slate-800 p-[6px] shadow-[0_30px_70px_rgba(17,24,39,0.22),0_10px_30px_rgba(17,24,39,0.12)] border border-slate-700/50">
          
          {/* Inner bezel */}
          <div className="relative h-full w-full overflow-hidden rounded-[42px] bg-black">
            
            {/* Dynamic Island / Speaker Notch */}
            <div className="absolute left-1/2 top-3 z-40 h-5 w-[28%] -translate-x-1/2 rounded-full bg-black shadow-inner flex items-center justify-between px-2">
              <div className="h-2.5 w-2.5 rounded-full bg-slate-900 border border-slate-800" />
              <div className="h-2 w-2 rounded-full bg-blue-950/60" />
            </div>

            {/* Subtle Glass Reflection Overlay */}
            <div className="pointer-events-none absolute inset-0 z-30 bg-gradient-to-tr from-transparent via-white/10 to-transparent opacity-80" />

            {/* Screen Content Container */}
            <div className="relative h-full w-full overflow-hidden bg-white text-slate-900">
              {children}
            </div>
          </div>
        </div>
      </motion.div>
    </div>
  );
}
