"use client";
import React, { useRef, useState, useEffect } from "react";
import { motion, useInView, type MotionProps, type Transition } from "framer-motion";

type AnimationTarget = Exclude<MotionProps["initial"], boolean | string | undefined>;

interface SplitTextProps {
  text: string;
  style?: React.CSSProperties;
  delay?: number;
  duration?: number;
  ease?: Transition["ease"];
  splitType?: "chars" | "words";
  from?: AnimationTarget;
  to?: AnimationTarget;
  threshold?: number;
  rootMargin?: `${number}px`;
  textAlign?: "left" | "center" | "right";
  onLetterAnimationComplete?: () => void;
  showCallback?: boolean;
}

export default function SplitText({
  text,
  style = {},
  delay = 50,
  duration = 0.5,
  ease = "easeOut",
  splitType = "chars",
  from = { opacity: 0, y: 40 },
  to = { opacity: 1, y: 0 },
  threshold = 0.1,
  rootMargin = "0px",
  textAlign = "center",
  onLetterAnimationComplete,
  showCallback = false,
}: SplitTextProps) {
  const ref = useRef<HTMLDivElement>(null);
  const inView = useInView(ref, { once: true, margin: rootMargin, amount: threshold });
  const [complete, setComplete] = useState(false);

  const elements = splitType === "chars" ? text.split("") : text.split(" ");

  useEffect(() => {
    if (complete && showCallback && onLetterAnimationComplete) {
      onLetterAnimationComplete();
    }
  }, [complete, showCallback, onLetterAnimationComplete]);

  const justifyMap = {
    left: "flex-start",
    center: "center",
    right: "flex-end",
  };

  return (
    <div
      ref={ref}
      style={{
        display: "flex",
        flexWrap: "wrap",
        justifyContent: justifyMap[textAlign],
        ...style,
      }}
    >
      {elements.map((el, i) => (
        <motion.span
          key={i}
          style={{ display: "inline-block", whiteSpace: "pre" }}
          initial={from}
          animate={inView ? to : from}
          transition={{
            duration,
            ease,
            delay: delay / 1000 + i * 0.04,
          }}
          onAnimationComplete={() => {
            if (i === elements.length - 1) setComplete(true);
          }}
        >
          {el}
        </motion.span>
      ))}
    </div>
  );
}
