const express = require('express');
const User = require('../models/User');
const router = express.Router();

// Middleware to verify JWT
const auth = (req, res, next) => {
  try {
    const token = req.header('Authorization').replace('Bearer ', '');
    const decoded = jwt.verify(token, process.env.JWT_SECRET || 'your-secret-key');
    req.userId = decoded.userId;
    next();
  } catch (error) {
    res.status(401).json({ message: 'Token is not valid' });
  }
};

// Get current game state
router.get('/state', auth, async (req, res) => {
  try {
    const user = await User.findById(req.userId);
    res.json({
      chips: user.chips,
      username: user.username
    });
  } catch (error) {
    res.status(500).json({ message: 'Server error' });
  }
});

// Join game round
router.post('/join', auth, async (req, res) => {
  try {
    const user = await User.findById(req.userId);
    
    if (user.chips < 100) {
      return res.status(400).json({ message: 'Not enough chips to join' });
    }

    // Deduct chips immediately
    user.chips -= 100;
    await user.save();

    res.json({ 
      message: 'Successfully joined the game!',
      chips: user.chips
    });
  } catch (error) {
    res.status(500).json({ message: 'Server error' });
  }
});

module.exports = router;
