/**
 * API client for communicating with the backend.
 */

import axios, { AxiosInstance } from 'axios'

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'

class APIClient {
  private client: AxiosInstance

  constructor() {
    this.client = axios.create({
      baseURL: API_URL,
      headers: {
        'Content-Type': 'application/json',
      },
      timeout: 30000,
    })
  }

  // Chat endpoints
  async sendMessage(message: string, sessionId: string) {
    const response = await this.client.post('/api/chat', {
      message,
      session_id: sessionId,
    })
    return response.data
  }

  // Product endpoints
  async getProducts() {
    const response = await this.client.get('/api/products')
    return response.data
  }

  async getProduct(productId: number) {
    const response = await this.client.get(`/api/products/${productId}`)
    return response.data
  }

  async compareProducts(productIds: number[]) {
    const response = await this.client.get('/api/products/compare', {
      params: { ids: productIds.join(',') },
    })
    return response.data
  }

  // Order endpoints
  async getOrder(orderId: string) {
    const response = await this.client.get(`/api/orders/${orderId}`)
    return response.data
  }

  // Complaint endpoints
  async createComplaint(orderId: string, issue: string, description: string) {
    const response = await this.client.post('/api/complaints', {
      order_id: orderId,
      issue,
      description,
    })
    return response.data
  }

  // Refund endpoints
  async getRefundStatus(orderId: string) {
    const response = await this.client.get(`/api/refunds/${orderId}`)
    return response.data
  }

  // Delivery endpoints
  async getDeliveryStatus(orderId: string) {
    const response = await this.client.get(`/api/delivery/${orderId}`)
    return response.data
  }

  // Health check
  async healthCheck() {
    const response = await this.client.get('/health')
    return response.data
  }
}

export const api = new APIClient()
export default api
