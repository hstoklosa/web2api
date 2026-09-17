import { createBrowserRouter } from "react-router";
import { RouterProvider } from "react-router/dom";

import AppLayout from "@/components/layout/app-layout";
import RootLayout from "@/components/layout/root-layout";
import { requireAuth } from "./middleware/require-auth";
import DashboardRoute from "./routes/dashboard";
import HomeRoute from "./routes/home";
import RegisterRoute from "./routes/register";

const router = createBrowserRouter([
  {
    path: "/",
    Component: RootLayout,
    children: [
      { index: true, Component: HomeRoute },
      { path: "register", Component: RegisterRoute },
      {
        Component: AppLayout,
        middleware: [requireAuth],
        children: [{ path: "dashboard", Component: DashboardRoute }],
      },
    ],
  },
]);

export const AppRouter = () => {
  return <RouterProvider router={router} />;
};
