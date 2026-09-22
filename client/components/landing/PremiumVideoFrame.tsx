'use client';

import React, { useState, useRef, useEffect } from 'react';
import { Volume2, VolumeX, Play, Pause, Maximize2 } from 'lucide-react';

export interface PremiumVideoFrameProps {
  source?: string; // MP4 file path (e.g., "/media/BizMateLaunchVideo.mp4") OR YouTube video ID (e.g., "fZdbSssVUp4")
  videoId?: string; // Backwards compatible prop for YouTube ID
  type?: 'mp4' | 'youtube';
  title: string;
  subtitle?: string;
  label?: string;
  isActive?: boolean;
  poster?: string;
}

export function PremiumVideoFrame({
  source,
  videoId,
  type,
  title,
  subtitle,
  label = 'BIZMATE PRODUCT',
  isActive = true,
  poster,
}: PremiumVideoFrameProps) {
  const containerRef = useRef<HTMLDivElement>(null);
  const iframeRef = useRef<HTMLIFrameElement>(null);
  const videoRef = useRef<HTMLVideoElement>(null);

  const mediaSource = source || videoId || '';

  // Auto-detect type if not explicitly provided
  const videoType = type || (mediaSource.endsWith('.mp4') || mediaSource.includes('/') ? 'mp4' : 'youtube');

  const [isMuted, setIsMuted] = useState(true);
  const isMutedRef = useRef(true);
  const [isPlaying, setIsPlaying] = useState(true);
  const [showControls, setShowControls] = useState(true);
  const hideControlsTimeout = useRef<NodeJS.Timeout | null>(null);

  // Send message to YouTube iframe API
  const sendYTCommand = (func: string, args: any[] = []) => {
    if (iframeRef.current && iframeRef.current.contentWindow) {
      iframeRef.current.contentWindow.postMessage(
        JSON.stringify({ event: 'command', func, args }),
        '*'
      );
    }
  };

  // Toggle Mute
  const toggleMute = (e: React.MouseEvent) => {
    e.stopPropagation();
    const nextMuteState = !isMuted;
    setIsMuted(nextMuteState);
    isMutedRef.current = nextMuteState;

    if (videoType === 'mp4') {
      if (videoRef.current) {
        videoRef.current.muted = nextMuteState;
      }
    } else {
      sendYTCommand(nextMuteState ? 'mute' : 'unMute');
    }
  };

  // Toggle Play / Pause
  const togglePlay = (e: React.MouseEvent) => {
    e.stopPropagation();
    const nextPlayState = !isPlaying;
    setIsPlaying(nextPlayState);

    if (videoType === 'mp4') {
      if (videoRef.current) {
        if (nextPlayState) {
          videoRef.current.play().catch(() => {});
        } else {
          videoRef.current.pause();
        }
      }
    } else {
      sendYTCommand(nextPlayState ? 'playVideo' : 'pauseVideo');
    }
  };

  // Fullscreen Toggle
  const toggleFullscreen = (e: React.MouseEvent) => {
    e.stopPropagation();
    if (containerRef.current) {
      if (document.fullscreenElement) {
        document.exitFullscreen().catch(() => {});
      } else {
        containerRef.current.requestFullscreen().catch(() => {});
      }
    }
  };

  // Handle pointer activity for auto-hiding controls
  const handleMouseMove = () => {
    setShowControls(true);
    if (hideControlsTimeout.current) {
      clearTimeout(hideControlsTimeout.current);
    }
    hideControlsTimeout.current = setTimeout(() => {
      setShowControls(false);
    }, 3000);
  };

  // On YouTube iframe load
  const handleIframeLoad = () => {
    if (isActive) {
      sendYTCommand(isMutedRef.current ? 'mute' : 'unMute');
      sendYTCommand('playVideo');
    }
  };

  // IntersectionObserver for pausing when out of view & resuming when in view
  useEffect(() => {
    if (!containerRef.current || !isActive) return;

    const observer = new IntersectionObserver(
      (entries) => {
        entries.forEach((entry) => {
          if (entry.isIntersecting) {
            if (videoType === 'mp4') {
              if (videoRef.current) {
                videoRef.current.muted = isMutedRef.current;
                videoRef.current.play().catch(() => {});
              }
            } else {
              sendYTCommand(isMutedRef.current ? 'mute' : 'unMute');
              sendYTCommand('playVideo');
            }
            setIsPlaying(true);
          } else {
            if (videoType === 'mp4') {
              if (videoRef.current) {
                videoRef.current.pause();
              }
            } else {
              sendYTCommand('pauseVideo');
            }
            setIsPlaying(false);
          }
        });
      },
      { threshold: 0.35 }
    );

    observer.observe(containerRef.current);

    return () => {
      observer.disconnect();
      if (hideControlsTimeout.current) clearTimeout(hideControlsTimeout.current);
    };
  }, [isActive, mediaSource, videoType]);

  return (
    <div
      ref={containerRef}
      onMouseMove={handleMouseMove}
      onMouseLeave={() => setShowControls(false)}
      className="group relative w-full overflow-hidden rounded-[28px] border border-white/75 bg-slate-950 shadow-[0_35px_80px_rgba(40,55,100,0.16)] transition-all duration-500"
    >
      {/* Soft Ambient Background Glow */}
      <div className="absolute -inset-4 bg-gradient-to-r from-indigo-500/10 via-purple-500/10 to-indigo-500/10 blur-3xl pointer-events-none -z-10" />

      {/* 16:9 Aspect Ratio Frame */}
      <div className="relative aspect-16/9 w-full bg-slate-950 overflow-hidden flex items-center justify-center">
        
        {/* Media Render: Native MP4 or YouTube Embed */}
        {videoType === 'mp4' ? (
          <video
            ref={videoRef}
            src={mediaSource}
            poster={poster}
            autoPlay
            muted
            loop
            playsInline
            preload="metadata"
            className="absolute inset-0 h-full w-full object-cover"
          />
        ) : (
          <iframe
            ref={iframeRef}
            src={`https://www.youtube-nocookie.com/embed/${mediaSource}?autoplay=1&mute=1&controls=0&enablejsapi=1&loop=1&playlist=${mediaSource}&playsinline=1&rel=0&modestbranding=1&title=0&byline=0&portrait=0`}
            title={title}
            allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture"
            onLoad={handleIframeLoad}
            className="absolute inset-0 h-full w-full border-0 pointer-events-none scale-[1.03]"
          />
        )}

        {/* Top Overlay Glass Badge (Category/Eyebrow) */}
        <div
          className={`absolute top-4 left-4 right-4 z-20 flex items-start justify-between transition-opacity duration-300 pointer-events-none ${
            showControls ? 'opacity-100' : 'opacity-0'
          }`}
        >
          <div className="flex items-center gap-2">
            <span className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full bg-slate-900/80 backdrop-blur-md border border-white/20 text-[10px] font-extrabold uppercase tracking-wider text-white shadow-lg">
              <span className="h-2 w-2 rounded-full bg-emerald-400 animate-pulse" />
              {label}
            </span>
          </div>
        </div>

        {/* Bottom Overlay Info & Custom Glass Controls */}
        <div
          className={`absolute bottom-0 inset-x-0 z-20 p-4 sm:p-6 bg-gradient-to-t from-slate-950/90 via-slate-950/40 to-transparent flex items-end justify-between transition-opacity duration-300 ${
            showControls ? 'opacity-100' : 'opacity-0'
          }`}
        >
          {/* Left Text (Hidden on mobile to preserve video-first priority) */}
          <div className="max-w-[70%] space-y-1 hidden sm:block">
            <h3 className="text-base sm:text-xl font-extrabold text-white tracking-tight drop-shadow-md">
              {title}
            </h3>
            {subtitle && (
              <p className="text-xs sm:text-sm text-slate-300 font-medium leading-relaxed drop-shadow-sm line-clamp-2">
                {subtitle}
              </p>
            )}
          </div>

          {/* Right Custom Glass Controls */}
          <div className="flex items-center gap-2">
            {/* Play/Pause Button */}
            <button
              onClick={togglePlay}
              aria-label={isPlaying ? 'Pause' : 'Play'}
              className="flex h-10 w-10 items-center justify-center rounded-2xl bg-white/15 backdrop-blur-md border border-white/25 text-white hover:bg-white/30 transition-all cursor-pointer shadow-lg active:scale-95"
            >
              {isPlaying ? <Pause className="h-4 w-4" /> : <Play className="h-4 w-4 fill-white ml-0.5" />}
            </button>

            {/* Mute/Unmute Button */}
            <button
              onClick={toggleMute}
              aria-label={isMuted ? 'Unmute' : 'Mute'}
              className="flex h-10 px-3.5 items-center gap-2 rounded-2xl bg-white/15 backdrop-blur-md border border-white/25 text-white hover:bg-white/30 transition-all cursor-pointer shadow-lg active:scale-95"
            >
              {isMuted ? (
                <>
                  <VolumeX className="h-4 w-4 text-amber-300" />
                  <span className="text-xs font-bold hidden sm:inline">Muted</span>
                </>
              ) : (
                <>
                  <Volume2 className="h-4 w-4 text-emerald-400" />
                  <span className="text-xs font-bold hidden sm:inline">Sound On</span>
                </>
              )}
            </button>

            {/* Fullscreen Button */}
            <button
              onClick={toggleFullscreen}
              aria-label="Fullscreen"
              className="flex h-10 w-10 items-center justify-center rounded-2xl bg-white/15 backdrop-blur-md border border-white/25 text-white hover:bg-white/30 transition-all cursor-pointer shadow-lg active:scale-95"
            >
              <Maximize2 className="h-4 w-4" />
            </button>
          </div>
        </div>

      </div>
    </div>
  );
}
