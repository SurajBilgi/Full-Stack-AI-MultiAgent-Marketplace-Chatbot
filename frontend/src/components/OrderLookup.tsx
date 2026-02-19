'use client'

import { useState } from 'react'
import { Search, Package, Truck, CheckCircle, Clock, Loader2 } from 'lucide-react'
import api from '@/lib/api'

interface OrderItem {
  product_id: number
  product_name: string
  quantity: number
  price: number
}

interface Order {
  order_id: string
  customer_name: string
  customer_email: string
  items: OrderItem[]
  total: number
  status: string
  order_date: string
  expected_delivery?: string
  tracking_number?: string
}

export default function OrderLookup() {
  const [orderId, setOrderId] = useState('')
  const [order, setOrder] = useState<Order | null>(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')

  const handleLookup = async () => {
    if (!orderId.trim()) return

    setLoading(true)
    setError('')
    setOrder(null)

    try {
      const response = await api.getOrder(orderId.trim())
      setOrder(response)
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Order not found. Please check the order ID.')
    } finally {
      setLoading(false)
    }
  }

  const getStatusIcon = (status: string) => {
    switch (status.toLowerCase()) {
      case 'delivered':
        return <CheckCircle className="h-6 w-6 text-green-500" />
      case 'in_transit':
        return <Truck className="h-6 w-6 text-blue-500" />
      case 'processing':
        return <Clock className="h-6 w-6 text-yellow-500" />
      default:
        return <Package className="h-6 w-6 text-gray-500" />
    }
  }

  const getStatusColor = (status: string) => {
    switch (status.toLowerCase()) {
      case 'delivered':
        return 'bg-green-100 text-green-800'
      case 'in_transit':
        return 'bg-blue-100 text-blue-800'
      case 'processing':
        return 'bg-yellow-100 text-yellow-800'
      default:
        return 'bg-gray-100 text-gray-800'
    }
  }

  return (
    <div className="max-w-3xl mx-auto space-y-6">
      {/* Header */}
      <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
        <h2 className="text-2xl font-bold text-gray-900 mb-2">Track Your Order</h2>
        <p className="text-gray-600">Enter your order ID to view status and details</p>
      </div>

      {/* Search Box */}
      <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
        <div className="flex space-x-3">
          <div className="flex-1">
            <input
              type="text"
              value={orderId}
              onChange={(e) => setOrderId(e.target.value.toUpperCase())}
              onKeyPress={(e) => e.key === 'Enter' && handleLookup()}
              placeholder="Enter Order ID (e.g., ORD-1001)"
              className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent text-sm"
            />
          </div>
          <button
            onClick={handleLookup}
            disabled={!orderId.trim() || loading}
            className="px-6 py-3 bg-blue-600 text-white font-medium rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors flex items-center space-x-2"
          >
            {loading ? (
              <Loader2 className="h-5 w-5 animate-spin" />
            ) : (
              <Search className="h-5 w-5" />
            )}
            <span>Search</span>
          </button>
        </div>

        {/* Sample Order IDs */}
        <div className="mt-4 pt-4 border-t border-gray-200">
          <p className="text-xs text-gray-500 mb-2">Try these order IDs:</p>
          <div className="flex flex-wrap gap-2">
            {['ORD-1001', 'ORD-1002', 'ORD-1003', 'ORD-1004'].map((id) => (
              <button
                key={id}
                onClick={() => setOrderId(id)}
                className="text-xs px-3 py-1.5 rounded-full bg-gray-100 text-gray-700 hover:bg-gray-200 transition-colors"
              >
                {id}
              </button>
            ))}
          </div>
        </div>
      </div>

      {/* Error Message */}
      {error && (
        <div className="bg-red-50 border border-red-200 rounded-xl p-4">
          <p className="text-sm text-red-800">{error}</p>
        </div>
      )}

      {/* Order Details */}
      {order && (
        <div className="space-y-4">
          {/* Status Card */}
          <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
            <div className="flex items-center justify-between mb-4">
              <div className="flex items-center space-x-3">
                {getStatusIcon(order.status)}
                <div>
                  <h3 className="text-lg font-semibold text-gray-900">Order {order.order_id}</h3>
                  <p className="text-sm text-gray-600">Placed on {order.order_date}</p>
                </div>
              </div>
              <span
                className={`px-3 py-1 rounded-full text-sm font-medium ${getStatusColor(
                  order.status
                )}`}
              >
                {order.status.replace('_', ' ').toUpperCase()}
              </span>
            </div>

            {order.expected_delivery && (
              <div className="bg-blue-50 rounded-lg p-4 mb-4">
                <p className="text-sm text-blue-900">
                  <strong>Expected Delivery:</strong> {order.expected_delivery}
                </p>
              </div>
            )}

            {order.tracking_number && (
              <div className="bg-gray-50 rounded-lg p-4">
                <p className="text-sm text-gray-900">
                  <strong>Tracking Number:</strong> {order.tracking_number}
                </p>
              </div>
            )}
          </div>

          {/* Customer Info */}
          <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
            <h4 className="font-semibold text-gray-900 mb-3">Customer Information</h4>
            <div className="space-y-2 text-sm">
              <p className="text-gray-600">
                <strong>Name:</strong> {order.customer_name}
              </p>
              <p className="text-gray-600">
                <strong>Email:</strong> {order.customer_email}
              </p>
            </div>
          </div>

          {/* Items */}
          <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
            <h4 className="font-semibold text-gray-900 mb-4">Order Items</h4>
            <div className="space-y-3">
              {order.items.map((item, index) => (
                <div
                  key={index}
                  className="flex items-center justify-between py-3 border-b border-gray-100 last:border-0"
                >
                  <div className="flex-1">
                    <p className="font-medium text-gray-900">{item.product_name}</p>
                    <p className="text-sm text-gray-500">Quantity: {item.quantity}</p>
                  </div>
                  <p className="font-semibold text-gray-900">${item.price.toFixed(2)}</p>
                </div>
              ))}
            </div>
            <div className="mt-4 pt-4 border-t border-gray-200 flex items-center justify-between">
              <p className="text-lg font-semibold text-gray-900">Total</p>
              <p className="text-2xl font-bold text-blue-600">${order.total.toFixed(2)}</p>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
