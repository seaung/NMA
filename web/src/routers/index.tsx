import { lazy, Suspense } from 'react'
import { createBrowserRouter } from 'react-router-dom'

const LoginPage = lazy(() => import('../views/login'))
const NotAuth = lazy(() => import('../components/ErrorMessage/403'))
const Layout = lazy(() => import('../layout'))
const NotFound = lazy(() => import('../components/ErrorMessage/404'))
const NotNetwork = lazy(() => import('../components/ErrorMessage/500'))
const HomePage = lazy(() => import('../views/home'))

const router = createBrowserRouter([
  {
    path: '/login',
    element: <LoginPage />,
  },
  {
    path: '/403',
    element: <NotAuth />,
  },
  {
    path: '/404',
    element: <NotFound />,
  },
  {
    path: '/500',
    element: <NotNetwork />,
  },
  {
    path: '/',
    element: <Layout />,
    children: [
      {
        path: '/home',
        element: <HomePage />,
      },
      {
        path: '*',
        element: <NotFound />,
      }
    ]
  },
])

export default router