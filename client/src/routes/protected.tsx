import { ReactNode, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import { useAuth } from "../components/auth";

export const ProtectedAuthRoute: React.FC<{ children: ReactNode }> = ({
  children,
}) => {
  const { authorized } = useAuth();
  const navigate = useNavigate();

  useEffect(() => {
    if (!authorized) {
      navigate("/restricted");
    }
  }, [authorized]);

  return children;
};

export const ProtectedNonAuthRoute: React.FC<{ children: ReactNode }> = ({
  children,
}) => {
  const { authorized } = useAuth();
  const navigate = useNavigate();

  useEffect(() => {
    if (authorized) {
      navigate("/inbox");
    }
  }, [authorized]);

  return children;
};
