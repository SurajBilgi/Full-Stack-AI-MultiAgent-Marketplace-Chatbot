'use client'

import { useState, useEffect } from 'react'
import { Package, Star, CheckCircle, XCircle, Loader2 } from 'lucide-react'
import api from '@/lib/api'

interface Product {
  id: number
  name: string
  category: string
  brand: string
  price: number
  description: string
  in_stock: boolean
  warranty: string
  rating: number
  reviews_count: number
}

export default function ProductBrowser() {
  const [products, setProducts] = useState<Product[]>([])
  const [loading, setLoading] = useState(true)
  const [filter, setFilter] = useState<string>('all')

  useEffect(() => {
    loadProducts()
  }, [])

  const loadProducts = async () => {
    try {
      const response = await api.getProducts()
      setProducts(response.products)
    } catch (error) {
      console.error('Error loading products:', error)
    } finally {
      setLoading(false)
    }
  }

  const categories = ['all', ...Array.from(new Set(products.map((p) => p.category)))]
  const filteredProducts =
    filter === 'all' ? products : products.filter((p) => p.category === filter)

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <Loader2 className="h-8 w-8 animate-spin text-blue-600" />
      </div>
    )
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
        <h2 className="text-2xl font-bold text-gray-900 mb-2">Browse Products</h2>
        <p className="text-gray-600">Explore our full catalog of electronics</p>
      </div>

      {/* Category Filter */}
      <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-4">
        <div className="flex flex-wrap gap-2">
          {categories.map((category) => (
            <button
              key={category}
              onClick={() => setFilter(category)}
              className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors ${
                filter === category
                  ? 'bg-blue-600 text-white'
                  : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
              }`}
            >
              {category}
            </button>
          ))}
        </div>
      </div>

      {/* Products Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {filteredProducts.map((product) => (
          <div
            key={product.id}
            className="bg-white rounded-xl shadow-sm border border-gray-200 overflow-hidden hover:shadow-lg transition-shadow duration-200"
          >
            {/* Product Image Placeholder */}
            <div className="bg-gradient-to-br from-blue-50 to-purple-50 h-48 flex items-center justify-center">
              <Package className="h-16 w-16 text-gray-400" />
            </div>

            {/* Product Info */}
            <div className="p-4 space-y-3">
              <div>
                <div className="flex items-start justify-between mb-1">
                  <h3 className="font-semibold text-gray-900 text-sm line-clamp-2">
                    {product.name}
                  </h3>
                  {product.in_stock ? (
                    <CheckCircle className="h-5 w-5 text-green-500 flex-shrink-0 ml-2" />
                  ) : (
                    <XCircle className="h-5 w-5 text-red-500 flex-shrink-0 ml-2" />
                  )}
                </div>
                <p className="text-xs text-gray-500">{product.category}</p>
              </div>

              <p className="text-sm text-gray-600 line-clamp-2">{product.description}</p>

              {/* Rating */}
              <div className="flex items-center space-x-1">
                <Star className="h-4 w-4 text-yellow-400 fill-current" />
                <span className="text-sm font-medium text-gray-900">{product.rating}</span>
                <span className="text-xs text-gray-500">({product.reviews_count})</span>
              </div>

              {/* Price and Warranty */}
              <div className="flex items-end justify-between pt-2 border-t border-gray-100">
                <div>
                  <p className="text-2xl font-bold text-gray-900">
                    ${product.price.toFixed(2)}
                  </p>
                  <p className="text-xs text-gray-500">{product.warranty} warranty</p>
                </div>
                <button className="px-4 py-2 bg-blue-600 text-white text-sm font-medium rounded-lg hover:bg-blue-700 transition-colors">
                  Details
                </button>
              </div>
            </div>
          </div>
        ))}
      </div>

      {filteredProducts.length === 0 && (
        <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-12 text-center">
          <Package className="h-12 w-12 text-gray-400 mx-auto mb-4" />
          <p className="text-gray-600">No products found in this category</p>
        </div>
      )}
    </div>
  )
}
