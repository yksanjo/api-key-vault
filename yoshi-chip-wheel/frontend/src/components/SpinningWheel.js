import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';

const SpinningWheel = ({ players, isSpinning, winner, onSpinComplete }) => {
  const [rotation, setRotation] = useState(0);
  const [isAnimating, setIsAnimating] = useState(false);

  useEffect(() => {
    if (isSpinning && players.length > 0) {
      setIsAnimating(true);
      const spins = 5 + Math.random() * 5; // 5-10 full rotations
      const finalRotation = rotation + (spins * 360);
      
      setRotation(finalRotation);
      
      setTimeout(() => {
        setIsAnimating(false);
        if (onSpinComplete) onSpinComplete();
      }, 3000);
    }
  }, [isSpinning, players]);

  if (players.length === 0) {
    return (
      <div className="w-80 h-80 rounded-full border-8 border-gray-300 bg-gray-100 flex items-center justify-center">
        <div className="text-center">
          <div className="text-6xl mb-4">🎯</div>
          <p className="text-gray-500">No players joined yet</p>
          <p className="text-sm text-gray-400">Join the game to start spinning!</p>
        </div>
      </div>
    );
  }

  const segments = players.length;
  const angleStep = 360 / segments;

  return (
    <div className="relative">
      <motion.div
        className="w-80 h-80 rounded-full border-8 border-yoshi-green bg-white relative overflow-hidden"
        animate={{ rotate: rotation }}
        transition={{ duration: 3, ease: "easeOut" }}
      >
        {players.map((player, index) => {
          const angle = index * angleStep;
          const isWinner = winner && winner.userId === player.userId;
          
          return (
            <div
              key={player.userId}
              className={`absolute w-full h-full origin-center ${
                isWinner ? 'bg-yellow-400' : 'bg-yoshi-green'
              }`}
              style={{
                clipPath: `polygon(50% 50%, 50% 0%, ${50 + 50 * Math.cos((angle + angleStep) * Math.PI / 180)}% ${50 + 50 * Math.sin((angle + angleStep) * Math.PI / 180)}%, ${50 + 50 * Math.cos(angle * Math.PI / 180)}% ${50 + 50 * Math.sin(angle * Math.PI / 180)}%)`
              }}
            >
              <div
                className="absolute text-center text-white font-bold text-sm"
                style={{
                  transform: `rotate(${angle + angleStep / 2}deg)`,
                  top: '25%',
                  left: '50%',
                  transformOrigin: '0 0'
                }}
              >
                {player.username}
              </div>
            </div>
          );
        })}
      </motion.div>
      
      {/* Center pointer */}
      <div className="absolute top-1/2 left-1/2 transform -translate-x-1/2 -translate-y-1/2">
        <div className="w-0 h-0 border-l-[20px] border-r-[20px] border-b-[40px] border-l-transparent border-r-transparent border-b-red-500"></div>
      </div>
      
      {/* Spin button */}
      {!isSpinning && !isAnimating && (
        <motion.button
          className="absolute top-1/2 left-1/2 transform -translate-x-1/2 -translate-y-1/2 mt-20 bg-red-500 hover:bg-red-600 text-white px-6 py-3 rounded-full font-bold shadow-lg"
          whileHover={{ scale: 1.05 }}
          whileTap={{ scale: 0.95 }}
          onClick={() => onSpinComplete && onSpinComplete()}
        >
          SPIN WHEEL
        </motion.button>
      )}
      
      {/* Spinning indicator */}
      {isSpinning && (
        <div className="absolute top-1/2 left-1/2 transform -translate-x-1/2 -translate-y-1/2 mt-20">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-white"></div>
        </div>
      )}
    </div>
  );
};

export default SpinningWheel;
