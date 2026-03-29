"use client";

import { useEffect, useRef, useState } from "react";

/**
 * Eases out using an exponential curve.
 * Returns 0 for t=0 and 1 for t=1.
 */
function easeOutExpo(t: number): number {
	return t >= 1 ? 1 : 1 - 2 ** (-10 * t);
}

/**
 * Smoothly animates a number from 0 to the target value using
 * requestAnimationFrame at ~60fps with an ease-out curve.
 *
 * @param target  - The final value to animate towards
 * @param duration - Animation duration in milliseconds (default 1000)
 * @returns The current animated value (number)
 *
 * @example
 * ```tsx
 * const revenue = useAnimatedCounter(48200, 1200);
 * <span>{revenue.toLocaleString()}</span>
 * ```
 */
export function useAnimatedCounter(
	target: number,
	duration: number = 1000,
): number {
	const [current, setCurrent] = useState(0);
	const rafRef = useRef<number | null>(null);
	const startTimeRef = useRef<number | null>(null);
	const previousTargetRef = useRef(0);

	useEffect(() => {
		// Animate from whatever value we were at to the new target
		const startValue = previousTargetRef.current;
		const delta = target - startValue;

		// Skip animation for zero delta
		if (delta === 0) {
			setCurrent(target);
			return;
		}

		startTimeRef.current = null;

		function tick(timestamp: number) {
			if (startTimeRef.current === null) {
				startTimeRef.current = timestamp;
			}

			const elapsed = timestamp - startTimeRef.current;
			const progress = Math.min(elapsed / duration, 1);
			const easedProgress = easeOutExpo(progress);

			const value = startValue + delta * easedProgress;
			setCurrent(value);

			if (progress < 1) {
				rafRef.current = requestAnimationFrame(tick);
			} else {
				// Ensure we land exactly on target
				setCurrent(target);
				previousTargetRef.current = target;
			}
		}

		rafRef.current = requestAnimationFrame(tick);

		return () => {
			if (rafRef.current !== null) {
				cancelAnimationFrame(rafRef.current);
			}
		};
	}, [target, duration]);

	return current;
}
