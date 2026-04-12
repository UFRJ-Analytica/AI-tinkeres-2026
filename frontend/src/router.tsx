import { createBrowserRouter } from "react-router-dom"
import LandingPage from "@/pages/LandingPage"
import DemoPage from "@/pages/DemoPage"

export const router = createBrowserRouter([
  {
    path: "/",
    element: <LandingPage />,
  },
  {
    path: "/solicitar-demo",
    element: <DemoPage />,
  },
])
