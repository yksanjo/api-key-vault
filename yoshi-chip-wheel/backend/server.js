const express = require('express');
const mongoose = require('mongoose');
const cors = require('cors');
const http = require('http');
const socketIo = require('socket.io');
const cron = require('node-cron');
const bcrypt = require('bcryptjs');
const jwt = require('jsonwebtoken');
// const stripe = require('stripe')(process.env.STRIPE_SECRET_KEY); // Commented out for demo

require('dotenv').config();

const app = express();
const server = http.createServer(app);
const io = socketIo(server, {
  cors: {
    origin: process.env.FRONTEND_URL || "http://localhost:3000",
    methods: ["GET", "POST"]
  }
});

// Middleware
app.use(cors());
app.use(express.json());

// MongoDB Connection
mongoose.connect(process.env.MONGODB_URI || 'mongodb://localhost:27017/yoshi-chip-wheel', {
  useNewUrlParser: true,
  useUnifiedTopology: true,
});

const db = mongoose.connection;
db.on('error', console.error.bind(console, 'MongoDB connection error:'));
db.once('open', () => {
  console.log('Connected to MongoDB');
});

// Models
const User = require('./models/User');
const GameRound = require('./models/GameRound');
const Payment = require('./models/Payment');

// Game state
let currentRound = {
  players: [],
  isActive: false,
  startTime: null,
  endTime: null
};

// Socket.IO connection handling
io.on('connection', (socket) => {
  console.log('User connected:', socket.id);

  socket.on('joinGame', async (data) => {
    try {
      const { userId, chips } = data;
      if (chips < 100) {
        socket.emit('error', 'Not enough chips to join!');
        return;
      }

      if (currentRound.players.find(p => p.userId === userId)) {
        socket.emit('error', 'Already joined this round!');
        return;
      }

      currentRound.players.push({
        userId,
        chips,
        socketId: socket.id
      });

      socket.emit('joinedGame', { message: 'Successfully joined the game!' });
      io.emit('gameUpdate', { players: currentRound.players });
    } catch (error) {
      socket.emit('error', 'Failed to join game');
    }
  });

  socket.on('disconnect', () => {
    console.log('User disconnected:', socket.id);
    currentRound.players = currentRound.players.filter(p => p.socketId !== socket.id);
    io.emit('gameUpdate', { players: currentRound.players });
  });
});

// Game round logic - runs every minute
cron.schedule('* * * * *', async () => {
  if (currentRound.players.length > 0) {
    await runGameRound();
  }
});

async function runGameRound() {
  try {
    console.log('Running game round...');
    
    const winnerIndex = Math.floor(Math.random() * currentRound.players.length);
    const winner = currentRound.players[winnerIndex];
    const totalPot = currentRound.players.length * 100;

    await User.findByIdAndUpdate(winner.userId, {
      $inc: { chips: totalPot }
    });

    for (const player of currentRound.players) {
      await User.findByIdAndUpdate(player.userId, {
        $inc: { chips: -100 }
      });
    }

    const gameRound = new GameRound({
      players: currentRound.players.map(p => p.userId),
      winner: winner.userId,
      totalPot,
      timestamp: new Date()
    });
    await gameRound.save();

    io.emit('gameResult', {
      winner: winner.userId,
      totalPot,
      players: currentRound.players
    });

    currentRound = {
      players: [],
      isActive: false,
      startTime: null,
      endTime: null
    };

    io.emit('gameUpdate', { players: currentRound.players });

  } catch (error) {
    console.error('Error running game round:', error);
  }
}

// Routes
app.use('/api/auth', require('./routes/auth'));
app.use('/api/game', require('./routes/game'));
app.use('/api/payments', require('./routes/payments'));
app.use('/api/leaderboard', require('./routes/leaderboard'));

const PORT = 5001; // Hardcoded for demo
server.listen(PORT, () => {
  console.log(`Server running on port ${PORT}`);
});
