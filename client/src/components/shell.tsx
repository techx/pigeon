import { ReactElement, useState, useEffect } from "react";
import { Outlet, useNavigate } from "react-router-dom";
import {
  IconHome,
  IconInbox,
  IconBook,
  IconLogin,
  IconLogout,
} from "@tabler/icons-react";
import {
  AppShell,
  Box,
  Anchor,
  NavLink,
  Text,
  Group,
  Burger,
} from "@mantine/core";
import { useDisclosure } from "@mantine/hooks";
import { notifications } from "@mantine/notifications";
import { useAuth } from "./auth";
import classes from "./shell.module.css";

interface LinkData {
  label: string;
  icon: React.ElementType<React.SVGProps<SVGSVGElement>>;
  link?: string;
  onClick?: () => void;
}

export default function Shell() {
  const navigate = useNavigate();
  const [opened, { toggle }] = useDisclosure();
  const { authorized } = useAuth();
  const [links, setLinks] = useState<ReactElement[]>([]);

  const handleLogout = async () => {
    const response = await fetch(`/api/auth/logout`, {
      method: "POST",
    });
    try {
      window.location.replace(response.url);
    } catch (e) {
      notifications.show({
        title: "Error!",
        color: "red",
        message: "Something went wrong!",
      });
    }
  };

  useEffect(() => {
    const commonLinks: LinkData[] = [
      { label: "Home", icon: IconHome, link: "/" },
    ];

    const authLinks: LinkData[] = [
      { label: "Inbox", icon: IconInbox, link: "/inbox" },
      { label: "Documents", icon: IconBook, link: "/documents" },
      {
        label: "Log Out",
        icon: IconLogout,
        onClick: handleLogout,
      },
    ];

    const unauthLinks: LinkData[] = [
      { label: "Log In", icon: IconLogin, link: "/login" },
    ];

    // Combining common links with either authenticated or unauthenticated links
    const linkDataAll: LinkData[] = authorized
      ? [...commonLinks, ...authLinks]
      : [...commonLinks, ...unauthLinks];

    const linksComponents = linkDataAll.map((item) => (
      <NavLink
        key={item.label}
        active={location.pathname === item.link}
        label={<Text size="lg">{item.label}</Text>}
        leftSection={<item.icon height="1.5rem" width="1.5rem" stroke="2" />}
        onClick={() => {
          if (item.onClick) {
            item.onClick();
          } else if (item.link) {
            navigate(item.link);
          }
        }}
      />
    ));
    setLinks(linksComponents);
  }, [authorized, location.pathname]);

  return (
    <AppShell
      navbar={{ width: 200, breakpoint: "sm", collapsed: { mobile: !opened } }}
    >
      <AppShell.Header>
        <Group h={{ base: "60px", sm: 0 }} px="md">
          <Burger opened={opened} onClick={toggle} hiddenFrom="sm" size="sm" />
        </Group>
      </AppShell.Header>
      <AppShell.Navbar mt={{ base: "60px", sm: 0 }}>
        <Anchor
          style={{ paddingTop: "20px", paddingLeft: "20px" }}
          key="Home"
          onClick={() => {
            navigate("/");
          }}
        >
          <img src="./pigeon.png" width="160px" height="160px" />
        </Anchor>
        <Box className="navlinksinner">{links}</Box>
      </AppShell.Navbar>
      <AppShell.Main>
        <div className={classes.paddingDiv}></div>
        <Outlet />
      </AppShell.Main>
    </AppShell>
  );
}
