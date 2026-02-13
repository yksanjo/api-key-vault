const express = require('express');
const User = require('../models/User');
const router = express.Router();

// Get leaderboard
router.get('/', async (req, res) => {
  try {
    const leaderboard = await User.find({})
      .select('username chips totalWinnings gamesPlayed gamesWon')
      .sort({ chips: -1 })
      .limit(100);

    res.json(leaderboard);
  } catch (error) {
    res.status(500).json({ message: 'Server error' });
  }
});

// Get user stats
router.get('/user/:userId', async (req, res) => {
  try {
    const user = await User.findById(req.params.userId)
      .select('username chips totalWinnings gamesPlayed gamesWon');

    if (!user) {
      return res.status(404).json({ message: 'User not found' });
    }

    res.json(user);
  } catch (error) {
    res.status(500).json({ message: 'Server error' });
  }
});

module.exports = router;
