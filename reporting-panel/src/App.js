import logo from "./logo.svg";
import "./App.css";
import { BrowserRouter as Router, Route, Routes } from "react-router-dom";
import ReportingPanel from "./ReportingPanel";
import Logout from "./Components/Logout";
function App() {
  return (
    <div>
      {console.log("APP.js")}

      <Router>
        <Routes>
          <Route path="/" element={<ReportingPanel />} />
          {/* <Route path="/logout" element={<Logout />} /> */}
        </Routes>
      </Router>
    </div>
  );
}

export default App;
