import { BrowserRouter as Router, Routes, Route, Navigate } from "react-router-dom";
import Login from "./pages/Login";
import Dashboard from "./pages/Dashboard";
import { useAuth } from "./context/AuthContext";
import Navbar from "./components/Navbar";
import CreateLesson from "./pages/CreateLesson";
import StudentManagement from "./pages/StudentManagement";
import Transcript from "./pages/Transcript";
import ManageUsers from "./pages/ManageUsers";
import EditLesson from "./pages/EditLesson";
import ProfileSettings from "./pages/ProfileSettings";


// Gecici placeholder bilesenleri
const PageUnderConstruction = ({ title }) => (
  <div className="p-8 bg-gray-50 min-h-screen flex items-center justify-center">
    <div className="text-center">
      <h1 className="text-4xl font-bold text-gray-800 mb-4">🚧 {title}</h1>
      <p className="text-gray-600">Bu sayfa yakında hazır olacak.</p>
    </div>
  </div>
);

function App() {
  const { token, user } = useAuth();   //hafizadaki token bilgisini aliyoruz
  

  return (
    <Router>
      <div className="App">
        <Navbar /> {/* Navbar'i her zaman goster, icerisinde token kontrolu yaparak linkleri gosteririz */}
        <Routes>
          {/*
           GİRİS KONTROLU: 
            Eger kullanici giris yapmissa (token varsa) ana sayfada Dashboard'u goster.
            Giris yapmamissa direkt Login sayfasina yonlendir
           */}
          <Route
            path="/" 
            element={token ? <Dashboard /> : <Navigate to="/login" />} 
           />

          {/* Login sayfasi: Eger zaten giris yapilmissa tekrar login'e girmesin, ana sayfaya gitsin */}
          <Route
            path="/login"
            element={!token ? <Login /> : <Navigate to="/" />} 
            />

          {/* Create Lesson Sayfası - Sadece Teacher ve Admin gorebilir */}
          <Route 
            path="/create-lesson" 
            element={
              token && (user?.role === 'teacher' || user?.role === 'admin') 
              ? <CreateLesson /> 
              : <Navigate to="/" />
            } 
          />

          {/* Profile Sayfasi */}
          <Route
            path="/profile"
            element={token ? <ProfileSettings /> : <Navigate to="/login" />}
          />

          {/* Transcript Sayfasi - Sadece Student */}
          <Route
            path="/transcript"
            element={token && user?.role === 'student' ? <Transcript /> : <Navigate to="/" />}
          />

          {/* Admin - Manage Users */}
          <Route
            path="/admin/manage-users"
            element={token && user?.role === 'admin' ? <ManageUsers /> : <Navigate to="/" />}
          />

          {/* Admin - Edit Lesson */}
          <Route
            path="/admin/edit-lesson/:id"
            element={token && user?.role === 'admin' ? <EditLesson /> : <Navigate to="/" />}
          />

          {/* Teacher - Manage Students */}
          <Route
            path="/lesson/:id/students"
            element={
              token && (user?.role === 'teacher' || user?.role === 'admin') 
              ? <StudentManagement /> 
              : <Navigate to="/" />}
          />

          {/* Hatali bir yol yazilirsa(404) Login'e geri gonder */}
          <Route path="*" element={<Navigate to="/login" />} />
        </Routes>
      </div>
    </Router>
  );
}

export default App;