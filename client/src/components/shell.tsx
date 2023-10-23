import { useState } from "react";
import { Outlet, useNavigate } from "react-router-dom";
import { AppShell, NavLink, Space, Text, Anchor } from "@mantine/core";
import { IconInbox, IconBook } from "@tabler/icons-react";
const data = [
  { label: "Pigeon", img: "./pigeon.png" },
  { label: "Inbox", icon: IconInbox },
  { label: "Documents", icon: IconBook },
];

export default function HeaderNav() {
  const inboxPath = document.location.pathname === "/inbox";
  const documentsPath = document.location.pathname === "/documents";
  const [active, setActive] = useState(+inboxPath + 2 * +documentsPath);
  const navigate = useNavigate();
  const links = data.map((item, index) =>
    item.icon ? (
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
    ) : (
      <Anchor
        style={{ paddingTop: "20px", paddingLeft: "20px" }}
        key={item.label}
        onClick={() => {
          setActive(index);
          navigate("/");
        }}
      >
        <img src={item.img} width="160px" height="160px" />
      </Anchor>
    ),
  );
  return (
    <AppShell navbar={{ width: 200, breakpoint: "sm" }}>
      <AppShell.Navbar>{links}</AppShell.Navbar>
      <AppShell.Main>
        <Outlet />
      </AppShell.Main>
    </AppShell>
  );
}
