import { useEffect, useState } from "react";
import { Outlet, useNavigate } from "react-router-dom";
import { AppShell, NavLink, Space } from "@mantine/core";

const data = [{label: "Inbox"}, {label: "Documents"}]

export default function HeaderNav() {
    const [active, setActive] = useState(0);
    const navigate = useNavigate();
    const links = data.map((item, index) => (
        <NavLink
            key={item.label}
            active={index === active}
            label={item.label}
            //leftSection={<item.icon size="1rem" stroke={1.5} />}
            onClick={() => {
                setActive(index); 
                navigate(item.label.toLowerCase());
            }}
        />
      ));
    useEffect(() => {
        console.log(active);
    }, [])

    return (
        <AppShell navbar={{ width: 200, breakpoint: "sm" }}>
            <AppShell.Navbar>
                <Space h="xl"/>
                {links}
            </AppShell.Navbar>
            <AppShell.Main>
                <Outlet />
            </AppShell.Main>
        </AppShell>
    )
}

