import React from 'react';
import { render, screen, waitFor } from '@testing-library/react';
import { Provider } from 'react-redux';
import { configureStore } from '@reduxjs/toolkit';
import axios from 'axios';
import ProductList from '../components/ProductList';
import productsSlice from '../store/productsSlice';

jest.mock('axios');
const mockedAxios = axios;

const mockStore = configureStore({
  reducer: {
    products: productsSlice,
  },
});

describe('ProductList', () => {
  test('renders loading state initially', () => {
    render(
      <Provider store={mockStore}>
        <ProductList />
      </Provider>
    );
    
    expect(screen.getByText('Loading products...')).toBeInTheDocument();
  });

  test('renders products after successful API call', async () => {
    const mockProducts = [
      { id: 1, name: 'Test Product', price: 29.99, image: 'test.jpg' },
      { id: 2, name: 'Another Product', price: 39.99, image: 'test2.jpg' },
    ];

    mockedAxios.get.mockResolvedValueOnce({ data: mockProducts });

    render(
      <Provider store={mockStore}>
        <ProductList />
      </Provider>
    );

    await waitFor(() => {
      expect(screen.getByText('Test Product')).toBeInTheDocument();
      expect(screen.getByText('Another Product')).toBeInTheDocument();
    });
  });
});