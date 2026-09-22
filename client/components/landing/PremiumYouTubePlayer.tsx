'use client';

import React from 'react';
import { PremiumVideoFrame, PremiumVideoFrameProps } from './PremiumVideoFrame';

export function PremiumYouTubePlayer(props: PremiumVideoFrameProps) {
  return <PremiumVideoFrame {...props} />;
}

export { PremiumVideoFrame };
