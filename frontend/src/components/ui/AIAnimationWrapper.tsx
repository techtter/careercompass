"use client";

import dynamic from 'next/dynamic';

const AIBackgroundAnimation = dynamic(
  () => import('@/components/ui/AIBackgroundAnimation'),
  { ssr: false }
);

export default function AIAnimationWrapper() {
  return <AIBackgroundAnimation />;
} 