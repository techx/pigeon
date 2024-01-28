import classes from "./restricted.module.css";

export default function RestrictedPage() {
  return (
    <div className={classes.restrictedContainer}>
      <h1>Access Denied</h1>
      <div>You have reached a restricted route.</div>
    </div>
  );
}
