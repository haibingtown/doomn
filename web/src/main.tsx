import { createRoot } from "react-dom/client";
import Fabritor from "./pages/editor";
import './typings.d.ts';
import './font.css';
import './global.css';

import { StrictMode } from "react";
import { Route, BrowserRouter as Router, Routes } from "react-router-dom";
import { I18nProvider } from "./utils/i18n";


createRoot(document.getElementById('root')!).render(
    <StrictMode>
        <I18nProvider>
            <Router>
                <Routes>
                    <Route path="/" element={<Fabritor />} />
                </Routes>
            </Router>
        </I18nProvider>
    </StrictMode>
)