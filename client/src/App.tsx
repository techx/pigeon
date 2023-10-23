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

const router = createBrowserRouter(
  createRoutesFromElements(
    <Route element={<Shell />}>
      <Route index path="/" element={<IndexPage />} />
      <Route index path="/inbox" element={<InboxPage />} />
      <Route index path="/documents" element={<DocumentsPage />} />
    </Route>,
  ),
);

export default function App() {
  return <RouterProvider router={router} />;
}
