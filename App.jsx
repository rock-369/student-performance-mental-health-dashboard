import React, { useState, useEffect } from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import Sidebar from './components/Sidebar';
import StudentDashboard from './pages/StudentDashboard';
import TeacherDashboard from './pages/TeacherDashboard';
import CounselorDashboard from './pages/CounselorDashboard';
import Login from './pages/Login';
import Signup from './pages/Signup';
import StudentQuestionnaire from './pages/StudentQuestionnaire';
import Chat from './pages/Chat';

function App() {
    const [user, setUser] = useState(null);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        const token = localStorage.getItem('token');
        const role = localStorage.getItem('role');
        const user_id = localStorage.getItem('user_id');
        const name = localStorage.getItem('user_name');

        if (token && role) {
            setUser({ token, role, user_id, name });
        }
        setLoading(false);
    }, []);

    const handleLogin = (userData) => {
        setUser(userData);
    };

    const handleLogout = () => {
        localStorage.clear();
        setUser(null);
    };

    if (loading) return <div>Loading...</div>;

    return (
        <Router>
            <div className="app-container">
                {user && (
                    <Sidebar
                        currentRole={user.role}
                        onLogout={handleLogout}
                        userName={user.name}
                    />
                )}
                <main className={user ? "main-content" : ""}>
                    <Routes>
                        <Route
                            path="/login"
                            element={!user ? <Login onLogin={handleLogin} /> : <Navigate to="/" />}
                        />
                        <Route
                            path="/signup"
                            element={!user ? <Signup /> : <Navigate to="/" />}
                        />

                        <Route
                            path="/"
                            element={
                                user ? (
                                    user.role === 'student' ? <StudentDashboard /> :
                                        user.role === 'teacher' ? <TeacherDashboard /> :
                                            <CounselorDashboard />
                                ) : <Navigate to="/login" />
                            }
                        />

                        {/* Protected Routes */}
                        <Route
                            path="/student"
                            element={user?.role === 'student' ? <StudentDashboard /> : <Navigate to="/" />}
                        />
                        <Route
                            path="/questionnaire"
                            element={user?.role === 'student' ? <StudentQuestionnaire /> : <Navigate to="/" />}
                        />
                        <Route
                            path="/teacher"
                            element={user?.role === 'teacher' ? <TeacherDashboard /> : <Navigate to="/" />}
                        />
                        <Route
                            path="/counselor"
                            element={user?.role === 'counselor' ? <CounselorDashboard /> : <Navigate to="/" />}
                        />
                        <Route
                            path="/chat"
                            element={user ? <Chat /> : <Navigate to="/login" />}
                        />

                        <Route path="*" element={<Navigate to="/" replace />} />
                    </Routes>
                </main>
            </div>
        </Router>
    );
}

export default App;
