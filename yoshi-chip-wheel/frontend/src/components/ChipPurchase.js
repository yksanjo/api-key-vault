import React, { useState } from 'react';
import axios from 'axios';
import { useAuth } from '../contexts/AuthContext';

const ChipPurchase = () => {
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState('');
  const { updateUserChips } = useAuth();

  const handlePurchase = async (amount) => {
    setLoading(true);
    setMessage('');

    try {
      // Create payment intent
      const paymentResponse = await axios.post('/api/payments/create-payment-intent', {
        amount: amount * 100 // Convert to cents
      });

      // In a real app, you would integrate with Stripe Elements here
      // For demo purposes, we'll simulate a successful payment
      const { clientSecret } = paymentResponse.data;

      // Simulate payment confirmation
      const confirmResponse = await axios.post('/api/payments/confirm-payment', {
        paymentIntentId: clientSecret,
        amount: amount * 100
      });

      setMessage(`Successfully purchased ${confirmResponse.data.chipsAdded.toLocaleString()} chips!`);
      updateUserChips(confirmResponse.data.chips);

    } catch (error) {
      setMessage('Payment failed. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="bg-white rounded-lg shadow-lg p-6">
      <h3 className="text-xl font-bold text-gray-800 mb-4">Buy Yoshi Chips</h3>
      
      <div className="space-y-3">
        <div className="flex items-center justify-between p-3 border rounded-lg">
          <div>
            <span className="font-semibold">5,000 Yoshi Chips</span>
            <p className="text-sm text-gray-500">Perfect for getting started!</p>
          </div>
          <button
            onClick={() => handlePurchase(5)}
            disabled={loading}
            className="bg-yoshi-green hover:bg-yoshi-dark text-white px-4 py-2 rounded-lg disabled:opacity-50 transition-colors"
          >
            $5.00
          </button>
        </div>
        
        <div className="flex items-center justify-between p-3 border rounded-lg">
          <div>
            <span className="font-semibold">10,000 Yoshi Chips</span>
            <p className="text-sm text-gray-500">Great value!</p>
          </div>
          <button
            onClick={() => handlePurchase(10)}
            disabled={loading}
            className="bg-yoshi-green hover:bg-yoshi-dark text-white px-4 py-2 rounded-lg disabled:opacity-50 transition-colors"
          >
            $10.00
          </button>
        </div>
        
        <div className="flex items-center justify-between p-3 border rounded-lg">
          <div>
            <span className="font-semibold">25,000 Yoshi Chips</span>
            <p className="text-sm text-gray-500">Best value!</p>
          </div>
          <button
            onClick={() => handlePurchase(25)}
            disabled={loading}
            className="bg-yoshi-green hover:bg-yoshi-dark text-white px-4 py-2 rounded-lg disabled:opacity-50 transition-colors"
          >
            $25.00
          </button>
        </div>
      </div>
      
      {message && (
        <div className={`mt-4 p-3 rounded-lg ${
          message.includes('Successfully') ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'
        }`}>
          {message}
        </div>
      )}
      
      <p className="text-xs text-gray-500 mt-4 text-center">
        * Chips cannot be cashed out and are for game purposes only
      </p>
    </div>
  );
};

export default ChipPurchase;
