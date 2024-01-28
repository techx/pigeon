import { useState } from "react";
import {
  TextInput,
  PasswordInput,
  Divider,
  Paper,
  Title,
  Container,
  Button,
} from "@mantine/core";
import { useForm } from "@mantine/form";
import {
  showNotification,
  updateNotification,
  cleanNotifications,
} from "@mantine/notifications";
import { IconX } from "@tabler/icons-react";
import { FcGoogle } from "react-icons/fc";
import { useNavigate } from "react-router-dom";
import { useAuth } from "./auth";
import classes from "./login.module.css";

export function GoogleButton(props: any) {
  return <Button leftSection={<FcGoogle />} variant="light" {...props} />;
}

import { BASE_URL } from "../main";

export default function LoginPage() {
  const [adminLoginModal, setAdminLoginModal] = useState(false);
  const { setAuthorized } = useAuth();
  const navigate = useNavigate();

  const adminLogin = async (username: string, password: string) => {
    return await fetch(`${BASE_URL}/api/auth/login_admin`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        username: username,
        password: password,
      }),
    });
  };

  function handleGoogleSubmit() {
    window.location.replace(`${BASE_URL}/api/auth/login`);
  }

  async function onAdminLoginSubmit({
    username,
    password,
  }: {
    username: string;
    password: string;
  }) {
    cleanNotifications();
    showNotification({
      id: "login",
      loading: true,
      title: `Logging in`,
      message: "Processing credentials...",
      autoClose: false,
    });

    const response = await adminLogin(username, password);

    loginForm.setValues({
      password: "",
    });

    if (response.status >= 400) {
      const response_text = await response.text();
      const message = JSON.parse(response_text).message || response.statusText;
      updateNotification({
        id: "login",
        color: "red",
        title: `Failed to log in`,
        message: `Reason: ${message}`,
        icon: <IconX size={16} />,
        autoClose: false,
        loading: false,
      });
      return;
    } else {
      cleanNotifications();
      setAuthorized(true);
      navigate("/inbox");
    }
  }

  const loginForm = useForm({
    initialValues: {
      username: "",
      password: "",
    },
    validate: {
      username: (value) => (value.length === 0 ? "Username required" : null),
      password: (value) => (value.length === 0 ? "Password required" : null),
    },
  });

  return (
    <>
      <Container className={classes.loginContainer}>
        <Container className={classes.loginModal}>
          <Paper withBorder shadow="md" p={30} mt={30} radius="md">
            <Title ta="center">Login</Title>
            <GoogleButton
              fullWidth
              radius="md"
              my="md"
              onClick={() => handleGoogleSubmit()}
            >
              Log in with Google
            </GoogleButton>
            <Divider
              label="Use admin credentials"
              labelPosition="center"
              mt={24}
              mb={adminLoginModal ? 16 : 0}
              className={classes.pointer}
              onClick={() => setAdminLoginModal(!adminLoginModal)}
            />
            {adminLoginModal && (
              <form onSubmit={loginForm.onSubmit(onAdminLoginSubmit)}>
                <TextInput
                  label="Username"
                  placeholder="Username"
                  autoComplete="off"
                  withAsterisk
                  {...loginForm.getInputProps("username")}
                />
                <PasswordInput
                  label="Password"
                  placeholder="Password"
                  mt="md"
                  withAsterisk
                  {...loginForm.getInputProps("password")}
                />
                <Button fullWidth mt="xl" type="submit">
                  Log in
                </Button>
              </form>
            )}
          </Paper>
        </Container>
      </Container>
    </>
  );
}
