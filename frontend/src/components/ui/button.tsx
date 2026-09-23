import {
  Button as MantineButton,
  createPolymorphicComponent,
  type ButtonProps,
} from "@mantine/core";

import classes from "./button.module.css";

// Mantine's `Button` with the app's uppercase, tightly tracked label styling,
// kept polymorphic so callers can still render it as a `Link`.
const ButtonBase = ({ className, ...props }: ButtonProps) => {
  return (
    <MantineButton
      color="dark"
      radius="sm"
      tt="uppercase"
      fz="xs"
      lts="0.05em"
      {...props}
      className={className ? `${classes.root} ${className}` : classes.root}
    />
  );
};

export const Button = createPolymorphicComponent<"button", ButtonProps>(
  ButtonBase,
);
