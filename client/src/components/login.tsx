import { useEffect } from "react";
import {
  Container,
  Button,
  Paper,
  Title,
  TextInput,
  PasswordInput,
} from "@mantine/core";
import { useForm } from "@mantine/form";
import {
  showNotification,
  updateNotification,
  cleanNotifications,
} from "@mantine/notifications";
import { IconX } from "@tabler/icons-react";
import { useLoaderData } from "react-router-dom";
import { useAuth } from "./auth";

interface LoginResponse {
  status: number;
  statusText: string;
  text: () => Promise<string>;
  json: () => Promise<{ new_url: string }>;
}

interface LoginCredentials {
  username: string;
  password: string
}

export async function whoami() {
  const res = await fetch("/api/auth/whoami");
  const data = await res.json();
  return data.auth;
}

export async function loginLoader() {
  return await whoami();
}

export default function LoginPage() {
  const { setAuthorized } = useAuth();

  async function login(username: string, password: string) {
    return await fetch("/api/auth/login", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        username: username,
        password: password,
      }),
    });
  }

  useEffect(() => {
    whoami().then(isAuthenticated => {
      if (isAuthenticated) {
        window.location.replace("/inbox");
      }
    });
  }, []);
  
  async function onLoginSubmit({ username, password }: LoginCredentials) {
    cleanNotifications();
    showNotification({
      id: "login",
      loading: true,
      title: `logging in`,
      message: "processing credentials...",
      autoClose: false,
      // disallowClose: true,
    });
    updateNotification({
      id: "login",
      loading: true,
      title: `logging in`,
      message: "processing credentials...",
      autoClose: false,
      // disallowClose: true,
    });

    const response: LoginResponse = await login(username, password);
    loginForm.setValues({
      password: "",
    });

    if (response.status >= 400) {
      const response_text = await response.text();
      const message = response_text || response.statusText;
      updateNotification({
          id: "login",
          color: "red",
          title: "failed to log in",
          message: `reason: ${message}`,
          icon: <IconX size={16} />,
          autoClose: false,
          // disallowClose: false,
      });
      return;
    }
    setAuthorized(true);
    const new_url = await response.json();
    window.location.replace(new_url.new_url);
  };

  const loginForm = useForm({
    initialValues: {
      username: "",
      password: "",
    },
    validate: {
      username: (value: string) => (value.length === 0 ? "username required" : null),
      password: (value: string) => (value.length === 0 ? "password required" : null),
    }
  });

  return (
    <Container className="loginContainer">
      <Container style={{width:420}} className="">
        <Paper withBorder shadow="md" p={30} mt={30} radius="md">
          <Title style={{align:"center"}}>login</Title>
          <form onSubmit={loginForm.onSubmit(onLoginSubmit)}>
            <TextInput
              label="username"
              placeholder="bobby"
              autoComplete="off"
              withAsterisk
              {...loginForm.getInputProps("username")}
            />
            <PasswordInput
              label="password"
              placeholder="imbobby"
              mt="md"
              withAsterisk
              {...loginForm.getInputProps("password")}
            />
            <Button fullWidth mt="xl" type="submit">
              log in
            </Button>
          </form>
        </Paper>
      </Container>
    </Container>
  );
}