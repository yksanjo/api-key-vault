const express = require('express');
// const stripe = require('stripe')(process.env.STRIPE_SECRET_KEY); // Commented out for demo
const jwt = require('jsonwebtoken');
const User = require('../models/User');
const Payment = require('../models/Payment');
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

// Create payment intent (Demo mode - Stripe disabled)
router.post('/create-payment-intent', auth, async (req, res) => {
  try {
    // Demo mode - return fake payment intent
    res.json({
      clientSecret: 'demo_payment_intent_secret',
      message: 'Demo mode - Stripe disabled'
    });
  } catch (error) {
    res.status(500).json({ message: 'Demo mode error' });
  }
});

// Confirm payment and add chips (Demo mode - Stripe disabled)
router.post('/confirm-payment', auth, async (req, res) => {
  try {
    const { amount } = req.body;
    
    // Demo mode - skip Stripe verification
    // Calculate chips (5000 chips per $5)
    const chips = (amount / 100) * 1000; // Convert cents to dollars, then multiply by 1000

    // Update user chips (demo mode)
    const user = await User.findById(req.userId);
    if (user) {
      user.chips += chips;
      await user.save();
    }

    res.json({
      message: 'Demo mode - Payment confirmed!',
      chips: user ? user.chips : 5000,
      chipsAdded: chips
    });
  } catch (error) {
    res.status(500).json({ message: 'Demo mode error' });
  }
});

module.exports = router;
