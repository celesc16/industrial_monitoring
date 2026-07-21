import { Outlet } from "react-router";

import AppNavigation from "../../components/AppNavigation/AppNavigation";

export default function AppLayout() {
  return (
    <>
      <AppNavigation />

      <main>
        <Outlet />
      </main>
    </>
  );
}