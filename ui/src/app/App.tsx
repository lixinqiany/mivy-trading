import { Navigate, Route, Routes } from 'react-router-dom';
import { AppShell } from '../components/layout/AppShell';
import { APP_PATHS } from '../config/navigation';
import { DataCrawlingView } from '../views/data-crawling/DataCrawlingView';
import { SecurityPoolView } from '../views/security-pool/SecurityPoolView';
import { TaskCenterView } from '../views/task-center/TaskCenterView';
import { WatchlistsView } from '../views/watchlists/WatchlistsView';

export function App() {
  return (
    <Routes>
      <Route element={<AppShell />}>
        <Route
          index
          element={<Navigate to={APP_PATHS.securityPool} replace />}
        />
        <Route path={APP_PATHS.securityPool} element={<SecurityPoolView />} />
        <Route path={APP_PATHS.watchlists} element={<WatchlistsView />} />
        <Route path={APP_PATHS.dataCrawling} element={<DataCrawlingView />} />
        <Route path={APP_PATHS.taskCenter} element={<TaskCenterView />} />
        <Route
          path="*"
          element={<Navigate to={APP_PATHS.securityPool} replace />}
        />
      </Route>
    </Routes>
  );
}
