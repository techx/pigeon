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
import LoginPage, { loginLoader } from "./components/login"
import { AuthProvider } from "./components/auth";
import { ProtectedAuthRoute, ProtectedNonAuthRoute } from "./routes/protected";
import RestrictedPage from "./routes/restricted";

const router = createBrowserRouter(
  createRoutesFromElements(
    <Route element={<Shell />}>
      <Route index path="/" element={<IndexPage />} />
      <Route path="/login" loader={loginLoader} element={<LoginPage />} />
      <Route path="/inbox" element={
        <ProtectedAuthRoute>
          <InboxPage />
        </ProtectedAuthRoute>} />
      <Route path="/documents" element={
        <ProtectedAuthRoute>
          <DocumentsPage />
        </ProtectedAuthRoute>} />
        <Route path="/restricted" element={
        <ProtectedNonAuthRoute>
          <RestrictedPage />
        </ProtectedNonAuthRoute>} />
    </Route>,
  ),
);

export default function App() {
  return (
    <AuthProvider>
      <RouterProvider router={router} />;
    </AuthProvider>
  )
}
