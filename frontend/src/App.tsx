import { Route, Routes } from "react-router";

import Chat from "@/pages/Chat";
import Landing from "@/pages/Landing";
import NotFound from "@/pages/NotFound";

export default function App() {
  return (
    <Routes>
      <Route path="/" element={<Landing />} />
      <Route path="/chat" element={<Chat />} />
      <Route path="*" element={<NotFound />} />
    </Routes>
  );
}
