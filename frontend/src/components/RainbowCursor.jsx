import React, { useEffect, useRef } from "react";

export default function RainbowCursor() {
  const canvasRef = useRef(null);

  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;

    const ctx = canvas.getContext("2d");
    let width = window.innerWidth;
    let height = window.innerHeight;

    canvas.width = width;
    canvas.height = height;

    let particles = [];
    let mouse = { x: -100, y: -100 };

    const render = () => {
      ctx.clearRect(0, 0, width, height);
      
      for (let i = 0; i < particles.length; i++) {
        let p = particles[i];
        ctx.beginPath();
        ctx.arc(p.x, p.y, p.size, 0, Math.PI * 2);
        ctx.fillStyle = `hsla(${p.hue}, 100%, 65%, ${p.alpha})`;
        ctx.fill();
        
        p.x += p.vx;
        p.y += p.vy;
        p.alpha -= 0.025; 
        p.size *= 0.94; 
      }

      particles = particles.filter((p) => p.alpha > 0 && p.size > 0.1);

      requestAnimationFrame(render);
    };

    let frameId = requestAnimationFrame(render);
    let hueCounter = 0;

    const onMouseMove = (e) => {
      mouse.x = e.clientX;
      mouse.y = e.clientY;

      hueCounter += 6; 
      
      for (let i = 0; i < 3; i++) {
        particles.push({
          x: mouse.x,
          y: mouse.y,
          size: Math.random() * 6 + 4,
          vx: (Math.random() - 0.5) * 2.5,
          vy: (Math.random() - 0.5) * 2.5,
          hue: (hueCounter + Math.random() * 20) % 360,
          alpha: 1,
        });
      }
    };

    // Keep particles matching cursor position during scrolling if necessary, though fixed positioning usually handles it.
    
    const onResize = () => {
      width = window.innerWidth;
      height = window.innerHeight;
      canvas.width = width;
      canvas.height = height;
    };

    window.addEventListener("mousemove", onMouseMove);
    window.addEventListener("resize", onResize);

    return () => {
      window.removeEventListener("mousemove", onMouseMove);
      window.removeEventListener("resize", onResize);
      cancelAnimationFrame(frameId);
    };
  }, []);

  return (
    <canvas
      ref={canvasRef}
      className="pointer-events-none fixed inset-0 z-[100]"
    />
  );
}
