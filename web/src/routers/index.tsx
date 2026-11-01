import { lazy } from 'react'
import { createBrowserRouter, Navigate } from 'react-router-dom'

const LoginPage = lazy(() => import('../views/login'))
const NotAuth = lazy(() => import('../components/ErrorMessage/403'))
const Layout = lazy(() => import('../layout'))
const NotFound = lazy(() => import('../components/ErrorMessage/404'))
const NotNetwork = lazy(() => import('../components/ErrorMessage/500'))
const HomePage = lazy(() => import('../views/home'))
const AssetsPage = lazy(() => import('../views/assets'))
const VulnerabilitiesPage = lazy(() => import('../views/vulnerabilities'))
const TicketsPage = lazy(() => import('../views/tickets'))
const MessagesPage = lazy(() => import('../views/messages'))
const TasksPage = lazy(() => import('../views/tasks'))
const ReportsPage = lazy(() => import('../views/reports'))

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
      { index: true, element: <Navigate to="/dashboard" replace /> },
      { path: 'dashboard', element: <HomePage /> },
      { path: 'assets', element: <AssetsPage /> },
      { path: 'vulnerabilities', element: <VulnerabilitiesPage /> },
      { path: 'tickets', element: <TicketsPage /> },
      { path: 'messages', element: <MessagesPage /> },
      { path: 'tasks', element: <TasksPage /> },
      { path: 'reports', element: <ReportsPage /> },
      { path: '*', element: <NotFound /> },
    ],
  },
])

export default router
