import { createBrowserRouter } from "react-router";
import { RouterProvider } from "react-router/dom";

import RootLayout from "../components/layout/root-layout";
import HomeRoute from "./routes/home";
import RegisterRoute from "./routes/register";

const router = createBrowserRouter([
  {
    path: "/",
    Component: RootLayout,
    children: [
      { index: true, Component: HomeRoute },
      { path: "register", Component: RegisterRoute },
    ],
  },
]);

export const AppRouter = () => {
  return <RouterProvider router={router} />;
};
