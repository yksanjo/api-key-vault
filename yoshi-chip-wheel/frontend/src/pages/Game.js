import React, { useState, useEffect } from 'react';
import { useAuth } from '../contexts/AuthContext';
import SpinningWheel from '../components/SpinningWheel';
import ChipPurchase from '../components/ChipPurchase';
import axios from 'axios';

const Game = ({ socket }) => {
  const { user, updateUserChips } = useAuth();
  const [players, setPlayers] = useState([
    // DEMO DATA: Add some fake players to show the game
    { userId: 'demo1', username: 'DemoPlayer1', chips: 1500 },
    { userId: 'demo2', username: 'DemoPlayer2', chips: 2200 },
    { userId: 'demo3', username: 'DemoPlayer3', chips: 800 }
  ]);
  const [isSpinning, setIsSpinning] = useState(false);
  const [winner, setWinner] = useState(null);
  const [gameMessage, setGameMessage] = useState('🎮 Demo Mode - Welcome to Yoshi Chip Wheel!');
  const [timeUntilSpin, setTimeUntilSpin] = useState(60);
  const [hasJoined, setHasJoined] = useState(true); // Auto-join in demo mode

  useEffect(() => {
    if (!socket) return;

    socket.on('gameUpdate', (data) => {
      setPlayers(data.players);
    });

    socket.on('gameResult', (data) => {
      setWinner(data.winner);
      setIsSpinning(false);
      setGameMessage(`🎉 ${data.winner} won ${data.totalPot} chips!`);
      
      // Update user chips if they were in the game
      if (data.players.find(p => p.userId === user.id)) {
        // Refresh user data
        fetchUserData();
      }
      
      setTimeout(() => {
        setWinner(null);
        setGameMessage('');
        setHasJoined(false);
      }, 5000);
    });

    socket.on('error', (error) => {
      setGameMessage(error);
    });

    return () => {
      socket.off('gameUpdate');
      socket.off('gameResult');
      socket.off('error');
    };
  }, [socket, user.id]);

  useEffect(() => {
    const timer = setInterval(() => {
      setTimeUntilSpin((prev) => {
        if (prev <= 1) {
          return 60;
        }
        return prev - 1;
      });
    }, 1000);

    return () => clearInterval(timer);
  }, []);

  const fetchUserData = async () => {
    try {
      const response = await axios.get('/api/game/state');
      updateUserChips(response.data.chips);
    } catch (error) {
      console.error('Failed to fetch user data:', error);
    }
  };

  const handleJoinGame = async () => {
    // DEMO MODE: Skip authentication checks
    try {
      // In demo mode, just simulate joining
      setHasJoined(true);
      setGameMessage('🎮 Demo Mode: Successfully joined the game!');
      
      // Add demo player to the list
      setPlayers(prev => [...prev, { 
        userId: 'demo-player', 
        username: 'DemoPlayer', 
        chips: 5000 
      }]);
    } catch (error) {
      setGameMessage('Demo mode: Game joined successfully!');
    }
  };

  const handleSpinWheel = () => {
    if (players.length === 0) return;
    
    setIsSpinning(true);
    setGameMessage('Spinning the wheel...');
    
    // Simulate wheel spin
    setTimeout(() => {
      const randomWinner = players[Math.floor(Math.random() * players.length)];
      setWinner(randomWinner);
      setIsSpinning(false);
      setGameMessage(`🎉 ${randomWinner.username} won ${players.length * 100} chips!`);
    }, 3000);
  };

  return (
    <div className="max-w-7xl mx-auto px-4 py-8">
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        {/* Main Game Area */}
        <div className="lg:col-span-2">
          <div className="bg-white rounded-lg shadow-lg p-8 text-center">
            <h1 className="text-4xl font-bold text-gray-800 mb-8">Yoshi Chip Wheel</h1>
            
            {/* Game Status */}
            <div className="mb-6">
              <div className="text-2xl font-bold text-yoshi-green mb-2">
                Next Spin in: {timeUntilSpin}s
              </div>
              <div className="text-lg text-gray-600">
                {players.length} players joined • Pot: {players.length * 100} chips (Demo Mode)
              </div>
            </div>

            {/* Spinning Wheel */}
            <div className="flex justify-center mb-8">
              <SpinningWheel
                players={players}
                isSpinning={isSpinning}
                winner={winner}
                onSpinComplete={handleSpinWheel}
              />
            </div>

            {/* Game Controls */}
            <div className="space-y-4">
              {!hasJoined && (
                <button
                  onClick={handleJoinGame}
                  className="bg-yoshi-green hover:bg-yoshi-dark text-white px-8 py-3 rounded-lg text-lg font-bold transition-colors"
                >
                  Join Next Spin (100 chips)
                </button>
              )}
              
              {hasJoined && (
                <div className="bg-green-100 text-green-800 px-6 py-3 rounded-lg">
                  ✓ You're in the game! Waiting for the wheel to spin...
                </div>
              )}
            </div>

            {/* Game Messages */}
            {gameMessage && (
              <div className="mt-6 p-4 bg-blue-100 text-blue-800 rounded-lg">
                {gameMessage}
              </div>
            )}
          </div>
        </div>

        {/* Sidebar */}
        <div className="space-y-6">
          {/* Player Info */}
          <div className="bg-white rounded-lg shadow-lg p-6">
            <h3 className="text-xl font-bold text-gray-800 mb-4">Your Stats (Demo Mode)</h3>
            <div className="space-y-3">
              <div className="flex justify-between">
                <span className="text-gray-600">Username:</span>
                <span className="font-semibold">DemoPlayer</span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-600">Chips:</span>
                <span className="font-bold text-yoshi-green text-lg">
                  5,000
                </span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-600">Status:</span>
                <span className="font-semibold text-green-600">
                  In Game
                </span>
              </div>
            </div>
          </div>

          {/* Chip Purchase */}
          <ChipPurchase />

          {/* Current Players */}
          <div className="bg-white rounded-lg shadow-lg p-6">
            <h3 className="text-xl font-bold text-gray-800 mb-4">Current Players</h3>
            {players.length === 0 ? (
              <p className="text-gray-500 text-center py-4">No players joined yet</p>
            ) : (
              <div className="space-y-2">
                {players.map((player, index) => (
                  <div key={player.userId} className="flex items-center justify-between p-2 bg-gray-50 rounded">
                    <span className="font-medium">{player.username}</span>
                    <span className="text-yoshi-green font-bold">{player.chips} chips</span>
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

export default Game;
