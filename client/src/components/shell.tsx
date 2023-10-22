import { useState } from "react";
import { Outlet, useNavigate } from "react-router-dom";
import { AppShell, NavLink, Space, Text } from "@mantine/core";
import { IconInbox, IconBook } from "@tabler/icons-react";

const data = [{label: "Inbox", icon: IconInbox}, {label: "Documents", icon: IconBook}]

export default function HeaderNav() {
    const [active, setActive] = useState(document.location.pathname === "/inbox" ? 0: 1);
    const navigate = useNavigate();
    const links = data.map((item, index) => (
        <NavLink
            key={item.label}
            active={index === active}
            label={<Text size="lg">{item.label}</Text>}
            leftSection={<item.icon size="1.5rem" stroke={2} />}
            onClick={() => {
                setActive(index); 
                navigate(item.label.toLowerCase());
            }}
        />
      ));
    return (
        <AppShell navbar={{ width: 200, breakpoint: "sm" }}>
            <AppShell.Navbar>
                <Space h={150}/>
                {links}
            </AppShell.Navbar>
            <AppShell.Main>
                <Outlet />
            </AppShell.Main>
        </AppShell>
    )
}

