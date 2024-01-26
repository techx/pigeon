import "@mantine/core/styles.css";
import "@mantine/notifications/styles.css";
import "@mantine/tiptap/styles.css";
import {
  createBrowserRouter,
  createRoutesFromElements,
  Route,
  RouterProvider,
} from "react-router-dom";

import InboxPage from "./routes/inbox";
import IndexPage from "./routes/index";
import DocumentsPage from "./routes/documents";
import Shell from "./components/shell";
import LoginPage from "./components/login";
import { AuthProvider, authLoader } from "./components/auth";
import { ProtectedAuthRoute, ProtectedNonAuthRoute } from "./routes/protected";
import RestrictedPage from "./routes/restricted";

const router = createBrowserRouter(
  createRoutesFromElements(
    <Route element={<Shell />}>
      <Route index path="/" loader={authLoader} element={<IndexPage />} />
      <Route path="/login" loader={authLoader} element={<LoginPage />} />
      <Route
        path="/inbox"
        loader={authLoader}
        element={
          <ProtectedAuthRoute>
            <InboxPage />
          </ProtectedAuthRoute>
        }
      />
      <Route
        path="/documents"
        loader={authLoader}
        element={
          <ProtectedAuthRoute>
            <DocumentsPage />
          </ProtectedAuthRoute>
        }
      />
      <Route
        path="/restricted"
        loader={authLoader}
        element={
          <ProtectedNonAuthRoute>
            <RestrictedPage />
          </ProtectedNonAuthRoute>
        }
      />

      <Route path="*" element={<RestrictedPage />} />
    </Route>
  )
);

export default function App() {
  return (
    <AuthProvider>
      <RouterProvider router={router} />
    </AuthProvider>
  );
}
