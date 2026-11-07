export interface SM2Result {
  interval: number;
  ease: number;
  reps: number;
}

export function sm2(
  interval: number,
  ease: number,
  reps: number,
  quality: number,
): SM2Result {
  let nextInterval = Math.max(1, interval || 1);
  let nextEase = Number(ease || 2.5);
  let nextReps = Math.max(0, reps || 0);

  if (quality < 3) {
    nextReps = 0;
    nextInterval = 1;
    nextEase = Math.max(1.3, nextEase - 0.2);
  } else {
    if (nextReps === 0) nextInterval = 1;
    else if (nextReps === 1) nextInterval = 3;
    else nextInterval = Math.max(1, Math.round(nextInterval * nextEase));
    nextReps += 1;
    nextEase = Math.min(2.8, nextEase + 0.1);
  }

  return {
    interval: nextInterval,
    ease: Math.round(nextEase * 100) / 100,
    reps: nextReps,
  };
}
