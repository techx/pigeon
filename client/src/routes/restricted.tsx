import classes from "./restricted.module.css";

export default function RestrictedPage() {
  return (
    <div className={classes.restrictedContainer}>
      <h1>Access Denied</h1>
      <div>You are either not logged in, or your email is not whitelisted.</div>
    </div>
  );
}
