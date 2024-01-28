import classes from "./restricted.module.css";

export default function RestrictedPage() {
  return (
    <div className={classes.restrictedContainer}>
      <h1>Access Denied</h1>
      <div>
        You have reached a restricted route. If you are trying to log in with
        Google, make sure you are whitelisted!
      </div>
    </div>
  );
}
