import { ReactNode } from "react";
import { useNavigate } from "react-router-dom";
import { useAuth } from "../components/auth";

export const ProtectedAuthRoute: React.FC<{ children: ReactNode }> = ({
  children,
}) => {
  const { authorized } = useAuth();
  const navigate = useNavigate();

  if (!authorized) {
    navigate("/restricted");
  }

  return children;
};

export const ProtectedNonAuthRoute: React.FC<{ children: ReactNode }> = ({
  children,
}) => {
  const { authorized } = useAuth();
  const navigate = useNavigate();

  if (authorized) {
    navigate("/inbox");
  }

  return children;
};
