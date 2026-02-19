'use client'

import { useState } from 'react'
import { MessageSquareWarning, CheckCircle, AlertCircle, Loader2 } from 'lucide-react'
import api from '@/lib/api'

export default function ComplaintForm() {
  const [orderId, setOrderId] = useState('')
  const [issue, setIssue] = useState('')
  const [description, setDescription] = useState('')
  const [loading, setLoading] = useState(false)
  const [success, setSuccess] = useState(false)
  const [error, setError] = useState('')
  const [complaintId, setComplaintId] = useState('')

  const issueTypes = [
    'Product defect',
    'Damaged in shipping',
    'Wrong item received',
    'Missing parts',
    'Not as described',
    'Quality issue',
    'Other',
  ]

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()

    if (!orderId.trim() || !issue || !description.trim()) {
      setError('Please fill in all fields')
      return
    }

    setLoading(true)
    setError('')
    setSuccess(false)

    try {
      const response = await api.createComplaint(orderId.trim(), issue, description)
      setComplaintId(response.complaint_id)
      setSuccess(true)
      // Reset form
      setOrderId('')
      setIssue('')
      setDescription('')
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to submit complaint. Please try again.')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="max-w-2xl mx-auto space-y-6">
      {/* Header */}
      <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
        <div className="flex items-center space-x-3 mb-2">
          <MessageSquareWarning className="h-6 w-6 text-blue-600" />
          <h2 className="text-2xl font-bold text-gray-900">Submit a Complaint</h2>
        </div>
        <p className="text-gray-600">
          We're sorry you're experiencing an issue. Let us know and we'll make it right.
        </p>
      </div>

      {/* Success Message */}
      {success && (
        <div className="bg-green-50 border border-green-200 rounded-xl p-6">
          <div className="flex items-start space-x-3">
            <CheckCircle className="h-6 w-6 text-green-600 flex-shrink-0 mt-0.5" />
            <div>
              <h3 className="text-lg font-semibold text-green-900 mb-1">
                Complaint Submitted Successfully
              </h3>
              <p className="text-sm text-green-800 mb-2">
                Your complaint <strong>{complaintId}</strong> has been created. Our support team
                will contact you within 24 hours.
              </p>
              <button
                onClick={() => setSuccess(false)}
                className="text-sm text-green-700 underline hover:text-green-800"
              >
                Submit another complaint
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Error Message */}
      {error && (
        <div className="bg-red-50 border border-red-200 rounded-xl p-4">
          <div className="flex items-center space-x-2">
            <AlertCircle className="h-5 w-5 text-red-600" />
            <p className="text-sm text-red-800">{error}</p>
          </div>
        </div>
      )}

      {/* Form */}
      {!success && (
        <form onSubmit={handleSubmit} className="bg-white rounded-xl shadow-sm border border-gray-200 p-6 space-y-6">
          {/* Order ID */}
          <div>
            <label htmlFor="orderId" className="block text-sm font-medium text-gray-700 mb-2">
              Order ID <span className="text-red-500">*</span>
            </label>
            <input
              type="text"
              id="orderId"
              value={orderId}
              onChange={(e) => setOrderId(e.target.value.toUpperCase())}
              placeholder="ORD-1001"
              className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent text-sm"
              required
            />
            <p className="mt-1 text-xs text-gray-500">Enter your order ID (format: ORD-XXXX)</p>
          </div>

          {/* Issue Type */}
          <div>
            <label htmlFor="issue" className="block text-sm font-medium text-gray-700 mb-2">
              Issue Type <span className="text-red-500">*</span>
            </label>
            <select
              id="issue"
              value={issue}
              onChange={(e) => setIssue(e.target.value)}
              className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent text-sm"
              required
            >
              <option value="">Select an issue type</option>
              {issueTypes.map((type) => (
                <option key={type} value={type}>
                  {type}
                </option>
              ))}
            </select>
          </div>

          {/* Description */}
          <div>
            <label htmlFor="description" className="block text-sm font-medium text-gray-700 mb-2">
              Description <span className="text-red-500">*</span>
            </label>
            <textarea
              id="description"
              value={description}
              onChange={(e) => setDescription(e.target.value)}
              placeholder="Please describe the issue in detail..."
              rows={5}
              className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent resize-none text-sm"
              required
            />
            <p className="mt-1 text-xs text-gray-500">
              Include as much detail as possible to help us resolve your issue faster
            </p>
          </div>

          {/* Submit Button */}
          <button
            type="submit"
            disabled={loading}
            className="w-full bg-blue-600 text-white py-3 rounded-lg font-medium hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors flex items-center justify-center space-x-2"
          >
            {loading ? (
              <>
                <Loader2 className="h-5 w-5 animate-spin" />
                <span>Submitting...</span>
              </>
            ) : (
              <>
                <MessageSquareWarning className="h-5 w-5" />
                <span>Submit Complaint</span>
              </>
            )}
          </button>
        </form>
      )}

      {/* Info Box */}
      <div className="bg-blue-50 border border-blue-200 rounded-xl p-6">
        <h3 className="text-sm font-semibold text-blue-900 mb-2">What happens next?</h3>
        <ul className="text-sm text-blue-800 space-y-2">
          <li className="flex items-start space-x-2">
            <span className="text-blue-600">•</span>
            <span>Our support team will review your complaint within 2 hours</span>
          </li>
          <li className="flex items-start space-x-2">
            <span className="text-blue-600">•</span>
            <span>You'll receive an email confirmation with your complaint ID</span>
          </li>
          <li className="flex items-start space-x-2">
            <span className="text-blue-600">•</span>
            <span>We'll contact you within 24 hours to resolve the issue</span>
          </li>
          <li className="flex items-start space-x-2">
            <span className="text-blue-600">•</span>
            <span>Track your complaint status in your account dashboard</span>
          </li>
        </ul>
      </div>
    </div>
  )
}
