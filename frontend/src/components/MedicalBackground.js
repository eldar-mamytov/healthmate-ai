import React, { useEffect, useRef } from "react";
import medicalBg from '../assets/medical-bg.png';

// Import all your pill images (make sure the path matches your folder structure)
const pillImages = [
  require("../assets/pills/pills1.png"),
  require("../assets/pills/pills2.png"),
  require("../assets/pills/pills3.png"),
  require("../assets/pills/pills4.png"),
  require("../assets/pills/pills5.png"),
  require("../assets/pills/pills6.png"),
  require("../assets/pills/pills7.png"),
  require("../assets/pills/pills8.png"),
  require("../assets/pills/pills9.png"),
  require("../assets/pills/pills10.png"),
  require("../assets/pills/pills11.png"),
  require("../assets/pills/pills12.png"),
  require("../assets/pills/pills13.png"),
  require("../assets/pills/pills14.png"),
];

function randomInt(min, max) {
  return Math.floor(Math.random() * (max - min + 1)) + min;
}

const MedicalBackground = ({ count = 36 }) => {
  const containerRef = useRef();

  useEffect(() => {
    const container = containerRef.current;
    let pills = [];

    for (let i = 0; i < count; i++) {
      const pill = document.createElement("img");
      pill.src = pillImages[randomInt(0, pillImages.length - 1)];
      pill.style.position = "absolute";
      pill.style.left = `${randomInt(0, 98)}vw`;
      pill.style.top = `-${randomInt(15, 30)}vh`;
      pill.style.transform = `rotate(${randomInt(-90, 90)}deg)`;
      pill.style.opacity = Math.random() * 0.5 + 0.45;
      pill.style.pointerEvents = "none";
      pill.style.zIndex = 0;
      const size = randomInt(28, 110); // 28px up to 110px wide
      pill.style.width = `${size}px`;
      pill.style.height = "auto";
      pill.style.filter = size > 70 ? "blur(0.5px)" : "";
      // Animate with different durations/delays/directions
      const duration = randomInt(8, 18);
      pill.style.animation = `fall-medical ${duration}s linear ${randomInt(0, 12)}s infinite,
                        spin-medical ${randomInt(3, 9)}s linear infinite`;
      container.appendChild(pill);
      pills.push(pill);
    }
    return () => {
      pills.forEach((pill) => pill.remove());
    };
  }, [count]);

  return (
    <>
      <style>
        {`
          .medical-bg-image {
            position: fixed;
            inset: 0;
            z-index: -2;
            background: url(${medicalBg}) center center / cover no-repeat;
            pointer-events: none;
          }
          @keyframes fall-medical {
            to {
              transform: translateY(110vh) rotate(360deg);
            }
          }
          @keyframes spin-medical {
            to {
              filter: hue-rotate(360deg);
            }
          }
          .medical-bg-anim {
            position: fixed;
            inset: 0;
            z-index: -1;
            pointer-events: none;
            overflow: hidden;
          }
        `}
      </style>
      <div className="medical-bg-image"></div>
      <div ref={containerRef} className="medical-bg-anim"></div>
    </>
  );
};

export default MedicalBackground;